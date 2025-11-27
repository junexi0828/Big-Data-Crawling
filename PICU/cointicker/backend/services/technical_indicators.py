"""
기술적 지표 계산 서비스
RSI, MACD, Bollinger Bands 등
"""

import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
import pandas as pd
import numpy as np

from backend.models import MarketTrends, TechnicalIndicators

logger = logging.getLogger(__name__)


class TechnicalIndicatorsCalculator:
    """기술적 지표 계산기"""

    def __init__(self, db_session: Session):
        """
        초기화

        Args:
            db_session: 데이터베이스 세션
        """
        self.db = db_session

    def calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """
        RSI (Relative Strength Index) 계산

        Args:
            prices: 가격 리스트
            period: 기간 (기본값: 14)

        Returns:
            RSI 값 (0-100)
        """
        if len(prices) < period + 1:
            return 50.0  # 기본값

        try:
            prices_array = np.array(prices)
            deltas = np.diff(prices_array)

            gains = np.where(deltas > 0, deltas, 0)
            losses = np.where(deltas < 0, -deltas, 0)

            avg_gain = np.mean(gains[-period:])
            avg_loss = np.mean(losses[-period:])

            if avg_loss == 0:
                return 100.0

            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))

            return round(rsi, 2)

        except Exception as e:
            logger.error(f"Error calculating RSI: {e}")
            return 50.0

    def calculate_macd(self, prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, float]:
        """
        MACD (Moving Average Convergence Divergence) 계산

        Args:
            prices: 가격 리스트
            fast: 빠른 이동평균 기간
            slow: 느린 이동평균 기간
            signal: 시그널 라인 기간

        Returns:
            MACD 값, 시그널 값
        """
        if len(prices) < slow + signal:
            return {'macd': 0.0, 'signal': 0.0}

        try:
            prices_array = np.array(prices)

            # 이동평균 계산
            ema_fast = pd.Series(prices_array).ewm(span=fast).mean().iloc[-1]
            ema_slow = pd.Series(prices_array).ewm(span=slow).mean().iloc[-1]

            macd_line = ema_fast - ema_slow

            # 시그널 라인 (MACD의 이동평균)
            macd_values = pd.Series(prices_array).ewm(span=fast).mean() - pd.Series(prices_array).ewm(span=slow).mean()
            signal_line = macd_values.ewm(span=signal).mean().iloc[-1]

            return {
                'macd': round(float(macd_line), 4),
                'signal': round(float(signal_line), 4)
            }

        except Exception as e:
            logger.error(f"Error calculating MACD: {e}")
            return {'macd': 0.0, 'signal': 0.0}

    def calculate_bollinger_bands(self, prices: List[float], period: int = 20, std_dev: int = 2) -> Dict[str, float]:
        """
        Bollinger Bands 계산

        Args:
            prices: 가격 리스트
            period: 기간
            std_dev: 표준편차 배수

        Returns:
            상단, 중간, 하단 밴드
        """
        if len(prices) < period:
            return {'upper': 0.0, 'middle': 0.0, 'lower': 0.0}

        try:
            prices_array = np.array(prices[-period:])
            middle = np.mean(prices_array)
            std = np.std(prices_array)

            upper = middle + (std_dev * std)
            lower = middle - (std_dev * std)

            return {
                'upper': round(float(upper), 2),
                'middle': round(float(middle), 2),
                'lower': round(float(lower), 2)
            }

        except Exception as e:
            logger.error(f"Error calculating Bollinger Bands: {e}")
            return {'upper': 0.0, 'middle': 0.0, 'lower': 0.0}

    def calculate_for_symbol(self, symbol: str, limit: int = 100) -> bool:
        """
        특정 심볼에 대한 모든 기술적 지표 계산

        Args:
            symbol: 코인 심볼
            limit: 사용할 최근 데이터 개수

        Returns:
            성공 여부
        """
        try:
            # 최근 가격 데이터 조회
            trends = self.db.query(MarketTrends).filter_by(
                symbol=symbol
            ).order_by(MarketTrends.timestamp.desc()).limit(limit).all()

            if len(trends) < 26:  # MACD를 위해 최소 26개 필요
                logger.warning(f"Not enough data for {symbol}")
                return False

            # 가격 리스트 추출
            prices = [t.price for t in reversed(trends) if t.price]

            # 지표 계산
            rsi = self.calculate_rsi(prices)
            macd_data = self.calculate_macd(prices)
            bb_data = self.calculate_bollinger_bands(prices)

            # DB에 저장
            latest_trend = trends[0]
            indicator = TechnicalIndicators(
                symbol=symbol,
                timestamp=latest_trend.timestamp,
                rsi=rsi,
                macd=macd_data['macd'],
                macd_signal=macd_data['signal'],
                bb_upper=bb_data['upper'],
                bb_middle=bb_data['middle'],
                bb_lower=bb_data['lower'],
                volume=latest_trend.volume_24h
            )

            self.db.add(indicator)
            self.db.commit()

            logger.info(f"Calculated indicators for {symbol}")
            return True

        except Exception as e:
            logger.error(f"Error calculating indicators for {symbol}: {e}")
            self.db.rollback()
            return False

