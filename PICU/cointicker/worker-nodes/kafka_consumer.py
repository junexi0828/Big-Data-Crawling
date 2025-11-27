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
from typing import Optional, Callable

# 공통 라이브러리 import
# kafka_consumer.py 위치: cointicker/worker-nodes/kafka_consumer.py
# shared 위치: cointicker/shared
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent  # worker-nodes -> cointicker
shared_path = project_root / "shared"
sys.path.insert(0, str(shared_path))

from shared.kafka_client import KafkaConsumerClient
from shared.hdfs_client import HDFSClient
from shared.logger import setup_logger

logger = setup_logger(__name__)


class KafkaConsumerService:
    """Kafka Consumer 서비스"""

    def __init__(
        self,
        bootstrap_servers: list = None,
        topics: list = None,
        group_id: str = "cointicker-consumer",
        hdfs_namenode: str = None,
    ):
        """
        Kafka Consumer 서비스 초기화

        Args:
            bootstrap_servers: Kafka 브로커 주소 리스트
            topics: 구독할 토픽 리스트
            group_id: Consumer Group ID
            hdfs_namenode: HDFS NameNode 주소
        """
        self.bootstrap_servers = bootstrap_servers or ["localhost:9092"]
        self.topics = topics or ["cointicker.raw.*"]
        self.group_id = group_id
        self.hdfs_namenode = hdfs_namenode or "hdfs://localhost:9000"

        self.consumer = None
        self.hdfs_client = None
        self.running = False
        self.processed_count = 0
        self.error_count = 0

        # HDFS 클라이언트 초기화
        try:
            self.hdfs_client = HDFSClient(namenode=self.hdfs_namenode)
            logger.info(f"HDFS Client initialized: {self.hdfs_namenode}")
        except Exception as e:
            logger.error(f"Failed to initialize HDFS client: {e}")

    def start(self):
        """Consumer 서비스 시작"""
        try:
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

            self.running = True
            logger.info(
                f"Kafka Consumer Service started. Topics: {self.topics}, "
                f"Group: {self.group_id}"
            )

            # 시그널 핸들러 등록
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)

            # 메시지 소비 시작
            self.consumer.consume(callback=self._process_message)

            return True

        except Exception as e:
            logger.error(f"Error starting Kafka Consumer Service: {e}")
            return False

    def stop(self):
        """Consumer 서비스 중지"""
        self.running = False
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

            # 통계 로깅 (100개마다)
            if self.processed_count % 100 == 0:
                logger.info(
                    f"Processed {self.processed_count} messages "
                    f"(Errors: {self.error_count})"
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
        """HDFS에 데이터 저장"""
        try:
            # 로컬 임시 파일에 저장
            from shared.utils import get_timestamp, get_date_path
            import tempfile

            timestamp = get_timestamp()
            date_path = get_date_path("data/temp", datetime.now())
            date_path.mkdir(parents=True, exist_ok=True)

            local_file = date_path / f"{source}_{timestamp}.json"

            with open(local_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            # HDFS 경로 생성
            hdfs_path = self.hdfs_client.get_raw_path(source, datetime.now())

            # HDFS 디렉토리 생성
            if not self.hdfs_client.exists(hdfs_path):
                self.hdfs_client.mkdir(hdfs_path)

            # HDFS에 업로드
            hdfs_file = f"{hdfs_path}/{local_file.name}"
            success = self.hdfs_client.put(str(local_file), hdfs_file)

            if success:
                logger.debug(f"Saved to HDFS: {hdfs_file}")
                # 로컬 임시 파일 삭제
                local_file.unlink()
            else:
                logger.error(f"Failed to save to HDFS: {hdfs_file}")

        except Exception as e:
            logger.error(f"Error saving to HDFS: {e}")


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
