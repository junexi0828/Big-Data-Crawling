"""
Spider 모듈
Scrapy Spider를 관리하는 모듈
"""

import subprocess
from typing import Dict, Any
from pathlib import Path

from gui.core.module_manager import ModuleInterface
from shared.logger import setup_logger

logger = setup_logger(__name__)


class SpiderModule(ModuleInterface):
    """Spider 모듈 클래스"""

    def __init__(self, name: str = "SpiderModule"):
        super().__init__(name)
        self.spiders = {
            "upbit_trends": {"status": "stopped", "schedule": "5분"},
            "coinness": {"status": "stopped", "schedule": "10분"},
            "saveticker": {"status": "stopped", "schedule": "5분"},
            "perplexity": {"status": "stopped", "schedule": "1시간"},
            "cnn_fear_greed": {"status": "stopped", "schedule": "1일"}
        }
        self.worker_nodes_path = Path("worker-nodes")

    def initialize(self, config: dict) -> bool:
        """모듈 초기화"""
        try:
            self.config = config
            self.worker_nodes_path = Path(config.get("worker_nodes_path", "worker-nodes"))
            logger.info("Spider 모듈 초기화 완료")
            return True
        except Exception as e:
            logger.error(f"Spider 모듈 초기화 실패: {e}")
            return False

    def start(self) -> bool:
        """모듈 시작"""
        self.status = "running"
        logger.info("Spider 모듈 시작")
        return True

    def stop(self) -> bool:
        """모듈 중지"""
        # 실행 중인 모든 Spider 중지
        for spider_name in self.spiders:
            if self.spiders[spider_name]["status"] == "running":
                self.stop_spider(spider_name)

        self.status = "stopped"
        logger.info("Spider 모듈 중지")
        return True

    def execute(self, command: str, params: dict = None) -> dict:
        """명령어 실행"""
        params = params or {}

        if command == "list_spiders":
            return {
                "success": True,
                "spiders": list(self.spiders.keys())
            }

        elif command == "start_spider":
            spider_name = params.get("spider_name")
            host = params.get("host")
            if not spider_name:
                return {"success": False, "error": "spider_name이 필요합니다"}

            return self.start_spider(spider_name, host)

        elif command == "stop_spider":
            spider_name = params.get("spider_name")
            host = params.get("host")
            if not spider_name:
                return {"success": False, "error": "spider_name이 필요합니다"}

            return self.stop_spider(spider_name, host)

        elif command == "get_spider_status":
            spider_name = params.get("spider_name")
            if spider_name:
                return {
                    "success": True,
                    "status": self.spiders.get(spider_name, {})
                }
            else:
                return {
                    "success": True,
                    "spiders": self.spiders
                }

        else:
            return {"success": False, "error": f"알 수 없는 명령어: {command}"}

    def start_spider(self, spider_name: str, host: str = None) -> dict:
        """
        Spider 시작

        Args:
            spider_name: Spider 이름
            host: 호스트 주소 (None이면 로컬)

        Returns:
            실행 결과
        """
        if spider_name not in self.spiders:
            return {"success": False, "error": f"알 수 없는 Spider: {spider_name}"}

        try:
            if host:
                # 원격 실행 (SSH 필요)
                cmd = f"ssh {host} 'cd ~/cointicker/worker-nodes && scrapy crawl {spider_name}'"
            else:
                # 로컬 실행
                cmd = f"cd {self.worker_nodes_path} && scrapy crawl {spider_name}"

            process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            self.spiders[spider_name]["status"] = "running"
            self.spiders[spider_name]["process"] = process

            logger.info(f"Spider 시작: {spider_name}")
            return {
                "success": True,
                "spider_name": spider_name,
                "pid": process.pid
            }
        except Exception as e:
            logger.error(f"Spider 시작 실패 {spider_name}: {e}")
            return {"success": False, "error": str(e)}

    def stop_spider(self, spider_name: str, host: str = None) -> dict:
        """
        Spider 중지

        Args:
            spider_name: Spider 이름
            host: 호스트 주소

        Returns:
            실행 결과
        """
        if spider_name not in self.spiders:
            return {"success": False, "error": f"알 수 없는 Spider: {spider_name}"}

        try:
            if host:
                cmd = f"ssh {host} 'pkill -f \"scrapy crawl {spider_name}\"'"
            else:
                if "process" in self.spiders[spider_name]:
                    process = self.spiders[spider_name]["process"]
                    process.terminate()
                cmd = f"pkill -f 'scrapy crawl {spider_name}'"

            subprocess.run(cmd, shell=True, timeout=5)

            self.spiders[spider_name]["status"] = "stopped"
            if "process" in self.spiders[spider_name]:
                del self.spiders[spider_name]["process"]

            logger.info(f"Spider 중지: {spider_name}")
            return {"success": True, "spider_name": spider_name}
        except Exception as e:
            logger.error(f"Spider 중지 실패 {spider_name}: {e}")
            return {"success": False, "error": str(e)}

