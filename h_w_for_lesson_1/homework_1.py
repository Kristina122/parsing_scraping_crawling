### 1-е задание

import requests
import json

def take_rep(user):
    url = 'https://api.github.com/users/' + user + '/repos'
    rep = requests.get(url).json()
    return rep

def write_file(path, rep):
    with open(path, 'w') as f:
        json.dump(rep, f, indent=2)

def read_rep_user(path):
    with open(path, 'r') as f:
        json_rep = json.load(f)
    return json_rep

if __name__ == "__main__":
    user = 'Kristina122'
    write_file('rep_Kristina122.json', take_rep(user))
    print("Список репозиториев пользователя " + user + "на GitHUB:")
    for i in read_rep_user('rep_Kristina122.json'):
        print(i['name'])

### 2-е задание

import requests
import os
from dotenv import load_dotenv

load_dotenv("../h_w_for_lesson_1/.env")

def get_weather(city):
    base_url = 'https://api.openweathermap.org/data/2.5/weather'
    w_params = {'q': city, 'units': 'metric', 'lang': 'ru', 'appid': os.environ.get('API_key')}
    w = requests.get(base_url, params=w_params)
    return w.json()

if __name__ == "__main__":
    city = input('Введите название города: ')
    w = get_weather(city)
    print(f"Температура в городе {city}: {w['main']['temp']} градусам, {w['weather'][0]['description']}")
