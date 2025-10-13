"""
로그인 후 데이터 수집 스파이더 (login_quotes)
- ItemLoader와 QuotesItem 활용
- 2-pass 로그인 방식 (CSRF 토큰 처리)
- 로그인 후 여러 페이지 크롤링
"""

import scrapy
from scrapy.loader import ItemLoader
from tutorial.items import QuotesItem
from scrapy.http import Request
from scrapy.http import FormRequest


class LoginQuotesSpider(scrapy.Spider):
    name = "login_quotes"
    start_urls = ["http://quotes.toscrape.com"]
    login_url = "http://quotes.toscrape.com/login"

    custom_settings = {
        "DUPEFILTER_CLASS": "scrapy.dupefilters.BaseDupeFilter",
        "COOKIES_ENABLED": True,
    }

    def start_requests(self):
        """로그인 페이지로 이동"""
        return [Request(self.login_url, callback=self.process_login)]

    def process_login(self, response):
        """CSRF 토큰 추출 후 로그인 폼 제출"""
        csrf_token = response.xpath(
            "//input[@name='csrf_token']/@value"
        ).extract_first()
        self.logger.info(f"🔑 [process_login] csrf_token: {csrf_token}")

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
        """로그인 후 메인 페이지 크롤링"""
        self.logger.info(f"📖 [parse] called while crawling {response.url}")

        # 로그인 성공 확인
        if "Logout" not in response.text:
            self.logger.error("❌ 로그인 실패!")
            return

        self.logger.info("✅ 로그인 성공! 데이터 수집 시작...")

        # quotes 수집
        for q in response.css("div.quote"):
            loader = ItemLoader(item=QuotesItem(), selector=q)
            loader.add_css("quote_content", "span.text::text")
            loader.add_css("author_name", "small.author::text")
            loader.add_css("tags", "div.tags a.tag::text")

            current_quote = loader.load_item()

            # 작가 페이지 URL 추출
            author_url = q.css("small.author ~ a::attr(href)").get()
            if author_url:
                current_quote["author_url"] = response.urljoin(author_url)

            yield current_quote

        # 다음 페이지로 이동
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            self.logger.info(f"➡️ 다음 페이지로 이동: {next_page}")
            yield response.follow(next_page, callback=self.parse)
