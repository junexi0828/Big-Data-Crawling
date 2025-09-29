import scrapy


class QuotesSpider(scrapy.Spider):
    name = "quotes"

    def start_requests(self):
        """Spider Arguments를 사용한 태그 필터링"""
        url = "http://quotes.toscrape.com/"
        tag = getattr(self, "tag", None)
        if tag is not None:
            url = url + "tag/" + tag
            self.logger.info(f"🏷️ 태그 필터링: {tag}")
        yield scrapy.Request(url, self.parse)

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
