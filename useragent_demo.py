#!/usr/bin/env python3
"""
USER-AGENT 사용법 완전 데모 - 이미지 슬라이드 구현
- Some sites block crawlers with User-agent headers!
- Web-server simply ignores requests from a specific useragent
- Identify S/W agent that sends HTTP(S) request
"""
import subprocess
import os
import requests


def demo_useragent_blocking():
    """User-Agent로 인한 차단 데모"""
    print("🚫 USER-AGENT usage - Some sites block crawlers with User-agent headers!")
    print("=" * 80)
    print("Web-server simply ignores requests from a specific useragent.")
    print()

    print("🌐 이미지에서 보여준 시나리오:")
    print("• scrapy shell http://www.todayhumor.co.kr/")
    print("• 성공적으로 접근 가능 (response = <200 http://www.todayhumor.co.kr/>)")
    print("• 하지만 일부 사이트는 특정 User-Agent를 차단함")
    print()


def demo_well_known_useragents():
    """잘 알려진 User-Agent 목록"""
    print("🌍 Several well-known useragents such as web browsers")
    print("=" * 60)

    useragents = [
        ("Mozilla/5.0 (Windows NT 6.2; WOW64)", "Old Windows"),
        ("AppleWebKit/537.36 (KHTML, like Gecko)", "WebKit 기반"),
        ("Chrome/27.0.1453.93, Safari/537.36", "Chrome/Safari"),
    ]

    for ua, description in useragents:
        print(f"• {ua}")
        print(f"  → {description}")
    print()


def demo_scrapy_useragent_change():
    """Scrapy에서 User-Agent 변경 방법"""
    print('🔧 Change setting ← default: "Scrapy/VERSION (+https://scrapy.org)"')
    print("=" * 70)

    print("📋 이미지에서 보여준 방법들:")
    print()

    # 1. Command line 방법
    print("1️⃣ Command line 옵션:")
    print('   scrapy shell http://www.todayhumor.co.kr/ -s USER_AGENT="Safari/537.36"')
    print()

    # 2. settings.py 방법
    print("2️⃣ settings.py 파일 수정:")
    print(
        "   # Crawl responsibly by identifying yourself (and your website) on the user-agent"
    )
    print('   #USER_AGENT = "quotes (+http://www.yourdomain.com)"')
    print('   USER_AGENT = "Safari/537.36"  # Set to some proper values!')
    print()

    print('💡 이미지의 주요 메시지: "Set to some proper values!"')


def demo_practical_useragent_rotation():
    """실용적인 User-Agent 회전 데모"""
    print("\n🔄 실용적인 User-Agent 회전 기법")
    print("=" * 50)

    useragent_list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0",
    ]

    print("📱 다양한 User-Agent 목록:")
    for i, ua in enumerate(useragent_list, 1):
        browser_type = (
            "Chrome" if "Chrome" in ua else "Firefox" if "Firefox" in ua else "기타"
        )
        os_type = "Windows" if "Windows" in ua else "Mac" if "Mac" in ua else "Linux"
        print(f"{i}. {browser_type} on {os_type}")
        print(f"   {ua[:60]}...")
    print()


def create_useragent_spider():
    """User-Agent를 사용하는 스파이더 생성"""
    print("🕷️ User-Agent 회전 스파이더 예제")
    print("=" * 50)

    spider_code = """
import scrapy
import random

class UserAgentSpider(scrapy.Spider):
    name = 'useragent_spider'

    # 다양한 User-Agent 목록
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    ]

    def start_requests(self):
        urls = ['http://quotes.toscrape.com']
        for url in urls:
            # 랜덤한 User-Agent 선택
            user_agent = random.choice(self.user_agents)
            yield scrapy.Request(
                url=url,
                headers={'User-Agent': user_agent},
                callback=self.parse,
                meta={'user_agent': user_agent}
            )

    def parse(self, response):
        used_ua = response.meta.get('user_agent', 'Unknown')
        self.logger.info(f"사용된 User-Agent: {used_ua}")

        for quote in response.css('div.quote'):
            yield {
                'text': quote.css('span.text::text').get(),
                'author': quote.css('small.author::text').get(),
                'user_agent_used': used_ua,
            }
"""

    print("📄 User-Agent 회전 스파이더 코드:")
    print(spider_code)

    # 파일로 저장
    with open(
        "/Users/juns/bigdata/tutorial/tutorial/spiders/useragent_spider.py",
        "w",
        encoding="utf-8",
    ) as f:
        f.write(spider_code.strip())

    print("💾 파일 저장: tutorial/tutorial/spiders/useragent_spider.py")


def demo_scrapy_shell_useragent():
    """Scrapy Shell에서 User-Agent 테스트"""
    print("\n🐚 Scrapy Shell에서 User-Agent 테스트")
    print("=" * 50)

    print("📋 이미지 시나리오 재현:")
    print("1️⃣ 기본 Scrapy User-Agent로 접속:")
    print("   scrapy shell http://www.todayhumor.co.kr/")
    print("   → response = <200 http://www.todayhumor.co.kr/>")
    print()

    print("2️⃣ Safari User-Agent로 접속:")
    print('   scrapy shell http://www.todayhumor.co.kr/ -s USER_AGENT="Safari/537.36"')
    print("   → User-Agent 헤더가 변경되어 접속")
    print()

    print("3️⃣ Chrome User-Agent로 접속:")
    print(
        '   scrapy shell http://www.todayhumor.co.kr/ -s USER_AGENT="Chrome/91.0.4472.124"'
    )
    print("   → 실제 브라우저처럼 위장하여 접속")
    print()

    print("💡 실제 테스트 명령어:")
    print("   cd /Users/juns/bigdata/tutorial")
    print('   scrapy shell "http://quotes.toscrape.com" -s USER_AGENT="Safari/537.36"')
    print("   그 후 response.request.headers를 확인해보세요!")


if __name__ == "__main__":
    print("🎯 USER-AGENT 사용법 완전 데모")
    print("=" * 80)
    print("Identify S/W agent that sends HTTP(S) request")
    print()

    # 1. User-Agent 차단 데모
    demo_useragent_blocking()

    # 2. 잘 알려진 User-Agent 소개
    demo_well_known_useragents()

    # 3. Scrapy에서 User-Agent 변경 방법
    demo_scrapy_useragent_change()

    # 4. 실용적인 User-Agent 회전
    demo_practical_useragent_rotation()

    # 5. User-Agent 스파이더 생성
    create_useragent_spider()

    # 6. Scrapy Shell 테스트
    demo_scrapy_shell_useragent()

    print("\n✅ USER-AGENT 데모 완료!")
    print(
        "웹 서버가 특정 User-Agent를 차단하는 경우, 브라우저로 위장하여 접근할 수 있습니다! 🌐"
    )
