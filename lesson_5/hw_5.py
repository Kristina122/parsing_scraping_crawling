from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from dotenv import load_dotenv
import os
import time
from pymongo import MongoClient
import json
import hashlib

client = MongoClient('localhost', 27017)
db = client['email_db']
try:
    collection = db.create_collection('email')
except:
    collection = db.email

driver = webdriver.Chrome()
driver.get("https://mail.ru/")


load_dotenv("../lesson_5/.env")

elem = driver.find_element_by_class_name('email-input') ##  вводим логин
elem.send_keys(os.getenv("LOGIN"))

check = driver.find_element_by_class_name('button ') ## нажимаем на кнопку: "Ввести пароль"
check.click()

time.sleep(2)

elem = driver.find_element_by_class_name('password-input') ### вводим пароль
elem.send_keys(os.getenv("PASSWORD"))

elem.send_keys(Keys.ENTER)

link_all = set()
time.sleep(3)
email_list = driver.find_elements_by_class_name('js-tooltip-direction_letter-bottom')
link_list = list(map(lambda el: el.get_attribute('href'), email_list))
link_all = link_all.union(set(link_list))

while True:
    actions = ActionChains(driver)
    actions.move_to_element(email_list[-1])
    actions.perform()
    WebDriverWait(driver, 8).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    time.sleep(3)
    email_list = driver.find_elements_by_class_name('js-tooltip-direction_letter-bottom')
    link_list = list(map(lambda el: el.get_attribute('href'), email_list))

    if link_list[-1] not in link_all:
        link_all = link_all.union(set(link_list))
        continue
    else:
        break

for href in list(link_all):
    driver.get(href)
    time.sleep(4)
    email_for_mongo_db = dict()
    email_for_mongo_db['sender'] = driver.find_element_by_class_name('letter-contact').get_attribute('title')
    email_for_mongo_db['date'] = driver.find_element_by_class_name('letter__date').text
    email_for_mongo_db['title'] = driver.find_element_by_xpath('//h2').text
    email_for_mongo_db['body'] = driver.find_element_by_class_name('letter-body').text

    email_binary = json.dumps(email_for_mongo_db).encode('utf-8')
    email_hash = hashlib.sha3_256(email_binary)
    email_id = email_hash.hexdigest()
    email_for_mongo_db['_id'] = email_id

    try:
        collection.insert_one(email_for_mongo_db)

    except Exception:
        continue

driver.quit()

with open('email_results.txt', 'w') as file:
    for doc in collection.find({}):
        file.write(f'{str(doc)} \n')