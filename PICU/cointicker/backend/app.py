"""
FastAPI 백엔드 메인 애플리케이션
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

from backend.config import get_db
from backend.api import dashboard, news, insights

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


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {"message": "CoinTicker API", "version": "1.0.0", "status": "running"}


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """헬스 체크"""
    try:
        # DB 연결 확인
        db.execute("SELECT 1")
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5000)
