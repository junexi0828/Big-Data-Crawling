"""
Perplexity Finance Spider
Perplexity AI 기반 금융 요약 및 시장 분석 수집

Selenium을 사용하여 JavaScript로 렌더링된 동적 콘텐츠를 처리합니다.
"""

import scrapy
import time
from datetime import datetime
from bs4 import BeautifulSoup
from cointicker.items import CryptoNewsItem


class PerplexitySpider(scrapy.Spider):
    name = "perplexity"
    allowed_domains = ["perplexity.ai", "www.perplexity.ai"]

    start_urls = [
        "https://www.perplexity.ai/search?q=cryptocurrency+market+analysis",
        "https://www.perplexity.ai/search?q=bitcoin+ethereum+market+trends",
        "https://www.perplexity.ai/search?q=altcoin+market+trends+2024",
    ]

    custom_settings = {
        "DOWNLOAD_DELAY": 5,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
        "USER_AGENT": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        # Selenium 미들웨어 활성화
        "SELENIUM_ENABLED_DOMAINS": ["perplexity.ai", "www.perplexity.ai"],
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

        # Selenium으로 렌더링된 HTML에서 데이터 추출
        # Perplexity의 주요 콘텐츠 영역 선택자 (우선순위 순)
        content_selectors = [
            'div[class*="content"]',
            'div[class*="answer"]',
            'div[class*="summary"]',
            'div[class*="text"]',
            "article",
            "main",
            ".prose",
        ]

        content_text = ""
        title_text = ""

        # 제목 추출 (URL 쿼리에서 추출)
        if "q=" in response.url:
            try:
                query = response.url.split("q=")[1].split("&")[0]
                title_text = query.replace("+", " ").replace("%20", " ").title()
            except:
                pass

        # 제목이 없으면 메타 태그나 페이지에서 추출
        if not title_text:
            title_selectors = [
                "h1::text",
                'h2[class*="title"]::text',
                "title::text",
                'meta[property="og:title"]::attr(content)',
            ]

            for selector in title_selectors:
                title = response.css(selector).get()
                if title:
                    title_text = title.strip()
                    if title_text:
                        break

        # 콘텐츠 추출 (여러 선택자 시도)
        for selector in content_selectors:
            elements = response.css(selector)
            if elements:
                # 텍스트 추출
                texts = elements.css("::text").getall()
                if texts:
                    content_text = " ".join([t.strip() for t in texts if t.strip()])
                    # 의미있는 콘텐츠인지 확인 (최소 200자)
                    if len(content_text) > 200:
                        self.logger.debug(
                            f"콘텐츠 발견: {selector} ({len(content_text)}자)"
                        )
                        break

        # 콘텐츠가 없으면 전체 페이지에서 텍스트 추출
        if not content_text or len(content_text) < 200:
            # 방법 1: body의 모든 텍스트
            all_texts = response.css("body ::text").getall()
            content_text = " ".join([t.strip() for t in all_texts if t.strip()])

            self.logger.debug(f"body 텍스트 추출: {len(content_text)}자")

            # 방법 2: BeautifulSoup 사용
            if len(content_text) < 200:
                body_html = response.css("body").get()
                if body_html:
                    soup = BeautifulSoup(body_html, "html.parser")
                    content_text = soup.get_text(separator=" ", strip=True)
                    self.logger.debug(
                        f"BeautifulSoup 텍스트 추출: {len(content_text)}자"
                    )

            # 불필요한 텍스트 제거 (너무 짧은 단어들, 메뉴 텍스트 등)
            if content_text:
                # 메뉴/네비게이션 텍스트 제거
                lines = content_text.split("\n")
                filtered_lines = []
                skip_keywords = [
                    "홈",
                    "추천",
                    "공간",
                    "재무",
                    "답변",
                    "링크",
                    "이미지",
                    "공유",
                ]

                for line in lines:
                    line = line.strip()
                    if line and len(line) > 10:  # 최소 길이
                        # 메뉴 키워드가 포함된 짧은 줄 제거
                        if (
                            not any(keyword in line for keyword in skip_keywords)
                            or len(line) > 50
                        ):
                            filtered_lines.append(line)

                content_text = " ".join(filtered_lines)
                words = content_text.split()
                content_text = " ".join([w for w in words if len(w) > 2])[:5000]

                self.logger.debug(f"필터링 후 텍스트: {len(content_text)}자")

        # 최소 길이 체크 (100자로 낮춤)
        if not content_text or len(content_text) < 100:
            self.logger.warning(
                f"콘텐츠가 너무 짧습니다: {response.url} ({len(content_text) if content_text else 0}자)"
            )
            return

        # 아이템 생성
        item = CryptoNewsItem()
        item["source"] = "perplexity"
        item["title"] = (
            title_text
            or f"Perplexity AI Analysis - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
        item["url"] = response.url

        # 콘텐츠 정제 (최대 10000자)
        content_text = content_text[:10000].strip()
        item["content"] = content_text

        item["published_at"] = datetime.now().isoformat()
        item["keywords"] = self._extract_keywords(response)
        item["timestamp"] = datetime.now().isoformat()

        self.logger.info(
            f"아이템 생성 완료: {item['title'][:50]}... ({len(content_text)}자)"
        )
        yield item

        # 관련 링크 추출 (선택적)
        related_links = response.css('a[href*="/search"]::attr(href)').getall()
        for link in related_links[:3]:  # 최대 3개만
            if link.startswith("/"):
                link = response.urljoin(link)
            elif link.startswith("http"):
                pass
            else:
                continue

            # 같은 도메인인지 확인
            if any(domain in link for domain in self.allowed_domains):
                yield scrapy.Request(
                    link,
                    callback=self.parse,
                    meta={"selenium": True},
                    dont_filter=False,
                )

    def _extract_keywords(self, response):
        """키워드 추출"""
        keywords = ["AI Analysis", "Market Trends", "Cryptocurrency"]

        # URL에서 키워드 추출
        if "q=" in response.url:
            try:
                query = response.url.split("q=")[1].split("&")[0]
                query_keywords = query.replace("+", " ").split()
                keywords.extend(query_keywords[:3])
            except:
                pass

        # 메타 태그에서 키워드 추출
        meta_keywords = response.css('meta[name="keywords"]::attr(content)').get()
        if meta_keywords:
            keywords.extend([k.strip() for k in meta_keywords.split(",")[:3]])

        return list(set(keywords))[:10]  # 중복 제거 후 최대 10개
