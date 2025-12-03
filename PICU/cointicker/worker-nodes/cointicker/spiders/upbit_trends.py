"""
Upbit Trends Spider
Upbit 거래소의 트렌드 데이터 수집
"""

import scrapy
import json
from datetime import datetime
from cointicker.items import UpbitTrendItem, MarketTrendItem
from cointicker.ct_itemloaders import MarketTrendItemLoader
from itemadapter import ItemAdapter


class UpbitTrendsSpider(scrapy.Spider):
    name = "upbit_trends"
    allowed_domains = ["upbit.com"]

    # 시작 URL (실제 Upbit API)
    start_urls = [
        "https://api.upbit.com/v1/market/all",  # 전체 마켓 목록
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
                yield from self.parse_ticker(response)

        except json.JSONDecodeError:
            self.logger.error(f"Failed to parse JSON from {response.url}")
        except Exception as e:
            self.logger.error(f"Error parsing {response.url}: {e}")

    def parse_market_list(self, response, data):
        """마켓 목록 파싱"""
        # KRW 마켓만 필터링
        krw_markets = [
            m
            for m in data
            if isinstance(m, dict) and m.get("market", "").startswith("KRW-")
        ]

        if not krw_markets:
            self.logger.warning("KRW 마켓을 찾을 수 없습니다")
            return

        # 주요 코인만 선택 (BTC, ETH, XRP, ADA, DOGE 등)
        major_coins = [
            "BTC",
            "ETH",
            "XRP",
            "ADA",
            "DOGE",
            "SOL",
            "DOT",
            "MATIC",
            "AVAX",
            "LINK",
        ]
        selected_markets = []

        for market in krw_markets:
            market_code = market.get("market", "")
            symbol = market_code.replace("KRW-", "")
            if symbol in major_coins:
                selected_markets.append(market_code)

        # 주요 코인이 없으면 상위 20개 마켓 사용
        if not selected_markets:
            selected_markets = [
                m.get("market") for m in krw_markets[:20] if m.get("market")
            ]

        # 배치로 요청 (Upbit API는 최대 100개까지 한 번에 요청 가능)
        if selected_markets:
            # 100개씩 나누어 요청
            batch_size = 100
            for i in range(0, len(selected_markets), batch_size):
                batch = selected_markets[i : i + batch_size]
                markets_param = ",".join([str(m) for m in batch if m])
                ticker_url = f"https://api.upbit.com/v1/ticker?markets={markets_param}"
                yield scrapy.Request(
                    ticker_url,
                    callback=self.parse_ticker,
                    meta={"markets": batch},
                )

    def parse_ticker(self, response):
        """현재가 정보 파싱 (배치)"""
        try:
            data = json.loads(response.text)

            if isinstance(data, list):
                for ticker_data in data:
                    if isinstance(ticker_data, dict):
                        yield from self._create_trend_item(ticker_data)
            elif isinstance(data, dict):
                yield from self._create_trend_item(data)
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON 파싱 오류 {response.url}: {e}")
        except Exception as e:
            self.logger.error(f"Ticker 파싱 오류 {response.url}: {e}")

    def parse_ticker_detail(self, response):
        """개별 마켓 상세 정보 파싱"""
        try:
            data = json.loads(response.text)
            if isinstance(data, list) and len(data) > 0:
                yield from self._create_trend_item(data[0])
        except Exception as e:
            self.logger.error(f"Error parsing ticker detail: {e}")

    def _create_trend_item(self, ticker_data):
        """트렌드 아이템 생성 (ItemLoader 사용)"""
        try:
            market = ticker_data.get("market", "")
            symbol = market.replace("KRW-", "") if market.startswith("KRW-") else market

            # 24시간 변동률 계산
            prev_closing_price = ticker_data.get("prev_closing_price", 0)
            trade_price = ticker_data.get("trade_price", 0)
            if prev_closing_price > 0:
                change_24h = (
                    (trade_price - prev_closing_price) / prev_closing_price
                ) * 100
                change_24h = round(change_24h, 2)
            else:
                change_24h = 0.0

            # ItemLoader 사용
            loader = MarketTrendItemLoader(item=MarketTrendItem())
            loader.add_value("source", "upbit")
            loader.add_value("symbol", symbol)
            loader.add_value("price", ticker_data.get("trade_price", 0))
            loader.add_value("volume_24h", ticker_data.get("acc_trade_volume_24h", 0))
            loader.add_value("change_24h", change_24h)
            loader.add_value(
                "market_cap", ticker_data.get("acc_trade_price_24h", 0)
            )  # 24시간 거래대금
            loader.add_value("timestamp", datetime.now().isoformat())

            item = loader.load_item()

            self.logger.debug(f"Created trend item: {symbol}")
            yield item

        except Exception as e:
            self.logger.error(f"Error creating trend item: {e}")

    def closed(self, reason):
        """Spider 종료 시"""
        self.logger.info(f"Spider closed: {reason}")
