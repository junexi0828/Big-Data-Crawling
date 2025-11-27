"""
Backend 모듈
FastAPI 백엔드를 관리하는 모듈
"""

import subprocess
from typing import Dict, Any
from pathlib import Path

from gui.core.module_manager import ModuleInterface
from gui.tier2_monitor import Tier2Monitor
from shared.logger import setup_logger

logger = setup_logger(__name__)


class BackendModule(ModuleInterface):
    """Backend 모듈 클래스"""

    def __init__(self, name: str = "BackendModule"):
        super().__init__(name)
        self.tier2_monitor = None
        self.process = None
        self.backend_path = Path("backend")

    def initialize(self, config: dict) -> bool:
        """모듈 초기화"""
        try:
            self.config = config
            self.backend_path = Path(config.get("backend_path", "backend"))
            base_url = config.get("base_url", "http://localhost:5000")
            self.tier2_monitor = Tier2Monitor(base_url=base_url)
            logger.info("Backend 모듈 초기화 완료")
            return True
        except Exception as e:
            logger.error(f"Backend 모듈 초기화 실패: {e}")
            return False

    def start(self) -> bool:
        """모듈 시작"""
        try:
            # FastAPI 서버 시작
            cmd = f"cd {self.backend_path} && uvicorn app:app --host 0.0.0.0 --port 5000"
            self.process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            self.status = "running"
            logger.info("Backend 모듈 시작")
            return True
        except Exception as e:
            logger.error(f"Backend 모듈 시작 실패: {e}")
            return False

    def stop(self) -> bool:
        """모듈 중지"""
        try:
            if self.process:
                self.process.terminate()
                self.process = None

            # uvicorn 프로세스 종료
            subprocess.run("pkill -f 'uvicorn app:app'", shell=True, timeout=5)

            self.status = "stopped"
            logger.info("Backend 모듈 중지")
            return True
        except Exception as e:
            logger.error(f"Backend 모듈 중지 실패: {e}")
            return False

    def execute(self, command: str, params: dict = None) -> dict:
        """명령어 실행"""
        params = params or {}

        if not self.tier2_monitor:
            return {"success": False, "error": "Tier2 모니터가 초기화되지 않았습니다"}

        if command == "check_health":
            health = self.tier2_monitor.check_health()
            return health

        elif command == "get_dashboard_summary":
            summary = self.tier2_monitor.get_dashboard_summary()
            return summary

        elif command == "get_sentiment_timeline":
            hours = params.get("hours", 24)
            timeline = self.tier2_monitor.get_sentiment_timeline(hours=hours)
            return timeline

        elif command == "get_latest_news":
            limit = params.get("limit", 50)
            news = self.tier2_monitor.get_latest_news(limit=limit)
            return news

        elif command == "get_recent_insights":
            limit = params.get("limit", 20)
            insights = self.tier2_monitor.get_recent_insights(limit=limit)
            return insights

        elif command == "generate_insights":
            result = self.tier2_monitor.generate_insights()
            return result

        else:
            return {"success": False, "error": f"알 수 없는 명령어: {command}"}

