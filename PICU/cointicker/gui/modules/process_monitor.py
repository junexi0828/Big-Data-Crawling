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
            self.monitoring_threads[process_id].join(timeout=2)
            del self.monitoring_threads[process_id]
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

                line = line.decode("utf-8", errors="ignore").strip()
                if not line:
                    continue

                # 로그 저장
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
        if "item_scraped_count" in line.lower():
            match = re.search(r"item_scraped_count[:\s]+(\d+)", line, re.IGNORECASE)
            if match:
                stats["items_processed"] = int(match.group(1))

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
