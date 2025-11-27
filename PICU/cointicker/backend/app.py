"""
FastAPI 백엔드 메인 애플리케이션
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
import logging

from backend.config import get_db, engine
from backend.models import Base
from backend.api import dashboard, news, insights, market

logger = logging.getLogger(__name__)

app = FastAPI(
    title="CoinTicker API", description="암호화폐 시장 동향 분석 API", version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(dashboard.router)
app.include_router(news.router)
app.include_router(insights.router)
app.include_router(market.router)


@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 데이터베이스 테이블 자동 생성"""
    try:
        logger.info("데이터베이스 테이블 생성 중...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ 데이터베이스 테이블 생성 완료")
    except Exception as e:
        logger.warning(f"⚠️ 데이터베이스 테이블 생성 중 오류 발생 (계속 진행): {e}")


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {"message": "CoinTicker API", "version": "1.0.0", "status": "running"}


@app.get("/health")
async def health_check():
    """헬스 체크"""
    try:
        # DB 연결 확인 (선택적)
        db_status = "unknown"
        try:
            db = next(get_db())
            from sqlalchemy import text

            db.execute(text("SELECT 1"))
            db.close()
            db_status = "connected"
        except Exception as db_error:
            db_status = f"disconnected ({str(db_error)[:50]})"

        return {
            "status": "healthy",
            "database": db_status,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {
            "status": "degraded",
            "database": "unknown",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5000)
