#!/usr/bin/env python3
"""
response.follow() 방식 상세 설명 및 예제
"""


# 1. 기존 방식 (Manual Request Creation)
def old_way_example(response):
    """기존 방식: 수동으로 Request 객체 생성"""
    print("=== 기존 방식 ===")

    # 1단계: href 속성 추출
    next_page = response.css("li.next a::attr(href)").get()
    print(f"1. href 추출: {next_page}")

    # 2단계: 상대경로를 절대경로로 변환
    if next_page is not None:
        full_url = response.urljoin(next_page)
        print(f"2. 절대경로 변환: {full_url}")

        # 3단계: Request 객체 수동 생성
        request = scrapy.Request(full_url, callback=self.parse)
        print(f"3. Request 객체 생성: {request}")

        yield request


# 2. 새로운 방식 (response.follow())
def new_way_example(response):
    """새로운 방식: response.follow() 사용"""
    print("=== 새로운 방식 ===")

    # 한 번에 처리!
    for a in response.css("ul.pager a"):
        print(f"링크 요소: {a.get()}")
        yield response.follow(a, callback=self.parse)
        print("✅ response.follow()가 모든 것을 자동 처리!")


# 3. response.follow()가 자동으로 해주는 일들
def what_follow_does():
    """response.follow()의 내부 동작"""

    print("\n🤖 response.follow()가 자동으로 해주는 일들:")
    print("1️⃣ href 속성 자동 추출")
    print("2️⃣ 상대경로 → 절대경로 자동 변환")
    print("3️⃣ Request 객체 자동 생성")
    print("4️⃣ 적절한 HTTP 헤더 자동 설정")
    print("5️⃣ 인코딩 문제 자동 처리")


# 4. 다양한 사용 방법
def follow_usage_examples():
    """response.follow() 사용 방법들"""

    print("\n📚 response.follow() 사용 방법들:")

    # 방법 1: CSS 셀렉터로 직접 선택
    print("방법 1: CSS 셀렉터 직접 사용")
    print("yield response.follow('li.next a', callback=self.parse)")

    # 방법 2: 요소 객체 전달
    print("\n방법 2: 요소 객체 전달")
    print("link = response.css('li.next a').get()")
    print("yield response.follow(link, callback=self.parse)")

    # 방법 3: 여러 링크 일괄 처리
    print("\n방법 3: 여러 링크 일괄 처리")
    print("for link in response.css('ul.pager a'):")
    print("    yield response.follow(link, callback=self.parse)")

    # 방법 4: URL 문자열 직접 전달
    print("\n방법 4: URL 문자열 직접 전달")
    print("yield response.follow('/page/2/', callback=self.parse)")


# 5. 실제 동작 과정 시뮬레이션
def simulate_follow_process():
    """response.follow() 동작 과정 시뮬레이션"""

    print("\n🔄 response.follow() 동작 과정:")

    # 가상의 HTML 요소
    html_element = '<a href="/page/2/">Next</a>'
    base_url = "http://quotes.toscrape.com/page/1/"

    print(f"입력: {html_element}")
    print(f"현재 페이지: {base_url}")

    print("\n단계별 처리:")
    print("1️⃣ href 추출: '/page/2/'")
    print("2️⃣ 절대경로 변환: 'http://quotes.toscrape.com/page/2/'")
    print("3️⃣ Request 생성: GET http://quotes.toscrape.com/page/2/")
    print("4️⃣ 콜백 함수 연결: callback=self.parse")
    print("5️⃣ 스케줄러에 등록: 크롤링 대기열에 추가")


if __name__ == "__main__":
    print("🚀 response.follow() 방식 완전 분석")
    print("=" * 50)

    what_follow_does()
    follow_usage_examples()
    simulate_follow_process()

    print("\n✨ 결론:")
    print("response.follow()는 복잡한 링크 처리를 한 줄로 간단하게!")
    print("개발자는 비즈니스 로직에만 집중할 수 있습니다!")
