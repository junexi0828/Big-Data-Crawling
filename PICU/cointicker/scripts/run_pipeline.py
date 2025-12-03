#!/usr/bin/env python3
"""
전체 파이프라인 실행 스크립트
"""

import sys
import os
from pathlib import Path

# 통합 경로 설정 유틸리티 사용
try:
    from shared.path_utils import setup_pythonpath
    setup_pythonpath()
except ImportError:
    # Fallback: 유틸리티 로드 실패 시 하드코딩 경로 사용
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    sys.path.insert(0, str(project_root / "shared"))

import logging
from datetime import datetime
from shared.logger import setup_logger
from shared.hdfs_client import HDFSClient

# 서비스 import
from backend.config import get_db, engine
from backend.services.data_loader import DataLoader
from backend.services.sentiment_analyzer import SentimentAnalyzer
from backend.services.technical_indicators import TechnicalIndicatorsCalculator
from backend.services.insight_generator import InsightGenerator

logger = setup_logger(__name__)


def run_full_pipeline():
    """전체 파이프라인 실행"""
    logger.info("=" * 60)
    logger.info(f"[{datetime.now()}] Full Pipeline Started")
    logger.info("=" * 60)

    db = next(get_db())
    hdfs_client = HDFSClient()

    try:
        # Step 1: HDFS에서 데이터 로드
        logger.info("Step 1: Loading data from HDFS...")
        data_loader = DataLoader(db, hdfs_client)
        data_loader.load_from_hdfs()

        # Step 2: 감성 분석
        logger.info("Step 2: Running sentiment analysis...")
        sentiment_analyzer = SentimentAnalyzer(db)
        analyzed_count = sentiment_analyzer.batch_analyze(limit=100)
        logger.info(f"Analyzed {analyzed_count} news articles")

        # Step 3: 기술적 지표 계산
        logger.info("Step 3: Calculating technical indicators...")
        indicator_calc = TechnicalIndicatorsCalculator(db)
        symbols = ['BTC', 'ETH', 'XRP', 'ADA', 'DOGE']
        for symbol in symbols:
            indicator_calc.calculate_for_symbol(symbol)

        # Step 4: 인사이트 생성
        logger.info("Step 4: Generating insights...")
        insight_gen = InsightGenerator(db)
        insights = insight_gen.generate_all_insights()
        total_insights = sum(len(v) for v in insights.values())
        logger.info(f"Generated {total_insights} insights")

        logger.info("=" * 60)
        logger.info(f"[{datetime.now()}] Full Pipeline Completed")
        logger.info("=" * 60)

        return True

    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        return False

    finally:
        db.close()


if __name__ == "__main__":
    success = run_full_pipeline()
    sys.exit(0 if success else 1)

