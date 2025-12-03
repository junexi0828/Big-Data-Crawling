"""
Yahoo Finance 데이터 수집 서비스
비공식 API를 사용하여 암호화폐 가격 데이터를 수집합니다.

주의: Yahoo Finance는 공식 API를 제공하지 않으므로,
이 서비스는 비공식 엔드포인트를 사용합니다.
안정성을 위해 에러 처리 및 재시도 로직이 포함되어 있습니다.
"""

import json
import logging
import time
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.models import MarketTrends

logger = logging.getLogger(__name__)


class YahooFinanceService:
    """Yahoo Finance 데이터 수집 서비스"""

    # 주요 암호화폐 심볼 (USD 기준)
    DEFAULT_SYMBOLS = [
        "BTC-USD",
        "ETH-USD",
        "XRP-USD",
        "ADA-USD",
        "DOGE-USD",
        "SOL-USD",
        "DOT-USD",
        "MATIC-USD",
        "AVAX-USD",
        "LINK-USD",
    ]

    def __init__(
        self,
        db_session: Session,
        base_url: str = "https://query1.finance.yahoo.com/v8/finance/chart",
    ):
        """
        초기화

        Args:
            db_session: 데이터베이스 세션
            base_url: Yahoo Finance API 기본 URL
        """
        self.db = db_session
        self.base_url = base_url
        self.usd_krw_rate = 1300.0  # 기본 환율
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
        )

    def fetch_usd_krw_rate(self, retries: int = 3) -> float:
        """
        USD-KRW 환율 조회

        Args:
            retries: 재시도 횟수

        Returns:
            USD-KRW 환율
        """
        url = f"{self.base_url}/USDKRW=X"

        for attempt in range(retries):
            try:
                response = self.session.get(url, timeout=10)

                if response.status_code == 429:
                    # Rate limiting - 대기 후 재시도
                    wait_time = (attempt + 1) * 5
                    logger.warning(f"Rate limited. Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue

                if response.status_code != 200:
                    logger.warning(
                        f"Failed to fetch USD-KRW rate: {response.status_code}"
                    )
                    continue

                data = response.json()

                if "chart" in data and "result" in data["chart"]:
                    result = data["chart"]["result"][0]
                    meta = result.get("meta", {})
                    rate = meta.get("regularMarketPrice", 1300.0)

                    if rate and rate > 0:
                        self.usd_krw_rate = rate
                        logger.info(f"USD-KRW 환율 조회 성공: {rate:.2f}")
                        return rate

            except requests.exceptions.RequestException as e:
                logger.error(
                    f"USD-KRW 환율 조회 오류 (시도 {attempt + 1}/{retries}): {e}"
                )
                if attempt < retries - 1:
                    time.sleep(2**attempt)  # Exponential backoff
            except json.JSONDecodeError as e:
                logger.error(f"JSON 파싱 오류: {e}")
                break
            except Exception as e:
                logger.error(f"예상치 못한 오류: {e}")
                break

        logger.warning(f"USD-KRW 환율 조회 실패. 기본값 사용: {self.usd_krw_rate}")
        return self.usd_krw_rate

    def fetch_crypto_price(
        self, symbol: str, retries: int = 3
    ) -> Optional[Dict[str, Any]]:
        """
        암호화폐 가격 조회

        Args:
            symbol: 심볼 (예: BTC-USD)
            retries: 재시도 횟수

        Returns:
            가격 데이터 또는 None
        """
        url = f"{self.base_url}/{symbol}"

        for attempt in range(retries):
            try:
                response = self.session.get(url, timeout=10)

                if response.status_code == 429:
                    # Rate limiting
                    wait_time = (attempt + 1) * 5
                    logger.warning(
                        f"Rate limited for {symbol}. Waiting {wait_time} seconds..."
                    )
                    time.sleep(wait_time)
                    continue

                if response.status_code != 200:
                    logger.warning(f"Failed to fetch {symbol}: {response.status_code}")
                    continue

                data = response.json()

                if "chart" in data and "result" in data["chart"]:
                    result = data["chart"]["result"][0]
                    meta = result.get("meta", {})

                    price_usd = meta.get("regularMarketPrice", 0)
                    price_krw = price_usd * self.usd_krw_rate if price_usd > 0 else 0

                    previous_close = meta.get("previousClose", 0)
                    current_price = meta.get("regularMarketPrice", 0)

                    change_24h = 0.0
                    if previous_close > 0 and current_price > 0:
                        change_24h = (
                            (current_price - previous_close) / previous_close
                        ) * 100

                    return {
                        "symbol": symbol.replace("-USD", ""),
                        "price_usd": price_usd,
                        "price_krw": round(price_krw, 2),
                        "volume_24h": meta.get("regularMarketVolume", 0),
                        "change_24h": round(change_24h, 2),
                        "timestamp": datetime.now().isoformat(),
                    }

            except requests.exceptions.RequestException as e:
                logger.error(f"{symbol} 조회 오류 (시도 {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    time.sleep(2**attempt)  # Exponential backoff
            except json.JSONDecodeError as e:
                logger.error(f"JSON 파싱 오류 {symbol}: {e}")
                break
            except Exception as e:
                logger.error(f"예상치 못한 오류 {symbol}: {e}")
                break

        return None

    def fetch_all_crypto_prices(
        self, symbols: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        모든 암호화폐 가격 조회

        Args:
            symbols: 심볼 리스트 (None이면 기본값 사용)

        Returns:
            가격 데이터 리스트
        """
        if symbols is None:
            symbols = self.DEFAULT_SYMBOLS

        # 환율 먼저 조회
        self.fetch_usd_krw_rate()

        results = []

        for symbol in symbols:
            data = self.fetch_crypto_price(symbol)
            if data:
                results.append(data)

            # Rate limiting 방지를 위한 대기
            time.sleep(0.5)

        logger.info(f"Yahoo Finance 데이터 수집 완료: {len(results)}/{len(symbols)}개")
        return results

    def save_to_database(self, price_data: Dict[str, Any]) -> bool:
        """
        가격 데이터를 데이터베이스에 저장

        Args:
            price_data: 가격 데이터

        Returns:
            성공 여부
        """
        try:
            # 중복 체크 (같은 심볼, 같은 시간대)
            existing = (
                self.db.query(MarketTrends)
                .filter_by(source="yahoo_finance", symbol=price_data["symbol"])
                .order_by(MarketTrends.timestamp.desc())
                .first()
            )

            # 최근 5분 이내 데이터가 있으면 스킵
            if existing:
                from datetime import timedelta

                time_diff = datetime.now() - existing.timestamp
                if time_diff < timedelta(minutes=5):
                    logger.debug(f"최근 데이터 존재: {price_data['symbol']}")
                    return True

            trend = MarketTrends(
                source="yahoo_finance",
                symbol=price_data["symbol"],
                price=price_data["price_krw"],
                volume_24h=price_data["volume_24h"],
                change_24h=price_data["change_24h"],
                timestamp=datetime.fromisoformat(price_data["timestamp"]),
            )

            self.db.add(trend)
            self.db.commit()

            logger.info(
                f"Yahoo Finance 데이터 저장: {price_data['symbol']} = {price_data['price_krw']:,.0f} KRW"
            )
            return True

        except Exception as e:
            logger.error(f"데이터베이스 저장 오류: {e}")
            self.db.rollback()
            return False

    def collect_and_save(self, symbols: Optional[List[str]] = None) -> int:
        """
        데이터 수집 및 저장 (통합 메서드)

        Args:
            symbols: 심볼 리스트

        Returns:
            저장된 데이터 개수
        """
        price_data_list = self.fetch_all_crypto_prices(symbols)

        saved_count = 0
        for price_data in price_data_list:
            if self.save_to_database(price_data):
                saved_count += 1

        return saved_count
