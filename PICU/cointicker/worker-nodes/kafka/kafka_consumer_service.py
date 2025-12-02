"""
Kafka Consumer 서비스를 systemd 서비스로 실행하기 위한 래퍼
"""

import sys
import os
from pathlib import Path

# 통합 경로 설정 유틸리티 사용
try:
    from shared.path_utils import setup_pythonpath
    setup_pythonpath()
except ImportError:
    # Fallback: 유틸리티 로드 실패 시 하드코딩 경로 사용
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

from worker_nodes.kafka_consumer import KafkaConsumerService
from shared.logger import setup_logger
import yaml

logger = setup_logger(__name__)


def load_config():
    """설정 파일 로드"""
    config_path = project_root / "config" / "kafka_config.yaml"

    if not config_path.exists():
        logger.warning(f"Config file not found: {config_path}, using defaults")
        return None

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return None


def main():
    """메인 함수"""
    config = load_config()

    # 기본값 설정
    bootstrap_servers = ["localhost:9092"]
    topics = ["cointicker.raw.*"]
    group_id = "cointicker-consumer"
    hdfs_namenode = "hdfs://localhost:9000"

    # 설정 파일에서 값 가져오기
    if config and "kafka" in config:
        kafka_config = config["kafka"]

        if "bootstrap_servers" in kafka_config:
            bootstrap_servers = kafka_config["bootstrap_servers"]

        if "topics" in kafka_config:
            topics = []
            if "raw_prefix" in kafka_config["topics"]:
                topics.append(f"{kafka_config['topics']['raw_prefix']}.*")

        if "consumer" in kafka_config:
            consumer_config = kafka_config["consumer"]
            if "group_id" in consumer_config:
                group_id = consumer_config["group_id"]

    # 환경 변수로 오버라이드
    if os.getenv("KAFKA_BOOTSTRAP_SERVERS"):
        bootstrap_servers = [
            s.strip() for s in os.getenv("KAFKA_BOOTSTRAP_SERVERS").split(",")
        ]

    if os.getenv("KAFKA_TOPICS"):
        topics = os.getenv("KAFKA_TOPICS").split(",")

    if os.getenv("KAFKA_GROUP_ID"):
        group_id = os.getenv("KAFKA_GROUP_ID")

    if os.getenv("HDFS_NAMENODE"):
        hdfs_namenode = os.getenv("HDFS_NAMENODE")

    # Consumer 서비스 생성 및 시작
    service = KafkaConsumerService(
        bootstrap_servers=bootstrap_servers,
        topics=topics,
        group_id=group_id,
        hdfs_namenode=hdfs_namenode,
    )

    try:
        service.start()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    finally:
        service.stop()


if __name__ == "__main__":
    main()
