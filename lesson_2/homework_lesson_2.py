import requests
import time
from bs4 import BeautifulSoup as bs


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


def get_page_data(html, f):
    soup = bs(html.text, 'lxml')
    ads = soup.find('div', class_='vacancy-serp').find_all('div', class_='vacancy-serp-item')
    for ad in ads:
        try:
            title = ad.find('a', {"data-qa": "vacancy-serp__vacancy-title"}).text
        except:
            title = ''
        try:
            price = ad.find('div', class_='vacancy-serp-item__sidebar').find('span').text.strip()
        except:
            price = ''
        try:
            url = ad.find('a', {"data-qa": "vacancy-serp__vacancy-title"}).get('href')
        except:
            url = ''

        f.write(title + ',' + price + ',' + url + ',spb.hh.ru')
        f.write('\n')


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

