"""
파이프라인 오케스트레이터
전체 프로세스를 통합 관리하는 모듈

⚠️ 주의: 삭제 및 수정 금지 ⚠️

이 모듈은 GUI와 백엔드/프론트엔드 스크립트와 연동되어 있습니다:
- _start_process_direct()에서 백엔드 시작 시 backend/run_server.sh 사용
- _start_process_direct()에서 프론트엔드 시작 시 frontend/run_dev.sh 사용
- 이 스크립트들이 포트 파일을 생성/읽어 GUI와 포트 동기화

연동된 컴포넌트:
- backend/run_server.sh: 백엔드 포트 파일 생성 (config/.backend_port)
- frontend/run_dev.sh: 백엔드 포트 파일 읽기 및 VITE_API_BASE_URL 설정
- gui/tier2_monitor.py: 포트 파일 읽어 Tier2 모니터 초기화
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
                        if self._start_kafka_broker():
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

    def _check_and_start_hdfs(self) -> Dict:
        """HDFS 체크 및 자동 시작 시도"""
        try:
            import socket
            import subprocess as sp

            # HDFS NameNode 포트 확인 (기본: 9000, 웹 UI: 9870)
            namenode_ports = [9000, 9870]
            hdfs_running = False

            for port in namenode_ports:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    result = sock.connect_ex(("localhost", port))
                    sock.close()
                    if result == 0:
                        hdfs_running = True
                        logger.info(f"HDFS가 실행 중입니다 (포트 {port})")
                        break
                except:
                    pass

            if hdfs_running:
                return {"success": True, "message": "HDFS가 이미 실행 중입니다."}

            # HDFS 시작 시도
            logger.info("HDFS가 실행 중이 아닙니다. 자동으로 시작을 시도합니다...")

            # 클러스터 설정 확인 (cluster_config.yaml 읽기)
            cluster_config = self._get_cluster_config()
            is_cluster_mode = (
                cluster_config is not None and cluster_config.get("cluster") is not None
            )

            if is_cluster_mode and cluster_config:
                logger.info("✅ 클러스터 설정 파일 감지됨. 클러스터 모드로 전환합니다.")
                master_hostname = (
                    cluster_config.get("cluster", {})
                    .get("master", {})
                    .get("hostname", "unknown")
                )
                worker_count = len(cluster_config.get("cluster", {}).get("workers", []))
                logger.info(
                    f"   마스터: {master_hostname}, 워커 노드: {worker_count}개"
                )
            else:
                logger.debug(
                    "클러스터 설정 파일이 없거나 불완전합니다. 단일 노드 모드로 진행합니다."
                )

            # HADOOP_HOME 환경 변수 확인 및 자동 설정
            hadoop_home = os.environ.get("HADOOP_HOME")
            if not hadoop_home:
                # 프로젝트 루트 찾기 (현재 파일 기준)
                # pipeline_orchestrator.py -> gui/modules -> gui -> cointicker -> PICU -> bigdata
                current_file = Path(__file__)
                project_root = current_file.parent.parent.parent.parent.parent

                # 검색할 경로 목록 (프로젝트 내 경로 우선)
                search_paths = [
                    # 프로젝트 내 hadoop_project 경로
                    project_root / "hadoop_project" / "hadoop-3.4.1",
                    project_root.parent / "hadoop_project" / "hadoop-3.4.1",
                    # 일반적인 시스템 경로
                    Path("/opt/hadoop"),
                    Path("/usr/local/hadoop"),
                    Path("/home/bigdata/hadoop-3.4.1"),
                    Path("/usr/lib/hadoop"),
                    # macOS Homebrew 경로
                    Path("/opt/homebrew/opt/hadoop"),
                    Path("/usr/local/opt/hadoop"),
                ]

                for path in search_paths:
                    if path.exists() and (path / "sbin" / "start-dfs.sh").exists():
                        hadoop_home = str(path)
                        logger.info(f"✅ HADOOP_HOME 자동 감지: {hadoop_home}")
                        # 환경 변수에 설정 (현재 프로세스와 하위 프로세스에 적용)
                        os.environ["HADOOP_HOME"] = hadoop_home
                        break

            if hadoop_home:
                start_dfs_script = Path(hadoop_home) / "sbin" / "start-dfs.sh"
                if start_dfs_script.exists():
                    logger.info(f"HDFS 시작 스크립트 발견: {start_dfs_script}")

                    # HDFS 환경 변수 설정
                    hdfs_env = {**os.environ, "HADOOP_HOME": hadoop_home}
                    import getpass

                    current_user = getpass.getuser()
                    hdfs_env["HDFS_NAMENODE_USER"] = current_user
                    hdfs_env["HDFS_DATANODE_USER"] = current_user
                    hdfs_env["HDFS_SECONDARYNAMENODE_USER"] = current_user

                    # 1단계: 클러스터 모드 확인 및 설정
                    if is_cluster_mode and cluster_config:
                        logger.info(
                            "클러스터 모드 감지됨. 클러스터 설정을 확인합니다..."
                        )
                        cluster_setup_success = self._setup_cluster_mode(
                            hadoop_home, cluster_config
                        )
                        if cluster_setup_success:
                            logger.info(
                                "✅ 클러스터 모드 설정 완료. HDFS를 시작합니다."
                            )
                            ssh_available = True
                        else:
                            logger.warning(
                                "⚠️ 클러스터 모드 설정 실패. 단일 노드 모드로 전환합니다."
                            )
                            ssh_available = False
                    else:
                        # 단일 노드 모드: SSH 연결 테스트
                        logger.info("단일 노드 모드: SSH 연결 테스트 중...")
                        ssh_test = subprocess.run(
                            [
                                "ssh",
                                "-o",
                                "StrictHostKeyChecking=no",
                                "-o",
                                "ConnectTimeout=2",
                                "localhost",
                                "exit",
                            ],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            timeout=5,
                        )
                        ssh_available = ssh_test.returncode == 0

                    # 2단계: SSH 실패 시 단일 노드 모드로 분기 - 로컬 SSH 자동 설정
                    if not ssh_available:
                        logger.info(
                            "SSH 연결 실패. 단일 노드 모드로 전환하여 로컬 SSH 설정을 시도합니다..."
                        )
                        ssh_setup_success = self._setup_local_ssh()

                        if ssh_setup_success:
                            # SSH 설정 후 다시 테스트
                            ssh_test_retry = subprocess.run(
                                [
                                    "ssh",
                                    "-o",
                                    "StrictHostKeyChecking=no",
                                    "-o",
                                    "ConnectTimeout=2",
                                    "localhost",
                                    "exit",
                                ],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                timeout=5,
                            )
                            ssh_available = ssh_test_retry.returncode == 0

                            if ssh_available:
                                logger.info("✅ 로컬 SSH 설정 완료. HDFS를 시작합니다.")
                            else:
                                logger.warning(
                                    "⚠️ SSH 설정 후에도 연결 실패. SSH 없이 HDFS 데몬을 직접 시작합니다."
                                )
                                # SSH 없이 데몬 직접 시작 모드로 전환
                                ssh_available = False
                        else:
                            logger.warning(
                                "⚠️ 로컬 SSH 설정 실패. SSH 없이 HDFS 데몬을 직접 시작합니다."
                            )
                            ssh_available = False
                    else:
                        logger.info(
                            "✅ SSH 연결 성공. 클러스터 모드로 HDFS를 시작합니다."
                        )

                    # HDFS 시작
                    if not ssh_available:
                        # SSH 없이 데몬 직접 시작 (단일 노드 모드)
                        logger.info("SSH 없이 HDFS 데몬을 직접 시작합니다...")
                        return self._start_hdfs_daemons_direct(
                            hadoop_home, hdfs_env, namenode_ports
                        )
                    else:
                        # SSH를 통한 일반 시작 (클러스터 모드)
                        logger.info("HDFS 시작 중...")
                        process = subprocess.Popen(
                            ["bash", str(start_dfs_script)],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            start_new_session=True,
                            env=hdfs_env,
                        )
                    import time

                    # HDFS 시작 대기 및 포트 확인 (재시도 로직)
                    max_retries = 15  # 최대 30초 대기 (2초 간격)
                    retry_interval = 2

                    for attempt in range(max_retries):
                        time.sleep(retry_interval)

                        # 프로세스가 종료되었는지 확인
                        if process.poll() is not None:
                            # 프로세스가 종료됨 - 에러 출력 확인
                            stdout, stderr = process.communicate()
                            if stderr:
                                stderr_text = stderr.decode("utf-8", errors="ignore")
                                # SSH 관련 경고는 무시 (단일 노드 모드에서는 정상)
                                if (
                                    "ssh:" in stderr_text.lower()
                                    or "connection refused" in stderr_text.lower()
                                ):
                                    logger.debug(
                                        f"HDFS SSH 경고 (단일 노드 모드에서는 정상): {stderr_text[:300]}"
                                    )
                                    # SSH 오류만 있고 실제 데몬이 시작되었을 수 있으므로 break하지 않고 포트 확인 계속
                                else:
                                    logger.warning(
                                        f"HDFS 시작 스크립트 오류: {stderr_text[:500]}"
                                    )
                                    # 다른 오류는 break
                                    break

                        # 포트 확인
                        for port in namenode_ports:
                            try:
                                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                sock.settimeout(1)
                                result = sock.connect_ex(("localhost", port))
                                sock.close()
                                if result == 0:
                                    logger.info(
                                        f"✅ HDFS 시작 성공 (포트 {port}, 시도 {attempt + 1}/{max_retries})"
                                    )
                                    return {
                                        "success": True,
                                        "message": f"HDFS가 시작되었습니다 (포트 {port})",
                                    }
                            except Exception as e:
                                logger.debug(f"HDFS 포트 확인 오류 (포트 {port}): {e}")

                        if attempt < max_retries - 1:
                            logger.debug(
                                f"HDFS 시작 대기 중... ({attempt + 1}/{max_retries})"
                            )

                    return {
                        "success": False,
                        "error": f"HDFS 시작 후 포트 확인 실패 (최대 {max_retries * retry_interval}초 대기)",
                    }
                else:
                    return {
                        "success": False,
                        "error": f"HDFS 시작 스크립트를 찾을 수 없습니다: {start_dfs_script}",
                    }
            else:
                # HADOOP_HOME이 없어도 경고만 출력하고 계속 진행
                # HDFS는 외부 서비스이므로 필수는 아님
                logger.warning(
                    "HADOOP_HOME 환경 변수가 설정되지 않았고 일반 경로에서도 찾을 수 없습니다. "
                    "HDFS는 수동으로 시작해야 합니다."
                )
                return {
                    "success": False,
                    "error": "HADOOP_HOME 환경 변수가 설정되지 않았고 일반 경로에서도 찾을 수 없습니다. HDFS는 수동으로 시작해야 합니다.",
                }
        except Exception as e:
            logger.error(f"HDFS 체크 및 시작 중 오류: {e}")
            return {"success": False, "error": f"HDFS 시작 중 오류: {str(e)}"}

    def _setup_local_ssh(self) -> bool:
        """
        단일 노드 모드를 위한 로컬 SSH 자동 설정

        Returns:
            SSH 설정 성공 여부
        """
        try:
            import getpass
            from pathlib import Path as PathLib
            import platform

            home_dir = PathLib.home()
            ssh_dir = home_dir / ".ssh"

            # .ssh 디렉토리 생성
            ssh_dir.mkdir(mode=0o700, exist_ok=True)

            # macOS에서 SSH 서버 활성화 확인 및 시도
            if platform.system() == "Darwin":  # macOS
                logger.info("macOS 감지: SSH 서버 활성화 확인 중...")
                # SSH 서버 상태 확인
                ssh_status = subprocess.run(
                    ["sudo", "systemsetup", "-getremotelogin"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=5,
                )

                if ssh_status.returncode == 0:
                    status_output = ssh_status.stdout.decode(
                        "utf-8", errors="ignore"
                    ).strip()
                    if "On" not in status_output:
                        logger.info(
                            "SSH 서버가 비활성화되어 있습니다. 활성화를 시도합니다..."
                        )
                        logger.warning(
                            "⚠️ SSH 서버 활성화는 관리자 권한이 필요합니다. "
                            "수동으로 활성화하려면: sudo systemsetup -setremotelogin on"
                        )
                        # 비대화형으로 활성화 시도 (비밀번호 필요하므로 실패할 수 있음)
                        enable_ssh = subprocess.run(
                            ["sudo", "systemsetup", "-setremotelogin", "on"],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            timeout=5,
                            input=b"\n",  # 비밀번호 프롬프트에 빈 입력
                        )
                        if enable_ssh.returncode == 0:
                            logger.info("✅ SSH 서버 활성화 완료")
                            import time

                            time.sleep(2)  # SSH 서버 시작 대기
                        else:
                            logger.warning(
                                "SSH 서버 자동 활성화 실패. 수동으로 활성화해야 합니다."
                            )
                    else:
                        logger.debug("SSH 서버가 이미 활성화되어 있습니다.")
                else:
                    logger.debug(
                        "SSH 서버 상태 확인 실패 (권한 필요). 계속 진행합니다."
                    )

            # SSH 키 생성 (없는 경우)
            private_key = ssh_dir / "id_rsa"
            public_key = ssh_dir / "id_rsa.pub"

            if not private_key.exists():
                logger.info("SSH 키 생성 중...")
                keygen_result = subprocess.run(
                    ["ssh-keygen", "-t", "rsa", "-P", "", "-f", str(private_key)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=10,
                )
                if keygen_result.returncode != 0:
                    logger.error(
                        f"SSH 키 생성 실패: {keygen_result.stderr.decode('utf-8', errors='ignore')}"
                    )
                    return False
                logger.info("✅ SSH 키 생성 완료")
            else:
                logger.debug("SSH 키가 이미 존재합니다.")

            # authorized_keys에 공개키 추가
            if public_key.exists():
                authorized_keys = ssh_dir / "authorized_keys"
                public_key_content = public_key.read_text().strip()

                # authorized_keys 파일이 없거나 현재 키가 없으면 추가
                if not authorized_keys.exists():
                    authorized_keys.write_text(public_key_content + "\n")
                    authorized_keys.chmod(0o600)
                    logger.info("✅ authorized_keys 파일 생성 및 공개키 추가 완료")
                else:
                    authorized_keys_content = authorized_keys.read_text()
                    if public_key_content not in authorized_keys_content:
                        with authorized_keys.open("a") as f:
                            f.write(public_key_content + "\n")
                        authorized_keys.chmod(0o600)
                        logger.info("✅ authorized_keys에 공개키 추가 완료")
                    else:
                        logger.debug("공개키가 이미 authorized_keys에 있습니다.")

                # known_hosts에 localhost 추가 (StrictHostKeyChecking 우회)
                known_hosts = ssh_dir / "known_hosts"
                if (
                    not known_hosts.exists()
                    or "localhost" not in known_hosts.read_text()
                ):
                    logger.debug("known_hosts에 localhost 추가 중...")
                    # ssh-keyscan으로 localhost 키 추가
                    keyscan_result = subprocess.run(
                        ["ssh-keyscan", "-H", "localhost"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        timeout=5,
                    )
                    if keyscan_result.returncode == 0:
                        keys = keyscan_result.stdout.decode("utf-8", errors="ignore")
                        with known_hosts.open("a") as f:
                            f.write(keys)
                        known_hosts.chmod(0o600)
                        logger.debug("✅ known_hosts에 localhost 추가 완료")

                return True
            else:
                logger.error("공개키 파일을 찾을 수 없습니다.")
                return False

        except Exception as e:
            logger.error(f"로컬 SSH 설정 중 오류: {e}")
            return False

    def _start_hdfs_daemons_direct(
        self, hadoop_home: str, hdfs_env: Dict, namenode_ports: List[int]
    ) -> Dict:
        """
        SSH 없이 HDFS 데몬을 직접 시작 (단일 노드 모드)

        Args:
            hadoop_home: HADOOP_HOME 경로
            hdfs_env: HDFS 환경 변수 딕셔너리
            namenode_ports: NameNode 포트 목록

        Returns:
            시작 결과
        """
        try:
            import time
            import socket

            hadoop_path = Path(hadoop_home)
            bin_dir = hadoop_path / "bin"

            # NameNode 포맷 확인 (필요시)
            namenode_dir = hadoop_path / "tmp" / "dfs" / "name"
            if not namenode_dir.exists() or not any(namenode_dir.iterdir()):
                logger.info("NameNode 포맷이 필요합니다. 포맷을 시도합니다...")
                format_result = subprocess.run(
                    [
                        str(bin_dir / "hdfs"),
                        "namenode",
                        "-format",
                        "-force",
                        "-nonInteractive",
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=30,
                    env=hdfs_env,
                    cwd=str(hadoop_path),
                )
                if format_result.returncode == 0:
                    logger.info("✅ NameNode 포맷 완료")
                else:
                    stderr_text = format_result.stderr.decode("utf-8", errors="ignore")
                    if "already formatted" not in stderr_text.lower():
                        logger.warning(f"NameNode 포맷 실패: {stderr_text[:200]}")
                    # 포맷 실패해도 계속 진행 (이미 포맷되어 있을 수 있음)

            # 데몬 직접 시작
            logger.info("HDFS 데몬 직접 시작 중...")
            daemons = []

            # NameNode 시작
            namenode_process = subprocess.Popen(
                [str(bin_dir / "hdfs"), "--daemon", "start", "namenode"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True,
                env=hdfs_env,
                cwd=str(hadoop_path),
            )
            daemons.append(("namenode", namenode_process))
            logger.info("NameNode 데몬 시작 중...")
            time.sleep(2)

            # DataNode 시작
            datanode_process = subprocess.Popen(
                [str(bin_dir / "hdfs"), "--daemon", "start", "datanode"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True,
                env=hdfs_env,
                cwd=str(hadoop_path),
            )
            daemons.append(("datanode", datanode_process))
            logger.info("DataNode 데몬 시작 중...")
            time.sleep(2)

            # SecondaryNameNode 시작
            secondary_namenode_process = subprocess.Popen(
                [str(bin_dir / "hdfs"), "--daemon", "start", "secondarynamenode"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True,
                env=hdfs_env,
                cwd=str(hadoop_path),
            )
            daemons.append(("secondarynamenode", secondary_namenode_process))
            logger.info("SecondaryNameNode 데몬 시작 중...")
            time.sleep(3)

            # 포트 확인 (재시도 로직)
            max_retries = 15
            retry_interval = 2

            for attempt in range(max_retries):
                time.sleep(retry_interval)

                # 포트 확인
                for port in namenode_ports:
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(1)
                        result = sock.connect_ex(("localhost", port))
                        sock.close()
                        if result == 0:
                            logger.info(
                                f"✅ HDFS 시작 성공 (포트 {port}, 시도 {attempt + 1}/{max_retries})"
                            )
                            return {
                                "success": True,
                                "message": f"HDFS가 시작되었습니다 (포트 {port})",
                            }
                    except Exception as e:
                        logger.debug(f"HDFS 포트 확인 오류 (포트 {port}): {e}")

                if attempt < max_retries - 1:
                    logger.debug(f"HDFS 시작 대기 중... ({attempt + 1}/{max_retries})")

            # 실패 시 데몬 정리
            logger.warning("HDFS 데몬 시작 실패. 데몬을 정리합니다...")
            for daemon_name, proc in daemons:
                try:
                    proc.terminate()
                    proc.wait(timeout=5)
                except:
                    pass

            return {
                "success": False,
                "error": f"HDFS 데몬 시작 후 포트 확인 실패 (최대 {max_retries * retry_interval}초 대기)",
            }

        except Exception as e:
            logger.error(f"HDFS 데몬 직접 시작 중 오류: {e}")
            return {"success": False, "error": f"HDFS 데몬 시작 중 오류: {str(e)}"}

    def _get_cluster_config(self) -> Optional[Dict]:
        """클러스터 설정 파일 읽기 (cluster_config.yaml 자동 읽기)"""
        try:
            from gui.core.config_manager import ConfigManager

            config_manager = ConfigManager()
            cluster_config = config_manager.load_config("cluster")

            if cluster_config:
                logger.debug(
                    f"클러스터 설정 파일 로드 성공: {config_manager.config_dir / 'cluster_config.yaml'}"
                )
            else:
                logger.debug("클러스터 설정 파일이 없거나 비어있습니다.")

            return cluster_config
        except Exception as e:
            logger.debug(f"클러스터 설정 파일 읽기 실패: {e}")
            return None

    def _setup_cluster_mode(self, hadoop_home: str, cluster_config: Dict) -> bool:
        """
        클러스터 모드 설정 (유선 연결 시 자동 설정)

        Args:
            hadoop_home: HADOOP_HOME 경로
            cluster_config: 클러스터 설정 딕셔너리

        Returns:
            설정 성공 여부
        """
        try:
            hadoop_path = Path(hadoop_home)
            etc_hadoop = hadoop_path / "etc" / "hadoop"

            if not etc_hadoop.exists():
                logger.error(f"Hadoop 설정 디렉토리를 찾을 수 없습니다: {etc_hadoop}")
                return False

            cluster_info = cluster_config.get("cluster", {})
            hadoop_info = cluster_config.get("hadoop", {})

            if not cluster_info or not hadoop_info:
                logger.warning("클러스터 설정이 불완전합니다.")
                return False

            master = cluster_info.get("master", {})
            workers = cluster_info.get("workers", [])
            namenode_url = hadoop_info.get("hdfs", {}).get("namenode", "")
            replication = hadoop_info.get("hdfs", {}).get("replication", 1)

            if not master or not workers:
                logger.warning("마스터 또는 워커 노드 정보가 없습니다.")
                return False

            master_hostname = master.get("hostname", "localhost")

            # 1. 각 노드에 SSH 연결 테스트
            logger.info("클러스터 노드 SSH 연결 테스트 중...")
            all_nodes_accessible = True

            # 마스터 노드 테스트
            master_ssh = subprocess.run(
                [
                    "ssh",
                    "-o",
                    "StrictHostKeyChecking=no",
                    "-o",
                    "ConnectTimeout=3",
                    master_hostname,
                    "exit",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5,
            )
            if master_ssh.returncode != 0:
                logger.warning(f"마스터 노드({master_hostname}) SSH 연결 실패")
                all_nodes_accessible = False

            # 워커 노드 테스트
            for worker in workers:
                worker_hostname = worker.get("hostname", "")
                if worker_hostname:
                    worker_ssh = subprocess.run(
                        [
                            "ssh",
                            "-o",
                            "StrictHostKeyChecking=no",
                            "-o",
                            "ConnectTimeout=3",
                            worker_hostname,
                            "exit",
                        ],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        timeout=5,
                    )
                    if worker_ssh.returncode != 0:
                        logger.warning(f"워커 노드({worker_hostname}) SSH 연결 실패")
                        all_nodes_accessible = False

            if not all_nodes_accessible:
                logger.warning(
                    "일부 노드에 SSH 연결할 수 없습니다. 클러스터 모드 설정을 건너뜁니다."
                )
                return False

            # 2. core-site.xml 생성/업데이트
            core_site = etc_hadoop / "core-site.xml"
            logger.info(f"core-site.xml 설정 중: {namenode_url}")
            core_site.write_text(
                f"""<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
    <property>
        <name>fs.defaultFS</name>
        <value>{namenode_url}</value>
    </property>
