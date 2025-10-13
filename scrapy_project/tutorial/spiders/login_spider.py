"""
로그인 처리 데모 스파이더
- scrapy.http.FormRequest 클래스 사용
- CSRF 토큰 처리
- 세션 쿠키 자동 관리
- 로그인 후 보호된 페이지 접근
"""

import scrapy
from scrapy.http import FormRequest


class LoginSpider(scrapy.Spider):
    name = "login_spider"
    allowed_domains = ["quotes.toscrape.com"]
    start_urls = ["http://quotes.toscrape.com/login"]

    # 로그인을 위해 쿠키 활성화
    custom_settings = {"COOKIES_ENABLED": True}

    def parse(self, response):
        """로그인 페이지에서 폼 데이터 추출 및 로그인 요청 생성"""
        self.logger.info("🔐 로그인 페이지 접근 성공")

        # 1. CSRF 토큰 추출 (hidden input에서)
        csrf_token = response.css('form input[name="csrf_token"]::attr(value)').get()
        self.logger.info(
            f"🔑 CSRF 토큰 추출: {csrf_token[:20]}..."
            if csrf_token
            else "❌ CSRF 토큰 없음"
        )

        # 2. 폼의 action URL 확인
        form_action = response.css("form::attr(action)").get()
        login_url = response.urljoin(form_action) if form_action else response.url
        self.logger.info(f"📍 로그인 URL: {login_url}")

        # 3. FormRequest로 로그인 요청 생성
        return FormRequest.from_response(
            response,
            formdata={
                "csrf_token": csrf_token,
                "username": "user",  # 이미지에서 보여준 로그인 정보
                "password": "secret",
            },
            callback=self.after_login,
            dont_filter=True,  # 중복 필터 비활성화
        )

    def after_login(self, response):
        """로그인 후 처리"""
        # 디버깅: 로그인 응답 상세 정보 출력
        self.logger.info(f"🔍 로그인 후 응답 URL: {response.url}")
        self.logger.info(f"🔍 응답 상태: {response.status}")
        self.logger.info(f"🔍 응답 텍스트 일부: {response.text[:200]}...")

        # 로그인 성공 여부 확인
        if "Logout" in response.text:
            self.logger.info("✅ 로그인 성공!")

            # 로그인 후 보호된 페이지들에 접근
            yield response.follow(
                "/author/Albert-Einstein", callback=self.parse_author_page
            )
            yield response.follow("/", callback=self.parse_main_page)

        else:
            self.logger.error("❌ 로그인 실패")
            # 에러 정보 출력
            self.logger.error(f"응답 URL: {response.url}")
            self.logger.error(f"응답 상태: {response.status}")

            # 로그인 실패 원인 분석
            if "Please enter a correct username and password" in response.text:
                self.logger.error("🚫 잘못된 사용자명 또는 비밀번호")
            elif "csrf" in response.text.lower():
                self.logger.error("🚫 CSRF 토큰 문제")
            else:
                self.logger.error("🚫 알 수 없는 로그인 실패 원인")

            # 실제 웹사이트 확인을 위해 간단한 데이터 수집
            yield {
                "type": "login_failure_debug",
                "url": response.url,
                "status": response.status,
                "has_login_form": bool(response.css('form input[name="username"]')),
                "has_csrf_token": bool(response.css('form input[name="csrf_token"]')),
                "page_title": response.css("title::text").get(),
            }

    def parse_author_page(self, response):
        """작가 페이지 파싱 (로그인 후에만 접근 가능한 정보 포함)"""
        self.logger.info(f"📖 작가 페이지 접근: {response.url}")

        # 작가 정보 추출
        author_name = response.css("h3.author-title::text").get()
        author_born = response.css(".author-born-date::text").get()
        author_location = response.css(".author-born-location::text").get()
        author_description = response.css(".author-description::text").get()

        yield {
            "type": "author_info",
            "name": author_name.strip() if author_name else None,
            "born_date": author_born.strip() if author_born else None,
            "born_location": author_location.strip() if author_location else None,
            "description": author_description.strip() if author_description else None,
            "url": response.url,
        }

    def parse_main_page(self, response):
        """메인 페이지에서 로그인 상태 확인"""
        self.logger.info("🏠 메인 페이지 접근 (로그인 상태)")

        # 로그아웃 링크가 있는지 확인
        logout_link = response.css('a[href="/logout"]::text').get()
        if logout_link:
            self.logger.info("✅ 로그인 상태 확인됨 - Logout 링크 발견")

            # 로그인 상태에서만 보이는 정보들 수집
            quotes = response.css("div.quote")
            for quote in quotes[:3]:  # 처음 3개만
                text = quote.css("span.text::text").get()
                author = quote.css("small.author::text").get()
                tags = quote.css("div.tags a.tag::text").getall()

                yield {
                    "type": "logged_in_quote",
                    "text": text,
                    "author": author,
                    "tags": tags,
                    "login_status": "authenticated",
                }
        else:
            self.logger.warning("⚠️ 로그인 상태가 아님")
