import scrapy
from tutorial.items import TutorialItem


class MybotSpider(scrapy.Spider):
    name = "mybot"
    allowed_domains = ["quotes.toscrape.com"]
    start_urls = ["https://quotes.toscrape.com"]

    def parse(self, response):
        for node in response.xpath("//div[@class='quote']"):
            print('found quote')
            item = TutorialItem()
            item["quote"] = node.xpath('span[1]/text()').extract_first()
            print("quote ==> ", item['quote'])
            item["author"] = node.xpath('span[2]/small/text()').extract_first()
            print("author ==> ", item['author'])
            yield item
