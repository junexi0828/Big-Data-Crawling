"""
인사이트 API 라우트
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional

from backend.models import CryptoInsights
from backend.config import get_db

router = APIRouter(prefix="/api/insights", tags=["insights"])


@router.get("/recent")
async def get_recent_insights(
    limit: int = Query(20, ge=1, le=100),
    severity: Optional[str] = Query(None),
    symbol: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """최신 인사이트 목록"""
    query = db.query(CryptoInsights).order_by(desc(CryptoInsights.created_at))

    if severity:
        query = query.filter(CryptoInsights.severity == severity)

    if symbol:
        query = query.filter(CryptoInsights.symbol == symbol)

    insights = query.limit(limit).all()

    return {
        "insights": [
            {
                "id": i.id,
                "type": i.insight_type,
                "symbol": i.symbol,
                "description": i.description,
                "severity": i.severity,
                "created_at": i.created_at.isoformat()
            }
            for i in insights
        ]
    }


@router.post("/generate")
async def generate_insights(db: Session = Depends(get_db)):
    """인사이트 생성 (수동 트리거)"""
    from backend.services.insight_generator import InsightGenerator

    generator = InsightGenerator(db)
    results = generator.generate_all_insights()

    return {
        "status": "success",
        "generated": {
            "sentiment_shift": len(results.get("sentiment_shift", [])),
            "volume_spike": len(results.get("volume_spike", [])),
            "trend_reversal": len(results.get("trend_reversal", []))
        },
        "insights": results
    }

