"""
데이터베이스 초기화 스크립트
테이블 생성 및 기본 데이터 설정
"""

import sys
from pathlib import Path

# 통합 경로 설정 유틸리티 사용
try:
    from shared.path_utils import setup_pythonpath
    setup_pythonpath()
except ImportError:
    # Fallback: 유틸리티 로드 실패 시 하드코딩 경로 사용
    sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.models import Base
from backend.config import engine, DATABASE_URL
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_database():
    """데이터베이스 초기화"""
    try:
        logger.info(f"Connecting to database: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL}")

        # 모든 테이블 생성
        Base.metadata.create_all(bind=engine)

        logger.info("✅ Database tables created successfully!")
        logger.info("Created tables:")
        for table_name in Base.metadata.tables.keys():
            logger.info(f"  - {table_name}")

        return True

    except Exception as e:
        logger.error(f"❌ Error initializing database: {e}")
        return False


if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)

