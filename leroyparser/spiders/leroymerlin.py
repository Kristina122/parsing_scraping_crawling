import scrapy
from scrapy.http import HtmlResponse
from scrapy.loader import ItemLoader
from leroyparser.items import LeroyparserItem

class LeroymerlinSpider(scrapy.Spider):
    name = 'leroymerlin'
    allowed_domains = ['leroymerlin.ru']
    start_urls = ['http://leroymerlin.ru/']

    def __init__(self, search):
        super(LeroymerlinSpider, self).__init__()
        self.start_urls = [f'https://leroymerlin.ru/search/?q={search}&suggest=true']

    def parse(self, response:HtmlResponse):
        product_links = response.xpath("//a[contains(@data-qa,'product-name')]")
        next_page = response.xpath("//a[contains(@data-qa-pagination-item,'right')]")

        for link in product_links:
            yield response.follow(link, callback=self.parse_goods)

        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_goods(self, response):
        loader = ItemLoader(item=LeroyparserItem(), response=response)
        loader.add_xpath('name', '//h1/text()' )
        loader.add_value('url', response.url)
        loader.add_xpath('price', '//span[@slot="price"]/text()')
        loader.add_xpath('article', '//span[@slot="article"]/text()')
        loader.add_xpath('text', '//uc-pdp-section-layout/uc-pdp-section-vlimited/div/p/text()')
        loader.add_xpath('photo', '//img[@alt="image thumb"]/@src')
        specifications_list = response.xpath('//dl[@class="def-list"]/child::div')
        loader.add_value('specifications', specifications_list)

        yield loader.load_item()