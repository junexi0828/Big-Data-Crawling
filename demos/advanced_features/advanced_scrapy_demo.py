#!/usr/bin/env python3
"""
고급 Scrapy 기능 데모: response.follow_all, Spider Arguments, Complex Spiders
"""
import scrapy
from scrapy.crawler import CrawlerProcess
import subprocess
import os


def demo_spider_arguments():
    """Spider Arguments 데모"""
    print("🎯 Spider Arguments 데모")
    print("=" * 50)

    # 1. 태그 없이 실행
    print("\n1️⃣ 기본 실행 (모든 명언)")
    cmd = "cd /Users/juns/bigdata && source scrapy_env/bin/activate && cd tutorial && scrapy crawl quotes -s DOWNLOAD_DELAY=1 -s LOG_LEVEL=INFO -L INFO -o quotes_all.json"
    print(f"실행 명령어: {cmd.split('&&')[-1].strip()}")

    # 2. humor 태그로 필터링
    print("\n2️⃣ 태그 필터링 실행 (humor 태그만)")
    cmd2 = "cd /Users/juns/bigdata && source scrapy_env/bin/activate && cd tutorial && scrapy crawl quotes -a tag=humor -s DOWNLOAD_DELAY=1 -s LOG_LEVEL=INFO -L INFO -o quotes_humor.json"
    print(f"실행 명령어: {cmd2.split('&&')[-1].strip()}")

    # 3. love 태그로 필터링
    print("\n3️⃣ 태그 필터링 실행 (love 태그만)")
    cmd3 = "cd /Users/juns/bigdata && source scrapy_env/bin/activate && cd tutorial && scrapy crawl quotes -a tag=love -s DOWNLOAD_DELAY=1 -s LOG_LEVEL=INFO -L INFO -o quotes_love.json"
    print(f"실행 명령어: {cmd3.split('&&')[-1].strip()}")

    print("\n📝 실행 예시:")
    print("• scrapy crawl quotes                    # 모든 명언")
    print("• scrapy crawl quotes -a tag=humor       # humor 태그만")
    print("• scrapy crawl quotes -a tag=love        # love 태그만")
    print("• scrapy crawl quotes -a tag=inspirational # inspirational 태그만")


def demo_response_follow_all():
    """response.follow_all 데모"""
    print("\n🔗 response.follow_all 기능 설명")
    print("=" * 50)

    print(
        """
📚 기본 방식 vs response.follow_all 비교:

🔸 기본 방식 (반복문 사용):
    for author_link in response.css('.author + a'):
        yield response.follow(author_link, callback=self.parse_author)

    for page_link in response.css('li.next a'):
        yield response.follow(page_link, callback=self.parse)

🔸 response.follow_all 방식 (간결함):
    yield from response.follow_all(response.css('.author + a'), self.parse_author)
    yield from response.follow_all(response.css('li.next a'), callback=self.parse)

✅ 장점:
• 코드가 더 간결하고 읽기 쉬움
• 여러 링크를 한 번에 처리
• 자동으로 비동기 스케줄링됨
• 상대 URL 자동 처리
"""
    )


def demo_complex_spider():
    """ComplexQuotesSpider 데모"""
    print("\n🏗️ ComplexQuotesSpider 특징")
    print("=" * 50)

    print(
        """
🎯 ComplexQuotesSpider의 특징:

1️⃣ 동시 데이터 수집:
   • 명언 정보 (text, author, tags)
   • 작가 상세 정보 (name, birthdate, birthplace, bio)

2️⃣ 비동기 처리:
   • 명언과 작가 페이지가 비동기로 처리됨
   • 개별 작가 페이지가 해당 명언과 동기화되지 않을 수 있음

3️⃣ response.follow_all 활용:
   • 모든 작가 링크를 한 번에 처리
   • 모든 페이지네이션을 한 번에 처리

4️⃣ 실행 명령어:
   scrapy crawl complex_quotes -o complex_output.json
"""
    )


def show_scrapy_shell_examples():
    """Scrapy Shell 사용 예시"""
    print("\n🐚 Scrapy Shell 활용법")
    print("=" * 50)

    print(
        """
🔍 CSS 선택자 테스트:

1️⃣ Shell 시작:
   scrapy shell "http://quotes.toscrape.com"

2️⃣ 작가 링크 확인:
   response.css('.author + a::attr(href)').get()
   response.css('.author + a::attr(href)').getall()

3️⃣ 여러 요소 선택:
   anchors = response.css('.author + a')
   [a.css('::attr(href)').get() for a in anchors]

4️⃣ response.follow_all 테스트:
   requests = list(response.follow_all(response.css('.author + a')))
   len(requests)  # 생성된 요청 개수 확인

5️⃣ 복합 선택자:
   response.css('li.next a::attr(href)').get()
   response.css('div.quote .author::text').getall()
"""
    )


def demo_dupefilter_class():
    """DUPEFILTER_CLASS 설명"""
    print("\n🔄 DUPEFILTER_CLASS 동작 원리")
    print("=" * 50)

    print(
        """
🛡️ Scrapy의 중복 필터링:

📌 기본 동작:
• Scrapy는 기본적으로 이미 방문한 URL에 대한 요청을 필터링
• 동일한 URL로 여러 번 요청해도 한 번만 처리됨

📌 설정 옵션:
• DUPEFILTER_CLASS = 'scrapy.dupefilters.RFPDupeFilter'  (기본값)
• DUPEFILTER_CLASS = 'scrapy.dupefilters.BaseDupeFilter'  (비활성화)

📌 실제 예시:
같은 작가 페이지가 여러 명언에서 링크되어도 한 번만 크롤링됨

📌 디버깅:
• DUPEFILTER_DEBUG = True 설정으로 로그 확인 가능
• 로그에서 "Filtered duplicate request" 메시지 확인
"""
    )


if __name__ == "__main__":
    print("🚀 고급 Scrapy 기능 데모")
    print("🎯 response.follow_all, Spider Arguments, Complex Spiders")
    print()

    # 모든 데모 실행
    demo_spider_arguments()
    demo_response_follow_all()
    demo_complex_spider()
    show_scrapy_shell_examples()
    demo_dupefilter_class()

    print("\n🎉 모든 고급 기능이 구현되었습니다!")
    print("📚 위의 명령어들을 직접 실행해보세요.")
