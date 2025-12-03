"""
Kafka Producer Pipeline
Scrapy Spider에서 수집한 데이터를 Kafka로 전송
"""

import json
import logging
from datetime import datetime
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem

# 공통 라이브러리 import
import sys
from pathlib import Path as PathLib

# 통합 경로 설정 유틸리티 사용
try:
    from shared.path_utils import setup_pythonpath
    setup_pythonpath()
except ImportError:
    # Fallback: 유틸리티 로드 실패 시 하드코딩 경로 사용
    current_file = PathLib(__file__).resolve()
    project_root = current_file.parent.parent.parent.parent
    shared_path = project_root / "shared"
    sys.path.insert(0, str(shared_path))

from shared.kafka_client import KafkaProducerClient
from shared.logger import setup_logger

logger = setup_logger(__name__)


class KafkaPipeline:
    """Kafka Producer Pipeline"""

    def __init__(self):
        self.producer = None
        self.items = []
        self.batch_size = 10  # 배치 크기
        self.topic_prefix = "cointicker"

    def open_spider(self, spider):
        """Spider 시작 시 Kafka Producer 초기화"""
        try:
            # 설정에서 Kafka 정보 가져오기
            bootstrap_servers = spider.settings.get(
                "KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"
            )
            if isinstance(bootstrap_servers, str):
                bootstrap_servers = [s.strip() for s in bootstrap_servers.split(",")]

            self.topic_prefix = spider.settings.get("KAFKA_TOPIC_PREFIX", "cointicker")

            # Producer 초기화
            self.producer = KafkaProducerClient(
                bootstrap_servers=bootstrap_servers,
                timeout=10,
            )

            if not self.producer.connect():
                logger.error("Failed to connect Kafka Producer")
                self.producer = None
            else:
                logger.info(f"Kafka Pipeline initialized for {spider.name}")

        except Exception as e:
            logger.error(f"Failed to initialize Kafka Producer: {e}")
            self.producer = None

    def close_spider(self, spider):
        """Spider 종료 시 배치 데이터 전송"""
        if self.items:
            self._send_batch(spider)
        if self.producer:
            self.producer.flush()
            self.producer.close()
        logger.info(f"Kafka Pipeline closed for {spider.name}")

    def process_item(self, item, spider):
        """아이템 처리"""
        if not self.producer:
            # Kafka가 없어도 다른 파이프라인은 계속 진행
            return item

        adapter = ItemAdapter(item)

        # 아이템을 딕셔너리로 변환
        item_dict = dict(adapter)

        # 메타데이터 추가
        item_dict["_spider"] = spider.name
        item_dict["_collected_at"] = datetime.now().isoformat()

        self.items.append(item_dict)

        # 배치 크기 도달 시 전송
        if len(self.items) >= self.batch_size:
            self._send_batch(spider)
            self.items = []

        return item

    def _send_batch(self, spider):
        """배치 데이터를 Kafka로 전송"""
        if not self.producer or not self.items:
            return

        try:
            # 토픽 이름 생성 (예: cointicker.raw.upbit_trends)
            topic = f"{self.topic_prefix}.raw.{spider.name}"

            success_count = 0
            for item in self.items:
                # 키 생성 (source + timestamp)
                key = f"{item.get('source', 'unknown')}_{item.get('timestamp', '')}"

                if self.producer.send(topic, item, key=key):
                    success_count += 1
                else:
                    logger.warning(
                        f"Failed to send item to Kafka: {item.get('title', 'N/A')[:50]}"
                    )

            logger.info(
                f"Sent {success_count}/{len(self.items)} items to Kafka topic: {topic}"
            )

            # 전송 성공한 아이템만 제거
            self.items = []

        except Exception as e:
            logger.error(f"Error sending batch to Kafka: {e}")
