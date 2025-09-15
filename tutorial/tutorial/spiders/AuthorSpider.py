import scrapy


class AuthorSpider(scrapy.Spider):
    name = "author"

    start_urls = ["http://quotes.toscrape.com/"]

    def parse(self, response):
        # response.follow_all을 사용한 더 간결한 방법
        yield from response.follow_all(response.css(".author + a"), self.parse_author)
        yield from response.follow_all(response.css("li.next a"), callback=self.parse)

    def parse_author(self, response):
        yield {
            "name": response.css(".author-title::text").get().strip(),
            "birthdate": response.css(".author-born-date::text").get(),
            "birthplace": response.css(".author-born-location::text").get(),
            "bio": response.css(".author-description::text").get().strip(),
        }
