# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose, TakeFirst, Join
from tutorial.itemloaders import remove_mark, convert_date, parse_location


class TutorialItem(scrapy.Item):
    # define the fields for your item here like:
    quote = scrapy.Field()
    author = scrapy.Field()


class QuotesItem(scrapy.Item):
    """명언 수집을 위한 Item 클래스 - 이미지의 Finished items.py file 구현"""
    # Insert Field Definition Here (이미지에서 강조된 부분)
    quote_content = scrapy.Field(
        input_processor=MapCompose(remove_mark),
        output_processor=TakeFirst()
    )
    tags = scrapy.Field(
        output_processor=Join(', ')  # 이미지의 try: Join(', ') 구현
    )
    author_name = scrapy.Field(
        input_processor=MapCompose(str.strip),
        output_processor=TakeFirst()
    )
    birthdate = scrapy.Field(
        input_processor=MapCompose(convert_date),
        output_processor=TakeFirst()
    )
    birthplace = scrapy.Field(
        input_processor=MapCompose(parse_location),
        output_processor=TakeFirst()
    )
    bio = scrapy.Field(
        input_processor=MapCompose(str.strip),
        output_processor=TakeFirst()
    )