</configuration>
"""
            )

            # 3. hdfs-site.xml 생성/업데이트
            hdfs_site = etc_hadoop / "hdfs-site.xml"
            logger.info(f"hdfs-site.xml 설정 중: replication={replication}")
            hdfs_site.write_text(
                f"""<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
    <property>
        <name>dfs.replication</name>
        <value>{replication}</value>
    </property>
</configuration>
"""
            )

            # 4. workers 파일 생성
            workers_file = etc_hadoop / "workers"
            worker_hostnames = [
                w.get("hostname", "") for w in workers if w.get("hostname")
            ]
            if worker_hostnames:
                logger.info(f"workers 파일 생성 중: {', '.join(worker_hostnames)}")
                workers_file.write_text("\n".join(worker_hostnames) + "\n")

            # 5. master 파일 생성 (SecondaryNameNode용)
            master_file = etc_hadoop / "master"
            logger.info(f"master 파일 생성 중: {master_hostname}")
            master_file.write_text(master_hostname + "\n")

            logger.info("✅ 클러스터 모드 설정 완료")
            return True

        except Exception as e:
            logger.error(f"클러스터 모드 설정 중 오류: {e}")
            return False

    def _start_kafka_broker(self) -> bool:
        """Kafka 브로커 자동 시작"""
        try:
            project_root = Path(__file__).parent.parent.parent.parent

            # 여러 가능한 Kafka 시작 스크립트 경로 확인
            kafka_scripts = [
                project_root / "kafka_project" / "kafka_streams" / "start_kafka.sh",
                Path("/opt/homebrew/opt/kafka/bin/kafka-server-start.sh"),
                Path("/usr/local/kafka/bin/kafka-server-start.sh"),
            ]

            # 스크립트가 있으면 실행
            for script_path in kafka_scripts:
                if script_path.exists() and script_path.is_file():
                    logger.info(f"Kafka 브로커 시작 스크립트 발견: {script_path}")
                    # 백그라운드에서 실행
                    process = subprocess.Popen(
                        ["bash", str(script_path)],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        start_new_session=True,
                    )
                    # 시작 확인을 위해 잠시 대기
                    import time

                    time.sleep(3)
                    # 포트 확인
                    import socket

                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    result = sock.connect_ex(("localhost", 9092))
                    sock.close()
                    if result == 0:
                        logger.info(f"✅ Kafka 브로커 시작 성공 (PID: {process.pid})")
                        return True
                    else:
                        logger.warning("Kafka 브로커 시작 후 포트 확인 실패")
                        return False

            # 스크립트가 없으면 직접 kafka-server-start 시도
            logger.info(
                "Kafka 시작 스크립트를 찾을 수 없습니다. 직접 시작을 시도합니다..."
            )
            # macOS Homebrew 경로
            kafka_bin = Path("/opt/homebrew/opt/kafka/bin/kafka-server-start")
            kafka_config = Path("/opt/homebrew/etc/kafka/server.properties")

            if kafka_bin.exists() and kafka_config.exists():
                process = subprocess.Popen(
                    [str(kafka_bin), str(kafka_config)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    start_new_session=True,
                )
                import time

                time.sleep(3)
                import socket

                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex(("localhost", 9092))
                sock.close()
                if result == 0:
                    logger.info(f"✅ Kafka 브로커 시작 성공 (PID: {process.pid})")
                    return True

            logger.warning(
                "Kafka 브로커를 자동으로 시작할 수 없습니다. 수동으로 시작해주세요."
            )
            return False
        except Exception as e:
            logger.error(f"Kafka 브로커 시작 중 오류: {e}")
            return False

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
                cmd = "bash run_server.sh"
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
                cmd = "bash run_dev.sh"
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
                cmd = f"python {project_root}/cointicker/worker-nodes/kafka_consumer.py"
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
                hdfs_status = self._check_and_start_hdfs()
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
