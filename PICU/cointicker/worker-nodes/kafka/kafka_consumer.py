"""
Kafka Consumer 서비스
Kafka에서 데이터를 수신하여 처리하는 백그라운드 서비스
"""

import json
import time
import signal
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Callable, Dict, Any

# --- 중앙 경로 관리 시스템을 사용하기 위한 부트스트랩 ---
# 이 스크립트가 직접 실행될 때 'shared' 같은 공통 모듈을 찾을 수 있도록,
# 먼저 'cointicker' 프로젝트 루트를 수동으로 찾아 Python 경로에 추가합니다.
try:
    # 현재 파일 위치: cointicker/worker-nodes/kafka/kafka_consumer.py
    # 세 단계 위로 올라가면 'cointicker' 디렉토리입니다.
    project_root = Path(__file__).resolve().parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    # 이제 경로가 설정되었으므로, 중앙 관리 유틸리티를 호출하여
    # 일관성 있게 전체 파이썬 경로와 하둡 환경을 설정합니다.
    from shared.path_utils import setup_pythonpath, setup_hadoop_env
    setup_pythonpath()
    setup_hadoop_env(verbose=True) # HADOOP_HOME 등의 설정을 로그에 출력합니다.

except ImportError:
    # 이 블록이 실행된다면, 프로젝트 구조가 예상과 다르다는 의미이므로
    # 심각한 오류로 간주하고 실행을 중단합니다.
    print(f"FATAL: 파이썬 경로 설정에 실패했습니다. 'shared' 모듈을 찾을 수 없습니다.", file=sys.stderr)
    sys.exit(1)

from shared.kafka_client import KafkaConsumerClient, KafkaProducerClient
from shared.hdfs_client import HDFSClient
from shared.hdfs_upload_manager import HDFSUploadManager
from shared.logger import setup_logger
from shared.path_utils import get_cointicker_root
import socket
import os
import threading

# 로그 파일 경로 설정
cointicker_root = get_cointicker_root()
log_file = str(cointicker_root / "logs" / "kafka_consumer.log")
logger = setup_logger(__name__, log_file=log_file)


