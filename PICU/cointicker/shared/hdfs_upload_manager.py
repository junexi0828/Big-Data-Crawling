"""
HDFS 업로드 매니저
재시도 로직, 에러 분류, 자동 업로드 기능 제공
"""

import time
import json
import logging
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Callable
from enum import Enum
from dataclasses import dataclass, field

from shared.hdfs_client import HDFSClient
from shared.utils import get_timestamp, get_date_path
from shared.path_utils import get_cointicker_root
from shared.logger import setup_logger

# 로그 파일 경로 설정
cointicker_root = get_cointicker_root()
log_file = str(cointicker_root / "logs" / "hdfs_upload_manager.log")
logger = setup_logger(__name__, log_file=log_file)


class ErrorType(Enum):
    """에러 타입 분류"""
    TRANSIENT = "transient"  # 일시적 오류 (네트워크, HDFS 일시 다운 등)
    PERMANENT = "permanent"  # 영구적 오류 (설정 오류, 권한 문제 등)
    UNKNOWN = "unknown"  # 알 수 없는 오류


@dataclass
class PendingFile:
    """대기 중인 파일 정보"""
    local_path: Path
    hdfs_path: str
    source: str
    timestamp: datetime
    retry_count: int = 0
    error_type: ErrorType = ErrorType.UNKNOWN
    last_error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)


