import numpy as np
import scrapy
import pandas as pd


class AmazonItem(scrapy.Item):
    # define the fields for your item here like:
    product_name = scrapy.Field()
    product_ASIN = scrapy.Field()


class ASINScraper(scrapy.Spider):
    name = "ASIN_spider"

    def __init__(self, *args, **kwargs):
        super(ASINScraper, self).__init__(*args, **kwargs)

        self.start_urls = ["https://www.amazon.com/s?k=" + kwargs.get('search_term') + "&ref=nb_sb_noss_2"]

    def parse(self, response):
        name = response.xpath("//*[@id=\"search\"]/div[1]/div[2]/div/span[3]/div[2]/div[1]").extract()
        ASIN = response.xpath("//*[@id=\"search\"]/div[1]/div[2]/div/span[3]/div[2]/div[1]").extract()

        # for each product, create an AmazonItem, populate the fields and yield the item
        for result in zip(name, ASIN):
            item = AmazonItem()
            item.product_name = result[1]
            item.product_ASIN = result[0]
            yield item
