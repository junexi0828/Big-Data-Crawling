"""
Kafka 모듈
Kafka Producer/Consumer를 관리하는 모듈
"""

import subprocess
import signal
import os
import time
import threading
import json
from typing import Dict, Any, Optional, Union
from pathlib import Path

from gui.core.module_manager import ModuleInterface
from shared.logger import setup_logger

logger = setup_logger(__name__)


class ProcessWrapper:
    """
    psutil.Process를 subprocess.Popen 인터페이스처럼 사용할 수 있게 하는 래퍼 클래스
    기존 프로세스를 발견했을 때 사용
    """

    def __init__(self, psutil_process):
        """
        Args:
            psutil_process: psutil.Process 객체
        """
        self.process = psutil_process
        self.pid = psutil_process.pid

    def poll(self):
        """
        프로세스가 실행 중인지 확인 (subprocess.Popen.poll() 호환)

        Returns:
            실행 중이면 None, 종료되었으면 종료 코드
        """
        try:
            if self.process.is_running():
                return None  # 실행 중
            else:
                return (
                    self.process.returncode
                    if hasattr(self.process, "returncode")
                    else 0
                )
        except Exception:
            return 0  # 종료된 것으로 간주

    def terminate(self):
        """프로세스 종료 요청"""
        try:
            self.process.terminate()
        except Exception as e:
            logger.debug(f"프로세스 종료 실패 (PID: {self.pid}): {e}")

    def kill(self):
        """프로세스 강제 종료"""
        try:
            self.process.kill()
        except Exception as e:
            logger.debug(f"프로세스 강제 종료 실패 (PID: {self.pid}): {e}")

    def wait(self, timeout=None):
        """프로세스 종료 대기"""
        try:
            self.process.wait(timeout=timeout)
        except Exception as e:
            logger.debug(f"프로세스 대기 실패 (PID: {self.pid}): {e}")


