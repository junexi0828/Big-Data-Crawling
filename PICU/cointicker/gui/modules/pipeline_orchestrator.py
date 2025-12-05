"""
파이프라인 오케스트레이터
전체 프로세스를 통합 관리하는 모듈

⚠️ 주의: 삭제 및 수정 금지 ⚠️

이 모듈은 GUI와 백엔드/프론트엔드 스크립트와 연동되어 있습니다:
- _start_process_direct()에서 백엔드 시작 시 backend/scripts/run_server.sh 사용
- _start_process_direct()에서 프론트엔드 시작 시 frontend/scripts/run_dev.sh 사용
- 이 스크립트들이 포트 파일을 생성/읽어 GUI와 포트 동기화

연동된 컴포넌트:
- backend/scripts/run_server.sh: 백엔드 포트 파일 생성 (config/.backend_port)
- frontend/scripts/run_dev.sh: 백엔드 포트 파일 읽기 및 VITE_API_BASE_URL 설정
- gui/monitors/tier2_monitor.py: 포트 파일 읽어 Tier2 모니터 초기화
- gui/app.py: _auto_start_essential_services()로 백엔드/프론트엔드 자동 시작

이 모듈의 _start_process_direct() 메서드를 수정하면 포트 동기화가 깨집니다.
"""

import subprocess
import time
import threading
import os
from typing import Dict, List, Optional, Callable
from pathlib import Path
from datetime import datetime
from enum import Enum

