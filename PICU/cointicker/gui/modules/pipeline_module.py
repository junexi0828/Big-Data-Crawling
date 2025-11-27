"""
파이프라인 모듈
전체 데이터 파이프라인을 관리하는 모듈
"""

import subprocess
from typing import Dict, Any
from pathlib import Path

from gui.core.module_manager import ModuleInterface
from shared.logger import setup_logger

logger = setup_logger(__name__)


class PipelineModule(ModuleInterface):
    """파이프라인 모듈 클래스"""

    def __init__(self, name: str = "PipelineModule"):
        super().__init__(name)
        # 프로젝트 루트 기준으로 경로 해결
        # gui/modules/pipeline_module.py -> cointicker/master-node/orchestrator.py
        project_root = Path(__file__).parent.parent.parent
        self.orchestrator_path = project_root / "master-node" / "orchestrator.py"
        self.scheduler_path = project_root / "master-node" / "scheduler.py"
        self.processes = {}

    def initialize(self, config: dict) -> bool:
        """모듈 초기화"""
        try:
            self.config = config
            # 프로젝트 루트 기준으로 경로 해결
            project_root = Path(__file__).parent.parent.parent
            orchestrator_relative = config.get("orchestrator_path", "master-node/orchestrator.py")
            scheduler_relative = config.get("scheduler_path", "master-node/scheduler.py")
            self.orchestrator_path = (project_root / orchestrator_relative).resolve()
            self.scheduler_path = (project_root / scheduler_relative).resolve()
            logger.info(f"파이프라인 모듈 초기화 완료: orchestrator = {self.orchestrator_path}, scheduler = {self.scheduler_path}")
            return True
        except Exception as e:
            logger.error(f"파이프라인 모듈 초기화 실패: {e}")
            return False

    def start(self) -> bool:
        """모듈 시작"""
        self.status = "running"
        logger.info("파이프라인 모듈 시작")
        return True

    def stop(self) -> bool:
        """모듈 중지"""
        # 모든 프로세스 종료
        for process in self.processes.values():
            try:
                process.terminate()
            except:
                pass
        self.processes.clear()

        self.status = "stopped"
        logger.info("파이프라인 모듈 중지")
        return True

    def execute(self, command: str, params: dict = None) -> dict:
        """명령어 실행"""
        params = params or {}

        if command == "start_orchestrator":
            return self.start_orchestrator(params.get("host"))

        elif command == "stop_orchestrator":
            return self.stop_orchestrator()

        elif command == "start_scheduler":
            return self.start_scheduler(params.get("host"))

        elif command == "stop_scheduler":
            return self.stop_scheduler()

        elif command == "run_full_pipeline":
            return self.run_full_pipeline(params.get("host"))

        else:
            return {"success": False, "error": f"알 수 없는 명령어: {command}"}

    def start_orchestrator(self, host: str = None) -> dict:
        """오케스트레이터 시작"""
        try:
            if host:
                cmd = f"ssh {host} 'cd ~/cointicker && python master-node/orchestrator.py'"
            else:
                # 프로젝트 루트를 작업 디렉토리로 설정
                project_root = Path(__file__).parent.parent.parent
                orchestrator_abs = str(self.orchestrator_path.resolve())
                cmd = f"python {orchestrator_abs}"

            process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(project_root.resolve()),  # 프로젝트 루트를 작업 디렉토리로
            )

            self.processes["orchestrator"] = process
            logger.info("오케스트레이터 시작")
            return {"success": True, "pid": process.pid}
        except Exception as e:
            logger.error(f"오케스트레이터 시작 실패: {e}")
            return {"success": False, "error": str(e)}

    def stop_orchestrator(self) -> dict:
        """오케스트레이터 중지"""
        try:
            if "orchestrator" in self.processes:
                self.processes["orchestrator"].terminate()
                del self.processes["orchestrator"]

            subprocess.run("pkill -f 'orchestrator.py'", shell=True, timeout=5)
            logger.info("오케스트레이터 중지")
            return {"success": True}
        except Exception as e:
            logger.error(f"오케스트레이터 중지 실패: {e}")
            return {"success": False, "error": str(e)}

    def start_scheduler(self, host: str = None) -> dict:
        """스케줄러 시작"""
        try:
            if host:
                cmd = f"ssh {host} 'cd ~/cointicker && python master-node/scheduler.py'"
            else:
                # 프로젝트 루트를 작업 디렉토리로 설정
                project_root = Path(__file__).parent.parent.parent
                scheduler_abs = str(self.scheduler_path.resolve())
                cmd = f"python {scheduler_abs}"

            process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(project_root.resolve()),  # 프로젝트 루트를 작업 디렉토리로
            )

            self.processes["scheduler"] = process
            logger.info("스케줄러 시작")
            return {"success": True, "pid": process.pid}
        except Exception as e:
            logger.error(f"스케줄러 시작 실패: {e}")
            return {"success": False, "error": str(e)}

    def stop_scheduler(self) -> dict:
        """스케줄러 중지"""
        try:
            if "scheduler" in self.processes:
                self.processes["scheduler"].terminate()
                del self.processes["scheduler"]

            subprocess.run("pkill -f 'scheduler.py'", shell=True, timeout=5)
            logger.info("스케줄러 중지")
            return {"success": True}
        except Exception as e:
            logger.error(f"스케줄러 중지 실패: {e}")
            return {"success": False, "error": str(e)}

    def run_full_pipeline(self, host: str = None) -> dict:
        """전체 파이프라인 실행"""
        try:
            script_path = Path("scripts/run_pipeline.py")
            if host:
                cmd = f"ssh {host} 'cd ~/cointicker && python scripts/run_pipeline.py'"
            else:
                cmd = f"python {script_path}"

            process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            logger.info("전체 파이프라인 실행")
            return {"success": True, "pid": process.pid}
        except Exception as e:
            logger.error(f"파이프라인 실행 실패: {e}")
            return {"success": False, "error": str(e)}

