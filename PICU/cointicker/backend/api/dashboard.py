"""
대시보드 API 라우트
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from typing import List

from backend.models import (
    RawNews, SentimentAnalysis, MarketTrends,
    FearGreedIndex, CryptoInsights
)
from backend.config import get_db

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary")
async def get_summary(db: Session = Depends(get_db)):
    """대시보드 요약 정보"""
    try:
        # 공포·탐욕 지수 (최신)
        fgi = None
        try:
            fgi = db.query(FearGreedIndex).order_by(desc(FearGreedIndex.timestamp)).first()
        except Exception as e:
            # 테이블이 없거나 데이터가 없는 경우 기본값 사용
            pass

        # 최근 24시간 감성 평균
        sentiment_avg = None
        try:
            day_ago = datetime.now() - timedelta(hours=24)
            sentiment_avg = db.query(func.avg(SentimentAnalysis.sentiment_score)).join(
                RawNews, SentimentAnalysis.news_id == RawNews.id
            ).filter(RawNews.published_at >= day_ago).scalar()
        except Exception as e:
            # 테이블이 없거나 데이터가 없는 경우 기본값 사용
            pass

        # 거래량 Top 5
        top_volume = []
        try:
            top_volume = db.query(MarketTrends).order_by(
                desc(MarketTrends.volume_24h)
            ).limit(5).all()
        except Exception as e:
            # 테이블이 없거나 데이터가 없는 경우 빈 리스트 사용
            pass

        # 최신 인사이트
        latest_insights = []
        try:
            latest_insights = db.query(CryptoInsights).order_by(
                desc(CryptoInsights.created_at)
            ).limit(10).all()
        except Exception as e:
            # 테이블이 없거나 데이터가 없는 경우 빈 리스트 사용
            pass

        return {
            "fear_greed_index": {
                "value": fgi.value if fgi else 50,
                "classification": fgi.classification if fgi else "Neutral"
            },
            "sentiment_average": round(sentiment_avg, 2) if sentiment_avg else 0.0,
            "top_volume_coins": [
                {
                    "symbol": t.symbol,
                    "volume_24h": t.volume_24h,
                    "change_24h": t.change_24h
                }
                for t in top_volume
            ],
            "latest_insights": [
                {
                    "type": i.insight_type,
                    "symbol": i.symbol,
                    "description": i.description,
                    "severity": i.severity
                }
                for i in latest_insights
            ]
        }

    except Exception as e:
        # 예상치 못한 오류 발생 시 상세 정보 반환
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sentiment-timeline")
async def get_sentiment_timeline(hours: int = 24, db: Session = Depends(get_db)):
    """감성 추이 데이터"""
    try:
        start_time = datetime.now() - timedelta(hours=hours)

        results = db.query(
            func.date_format(RawNews.published_at, '%Y-%m-%d %H:00:00').label('hour'),
            func.avg(SentimentAnalysis.sentiment_score).label('avg_sentiment'),
            func.count(RawNews.id).label('news_count')
        ).join(
            SentimentAnalysis, RawNews.id == SentimentAnalysis.news_id
        ).filter(
            RawNews.published_at >= start_time
        ).group_by('hour').order_by('hour').all()

        return {
            "timeline": [
                {
                    "timestamp": row.hour,
                    "sentiment": round(row.avg_sentiment, 2),
                    "count": row.news_count
                }
                for row in results
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

