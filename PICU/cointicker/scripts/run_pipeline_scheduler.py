#!/usr/bin/env python3
"""
Tier 2 파이프라인 스케줄러
주기적으로 HDFS에서 데이터를 가져와 DB에 적재
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트를 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "shared"))

import schedule
import time
import logging
from datetime import datetime
from shared.logger import setup_logger

# 파이프라인 import
from scripts.run_pipeline import run_full_pipeline

logger = setup_logger(__name__)


def run_pipeline_job():
    """파이프라인 작업 실행"""
    logger.info("=" * 60)
    logger.info(f"[{datetime.now()}] Tier 2 Pipeline Job Started")
    logger.info("=" * 60)

    try:
        success = run_full_pipeline()
        if success:
            logger.info("✅ Pipeline job completed successfully")
        else:
            logger.error("❌ Pipeline job failed")
        return success
    except Exception as e:
        logger.error(f"❌ Pipeline job error: {e}")
        return False


def main():
    """메인 함수"""
    logger.info("Tier 2 Pipeline Scheduler Started")
    logger.info("Scheduled jobs:")
    logger.info("  - Full pipeline: Every 30 minutes")

    # 30분마다 실행
    schedule.every(30).minutes.do(run_pipeline_job)

    # 첫 실행 (5초 후)
    def first_run():
        time.sleep(5)
        run_pipeline_job()

    import threading

    threading.Thread(target=first_run, daemon=True).start()

    # 무한 루프
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Scheduler error: {e}")
        sys.exit(1)
