#!/usr/bin/env python3
"""
Ethical Crawlers 완전 데모 - 이미지 슬라이드의 모든 내용 구현
- Respect robots.txt
- Never degrade website's performance
- Identify creator with contact information
- Don't cause pain for system administrator
"""
import scrapy
from scrapy.crawler import CrawlerProcess
import requests
import subprocess
import os


def demo_robots_txt():
    """robots.txt 데모"""
    print("🤖 robots.txt 데모")
    print("=" * 50)

    print("📋 robots.txt의 5가지 주요 용어:")
    print("• User-agent: 사용자 에이전트 지정")
    print("• Disallow: 크롤링 금지 URL")
    print("• Allow: 크롤링 허용 URL")
    print("• Crawl-delay: 요청 간 지연 시간")
    print("• Sitemap: 사이트맵 위치")
    print()

    print("🌐 실제 robots.txt 확인:")

    # 실제 robots.txt 확인
    sites = [
        "https://www.naver.com/robots.txt",
        "https://www.google.com/robots.txt",
        "https://quotes.toscrape.com/robots.txt",
    ]

    for site in sites:
        try:
            response = requests.get(site, timeout=5)
            if response.status_code == 200:
                print(f"✅ {site}: 접근 가능")
                lines = response.text.split("\\n")[:10]  # 처음 10줄만
                for line in lines:
                    if line.strip():
                        print(f"   {line}")
                print("   ...")
            else:
                print(f"❌ {site}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {site}: 접근 실패 - {e}")
        print()


def demo_scrapy_settings():
    """Scrapy 윤리적 설정 데모"""
    print("⚙️ Scrapy 윤리적 설정")
    print("=" * 50)

    print("📋 settings.py의 주요 윤리적 설정들:")
    print()

    print("1️⃣ robots.txt 준수:")
    print("   ROBOTSTXT_OBEY = True")
    print("   HTTPCACHE_ENABLED = True")
    print()

    print("2️⃣ 크롤러 신원 확인:")
    print("   USER_AGENT = 'MyCompany-MyCrawler (bot@mycompany.com)'")
    print()

    print("3️⃣ 웹사이트 성능 보호:")
    print("   DOWNLOAD_DELAY = 5.0  # 기본값은 0")
    print("   # Scrapy는 [0.5 ~ 1.5] x DOWNLOAD_DELAY 범위의 랜덤 지연 사용")
    print("   # 정확한 지연 시간 사용하려면 RANDOMIZE_DOWNLOAD_DELAY 비활성화")
    print()

    print("4️⃣ 동시 요청 제한:")
    print("   CONCURRENT_REQUESTS_PER_DOMAIN = 1")
    print("   # 모든 스파이더의 동시 요청 최대 개수 설정")
    print()

    print("5️⃣ AutoThrottle로 지연 시간 자동 조절:")
    print("   AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0")
    print("   # 요청 간 지연을 자동으로 조절")


def demo_scrapy_shell_robotstxt():
    """Scrapy Shell에서 robots.txt 확인"""
    print("\n🐚 Scrapy Shell에서 robots.txt 확인")
    print("=" * 50)

    print("📋 이미지에서 보여준 시나리오:")
    print("• scrapy shell https://finance.naver.com/marketindex/")
    print("• By default, robots.txt blocks scraping!")
    print()

    print("🔍 응답 확인:")
    print("• response == None  (robots.txt에 의해 차단됨)")
    print("• 'Forbidden by robots.txt' 메시지 출력")
    print()

    print("💡 해결 방법:")
    print("1️⃣ 프로젝트 전체 설정:")
    print("   Set 'ROBOTSTXT_OBEY = True' at the settings.py")
    print()

    print("2️⃣ Shell 세션별 설정:")
    print(
        "   scrapy shell https://finance.naver.com/marketindex/ -s ROBOTSTXT_OBEY=False"
    )
    print("   ← set additional option for this shell session!")
    print()

    print("3️⃣ 스파이더별 설정:")
    print("   scrapy crawl -s ROBOTSTXT_OBEY=False spider_name")
    print("   ← for this spider!")


def create_ethical_spider():
    """윤리적 크롤링 스파이더 생성"""
    print("\n🕷️ 윤리적 크롤링 스파이더 예제")
    print("=" * 50)

    spider_code = """
import scrapy

class EthicalSpider(scrapy.Spider):
    name = 'ethical_crawler'

    # 윤리적 크롤링 설정
    custom_settings = {
        'ROBOTSTXT_OBEY': True,
        'USER_AGENT': 'MyCompany-EthicalCrawler (contact@mycompany.com)',
        'DOWNLOAD_DELAY': 3.0,
        'RANDOMIZE_DOWNLOAD_DELAY': True,  # [0.5*3 ~ 1.5*3] 초 사이
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 60,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,
        'HTTPCACHE_ENABLED': True,
    }

    start_urls = ['http://quotes.toscrape.com']

    def parse(self, response):
        self.logger.info(f"윤리적으로 크롤링 중: {response.url}")

        # robots.txt 확인
        if hasattr(response, 'meta') and response.meta.get('download_timeout'):
            self.logger.warning("요청 시간 초과 - 서버 부하를 고려하여 대기")

        for quote in response.css('div.quote'):
            yield {
                'text': quote.css('span.text::text').get(),
                'author': quote.css('small.author::text').get(),
                'tags': quote.css('div.tags a.tag::text').getall(),
            }

        # 다음 페이지로 이동 (신중하게)
        next_page = response.css('li.next a::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)
"""

    print("📄 윤리적 스파이더 코드:")
    print(spider_code)

    # 파일로 저장
    with open(
        "/Users/juns/bigdata/tutorial/tutorial/spiders/ethical_spider.py",
        "w",
        encoding="utf-8",
    ) as f:
        f.write(spider_code.strip())

    print("💾 파일 저장: tutorial/tutorial/spiders/ethical_spider.py")


if __name__ == "__main__":
    print("🎯 Ethical Crawlers 완전 데모")
    print("=" * 80)
    print("Web crawlers: an essential component for many web applications")
    print("• search engine, digital library, online marketing, web data mining, ...")
    print("• crawlers are highly automated & seldom regulated manually")
    print("• crawler-generated visits significantly increase site traffic")
    print("  and can affect log statistics to overestimate real user traffic")
    print()

    print("🎭 Regular (Polite) Crawlers vs. Rogue (Nefarious) Crawlers")
    print("• regular crawl of web pages for general purpose indexing")
    print("• extraction of email & personal ID information, service attack")
    print()

    # 1. robots.txt 데모
    demo_robots_txt()

    # 2. Scrapy 설정 데모
    demo_scrapy_settings()

    # 3. Scrapy Shell 데모
    demo_scrapy_shell_robotstxt()

    # 4. 윤리적 스파이더 생성
    create_ethical_spider()

    print("\n🎯 Crawling the Web Politely! 4가지 원칙:")
    print("1️⃣ Respect robots.txt - Follow Allows and Disallows")
    print("2️⃣ Never degrade a website's performance - Follow Crawl-delay")
    print(
        "3️⃣ Identify its creator with contact information - Use request's User-agent header"
    )
    print("4️⃣ Don't cause pain for system administrator")
    print()

    print("✅ Ethical Crawlers 데모 완료!")
    print("모든 크롤러는 윤리적이고 정중하게 작동해야 합니다! 🤝")
