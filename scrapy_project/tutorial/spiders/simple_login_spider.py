"""
간단한 로그인 처리 데모 (1-pass login)
- FormRequest로 직접 로그인 폼 데이터 제출
- Hidden 데이터가 복잡하지 않은 경우 사용
- DUPEFILTER_CLASS 설정으로 중복 필터 비활성화
"""

import scrapy
from scrapy.http import FormRequest


class SimpleLoginSpider(scrapy.Spider):
    name = "simple_login"
    start_urls = ["http://quotes.toscrape.com"]
    login_url = "http://quotes.toscrape.com/login"

    # 중복 필터 비활성화 설정
    custom_settings = {
        "DUPEFILTER_CLASS": "scrapy.dupefilters.BaseDupeFilter",
        "COOKIES_ENABLED": True,
    }

    def start_requests(self):
        """간단한 1-pass 로그인: 직접 폼 데이터 제출"""
        return [
            FormRequest(
                self.login_url,
                formdata={"username": "user", "password": "secret"},
                callback=self.parse,
            )
        ]

    def parse(self, response):
        """로그인 후 메인 페이지 처리"""
        self.logger.info(f"🏠 메인 페이지 도착: {response.url}")

        # 로그인 성공 여부 확인
        if "Logout" in response.text:
            self.logger.info("✅ 간단 로그인 성공!")

            # quotes 수집
            quotes = response.css("div.quote")
            for quote in quotes[:5]:  # 처음 5개만
                text = quote.css("span.text::text").get()
                author = quote.css("small.author::text").get()
                tags = quote.css("div.tags a.tag::text").getall()

                yield {
                    "method": "simple_login",
                    "text": text,
                    "author": author,
                    "tags": tags,
                    "login_status": "success",
                }

        else:
            self.logger.error("❌ 간단 로그인 실패")
            yield {
                "method": "simple_login",
                "login_status": "failed",
                "url": response.url,
                "status": response.status,
            }
