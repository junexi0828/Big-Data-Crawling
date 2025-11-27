"""
Coinness News Spider
코인니스 암호화폐 뉴스 수집
"""

import scrapy
from datetime import datetime
from cointicker.items import CryptoNewsItem
from cointicker.itemloaders import CryptoNewsItemLoader


class CoinnessSpider(scrapy.Spider):
    name = "coinness"
    allowed_domains = ["coinness.com", "www.coinness.com"]

    start_urls = [
        "https://www.coinness.com/news",
        "https://www.coinness.com/news/list",
    ]

    custom_settings = {
        "DOWNLOAD_DELAY": 3,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
        # Selenium 미들웨어 활성화 (JavaScript 렌더링 필요)
        "SELENIUM_ENABLED_DOMAINS": ["coinness.com", "www.coinness.com"],
        "SELENIUM_HEADLESS": True,
        "SELENIUM_SCROLL": True,  # 동적 콘텐츠 로드를 위해 스크롤
    }

    def start_requests(self):
        """시작 요청 생성 (Selenium 활성화)"""
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                callback=self.parse,
                meta={"selenium": True},  # Selenium 미들웨어 사용
            )

    def parse(self, response):
        """메인 파싱 메서드"""
        self.logger.info(f"Parsing: {response.url}")

        # Selenium으로 렌더링된 페이지에서 뉴스 목록 추출
        # React 기반 SPA이므로 다양한 선택자 시도
        news_items = None

        # 선택자 우선순위: React 컴포넌트 구조에 맞게 조정
        selectors = [
            "article",
            'div[class*="News"]',
            'div[class*="news"]',
            'div[class*="Article"]',
            'div[class*="article"]',
            'div[class*="Item"]',
            'div[class*="item"]',
            'li[class*="news"]',
            'li[class*="article"]',
            'a[href*="/news/"]',
            'a[href*="/article/"]',
        ]

        for selector in selectors:
            news_items = response.css(selector)
            if news_items and len(news_items) > 0:
                self.logger.debug(f"뉴스 목록 발견: {selector} ({len(news_items)}개)")
                break

        if not news_items or len(news_items) == 0:
            self.logger.warning(f"뉴스 목록을 찾을 수 없습니다: {response.url}")
            # 전체 페이지에서 링크 추출 시도
            links = response.css(
                'a[href*="/news/"], a[href*="/article/"]::attr(href)'
            ).getall()
            if links:
                self.logger.info(f"링크 기반으로 {len(links)}개 기사 발견")
                for link in links[:20]:  # 최대 20개
                    if link.startswith("/"):
                        link = response.urljoin(link)
                    yield scrapy.Request(
                        link, callback=self.parse_article, meta={"selenium": True}
                    )
            return

        for item in news_items[:30]:  # 최대 30개만 처리
            # 제목 추출 (여러 방법 시도)
            title = (
                item.css("a::text").get()
                or item.css(".title::text, h2::text, h3::text, h4::text").get()
                or item.css("a .title::text").get()
                or item.css('[class*="title"]::text').get()
            )

            # URL 추출
            url = (
                item.css("a::attr(href)").get() or item.css("[href]::attr(href)").get()
            )

            if not title:
                # 제목이 없으면 스킵
                continue

            title = title.strip()

            if not url:
                # URL이 없으면 현재 페이지에서 직접 파싱
                yield scrapy.Request(
                    response.url,
                    callback=self.parse_article,
                    meta={"title": title},
                    dont_filter=True,
                )
                continue

            # 상대 URL을 절대 URL로 변환
            if url.startswith("/"):
                url = response.urljoin(url)
            elif not url.startswith("http"):
                url = response.urljoin(url)

            # 발행 시간 추출
            published_at = (
                item.css(".date::text, .time::text, time::attr(datetime)").get()
                or item.css('[class*="date"]::text').get()
                or item.css('[class*="time"]::text').get()
            )
            if not published_at:
                published_at = datetime.now().isoformat()
            else:
                published_at = published_at.strip()

            # 키워드 추출
            keywords = item.css(
                '.tag::text, .keyword::text, [class*="tag"]::text'
            ).getall()
            keywords = [k.strip() for k in keywords if k.strip()]

            yield scrapy.Request(
                url,
                callback=self.parse_article,
                meta={
                    "selenium": True,  # 상세 페이지도 Selenium 사용
                    "title": title,
                    "published_at": published_at,
                    "keywords": keywords,
                },
            )

        # 다음 페이지 링크
        next_selectors = [
            "a.next::attr(href)",
            ".pagination a:last-child::attr(href)",
            'a[class*="next"]::attr(href)',
            'a:contains("다음")::attr(href)',
        ]

        for selector in next_selectors:
            next_page = response.css(selector).get()
            if next_page:
                if next_page.startswith("/"):
                    next_page = response.urljoin(next_page)
                yield response.follow(next_page, self.parse)
                break

    def parse_article(self, response):
        """기사 상세 페이지 파싱 (ItemLoader 사용)"""
        try:
            loader = CryptoNewsItemLoader(item=CryptoNewsItem(), response=response)

            # 기본 정보
            loader.add_value("source", "coinness")
            loader.add_value("url", response.url)
            loader.add_value("timestamp", datetime.now().isoformat())

            # 제목 (메타에서 가져오거나 페이지에서 추출)
            title = response.meta.get("title", "")
            if title:
                loader.add_value("title", title)
            else:
                loader.add_css("title", "h1::text, .article-title::text, title::text")

            # 발행 시간
            published_at = response.meta.get("published_at")
            if published_at:
                loader.add_value("published_at", published_at)
            else:
                loader.add_css(
                    "published_at",
                    'time::attr(datetime), .date::text, [class*="date"]::text',
                )

            # 키워드
            keywords = response.meta.get("keywords", [])
            if keywords:
                loader.add_value("keywords", keywords)
            else:
                loader.add_css(
                    "keywords", '.tag::text, .keyword::text, [class*="tag"]::text'
                )

            # 본문 추출
            loader.add_css(
                "content", ".article-content, .content, .post-content, article p::text"
            )

            item = loader.load_item()

            self.logger.debug(f"Scraped article: {item.get('title', '')[:50]}")
            yield item

        except Exception as e:
            self.logger.error(f"Error parsing article {response.url}: {e}")
