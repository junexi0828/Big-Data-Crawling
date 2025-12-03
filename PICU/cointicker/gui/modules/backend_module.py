"""
Backend 모듈
FastAPI 백엔드를 관리하는 모듈

⚠️ 주의: 삭제 및 수정 금지 ⚠️

이 모듈은 GUI와 백엔드 스크립트와 연동되어 있습니다:
- start() 메서드에서 backend/scripts/run_server.sh를 사용하여 백엔드 시작
- run_server.sh가 포트 파일을 생성하면 GUI가 자동으로 포트를 감지

연동된 컴포넌트:
- backend/scripts/run_server.sh: 백엔드 포트 파일 생성 (config/.backend_port)
- gui/monitors/tier2_monitor.py: get_backend_port_from_file()로 포트 읽기
- gui/app.py: _reinitialize_tier2_monitor()로 포트 동기화
- gui/modules/pipeline_orchestrator.py: 백엔드 프로세스 시작 시 이 모듈 사용

이 모듈의 start() 메서드를 수정하면 포트 동기화가 깨집니다.
특히 uvicorn을 직접 실행하지 말고 반드시 scripts/run_server.sh를 사용해야 합니다.
"""

import subprocess
from typing import Dict, Any
from pathlib import Path

from gui.core.module_manager import ModuleInterface
from gui.monitors import Tier2Monitor, get_default_backend_url
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
            # 포트 파일에서 우선 읽기, 없으면 config에서, 그것도 없으면 기본값
            base_url = config.get("base_url")
            if base_url is None:
                base_url = get_default_backend_url()
            self.tier2_monitor = Tier2Monitor(base_url=base_url)
            logger.info(f"Backend 모듈 초기화 완료 (URL: {base_url})")
            return True
        except Exception as e:
            logger.error(f"Backend 모듈 초기화 실패: {e}")
            return False

    def start(self) -> bool:
        """모듈 시작"""
        try:
            # run_server.sh를 사용하여 포트 파일 생성 및 포트 충돌 처리
            # AUTO_PORT_SWITCH=true로 설정하여 비대화형 모드로 실행
            import os

            env = os.environ.copy()
            env["AUTO_PORT_SWITCH"] = "true"
            project_root = Path(__file__).parent.parent.parent.parent
            backend_dir = project_root / "cointicker" / "backend"
            cmd = "bash scripts/run_server.sh"
            # start_new_session=True로 설정하여 부모 프로세스 종료 시에도 계속 실행
            # stdout/stderr를 None으로 설정하여 출력이 터미널에 표시되도록 함
            self.process = subprocess.Popen(
                cmd,
                shell=True,
                cwd=str(backend_dir),
                stdout=None,  # 터미널에 출력
                stderr=None,  # 터미널에 출력
                env=env,
                start_new_session=True,  # 새 세션으로 시작
            )
            self.status = "running"
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
