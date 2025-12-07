"""
MapReduce 모듈
MapReduce 작업을 관리하는 모듈
"""

import subprocess
import os
from typing import Dict, Any, Optional
from pathlib import Path

from gui.core.module_manager import ModuleInterface
from shared.logger import setup_logger

logger = setup_logger(__name__)


class MapReduceModule(ModuleInterface):
    """MapReduce 모듈 클래스"""

    def __init__(self, name: str = "MapReduceModule"):
        super().__init__(name)
        self.jobs = {}
        self.processes = {}  # PID -> subprocess.Popen 매핑
        # 프로젝트 루트 기준으로 경로 해결
        # gui/modules/mapreduce_module.py -> cointicker/
        project_root = Path(__file__).parent.parent.parent
        self.mapreduce_path = project_root / "worker-nodes" / "mapreduce"
        self.scripts_path = project_root / "scripts"

    def initialize(self, config: dict) -> bool:
        """모듈 초기화"""
        try:
            self.config = config
            # 프로젝트 루트 기준으로 경로 해결
            project_root = Path(__file__).parent.parent.parent
            mapreduce_relative = config.get("mapreduce_path", "worker-nodes/mapreduce")
            self.mapreduce_path = (project_root / mapreduce_relative).resolve()
            logger.info(
                f"MapReduce 모듈 초기화 완료: mapreduce_path = {self.mapreduce_path}"
            )
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
            return self.run_cleaner(params.get("host"), params.get("mode"))
        elif command == "run_mapreduce":
            return self.run_mapreduce(
                params.get("input_path"), params.get("output_path"), params.get("host")
            )

        elif command == "get_job_status":
            job_id = params.get("job_id")
            if job_id:
                return {"success": True, "job": self.jobs.get(job_id, {})}
            else:
                return {"success": True, "jobs": self.jobs}

        else:
            return {"success": False, "error": f"알 수 없는 명령어: {command}"}

    def _find_hadoop_home(self) -> Optional[str]:
        """
        HADOOP_HOME 경로 자동 감지

        Returns:
            HADOOP_HOME 경로 또는 None
        """
        # 환경 변수 확인
        hadoop_home = os.environ.get("HADOOP_HOME")
        if hadoop_home and Path(hadoop_home).exists():
            return hadoop_home

        # 프로젝트 루트 찾기
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent  # cointicker/

        # 검색할 경로 목록 (HDFSManager와 동일한 로직)
        search_paths = [
            project_root.parent.parent / "hadoop_project" / "hadoop-3.4.1",  # bigdata/hadoop_project/hadoop-3.4.1
            project_root.parent / "hadoop_project" / "hadoop-3.4.1",  # cointicker/hadoop_project/hadoop-3.4.1
            Path("/opt/hadoop"),
            Path("/usr/local/hadoop"),
            Path("/home/bigdata/hadoop-3.4.1"),
            Path("/usr/lib/hadoop"),
            Path("/opt/homebrew/opt/hadoop"),
            Path("/usr/local/opt/hadoop"),
        ]

        for path in search_paths:
            if path.exists() and (path / "sbin" / "start-dfs.sh").exists():
                logger.info(f"✅ HADOOP_HOME 자동 감지: {path}")
                return str(path)

        return None

    def _is_cluster_mode(self) -> bool:
        """
        클러스터 모드인지 확인

        Returns:
            클러스터 모드이면 True, 단일 노드 모드이면 False
        """
        try:
            from gui.core.config_manager import ConfigManager

            config_manager = ConfigManager()
            cluster_config = config_manager.load_config("cluster")

            if cluster_config and cluster_config.get("cluster"):
                # HADOOP_HOME 자동 감지
                hadoop_home = self._find_hadoop_home()
                if hadoop_home and os.path.exists(f"{hadoop_home}/bin/hadoop"):
                    return True
            return False
        except Exception as e:
            logger.debug(f"클러스터 모드 확인 실패: {e}")
            return False

    def run_cleaner(self, host: str = None, mode: str = None) -> dict:
        """
        MapReduce 정제 작업 실행 (로컬 모드)

        Args:
            host: 호스트 주소 (None이면 로컬)
            mode: 실행 모드 ("local" 또는 "cluster", None이면 자동 감지)

        Returns:
            실행 결과
        """
        try:
            # 모드가 지정되지 않았으면 자동 감지
            if mode is None:
                mode = "cluster" if self._is_cluster_mode() else "local"

            if mode == "cluster":
                # 클러스터 모드: run_mapreduce.sh 사용
                return self.run_mapreduce(None, None, host)
            else:
                # 로컬 모드: run_cleaner.sh 사용
                script_path = self.mapreduce_path / "run_cleaner.sh"

                if not script_path.exists():
                    return {
                        "success": False,
                        "error": f"스크립트를 찾을 수 없습니다: {script_path}",
                    }

                if host:
                    cmd = f"ssh {host} 'bash ~/cointicker/{script_path}'"
                else:
                    cmd = f"bash {script_path}"

                process = subprocess.Popen(
                    cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )

                job_id = f"cleaner_{process.pid}"
                self.processes[process.pid] = process
                self.jobs[job_id] = {
                    "id": job_id,
                    "type": "cleaner",
                    "mode": "local",
                    "status": "running",
                    "pid": process.pid,
                    "process": process,
                    "start_time": str(
                        subprocess.run(
                            "date", shell=True, capture_output=True, text=True
                        ).stdout.strip()
                    ),
                }

                logger.info(f"MapReduce 작업 시작 (로컬 모드): {job_id}")
                return {
                    "success": True,
                    "job_id": job_id,
                    "pid": process.pid,
                    "mode": "local",
                }
        except Exception as e:
            logger.error(f"MapReduce 작업 실행 실패: {e}")
            return {"success": False, "error": str(e)}

    def run_mapreduce(
        self, input_path: str = None, output_path: str = None, host: str = None
    ) -> dict:
        """
        MapReduce 작업 실행 (클러스터 모드 - Hadoop Streaming)

        Args:
            input_path: HDFS 입력 경로 (None이면 기본값 사용)
            output_path: HDFS 출력 경로 (None이면 기본값 사용)
            host: 호스트 주소 (None이면 로컬)

        Returns:
            실행 결과
        """
        try:
            script_path = self.scripts_path / "run_mapreduce.sh"

            if not script_path.exists():
                return {
                    "success": False,
                    "error": f"스크립트를 찾을 수 없습니다: {script_path}",
                }

            # 명령어 구성
            cmd_parts = [str(script_path)]
            if input_path:
                cmd_parts.append(input_path)
            if output_path:
                cmd_parts.append(output_path)

            cmd = " ".join(cmd_parts)

            if host:
                cmd = f"ssh {host} 'bash ~/cointicker/{cmd}'"
            else:
                cmd = f"bash {cmd}"

            process = subprocess.Popen(
                cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )

            job_id = f"mapreduce_{process.pid}"
            self.processes[process.pid] = process
            self.jobs[job_id] = {
                "id": job_id,
                "type": "mapreduce",
                "mode": "cluster",
                "status": "running",
                "pid": process.pid,
                "process": process,
                "input_path": input_path or "/user/cointicker/raw",
                "output_path": output_path or "/user/cointicker/cleaned",
                "start_time": str(
                    subprocess.run(
                        "date", shell=True, capture_output=True, text=True
                    ).stdout.strip()
                ),
            }

            logger.info(f"MapReduce 작업 시작 (클러스터 모드): {job_id}")
            return {
                "success": True,
                "job_id": job_id,
                "pid": process.pid,
                "mode": "cluster",
            }
        except Exception as e:
            logger.error(f"MapReduce 작업 실행 실패: {e}")
            return {"success": False, "error": str(e)}

    def is_running(self) -> bool:
        """
        실행 중인 MapReduce 작업이 있는지 확인

        Returns:
            실행 중이면 True
        """
        self._update_job_status()
        for job in self.jobs.values():
            if job.get("status") == "running":
                return True
        return False

    def get_running_jobs(self) -> list:
        """
        실행 중인 작업 목록 조회

        Returns:
            실행 중인 작업 목록
        """
        self._update_job_status()
        return [job for job in self.jobs.values() if job.get("status") == "running"]

    def _update_job_status(self):
        """모든 작업의 상태 업데이트"""
        for job_id, job in list(self.jobs.items()):
            process = job.get("process")
            if process and hasattr(process, "poll"):
                returncode = process.poll()
                if returncode is not None:
                    # 프로세스 종료됨
                    job["status"] = "completed" if returncode == 0 else "failed"
                    job["returncode"] = returncode
                    # processes dict에서 제거
                    if job["pid"] in self.processes:
                        del self.processes[job["pid"]]

    def get_status(self) -> dict:
        """
        모듈 상태 조회

        Returns:
            상태 정보
        """
        self._update_job_status()
        running_jobs = self.get_running_jobs()
        return {
            "status": self.status,
            "running_jobs": len(running_jobs),
            "total_jobs": len(self.jobs),
            "jobs": list(self.jobs.values())
        }
