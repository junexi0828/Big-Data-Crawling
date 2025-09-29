import scrapy
from tutorial.items import QuotesItem
from tutorial.itemloaders import QuotesItemLoader


class QuotesWithItemLoaderSpider(scrapy.Spider):
    name = "quotes_itemloader"
    start_urls = ["http://quotes.toscrape.com"]

    def parse(self, response):
        quotes = response.css("div.quote")

        for quote in quotes:
            # ItemLoader 인스턴스 생성
            loader = QuotesItemLoader(item=QuotesItem(), selector=quote)

            # 데이터 추가
            loader.add_css("quote_content", "span.text::text")
            loader.add_css("tags", "div.tags a.tag::text")
            loader.add_css("author_name", "small.author::text")

            # 작가 링크 따라가서 추가 정보 수집
            author_link = quote.css(".author + a::attr(href)").get()
            if author_link:
                yield response.follow(
                    author_link, self.parse_author, meta={"loader": loader}
                )
            else:
                # 작가 정보 없이도 명언 데이터 반환
                yield loader.load_item()

        # 페이지네이션 처리
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_author(self, response):
        # 이전 페이지에서 전달받은 loader 사용
        loader = response.meta["loader"]

        # 작가 정보 추가
        loader.add_css("birthdate", ".author-born-date::text")
        loader.add_css("birthplace", ".author-born-location::text")
        loader.add_css("bio", ".author-description::text")

        # 완성된 아이템 반환
        yield loader.load_item()
