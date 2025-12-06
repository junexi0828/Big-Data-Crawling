"""
Kafka 클라이언트 유틸리티
Producer와 Consumer를 위한 공통 클라이언트
"""

import json
import logging
import re
from typing import Optional, List, Dict, Any
from pathlib import Path
from kafka import KafkaProducer, KafkaConsumer, KafkaAdminClient
from kafka.errors import KafkaError
from loguru import logger

# 로그 파일 경로 설정
from shared.path_utils import get_cointicker_root

cointicker_root = get_cointicker_root()
log_file = cointicker_root / "logs" / "kafka_client.log"
log_file.parent.mkdir(parents=True, exist_ok=True)

# loguru 파일 핸들러 추가
logger.add(
    str(log_file),
    rotation="10 MB",  # 10MB마다 로그 파일 회전
    retention="7 days",  # 7일 후 오래된 로그 삭제
    encoding="utf-8",
    level="INFO",
)


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

    def connect(
        self, topics: List[str], max_retries: int = 3, retry_delay: float = 2.0
    ) -> bool:
        """
        Consumer 연결 (재시도 로직 포함)

        Args:
            topics: 구독할 토픽 리스트 (와일드카드 패턴 지원, 예: "cointicker.raw.*")
            max_retries: 최대 재시도 횟수 (기본: 3)
            retry_delay: 재시도 지연 시간 (초, 기본: 2.0)

        Returns:
            성공 여부
        """
        from gui.core.retry_utils import execute_with_retry

        def _connect_attempt():
            return self._connect_internal(topics)

        try:
            return execute_with_retry(
                _connect_attempt,
                max_retries=max_retries,
                delay=retry_delay,
                backoff_factor=2.0,
                exceptions=(Exception,),
                on_retry=lambda attempt, e: self.logger.warning(
                    f"Kafka Consumer 연결 실패 (시도 {attempt}/{max_retries}): {e}. 재시도 중..."
                ),
            )
        except Exception as e:
            self.logger.error(f"Kafka Consumer 연결 최종 실패: {e}")
            return False

    def _connect_internal(self, topics: List[str]) -> bool:
        """
        Consumer 연결 내부 구현 (하이브리드 방식)

        초기 스캔은 AdminClient로 수행하여 즉시 토픽 목록을 확인하고,
        실제 구독은 Kafka 네이티브 패턴을 사용하여 자동 업데이트를 활성화합니다.

        Args:
            topics: 구독할 토픽 리스트

        Returns:
            성공 여부
        """
        try:
            # 와일드카드가 포함된 토픽이 있는지 확인
            pattern_topics = []
            direct_topics = []

            for topic in topics:
                if "*" in topic or "?" in topic:
                    # 와일드카드 패턴은 문자열 그대로 저장 (Kafka가 자체적으로 처리)
                    pattern_topics.append(topic)
                else:
                    direct_topics.append(topic)

            # 패턴이 있으면 하이브리드 방식 사용 (Rebalance 방지)
            if pattern_topics:
                # 🔍 1단계: AdminClient로 패턴 매칭 토픽 찾기
                admin_client = None
                matched_topics = []

                try:
                    admin_client = KafkaAdminClient(
                        bootstrap_servers=self.bootstrap_servers,
                        client_id=f"{self.group_id}-admin",
                    )
                    # 모든 토픽 목록 조회
                    all_topics = admin_client.list_topics()

                    # 각 패턴에 대해 매칭되는 토픽 찾기
                    for pattern_str in pattern_topics:
                        # 와일드카드 패턴을 정규식으로 변환
                        # * -> .*, ? -> ., . -> \.
                        pattern_regex = (
                            pattern_str.replace(".", r"\.")
                            .replace("*", ".*")
                            .replace("?", ".")
                        )
                        compiled_pattern = re.compile(f"^{pattern_regex}$")

                        for topic in all_topics:
                            if compiled_pattern.match(topic):
                                if topic not in matched_topics:
                                    matched_topics.append(topic)

                    self.logger.info(
                        f"🔍 Pattern matching: {pattern_topics} -> "
                        f"{len(matched_topics)} topics found: {matched_topics}"
                    )

                except Exception as e:
                    self.logger.warning(
                        f"Failed to list topics: {e}. "
                        f"Falling back to pattern subscription..."
                    )
                finally:
                    if admin_client:
                        try:
                            admin_client.close()
                        except:
                            pass

                # 🚀 2단계: Consumer 생성
                # consumer_timeout_ms를 매우 큰 값으로 설정 (무한 대기 효과, Python 3.14 호환)
                self.consumer = KafkaConsumer(
                    bootstrap_servers=self.bootstrap_servers,
                    group_id=self.group_id,
                    auto_offset_reset=self.auto_offset_reset,
                    enable_auto_commit=self.enable_auto_commit,
                    value_deserializer=self.value_deserializer,
                    key_deserializer=self.key_deserializer,
                    consumer_timeout_ms=2147483647,  # 무한 대기 (Python 3.14 호환)
                )

                # 🎯 3단계: 매칭된 토픽이 있으면 직접 구독 (Rebalance 방지)
                # 없으면 패턴 구독 (새 토픽 자동 감지)
                pattern_str = pattern_topics[0]

                if matched_topics:
                    # 직접 토픽 구독 (더 안정적, Rebalance 최소화)
                    self.consumer.subscribe(topics=matched_topics)
                    self.logger.info(
                        f"✅ Kafka Consumer subscribed to topics: {matched_topics}, "
                        f"group_id={self.group_id} (direct subscription to prevent rebalance)"
                    )
                else:
                    # 패턴 구독 (새 토픽 자동 감지)
                    # 와일드카드를 Java 정규식으로 변환
                    kafka_pattern = f"^{pattern_str.replace('.', r'\\.').replace('*', '.*').replace('?', '.')}$"
                    try:
                        self.consumer.subscribe(pattern=kafka_pattern)
                        self.logger.info(
                            f"🎯 Kafka Consumer subscribed with pattern: {kafka_pattern}, "
                            f"group_id={self.group_id}, mode=AUTO-UPDATE"
                        )
                    except Exception as e:
                        self.logger.error(
                            f"Failed to subscribe with pattern {kafka_pattern}: {e}"
                        )
                        return False

                if len(pattern_topics) > 1:
                    self.logger.warning(
                        f"Multiple patterns provided, using first pattern: {pattern_str}"
                    )

                # 🔄 4단계: 첫 poll()을 실행하여 토픽 할당 확정
                self.logger.info(
                    "Triggering initial poll() to finalize topic assignment..."
                )
                try:
                    # 짧은 타임아웃으로 poll 호출 (토픽 할당을 위해)
                    self.consumer.poll(timeout_ms=5000)

                    # poll 후 assignment 확인
                    assignment = self.consumer.assignment()
                    subscription = self.consumer.subscription()

                    if assignment:
                        assigned_topics = set(tp.topic for tp in assignment)
                        self.logger.info(
                            f"✅ Kafka Consumer topics assigned after poll: {sorted(assigned_topics)}, "
                            f"partitions={len(assignment)}"
                        )
                    else:
                        # 할당된 파티션이 없어도 새 토픽이 생성되면 자동 구독됨
                        self.logger.warning(
                            f"⚠️ No partitions assigned yet. "
                            f"Topics will be assigned when matching topics have data."
                        )
                except Exception as poll_error:
                    self.logger.warning(
                        f"Initial poll failed (non-critical): {poll_error}"
                    )

                subscription = self.consumer.subscription()
                self.logger.info(
                    f"✅ Kafka Consumer subscription confirmed: {subscription}"
                )
            elif direct_topics:
                # 직접 토픽 구독
                # consumer_timeout_ms를 매우 큰 값으로 설정 (무한 대기 효과, Python 3.14 호환)
                # 2147483647 = 2^31 - 1 (약 24일)
                self.consumer = KafkaConsumer(
                    *direct_topics,
                    bootstrap_servers=self.bootstrap_servers,
                    group_id=self.group_id,
                    auto_offset_reset=self.auto_offset_reset,
                    enable_auto_commit=self.enable_auto_commit,
                    value_deserializer=self.value_deserializer,
                    key_deserializer=self.key_deserializer,
                    consumer_timeout_ms=2147483647,  # 무한 대기 (Python 3.14 호환)
                )
                # 구독 확인
                subscription = self.consumer.subscription()
                self.logger.info(
                    f"Kafka Consumer connected to {self._get_servers_str()}, "
                    f"topics={direct_topics}, group_id={self.group_id}, subscription={subscription}"
                )
            else:
                # 토픽이 없으면 에러
                self.logger.error("No topics or patterns provided")
                return False

            return True
        except Exception as e:
            self.logger.error(f"Failed to connect Kafka Consumer: {e}", exc_info=True)
            raise  # 재시도 로직을 위해 예외를 다시 발생시킴

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
        poll_timeout_ms = 1000  # 1초 타임아웃
        no_assignment_warnings = 0
        max_no_assignment_warnings = 10  # 10번 경고 후 로그 레벨 변경

        try:
            self.logger.info("Starting message consumption loop...")

            # 파티션 할당 대기 (최대 10초, Rebalance 방지)
            assignment_wait_time = 0
            max_assignment_wait = 10
            while assignment_wait_time < max_assignment_wait:
                assignment = self.consumer.assignment()
                if assignment:
                    assigned_topics = set(tp.topic for tp in assignment)
                    self.logger.info(
                        f"✅ Partitions assigned: {sorted(assigned_topics)}, "
                        f"partitions={len(assignment)}"
                    )
                    break
                else:
                    # 파티션 할당 대기
                    self.consumer.poll(timeout_ms=1000)
                    assignment_wait_time += 1
                    if assignment_wait_time % 5 == 0:
                        self.logger.debug(
                            f"Waiting for partition assignment... ({assignment_wait_time}s/{max_assignment_wait}s)"
                        )

            if not self.consumer.assignment():
                self.logger.warning(
                    f"⚠️ No partitions assigned after {max_assignment_wait}s. "
                    f"Consumer will continue polling for new topics..."
                )

            # 메시지 소비 루프
            while True:
                try:
                    # poll()을 사용하여 메시지 가져오기
                    message_batch = self.consumer.poll(timeout_ms=poll_timeout_ms)

                    if not message_batch:
                        # 메시지가 없을 때 파티션 할당 상태 확인
                        assignment = self.consumer.assignment()
                        if not assignment:
                            no_assignment_warnings += 1
                            if no_assignment_warnings <= max_no_assignment_warnings:
                                self.logger.debug(
                                    f"No messages and no partitions assigned yet. "
                                    f"Waiting for topic assignment... ({no_assignment_warnings}/{max_no_assignment_warnings})"
                                )
                        continue

                    # 파티션이 할당되었으면 경고 카운터 리셋
                    if assignment:
                        no_assignment_warnings = 0

                    # 배치의 각 메시지 처리
                    for topic_partition, messages in message_batch.items():
                        for message in messages:
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
                                self.logger.info(
                                    f"Reached max_messages limit: {max_messages}"
                                )
                                return

                except Exception as poll_error:
                    self.logger.error(f"Error during poll: {poll_error}", exc_info=True)
                    # 에러가 발생해도 루프 계속 진행
                    continue

        except KeyboardInterrupt:
            self.logger.info("Consumer interrupted by user")
        except Exception as e:
            self.logger.error(f"Error consuming messages: {e}", exc_info=True)
        finally:
            self.logger.info(
                f"Message consumption loop ended. Total messages: {message_count}"
            )

    def get_consumer_groups(self) -> Dict[str, Any]:
        """
        Consumer Groups 상태 조회

        Returns:
            Consumer Groups 정보 딕셔너리
        """
        if not self.consumer:
            return {"error": "Consumer not connected"}

        try:
            # Consumer의 그룹 ID와 구독 정보
            subscription = self.consumer.subscription()
            assignment = self.consumer.assignment()

            return {
                "group_id": self.group_id,
                "subscription": list(subscription) if subscription else [],
                "assignment": (
                    [
                        {
                            "topic": tp.topic,
                            "partition": tp.partition,
                        }
                        for tp in assignment
                    ]
                    if assignment
                    else []
                ),
                "num_partitions": len(assignment) if assignment else 0,
            }
        except Exception as e:
            self.logger.error(f"Failed to get consumer groups: {e}")
            return {"error": str(e)}

    def close(self):
        """Consumer 종료"""
        if self.consumer:
            self.consumer.close()
            self.logger.info("Kafka Consumer closed")