class KafkaConsumerService:
    """Kafka Consumer 서비스 (자동 재업로드 기능 포함)"""

    def __init__(
        self,
        bootstrap_servers: list = None,
        topics: list = None,
        group_id: str = "cointicker-consumer",
        hdfs_namenode: str = None,
        hdfs_max_retries: int = 3,
        hdfs_initial_delay: float = 2.0,
        hdfs_backoff_factor: float = 2.0,
        hdfs_health_check_interval: int = 300,
    ):
        """
        Kafka Consumer 서비스 초기화

        Args:
            bootstrap_servers: Kafka 브로커 주소 리스트
            topics: 구독할 토픽 리스트
            group_id: Consumer Group ID
            hdfs_namenode: HDFS NameNode 주소
            hdfs_max_retries: HDFS 최대 재시도 횟수
            hdfs_initial_delay: HDFS 초기 재시도 지연 시간 (초)
            hdfs_backoff_factor: HDFS 재시도 간격 증가 배수
            hdfs_health_check_interval: HDFS 상태 확인 간격 (초)
        """
        self.bootstrap_servers = bootstrap_servers or ["localhost:9092"]
        self.topics = topics or ["cointicker.raw.*"]
        self.group_id = group_id
        self.hdfs_namenode = hdfs_namenode or "hdfs://localhost:9000"

        self.consumer = None
        self.status_producer = None  # 상태 발행용 Producer
        self.hdfs_client = None
        self.upload_manager = None
        self.running = False
        self.processed_count = 0
        self.error_count = 0

        # 메시지 소비율 추적
        import time
        self._start_time = None
        self._last_message_time = None
        self._messages_per_second = 0.0
        self._last_processed_count = 0
        self._last_rate_calc_time = time.time()

        # 상태 발행 관련
        self._status_publish_interval = 5.0  # 5초마다 상태 발행
        self._status_publish_thread = None
        self._status_topic = "cointicker.consumer.status"  # 상태 토픽

        # HDFS 클라이언트 초기화
        try:
            self.hdfs_client = HDFSClient(namenode=self.hdfs_namenode)
            logger.info(f"HDFS Client initialized: {self.hdfs_namenode}")

            # HDFS 업로드 매니저 초기화
            self.upload_manager = HDFSUploadManager(
                hdfs_client=self.hdfs_client,
                temp_dir="data/temp",
                max_retries=hdfs_max_retries,
                initial_delay=hdfs_initial_delay,
                backoff_factor=hdfs_backoff_factor,
                health_check_interval=hdfs_health_check_interval,
            )
            logger.info("HDFS 업로드 매니저 초기화 완료")
        except Exception as e:
            logger.error(f"Failed to initialize HDFS client: {e}")

    def start(self):
        """Consumer 서비스 시작"""
        try:
            logger.info(
                f"Starting Kafka Consumer Service. Topics: {self.topics}, "
                f"Group: {self.group_id}, Bootstrap servers: {self.bootstrap_servers}"
            )

            # Consumer 연결
            self.consumer = KafkaConsumerClient(
                bootstrap_servers=self.bootstrap_servers,
                group_id=self.group_id,
                auto_offset_reset="earliest",
                enable_auto_commit=True,
            )

            if not self.consumer.connect(self.topics):
                logger.error("Failed to connect Kafka Consumer")
                return False

            # 구독 상태 확인
            # 주의: 패턴 기반 구독에서는 poll() 호출 전까지 subscription()이 빈 set을 반환할 수 있음
            # 따라서 빈 subscription은 에러가 아니라 정상 상태임
            if self.consumer.consumer:
                subscription = self.consumer.consumer.subscription()
                logger.info(f"Consumer subscription confirmed: {subscription}")

                # 패턴 구독인 경우, 첫 poll() 후에 실제 토픽이 할당됨
                # 빈 subscription은 패턴 구독에서는 정상임
                if not subscription:
                    logger.info(
                        "Consumer subscription is empty (normal for pattern-based subscription). "
                        "Topics will be assigned after first poll()."
                    )

            self.running = True
            self._start_time = time.time()
            self._last_message_time = None
            self._messages_per_second = 0.0
            self._last_processed_count = 0
            self._last_rate_calc_time = time.time()

            # 자동 업로드 시작
            if self.upload_manager:
                self.upload_manager.start_auto_upload()
                logger.info("HDFS auto-upload started")

            # 상태 발행용 Producer 초기화
            try:
                self.status_producer = KafkaProducerClient(
                    bootstrap_servers=self.bootstrap_servers,
                    timeout=5,
                )
                if self.status_producer.connect():
                    logger.info("상태 발행 Producer 연결 완료")
                    # 초기 상태 발행
                    self._publish_status()
                    # 주기적 상태 발행 스레드 시작
                    self._status_publish_thread = threading.Thread(
                        target=self._status_publish_loop,
                        daemon=True,
                    )
                    self._status_publish_thread.start()
                else:
                    logger.warning("상태 발행 Producer 연결 실패 (계속 진행)")
                    self.status_producer = None
            except Exception as e:
                logger.warning(f"상태 발행 Producer 초기화 실패 (계속 진행): {e}")
                self.status_producer = None

            logger.info(
                f"✅ Kafka Consumer Service started successfully. Topics: {self.topics}, "
                f"Group: {self.group_id}"
            )
            # 연결 성공 로그 (GUI에서 파싱하기 위해)
            logger.info(f"Kafka Consumer connected and ready to consume messages")

            # 시그널 핸들러 등록
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)

            # 메시지 소비 시작 (블로킹 호출)
            logger.info("Starting message consumption loop...")
            self.consumer.consume(callback=self._process_message)

            return True

        except Exception as e:
            logger.error(f"Error starting Kafka Consumer Service: {e}", exc_info=True)
            return False

    def stop(self):
        """Consumer 서비스 중지"""
        self.running = False

        # 상태 발행 중지
        if self.status_producer:
            try:
                # 마지막 상태 발행 (종료 상태)
                self._publish_status(is_shutting_down=True)
                self.status_producer.close()
            except Exception as e:
                logger.debug(f"상태 발행 Producer 종료 중 오류 (무시): {e}")

        # 자동 업로드 중지
        if self.upload_manager:
            self.upload_manager.stop_auto_upload()

        if self.consumer:
            self.consumer.close()
        logger.info(
            f"Kafka Consumer Service stopped. "
            f"Processed: {self.processed_count}, Errors: {self.error_count}"
        )

    def _signal_handler(self, signum, frame):
        """시그널 핸들러"""
        logger.info(f"Received signal {signum}, stopping consumer...")
        self.stop()
        sys.exit(0)

    def _process_message(self, message):
        """메시지 처리"""
        try:
            topic = message.topic
            key = message.key
            value = message.value

            logger.debug(
                f"Received message: topic={topic}, partition={message.partition}, "
                f"offset={message.offset}, key={key}"
            )

            # 메시지 값이 딕셔너리인 경우
            if isinstance(value, dict):
                data = value
            elif isinstance(value, str):
                data = json.loads(value)
            else:
                logger.warning(f"Unexpected message value type: {type(value)}")
                self.error_count += 1
                return

            # 데이터 처리
            self._handle_data(topic, data)

            self.processed_count += 1
            self._last_message_time = time.time()

            # 메시지 소비율 계산 (1초마다)
            current_time = time.time()
            time_diff = current_time - self._last_rate_calc_time
            if time_diff >= 1.0:
                count_diff = self.processed_count - self._last_processed_count
                self._messages_per_second = count_diff / time_diff if time_diff > 0 else 0.0
                self._last_processed_count = self.processed_count
                self._last_rate_calc_time = current_time

            # 통계 로깅 (100개마다)
            if self.processed_count % 100 == 0:
                logger.info(
                    f"Processed {self.processed_count} messages "
                    f"(Errors: {self.error_count}, Rate: {self._messages_per_second:.2f} msg/s)"
                )

        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            self.error_count += 1
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            self.error_count += 1

    def _handle_data(self, topic: str, data: dict):
        """
        데이터 처리 (HDFS 저장 또는 다른 처리)

        Args:
            topic: Kafka 토픽
            data: 메시지 데이터
        """
        try:
            # 토픽에서 소스 추출 (예: cointicker.raw.upbit_trends -> upbit_trends)
            source = data.get("_spider") or data.get("source", "unknown")

            # HDFS에 저장
            if self.hdfs_client:
                self._save_to_hdfs(source, data)
            else:
                logger.warning("HDFS client not available, skipping save")

        except Exception as e:
            logger.error(f"Error handling data: {e}")

    def _save_to_hdfs(self, source: str, data: dict):
        """HDFS에 데이터 저장 (자동 재업로드 기능 포함)"""
        if not self.upload_manager:
            logger.warning("HDFS 업로드 매니저가 초기화되지 않았습니다.")
            return

        try:
            # 업로드 매니저를 통해 저장 (재시도 로직 포함)
            # 단일 아이템을 리스트로 변환
            success = self.upload_manager.save_to_hdfs(
                items=[data],
                source=source,
                date=datetime.now(),
            )

            if success:
                logger.debug(f"Saved to HDFS (source: {source})")
            else:
                logger.warning(
                    f"Failed to save to HDFS, added to pending list (source: {source})"
                )

        except Exception as e:
            logger.error(f"Error saving to HDFS: {e}")

    def get_stats(self) -> dict:
        """
        Consumer 통계 조회

        Returns:
            통계 정보 딕셔너리
        """
        import time
        current_time = time.time()
        uptime = current_time - self._start_time if self._start_time else 0

        # Consumer Groups 정보
        consumer_groups = {}
        if self.consumer and self.consumer.consumer:
            consumer_groups = self.consumer.get_consumer_groups()

        return {
            "processed_count": self.processed_count,
            "error_count": self.error_count,
            "messages_per_second": self._messages_per_second,
            "uptime_seconds": uptime,
            "running": self.running,
            "consumer_groups": consumer_groups,
            "last_message_time": self._last_message_time,
        }

    def _publish_status(self, is_shutting_down: bool = False):
        """상태를 Kafka 토픽에 발행"""
        if not self.status_producer or not self.running:
            return

        try:
            import time
            from datetime import datetime

            # Consumer Groups 정보 수집
            consumer_groups = {}
            subscription = []
            num_partitions = 0

            if self.consumer and self.consumer.consumer:
                try:
                    consumer_groups = self.consumer.get_consumer_groups()
                    subscription = consumer_groups.get("subscription", [])
                    num_partitions = consumer_groups.get("num_partitions", 0)
                except Exception as e:
                    logger.debug(f"Consumer Groups 정보 조회 실패: {e}")

            # 상태 메시지 구성
            status_message = {
                "hostname": socket.gethostname(),
                "pid": os.getpid(),
                "group_id": self.group_id,
                "topics": self.topics,
                "subscription": subscription,
                "num_partitions": num_partitions,
                "processed_count": self.processed_count,
                "error_count": self.error_count,
                "messages_per_second": self._messages_per_second,
                "running": self.running and not is_shutting_down,
                "uptime_seconds": (
                    time.time() - self._start_time if self._start_time else 0
                ),
                "last_message_time": (
                    datetime.fromtimestamp(self._last_message_time).isoformat()
                    if self._last_message_time
                    else None
                ),
                "timestamp": datetime.now().isoformat(),
            }

            # 상태 발행 (키는 group_id + hostname + pid로 고유성 보장)
            key = f"{self.group_id}:{socket.gethostname()}:{os.getpid()}"
            if self.status_producer.send(self._status_topic, status_message, key=key):
                logger.debug(f"상태 발행 완료: {key}")
            else:
                logger.debug("상태 발행 실패 (Producer 오류)")

        except Exception as e:
            logger.debug(f"상태 발행 중 오류 (무시): {e}")

    def _status_publish_loop(self):
        """주기적 상태 발행 루프"""
        import time

        while self.running:
            try:
                self._publish_status()
                time.sleep(self._status_publish_interval)
            except Exception as e:
                logger.debug(f"상태 발행 루프 오류 (무시): {e}")
                time.sleep(self._status_publish_interval)


def main():
    """메인 함수"""
    import argparse

    parser = argparse.ArgumentParser(description="Kafka Consumer Service")
    parser.add_argument(
        "--bootstrap-servers",
        default="localhost:9092",
        help="Kafka bootstrap servers (comma-separated)",
    )
    parser.add_argument(
        "--topics",
        nargs="+",
        default=["cointicker.raw.*"],
        help="Kafka topics to consume",
    )
    parser.add_argument(
        "--group-id",
        default="cointicker-consumer",
        help="Consumer group ID",
    )
    parser.add_argument(
        "--hdfs-namenode",
        default="hdfs://localhost:9000",
        help="HDFS NameNode address",
    )

    args = parser.parse_args()

    # Bootstrap servers 파싱
    bootstrap_servers = [s.strip() for s in args.bootstrap_servers.split(",")]

    # Consumer 서비스 생성 및 시작
    service = KafkaConsumerService(
        bootstrap_servers=bootstrap_servers,
        topics=args.topics,
        group_id=args.group_id,
        hdfs_namenode=args.hdfs_namenode,
    )

    try:
        service.start()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    finally:
        service.stop()


if __name__ == "__main__":
    main()
