import scrapy


class QuotesSpider(scrapy.Spider):
    name = "quotes"
    start_urls = ["http://quotes.toscrape.com"]

    def parse(self, response):
        self.logger.info("[quotes] first spider for quotes.toscrape.com!")
        quotes = response.css("div.quote")
        for q in quotes:
            yield {
                "text": q.css("span.text::text").get(),
                "author": q.css("small.author::text").get(),
                "tags": q.css("div.tags a.tag::text").getall(),
            }

        # response.follow() 메소드를 사용한 페이지 네비게이션
        for a in response.css("ul.pager a"):
            yield response.follow(a, callback=self.parse)
