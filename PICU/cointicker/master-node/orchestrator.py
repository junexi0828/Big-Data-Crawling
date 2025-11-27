"""
파이프라인 오케스트레이터
전체 데이터 파이프라인을 관리하고 스케줄링
"""

import schedule
import time
import logging
from datetime import datetime
from pathlib import Path
import subprocess

from shared.logger import setup_logger

logger = setup_logger(__name__)


class PipelineOrchestrator:
    """파이프라인 오케스트레이터"""

    def __init__(self):
        """초기화"""
        self.worker_nodes = []
        self.hdfs_client = None

    def run_crawlers(self):
        """크롤러 실행"""
        logger.info("Starting crawlers...")

        # 각 Spider 실행
        spiders = [
            'upbit_trends',      # 5분마다
            'coinness',          # 10분마다
            'saveticker',        # 5분마다
            'perplexity',        # 1시간마다
            'cnn_fear_greed'     # 1일 1회
        ]

        for spider in spiders:
            try:
                cmd = f"cd worker-nodes && scrapy crawl {spider}"
                subprocess.run(cmd, shell=True, timeout=300)
                logger.info(f"Spider {spider} completed")
            except Exception as e:
                logger.error(f"Error running spider {spider}: {e}")

    def run_mapreduce(self):
        """MapReduce 정제 작업 실행"""
        logger.info("Starting MapReduce cleaning job...")

        try:
            mapreduce_script = Path("worker-nodes/mapreduce/run_cleaner.sh")
            if mapreduce_script.exists():
                subprocess.run(f"bash {mapreduce_script}", shell=True, timeout=600)
                logger.info("MapReduce job completed")
            else:
                logger.warning("MapReduce script not found")
        except Exception as e:
            logger.error(f"Error running MapReduce: {e}")

    def run_full_pipeline(self):
        """전체 파이프라인 실행"""
        logger.info("=" * 60)
        logger.info(f"[{datetime.now()}] Full pipeline started")
        logger.info("=" * 60)

        try:
            # Step 1: 크롤링
            logger.info("Step 1: Running crawlers...")
            self.run_crawlers()

            # Step 2: MapReduce 정제
            logger.info("Step 2: Running MapReduce cleaning...")
            self.run_mapreduce()

            logger.info("=" * 60)
            logger.info(f"[{datetime.now()}] Full pipeline completed")
            logger.info("=" * 60)

        except Exception as e:
            logger.error(f"Pipeline error: {e}")


def main():
    """메인 함수"""
    orchestrator = PipelineOrchestrator()

    # 스케줄 등록
    # 5분마다: 실시간 데이터 크롤링
    schedule.every(5).minutes.do(lambda: orchestrator.run_crawlers())

    # 30분마다: 전체 파이프라인
    schedule.every(30).minutes.do(lambda: orchestrator.run_full_pipeline())

    # 매일 자정: 공포·탐욕 지수
    schedule.every().day.at("00:00").do(
        lambda: subprocess.run("cd worker-nodes && scrapy crawl cnn_fear_greed", shell=True)
    )

    logger.info("Pipeline orchestrator started")
    logger.info("Scheduled jobs:")
    logger.info("  - Crawlers: Every 5 minutes")
    logger.info("  - Full pipeline: Every 30 minutes")
    logger.info("  - Fear & Greed Index: Daily at 00:00")

    # 첫 실행
    orchestrator.run_full_pipeline()

    # 무한 루프
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()