class KafkaModule(ModuleInterface):
    """Kafka 모듈 클래스"""

    def __init__(self, name: str = "KafkaModule"):
        super().__init__(name)
        # 프로젝트 루트 기준으로 경로 해결
        # gui/modules/kafka_module.py -> cointicker/worker-nodes/kafka/kafka_consumer.py
        from shared.path_utils import get_cointicker_root

        cointicker_root = get_cointicker_root()
        self.consumer_path = (
            cointicker_root / "worker-nodes" / "kafka" / "kafka_consumer.py"
        )
        # ProcessWrapper 또는 subprocess.Popen을 저장할 수 있음
        self.consumer_process: Optional[Union[subprocess.Popen, ProcessWrapper]] = None
        self.consumer_log_file = None  # 로그 파일 핸들 (프로세스 종료 시 닫기 위해)
        self.bootstrap_servers = ["localhost:9092"]
        self.topics = ["cointicker.raw.*"]
        self.group_id = "cointicker-consumer"
        self.status_topic = "cointicker.consumer.status"  # 상태 토픽
        self.status_consumer = None  # 상태 구독용 Consumer
        self.latest_status = {}  # 최신 상태 캐시
        self._status_consumer_thread = None  # 상태 구독 스레드

        # 캐싱 (성능 최적화)
        self._stats_cache: Optional[Dict[str, Any]] = None
        self._stats_cache_time: float = 0
        self._consumer_groups_cache: Optional[Dict[str, Any]] = None
        self._consumer_groups_cache_time: float = 0
        self._cache_ttl: float = 5.0  # 5초 TTL

    def initialize(self, config: dict) -> bool:
        """모듈 초기화"""
        try:
            self.config = config
            # 프로젝트 루트 기준으로 경로 해결
            from shared.path_utils import get_cointicker_root

            cointicker_root = get_cointicker_root()
            consumer_relative = config.get(
                "consumer_path", "worker-nodes/kafka/kafka_consumer.py"
            )
            self.consumer_path = (cointicker_root / consumer_relative).resolve()
            self.bootstrap_servers = config.get("bootstrap_servers", ["localhost:9092"])
            self.topics = config.get("topics", ["cointicker.raw.*"])
            self.group_id = config.get("group_id", "cointicker-consumer")

            # 상태 토픽 구독 시작
            self._start_status_consumer()

            logger.info(f"Kafka 모듈 초기화 완료: consumer_path = {self.consumer_path}")
            return True
        except Exception as e:
            logger.error(f"Kafka 모듈 초기화 실패: {e}")
            return False

    def start(self) -> bool:
        """Consumer 서비스 시작"""
        # 1. 모듈이 관리하는 프로세스 확인
        if self.consumer_process and self.consumer_process.poll() is None:
            # 이미 실행 중이면 성공으로 간주 (중복 시작 방지)
            logger.debug(
                "Kafka Consumer가 이미 실행 중입니다 (PID: {})".format(
                    self.consumer_process.pid
                )
            )
            return True

        # 2. 시스템 전체에서 실행 중인 Consumer 프로세스 확인 (중복 방지)
        try:
            import psutil

            for proc in psutil.process_iter(["pid", "name", "cmdline"]):
                try:
                    cmdline = proc.info.get("cmdline", [])
                    if (
                        cmdline
                        and "kafka_consumer.py" in " ".join(cmdline)
                        and "--group-id" in " ".join(cmdline)
                        and self.group_id in " ".join(cmdline)
                    ):
                        # 같은 group_id로 실행 중인 Consumer 발견
                        pid = proc.info["pid"]
                        logger.warning(
                            f"같은 group_id({self.group_id})로 실행 중인 Kafka Consumer 발견 (PID: {pid})"
                        )
                        # 기존 프로세스를 ProcessWrapper로 연결 (subprocess.Popen 인터페이스 호환)
                        try:
                            psutil_proc = psutil.Process(pid)
                            self.consumer_process = ProcessWrapper(psutil_proc)
                            logger.info(
                                f"기존 Kafka Consumer 프로세스 연결 완료 (PID: {pid})"
                            )

                            # Kafka 토픽 기반 모니터링 사용 (process_monitor 불필요)
                            # 상태는 Kafka 토픽에서 자동으로 수신됨
                            logger.debug(
                                f"기존 Consumer 프로세스 연결 완료 (PID: {pid}), "
                                f"상태는 Kafka 토픽에서 모니터링됨"
                            )
                        except Exception as e:
                            logger.debug(f"기존 프로세스 연결 실패 (무시): {e}")
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except ImportError:
            # psutil이 없으면 건너뛰기
            pass
        except Exception as e:
            logger.debug(f"시스템 프로세스 확인 중 오류 (무시): {e}")

        try:
            # Consumer 실행
            cmd = [
                "python",
                str(self.consumer_path),
                "--bootstrap-servers",
                ",".join(self.bootstrap_servers),
                "--topics",
                *self.topics,
                "--group-id",
                self.group_id,
            ]

            # 프로젝트 루트를 작업 디렉토리로 설정
            from shared.path_utils import get_cointicker_root

            cointicker_root = get_cointicker_root()

            # 환경 변수 설정 (PYTHONPATH 포함)
            env = os.environ.copy()
            pythonpath = env.get("PYTHONPATH", "")

            # worker-nodes와 cointicker 경로를 PYTHONPATH에 추가
            worker_nodes_path = str((cointicker_root / "worker-nodes").resolve())
            paths = [str(cointicker_root), worker_nodes_path]
            if pythonpath:
                paths.append(pythonpath)
            env["PYTHONPATH"] = ":".join(paths)

            # 로그 파일 경로 설정 (stdout/stderr 리다이렉트용)
            log_dir = cointicker_root / "logs"
            log_dir.mkdir(exist_ok=True)
            log_file_path = log_dir / "kafka_consumer.log"

            # 로그 파일을 append 모드로 열기 (stdout/stderr 모두 리다이렉트)
            # 프로세스 종료 시 닫기 위해 핸들 저장
            self.consumer_log_file = open(
                log_file_path, "a", encoding="utf-8", buffering=1
            )

            self.consumer_process = subprocess.Popen(
                cmd,
                stdout=self.consumer_log_file,  # 로그 파일로 리다이렉트
                stderr=subprocess.STDOUT,  # stderr도 stdout으로 리다이렉트 (같은 파일)
                cwd=str(cointicker_root.resolve()),  # 프로젝트 루트를 작업 디렉토리로
                env=env,  # PYTHONPATH가 설정된 환경 변수 사용
                universal_newlines=True,
                bufsize=1,
                start_new_session=True,  # GUI 종료 후에도 계속 실행
            )

            # Kafka 토픽 기반 모니터링 사용 (process_monitor 불필요)
            # 상태는 Kafka 토픽에서 자동으로 수신됨
            logger.debug(
                f"Kafka Consumer 시작 완료 (PID: {self.consumer_process.pid}), "
                f"상태는 Kafka 토픽에서 모니터링됨"
            )

            self.status = "running"
            logger.info(f"Kafka Consumer 시작: PID {self.consumer_process.pid}")
            return True

        except Exception as e:
            logger.error(f"Kafka Consumer 시작 실패: {e}")
            return False

    def stop(self) -> bool:
        """Consumer 서비스 중지"""
        if not self.consumer_process:
            logger.warning("Kafka Consumer가 실행 중이 아닙니다")
            return False

        try:
            # 프로세스 종료
            self.consumer_process.terminate()
            try:
                self.consumer_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.consumer_process.kill()
                self.consumer_process.wait()

            # 로그 파일 닫기 (새 프로세스인 경우에만)
            if self.consumer_log_file:
                try:
                    self.consumer_log_file.close()
                    self.consumer_log_file = None
                except Exception as e:
                    logger.debug(f"로그 파일 닫기 실패: {e}")

            self.consumer_process = None
            self.status = "stopped"
            logger.info("Kafka Consumer 중지 완료")
            return True

        except Exception as e:
            logger.error(f"Kafka Consumer 중지 실패: {e}")
            return False

    def restart(self) -> bool:
        """Consumer 서비스 재시작"""
        self.stop()
        return self.start()

    def _start_status_consumer(self):
        """상태 토픽 구독 시작"""
        try:
            from shared.kafka_client import KafkaConsumerClient

            # 상태 구독용 Consumer 생성 (별도 group_id 사용)
            self.status_consumer = KafkaConsumerClient(
                bootstrap_servers=self.bootstrap_servers,
                group_id=f"{self.group_id}-status-monitor",  # 별도 그룹 ID
                auto_offset_reset="latest",  # 최신 상태만 읽기 (과거 메시지 불필요)
                enable_auto_commit=True,
            )

            # 상태 토픽 구독
            if self.status_consumer.connect(
                [self.status_topic], max_retries=3, retry_delay=1.0  # 재시도 증가
            ):
                logger.info(f"✅ 상태 토픽 구독 시작: {self.status_topic}")
                # 별도 스레드에서 메시지 수신
                self._status_consumer_thread = threading.Thread(
                    target=self._status_consume_loop,
                    daemon=True,
                )
                self._status_consumer_thread.start()
                logger.info("상태 Consumer 스레드 시작 완료")
            else:
                logger.warning("⚠️ 상태 토픽 구독 실패 (브로커 없음 또는 토픽 없음)")
                self.status_consumer = None
        except Exception as e:
            logger.warning(f"⚠️ 상태 Consumer 초기화 실패: {e}", exc_info=True)
            self.status_consumer = None

    def _status_consume_loop(self):
        """상태 메시지 수신 루프 (재연결 로직 포함)"""
        logger.info("상태 메시지 수신 루프 시작")
        reconnect_delay = 5  # 재연결 시도 간격 (초)
        consecutive_failures = 0  # 연속 실패 횟수

        while True:
            try:
                # Consumer가 없거나 연결이 끊어진 경우 재연결 시도
                if not self.status_consumer or not self.status_consumer.consumer:
                    logger.warning(
                        f"상태 Consumer가 없습니다. {reconnect_delay}초 후 재연결 시도..."
                    )
                    time.sleep(reconnect_delay)
                    self._start_status_consumer()
                    consecutive_failures += 1
                    if consecutive_failures > 10:
                        logger.error(
                            "상태 Consumer 재연결 실패가 너무 많습니다. "
                            "Kafka 브로커 상태를 확인하세요."
                        )
                        time.sleep(30)  # 30초 대기 후 재시도
                        consecutive_failures = 0
                    continue

                consecutive_failures = 0  # 성공 시 실패 카운터 리셋
                poll_timeout_ms = 1000  # 1초 타임아웃
                no_message_count = 0

                while True:
                    try:
                        # 메시지 폴링
                        messages = self.status_consumer.consumer.poll(
                            timeout_ms=poll_timeout_ms
                        )

                        if not messages:
                            no_message_count += 1
                            # 10초마다 로그 (디버깅용)
                            if no_message_count % 10 == 0:
                                logger.debug(f"상태 메시지 대기 중... (10초 경과)")
                            continue

                        no_message_count = 0  # 메시지 수신 시 카운터 리셋

                        for topic_partition, partition_messages in messages.items():
                            for message in partition_messages:
                                try:
                                    # 메시지 값 파싱
                                    if isinstance(message.value, dict):
                                        status = message.value
                                    elif isinstance(message.value, str):
                                        status = json.loads(message.value)
                                    elif hasattr(message.value, "decode"):
                                        status = json.loads(
                                            message.value.decode("utf-8")
                                        )
                                    else:
                                        status = message.value

                                    # 키에서 group_id 추출 (group_id:hostname:pid)
                                    key = ""
                                    if message.key:
                                        if isinstance(message.key, bytes):
                                            key = message.key.decode("utf-8")
                                        else:
                                            key = str(message.key)

                                    # group_id로 시작하는 키만 필터링 (같은 group_id의 Consumer만)
                                    if key.startswith(f"{self.group_id}:"):
                                        # 최신 상태 업데이트
                                        self.latest_status = status
                                        # 로그 레벨을 DEBUG로 변경 (너무 많은 로그 방지)
                                        logger.debug(
                                            f"✅ 상태 업데이트: {status.get('processed_count', 0)}개 처리, "
                                            f"{status.get('num_partitions', 0)}개 파티션, "
                                            f"소비율: {status.get('messages_per_second', 0.0):.2f} msg/s, "
                                            f"PID: {status.get('pid', 'N/A')}"
                                        )
                                    else:
                                        logger.debug(
                                            f"다른 group_id 메시지 무시: key={key}, "
                                            f"기대 group_id={self.group_id}"
                                        )
                                except json.JSONDecodeError as e:
                                    logger.warning(
                                        f"상태 메시지 JSON 파싱 오류: {e}, value={message.value}"
                                    )
                                except Exception as e:
                                    logger.warning(
                                        f"상태 메시지 파싱 오류: {e}", exc_info=True
                                    )

                    except Exception as e:
                        logger.warning(f"상태 메시지 폴링 오류: {e}", exc_info=True)
                        # 폴링 오류 시 Consumer 연결 상태 확인
                        if (
                            not self.status_consumer
                            or not self.status_consumer.consumer
                        ):
                            logger.warning(
                                "Consumer 연결이 끊어졌습니다. 재연결 시도..."
                            )
                            break  # 외부 while 루프로 돌아가서 재연결
                        time.sleep(1)

            except Exception as e:
                logger.error(f"상태 Consumer 루프 오류: {e}", exc_info=True)
                logger.info(f"{reconnect_delay}초 후 재연결 시도...")
                time.sleep(reconnect_delay)
                consecutive_failures += 1

    def execute(self, command: str, params: Optional[dict] = None) -> dict:
        """
        명령어 실행

        지원 명령어:
        - start_consumer: Consumer 시작
        - stop_consumer: Consumer 중지
        - restart_consumer: Consumer 재시작
        - get_status: Consumer 상태 조회
        - get_stats: Consumer 통계 조회
        - get_consumer_groups: Consumer Groups 상태 조회
        - get_logs: Consumer 로그 조회
        - get_topics: 구독 가능한 토픽 목록 조회 (미구현)
        """
        params = params or {}

        if command == "start_consumer":
            success = self.start()
            return {"success": success, "status": self.status}

        elif command == "stop_consumer":
            success = self.stop()
            return {"success": success, "status": self.status}

        elif command == "restart_consumer":
            success = self.restart()
            return {"success": success, "status": self.status}

        elif command == "get_status":
            # Kafka 토픽에서 최신 상태 가져오기 (우선순위)
            # latest_status가 있고 running=True면 정상 연결 상태
            if self.latest_status and self.latest_status.get("running", False):
                # Kafka 토픽에서 상태 정보 사용
                status = self.latest_status
                is_running = True
                service_connected = True
                service_status = "running"
                pid = status.get("pid")
                logger.debug(
                    f"get_status: Kafka 토픽에서 상태 조회 (running=True, pid={pid})"
                )
            elif self.consumer_process:
                # 프로세스는 실행 중이지만 Kafka 토픽에서 상태를 받지 못한 경우
                is_running = self.consumer_process.poll() is None
                service_connected = False
                service_status = "unknown"
                pid = self.consumer_process.pid if is_running else None
                logger.debug(
                    f"get_status: 프로세스 실행 중이지만 상태 토픽에서 정보 없음 "
                    f"(pid={pid}, latest_status={bool(self.latest_status)})"
                )
            else:
                # 프로세스가 없는 경우
                is_running = False
                service_connected = False
                service_status = "stopped"
                pid = None
                logger.debug("get_status: 프로세스 없음")

            return {
                "success": True,
                "running": is_running,
                "connected": service_connected,  # 실제 Kafka 연결 상태
                "service_status": service_status,  # 서비스 상태 (running/error/unknown/stopped)
                "pid": pid,
                "status": "running" if is_running else "stopped",
            }

        elif command == "get_stats":
            # 캐시 확인 (5초 TTL)
            current_time = time.time()
            if (
                self._stats_cache is not None
                and (current_time - self._stats_cache_time) < self._cache_ttl
            ):
                return self._stats_cache

            # Consumer 통계 조회
            # Kafka 토픽에서만 상태 가져오기 (Single Source of Truth)
            stats = {
                "success": True,
                "processed_count": 0,
                "error_count": 0,
                "messages_per_second": 0.0,
                "topics": self.topics,
                "group_id": self.group_id,
                "status": self.status,
                "consumer_groups": {},
            }

            # Kafka 토픽에서 최신 상태 가져오기
            if self.latest_status and self.latest_status.get("running"):
                status = self.latest_status
                stats["processed_count"] = status.get("processed_count", 0)
                stats["error_count"] = status.get("error_count", 0)
                stats["messages_per_second"] = status.get("messages_per_second", 0.0)

                # Consumer Groups 정보
                consumer_groups = {
                    "subscription": status.get("subscription", []),
                    "num_partitions": status.get("num_partitions", 0),
                }
                stats["consumer_groups"] = consumer_groups

                logger.debug("Kafka 토픽에서 상태 조회 완료")
            else:
                # Kafka 토픽에서 상태를 받지 못한 경우 (프로세스는 실행 중일 수 있음)
                if self.consumer_process and self.consumer_process.poll() is None:
                    logger.debug(
                        "프로세스는 실행 중이지만 Kafka 토픽에서 상태를 받지 못함 "
                        "(재연결 대기 중일 수 있음)"
                    )
                # 기본값 반환 (processed_count=0, error_count=0 등)

            # 캐시 업데이트
            self._stats_cache = stats
            self._stats_cache_time = current_time

            return stats

        elif command == "get_consumer_groups":
            # 캐시 확인 (5초 TTL)
            current_time = time.time()
            if (
                self._consumer_groups_cache is not None
                and (current_time - self._consumer_groups_cache_time) < self._cache_ttl
            ):
                return self._consumer_groups_cache

            # Consumer Groups 상태 조회
            # Kafka 토픽에서 최신 상태 가져오기 (단일 소스 - 로그 파일 파싱 제거)
            consumer_groups = {}
            broker_available = True

            # Kafka 토픽에서 최신 상태 확인
            if self.latest_status and self.latest_status.get("running"):
                status = self.latest_status
                consumer_groups = {
                    "subscription": status.get("subscription", []),
                    "num_partitions": status.get("num_partitions", 0),
                }
                broker_available = True
                logger.debug("Kafka 토픽에서 Consumer Groups 조회 완료")
            else:
                # 브로커가 실행 중인지 확인
                from gui.modules.managers.kafka_manager import KafkaManager

                kafka_manager = KafkaManager()
                broker_available = kafka_manager.check_broker_running()
                if not broker_available:
                    logger.debug(
                        "Kafka 브로커가 실행 중이 아니므로 Consumer Groups 조회를 건너뜁니다"
                    )

            result = {
                "success": True,
                "consumer_groups": consumer_groups,
                "group_id": self.group_id,
                "broker_available": broker_available,
            }
            # 캐시 업데이트
            self._consumer_groups_cache = result
            self._consumer_groups_cache_time = current_time
            return result

        elif command == "get_logs":
            limit = params.get("limit", 100)
            if self.consumer_process and self.consumer_process.poll() is None:
                process_id = f"kafka_consumer_{self.consumer_process.pid}"
                from gui.modules.process_monitor import get_monitor

                monitor = get_monitor()
                logs = monitor.get_logs(process_id, limit=limit)
                return {"success": True, "logs": logs}
            return {"success": True, "logs": []}

        elif command == "get_topics":
            # 구독 가능한 토픽 목록 조회 (Kafka AdminClient를 통한 방법)
            try:
                from kafka import KafkaAdminClient
                import re

                # AdminClient를 생성하여 토픽 목록 조회
                admin_client = KafkaAdminClient(
                    bootstrap_servers=self.bootstrap_servers,
                    client_id="kafka_module_topic_lister",
                )

                # 모든 토픽 목록 조회
                topics_list = list(admin_client.list_topics())

                # 패턴 매칭 (cointicker.raw.*)
                matching_topics = []
                for pattern in self.topics:
                    # 와일드카드 패턴을 정규식으로 변환
                    pattern_regex = (
                        pattern.replace(".", r"\.").replace("*", ".*").replace("?", ".")
                    )
                    compiled_pattern = re.compile(pattern_regex)

                    for topic in topics_list:
                        if compiled_pattern.match(topic):
                            if topic not in matching_topics:
                                matching_topics.append(topic)

                admin_client.close()

                return {
                    "success": True,
                    "all_topics": topics_list,
                    "matching_topics": matching_topics,
                    "subscribed_patterns": self.topics,
                }
            except Exception as e:
                logger.error(f"토픽 목록 조회 실패: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "all_topics": [],
                    "matching_topics": [],
                    "subscribed_patterns": self.topics,
                }

        else:
            return {"success": False, "error": f"Unknown command: {command}"}

    def get_info(self) -> dict:
        """모듈 정보 조회"""
        status_info = self.execute("get_status")
        return {
            "name": self.name,
            "status": status_info.get("status", "unknown"),
            "bootstrap_servers": self.bootstrap_servers,
            "topics": self.topics,
            "group_id": self.group_id,
            "consumer_path": str(self.consumer_path),
        }
