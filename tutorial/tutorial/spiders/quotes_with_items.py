#!/usr/bin/env python3
"""
이미지 슬라이드에 맞는 QuotesItem 사용 스파이더
- 이미지의 ComplexQuotesSpider 리뷰 내용 구현
- QuotesItem을 사용한 Item 기반 데이터 수집
"""
import scrapy
from tutorial.items import QuotesItem


class QuotesWithItemsSpider(scrapy.Spider):
    name = "quotes_with_items"
    start_urls = ["http://quotes.toscrape.com"]

    def parse(self, response):
        """명언 페이지 파싱 - 이미지의 ComplexQuotesSpider와 동일"""
        for q in response.css("div.quote"):
            # QuotesItem 인스턴스 생성
            quote_item = QuotesItem()

            # 이미지에서 강조된 필드들 매핑
            quote_item["quote_content"] = q.css(
                "span.text::text"
            ).get()  # text → quote_content
            quote_item["author_name"] = q.css(
                "small.author::text"
            ).get()  # author → author_name
            quote_item["tags"] = q.css("div.tags a.tag::text").getall()  # tags → tags

            # 명언 데이터 먼저 yield
            yield quote_item

        # 작가 링크들을 따라가서 작가 정보 수집
        yield from response.follow_all(q.css(".author + a"), self.parse_author)

        # 다음 페이지로 이동
        yield from response.follow_all(response.css("li.next a"), callback=self.parse)

    def parse_author(self, response):
        """작가 상세 정보 파싱 - 이미지의 필드명과 일치"""
        author_item = QuotesItem()

        # 이미지에서 강조된 필드들 매핑
        author_item["author_name"] = (
            response.css(".author-title::text").get().strip()
        )  # name → author_name
        author_item["birthdate"] = response.css(
            ".author-born-date::text"
        ).get()  # birthdate → birthdate
        author_item["birthplace"] = response.css(
            ".author-born-location::text"
        ).get()  # birthplace → birthplace
        author_item["bio"] = (
            response.css(".author-description::text").get().strip()
        )  # bio → bio

        yield author_item
