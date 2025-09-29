#!/usr/bin/env python3
"""
윤리적 크롤링 및 USER-AGENT 사용법 데모
"""
import scrapy
from scrapy.crawler import CrawlerProcess
import random
import time


class EthicalCrawlerSpider(scrapy.Spider):
    name = "ethical_crawler"

    # 다양한 USER-AGENT 목록
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    ]

    def start_requests(self):
        urls = [
            "http://quotes.toscrape.com/",
            "http://quotes.toscrape.com/page/2/",
        ]

        for url in urls:
            # 랜덤 USER-AGENT 선택
            user_agent = random.choice(self.user_agents)

            yield scrapy.Request(
                url=url,
                callback=self.parse,
                headers={"User-Agent": user_agent},
                meta={"user_agent": user_agent},
            )

    def parse(self, response):
        user_agent = response.meta.get("user_agent", "Unknown")
        print(f"\n🌐 페이지 처리: {response.url}")
        print(f"🎭 사용된 USER-AGENT: {user_agent[:50]}...")
        print(f"📊 응답 상태: {response.status}")

        # robots.txt 준수 여부 확인
        print(f"🤖 robots.txt 준수: {self.settings.get('ROBOTSTXT_OBEY')}")

        # 다운로드 지연 정보
        delay = self.settings.get("DOWNLOAD_DELAY", 0)
        print(f"⏰ 다운로드 지연: {delay}초")

        quotes = response.css("div.quote")
        print(f"💬 발견된 명언: {len(quotes)}개")

        for i, quote in enumerate(quotes[:3], 1):  # 처음 3개만 처리
            quote_text = quote.css("span.text::text").get()
            author = quote.css("small.author::text").get()

            yield {
                "quote": quote_text,
                "author": author,
                "url": response.url,
                "user_agent": user_agent[:50] + "...",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            }

            print(f"  📝 명언 {i}: {author} - {quote_text[:30]}...")


def test_ethical_crawling():
    """윤리적 크롤링 테스트"""
    print("🚀 윤리적 크롤링 데모 시작!")
    print("=" * 60)

    process = CrawlerProcess(
        {
            # 윤리적 크롤링 설정
            "USER_AGENT": "EthicalBot/1.0 (+http://example.com/bot-info)",
            "ROBOTSTXT_OBEY": True,  # robots.txt 준수
            "DOWNLOAD_DELAY": 2,  # 2초 지연
            "RANDOMIZE_DOWNLOAD_DELAY": True,  # 지연 시간 랜덤화
            "CONCURRENT_REQUESTS_PER_DOMAIN": 1,  # 도메인당 동시 요청 1개
            # AutoThrottle 설정
            "AUTOTHROTTLE_ENABLED": True,
            "AUTOTHROTTLE_START_DELAY": 1,
            "AUTOTHROTTLE_MAX_DELAY": 10,
            "AUTOTHROTTLE_TARGET_CONCURRENCY": 1.0,
            "AUTOTHROTTLE_DEBUG": True,
            # HTTP 캐시 활성화
            "HTTPCACHE_ENABLED": True,
            "HTTPCACHE_EXPIRATION_SECS": 300,
            # 로그 설정
            "LOG_LEVEL": "INFO",
            # 결과 저장
            "FEEDS": {
                "ethical_crawling_result.json": {
                    "format": "json",
                    "encoding": "utf8",
                    "overwrite": True,
                },
            },
        }
    )

    process.crawl(EthicalCrawlerSpider)
    process.start()


def test_robots_txt_check():
    """robots.txt 확인 데모"""
    print("\n🤖 robots.txt 확인 데모")
    print("=" * 40)

    import urllib.robotparser

    sites = [
        "http://quotes.toscrape.com",
        "https://finance.naver.com",
        "https://www.google.com",
    ]

    for site in sites:
        print(f"\n🌐 사이트: {site}")
        try:
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(f"{site}/robots.txt")
            rp.read()

            # 일반적인 크롤러 확인
            user_agents = ["*", "Googlebot", "Scrapy"]

            for ua in user_agents:
                can_fetch = rp.can_fetch(ua, site + "/")
                status = "✅ 허용" if can_fetch else "❌ 차단"
                print(f"  🎭 {ua}: {status}")

        except Exception as e:
            print(f"  ⚠️ robots.txt 확인 실패: {e}")


if __name__ == "__main__":
    print("📋 윤리적 크롤링 및 USER-AGENT 데모")
    print("🎯 웹사이트를 존중하며 크롤링하는 방법을 배워봅시다")
    print()
    print("1. 윤리적 크롤링 테스트")
    print("2. robots.txt 확인")
    print("3. 모두 실행")

    choice = input("\n번호를 입력하세요 (1-3): ").strip()

    if choice == "1":
        test_ethical_crawling()
    elif choice == "2":
        test_robots_txt_check()
    elif choice == "3":
        test_robots_txt_check()
        print("\n" + "=" * 60)
        test_ethical_crawling()
    else:
        print("❌ 잘못된 선택입니다. 1-3 중에서 선택해주세요.")
