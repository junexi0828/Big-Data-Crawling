"""
Upbit Trends Spider
Upbit 거래소의 트렌드 데이터 수집
"""

import scrapy
import json
from datetime import datetime
from cointicker.items import UpbitTrendItem, MarketTrendItem
from itemadapter import ItemAdapter


class UpbitTrendsSpider(scrapy.Spider):
    name = "upbit_trends"
    allowed_domains = ["upbit.com"]

    # 시작 URL (실제 Upbit API 또는 웹페이지)
    start_urls = [
        "https://api.upbit.com/v1/market/all",  # 전체 마켓 목록
        "https://api.upbit.com/v1/ticker",  # 현재가 정보
    ]

    custom_settings = {
        "DOWNLOAD_DELAY": 2,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
    }

    def parse(self, response):
        """메인 파싱 메서드"""
        self.logger.info(f"Parsing: {response.url}")

        try:
            # JSON 응답 파싱
            data = json.loads(response.text)

            if "market/all" in response.url:
                # 마켓 목록 응답
                yield from self.parse_market_list(response, data)
            elif "ticker" in response.url:
                # 현재가 정보 응답
                yield from self.parse_ticker(response, data)

        except json.JSONDecodeError:
            self.logger.error(f"Failed to parse JSON from {response.url}")
        except Exception as e:
            self.logger.error(f"Error parsing {response.url}: {e}")

    def parse_market_list(self, response, data):
        """마켓 목록 파싱"""
        # KRW 마켓만 필터링
        krw_markets = [m for m in data if m.get("market", "").startswith("KRW-")]

        # 상위 10개 마켓에 대해 상세 정보 요청
        for market in krw_markets[:10]:
            market_code = market.get("market")
            if market_code:
                ticker_url = f"https://api.upbit.com/v1/ticker?markets={market_code}"
                yield scrapy.Request(
                    ticker_url,
                    callback=self.parse_ticker_detail,
                    meta={"market": market_code},
                )

    def parse_ticker(self, response, data):
        """현재가 정보 파싱 (배치)"""
        if isinstance(data, list):
            for ticker_data in data:
                yield from self._create_trend_item(ticker_data)
        elif isinstance(data, dict):
            yield from self._create_trend_item(data)

    def parse_ticker_detail(self, response):
        """개별 마켓 상세 정보 파싱"""
        try:
            data = json.loads(response.text)
            if isinstance(data, list) and len(data) > 0:
                yield from self._create_trend_item(data[0])
        except Exception as e:
            self.logger.error(f"Error parsing ticker detail: {e}")

    def _create_trend_item(self, ticker_data):
        """트렌드 아이템 생성"""
        try:
            market = ticker_data.get("market", "")
            symbol = market.replace("KRW-", "") if market.startswith("KRW-") else market

            item = MarketTrendItem()
            item["source"] = "upbit"
            item["symbol"] = symbol
            item["price"] = ticker_data.get("trade_price", 0)
            item["volume_24h"] = ticker_data.get("acc_trade_volume_24h", 0)

            # 24시간 변동률 계산
            prev_closing_price = ticker_data.get("prev_closing_price", 0)
            trade_price = ticker_data.get("trade_price", 0)
            if prev_closing_price > 0:
                change_24h = (
                    (trade_price - prev_closing_price) / prev_closing_price
                ) * 100
                item["change_24h"] = round(change_24h, 2)
            else:
                item["change_24h"] = 0.0

            item["market_cap"] = ticker_data.get(
                "acc_trade_price_24h", 0
            )  # 24시간 거래대금
            item["timestamp"] = datetime.now().isoformat()

            self.logger.debug(f"Created trend item: {symbol}")
            yield item

        except Exception as e:
            self.logger.error(f"Error creating trend item: {e}")

    def closed(self, reason):
        """Spider 종료 시"""
        self.logger.info(f"Spider closed: {reason}")
