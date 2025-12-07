"""
프로세스 모니터링 유틸리티
각 프로세스의 실시간 상태를 수집하는 공통 모니터
"""

import subprocess
import threading
import time
import json
import re
from typing import Dict, List, Optional, Callable
from datetime import datetime
from pathlib import Path
from collections import deque

from shared.logger import setup_logger

logger = setup_logger(__name__)


class ProcessMonitor:
    """프로세스 모니터링 클래스"""

    def __init__(self, max_log_lines: int = 1000):
        """
        초기화

        Args:
            max_log_lines: 최대 로그 라인 수
        """
        self.max_log_lines = max_log_lines
        self.logs: Dict[str, deque] = {}  # 프로세스별 로그
        self.stats: Dict[str, Dict] = {}  # 프로세스별 통계
        self.monitoring_threads: Dict[str, threading.Thread] = {}
        self.monitoring_active: Dict[str, bool] = {}
        self.log_files: Dict[str, Any] = {}  # 파일 핸들 저장

    def start_monitoring(
        self,
        process_id: str,
        process: subprocess.Popen,
        log_callback: Optional[Callable] = None,
    ):
        """
        프로세스 모니터링 시작

        Args:
            process_id: 프로세스 ID
            process: subprocess.Popen 객체
            log_callback: 로그 콜백 함수
        """
        if process_id in self.monitoring_active and self.monitoring_active[process_id]:
            logger.warning(f"이미 모니터링 중인 프로세스: {process_id}")
            return

        # 로그 파일 설정
        try:
            from shared.path_utils import get_cointicker_root

            cointicker_root = get_cointicker_root()
            log_dir = cointicker_root / "logs"
            log_dir.mkdir(exist_ok=True)
            # kafka_consumer_12345 -> kafka_consumer.log
            base_process_name = process_id.split("_")[0]
            log_file_path = log_dir / f"{base_process_name}.log"
            self.log_files[process_id] = open(log_file_path, "a", encoding="utf-8")
            logger.info(f"로그 파일 열기: {log_file_path}")
        except Exception as e:
            logger.error(f"로그 파일을 열 수 없습니다: {process_id}, {e}")
            self.log_files[process_id] = None

        self.logs[process_id] = deque(maxlen=self.max_log_lines)
        self.stats[process_id] = {
            "start_time": datetime.now().isoformat(),
            "items_processed": 0,
            "errors": 0,
            "warnings": 0,
            "last_update": datetime.now().isoformat(),
        }
        self.monitoring_active[process_id] = True

        # 모니터링 스레드 시작
        thread = threading.Thread(
            target=self._monitor_process,
            args=(process_id, process, log_callback),
            daemon=True,
        )
        thread.start()
        self.monitoring_threads[process_id] = thread

        logger.info(f"프로세스 모니터링 시작: {process_id}")

    def stop_monitoring(self, process_id: str):
        """프로세스 모니터링 중지"""
        self.monitoring_active[process_id] = False
        if process_id in self.monitoring_threads:
            try:
                self.monitoring_threads[process_id].join(timeout=2)
            except Exception as e:
                logger.error(f"모니터링 스레드 조인 실패 {process_id}: {e}")
            del self.monitoring_threads[process_id]

        # 로그 파일 닫기
        if process_id in self.log_files and self.log_files[process_id]:
            try:
                self.log_files[process_id].close()
                del self.log_files[process_id]
                logger.info(f"로그 파일 닫기: {process_id}")
            except Exception as e:
                logger.error(f"로그 파일 닫기 실패 {process_id}: {e}")

        logger.info(f"프로세스 모니터링 중지: {process_id}")

    def _monitor_process(
        self,
        process_id: str,
        process: subprocess.Popen,
        log_callback: Optional[Callable] = None,
    ):
        """프로세스 모니터링 스레드"""
        try:
            # stdout 모니터링
            if process.stdout:
                stdout_thread = threading.Thread(
                    target=self._read_stream,
                    args=(process_id, process.stdout, "stdout", log_callback),
                    daemon=True,
                )
                stdout_thread.start()

            # stderr 모니터링
            if process.stderr:
                stderr_thread = threading.Thread(
                    target=self._read_stream,
                    args=(process_id, process.stderr, "stderr", log_callback),
                    daemon=True,
                )
                stderr_thread.start()

            # 프로세스 종료 대기
            process.wait()

            # 종료 후 통계 업데이트
            self.stats[process_id]["end_time"] = datetime.now().isoformat()
            self.stats[process_id]["exit_code"] = process.returncode
            self.monitoring_active[process_id] = False

            # 로그 파일 핸들러 닫기
            if process_id in self.log_files and self.log_files[process_id]:
                self.log_files[process_id].close()
                del self.log_files[process_id]

        except Exception as e:
            logger.error(f"프로세스 모니터링 오류 {process_id}: {e}")
            self.monitoring_active[process_id] = False

    def _read_stream(
        self,
        process_id: str,
        stream,
        stream_type: str,
        log_callback: Optional[Callable] = None,
    ):
        """스트림 읽기"""
        try:
            for line in iter(stream.readline, ""):
                if not line:
                    break

                if isinstance(line, bytes):
                    line = line.decode("utf-8", errors="ignore").strip()
                else:
                    line = line.strip()

                if not line:
                    continue

                # 파일에 로그 저장
                log_file = self.log_files.get(process_id)
                if log_file and not log_file.closed:
                    try:
                        log_file.write(
                            f"[{datetime.now().isoformat()}] [{stream_type.upper()}] {line}\n"
                        )
                        log_file.flush()
                    except Exception as e:
                        # 파일 쓰기 오류가 모니터링을 중단시키지 않도록 함
                        logger.error(f"로그 파일 쓰기 오류 {process_id}: {e}")

                # 메모리에 로그 저장
                log_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "type": stream_type,
                    "message": line,
                }
                self.logs[process_id].append(log_entry)

                # 통계 업데이트
                self._update_stats(process_id, line)

                # 콜백 호출
                if log_callback:
                    try:
                        log_callback(process_id, log_entry)
                    except Exception as e:
                        logger.error(f"로그 콜백 오류: {e}")

        except Exception as e:
            logger.error(f"스트림 읽기 오류 {process_id}: {e}")

    def _update_stats(self, process_id: str, line: str):
        """통계 업데이트"""
        stats = self.stats.get(process_id, {})
        stats["last_update"] = datetime.now().isoformat()

        # Scrapy 통계 파싱
        # item_scraped_count는 Scrapy의 공식 통계이므로 우선 사용
        if "item_scraped_count" in line.lower():
            match = re.search(r"item_scraped_count[:\s]+(\d+)", line, re.IGNORECASE)
            if match:
                stats["items_processed"] = int(match.group(1))
                # item_scraped_count가 설정되면 Kafka 전송 수는 별도로 추적
                stats["_has_scraped_count"] = True

        # Scrapy "Sent X/Y items to Kafka" 패턴 파싱
        # item_scraped_count가 없을 때만 사용 (대안 통계)
        if (
            "sent" in line.lower()
            and "items" in line.lower()
            and "kafka" in line.lower()
        ):
            sent_match = re.search(r"Sent\s+(\d+)/\d+\s+items", line, re.IGNORECASE)
            if sent_match:
                sent_count = int(sent_match.group(1))

                # item_scraped_count가 있으면 Kafka 전송 수는 별도 필드로 추적
                if stats.get("_has_scraped_count", False):
                    # 이미 item_scraped_count가 있으면 중복 카운팅 방지
                    # Kafka 전송 수는 참고용으로만 저장
                    stats["kafka_sent_count"] = (
                        stats.get("kafka_sent_count", 0) + sent_count
                    )
                else:
                    # item_scraped_count가 없으면 Kafka 전송 수를 대안으로 사용
                    # 하지만 중복 카운팅 방지를 위해 최대값 사용
                    current_count = stats.get("items_processed", 0)
                    # 같은 배치에서 여러 번 로그가 나올 수 있으므로 최대값 사용
                    stats["items_processed"] = max(current_count, sent_count)

            # Kafka Consumer 통계 파싱
            if "kafka_consumer" in process_id.lower():
                # "Processed X messages" 패턴 파싱
                processed_match = re.search(
                    r"Processed\s+(\d+)\s+messages", line, re.IGNORECASE
                )
                if processed_match:
                    stats["items_processed"] = int(processed_match.group(1))

                # "Rate: X.XX msg/s" 패턴 파싱
                rate_match = re.search(r"Rate:\s+([\d.]+)\s+msg/s", line, re.IGNORECASE)
                if rate_match:
                    stats["messages_per_second"] = float(rate_match.group(1))

                # "Received message" 패턴 파싱 (메시지 수신 카운트)
                if "Received message" in line:
                    stats["items_processed"] = stats.get("items_processed", 0) + 1

                # Consumer 연결 성공 확인
                if (
                    "Kafka Consumer Service started successfully" in line
                    or "✅ Kafka Consumer Service started" in line
                    or "Kafka Consumer connected and ready to consume messages" in line
                ):
                    stats["connected"] = True
                    stats["service_status"] = "running"

                # Consumer 연결 실패 확인
                if (
                    "Failed to connect Kafka Consumer" in line
                    or "Consumer subscription is empty" in line
                ):
                    stats["connected"] = False
                    stats["service_status"] = "error"

                # 파티션 할당 정보 파싱 (kafka_consumer 프로세스에만 적용)
                # 두 가지 패턴 지원:
                # 1. "✅ Partitions assigned: {topics}, partitions={len(assignment)}" (consume 메서드)
                # 2. "✅ Kafka Consumer topics assigned after poll: {topics}, partitions={len(assignment)}" (_connect_internal 메서드)
                partitions_match = re.search(
                    r"(?:Partitions assigned|topics assigned after poll):.*?partitions[=:]?\s*(\d+)", line, re.IGNORECASE
                )
                if partitions_match:
                    num_partitions = int(partitions_match.group(1))
                    if "consumer_groups" not in stats:
                        stats["consumer_groups"] = {}
                    stats["consumer_groups"]["num_partitions"] = num_partitions
                    # 파티션이 할당되었으면 연결 성공으로 간주
                    stats["connected"] = True
                    stats["service_status"] = "running"

            # Consumer Groups 정보 파싱 (subscription 정보)
            if "subscription" in line.lower() or "Consumer subscription" in line:
                # subscription=set(['cointicker.raw.upbit_trends']) 패턴 파싱
                sub_match = re.search(r"subscription[=:]\s*set\(\[(.*?)\]\)", line)
                if sub_match:
                    topics_str = sub_match.group(1)
                    topics = [
                        t.strip().strip("'\"")
                        for t in topics_str.split(",")
                        if t.strip()
                    ]
                    if "consumer_groups" not in stats:
                        stats["consumer_groups"] = {}
                    stats["consumer_groups"]["subscription"] = topics

                # "Consumer subscription confirmed: {subscription}" 패턴 파싱
                confirmed_match = re.search(
                    r"Consumer subscription confirmed:\s*(.+)", line
                )
                if confirmed_match:
                    sub_str = confirmed_match.group(1).strip()
                    if sub_str and sub_str != "set()":
                        if "consumer_groups" not in stats:
                            stats["consumer_groups"] = {}
                        # set() 형태 파싱 (set(['topic1', 'topic2']) 또는 set({'topic1', 'topic2'}))
                        set_match = re.search(
                            r"set\(\[(.*?)\]\)|set\(\{(.*?)\}\)", sub_str
                        )
                        if set_match:
                            topics_str = set_match.group(1) or set_match.group(2) or ""
                            topics = [
                                t.strip().strip("'\"")
                                for t in topics_str.split(",")
                                if t.strip()
                            ]
                            stats["consumer_groups"]["subscription"] = topics
                        # 단순 문자열 형태도 파싱 (예: {'topic1', 'topic2'})
                        elif "{" in sub_str and "}" in sub_str:
                            topics_match = re.findall(r"['\"]([^'\"]+)['\"]", sub_str)
                            if topics_match:
                                stats["consumer_groups"]["subscription"] = topics_match

            # 메시지 수신 확인
            if (
                "Received message" in line
                or "Starting message consumption loop" in line
            ):
                stats["consuming"] = True

        # 에러 카운트
        if "ERROR" in line or "error" in line.lower():
            stats["errors"] = stats.get("errors", 0) + 1

        # 경고 카운트
        if "WARNING" in line or "warning" in line.lower():
            stats["warnings"] = stats.get("warnings", 0) + 1

    def get_logs(self, process_id: str, limit: int = 100) -> List[Dict]:
        """로그 가져오기"""
        if process_id not in self.logs:
            return []
        logs = list(self.logs[process_id])
        return logs[-limit:] if limit else logs

    def get_stats(self, process_id: str) -> Dict:
        """통계 가져오기"""
        return self.stats.get(process_id, {})

    def get_all_stats(self) -> Dict[str, Dict]:
        """모든 프로세스 통계 가져오기"""
        return self.stats.copy()


# 전역 모니터 인스턴스
_global_monitor = ProcessMonitor()


def get_monitor() -> ProcessMonitor:
    """전역 모니터 인스턴스 가져오기"""
    return _global_monitor
