"""
뉴스 API 라우트
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List

from backend.models import RawNews, SentimentAnalysis
from backend.config import get_db

router = APIRouter(prefix="/api/news", tags=["news"])


@router.get("/latest")
async def get_latest_news(
    limit: int = Query(50, ge=1, le=100),
    source: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """최신 뉴스 목록"""
    query = db.query(RawNews).outerjoin(
        SentimentAnalysis, RawNews.id == SentimentAnalysis.news_id
    )

    if source:
        query = query.filter(RawNews.source == source)

    news_list = query.order_by(desc(RawNews.published_at)).limit(limit).all()

    return {
        "news": [
            {
                "id": n.id,
                "source": n.source,
                "title": n.title,
                "url": n.url,
                "published_at": n.published_at.isoformat() if n.published_at else None,
                "keywords": n.keywords or [],
            }
            for n in news_list
        ]
    }


@router.get("/{news_id}/sentiment")
async def get_news_sentiment(news_id: int, db: Session = Depends(get_db)):
    """특정 뉴스의 감성 분석 결과"""
    sentiment = db.query(SentimentAnalysis).filter_by(news_id=news_id).first()

    if not sentiment:
        return {"error": "Sentiment analysis not found"}

    return {
        "news_id": news_id,
        "sentiment_score": sentiment.sentiment_score,
        "sentiment_label": sentiment.sentiment_label,
        "confidence": sentiment.confidence,
        "analyzed_at": sentiment.analyzed_at.isoformat()
    }

