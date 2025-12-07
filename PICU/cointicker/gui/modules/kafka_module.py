"""
Kafka 모듈
Kafka Producer/Consumer를 관리하는 모듈
"""

import subprocess
import signal
import os
import time
from typing import Dict, Any, Optional
from pathlib import Path

from gui.core.module_manager import ModuleInterface
from shared.logger import setup_logger

logger = setup_logger(__name__)


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
        self.consumer_process: Optional[subprocess.Popen] = None
        self.bootstrap_servers = ["localhost:9092"]
        self.topics = ["cointicker.raw.*"]
        self.group_id = "cointicker-consumer"

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
                        logger.warning(
                            f"같은 group_id({self.group_id})로 실행 중인 Kafka Consumer 발견 (PID: {proc.info['pid']})"
                        )
                        # 기존 프로세스를 추적하도록 설정
                        # (이미 실행 중인 프로세스는 모니터링만 시작)
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

            self.consumer_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(cointicker_root.resolve()),  # 프로젝트 루트를 작업 디렉토리로
                env=env,  # PYTHONPATH가 설정된 환경 변수 사용
                universal_newlines=True,
                bufsize=1,
            )

            # 프로세스 모니터링 시작
            process_id = f"kafka_consumer_{self.consumer_process.pid}"
            from gui.modules.process_monitor import get_monitor

            monitor = get_monitor()
            monitor.start_monitoring(process_id, self.consumer_process)

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

    def execute(self, command: str, params: dict = None) -> dict:
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
            if self.consumer_process:
                is_running = self.consumer_process.poll() is None

                # 프로세스 모니터에서 실제 서비스 상태 확인
                service_connected = False
                service_status = "unknown"
                if is_running:
                    process_id = f"kafka_consumer_{self.consumer_process.pid}"
                    from gui.modules.process_monitor import get_monitor

                    monitor = get_monitor()
                    process_stats = monitor.get_stats(process_id)

                    if process_stats:
                        service_connected = process_stats.get("connected", False)
                        service_status = process_stats.get("service_status", "unknown")

                return {
                    "success": True,
                    "running": is_running,
                    "connected": service_connected,  # 실제 Kafka 연결 상태
                    "service_status": service_status,  # 서비스 상태 (running/error/unknown)
                    "pid": self.consumer_process.pid if is_running else None,
                    "status": "running" if is_running else "stopped",
                }
            else:
                return {
                    "success": True,
                    "running": False,
                    "connected": False,
                    "service_status": "stopped",
                    "status": "stopped",
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

            # 프로세스가 실행 중이면 로그에서 통계 추출
            if self.consumer_process and self.consumer_process.poll() is None:
                process_id = f"kafka_consumer_{self.consumer_process.pid}"
                from gui.modules.process_monitor import get_monitor

                monitor = get_monitor()
                process_stats = monitor.get_stats(process_id)

                if process_stats:
                    stats["processed_count"] = process_stats.get("items_processed", 0)
                    stats["error_count"] = process_stats.get("errors", 0)
                    stats["warnings"] = process_stats.get("warnings", 0)
                    stats["start_time"] = process_stats.get("start_time")
                    stats["last_update"] = process_stats.get("last_update")
                    # 메시지 소비율은 로그에서 추출 (실시간 통계는 Consumer 서비스에서 제공)
                    stats["messages_per_second"] = process_stats.get(
                        "messages_per_second", 0.0
                    )
                    stats["consumer_groups"] = process_stats.get("consumer_groups", {})

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
            # 0. 브로커가 실행 중인지 먼저 확인 (브로커가 없으면 연결 시도하지 않음)
            from gui.modules.managers.kafka_manager import KafkaManager

            kafka_manager = KafkaManager()
            if not kafka_manager.check_broker_running():
                logger.debug(
                    "Kafka 브로커가 실행 중이 아니므로 Consumer Groups 조회를 건너뜁니다"
                )
                result = {
                    "success": True,
                    "consumer_groups": {},
                    "group_id": self.group_id,
                    "broker_available": False,
                }
                # 브로커 없을 때도 캐시 (불필요한 체크 반복 방지)
                self._consumer_groups_cache = result
                self._consumer_groups_cache_time = current_time
                return result

            # 1. process_monitor에서 파싱된 정보 먼저 확인
            consumer_groups = {}
            process_monitor_has_info = False
            if self.consumer_process and self.consumer_process.poll() is None:
                process_id = f"kafka_consumer_{self.consumer_process.pid}"
                from gui.modules.process_monitor import get_monitor

                monitor = get_monitor()
                process_stats = monitor.get_stats(process_id)

                if process_stats:
                    consumer_groups = process_stats.get("consumer_groups", {})
                    # process_monitor에 정보가 있으면 (파티션 정보 포함) 그대로 사용
                    # 임시 Consumer를 생성하지 않음 (성능 개선)
                    if consumer_groups and (
                        consumer_groups.get("subscription")
                        or consumer_groups.get("num_partitions", 0) > 0
                    ):
                        process_monitor_has_info = True
                        result = {
                            "success": True,
                            "consumer_groups": consumer_groups,
                            "group_id": self.group_id,
                            "broker_available": True,
                        }
                        # 캐시 업데이트
                        self._consumer_groups_cache = result
                        self._consumer_groups_cache_time = current_time
                        return result
                    # process_monitor에 정보가 있지만 불완전한 경우에도 최소한의 정보 반환
                    elif consumer_groups:
                        process_monitor_has_info = True
                        # 최소한의 정보라도 반환 (빈 딕셔너리보다 나음)
                        result = {
                            "success": True,
                            "consumer_groups": consumer_groups,
                            "group_id": self.group_id,
                            "broker_available": True,
                        }
                        # 캐시 업데이트
                        self._consumer_groups_cache = result
                        self._consumer_groups_cache_time = current_time
                        return result

            # 2. process_monitor에 정보가 없거나 불완전한 경우에만 KafkaConsumerClient를 통해 직접 조회
            # 단, 실제 Consumer 프로세스가 실행 중이면 임시 Consumer 생성을 건너뜀 (성능 개선)
            # (실행 중인 Consumer 프로세스가 없을 때만 임시 Consumer 생성)
            # 단, process_monitor에 정보가 있지만 불완전한 경우는 이미 위에서 반환했으므로 여기서는 건너뜀
            if (
                not process_monitor_has_info
                and (not consumer_groups or not consumer_groups.get("subscription"))
                and (
                    not self.consumer_process
                    or self.consumer_process.poll() is not None
                )
            ):
                # Consumer 프로세스가 실행 중이 아니면 임시 Consumer 생성 (정보 조회용)
                try:
                    from shared.kafka_client import KafkaConsumerClient

                    # Consumer 클라이언트 생성 (연결 없이 정보만 조회)
                    consumer_client = KafkaConsumerClient(
                        bootstrap_servers=self.bootstrap_servers,
                        group_id=self.group_id,
                    )

                    # Consumer가 이미 연결되어 있으면 직접 조회
                    if consumer_client.consumer:
                        consumer_groups = consumer_client.get_consumer_groups()
                    else:
                        # Consumer가 없으면 연결 시도 (정보 조회용)
                        # 단, 브로커가 없으면 연결 시도하지 않음 (이미 위에서 확인)
                        try:
                            if consumer_client.connect(
                                self.topics, max_retries=1, retry_delay=0.5
                            ):
                                consumer_groups = consumer_client.get_consumer_groups()
                                consumer_client.close()
                        except Exception as connect_error:
                            # 연결 실패는 정상 (브로커가 없거나 일시적 문제)
                            logger.debug(
                                f"Kafka Consumer 연결 실패 (정상): {connect_error}"
                            )
                except Exception as e:
                    logger.debug(
                        f"KafkaConsumerClient를 통한 Consumer Groups 조회 실패: {e}"
                    )
            elif (
                not process_monitor_has_info
                and self.consumer_process
                and self.consumer_process.poll() is None
            ):
                # Consumer 프로세스가 실행 중이지만 process_monitor에 정보가 없는 경우
                # 최소한 프로세스가 실행 중이라는 정보라도 반환 (빈 딕셔너리보다 나음)
                if not consumer_groups:
                    consumer_groups = {}
                # Consumer 프로세스가 실행 중이면 최소한의 정보 반환
                logger.debug(
                    f"Consumer 프로세스 실행 중 (PID: {self.consumer_process.pid})이지만 "
                    f"process_monitor에 정보가 없습니다. 로그 파싱 대기 중..."
                )

            result = {
                "success": True,
                "consumer_groups": consumer_groups if consumer_groups else {},
                "group_id": self.group_id,
                "broker_available": True,
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
            # 구독 가능한 토픽 목록 조회 (Kafka Consumer를 통한 간단한 방법)
            try:
                from kafka import KafkaConsumer
                import re

                # Consumer를 생성하여 토픽 목록 조회
                consumer = KafkaConsumer(
                    bootstrap_servers=self.bootstrap_servers, consumer_timeout_ms=5000
                )

                # 모든 토픽 목록 조회
                all_topics = consumer.list_topics(timeout=5)
                topics_list = list(all_topics.topics.keys()) if all_topics else []

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

                consumer.close()

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
