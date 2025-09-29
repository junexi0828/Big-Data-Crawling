#!/usr/bin/env python3
"""
response.follow() 방식을 사용한 Scrapy 스파이더 테스트 스크립트
"""
import scrapy
from scrapy.crawler import CrawlerProcess
import json
import os


class QuotesSpider(scrapy.Spider):
    name = "quotes"
    start_urls = ["http://quotes.toscrape.com"]

    def __init__(self):
        self.collected_items = []
        self.page_count = 0

    def parse(self, response):
        self.page_count += 1
        print(f"\n📄 명언 페이지 {self.page_count} 처리 중: {response.url}")
        print(f"📊 응답 상태: {response.status}")

        quotes = response.css("div.quote")
        print(f"🔍 발견된 명언 수: {len(quotes)}개")

        for i, q in enumerate(quotes, 1):
            item = {
                "text": q.css("span.text::text").get(),
                "author": q.css("small.author::text").get(),
                "tags": q.css("div.tags a.tag::text").getall(),
            }
            self.collected_items.append(item)
            print(f"  💬 명언 {i}: {item['author']} - {item['text'][:50]}...")
            yield item

        # response.follow() 메소드를 사용한 페이지 네비게이션
        pager_links = response.css("ul.pager a")
        print(f"🔗 발견된 페이지 링크: {len(pager_links)}개")
        for a in pager_links:
            link_text = a.css("::text").get()
            link_href = a.css("::attr(href)").get()
            print(f"  ➡️ 링크 따라가기: '{link_text}' -> {link_href}")
            yield response.follow(a, callback=self.parse)

    def closed(self, reason):
        print(f"\n✅ 명언 크롤링 완료!")
        print(f"📊 총 수집된 명언: {len(self.collected_items)}개")
        print(f"📄 처리된 페이지: {self.page_count}개")
        print(f"🔚 종료 이유: {reason}")


class AuthorSpider(scrapy.Spider):
    name = "author"
    start_urls = ["http://quotes.toscrape.com/"]

    def __init__(self):
        self.collected_authors = []
        self.page_count = 0

    def parse(self, response):
        self.page_count += 1
        print(f"\n👤 작가 페이지 {self.page_count} 처리 중: {response.url}")
        print(f"📊 응답 상태: {response.status}")

        # 작가 링크 찾기 및 따라가기
        author_links = response.css(".author + a")
        print(f"🔍 발견된 작가 링크: {len(author_links)}개")
        for author_link in author_links:
            author_name = author_link.css("::text").get()
            print(f"  👤 작가 링크 따라가기: {author_name}")
            yield response.follow(author_link, callback=self.parse_author)

        # 페이지 네비게이션
        page_links = response.css("li.next a")
        for page_link in page_links:
            print(f"  ➡️ 다음 페이지로 이동")
            yield response.follow(page_link, callback=self.parse)

    def parse_author(self, response):
        print(f"\n📝 작가 상세 페이지 처리 중: {response.url}")

        author_data = {
            "name": response.css(".author-title::text").get(),
            "birthdate": response.css(".author-born-date::text").get(),
            "birthplace": response.css(".author-born-location::text").get(),
            "bio": response.css(".author-description::text").get(),
        }

        # None 값들을 정리
        for key, value in author_data.items():
            if value:
                author_data[key] = value.strip()

        self.collected_authors.append(author_data)
        print(f"  ✨ 작가 정보 수집: {author_data['name']}")
        print(f"    📅 생년월일: {author_data['birthdate']}")
        print(f"    📍 출생지: {author_data['birthplace']}")

        yield author_data

    def closed(self, reason):
        print(f"\n✅ 작가 크롤링 완료!")
        print(f"👤 총 수집된 작가: {len(self.collected_authors)}명")
        print(f"📄 처리된 페이지: {self.page_count}개")
        print(f"🔚 종료 이유: {reason}")


def run_quotes_spider():
    print("\n🚀 명언 스파이더 시작!")
    process = CrawlerProcess(
        {
            "USER_AGENT": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "ROBOTSTXT_OBEY": False,
            "DOWNLOAD_DELAY": 0.5,
            "FEEDS": {
                "quotes_follow_output.json": {
                    "format": "json",
                    "encoding": "utf8",
                    "store_empty": False,
                    "overwrite": True,
                },
            },
        }
    )
    process.crawl(QuotesSpider)
    process.start()


def run_author_spider():
    print("\n🚀 작가 스파이더 시작!")
    process = CrawlerProcess(
        {
            "USER_AGENT": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "ROBOTSTXT_OBEY": False,
            "DOWNLOAD_DELAY": 0.5,
            "FEEDS": {
                "authors_output.json": {
                    "format": "json",
                    "encoding": "utf8",
                    "store_empty": False,
                    "overwrite": True,
                },
            },
        }
    )
    process.crawl(AuthorSpider)
    process.start()


if __name__ == "__main__":
    print("🚀 response.follow() 방식 Scrapy 스파이더 테스트!")
    print("🎯 대상 사이트: http://quotes.toscrape.com")
    print("\n어떤 스파이더를 실행하시겠습니까?")
    print("1. 명언 스파이더 (QuotesSpider)")
    print("2. 작가 스파이더 (AuthorSpider)")

    choice = input("\n번호를 입력하세요 (1 또는 2): ").strip()

    if choice == "1":
        run_quotes_spider()
        print("\n🎉 명언 크롤링 완료! quotes_follow_output.json 파일을 확인하세요.")
    elif choice == "2":
        run_author_spider()
        print("\n🎉 작가 크롤링 완료! authors_output.json 파일을 확인하세요.")
    else:
        print("❌ 잘못된 선택입니다. 1 또는 2를 입력해주세요.")
