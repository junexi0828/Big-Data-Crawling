"""
Frontend 모듈
React 프론트엔드를 관리하는 모듈

⚠️ 주의: 삭제 및 수정 금지 ⚠️

이 모듈은 GUI와 프론트엔드 스크립트와 연동되어 있습니다:
- start() 메서드에서 frontend/scripts/run_dev.sh를 사용하여 프론트엔드 시작
- run_dev.sh가 백엔드 포트 파일을 읽어 VITE_API_BASE_URL 설정

연동된 컴포넌트:
- frontend/scripts/run_dev.sh: 백엔드 포트 파일 읽기 및 VITE_API_BASE_URL 설정
- gui/modules/pipeline_orchestrator.py: 프론트엔드 프로세스 시작 시 이 모듈 사용
- vite.config.js: VITE_API_BASE_URL 환경 변수 사용

이 모듈의 start() 메서드를 수정하면 포트 동기화가 깨집니다.
특히 npm run dev를 직접 실행하지 말고 반드시 scripts/run_dev.sh를 사용해야 합니다.
"""

import subprocess
from typing import Dict, Any, Optional
from pathlib import Path

from gui.core.module_manager import ModuleInterface
from shared.logger import setup_logger

logger = setup_logger(__name__)


class FrontendModule(ModuleInterface):
    """Frontend 모듈 클래스"""

    def __init__(self, name: str = "FrontendModule"):
        super().__init__(name)
        self.process = None
        self.frontend_path = Path("frontend")

    def initialize(self, config: dict) -> bool:
        """모듈 초기화"""
        try:
            self.config = config
            self.frontend_path = Path(config.get("frontend_path", "frontend"))
            logger.info("Frontend 모듈 초기화 완료")
            return True
        except Exception as e:
            logger.error(f"Frontend 모듈 초기화 실패: {e}")
            return False

    def start(self) -> bool:
        """모듈 시작"""
        try:
            # run_dev.sh를 사용하여 백엔드 포트 파일 읽기 및 포트 충돌 처리
            project_root = Path(__file__).parent.parent.parent.parent
            frontend_dir = project_root / "cointicker" / "frontend"
            cmd = "bash scripts/run_dev.sh"
            # start_new_session=True로 설정하여 부모 프로세스 종료 시에도 계속 실행
            # stdout/stderr를 None으로 설정하여 출력이 터미널에 표시되도록 함
            self.process = subprocess.Popen(
                cmd,
                shell=True,
                cwd=str(frontend_dir),
                stdout=None,  # 터미널에 출력
                stderr=None,  # 터미널에 출력
                start_new_session=True,  # 새 세션으로 시작
            )
            self.status = "running"
            logger.info("Frontend 모듈 시작 완료")
            return True
        except Exception as e:
            logger.error(f"Frontend 모듈 시작 실패: {e}")
            return False

    def stop(self) -> bool:
        """모듈 중지"""
        try:
            if self.process:
                self.process.terminate()
                self.process = None

            # vite 프로세스 종료
            subprocess.run("pkill -f 'vite'", shell=True, timeout=5)
            subprocess.run("pkill -f 'npm run dev'", shell=True, timeout=5)

            self.status = "stopped"
            logger.info("Frontend 모듈 중지")
            return True
        except Exception as e:
            logger.error(f"Frontend 모듈 중지 실패: {e}")
            return False

    def execute(self, command: str, params: Optional[Dict[str, Any]] = None) -> dict:
        """명령어 실행"""
        params = params or {}

        if command == "check_status":
            if self.process:
                # 프로세스가 실행 중인지 확인
                poll_result = self.process.poll()
                if poll_result is None:
                    return {
                        "success": True,
                        "running": True,
                        "pid": self.process.pid,
                    }
                else:
                    return {
                        "success": True,
                        "running": False,
                        "exit_code": poll_result,
                    }
            else:
                return {"success": True, "running": False}

        elif command == "get_url":
            # 프론트엔드 URL 반환 (기본값: http://localhost:3000)
            return {
                "success": True,
                "url": "http://localhost:3000",
                "message": "프론트엔드 URL (포트는 run_dev.sh에서 결정됨)",
            }

        else:
            return {"success": False, "error": f"알 수 없는 명령어: {command}"}
