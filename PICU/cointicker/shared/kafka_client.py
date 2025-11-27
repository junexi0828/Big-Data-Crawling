"""
Kafka 클라이언트 유틸리티
Producer와 Consumer를 위한 공통 클라이언트
"""

import json
import logging
from typing import Optional, List, Dict, Any
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
from loguru import logger


class KafkaClient:
    """Kafka 클라이언트 기본 클래스"""

    def __init__(
        self,
        bootstrap_servers: List[str] = None,
        timeout: int = 10,
    ):
        """
        Kafka 클라이언트 초기화

        Args:
            bootstrap_servers: Kafka 브로커 주소 리스트
            timeout: 타임아웃 (초)
        """
        self.bootstrap_servers = bootstrap_servers or ["localhost:9092"]
        self.timeout = timeout
        self.logger = logger

    def _get_servers_str(self) -> str:
        """브로커 서버 주소를 문자열로 변환"""
        return ",".join(self.bootstrap_servers)


class KafkaProducerClient(KafkaClient):
    """Kafka Producer 클라이언트"""

    def __init__(
        self,
        bootstrap_servers: List[str] = None,
        timeout: int = 10,
        value_serializer=None,
        key_serializer=None,
        acks: str = "all",
        retries: int = 3,
        compression_type: str = "gzip",
        linger_ms: int = 100,
    ):
        """
        Kafka Producer 초기화

        Args:
            bootstrap_servers: Kafka 브로커 주소 리스트
            timeout: 타임아웃 (초)
            value_serializer: 값 직렬화 함수
            key_serializer: 키 직렬화 함수
            acks: ACK 설정 ("all", "1", "0")
            retries: 재시도 횟수
            compression_type: 압축 타입 ("gzip", "snappy", "lz4", "zstd", None)
            linger_ms: 배치 전송 전 대기 시간 (밀리초)
        """
        super().__init__(bootstrap_servers, timeout)

        # 기본 직렬화 함수
        if value_serializer is None:
            value_serializer = lambda v: json.dumps(v, ensure_ascii=False).encode(
                "utf-8"
            )
        if key_serializer is None:
            key_serializer = lambda k: k.encode("utf-8") if k else None

        self.producer = None
        self.value_serializer = value_serializer
        self.key_serializer = key_serializer
        self.acks = acks
        self.retries = retries
        self.compression_type = compression_type
        self.linger_ms = linger_ms

    def connect(self) -> bool:
        """Producer 연결"""
        try:
            producer_config = {
                "bootstrap_servers": self.bootstrap_servers,
                "value_serializer": self.value_serializer,
                "key_serializer": self.key_serializer,
                "acks": self.acks,
                "retries": self.retries,
                "request_timeout_ms": self.timeout * 1000,
            }

            # 고급 설정 추가 (kafka_project의 producer.properties 참고)
            if self.compression_type:
                producer_config["compression_type"] = self.compression_type
            if self.linger_ms:
                producer_config["linger_ms"] = self.linger_ms

            self.producer = KafkaProducer(**producer_config)
            self.logger.info(
                f"Kafka Producer connected to {self._get_servers_str()} "
                f"(compression={self.compression_type}, linger_ms={self.linger_ms})"
            )
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect Kafka Producer: {e}")
            return False

    def send(
        self,
        topic: str,
        value: Any,
        key: Optional[str] = None,
        partition: Optional[int] = None,
    ) -> bool:
        """
        메시지 전송

        Args:
            topic: 토픽 이름
            value: 메시지 값
            key: 메시지 키 (선택)
            partition: 파티션 번호 (선택)

        Returns:
            성공 여부
        """
        if not self.producer:
            if not self.connect():
                return False

        try:
            future = self.producer.send(
                topic,
                value=value,
                key=key,
                partition=partition,
            )
            record_metadata = future.get(timeout=self.timeout)
            self.logger.debug(
                f"Message sent to topic={topic}, "
                f"partition={record_metadata.partition}, "
                f"offset={record_metadata.offset}"
            )
            return True
        except KafkaError as e:
            self.logger.error(f"Kafka send error: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error sending message: {e}")
            return False

    def send_batch(self, topic: str, messages: List[Dict[str, Any]]) -> int:
        """
        배치 메시지 전송

        Args:
            topic: 토픽 이름
            messages: 메시지 리스트 (각 메시지는 {"key": ..., "value": ...} 형식)

        Returns:
            성공적으로 전송된 메시지 수
        """
        if not self.producer:
            if not self.connect():
                return 0

        success_count = 0
        for msg in messages:
            key = msg.get("key")
            value = msg.get("value")
            if self.send(topic, value, key):
                success_count += 1

        return success_count

    def send_with_callback(
        self,
        topic: str,
        value: Any,
        key: Optional[str] = None,
        partition: Optional[int] = None,
        callback=None,
    ):
        """
        Callback을 사용한 비동기 메시지 전송 (kafka_project의 CallbackProducer 참고)

        Args:
            topic: 토픽 이름
            value: 메시지 값
            key: 메시지 키 (선택)
            partition: 파티션 번호 (선택)
            callback: 콜백 함수 (metadata, exception) -> None

        Returns:
            Future 객체 (선택적)
        """
        if not self.producer:
            if not self.connect():
                return None

        try:
            future = self.producer.send(
                topic,
                value=value,
                key=key,
                partition=partition,
            )

            # Callback이 제공되면 비동기로 처리 (kafka-python의 Future는 add_callback/add_errback 사용)
            if callback:

                def on_success(record_metadata):
                    """성공 시 콜백"""
                    try:
                        callback(record_metadata, None)
                    except Exception as e:
                        self.logger.error(f"Error in callback: {e}")

                def on_error(exception):
                    """실패 시 콜백"""
                    try:
                        callback(None, exception)
                    except Exception as e:
                        self.logger.error(f"Error in error callback: {e}")

                future.add_callback(on_success)
                future.add_errback(on_error)
                return None  # Callback이 있으면 Future를 반환하지 않음
            else:
                return future  # Callback이 없으면 Future 반환
        except Exception as e:
            self.logger.error(f"Error sending message with callback: {e}")
            if callback:
                callback(None, e)
            return None

    def flush(self):
        """Producer 버퍼 플러시"""
        if self.producer:
            self.producer.flush()

    def close(self):
        """Producer 종료"""
        if self.producer:
            self.producer.close()
            self.logger.info("Kafka Producer closed")