from gui.core.module_manager import ModuleInterface
from gui.modules.managers import HDFSManager, KafkaManager, SSHManager
from gui.core.timing_config import TimingConfig
from gui.core.retry_utils import execute_with_retry
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

    def __init__(
        self,
        name: str = "PipelineOrchestrator",
        user_confirm_callback: Optional[Callable[[str, str], bool]] = None,
        user_password_callback: Optional[Callable[[str, str], Optional[str]]] = None,
    ):
        super().__init__(name)

        # 사용자 확인 콜백 함수 (GUI에서 설정)
        # 시그니처: callback(title: str, message: str) -> bool
        self.user_confirm_callback = user_confirm_callback

        # 사용자 비밀번호 입력 콜백 함수 (GUI에서 설정)
        # 시그니처: callback(title: str, message: str) -> Optional[str]
        # 보안: 비밀번호는 메모리에만 저장되고 사용 후 즉시 삭제됨
        self.user_password_callback = user_password_callback

        # 매니저 초기화
        self.hdfs_manager = HDFSManager(
            user_confirm_callback=user_confirm_callback,
            user_password_callback=user_password_callback,
        )
        self.kafka_manager = KafkaManager()
        self.ssh_manager = SSHManager()

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
                # Kafka 브로커 확인 및 자동 시작
                try:
                    import socket

                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    result = sock.connect_ex(("localhost", 9092))
                    sock.close()
                    if result != 0:
                        # Kafka 브로커가 없으면 자동으로 시작 시도
                        logger.info(
                            "Kafka 브로커가 실행 중이 아닙니다. 자동으로 시작합니다..."
                        )
                        if self.kafka_manager.start_broker():
                            logger.info("✅ Kafka 브로커 자동 시작 완료")
                        else:
                            logger.warning(
                                "⚠️ Kafka 브로커 자동 시작 실패 (수동으로 시작해야 할 수 있습니다)"
                            )
                            failed.append(dep)
                except Exception as e:
                    logger.error(f"Kafka 브로커 확인 중 오류: {e}")
                    failed.append(dep)
            elif dep in self.processes:
                dep_status = self.processes[dep]["status"]
                if dep_status != ProcessStatus.RUNNING:
                    failed.append(dep)

        return len(failed) == 0, failed

    def _normalize_process_name(self, process_name: str) -> str:
        """
        프로세스 이름 정규화 (설정 파일 이름 -> 실제 프로세스 이름)

        Args:
            process_name: 설정 파일의 프로세스 이름

        Returns:
            실제 프로세스 이름
        """
        # 프로세스 이름 매핑
        name_mapping = {
            "kafka": "kafka_consumer",  # 설정 파일의 "kafka" -> 실제 "kafka_consumer"
            "mapreduce": None,  # MapReduce는 프로세스가 아닌 작업이므로 None 반환
        }

        if process_name in name_mapping:
            mapped_name = name_mapping[process_name]
            if mapped_name is None:
                logger.debug(
                    f"프로세스 '{process_name}'는 매핑되지 않습니다 (작업 타입)"
                )
                return None
            logger.debug(f"프로세스 이름 매핑: {process_name} -> {mapped_name}")
            return mapped_name

        return process_name

    def start_process(self, process_name: str, wait: bool = False) -> Dict:
        """
        개별 프로세스 시작

        Args:
            process_name: 프로세스 이름 (정규화됨)
            wait: 의존성 확인 후 대기 여부

        Returns:
            실행 결과
        """
        # 프로세스 이름 정규화
        normalized_name = self._normalize_process_name(process_name)
        if normalized_name is None:
            # MapReduce는 프로세스가 아닌 작업이므로 성공으로 처리
            if process_name == "mapreduce":
                return {
                    "success": True,
                    "message": "MapReduce는 작업 타입입니다. GUI에서 MapReduce 작업을 실행하세요.",
                }
            return {"success": False, "error": f"알 수 없는 프로세스: {process_name}"}

        process_name = normalized_name

        if process_name not in self.processes:
            return {"success": False, "error": f"알 수 없는 프로세스: {process_name}"}

        process_info = self.processes[process_name]

        # 이미 실행 중이면 스킵
        if process_info["status"] == ProcessStatus.RUNNING:
            return {"success": True, "message": f"{process_name}는 이미 실행 중입니다"}

        # systemd 서비스와 충돌 확인 (orchestrator 또는 tier2_scheduler인 경우)
        if process_name in ["orchestrator", "tier2_scheduler"]:
            try:
                from gui.modules.systemd_manager import SystemdManager

                service_name = (
                    "tier1_orchestrator"
                    if process_name == "orchestrator"
                    else "tier2_scheduler"
                )
                conflict_msg = SystemdManager.check_conflict_with_gui(service_name)

                if conflict_msg:
                    logger.warning(f"systemd 서비스 충돌 감지: {conflict_msg}")
                    return {"success": False, "error": conflict_msg}
            except Exception as e:
                logger.debug(f"충돌 확인 중 오류 (무시하고 계속 진행): {e}")
                # 충돌 확인 실패 시에도 프로세스 시작은 계속 진행

        # 의존성 확인 (kafka_broker는 선택적 의존성으로 처리)
        deps_ok, failed_deps = self.check_dependencies(process_name)
        # kafka_broker는 선택적 의존성 (없어도 시작 가능)
        if not deps_ok:
            # kafka_broker만 실패한 경우 경고만 출력하고 계속 진행
            if process_name == "kafka_consumer" and failed_deps == ["kafka_broker"]:
                logger.warning(
                    f"{process_name}의 Kafka 브로커가 실행 중이 아닙니다. 브로커 없이 시작합니다."
                )
            elif wait:
                # 의존성 프로세스 시작 대기
                logger.info(f"{process_name}의 의존성 시작 대기: {failed_deps}")
                for dep in failed_deps:
                    if dep in self.processes:
                        self.start_process(dep, wait=True)
                # 재확인
                deps_ok, failed_deps = self.check_dependencies(process_name)
                if not deps_ok:
                    # kafka_broker만 실패한 경우는 계속 진행
                    if process_name == "kafka_consumer" and failed_deps == [
                        "kafka_broker"
                    ]:
                        logger.warning(
                            f"{process_name}의 Kafka 브로커가 실행 중이 아닙니다. 브로커 없이 시작합니다."
                        )
                    else:
                        return {
                            "success": False,
                            "error": f"의존성 확인 실패: {failed_deps}",
                        }
            else:
                # kafka_broker만 실패한 경우는 계속 진행
                if process_name == "kafka_consumer" and failed_deps == ["kafka_broker"]:
                    logger.warning(
                        f"{process_name}의 Kafka 브로커가 실행 중이 아닙니다. 브로커 없이 시작합니다."
                    )
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
                # SpiderModule과 KafkaModule은 execute()를 사용해야 함
                if process_name == "spider":
                    # Spider는 모듈이 있으면 모듈을 통해 실행
                    # 기본 spider 하나를 자동으로 시작
                    result = module.execute("list_spiders", {})
                    if result.get("success"):
                        spiders = result.get("spiders", [])
                        if spiders:
                            # 첫 번째 spider를 자동으로 시작
                            default_spider = spiders[0]  # 예: "upbit_trends"
                            logger.info(f"기본 Spider 자동 시작: {default_spider}")
                            start_result = module.execute(
                                "start_spider", {"spider_name": default_spider}
                            )
                            if start_result.get("success"):
                                process_info["status"] = ProcessStatus.RUNNING
                                logger.info(
                                    f"프로세스 시작 성공: {process_name} (기본 Spider: {default_spider} 시작됨)"
                                )
                                return {
                                    "success": True,
                                    "process_name": process_name,
                                    "message": f"Spider 모듈이 활성화되었고 기본 Spider({default_spider})가 시작되었습니다.",
                                }
                            else:
                                # Spider 시작 실패해도 모듈은 활성화됨
                                process_info["status"] = ProcessStatus.RUNNING
                                logger.warning(
                                    f"Spider 모듈 활성화 완료, 하지만 기본 Spider 시작 실패: {start_result.get('error')}"
                                )
                                return {
                                    "success": True,
                                    "process_name": process_name,
                                    "message": "Spider 모듈이 활성화되었습니다. GUI에서 Spider를 선택하여 시작하세요.",
                                }
                        else:
                            process_info["status"] = ProcessStatus.RUNNING
                            logger.info(
                                f"프로세스 시작 성공: {process_name} (모듈 활성화, Spider 없음)"
                            )
                            return {
                                "success": True,
                                "process_name": process_name,
                                "message": "Spider 모듈이 활성화되었습니다.",
                            }
                    else:
                        process_info["status"] = ProcessStatus.ERROR
                        return result
                elif process_name == "kafka_consumer":
                    # Kafka Consumer는 start() 메서드 사용
                    if hasattr(module, "start"):
                        success = module.start()
                        if success:
                            process_info["status"] = ProcessStatus.RUNNING
                            logger.info(f"프로세스 시작 성공: {process_name}")
                            return {"success": True, "process_name": process_name}
                        else:
                            process_info["status"] = ProcessStatus.ERROR
                            return {
                                "success": False,
                                "error": f"{process_name} 시작 실패",
                            }
                    else:
                        # execute 명령어 사용
                        result = module.execute("start_consumer", {})
                        if result.get("success"):
                            process_info["status"] = ProcessStatus.RUNNING
                            return {"success": True, "process_name": process_name}
                        else:
                            process_info["status"] = ProcessStatus.ERROR
                            return result
                elif hasattr(module, "start"):
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
                # run_server.sh를 사용하여 포트 파일 생성 및 포트 충돌 처리
                # AUTO_PORT_SWITCH=true로 설정하여 비대화형 모드로 실행
                env = os.environ.copy()
                env["AUTO_PORT_SWITCH"] = "true"
                # 백엔드 디렉토리로 이동하여 실행
                backend_dir = project_root / "cointicker" / "backend"
                cmd = "bash scripts/run_server.sh"
                # start_new_session=True로 설정하여 부모 프로세스 종료 시에도 계속 실행
                # stdout/stderr를 None으로 설정하여 출력이 터미널에 표시되도록 함
                process = subprocess.Popen(
                    cmd,
                    shell=True,
                    cwd=str(backend_dir),
                    stdout=None,  # 터미널에 출력
                    stderr=None,  # 터미널에 출력
                    env=env,
                    start_new_session=True,  # 새 세션으로 시작
                )
            elif process_name == "frontend":
                # run_dev.sh를 사용하여 포트 파일 읽기 및 포트 충돌 처리
                frontend_dir = project_root / "cointicker" / "frontend"
                cmd = "bash scripts/run_dev.sh"
                # start_new_session=True로 설정하여 부모 프로세스 종료 시에도 계속 실행
                # stdout/stderr를 None으로 설정하여 출력이 터미널에 표시되도록 함
                process = subprocess.Popen(
                    cmd,
                    shell=True,
                    cwd=str(frontend_dir),
                    stdout=None,  # 터미널에 출력
                    stderr=None,  # 터미널에 출력
                    start_new_session=True,  # 새 세션으로 시작
                )
            elif process_name == "kafka_consumer":
                cmd = f"python {project_root}/cointicker/worker-nodes/kafka/kafka_consumer.py"
                process = subprocess.Popen(
                    cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
            elif process_name == "spider":
                # Spider는 모듈이 있으면 모듈을 통해 실행되어야 하므로
                # 여기서는 기본 스파이더 목록만 반환
                return {
                    "success": False,
                    "error": "Spider는 모듈을 통해 실행해야 합니다. SpiderModule이 로드되었는지 확인하세요.",
                }
            elif process_name == "hdfs":
                # HDFS 체크 및 자동 시작 시도
                hdfs_status = self.hdfs_manager.check_and_start(
                    user_confirm_callback=self.user_confirm_callback,
                    user_password_callback=self.user_password_callback,
                )
                if hdfs_status["success"]:
                    self.processes[process_name]["status"] = ProcessStatus.RUNNING
                    return {
                        "success": True,
                        "process_name": process_name,
                        "message": hdfs_status.get("message", "HDFS가 실행 중입니다."),
                    }
                else:
                    self.processes[process_name]["status"] = ProcessStatus.ERROR
                    return {
                        "success": False,
                        "error": hdfs_status.get("error", "HDFS를 시작할 수 없습니다."),
                    }
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
        # 프로세스 이름 정규화
        normalized_name = self._normalize_process_name(process_name)
        if normalized_name is None:
            # MapReduce는 프로세스가 아닌 작업이므로 성공으로 처리
            if process_name == "mapreduce":
                return {
                    "success": True,
                    "message": "MapReduce는 작업 타입입니다. 실행 중인 작업이 없습니다.",
                }
            return {"success": False, "error": f"알 수 없는 프로세스: {process_name}"}

        process_name = normalized_name

        if process_name not in self.processes:
            return {"success": False, "error": f"알 수 없는 프로세스: {process_name}"}

        process_info = self.processes[process_name]

        if process_info["status"] == ProcessStatus.STOPPED:
            return {"success": True, "message": f"{process_name}는 이미 중지되었습니다"}

        process_info["status"] = ProcessStatus.STOPPING

        try:
            module = process_info["module"]
            if module:
                # Kafka Consumer는 특별 처리
                if process_name == "kafka_consumer":
                    if hasattr(module, "stop"):
                        success = module.stop()
                        if success:
                            process_info["status"] = ProcessStatus.STOPPED
                            logger.info(f"프로세스 중지 성공: {process_name}")
                            return {"success": True, "process_name": process_name}
                        else:
                            process_info["status"] = ProcessStatus.ERROR
                            return {
                                "success": False,
                                "error": f"{process_name} 중지 실패",
                            }
                    else:
                        result = module.execute("stop_consumer", {})
                        if result.get("success"):
                            process_info["status"] = ProcessStatus.STOPPED
                            logger.info(f"프로세스 중지 성공: {process_name}")
                            return {"success": True, "process_name": process_name}
                        else:
                            process_info["status"] = ProcessStatus.ERROR
                            return result
                elif hasattr(module, "stop"):
                    success = module.stop()
                    if success:
                        process_info["status"] = ProcessStatus.STOPPED
                        logger.info(f"프로세스 중지 성공: {process_name}")
                        return {"success": True, "process_name": process_name}
                    else:
                        process_info["status"] = ProcessStatus.ERROR
                        return {"success": False, "error": f"{process_name} 중지 실패"}
                else:
                    result = module.execute("stop", {})
                    if result.get("success"):
                        process_info["status"] = ProcessStatus.STOPPED
                        logger.info(f"프로세스 중지 성공: {process_name}")
                        return {"success": True, "process_name": process_name}
                    else:
                        process_info["status"] = ProcessStatus.ERROR
                        return result
            else:
                # 직접 중지
                if process_name == "hdfs":
                    # HDFS는 hdfs_manager를 통해 중지
                    try:
                        hadoop_home = os.environ.get("HADOOP_HOME")
                        if not hadoop_home:
                            # HDFSManager에서 캐시된 경로 가져오기
                            hadoop_home = self.hdfs_manager._get_cached_hadoop_home()

                        if hadoop_home:
                            success = self.hdfs_manager.stop_all_daemons(hadoop_home)
                            if success:
                                process_info["status"] = ProcessStatus.STOPPED
                                logger.info("HDFS 데몬 중지 완료")
                                return {"success": True, "process_name": process_name}
                            else:
                                logger.warning("HDFS 데몬 중지 실패")
                        else:
                            logger.warning("HADOOP_HOME을 찾을 수 없어 HDFS 중지 실패")
                    except Exception as e:
                        logger.error(f"HDFS 중지 중 오류: {e}")

                process = process_info.get("process")
                if process:
                    process.terminate()
                    try:
                        wait_timeout = TimingConfig.get(
                            "pipeline.process_wait_timeout", 5
                        )
                        process.wait(timeout=wait_timeout)
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
            process_stop_delay = TimingConfig.get("pipeline.process_stop_delay", 1)
            time.sleep(process_stop_delay)

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
        else:
            # 프로세스 이름 정규화
            normalized_processes = []
            for p in processes:
                normalized = self._normalize_process_name(p)
                if normalized:
                    normalized_processes.append(normalized)
                elif p == "mapreduce":
                    # MapReduce는 건너뛰기
                    logger.debug(f"프로세스 '{p}'는 작업 타입이므로 건너뜁니다.")
            processes = (
                normalized_processes if normalized_processes else self.stop_order
            )

        results = {}
        for process_name in processes:
            if process_name not in self.processes:
                logger.warning(f"알 수 없는 프로세스: {process_name}, 건너뜁니다.")
                continue

            logger.info(f"프로세스 중지: {process_name}")
            result = self.stop_process(process_name)
            results[process_name] = result

            # 프로세스 간 간격
            process_check_delay = TimingConfig.get("pipeline.process_check_delay", 0.5)
            time.sleep(process_check_delay)

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

    def execute(self, command: str, params: Optional[dict] = None) -> dict:
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
