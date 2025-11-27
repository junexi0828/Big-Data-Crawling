"""
MapReduce 모듈
MapReduce 작업을 관리하는 모듈
"""

import subprocess
from typing import Dict, Any
from pathlib import Path

from gui.core.module_manager import ModuleInterface
from shared.logger import setup_logger

logger = setup_logger(__name__)


class MapReduceModule(ModuleInterface):
    """MapReduce 모듈 클래스"""

    def __init__(self, name: str = "MapReduceModule"):
        super().__init__(name)
        self.jobs = {}
        self.mapreduce_path = Path("worker-nodes/mapreduce")

    def initialize(self, config: dict) -> bool:
        """모듈 초기화"""
        try:
            self.config = config
            self.mapreduce_path = Path(config.get("mapreduce_path", "worker-nodes/mapreduce"))
            logger.info("MapReduce 모듈 초기화 완료")
            return True
        except Exception as e:
            logger.error(f"MapReduce 모듈 초기화 실패: {e}")
            return False

    def start(self) -> bool:
        """모듈 시작"""
        self.status = "running"
        logger.info("MapReduce 모듈 시작")
        return True

    def stop(self) -> bool:
        """모듈 중지"""
        self.status = "stopped"
        logger.info("MapReduce 모듈 중지")
        return True

    def execute(self, command: str, params: dict = None) -> dict:
        """명령어 실행"""
        params = params or {}

        if command == "run_cleaner":
            return self.run_cleaner(params.get("host"))

        elif command == "get_job_status":
            job_id = params.get("job_id")
            if job_id:
                return {
                    "success": True,
                    "job": self.jobs.get(job_id, {})
                }
            else:
                return {
                    "success": True,
                    "jobs": self.jobs
                }

        else:
            return {"success": False, "error": f"알 수 없는 명령어: {command}"}

    def run_cleaner(self, host: str = None) -> dict:
        """
        MapReduce 정제 작업 실행

        Args:
            host: 호스트 주소 (None이면 로컬)

        Returns:
            실행 결과
        """
        try:
            script_path = self.mapreduce_path / "run_cleaner.sh"

            if not script_path.exists():
                return {"success": False, "error": f"스크립트를 찾을 수 없습니다: {script_path}"}

            if host:
                cmd = f"ssh {host} 'bash ~/cointicker/{script_path}'"
            else:
                cmd = f"bash {script_path}"

            process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            job_id = f"cleaner_{process.pid}"
            self.jobs[job_id] = {
                "id": job_id,
                "type": "cleaner",
                "status": "running",
                "pid": process.pid,
                "start_time": str(subprocess.run("date", shell=True, capture_output=True, text=True).stdout.strip())
            }

            logger.info(f"MapReduce 작업 시작: {job_id}")
            return {
                "success": True,
                "job_id": job_id,
                "pid": process.pid
            }
        except Exception as e:
            logger.error(f"MapReduce 작업 실행 실패: {e}")
            return {"success": False, "error": str(e)}

