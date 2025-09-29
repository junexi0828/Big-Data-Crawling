import scrapy
from scrapy.loader import ItemLoader
from tutorial.items import QuotesItem


class ComplexQuotesSpider(scrapy.Spider):
    name = "complex_quotes"
    start_urls = ["http://quotes.toscrape.com"]

    # 3. Add custom_settings block to your spider ← spider-wise! (이미지 방법 3)
    custom_settings = {
        "DUPEFILTER_CLASS": "scrapy.dupefilters.BaseDupeFilter",
    }

    def parse(self, response):
        self.logger.info("[parse] called while crawling {}".format(response.url))
        for q in response.css("div.quote"):  # response.xpath("//div[@class='quote']")
            loader = ItemLoader(item=QuotesItem(), selector=q)
            loader.add_css("quote_content", "span.text::text")
            loader.add_css("tags", "div.tags a.tag::text")

            current_quote = loader.load_item()  # populate a QuotesItem
            author_url = q.css(".author + a::attr(href)").get()  # go to author page
            yield response.follow(
                author_url, self.parse_author, meta={"quote_item": current_quote}
            )

        # go to Next page
        yield from response.follow_all(response.css("li.next a"), self.parse)

    def parse_author(self, response):
        current_quote = response.meta["quote_item"]
        loader = ItemLoader(item=current_quote, response=response)
        loader.add_css("author_name", ".author-title::text")
        loader.add_css("birthdate", ".author-born-date::text")
        loader.add_css("birthplace", ".author-born-location::text")
        loader.add_css("bio", ".author-description::text")
        yield loader.load_item()
