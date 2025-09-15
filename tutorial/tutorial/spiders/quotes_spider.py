import scrapy


class QuotesSpider(scrapy.Spider):
    name = "quotes"
    start_urls = [
        "http://quotes.toscrape.com/page/1/",
        "http://quotes.toscrape.com/page/2/",
        "http://quotes.toscrape.com/page/3/",
    ]

    def parse(self, response):
        self.logger.info("[quotes] first spider for quotes.toscrape.com!")
        quotes = response.css("div.quote")
        for q in quotes:
            yield {
                "text": q.css("span.text::text").get(),
                "author": q.css("small.author::text").get(),
                "tags": q.css("div.tags a.tag::text").getall(),
            }

        # 다음 페이지 링크 따라가기
        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)
