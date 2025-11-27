"""
파이프라인 오케스트레이터
전체 프로세스를 통합 관리하는 모듈
"""

import subprocess
import time
import threading
from typing import Dict, List, Optional, Callable
from pathlib import Path
from datetime import datetime
from enum import Enum

from gui.core.module_manager import ModuleInterface
from shared.logger import setup_logger

logger = setup_logger(__name__)


class ProcessStatus(Enum):
    """프로세스 상태"""

    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


class PipelineOrchestrator(ModuleInterface):
    """파이프라인 오케스트레이터 클래스"""

    def __init__(self, name: str = "PipelineOrchestrator"):
        super().__init__(name)

        # 프로세스 의존성 정의
        self.process_dependencies = {
            "spider": [],  # Spider는 독립적으로 실행 가능
            "kafka_consumer": ["kafka_broker"],  # Kafka Consumer는 Kafka 브로커 필요
            "hdfs": [],  # HDFS는 독립적으로 실행 가능
            "backend": [],  # Backend는 독립적으로 실행 가능
            "frontend": ["backend"],  # Frontend는 Backend 필요 (선택적)
        }

        # 프로세스 상태
        self.processes: Dict[str, Dict] = {
            "spider": {
                "status": ProcessStatus.STOPPED,
                "process": None,
                "module": None,
                "start_time": None,
            },
            "kafka_consumer": {
                "status": ProcessStatus.STOPPED,
                "process": None,
                "module": None,
                "start_time": None,
            },
            "hdfs": {
                "status": ProcessStatus.STOPPED,
                "process": None,
                "module": None,
                "start_time": None,
            },
            "backend": {
                "status": ProcessStatus.STOPPED,
                "process": None,
                "module": None,
                "start_time": None,
            },
            "frontend": {
                "status": ProcessStatus.STOPPED,
                "process": None,
                "module": None,
                "start_time": None,
            },
        }

        # 실행 순서 (의존성 순서)
        self.start_order = ["backend", "kafka_consumer", "spider", "hdfs", "frontend"]
        self.stop_order = [
            "frontend",
            "spider",
            "kafka_consumer",
            "hdfs",
            "backend",
        ]  # 역순

    def initialize(self, config: dict) -> bool:
        """모듈 초기화"""
        try:
            self.config = config
            logger.info("파이프라인 오케스트레이터 초기화 완료")
            return True
        except Exception as e:
            logger.error(f"파이프라인 오케스트레이터 초기화 실패: {e}")
            return False

    def set_module(self, process_name: str, module: ModuleInterface):
        """프로세스에 모듈 연결"""
        if process_name in self.processes:
            self.processes[process_name]["module"] = module
            logger.info(
                f"모듈 연결: {process_name} -> {module.name if module else None}"
            )

    def check_dependencies(self, process_name: str):
        """
        프로세스 의존성 확인

        Returns:
            (의존성 만족 여부, 실패한 의존성 리스트)
        """
        if process_name not in self.process_dependencies:
            return True, []

        dependencies = self.process_dependencies[process_name]
        failed = []

        for dep in dependencies:
            if dep == "kafka_broker":
                # Kafka 브로커 확인 (간단한 체크)
                try:
                    import socket

                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    result = sock.connect_ex(("localhost", 9092))
                    sock.close()
                    if result != 0:
                        failed.append(dep)
                except:
                    failed.append(dep)
            elif dep in self.processes:
                dep_status = self.processes[dep]["status"]
                if dep_status != ProcessStatus.RUNNING:
                    failed.append(dep)

        return len(failed) == 0, failed

    def start_process(self, process_name: str, wait: bool = False) -> Dict:
        """
        개별 프로세스 시작

        Args:
            process_name: 프로세스 이름
            wait: 의존성 확인 후 대기 여부

        Returns:
            실행 결과
        """
        if process_name not in self.processes:
            return {"success": False, "error": f"알 수 없는 프로세스: {process_name}"}

        process_info = self.processes[process_name]

        # 이미 실행 중이면 스킵
        if process_info["status"] == ProcessStatus.RUNNING:
            return {"success": True, "message": f"{process_name}는 이미 실행 중입니다"}

        # 의존성 확인
        deps_ok, failed_deps = self.check_dependencies(process_name)
        if not deps_ok:
            if wait:
                # 의존성 프로세스 시작 대기
                logger.info(f"{process_name}의 의존성 시작 대기: {failed_deps}")
                for dep in failed_deps:
                    if dep in self.processes:
                        self.start_process(dep, wait=True)
                # 재확인
                deps_ok, failed_deps = self.check_dependencies(process_name)
                if not deps_ok:
                    return {
                        "success": False,
                        "error": f"의존성 확인 실패: {failed_deps}",
                    }
            else:
                return {
                    "success": False,
                    "error": f"의존성 확인 실패: {failed_deps}",
                }

        # 프로세스 시작
        process_info["status"] = ProcessStatus.STARTING
        process_info["start_time"] = datetime.now().isoformat()

        try:
            module = process_info["module"]
            if module:
                # 모듈을 통한 시작
                if hasattr(module, "start"):
                    success = module.start()
                    if success:
                        process_info["status"] = ProcessStatus.RUNNING
                        logger.info(f"프로세스 시작 성공: {process_name}")
                        return {"success": True, "process_name": process_name}
                    else:
                        process_info["status"] = ProcessStatus.ERROR
                        return {"success": False, "error": f"{process_name} 시작 실패"}
                else:
                    # execute 명령어 사용
                    result = module.execute("start", {})
                    if result.get("success"):
                        process_info["status"] = ProcessStatus.RUNNING
                        return {"success": True, "process_name": process_name}
                    else:
                        process_info["status"] = ProcessStatus.ERROR
                        return result
            else:
                # 직접 실행 (모듈이 없는 경우)
                return self._start_process_direct(process_name)

        except Exception as e:
            process_info["status"] = ProcessStatus.ERROR
            logger.error(f"프로세스 시작 오류 {process_name}: {e}")
            return {"success": False, "error": str(e)}

    def _start_process_direct(self, process_name: str) -> Dict:
        """프로세스를 직접 실행 (모듈이 없는 경우)"""
        project_root = Path(__file__).parent.parent.parent.parent

        try:
            if process_name == "backend":
                cmd = f"cd {project_root}/cointicker/backend && uvicorn app:app --host 0.0.0.0 --port 5000"
                process = subprocess.Popen(
                    cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
            elif process_name == "frontend":
                cmd = f"cd {project_root}/cointicker/frontend && npm run dev"
                process = subprocess.Popen(
                    cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
            elif process_name == "kafka_consumer":
                cmd = f"python {project_root}/cointicker/worker-nodes/kafka_consumer.py"
                process = subprocess.Popen(
                    cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
            else:
                return {"success": False, "error": f"직접 실행 불가: {process_name}"}

            self.processes[process_name]["process"] = process
            self.processes[process_name]["status"] = ProcessStatus.RUNNING
            return {"success": True, "process_name": process_name, "pid": process.pid}

        except Exception as e:
            self.processes[process_name]["status"] = ProcessStatus.ERROR
            return {"success": False, "error": str(e)}

    def stop_process(self, process_name: str) -> Dict:
        """개별 프로세스 중지"""
        if process_name not in self.processes:
            return {"success": False, "error": f"알 수 없는 프로세스: {process_name}"}

        process_info = self.processes[process_name]

        if process_info["status"] == ProcessStatus.STOPPED:
            return {"success": True, "message": f"{process_name}는 이미 중지되었습니다"}

        process_info["status"] = ProcessStatus.STOPPING

        try:
            module = process_info["module"]
            if module:
                if hasattr(module, "stop"):
                    success = module.stop()
                    if success:
                        process_info["status"] = ProcessStatus.STOPPED
                        return {"success": True, "process_name": process_name}
                    else:
                        return {"success": False, "error": f"{process_name} 중지 실패"}
                else:
                    result = module.execute("stop", {})
                    if result.get("success"):
                        process_info["status"] = ProcessStatus.STOPPED
                        return {"success": True, "process_name": process_name}
                    else:
                        return result
            else:
                # 직접 중지
                process = process_info.get("process")
                if process:
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                    process_info["process"] = None

            process_info["status"] = ProcessStatus.STOPPED
            return {"success": True, "process_name": process_name}

        except Exception as e:
            process_info["status"] = ProcessStatus.ERROR
            logger.error(f"프로세스 중지 오류 {process_name}: {e}")
            return {"success": False, "error": str(e)}

    def start_all(self, processes: Optional[List[str]] = None) -> Dict:
        """
        모든 프로세스 시작 (의존성 순서대로)

        Args:
            processes: 시작할 프로세스 리스트 (None이면 모든 프로세스)

        Returns:
            실행 결과
        """
        if processes is None:
            processes = self.start_order

        results = {}
        for process_name in processes:
            if process_name not in self.processes:
                continue

            logger.info(f"프로세스 시작: {process_name}")
            result = self.start_process(process_name, wait=True)
            results[process_name] = result

            if not result.get("success"):
                logger.warning(
                    f"프로세스 시작 실패: {process_name} - {result.get('error')}"
                )
                # 의존성 실패는 계속 진행, 다른 오류는 중단
                if "의존성" not in result.get("error", ""):
                    break

            # 프로세스 간 간격
            time.sleep(1)

        success_count = sum(1 for r in results.values() if r.get("success"))
        return {
            "success": success_count == len(results),
            "results": results,
            "started": success_count,
            "total": len(results),
        }

    def stop_all(self, processes: Optional[List[str]] = None) -> Dict:
        """
        모든 프로세스 중지 (역순으로)

        Args:
            processes: 중지할 프로세스 리스트 (None이면 모든 프로세스)

        Returns:
            중지 결과
        """
        if processes is None:
            processes = self.stop_order

        results = {}
        for process_name in processes:
            if process_name not in self.processes:
                continue

            logger.info(f"프로세스 중지: {process_name}")
            result = self.stop_process(process_name)
            results[process_name] = result

            # 프로세스 간 간격
            time.sleep(0.5)

        success_count = sum(1 for r in results.values() if r.get("success"))
        return {
            "success": success_count == len(results),
            "results": results,
            "stopped": success_count,
            "total": len(results),
        }

    def get_status(self) -> Dict:
        """전체 프로세스 상태 조회"""
        status = {}
        for name, info in self.processes.items():
            status[name] = {
                "status": info["status"].value,
                "start_time": info["start_time"],
                "running": info["status"] == ProcessStatus.RUNNING,
            }
        return status

    def execute(self, command: str, params: dict = None) -> dict:
        """명령어 실행"""
        params = params or {}

        if command == "start_all":
            processes = params.get("processes")
            return self.start_all(processes)

        elif command == "stop_all":
            processes = params.get("processes")
            return self.stop_all(processes)

        elif command == "start_process":
            process_name = params.get("process_name")
            wait = params.get("wait", False)
            if not process_name:
                return {"success": False, "error": "process_name이 필요합니다"}
            return self.start_process(process_name, wait=wait)

        elif command == "stop_process":
            process_name = params.get("process_name")
            if not process_name:
                return {"success": False, "error": "process_name이 필요합니다"}
            return self.stop_process(process_name)

        elif command == "get_status":
            return {"success": True, "status": self.get_status()}

        elif command == "check_dependencies":
            process_name = params.get("process_name")
            if not process_name:
                return {"success": False, "error": "process_name이 필요합니다"}
            deps_ok, failed = self.check_dependencies(process_name)
            return {"success": True, "dependencies_ok": deps_ok, "failed": failed}

        else:
            return {"success": False, "error": f"알 수 없는 명령어: {command}"}
