"""
Scrapyd 스케줄러
크롤링 작업을 스케줄링
"""

import schedule
import time
import logging
import requests
import yaml
import os
from datetime import datetime
from pathlib import Path

from shared.logger import setup_logger

logger = setup_logger(__name__)


class ScrapydScheduler:
    """Scrapyd 스케줄러"""

    def __init__(self, scrapyd_url: str = None):
        """
        초기화

        Args:
            scrapyd_url: Scrapyd 서버 URL (None이면 설정 파일 또는 기본값 사용)
        """
        # 설정 파일에서 scrapyd_url 로드
        if scrapyd_url is None:
            scrapyd_url = self._load_scrapyd_url()

        self.scrapyd_url = scrapyd_url
        self.project = "cointicker"
        self.spiders = self._load_spider_config()

    def _load_scrapyd_url(self):
        """설정 파일에서 Scrapyd URL 로드"""
        try:
            from shared.path_utils import get_cointicker_root
            config_file = get_cointicker_root() / "config" / "spider_config.yaml"
            if config_file.exists():
                with open(config_file, "r", encoding="utf-8") as f:
                    config = yaml.safe_load(f)
                    # spider_config.yaml에 scrapyd_url이 있으면 사용
                    if config and "scrapyd" in config:
                        return config["scrapyd"].get("url", "http://localhost:6800")
        except Exception as e:
            logger.debug(f"Failed to load scrapyd_url from config: {e}")

        # 환경 변수 또는 기본값
        return os.getenv("SCRAPYD_URL", "http://localhost:6800")

    def _load_spider_config(self):
        """spider_config.yaml에서 Spider 스케줄 정보 로드"""
        try:
            from shared.path_utils import get_cointicker_root
            config_file = get_cointicker_root() / "config" / "spider_config.yaml"
            if config_file.exists():
                with open(config_file, "r", encoding="utf-8") as f:
                    config = yaml.safe_load(f)
                    if config and "spiders" in config:
                        spiders = {}
                        for name, spider_config in config["spiders"].items():
                            if spider_config.get("enabled", True):
                                spiders[name] = {
                                    "schedule": spider_config.get("schedule", "*/5 * * * *"),
                                }
                        logger.info(f"Loaded {len(spiders)} enabled spiders from config")
                        return spiders
        except Exception as e:
            logger.warning(f"Failed to load spider_config.yaml: {e}")

        # 기본값
        return {
            "upbit_trends": {"schedule": "*/5 * * * *"},
            "saveticker": {"schedule": "*/5 * * * *"},
            "coinness": {"schedule": "*/10 * * * *"},
            "perplexity": {"schedule": "0 * * * *"},
            "cnn_fear_greed": {"schedule": "0 0 * * *"},
        }

    def schedule_spider(self, spider_name: str):
        """
        Spider 스케줄링

        Args:
            spider_name: Spider 이름
        """
        try:
            url = f"{self.scrapyd_url}/schedule.json"
            data = {
                "project": self.project,
                "spider": spider_name
            }

            response = requests.post(url, data=data, timeout=10)
            if response.status_code == 200:
                logger.info(f"Scheduled spider: {spider_name}")
                return True
            else:
                logger.error(f"Failed to schedule {spider_name}: {response.text}")
                return False

        except Exception as e:
            logger.error(f"Error scheduling {spider_name}: {e}")
            return False

    def start(self):
        """스케줄러 시작"""
        # 설정 파일에서 로드한 Spider 스케줄 등록
        for spider_name, spider_info in self.spiders.items():
            schedule_str = spider_info.get("schedule", "*/5 * * * *")
            # cron 형식 파싱 (간단한 형식만 지원: "*/5 * * * *" -> 5분마다)
            if schedule_str.startswith("*/"):
                minutes = int(schedule_str.split()[0].replace("*/", ""))
                schedule.every(minutes).minutes.do(
                    lambda name=spider_name: self.schedule_spider(name)
                )
            elif schedule_str.startswith("0 * * * *"):
                schedule.every(1).hours.do(
                    lambda name=spider_name: self.schedule_spider(name)
                )
            elif schedule_str.startswith("0 0 * * *"):
                schedule.every().day.at("00:00").do(
                    lambda name=spider_name: self.schedule_spider(name)
                )
            else:
                # 기본값: 5분마다
                schedule.every(5).minutes.do(
                    lambda name=spider_name: self.schedule_spider(name)
                )

        logger.info(f"Scrapyd scheduler started with {len(self.spiders)} spiders")

        while True:
            schedule.run_pending()
            time.sleep(60)


if __name__ == "__main__":
    scheduler = ScrapydScheduler()
    scheduler.start()

