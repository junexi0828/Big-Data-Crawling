#!/usr/bin/env python3
"""
기존 방식 vs response.follow() 방식 실제 코드 비교
"""

import scrapy

print("🔍 실제 코드 비교 - 기존 방식 vs response.follow()")
print("=" * 60)

print("\n📝 1. 기존 방식 (Manual Request Creation)")
print("-" * 40)
old_code = """
class QuotesSpider(scrapy.Spider):
    def parse(self, response):
        # 데이터 추출
        for quote in response.css("div.quote"):
            yield {...}

        # 다음 페이지 링크 처리 (복잡한 과정)
        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            # 1단계: 상대경로를 절대경로로 변환
            next_page = response.urljoin(next_page)
            # 2단계: Request 객체 수동 생성
            yield scrapy.Request(next_page, callback=self.parse)
"""
print(old_code)

print("\n📝 2. response.follow() 방식 (Automatic)")
print("-" * 40)
new_code = """
class QuotesSpider(scrapy.Spider):
    def parse(self, response):
        # 데이터 추출
        for quote in response.css("div.quote"):
            yield {...}

        # 다음 페이지 링크 처리 (간단!)
        for a in response.css("ul.pager a"):
            yield response.follow(a, callback=self.parse)
"""
print(new_code)

print("\n🔄 3. 내부 동작 과정 상세 분석")
print("-" * 40)

print("\n기존 방식의 단계:")
print("1️⃣ CSS 셀렉터로 href 속성 추출")
print("2️⃣ None 체크")
print("3️⃣ response.urljoin()으로 절대경로 변환")
print("4️⃣ scrapy.Request() 수동 생성")
print("5️⃣ callback 함수 지정")
print("6️⃣ yield로 반환")

print("\nresponse.follow() 방식:")
print("1️⃣ CSS 셀렉터로 요소 선택")
print("2️⃣ response.follow()가 모든 것을 자동 처리!")
print("   ↳ href 추출, 경로 변환, Request 생성, 콜백 설정 등")

print("\n💡 4. 핵심 차이점")
print("-" * 40)
print("기존 방식:")
print("❌ 6줄의 코드")
print("❌ 수동 경로 처리")
print("❌ None 체크 필요")
print("❌ 실수하기 쉬움")

print("\nresponse.follow() 방식:")
print("✅ 2줄의 코드")
print("✅ 자동 경로 처리")
print("✅ 자동 예외 처리")
print("✅ 실수 가능성 낮음")

print("\n🎯 5. 실제 크롤링에서의 동작")
print("-" * 40)
print("웹페이지에서 이런 HTML을 만나면:")
print('<ul class="pager">')
print('  <li class="previous"><a href="/page/1/">←</a></li>')
print('  <li class="next"><a href="/page/3/">Next</a></li>')
print("</ul>")

print("\nresponse.follow()는 자동으로:")
print("1. 두 개의 링크를 모두 감지")
print("2. '/page/1/' → 'http://quotes.toscrape.com/page/1/'")
print("3. '/page/3/' → 'http://quotes.toscrape.com/page/3/'")
print("4. 각각에 대해 Request 객체 생성")
print("5. 크롤링 스케줄러에 등록")

print("\n🚀 결론: response.follow()는 개발자의 삶을 편하게 만들어줍니다!")
