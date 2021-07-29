from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from instaparser.spiders.instagram import InstagramSpider
from instaparser import settings
from pymongo import MongoClient

if __name__ == '__main__':

    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(InstagramSpider)

    process.start()
    client = MongoClient('localhost', 27017)
    db = client['instagram']

    collection = db.followers_and_following

    user_name = 'raikov_workshop'

    with open('followers.txt', 'w') as file:
        for doc in collection.find({'$and': [{'parent_name': user_name}, {'type': 'followers'}]}):
            file.write(f'{str(doc)} \n')

    with open('following.txt', 'w') as file:
        for doc in collection.find({'$and': [{'parent_name': user_name}, {'type': 'following'}]}):
            file.write(f'{str(doc)} \n')