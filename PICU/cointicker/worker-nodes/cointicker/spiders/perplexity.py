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
from cointicker.ct_itemloaders import CryptoNewsItemLoader


class PerplexitySpider(scrapy.Spider):
    name = "perplexity"
    allowed_domains = ["perplexity.ai", "www.perplexity.ai"]

    start_urls = [
        "https://www.perplexity.ai/finance/crypto",
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
        """메인 파싱 메서드 - Perplexity Finance Crypto 페이지"""
        self.logger.info(f"Parsing: {response.url}")

        # /finance/crypto 페이지만 처리
        if "/finance/crypto" in response.url:
            yield from self.parse_crypto_finance(response)
        else:
            self.logger.warning(f"예상하지 못한 URL: {response.url}")

    def parse_crypto_finance(self, response):
        """암호화폐 금융 페이지 파싱"""
        self.logger.info("암호화폐 금융 페이지 파싱 시작")

        # 제목 추출
        title = ""
        title_selectors = [
            "h1::text",
            "h2::text",
            'h2[class*="title"]::text',
            'div[class*="title"]::text',
            "title::text",
        ]

        for selector in title_selectors:
            title_elem = response.css(selector).get()
            if title_elem:
                title = title_elem.strip()
                if title and len(title) > 5:
                    break

        if not title:
            title = "Perplexity Finance - 암호화폐 시장 분석"

        # 다양한 방법으로 콘텐츠 추출 (최대한 많은 데이터 수집)
        all_content_parts = []

        # 방법 1: item 기반 구조 추출 (제한 없이 모든 항목 처리)
        items = response.css('div[class*="item"]')
        self.logger.info(f"발견된 item 요소: {len(items)}개")

        extracted_items = []
        for item in items:  # 제한 없이 모든 항목 처리
            # 항목 텍스트 추출
            item_texts = item.css("::text").getall()
            item_text = " ".join([t.strip() for t in item_texts if t.strip()])

            # 의미있는 데이터만 추출 (최소 5자)
            if len(item_text) > 5:
                # 불필요한 텍스트 필터링 (최소한만)
                skip_patterns = ["NXXX", "·XX"]
                if not any(skip in item_text for skip in skip_patterns):
                    extracted_items.append(item_text)

        if extracted_items:
            all_content_parts.extend(extracted_items)
            self.logger.info(f"item에서 추출된 데이터: {len(extracted_items)}개")

        # 방법 2: 특정 클래스 기반 추출
        content_selectors = [
            'div[class*="content"]',
            'div[class*="text"]',
            'div[class*="data"]',
            'div[class*="price"]',
            'div[class*="volume"]',
            'div[class*="change"]',
            'div[class*="index"]',
            'div[class*="card"]',
            'div[class*="table"]',
            'div[class*="row"]',
        ]

        for selector in content_selectors:
            elements = response.css(selector)
            if elements:
                for elem in elements[:20]:  # 각 선택자당 최대 20개
                    texts = elem.css("::text").getall()
                    text = " ".join([t.strip() for t in texts if t.strip()])
                    if text and len(text) > 10:
                        all_content_parts.append(text)

        # 방법 3: main 영역에서 추출
        main_texts = response.css("main ::text").getall()
        main_content = " ".join([t.strip() for t in main_texts if t.strip()])
        if main_content and len(main_content) > 100:
            all_content_parts.append(main_content)
            self.logger.info(f"main 영역에서 추출: {len(main_content)}자")

        # 방법 4: BeautifulSoup으로 전체 페이지 추출
        body_html = response.css("body").get()
        if body_html:
            soup = BeautifulSoup(body_html, "html.parser")
            # 스크립트와 스타일 제거
            for script in soup(["script", "style", "noscript"]):
                script.decompose()

            body_text = soup.get_text(separator="\n", strip=True)
            if body_text and len(body_text) > 200:
                all_content_parts.append(body_text)
                self.logger.info(f"BeautifulSoup으로 추출: {len(body_text)}자")

        # 모든 콘텐츠 통합
        if all_content_parts:
            # 중복 제거 및 정제
            unique_parts = []
            seen = set()
            for part in all_content_parts:
                # 짧은 부분은 제외
                if len(part) < 10:
                    continue
                # 중복 체크 (처음 50자 기준)
                part_key = part[:50].lower()
                if part_key not in seen:
                    seen.add(part_key)
                    unique_parts.append(part)

            content_text = "\n\n".join(unique_parts)
            self.logger.info(f"통합된 콘텐츠 부분: {len(unique_parts)}개")
        else:
            content_text = ""

        # 불필요한 텍스트 제거
        content_text = self._clean_content(content_text)

        self.logger.info(f"정제 후 최종 콘텐츠 길이: {len(content_text)}자")

        # 최소 길이 체크 (50자로 낮춤)
        if not content_text or len(content_text) < 50:
            self.logger.warning(
                f"콘텐츠가 너무 짧습니다: {response.url} ({len(content_text) if content_text else 0}자)"
            )
            return

        # 아이템 생성 (ItemLoader 사용)
        loader = CryptoNewsItemLoader(item=CryptoNewsItem(), response=response)
        loader.add_value("source", "perplexity_finance")
        loader.add_value("title", title)
        loader.add_value("url", response.url)
        loader.add_value("content", content_text[:15000].strip())  # 최대 15000자로 확장
        loader.add_value("published_at", datetime.now().isoformat())
        loader.add_value(
            "keywords", self._extract_keywords_from_finance(response, content_text)
        )
        loader.add_value("timestamp", datetime.now().isoformat())

        item = loader.load_item()

        self.logger.info(
            f"아이템 생성 완료: {item.get('title', '')[:50]}... ({len(item.get('content', '') or '')}자)"
        )
        yield item

        # 관련 링크 추출 (crypto 관련만)
        crypto_links = response.css('a[href*="/finance/crypto"]::attr(href)').getall()
        for link in crypto_links[:3]:  # 최대 3개
            if link.startswith("/"):
                link = response.urljoin(link)
            elif not link.startswith("http"):
                continue

            if any(domain in link for domain in self.allowed_domains):
                yield scrapy.Request(
                    link,
                    callback=self.parse,
                    meta={"selenium": True},
                    dont_filter=False,
                )

    def _clean_content(self, content_text):
        """콘텐츠 정제 (불필요한 텍스트 제거)"""
        if not content_text:
            return ""

        import re

        # 메뉴/네비게이션 텍스트 제거
        skip_keywords = [
            "Enable JavaScript",
            "Cloudflare",
            "Ray ID",
            "잠시만 기다리십시오",
            "사람인지 확인",
            "응답을 기다리는 중",
        ]

        # 불필요한 패턴 제거 (예: "XXX US$110.00 NVDA XX 110.00%", "110.00 NVDA XX 110.00%")
        # 더 포괄적인 패턴으로 여러 번 제거
        patterns_to_remove = [
            r"XXX\s+US\$[\d,\.]+\s+[A-Z]+\s+XX\s+[\d\.]+\%",  # XXX US$110.00 NVDA XX 110.00%
            r"US\$[\d,\.]+\s+[A-Z]+\s+XX\s+[\d\.]+\%",  # US$110.00 NVDA XX 110.00%
            r"[\d,\.]+\s+NVDA\s+XX\s+[\d\.]+\%",  # 110.00 NVDA XX 110.00%
            r"[\d,\.]+\s+[A-Z]{2,5}\s+XX\s+[\d\.]+\%",  # 숫자 + 대문자코드 + XX + 퍼센트
            r"XX\s+[\d\.]+\%",  # XX 110.00%
            r"XXX\s+US\$",  # XXX US$로 시작하는 패턴
        ]

        for pattern in patterns_to_remove:
            content_text = re.sub(pattern, "", content_text, flags=re.IGNORECASE)

        # 추가: "NVDA XX" 패턴이 포함된 줄 전체 제거
        lines_after_pattern = []
        for line in content_text.split("\n"):
            if not re.search(r"NVDA\s+XX\s+[\d\.]+\%", line, re.IGNORECASE):
                lines_after_pattern.append(line)
        content_text = "\n".join(lines_after_pattern)

        lines = content_text.split("\n")
        filtered_lines = []

        for line in lines:
            line = line.strip()
            if line and len(line) > 5:  # 최소 길이
                # 스킵 키워드가 포함된 짧은 줄만 제거
                should_skip = False
                for keyword in skip_keywords:
                    if keyword in line and len(line) < 100:
                        should_skip = True
                        break

                # 반복되는 짧은 텍스트 제거 (예: "추천 공간 재무" 반복)
                if not should_skip:
                    # 같은 단어가 2번 이상 반복되면 제거 (짧은 텍스트인 경우)
                    words = line.split()
                    if len(words) > 0 and len(words) < 15:
                        word_counts = {}
                        for word in words:
                            word_counts[word] = word_counts.get(word, 0) + 1
                        max_repeat = max(word_counts.values()) if word_counts else 0
                        if max_repeat >= 2:
                            should_skip = True

                    # 특정 반복 패턴 제거
                    repeat_patterns = [
                        "추천 공간 재무",
                        "Perplexity 금융",
                        "암호화폐 암호화폐",
                        "수익 수익",
                        "스크리너 스크리너",
                        "정치인 정치인",
                        "관심 목록 관심 목록",
                    ]
                    for pattern in repeat_patterns:
                        if pattern in line and len(line) < 100:
                            should_skip = True
                            break

                if not should_skip:
                    filtered_lines.append(line)

        content_text = " ".join(filtered_lines)
        # 단어 필터링 (너무 짧은 단어 제거)
        words = content_text.split()
        content_text = " ".join([w for w in words if len(w) > 1])

        # 최대 길이 제한 (15000자)
        if len(content_text) > 15000:
            content_text = content_text[:15000]

        return content_text

    def _extract_keywords(self, response):
        """키워드 추출 (기존 메서드 - 호환성 유지)"""
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

    def _extract_keywords_from_finance(self, response, content_text):
        """Finance 페이지에서 키워드 추출"""
        keywords = []

        # URL 기반 키워드
        if "/finance/crypto" in response.url:
            keywords.extend(["Cryptocurrency", "Crypto", "암호화폐", "Coinbase"])

        # 콘텐츠에서 키워드 추출
        finance_keywords = [
            "Bitcoin",
            "BTC",
            "비트코인",
            "Ethereum",
            "ETH",
            "이더리움",
            "Coinbase",
            "코인베이스",
            "Market",
            "시장",
            "Price",
            "가격",
            "Volume",
            "거래량",
            "Index",
            "지수",
        ]

        content_lower = content_text.lower()
        for keyword in finance_keywords:
            if keyword.lower() in content_lower:
                keywords.append(keyword)

        # 메타 태그에서 키워드 추출
        meta_keywords = response.css('meta[name="keywords"]::attr(content)').get()
        if meta_keywords:
            keywords.extend([k.strip() for k in meta_keywords.split(",")[:3]])

        return list(set(keywords))[:15]  # 중복 제거 후 최대 15개
