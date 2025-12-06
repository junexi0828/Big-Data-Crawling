"""
FastAPI 백엔드 메인 애플리케이션
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import logging
import time

from backend.config import get_db, engine
from backend.models import Base
from backend.api import dashboard, news, insights, market, pipeline
from shared.path_utils import get_cointicker_root
from shared.logger import setup_logger

# 로그 파일 경로 설정
cointicker_root = get_cointicker_root()
log_file = str(cointicker_root / "logs" / "backend_api.log")
logger = setup_logger(__name__, log_file=log_file)


# uvicorn access log 필터 설정
# 헬스체크 성공(200 OK) 요청은 1분에 1번만 로그 출력
class HealthCheckAccessLogFilter(logging.Filter):
    """헬스체크 성공 요청의 access log를 필터링 (1분에 1번만 출력)"""

    _last_log_time = None  # 마지막 로그 출력 시간 (클래스 변수)
    _log_interval = 60  # 로그 출력 간격 (초)

    def filter(self, record):
        # uvicorn access log 형식: "127.0.0.1:61536 - "GET /health HTTP/1.1" 200 OK"
        try:
            message = record.getMessage().lower()
            # /health 경로와 200 상태 코드가 모두 포함된 경우
            if "/health" in message and " 200" in message:
                current_time = time.time()

                # 첫 번째 요청이거나 1분이 지난 경우에만 로그 출력
                if (
                    self._last_log_time is None
                    or (current_time - self._last_log_time) >= self._log_interval
                ):
                    self._last_log_time = current_time
                    return True  # 로그 출력 허용
                else:
                    return False  # 1분이 지나지 않았으면 로그 출력 안 함
        except Exception:
            pass
        return True  # 그 외는 로그 출력


def setup_uvicorn_logging():
    """uvicorn 로깅 설정"""
    uvicorn_access_logger = logging.getLogger("uvicorn.access")
    # 기존 필터 제거 후 추가 (중복 방지)
    uvicorn_access_logger.filters = [
        f
        for f in uvicorn_access_logger.filters
        if not isinstance(f, HealthCheckAccessLogFilter)
    ]
    uvicorn_access_logger.addFilter(HealthCheckAccessLogFilter())


# 초기 설정 (모듈 로드 시)
setup_uvicorn_logging()

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
app.include_router(pipeline.router)


@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 데이터베이스 테이블 자동 생성 및 로그 필터 설정"""
    # uvicorn이 시작된 후 로거가 재설정될 수 있으므로 필터를 다시 적용
    setup_uvicorn_logging()

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
