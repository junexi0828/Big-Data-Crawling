야 새로운 import scrapy


class AuthorSpider(scrapy.Spider):
    name = "author"
    start_urls = ["http://quotes.toscrape.com/"]

    def parse(self, response):
        # 작가 링크 찾기 및 따라가기
        for author_link in response.css(".author + a"):
            yield response.follow(author_link, callback=self.parse_author)

        # 페이지 네비게이션
        for page_link in response.css("li.next a"):
            yield response.follow(page_link, callback=self.parse)

    def parse_author(self, response):
        yield {
            "name": response.css(".author-title::text").get().strip(),
            "birthdate": response.css(".author-born-date::text").get(),
            "birthplace": response.css(".author-born-location::text").get(),
            "bio": response.css(".author-description::text").get().strip(),
        }
