import scrapy
import json


class ScrollableSpider(scrapy.Spider):
    name = "scrollable_spider"
    allowed_domains = ["quotes.toscrape.com"]
    page = 1
    start_urls = ["http://quotes.toscrape.com/api/quotes?page=1"]

    def parse(self, response):
        # JSON 응답을 파이썬 딕셔너리로 변환
        data = json.loads(response.text)

        # quotes 데이터에서 각 quote 추출
        for quote in data["quotes"]:
            yield {
                "quote": quote["text"],
                "author": quote["author"]["name"],
                "tags": quote["tags"],
            }

        # 다음 페이지가 있는지 확인
        if data["has_next"]:
            self.page += 1
            next_page = f"http://quotes.toscrape.com/api/quotes?page={self.page}"
            yield scrapy.Request(url=next_page, callback=self.parse)
