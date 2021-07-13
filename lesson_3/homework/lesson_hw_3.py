### 1. Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB
### и реализовать функцию, записывающую собранные вакансии в созданную БД.

import requests
import time
from bs4 import BeautifulSoup as bs
from pymongo import MongoClient
from pprint import pprint
import re

client = MongoClient('localhost', 27017)
db = client['vacancy']
job_data = db.hh_db


def get_html(url, retry_number, sleep):
    for i in range(retry_number):
        try:
            headers = {
                'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            r = requests.get(url, headers=headers)
            if r.status_code != 200:
                raise Exception("Status code != 200")
            return r
        except:
            time.sleep(sleep)
    return None


def get_total_pages(r):
    soup = bs(r.text, 'lxml')
    pages = soup.find_all('a', class_='bloko-button')[-2].find('span').getText()
    return int(pages)


def insert_new(vac1):
    vacs = job_data.count_documents({'url': vac1['url']})
    if vacs == 0:
        print('Новая вакансия:')
        pprint(vac1)
        job_data.insert_one(vac1)


def get_page_data(html, f):
    soup = bs(html.text, 'lxml')
    ads = soup.find('div', class_='vacancy-serp').find_all('div', class_='vacancy-serp-item')

    for ad in ads:
        price_min = None
        price_max = None
        price_currency = None

        try:
            title = ad.find('a', {"data-qa": "vacancy-serp__vacancy-title"}).text
        except:
            title = ''
        try:
            c_ = '–'
            price = ad.find('div', class_='vacancy-serp-item__sidebar').find('span').text.strip()
            if price:
                price = price.replace(u'\u202f', u'')
                price = re.split(r'\s|-', price)
                if price[0] == 'до':
                    price_min = None
                    price_max = int(price[1])
                    price_currency = str(price[2])
                elif price[0] == 'от':  # з/п "от"
                    price_min = int(price[1])
                    price_max = None
                    price_currency = str(price[2])
                else:  # з/п "от" и "до"
                    price_min = int(price[0])
                    price_max = int(price[2])
                    price_currency = str(price[3])

                price_currency = _get_name_currency(price_currency)

        except:
            price = ''
        try:
            url = ad.find('a', {"data-qa": "vacancy-serp__vacancy-title"}).get('href')
        except:
            url = ''

        f.write(f"{title}, {price_min} - {price_max} {price_currency}, {url} spb.hh.ru")
        f.write('\n')
        params = {
            'title': title,
            'price_min': price_min,
            'price_max': price_max,
            'price_currency': price_currency,
            'url': url
        }
        insert_new(params)

def _get_name_currency(currency_name):
    currency_dict = {
            'EUR': {' €'},
            'KZT': {' ₸'},
            'RUB': {' ₽', 'руб.'},
            'UAH': {' ₴', 'грн.'},
            'USD': {' $'}
        }

    name = currency_name

    for item_name, items_list in currency_dict.items():
        if currency_name in items_list:
            name = item_name

    return name

def main(vacancy):
    filename = "headh_" + vacancy + ".csv"
    url = 'https://spb.hh.ru/search/vacancy?clusters=true&area=2&enable_snippets=true&salary=&st=searchVacancy'
    page_part = '&page='
    query_part = '&text='
    url_query = url + query_part + vacancy

    total_pages = get_total_pages(get_html(url_query, 5, 5))

    with open(filename, 'w', encoding='utf8') as f:
        for i in range(0, total_pages):
            url_gen = url + page_part + str(i) + query_part + vacancy
            html = get_html(url_gen, 5, 5)
            get_page_data(html, f)


if __name__ == "__main__":
    vacancy = input('Введите название вакансии: ')
    main(vacancy)

### 2. Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше введённой суммы.


def show_salary_from(greater_than):
    print('Вакансии с зарплатой больше введенной суммы:\n')
    for vac in job_data.find({'$or': [{'price_min': {'$gt': greater_than}},
                                             {'price_max': {'$gt': greater_than}}]}):
        pprint(vac)

user_salary = int(input('Введите минимальную заработную плату: '))
show_salary_from(user_salary)