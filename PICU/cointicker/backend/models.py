"""
데이터베이스 모델 정의
"""

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Float,
    JSON,
    Boolean,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()


class RawNews(Base):
    """원시 뉴스 테이블"""

    __tablename__ = "raw_news"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(50), nullable=False)
    title = Column(Text, nullable=False)
    url = Column(Text)
    content = Column(Text)
    published_at = Column(DateTime)
    keywords = Column(JSON)
    collected_at = Column(DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs):
        """초기화 시 collected_at 자동 설정"""
        if "collected_at" not in kwargs or kwargs.get("collected_at") is None:
            kwargs["collected_at"] = datetime.utcnow()
        super().__init__(**kwargs)


class SentimentAnalysis(Base):
    """감성 분석 결과 테이블"""

    __tablename__ = "sentiment_analysis"

    id = Column(Integer, primary_key=True, autoincrement=True)
    news_id = Column(Integer, nullable=False)
    sentiment_score = Column(Float)  # -1.0 ~ 1.0
    sentiment_label = Column(String(20))  # positive/negative/neutral
    confidence = Column(Float)
    analyzed_at = Column(DateTime, default=datetime.now)


class MarketTrends(Base):
    """시장 트렌드 테이블"""

    __tablename__ = "market_trends"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(50))
    symbol = Column(String(20))
    volume_24h = Column(Float)
    price = Column(Float)
    change_24h = Column(Float)
    timestamp = Column(DateTime)


class TechnicalIndicators(Base):
    """기술적 지표 테이블"""

    __tablename__ = "technical_indicators"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20))
    timestamp = Column(DateTime)
    rsi = Column(Float)
    macd = Column(Float)
    macd_signal = Column(Float)
    bb_upper = Column(Float)
    bb_middle = Column(Float)
    bb_lower = Column(Float)
    volume = Column(Float)


class FearGreedIndex(Base):
    """공포·탐욕 지수 테이블"""

    __tablename__ = "fear_greed_index"

    id = Column(Integer, primary_key=True, autoincrement=True)
    value = Column(Integer)  # 0-100
    classification = Column(String(20))
    timestamp = Column(DateTime, default=datetime.now)


class CryptoInsights(Base):
    """암호화폐 인사이트 테이블"""

    __tablename__ = "crypto_insights"

    id = Column(Integer, primary_key=True, autoincrement=True)
    insight_type = Column(String(50))
    symbol = Column(String(20))
    description = Column(Text)
    severity = Column(String(20))  # low/medium/high/critical
    related_news = Column(JSON)
    created_at = Column(DateTime, default=datetime.now)


# 데이터베이스 연결 설정 (나중에 config에서 로드)
def get_db_engine(database_url: str):
    """데이터베이스 엔진 생성"""
    return create_engine(database_url)


def get_db_session(engine):
    """세션 생성"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()
