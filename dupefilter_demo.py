#!/usr/bin/env python3
"""
Scrapy의 DUPEFILTER_CLASS 중복 필터 기능 데모
기본적으로 Scrapy는 이미 방문한 URL에 대한 요청을 필터링합니다.
"""
import scrapy
from scrapy.crawler import CrawlerProcess


class DupeFilterTestSpider(scrapy.Spider):
    name = "dupefilter_test"
    start_urls = [
        "http://quotes.toscrape.com/page/1/",
        "http://quotes.toscrape.com/page/1/",  # 중복 URL
        "http://quotes.toscrape.com/page/2/",
        "http://quotes.toscrape.com/page/1/",  # 또 다른 중복 URL
    ]

    def parse(self, response):
        print(f"📄 처리 중인 페이지: {response.url}")

        quotes = response.css("div.quote")
        print(f"🔍 발견된 명언 수: {len(quotes)}개")

        for q in quotes:
            yield {
                "text": q.css("span.text::text").get(),
                "author": q.css("small.author::text").get(),
                "tags": q.css("div.tags a.tag::text").getall(),
            }

        # 동일한 페이지에 대한 중복 요청 생성
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            print(f"➡️ 다음 페이지로 이동: {next_page}")
            yield response.follow(next_page, callback=self.parse)

            # 중복 요청 시도 (필터링될 예정)
            yield response.follow(next_page, callback=self.parse)
            yield response.follow(next_page, callback=self.parse)


def test_with_dupefilter():
    """중복 필터 활성화된 상태로 테스트"""
    print("🚀 중복 필터 활성화 테스트 시작!")
    process = CrawlerProcess(
        {
            "USER_AGENT": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "ROBOTSTXT_OBEY": False,
            "DOWNLOAD_DELAY": 0.5,
            "DUPEFILTER_DEBUG": True,  # 중복 필터 디버그 로그 활성화
            "LOG_LEVEL": "INFO",
            "FEEDS": {
                "dupefilter_with_filter.json": {
                    "format": "json",
                    "encoding": "utf8",
                    "overwrite": True,
                },
            },
        }
    )
    process.crawl(DupeFilterTestSpider)
    process.start()


def test_without_dupefilter():
    """중복 필터 비활성화된 상태로 테스트"""
    print("🚀 중복 필터 비활성화 테스트 시작!")
    process = CrawlerProcess(
        {
            "USER_AGENT": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "ROBOTSTXT_OBEY": False,
            "DOWNLOAD_DELAY": 0.5,
            "DUPEFILTER_CLASS": "scrapy.dupefilters.BaseDupeFilter",  # 중복 필터 비활성화
            "LOG_LEVEL": "INFO",
            "FEEDS": {
                "dupefilter_without_filter.json": {
                    "format": "json",
                    "encoding": "utf8",
                    "overwrite": True,
                },
            },
        }
    )
    process.crawl(DupeFilterTestSpider)
    process.start()


if __name__ == "__main__":
    print("📋 Scrapy DUPEFILTER_CLASS 데모")
    print("📚 중복 URL 요청이 어떻게 처리되는지 확인해보세요")
    print()
    print("1. 중복 필터 활성화 (기본값)")
    print("2. 중복 필터 비활성화")

    choice = input("\n번호를 입력하세요 (1 또는 2): ").strip()

    if choice == "1":
        test_with_dupefilter()
    elif choice == "2":
        test_without_dupefilter()
    else:
        print("❌ 잘못된 선택입니다. 1 또는 2를 입력해주세요.")
