"""
백엔드 설정 파일
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 데이터베이스 설정
DATABASE_TYPE = os.getenv("DATABASE_TYPE", "mariadb")
DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
DATABASE_PORT = os.getenv("DATABASE_PORT", "3306")
DATABASE_USER = os.getenv("DATABASE_USER", "cointicker")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "password")
DATABASE_NAME = os.getenv("DATABASE_NAME", "cointicker")

# 데이터베이스 URL 생성
# 환경 변수로 SQLite 강제 설정 가능
if os.getenv("USE_SQLITE", "false").lower() == "true":
    DATABASE_URL = "sqlite:///./cointicker.db"
elif DATABASE_TYPE == "mariadb" or DATABASE_TYPE == "mysql":
    DATABASE_URL = f"mysql+pymysql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
elif DATABASE_TYPE == "postgresql":
    DATABASE_URL = f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
else:
    # 기본값: SQLite (개발/테스트용)
    DATABASE_URL = "sqlite:///./cointicker.db"

# 엔진 및 세션 생성
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """데이터베이스 세션 의존성"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# API 설정
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "5000"))

# HDFS 설정
HDFS_NAMENODE = os.getenv("HDFS_NAMENODE", "hdfs://localhost:9000")

# 로깅 설정
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