class KafkaConsumerClient(KafkaClient):
    """Kafka Consumer 클라이언트"""

    def __init__(
        self,
        bootstrap_servers: List[str] = None,
        timeout: int = 10,
        group_id: str = "cointicker-consumer",
        auto_offset_reset: str = "earliest",
        enable_auto_commit: bool = True,
        value_deserializer=None,
        key_deserializer=None,
    ):
        """
        Kafka Consumer 초기화

        Args:
            bootstrap_servers: Kafka 브로커 주소 리스트
            timeout: 타임아웃 (초)
            group_id: Consumer Group ID
            auto_offset_reset: 오프셋 리셋 방식 ("earliest", "latest")
            enable_auto_commit: 자동 커밋 여부
            value_deserializer: 값 역직렬화 함수
            key_deserializer: 키 역직렬화 함수
        """
        super().__init__(bootstrap_servers, timeout)

        # 기본 역직렬화 함수
        if value_deserializer is None:
            value_deserializer = lambda v: json.loads(v.decode("utf-8")) if v else None
        if key_deserializer is None:
            key_deserializer = lambda k: k.decode("utf-8") if k else None

        self.consumer = None
        self.group_id = group_id
        self.auto_offset_reset = auto_offset_reset
        self.enable_auto_commit = enable_auto_commit
        self.value_deserializer = value_deserializer
        self.key_deserializer = key_deserializer

    def connect(self, topics: List[str]) -> bool:
        """
        Consumer 연결

        Args:
            topics: 구독할 토픽 리스트

        Returns:
            성공 여부
        """
        try:
            self.consumer = KafkaConsumer(
                *topics,
                bootstrap_servers=self.bootstrap_servers,
                group_id=self.group_id,
                auto_offset_reset=self.auto_offset_reset,
                enable_auto_commit=self.enable_auto_commit,
                value_deserializer=self.value_deserializer,
                key_deserializer=self.key_deserializer,
                consumer_timeout_ms=self.timeout * 1000,
            )
            self.logger.info(
                f"Kafka Consumer connected to {self._get_servers_str()}, "
                f"topics={topics}, group_id={self.group_id}"
            )
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect Kafka Consumer: {e}")
            return False

    def consume(self, callback=None, max_messages: Optional[int] = None):
        """
        메시지 소비

        Args:
            callback: 메시지 처리 콜백 함수 (message -> None)
            max_messages: 최대 메시지 수 (None이면 무제한)
        """
        if not self.consumer:
            self.logger.error("Consumer not connected")
            return

        message_count = 0
        try:
            for message in self.consumer:
                if callback:
                    callback(message)
                else:
                    self.logger.info(
                        f"Received message: topic={message.topic}, "
                        f"partition={message.partition}, "
                        f"offset={message.offset}, "
                        f"key={message.key}, "
                        f"value={message.value}"
                    )

                message_count += 1
                if max_messages and message_count >= max_messages:
                    break

        except KeyboardInterrupt:
            self.logger.info("Consumer interrupted by user")
        except Exception as e:
            self.logger.error(f"Error consuming messages: {e}")

    def close(self):
        """Consumer 종료"""
        if self.consumer:
            self.consumer.close()
            self.logger.info("Kafka Consumer closed")
