"""
파이프라인 오케스트레이터
전체 데이터 파이프라인을 관리하고 스케줄링
"""

import schedule
import time
import logging
import os
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
        # 프로젝트 루트 경로 설정 (master-node/orchestrator.py -> cointicker/)
        self.project_root = Path(__file__).parent.parent
        self.cointicker_dir = self.project_root / "worker-nodes" / "cointicker"

    def run_crawlers(self):
        """크롤러 실행"""
        logger.info("Starting crawlers...")

        # 각 Spider 실행
        spiders = [
            "upbit_trends",  # 5분마다
            "coinness",  # 10분마다
            "saveticker",  # 5분마다
            "perplexity",  # 1시간마다
            "cnn_fear_greed",  # 1일 1회
        ]

        for spider in spiders:
            try:
                # scrapy.cfg가 있는 디렉토리로 이동 (worker-nodes/cointicker)
                cointicker_abs = str(self.cointicker_dir.resolve())
                cmd = f"cd {cointicker_abs} && scrapy crawl {spider}"

                # PYTHONPATH 설정 (shared 모듈 import를 위해)
                env = os.environ.copy()
                pythonpath = env.get("PYTHONPATH", "")
                if pythonpath:
                    pythonpath = f"{str(self.project_root)}:{pythonpath}"
                else:
                    pythonpath = str(self.project_root)
                env["PYTHONPATH"] = pythonpath

                result = subprocess.run(
                    cmd,
                    shell=True,
                    timeout=300,
                    cwd=cointicker_abs,  # 작업 디렉토리 명시
                    env=env,  # PYTHONPATH 설정된 환경 변수 사용
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0:
                    logger.info(f"Spider {spider} completed")
                else:
                    logger.error(f"Spider {spider} failed: {result.stderr}")
            except subprocess.TimeoutExpired:
                logger.error(f"Spider {spider} timeout after 300 seconds")
            except Exception as e:
                logger.error(f"Error running spider {spider}: {e}")

    def run_mapreduce(self):
        """MapReduce 정제 작업 실행"""
        logger.info("Starting MapReduce cleaning job...")

        try:
            # 절대 경로로 MapReduce 스크립트 찾기
            mapreduce_script = (
                self.project_root / "worker-nodes" / "mapreduce" / "run_cleaner.sh"
            )
            if mapreduce_script.exists():
                script_abs = str(mapreduce_script.resolve())
                result = subprocess.run(
                    f"bash {script_abs}",
                    shell=True,
                    timeout=600,
                    cwd=str(self.project_root),  # 프로젝트 루트에서 실행
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    logger.info("MapReduce job completed")
                else:
                    logger.error(f"MapReduce job failed: {result.stderr}")
            else:
                logger.warning(f"MapReduce script not found: {mapreduce_script}")
        except subprocess.TimeoutExpired:
            logger.error("MapReduce job timeout after 600 seconds")
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
    def run_fear_greed():
        """공포·탐욕 지수 스파이더 실행"""
        orchestrator = PipelineOrchestrator()
        cointicker_abs = str(orchestrator.cointicker_dir.resolve())
        cmd = f"cd {cointicker_abs} && scrapy crawl cnn_fear_greed"
        env = os.environ.copy()
        pythonpath = env.get("PYTHONPATH", "")
        if pythonpath:
            pythonpath = f"{str(orchestrator.project_root)}:{pythonpath}"
        else:
            pythonpath = str(orchestrator.project_root)
        env["PYTHONPATH"] = pythonpath
        subprocess.run(cmd, shell=True, cwd=cointicker_abs, env=env)

    schedule.every().day.at("00:00").do(run_fear_greed)

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
