"""
시장 데이터 API 라우트
Yahoo Finance 등 외부 API를 통한 시장 데이터 수집
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional, List

from backend.config import get_db
from backend.services.yahoo_finance_service import YahooFinanceService

router = APIRouter(prefix="/api/market", tags=["market"])


@router.post("/yahoo-finance/collect")
async def collect_yahoo_finance_data(
    background_tasks: BackgroundTasks,
    symbols: Optional[List[str]] = None,
    db: Session = Depends(get_db)
):
    """
    Yahoo Finance 데이터 수집 (백그라운드 작업)

    Args:
        symbols: 수집할 심볼 리스트 (None이면 기본값 사용)
        background_tasks: FastAPI 백그라운드 작업

    Returns:
        작업 시작 확인
    """
    try:
        service = YahooFinanceService(db)

        # 백그라운드에서 실행
        background_tasks.add_task(service.collect_and_save, symbols)

        return {
            "success": True,
            "message": "Yahoo Finance 데이터 수집 작업이 시작되었습니다",
            "symbols": symbols or service.DEFAULT_SYMBOLS
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/yahoo-finance/status")
async def get_yahoo_finance_status(db: Session = Depends(get_db)):
    """
    Yahoo Finance 데이터 수집 상태 확인

    Returns:
        최근 수집된 데이터 정보
    """
    try:
        from backend.models import MarketTrends
        from sqlalchemy import desc
        from datetime import datetime, timedelta

        # 최근 1시간 이내 데이터 조회
        hour_ago = datetime.now() - timedelta(hours=1)
        recent_data = db.query(MarketTrends).filter(
            MarketTrends.source == "yahoo_finance",
            MarketTrends.timestamp >= hour_ago
        ).order_by(desc(MarketTrends.timestamp)).all()

        symbols = list(set([d.symbol for d in recent_data]))

        return {
            "success": True,
            "recent_count": len(recent_data),
            "symbols": symbols,
            "latest_timestamp": recent_data[0].timestamp.isoformat() if recent_data else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trends")
async def get_market_trends(
    symbol: Optional[str] = None,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    시장 트렌드 데이터 조회

    Args:
        symbol: 코인 심볼 (선택적, 없으면 전체)
        limit: 반환할 개수

    Returns:
        시장 트렌드 데이터 리스트
    """
    try:
        from backend.models import MarketTrends
        from sqlalchemy import desc

        query = db.query(MarketTrends).order_by(desc(MarketTrends.timestamp))

        if symbol:
            query = query.filter(MarketTrends.symbol == symbol)

        trends = query.limit(limit).all()

        return {
            "trends": [
                {
                    "symbol": t.symbol,
                    "price": t.price,
                    "volume_24h": t.volume_24h,
                    "change_24h": t.change_24h,
                    "timestamp": t.timestamp.isoformat() if t.timestamp else None,
                    "source": t.source
                }
                for t in trends
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