class HDFSUploadManager:
    """
    HDFS 업로드 매니저
    - Exponential Backoff 재시도 로직
    - 에러 분류 및 처리
    - HDFS 상태 확인 및 자동 업로드
    """

    def __init__(
        self,
        hdfs_client: HDFSClient,
        temp_dir: str = "data/temp",
        max_retries: int = 3,
        initial_delay: float = 2.0,
        backoff_factor: float = 2.0,
        health_check_interval: int = 300,  # 5분
    ):
        """
        초기화

        Args:
            hdfs_client: HDFS 클라이언트
            temp_dir: 임시 파일 디렉토리
            max_retries: 최대 재시도 횟수
            initial_delay: 초기 재시도 지연 시간 (초)
            backoff_factor: 재시도 간격 증가 배수
            health_check_interval: HDFS 상태 확인 간격 (초)
        """
        self.hdfs_client = hdfs_client
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.backoff_factor = backoff_factor
        self.health_check_interval = health_check_interval

        # 대기 중인 파일 목록
        self.pending_files: List[PendingFile] = []
        self.pending_files_lock = threading.Lock()

        # HDFS 연결 상태
        self.hdfs_connected = True
        self.last_health_check = None

        # 자동 업로드 스레드
        self.upload_thread: Optional[threading.Thread] = None
        self.running = False

        logger.info(f"HDFS 업로드 매니저 초기화 완료 (temp_dir: {temp_dir})")

    def save_to_hdfs(
        self,
        items: List[Dict],
        source: str,
        date: Optional[datetime] = None,
    ) -> bool:
        """
        데이터를 HDFS에 저장 (재시도 로직 포함)

        Args:
            items: 저장할 데이터 리스트
            source: 데이터 소스 이름
            date: 날짜 (None이면 오늘)

        Returns:
            성공 여부
        """
        if not items:
            return True

        if date is None:
            date = datetime.now()

        try:
            # 로컬 임시 파일에 저장
            timestamp = get_timestamp()
            date_path = get_date_path(str(self.temp_dir), date)
            date_path.mkdir(parents=True, exist_ok=True)

            local_file = date_path / f"{source}_{timestamp}.json"

            with open(local_file, "w", encoding="utf-8") as f:
                json.dump(items, f, ensure_ascii=False, indent=2)

            # HDFS 경로 생성
            hdfs_path = self.hdfs_client.get_raw_path(source, date)

            # HDFS 디렉토리 생성
            if not self.hdfs_client.exists(hdfs_path):
                self.hdfs_client.mkdir(hdfs_path)

            # HDFS에 업로드 (재시도 로직 포함)
            hdfs_file = f"{hdfs_path}/{local_file.name}"
            success = self._upload_with_retry(str(local_file), hdfs_file, source, date)

            if success:
                logger.info(f"Saved {len(items)} items to HDFS: {hdfs_file}")
                # 로컬 임시 파일 삭제
                local_file.unlink()
                return True
            else:
                # 실패 시 대기 목록에 추가
                self._add_pending_file(local_file, hdfs_file, source, date)
                logger.warning(f"Failed to save to HDFS, added to pending list: {hdfs_file}")
                return False

        except Exception as e:
            logger.error(f"Error saving to HDFS: {e}")
            return False

    def _upload_with_retry(
        self,
        local_path: str,
        hdfs_path: str,
        source: str,
        date: datetime,
    ) -> bool:
        """
        Exponential Backoff를 사용한 재시도 로직

        Args:
            local_path: 로컬 파일 경로
            hdfs_path: HDFS 경로
            source: 데이터 소스
            date: 날짜

        Returns:
            성공 여부
        """
        delay = self.initial_delay

        for attempt in range(self.max_retries):
            try:
                # HDFS 연결 상태 확인
                if not self._check_hdfs_health():
                    logger.debug(f"HDFS 연결 실패, 재시도 대기 중... (시도 {attempt + 1}/{self.max_retries})")
                    if attempt < self.max_retries - 1:
                        time.sleep(delay)
                        delay *= self.backoff_factor
                    continue

                # 업로드 시도
                success = self.hdfs_client.put(local_path, hdfs_path)

                if success:
                    self.hdfs_connected = True
                    return True
                else:
                    # 업로드 실패
                    error_type = self._classify_error(None)
                    logger.warning(
                        f"HDFS 업로드 실패 (시도 {attempt + 1}/{self.max_retries}): "
                        f"{hdfs_path}, 에러 타입: {error_type.value}"
                    )

                    if attempt < self.max_retries - 1:
                        time.sleep(delay)
                        delay *= self.backoff_factor

            except Exception as e:
                error_type = self._classify_error(e)
                logger.warning(
                    f"HDFS 업로드 예외 발생 (시도 {attempt + 1}/{self.max_retries}): "
                    f"{e}, 에러 타입: {error_type.value}"
                )

                # 영구적 오류는 즉시 중단
                if error_type == ErrorType.PERMANENT:
                    logger.error(f"영구적 오류로 인해 재시도 중단: {e}")
                    return False

                if attempt < self.max_retries - 1:
                    time.sleep(delay)
                    delay *= self.backoff_factor

        # 모든 재시도 실패
        self.hdfs_connected = False
        return False

    def _classify_error(self, error: Optional[Exception]) -> ErrorType:
        """
        에러 분류

        Args:
            error: 발생한 예외 (None이면 업로드 실패)

        Returns:
            에러 타입
        """
        if error is None:
            # 업로드 실패는 일시적 오류로 간주
            return ErrorType.TRANSIENT

        error_str = str(error).lower()

        # 영구적 오류 패턴
        permanent_patterns = [
            "permission denied",
            "authentication failed",
            "invalid configuration",
            "namenode not found",
            "invalid path",
        ]

        # 일시적 오류 패턴
        transient_patterns = [
            "connection refused",
            "connection timeout",
            "network is unreachable",
            "name or service not known",
            "temporary failure",
        ]

        for pattern in permanent_patterns:
            if pattern in error_str:
                return ErrorType.PERMANENT

        for pattern in transient_patterns:
            if pattern in error_str:
                return ErrorType.TRANSIENT

        # 기본값은 일시적 오류로 간주
        return ErrorType.TRANSIENT

    def _add_pending_file(
        self,
        local_path: Path,
        hdfs_path: str,
        source: str,
        date: datetime,
    ):
        """
        대기 목록에 파일 추가

        Args:
            local_path: 로컬 파일 경로
            hdfs_path: HDFS 경로
            source: 데이터 소스
            date: 날짜
        """
        with self.pending_files_lock:
            pending_file = PendingFile(
                local_path=local_path,
                hdfs_path=hdfs_path,
                source=source,
                timestamp=date,
            )
            self.pending_files.append(pending_file)
            logger.debug(f"대기 목록에 추가: {local_path.name} -> {hdfs_path}")

    def _check_hdfs_health(self) -> bool:
        """
        HDFS 연결 상태 확인

        Returns:
            연결 가능 여부
        """
        try:
            # 간단한 연결 테스트 (루트 디렉토리 존재 확인)
            test_path = "/"
            exists = self.hdfs_client.exists(test_path)
            self.last_health_check = datetime.now()
            return exists
        except Exception as e:
            logger.debug(f"HDFS 헬스 체크 실패: {e}")
            return False

    def start_auto_upload(self):
        """자동 업로드 스레드 시작"""
        if self.running:
            logger.warning("자동 업로드 스레드가 이미 실행 중입니다.")
            return

        self.running = True
        self.upload_thread = threading.Thread(
            target=self._auto_upload_loop,
            daemon=True,
            name="HDFS-AutoUpload"
        )
        self.upload_thread.start()
        logger.info("HDFS 자동 업로드 스레드 시작")

    def stop_auto_upload(self):
        """자동 업로드 스레드 중지"""
        if not self.running:
            return

        self.running = False
        if self.upload_thread:
            self.upload_thread.join(timeout=5)
        logger.info("HDFS 자동 업로드 스레드 중지")

    def _auto_upload_loop(self):
        """자동 업로드 루프"""
        logger.info("HDFS 자동 업로드 루프 시작")

        while self.running:
            try:
                # HDFS 연결 상태 확인
                if not self.hdfs_connected:
                    if self._check_hdfs_health():
                        logger.info("HDFS 연결 복구됨, 대기 파일 업로드 시작")
                        self.hdfs_connected = True

                # 대기 중인 파일 업로드
                if self.hdfs_connected and self.pending_files:
                    self._process_pending_files()

                # 주기적으로 HDFS 상태 확인
                time.sleep(self.health_check_interval)

            except Exception as e:
                logger.error(f"자동 업로드 루프 오류: {e}")
                time.sleep(60)  # 오류 발생 시 1분 대기

        logger.info("HDFS 자동 업로드 루프 종료")

    def _process_pending_files(self):
        """대기 중인 파일 처리"""
        with self.pending_files_lock:
            if not self.pending_files:
                return

            # 복사본 생성 (락 해제 후 처리)
            files_to_process = self.pending_files.copy()

        uploaded_files = []
        failed_files = []

        for pending_file in files_to_process:
            try:
                # 파일 존재 확인
                if not pending_file.local_path.exists():
                    logger.warning(f"대기 파일이 존재하지 않음: {pending_file.local_path}")
                    uploaded_files.append(pending_file)
                    continue

                # 업로드 시도
                success = self.hdfs_client.put(
                    str(pending_file.local_path),
                    pending_file.hdfs_path
                )

                if success:
                    logger.info(
                        f"대기 파일 업로드 성공: {pending_file.local_path.name} -> "
                        f"{pending_file.hdfs_path}"
                    )
                    # 로컬 파일 삭제
                    pending_file.local_path.unlink()
                    uploaded_files.append(pending_file)
                else:
                    logger.warning(
                        f"대기 파일 업로드 실패: {pending_file.local_path.name}"
                    )
                    failed_files.append(pending_file)

            except Exception as e:
                logger.error(
                    f"대기 파일 처리 중 오류: {pending_file.local_path.name}, {e}"
                )
                failed_files.append(pending_file)

        # 성공한 파일 제거
        with self.pending_files_lock:
            for uploaded_file in uploaded_files:
                if uploaded_file in self.pending_files:
                    self.pending_files.remove(uploaded_file)

            # 실패한 파일은 유지 (다음 주기에 재시도)

        logger.info(
            f"대기 파일 처리 완료: 성공 {len(uploaded_files)}개, "
            f"실패 {len(failed_files)}개, 남은 파일 {len(self.pending_files)}개"
        )

    def get_pending_files_count(self) -> int:
        """대기 중인 파일 개수 반환"""
        with self.pending_files_lock:
            return len(self.pending_files)

    def get_status(self) -> Dict:
        """상태 정보 반환"""
        with self.pending_files_lock:
            return {
                "hdfs_connected": self.hdfs_connected,
                "pending_files_count": len(self.pending_files),
                "last_health_check": (
                    self.last_health_check.isoformat()
                    if self.last_health_check
                    else None
                ),
                "auto_upload_running": self.running,
            }

