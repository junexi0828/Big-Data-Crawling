"""
백엔드 설정 파일
환경 변수 우선, 설정 파일 fallback
"""

import os
import yaml
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 설정 파일 로드 (환경 변수 우선)
def _load_database_config():
    """database_config.yaml에서 데이터베이스 설정 로드"""
    try:
        # cointicker/config/database_config.yaml 찾기
        current_file = Path(__file__)
        config_file = current_file.parent.parent / "config" / "database_config.yaml"

        if config_file.exists():
            with open(config_file, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
                if config and "database" in config:
                    db_config = config["database"]
                    # 타입에 따라 적절한 설정 반환
                    db_type = db_config.get("type", "mariadb")
                    if db_type in ["mariadb", "mysql"]:
                        mariadb_config = db_config.get("mariadb", {})
                        return {
                            "type": db_type,
                            "host": mariadb_config.get("host", "localhost"),
                            "port": mariadb_config.get("port", 3306),
                            "user": mariadb_config.get("user", "cointicker"),
                            "password": mariadb_config.get("password", "password"),
                            "database": mariadb_config.get("database", "cointicker"),
                        }
                    elif db_type == "postgresql":
                        pg_config = db_config.get("postgresql", {})
                        return {
                            "type": db_type,
                            "host": pg_config.get("host", "localhost"),
                            "port": pg_config.get("port", 5432),
                            "user": pg_config.get("user", "cointicker"),
                            "password": pg_config.get("password", "password"),
                            "database": pg_config.get("database", "cointicker"),
                        }
    except Exception as e:
        import logging
        logging.getLogger(__name__).debug(f"Failed to load database_config.yaml: {e}")
    return None

# 설정 파일에서 로드 시도
_db_config = _load_database_config()

# 데이터베이스 설정 (환경 변수 우선, 설정 파일 fallback)
DATABASE_TYPE = os.getenv("DATABASE_TYPE", _db_config.get("type", "mariadb") if _db_config else "mariadb")
DATABASE_HOST = os.getenv("DATABASE_HOST", _db_config.get("host", "localhost") if _db_config else "localhost")
DATABASE_PORT = os.getenv("DATABASE_PORT", str(_db_config.get("port", 3306)) if _db_config else "3306")
DATABASE_USER = os.getenv("DATABASE_USER", _db_config.get("user", "cointicker") if _db_config else "cointicker")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", _db_config.get("password", "password") if _db_config else "password")
DATABASE_NAME = os.getenv("DATABASE_NAME", _db_config.get("database", "cointicker") if _db_config else "cointicker")

# 데이터베이스 URL 생성
# 환경 변수로 SQLite 강제 설정 가능
if os.getenv("USE_SQLITE", "false").lower() == "true":
    DATABASE_URL = "sqlite:///./data/cointicker.db"
elif DATABASE_TYPE == "mariadb" or DATABASE_TYPE == "mysql":
    DATABASE_URL = f"mysql+pymysql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
elif DATABASE_TYPE == "postgresql":
    DATABASE_URL = f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
else:
    # 기본값: SQLite (개발/테스트용)
    DATABASE_URL = "sqlite:///./data/cointicker.db"

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


# API 설정 (환경 변수 우선, 설정 파일 fallback)
def _load_cluster_config():
    """cluster_config.yaml에서 클러스터 설정 로드"""
    try:
        current_file = Path(__file__)
        config_file = current_file.parent.parent / "config" / "cluster_config.yaml"

        if config_file.exists():
            with open(config_file, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
                if config and "hadoop" in config:
                    hadoop_config = config["hadoop"]
                    hdfs_config = hadoop_config.get("hdfs", {})
                    return {
                        "hdfs_namenode": hdfs_config.get("namenode", "hdfs://localhost:9000"),
                    }
    except Exception as e:
        import logging
        logging.getLogger(__name__).debug(f"Failed to load cluster_config.yaml: {e}")
    return None

_cluster_config = _load_cluster_config()

API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "5000"))

# HDFS 설정 (환경 변수 우선, 설정 파일 fallback)
HDFS_NAMENODE = os.getenv(
    "HDFS_NAMENODE",
    _cluster_config.get("hdfs_namenode", "hdfs://localhost:9000") if _cluster_config else "hdfs://localhost:9000"
)

# 로깅 설정
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
