# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class AmazonclothItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    Division_Description = scrapy.Field()
    Department_Description = scrapy.Field()
    Sub_Department_Description = scrapy.Field()
    Brand_Desc = scrapy.Field()
    Color_Desc = scrapy.Field()
    Size_Desc = scrapy.Field()
    VSN = scrapy.Field()
    Wholesale_Price = scrapy.Field()
    pass
