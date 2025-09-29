# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class TutorialItem(scrapy.Item):
    # define the fields for your item here like:
    quote = scrapy.Field()
    author = scrapy.Field()


class QuotesItem(scrapy.Item):
    """명언 수집을 위한 Item 클래스"""
    quote_content = scrapy.Field()
    tags = scrapy.Field()
    author_name = scrapy.Field()
    birthdate = scrapy.Field()
    birthplace = scrapy.Field()
    bio = scrapy.Field()
