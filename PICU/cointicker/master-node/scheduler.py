"""
Scrapyd 스케줄러
크롤링 작업을 스케줄링
"""

import schedule
import time
import logging
import requests
from datetime import datetime

from shared.logger import setup_logger

logger = setup_logger(__name__)


class ScrapydScheduler:
    """Scrapyd 스케줄러"""

    def __init__(self, scrapyd_url: str = "http://localhost:6800"):
        """
        초기화

        Args:
            scrapyd_url: Scrapyd 서버 URL
        """
        self.scrapyd_url = scrapyd_url
        self.project = "cointicker"

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
        # 5분마다: Upbit, SaveTicker
        schedule.every(5).minutes.do(
            lambda: self.schedule_spider('upbit_trends')
        )
        schedule.every(5).minutes.do(
            lambda: self.schedule_spider('saveticker')
        )

        # 10분마다: Coinness
        schedule.every(10).minutes.do(
            lambda: self.schedule_spider('coinness')
        )

        # 1시간마다: Perplexity
        schedule.every(1).hours.do(
            lambda: self.schedule_spider('perplexity')
        )

        # 매일 자정: CNN Fear & Greed
        schedule.every().day.at("00:00").do(
            lambda: self.schedule_spider('cnn_fear_greed')
        )

        logger.info("Scrapyd scheduler started")

        while True:
            schedule.run_pending()
            time.sleep(60)


if __name__ == "__main__":
    scheduler = ScrapydScheduler()
    scheduler.start()

