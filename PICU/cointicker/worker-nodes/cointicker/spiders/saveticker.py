"""
SaveTicker Spider
SaveTicker/Yahoo Finance 암호화폐 가격 및 기술적 지표 수집
"""

import scrapy
import json
from datetime import datetime
from cointicker.items import MarketTrendItem


class SaveTickerSpider(scrapy.Spider):
    name = "saveticker"
    allowed_domains = ["saveticker.com", "finance.yahoo.com"]

    start_urls = [
        "https://saveticker.com/app/news",
        "https://finance.yahoo.com/crypto",
    ]

    custom_settings = {
        "DOWNLOAD_DELAY": 2,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
    }

    def parse(self, response):
        """메인 파싱 메서드"""
        self.logger.info(f"Parsing: {response.url}")

        if "saveticker.com" in response.url:
            yield from self.parse_saveticker(response)
        elif "yahoo.com" in response.url:
            yield from self.parse_yahoo_finance(response)

    def parse_saveticker(self, response):
        """SaveTicker 사이트 파싱"""
        # 코인 목록 추출
        coin_rows = response.css("tr, .coin-row, .crypto-item")

        for row in coin_rows:
            symbol = row.css("td:first-child::text, .symbol::text").get()
            price = row.css("td:nth-child(2)::text, .price::text").get()
            volume = row.css("td:nth-child(3)::text, .volume::text").get()
            change = row.css("td:nth-child(4)::text, .change::text").get()

            if not symbol or not price:
                continue

            item = MarketTrendItem()
            item["source"] = "saveticker"
            item["symbol"] = symbol.strip()
            item["price"] = self._parse_number(price)
            item["volume_24h"] = self._parse_number(volume) if volume else 0
            item["change_24h"] = self._parse_percentage(change) if change else 0.0
            item["timestamp"] = datetime.now().isoformat()

            yield item

    def parse_yahoo_finance(self, response):
        """Yahoo Finance 파싱"""
        # Yahoo Finance는 주로 JavaScript로 렌더링되므로
        # API 엔드포인트를 사용하는 것이 더 효율적
        symbols = ["BTC-KRW", "ETH-KRW", "XRP-KRW", "ADA-KRW", "DOGE-KRW"]

        for symbol in symbols:
            api_url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            yield scrapy.Request(
                api_url, callback=self.parse_yahoo_api, meta={"symbol": symbol}
            )

    def parse_yahoo_api(self, response):
        """Yahoo Finance API 응답 파싱"""
        try:
            data = json.loads(response.text)
            symbol = response.meta.get("symbol", "").replace("-KRW", "")

            if "chart" in data and "result" in data["chart"]:
                result = data["chart"]["result"][0]
                meta = result.get("meta", {})

                item = MarketTrendItem()
                item["source"] = "saveticker"
                item["symbol"] = symbol
                item["price"] = meta.get("regularMarketPrice", 0)
                item["volume_24h"] = meta.get("regularMarketVolume", 0)

                # 변동률 계산
                previous_close = meta.get("previousClose", 0)
                current_price = meta.get("regularMarketPrice", 0)
                if previous_close > 0:
                    change_24h = (
                        (current_price - previous_close) / previous_close
                    ) * 100
                    item["change_24h"] = round(change_24h, 2)
                else:
                    item["change_24h"] = 0.0

                item["timestamp"] = datetime.now().isoformat()

                yield item

        except Exception as e:
            self.logger.error(f"Error parsing Yahoo Finance API: {e}")

    def _parse_number(self, text):
        """텍스트에서 숫자 추출"""
        if not text:
            return 0

        # 쉼표, 통화 기호 제거
        cleaned = text.replace(",", "").replace("₩", "").replace("$", "").strip()

        try:
            return float(cleaned)
        except ValueError:
            return 0

    def _parse_percentage(self, text):
        """퍼센트 값 파싱"""
        if not text:
            return 0.0

        cleaned = text.replace("%", "").replace("+", "").strip()

        try:
            return float(cleaned)
        except ValueError:
            return 0.0
