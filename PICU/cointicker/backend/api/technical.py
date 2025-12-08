"""
기술적 지표 API 라우트
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from datetime import datetime, timedelta

from backend.config import get_db
from backend.models import TechnicalIndicators

router = APIRouter(prefix="/api/technical-indicators", tags=["technical"])


@router.get("/{symbol}")
async def get_technical_indicators(
    symbol: str,
    hours: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db)
):
    """
    특정 코인의 기술적 지표 조회

    Args:
        symbol: 코인 심볼 (예: BTC, ETH)
        hours: 조회할 시간 범위 (기본 24시간)

    Returns:
        기술적 지표 데이터
    """
    try:
        start_time = datetime.now() - timedelta(hours=hours)

        indicators = db.query(TechnicalIndicators).filter(
            TechnicalIndicators.symbol == symbol,
            TechnicalIndicators.timestamp >= start_time
        ).order_by(desc(TechnicalIndicators.timestamp)).first()

        if not indicators:
            # 데이터가 없으면 기본값 반환
            return {
                "symbol": symbol,
                "indicators": None,
                "message": "No technical indicators data available"
            }

        return {
            "symbol": symbol,
            "indicators": {
                "rsi": indicators.rsi,
                "macd": {
                    "value": indicators.macd,
                    "signal": indicators.macd_signal
                },
                "bollinger_bands": {
                    "upper": indicators.bb_upper,
                    "middle": indicators.bb_middle,
                    "lower": indicators.bb_lower
                },
                "volume": indicators.volume,
                "timestamp": indicators.timestamp.isoformat() if indicators.timestamp else None
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}/history")
async def get_technical_indicators_history(
    symbol: str,
    hours: int = Query(24, ge=1, le=168),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    특정 코인의 기술적 지표 히스토리 조회

    Args:
        symbol: 코인 심볼
        hours: 조회할 시간 범위
        limit: 반환할 개수

    Returns:
        기술적 지표 히스토리 리스트
    """
    try:
        start_time = datetime.now() - timedelta(hours=hours)

        indicators = db.query(TechnicalIndicators).filter(
            TechnicalIndicators.symbol == symbol,
            TechnicalIndicators.timestamp >= start_time
        ).order_by(desc(TechnicalIndicators.timestamp)).limit(limit).all()

        return {
            "symbol": symbol,
            "indicators": [
                {
                    "timestamp": ind.timestamp.isoformat() if ind.timestamp else None,
                    "rsi": ind.rsi,
                    "macd": ind.macd,
                    "macd_signal": ind.macd_signal,
                    "bollinger_bands": {
                        "upper": ind.bb_upper,
                        "middle": ind.bb_middle,
                        "lower": ind.bb_lower
                    },
                    "volume": ind.volume
                }
                for ind in indicators
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

