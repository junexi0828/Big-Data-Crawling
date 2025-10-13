"""
복잡한 로그인 처리 데모 (2-pass login)
- 1단계: 로그인 페이지에서 CSRF 토큰 추출
- 2단계: CSRF 토큰과 함께 로그인 폼 제출
- Hidden 데이터가 복잡한 경우 사용
"""

import scrapy
from scrapy.http import Request, FormRequest


class ComplexLoginSpider(scrapy.Spider):
    name = "complex_login"
    start_urls = ["http://quotes.toscrape.com"]
    login_url = "http://quotes.toscrape.com/login"

    # 중복 필터 비활성화 및 쿠키 활성화
    custom_settings = {
        "DUPEFILTER_CLASS": "scrapy.dupefilters.BaseDupeFilter",
        "COOKIES_ENABLED": True,
    }

    def start_requests(self):
        """2-pass 로그인 1단계: 로그인 페이지 요청"""
        return [Request(self.login_url, callback=self.process_login)]

    def process_login(self, response):
        """2-pass 로그인 2단계: CSRF 토큰 추출 후 로그인 폼 제출"""
        # CSRF 토큰 추출
        csrf_token = response.xpath(
            '//input[@name="csrf_token"]/@value'
        ).extract_first()
        self.logger.info(f"🔑 [process_login] CSRF 토큰: {csrf_token}")

        # FormRequest.from_response를 사용하여 로그인 폼 제출
        yield FormRequest.from_response(
            response,
            formdata={
                "csrf_token": csrf_token,
                "username": "user",
                "password": "secret",
            },
            callback=self.parse,
        )

    def parse(self, response):
        """로그인 후 메인 페이지 처리"""
        self.logger.info(f"🏠 [parse] 메인 페이지 도착: {response.url}")

        # 로그인 성공 여부 확인
        if "Logout" in response.text:
            self.logger.info("✅ 복잡한 로그인 성공!")

            # quotes 수집
            quotes = response.css("div.quote")
            for quote in quotes[:5]:  # 처음 5개만
                text = quote.css("span.text::text").get()
                author = quote.css("small.author::text").get()
                tags = quote.css("div.tags a.tag::text").getall()

                yield {
                    "method": "complex_login",
                    "text": text,
                    "author": author,
                    "tags": tags,
                    "login_status": "success",
                }

        else:
            self.logger.error("❌ 복잡한 로그인 실패")
            yield {
                "method": "complex_login",
                "login_status": "failed",
                "url": response.url,
                "status": response.status,
            }
