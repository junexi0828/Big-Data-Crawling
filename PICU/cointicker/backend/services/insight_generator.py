"""
인사이트 생성 서비스
감성 급변, 거래량 급증, 추세 반전 등 감지
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from backend.models import (
    RawNews, SentimentAnalysis, MarketTrends,
    TechnicalIndicators, CryptoInsights
)

logger = logging.getLogger(__name__)


class InsightGenerator:
    """인사이트 생성기"""

    def __init__(self, db_session: Session):
        """
        초기화

        Args:
            db_session: 데이터베이스 세션
        """
        self.db = db_session

    def detect_sentiment_shift(self, symbol: str = 'BTC', threshold: float = 30.0) -> List[Dict[str, Any]]:
        """
        감성 급변 감지

        Args:
            symbol: 코인 심볼
            threshold: 변화 임계값 (퍼센트)

        Returns:
            감지된 인사이트 리스트
        """
        try:
            # 최근 6시간 vs 이전 18시간 감성 비교
            now = datetime.now()
            recent_start = now - timedelta(hours=6)
            past_start = now - timedelta(hours=24)
            past_end = now - timedelta(hours=6)

            # 최근 감성 평균
            recent_avg = self.db.query(func.avg(SentimentAnalysis.sentiment_score)).join(
                RawNews, SentimentAnalysis.news_id == RawNews.id
            ).filter(
                and_(
                    RawNews.published_at >= recent_start,
                    RawNews.keywords.contains([symbol])
                )
            ).scalar()

            # 이전 감성 평균
            past_avg = self.db.query(func.avg(SentimentAnalysis.sentiment_score)).join(
                RawNews, SentimentAnalysis.news_id == RawNews.id
            ).filter(
                and_(
                    RawNews.published_at >= past_start,
                    RawNews.published_at < past_end,
                    RawNews.keywords.contains([symbol])
                )
            ).scalar()

            if recent_avg and past_avg and past_avg != 0:
                change = abs((recent_avg - past_avg) / abs(past_avg) * 100)

                if change >= threshold:
                    insight = CryptoInsights(
                        insight_type='sentiment_shift',
                        symbol=symbol,
                        description=f"{symbol} 감성 {change:.1f}% 급변 감지 (최근 6시간 vs 이전 18시간)",
                        severity='high' if change >= 50 else 'medium',
                        related_news=[]
                    )

                    self.db.add(insight)
                    self.db.commit()

                    return [{
                        'type': 'sentiment_shift',
                        'symbol': symbol,
                        'change': change,
                        'severity': insight.severity
                    }]

            return []

        except Exception as e:
            logger.error(f"Error detecting sentiment shift: {e}")
            self.db.rollback()
            return []

    def detect_volume_spike(self, threshold: float = 1.5) -> List[Dict[str, Any]]:
        """
        거래량 급증 감지

        Args:
            threshold: 평균 대비 배수 (기본값: 1.5배)

        Returns:
            감지된 인사이트 리스트
        """
        try:
            # 최근 7일 데이터로 평균 계산
            week_ago = datetime.now() - timedelta(days=7)

            # 심볼별 최근 거래량과 평균 비교
            results = self.db.query(
                MarketTrends.symbol,
                func.max(MarketTrends.volume_24h).label('recent_volume'),
                func.avg(MarketTrends.volume_24h).label('avg_volume')
            ).filter(
                MarketTrends.timestamp >= week_ago
            ).group_by(MarketTrends.symbol).all()

            insights = []
            for symbol, recent_vol, avg_vol in results:
                if avg_vol and avg_vol > 0:
                    spike_ratio = recent_vol / avg_vol

                    if spike_ratio >= threshold:
                        insight = CryptoInsights(
                            insight_type='volume_spike',
                            symbol=symbol,
                            description=f"{symbol} 거래량 {spike_ratio:.1f}배 급증 (7일 평균 대비)",
                            severity='critical' if spike_ratio >= 2.0 else 'high',
                            related_news=[]
                        )

                        self.db.add(insight)
                        insights.append({
                            'type': 'volume_spike',
                            'symbol': symbol,
                            'ratio': spike_ratio,
                            'severity': insight.severity
                        })

            if insights:
                self.db.commit()

            return insights

        except Exception as e:
            logger.error(f"Error detecting volume spike: {e}")
            self.db.rollback()
            return []

    def detect_trend_reversal(self) -> List[Dict[str, Any]]:
        """
        추세 반전 감지 (RSI + MACD 동시 신호)

        Returns:
            감지된 인사이트 리스트
        """
        try:
            # 최신 기술적 지표 조회
            latest_indicators = self.db.query(TechnicalIndicators).order_by(
                TechnicalIndicators.timestamp.desc()
            ).limit(100).all()

            insights = []
            for indicator in latest_indicators:
                # RSI 과매수/과매도 + MACD 골든크로스/데드크로스
                signals = []

                if indicator.rsi:
                    if indicator.rsi < 30:
                        signals.append('RSI 과매도')
                    elif indicator.rsi > 70:
                        signals.append('RSI 과매수')

                if indicator.macd and indicator.macd_signal:
                    if indicator.macd > indicator.macd_signal:
                        signals.append('MACD 상승')
                    else:
                        signals.append('MACD 하락')

                # 강력한 신호 조합
                if len(signals) >= 2:
                    insight = CryptoInsights(
                        insight_type='trend_reversal',
                        symbol=indicator.symbol,
                        description=f"{indicator.symbol} 추세 반전 신호: {', '.join(signals)}",
                        severity='high',
                        related_news=[]
                    )

                    self.db.add(insight)
                    insights.append({
                        'type': 'trend_reversal',
                        'symbol': indicator.symbol,
                        'signals': signals
                    })

            if insights:
                self.db.commit()

            return insights

        except Exception as e:
            logger.error(f"Error detecting trend reversal: {e}")
            self.db.rollback()
            return []

    def generate_all_insights(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        모든 인사이트 생성

        Returns:
            인사이트 딕셔너리
        """
        logger.info("Generating all insights...")

        sentiment_insights = self.detect_sentiment_shift()
        volume_insights = self.detect_volume_spike()
        trend_insights = self.detect_trend_reversal()

        return {
            'sentiment_shift': sentiment_insights,
            'volume_spike': volume_insights,
            'trend_reversal': trend_insights
        }

