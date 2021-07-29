# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstaparserItem(scrapy.Item):
    # define the fields for your item here like:
    parent_name = scrapy.Field()
    parent_id = scrapy.Field()
    name = scrapy.Field()
    user_id = scrapy.Field()
    type = scrapy.Field()
    photo = scrapy.Field()
    _id = scrapy.Field()




