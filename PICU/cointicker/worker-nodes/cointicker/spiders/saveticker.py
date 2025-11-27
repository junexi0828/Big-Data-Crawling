"""
SaveTicker Spider
SaveTicker 커뮤니티 게시판에서 미국 주식 및 암호화폐 관련 뉴스 수집
"""

import scrapy
import re
from datetime import datetime
from bs4 import BeautifulSoup
from cointicker.items import CryptoNewsItem


class SaveTickerSpider(scrapy.Spider):
    name = "saveticker"
    allowed_domains = ["saveticker.com", "www.saveticker.com"]

    # 키워드 리스트 (미국 주식 및 암호화폐 관련) - 매우 넓은 범위
    KEYWORDS = [
        # 인물 및 기관
        "연은 총재",
        "연준",
        "연방준비제도",
        "연방준비은행",
        "파월",
        "제롬 파월",
        "Jerome Powell",
        "Powell",
        "Fed",
        "Federal Reserve",
        "FOMC",
        "트럼프",
        "Trump",
        "도널드 트럼프",
        "Donald Trump",
        "바이든",
        "Biden",
        "조 바이든",
        "Joe Biden",
        "백악관",
        "White House",
        "화이트하우스",
        "캐시우드",
        "Cathie Wood",
        "ARK",
        "ARK Invest",
        "블랙록",
        "BlackRock",
        "블랙스톤",
        "Blackstone",
        "제이미 다이먼",
        "Jamie Dimon",
        "JP모건",
        "JPMorgan",
        "워렌 버핏",
        "Warren Buffett",
        "버크셔 해서웨이",
        "Berkshire",
        # 암호화폐 - 주요 코인
        "코인",
        "암호화폐",
        "가상화폐",
        "디지털 자산",
        "비트코인",
        "Bitcoin",
        "BTC",
        "비티씨",
        "이더리움",
        "Ethereum",
        "ETH",
        "이더",
        "XRP",
        "리플",
        "Ripple",
        "XRP코인",
        "솔라나",
        "Solana",
        "SOL",
        "카르다노",
        "Cardano",
        "ADA",
        "도지코인",
        "Dogecoin",
        "DOGE",
        "폴카닷",
        "Polkadot",
        "DOT",
        "체인링크",
        "Chainlink",
        "LINK",
        "아발란체",
        "Avalanche",
        "AVAX",
        "매틱",
        "Polygon",
        "MATIC",
        "라이트코인",
        "Litecoin",
        "LTC",
        "비트코인캐시",
        "Bitcoin Cash",
        "BCH",
        "스텔라",
        "Stellar",
        "XLM",
        "이오스",
        "EOS",
        "테더",
        "Tether",
        "USDT",
        "USD 코인",
        "USD Coin",
        "USDC",
        "cryptocurrency",
        "crypto",
        "altcoin",
        "알트코인",
        "블록체인",
        "blockchain",
        "디파이",
        "DeFi",
        # 국가/지역
        "중국",
        "China",
        "중화인민공화국",
        "미국",
        "USA",
        "US",
        "United States",
        "미합중국",
        "한국",
        "Korea",
        "South Korea",
        "대한민국",
        "일본",
        "Japan",
        "유럽",
        "Europe",
        "EU",
        "유럽연합",
        "영국",
        "UK",
        "United Kingdom",
        # 주식/시장
        "주식",
        "stock",
        "증권",
        "equity",
        "시장",
        "market",
        "자본시장",
        "capital market",
        "나스닥",
        "NASDAQ",
        "나스닥 종합지수",
        "S&P",
        "S&P 500",
        "S&P500",
        "에스앤피",
        "다우",
        "Dow",
        "다우존스",
        "Dow Jones",
        "DJIA",
        "러셀",
        "Russell",
        "러셀 2000",
        "VIX",
        "공포지수",
        "변동성 지수",
        "선물",
        "futures",
        "옵션",
        "options",
        "파생상품",
        "derivatives",
        # 경제/정책/금융
        "금리",
        "interest rate",
        "기준금리",
        "policy rate",
        "인플레이션",
        "inflation",
        "디플레이션",
        "deflation",
        "경제",
        "economy",
        "경제성장",
        "economic growth",
        "정책",
        "policy",
        "통화정책",
        "monetary policy",
        "재정정책",
        "fiscal policy",
        "GDP",
        "국내총생산",
        "실업률",
        "unemployment",
        "소비자물가",
        "CPI",
        "생산자물가",
        "PPI",
        "청산",
        "liquidation",
        "청산액",
        "청산 규모",
        "규모",
        "scale",
        "시가총액",
        "market cap",
        "거래량",
        "volume",
        "거래대금",
        "유동성",
        "liquidity",
        # 기관 및 규제
        "SEC",
        "증권거래위원회",
        "Securities and Exchange Commission",
        "규제",
        "regulation",
        "감독",
        "supervision",
        "CFTC",
        "상품선물거래위원회",
        "FBI",
        "연방수사국",
        "국세청",
        "IRS",
        # 투자 상품
        "ETF",
        "상장지수펀드",
        "exchange traded fund",
        "상장",
        "listing",
        "IPO",
        "기업공개",
        "SPAC",
        "스팩",
        "펀드",
        "fund",
        "뮤추얼 펀드",
        "mutual fund",
        "헤지펀드",
        "hedge fund",
        # 기업 및 산업
        "테슬라",
        "Tesla",
        "TSLA",
        "애플",
        "Apple",
        "AAPL",
        "마이크로소프트",
        "Microsoft",
        "MSFT",
        "구글",
        "Google",
        "GOOGL",
        "알파벳",
        "Alphabet",
        "아마존",
        "Amazon",
        "AMZN",
        "메타",
        "Meta",
        "페이스북",
        "Facebook",
        "FB",
        "엔비디아",
        "NVIDIA",
        "NVDA",
        "은행",
        "bank",
        "투자은행",
        "investment bank",
        "기관투자자",
        "institutional investor",
        # 시장 동향
        "강세",
        "bull",
        "상승",
        "rally",
        "약세",
        "bear",
        "하락",
        "crash",
        "조정",
        "correction",
        "반등",
        "rebound",
        "변동성",
        "volatility",
        "공포",
        "fear",
        "탐욕",
        "greed",
        "매수",
        "buy",
        "매도",
        "sell",
        "공매도",
        "short selling",
        "숏",
    ]

    start_urls = [
        "https://www.saveticker.com/app/news",
    ]

    custom_settings = {
        "DOWNLOAD_DELAY": 3,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
        "USER_AGENT": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        # Selenium 미들웨어 활성화 (JavaScript 렌더링 필요)
        "SELENIUM_ENABLED_DOMAINS": ["saveticker.com", "www.saveticker.com"],
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

        if "saveticker.com" in response.url:
            yield from self.parse_saveticker_news(response)
        else:
            self.logger.warning(f"예상하지 못한 URL: {response.url}")

    def parse_saveticker_news(self, response):
        """SaveTicker 게시판 뉴스 파싱"""
        self.logger.info("SaveTicker 게시판 파싱 시작")

        # SaveTicker는 React 기반으로 텍스트 기반 파싱 필요
        # Selenium으로 렌더링된 HTML에서 전체 텍스트 추출
        # 여러 방법 시도
        all_text = ""

        # 방법 1: body의 모든 텍스트 노드
        body_texts = response.css("body ::text").getall()
        if body_texts:
            all_text = " ".join([t.strip() for t in body_texts if t.strip()])

        # 방법 2: body 요소의 직접 텍스트
        if not all_text or len(all_text) < 100:
            body_elem = response.css("body").get()
            if body_elem:
                soup = BeautifulSoup(body_elem, "html.parser")
                all_text = soup.get_text(separator=" ", strip=True)

        self.logger.debug(f"추출된 텍스트 길이: {len(all_text)}자")

        if not all_text or len(all_text) < 50:
            self.logger.warning("페이지에서 충분한 텍스트를 추출하지 못했습니다")
            return

        # 시간 패턴으로 뉴스 항목 구분 (예: "6시간 전", "8시간 전", "1일 전")
        # 패턴 개선: "·" 문자와 다양한 시간 표현 고려
        time_pattern = r"(\d+시간\s*전|\d+일\s*전|\d+분\s*전|\d+주\s*전|\d+개월\s*전)"

        # 텍스트를 시간 패턴 기준으로 분할
        parts = re.split(time_pattern, all_text)

        self.logger.info(
            f"시간 패턴으로 분할된 부분: {len(parts)}개 (예상 항목: {len(parts)//2}개)"
        )

        items = []
        # 시간 패턴과 콘텐츠 쌍으로 처리
        for i in range(1, len(parts), 2):  # 시간 패턴 다음 텍스트
            if i + 1 < len(parts):
                time_str = parts[i]
                content = parts[i + 1].strip()

                # 콘텐츠가 너무 짧으면 스킵
                if len(content) < 20:
                    continue

                # 제목 추출 (더 유연하게)
                lines = content.split("\n")
                title = ""

                # 방법 1: 첫 번째 의미있는 줄 찾기
                for line in lines[:10]:  # 처음 10줄까지 확인
                    line = line.strip()
                    if line and len(line) > 5:
                        # #태그 제거
                        clean_line = re.sub(r"#\w+\s*", "", line)
                        # 불필요한 텍스트 제거
                        clean_line = re.sub(r"조회.*", "", clean_line).strip()
                        clean_line = re.sub(r"관련 기업.*", "", clean_line).strip()
                        clean_line = re.sub(
                            r"\$[A-Z]+\s*\d+.*", "", clean_line
                        ).strip()  # 주식 심볼 제거

                        # 너무 짧거나 의미없는 텍스트 제외
                        if (
                            len(clean_line) > 10
                            and not clean_line.startswith("관련")
                            and not clean_line.startswith("더 인포메이션")
                            and not re.match(r"^[\d\s\$\.,]+$", clean_line)
                        ):  # 숫자만 있는 경우 제외
                            title = clean_line
                            break

                # 방법 2: 첫 200자에서 제목 추출
                if not title or len(title) < 10:
                    title = content[:200].split("\n")[0].strip()
                    title = re.sub(r"#\w+\s*", "", title).strip()
                    title = re.sub(r"조회.*", "", title).strip()
                    title = re.sub(r"관련 기업.*", "", title).strip()

                # 제목 정제
                if title:
                    title = title.strip()
                    # 최소 길이 체크 (5자 이상)
                    if len(title) >= 5:
                        # 키워드 필터링 (제목 또는 본문에 키워드가 있으면 포함)
                        title_content = (
                            f"{title} {content[:1000]}"  # 제목 + 본문 일부 확장
                        )

                        # 키워드가 있으면 우선, 없어도 최소 조건 만족 시 수집
                        if self._contains_keyword(title_content) or len(content) > 50:
                            items.append(
                                {
                                    "title": title[:200],  # 최대 200자
                                    "content": content[:3000],  # 최대 3000자로 확장
                                    "time": time_str,
                                    "url": response.url,
                                }
                            )

        self.logger.info(
            f"SaveTicker에서 {len(items)}개 뉴스 항목 발견 (키워드 필터링 전: {len(parts)//2}개 시간 패턴)"
        )

        # 각 항목 처리
        for item_data in items[:100]:  # 최대 100개로 확장 (더 많은 데이터 수집)
            item = self._create_news_item(
                item_data["title"], item_data["url"], item_data["content"]
            )
            if item:
                self.logger.info(f"뉴스 수집: {item_data['title'][:50]}...")
                yield item

        # 다음 페이지 링크
        next_page = (
            response.css("a.next::attr(href)").get()
            or response.css(".pagination a:last-child::attr(href)").get()
            or response.css('a[class*="next"]::attr(href)').get()
        )
        if next_page:
            if next_page.startswith("/"):
                next_page = response.urljoin(next_page)
            yield response.follow(next_page, self.parse_saveticker_news)

    def parse_article_detail(self, response):
        """기사 상세 페이지 파싱"""
        try:
            # 제목 추출
            title = response.meta.get("title") or (
                response.css("h1::text, .title::text, article h1::text").get()
                or response.css("title::text").get()
            )

            if not title:
                self.logger.warning(f"제목을 찾을 수 없습니다: {response.url}")
                return

            title = title.strip()

            # 키워드 기반 필터링
            if not self._contains_keyword(title):
                return

            # 본문 추출
            content = self._extract_content_from_page(response)

            # 아이템 생성
            item = self._create_news_item(title, response.url, content)
            if item:
                self.logger.info(f"뉴스 수집: {title[:50]}...")
                yield item

        except Exception as e:
            self.logger.error(f"기사 상세 파싱 오류 {response.url}: {e}")

    def _contains_keyword(self, text):
        """텍스트에 키워드가 포함되어 있는지 확인 (유연한 매칭)"""
        if not text:
            return False

        text_lower = text.lower()

        # 키워드 매칭 (대소문자 무시)
        for keyword in self.KEYWORDS:
            keyword_lower = keyword.lower()
            # 정확한 단어 매칭 또는 부분 문자열 매칭
            if keyword_lower in text_lower:
                return True
            # 공백 제거 후 매칭 (예: "XRP"와 "XRP코인")
            if keyword_lower.replace(" ", "") in text_lower.replace(" ", ""):
                return True

        return False

    def _extract_content(self, element):
        """요소에서 본문 추출"""
        content_selectors = [
            ".content",
            ".post-content",
            ".article-content",
            "p::text",
            ".text::text",
            '[class*="content"]::text',
        ]

        for selector in content_selectors:
            texts = element.css(selector).getall()
            if texts:
                content = " ".join([t.strip() for t in texts if t.strip()])
                if len(content) > 20:  # 최소 길이 체크
                    return content

        return None

    def _extract_content_from_page(self, response):
        """페이지에서 본문 추출"""
        content_selectors = [
            "article .content",
            "article p",
            ".post-content",
            ".article-content",
            "main p",
            '[class*="content"] p',
        ]

        for selector in content_selectors:
            elements = response.css(selector)
            if elements:
                texts = elements.css("::text").getall()
                content = " ".join([t.strip() for t in texts if t.strip()])
                if len(content) > 50:  # 최소 길이 체크
                    return content[:5000]  # 최대 5000자

        # 전체 페이지에서 텍스트 추출 (마지막 수단)
        all_texts = response.css("body p::text, body div::text").getall()
        content = " ".join([t.strip() for t in all_texts if t.strip()])
        return content[:5000] if content else ""

    def _extract_keywords_from_text(self, text):
        """텍스트에서 키워드 추출"""
        if not text:
            return []

        found_keywords = []
        text_lower = text.lower()

        for keyword in self.KEYWORDS:
            if keyword.lower() in text_lower:
                found_keywords.append(keyword)

        return list(set(found_keywords))  # 중복 제거

    def _create_news_item(self, title, url, content):
        """뉴스 아이템 생성"""
        try:
            # 키워드 추출
            keywords = self._extract_keywords_from_text(f"{title} {content}")

            # 키워드가 없어도 수집 (더 유연하게)
            # 키워드가 있으면 우선순위가 높지만, 없어도 수집 가능
            if not keywords:
                # 키워드가 없어도 최소한의 조건을 만족하면 수집
                if len(title) < 10 or len(content) < 20:
                    return None
                # 키워드가 없으면 빈 리스트로 설정
                keywords = []

            item = CryptoNewsItem()
            item["source"] = "saveticker"
            item["title"] = title
            item["url"] = url
            item["content"] = content or ""
            item["published_at"] = datetime.now().isoformat()
            item["keywords"] = keywords
            item["timestamp"] = datetime.now().isoformat()

            return item
        except Exception as e:
            self.logger.error(f"아이템 생성 오류: {e}")
            return None
