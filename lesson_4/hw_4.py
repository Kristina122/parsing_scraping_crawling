import html as html
import requests
import time
from lxml import html
from pymongo import MongoClient
from pprint import pprint


client = MongoClient('localhost', 27017)
db = client['news']
news_data = db.news


def get_page(url, retry_number, sleep):
    for i in range(retry_number):
        try:
            headers = {
                'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/91.0.4472.124 Safari/537.36"
            }
            r = requests.get(url, headers=headers)
            if r.status_code != 200:
                raise Exception("Status code != 200")
            return r
        except:
            time.sleep(sleep)
    return None


def process_news_data(link, site_data):
    news_data_c = get_page(link, 5, 5)
    dom = html.fromstring(news_data_c.text)
    news_source = dom.xpath(site_data['source_xpath'])
    news_text = dom.xpath(site_data['text_xpath'])
    news_link = link
    news_date = dom.xpath(site_data['date_xpath'])
    news = {
        'source': news_source,
        'text': news_text,
        'link': news_link,
        'date': news_date
    }
    # pprint(news)
    insert_new(news)


def insert_new(news):
    vacs = news_data.count_documents({'link': news['link']})
    if vacs == 0:
        print('Новая новость:')
        pprint(news)
        news_data.insert_one(news)


def main():

    my_dict = {
        'mail': {
            'url': 'https://news.mail.ru/',
            'links_xpath': '//div[contains(@class,"cols__wrapper")]'
                           '//a[contains(@class,"link")]/@href',
            'source_xpath': '//a[contains(@class,"breadcrumbs__link")]//text()',
            'text_xpath': '//div[contains(@class,"article__text")]//text()',
            'date_xpath': '//span[contains(@class,"breadcrumbs__text") and contains(@class,"js-ago")]/@datetime'
        },
        'lenta': {
            'url': 'https://lenta.ru/',
            'links_xpath': '//section[contains(@class,"js-top-seven") or contains(@class,"b-top7-for-main")]'
                           '//div[contains(@class,"item") or contains(@class,"first-item")]',
            'source_xpath': '//p[@itemprop="author"]//text()',
            'text_xpath': '//div[@itemprop="articleBody"]//text()',
            'date_xpath': '//time[@pubdate]/@datetime'
        },
        'yandex': {
            'url': 'https://yandex.ru/news/',
            'links_xpath': '//div[contains(@class,"news-app__top") or contains(@class,"news-top-flexible-stories")]'
                           '//a/@href',
            'source_xpath': '//span[contains(@class,"news-story__subtitle-text")]//text()',
            'text_xpath': '//div[contains(@class,"news-story__annotation")]//text()',
            'date_xpath': '//span[contains(@class,"news-snippet-source-info__time")][1]//text()'
        }
    }
    for site, site_data in my_dict.items():
        site_url = site_data['url']
        resp = get_page(site_url, 5, 5)
        dom = html.fromstring(resp.text)
        news_links = dom.xpath(site_data['links_xpath'])
        for link in news_links:
            try:
                if not link.startswith('http'):
                    link = site_url + link
                if 'news' in link:
                    process_news_data(link, site_data)
            except:
                pprint(site)


if __name__ == "__main__":
    main()
