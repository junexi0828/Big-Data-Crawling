"""
타이밍 설정 상수
매직 넘버를 제거하고 설정 파일에서 관리
"""

from typing import Dict, Any, Optional
from gui.core.config_manager import ConfigManager

# 전역 ConfigManager 인스턴스 (필요시 초기화)
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """ConfigManager 인스턴스 가져오기 (싱글톤 패턴)"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


class TimingConfig:
    """타이밍 관련 설정 클래스"""

    # 기본값 (설정 파일에 없을 때 사용)
    DEFAULTS = {
        # GUI 타이밍
        "gui.auto_start_delay": 1000,  # GUI 시작 후 백엔드/프론트엔드 자동 시작 지연 (ms)
        "gui.process_status_update_delay": 2000,  # 프로세스 상태 업데이트 지연 (ms)
        "gui.initial_refresh_delay": 5000,  # 초기 데이터 로드 지연 (ms)
        "gui.stats_update_interval": 3000,  # 통계 업데이트 간격 (ms) - 3초
        "gui.tier2_reconnect_delay": 3000,  # Tier2 재연결 지연 (ms)
        "gui.tier2_refresh_delay": 5000,  # Tier2 새로고침 지연 (ms)
        "gui.dialog_wait_delay": 0.2,  # 다이얼로그 대기 시간 (초)
        "gui.config_refresh_delay": 500,  # 설정 새로고침 지연 (ms)
        "gui.user_confirm_timeout": 30,  # 사용자 확인 대기 시간 (초, 30초)
        # HDFS 타이밍
        "hdfs.port_check_retry_interval": 2,  # HDFS 포트 확인 재시도 간격 (초)
        "hdfs.port_check_max_retries": 15,  # HDFS 포트 확인 최대 재시도 횟수
        "hdfs.daemon_start_delay": 2,  # HDFS 데몬 시작 간격 (초)
        "hdfs.secondary_namenode_delay": 3,  # SecondaryNameNode 시작 지연 (초)
        # Kafka 타이밍
        "kafka.broker_start_delay": 3,  # Kafka 브로커 시작 확인 지연 (초)
        # SSH 타이밍
        "ssh.server_start_delay": 2,  # SSH 서버 시작 대기 시간 (초)
        # Spider 타이밍
        "spider.status_check_delay": 2,  # Spider 상태 확인 지연 (초)
        # Pipeline 타이밍
        "pipeline.process_stop_delay": 1,  # 프로세스 중지 대기 시간 (초)
        "pipeline.process_check_delay": 0.5,  # 프로세스 상태 확인 지연 (초)
        # 재시도 설정
        "retry.default_max_retries": 3,  # 기본 최대 재시도 횟수
        "retry.default_delay": 1.0,  # 기본 재시도 지연 시간 (초)
        "retry.backoff_factor": 1.5,  # 재시도 간격 증가 배수
    }

    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        """
        타이밍 설정 값 가져오기

        Args:
            key: 설정 키 (예: "gui.auto_start_delay")
            default: 기본값 (None이면 DEFAULTS에서 찾음)

        Returns:
            설정 값
        """
        config_manager = get_config_manager()
        if default is None:
            default = TimingConfig.DEFAULTS.get(key)

        # GUI 설정에서 가져오기
        value = config_manager.get_config("gui", key.replace("gui.", ""), default)
        if value is not None:
            return value

        # 다른 설정에서 가져오기 (hdfs, kafka 등)
        if key.startswith("hdfs."):
            return config_manager.get_config(
                "cluster", key.replace("hdfs.", "hdfs.timing."), default
            )
        elif key.startswith("kafka."):
            return config_manager.get_config(
                "cluster", key.replace("kafka.", "kafka.timing."), default
            )
        elif key.startswith("ssh."):
            return config_manager.get_config(
                "gui", key.replace("ssh.", "ssh.timing."), default
            )
        elif key.startswith("spider."):
            return config_manager.get_config(
                "spider", key.replace("spider.", "timing."), default
            )
        elif key.startswith("pipeline."):
            return config_manager.get_config(
                "gui", key.replace("pipeline.", "pipeline.timing."), default
            )
        elif key.startswith("retry."):
            return config_manager.get_config(
                "gui", key.replace("retry.", "retry."), default
            )

        return default

    @staticmethod
    def set(key: str, value: Any):
        """
        타이밍 설정 값 설정

        Args:
            key: 설정 키
            value: 설정 값
        """
        config_manager = get_config_manager()

        if key.startswith("gui."):
            config_manager.set_config("gui", key.replace("gui.", ""), value)
        elif key.startswith("hdfs."):
            config_manager.set_config(
                "cluster", key.replace("hdfs.", "hdfs.timing."), value
            )
        elif key.startswith("kafka."):
            config_manager.set_config(
                "cluster", key.replace("kafka.", "kafka.timing."), value
            )
        elif key.startswith("ssh."):
            config_manager.set_config("gui", key.replace("ssh.", "ssh.timing."), value)
        elif key.startswith("spider."):
            config_manager.set_config(
                "spider", key.replace("spider.", "timing."), value
            )
        elif key.startswith("pipeline."):
            config_manager.set_config(
                "gui", key.replace("pipeline.", "pipeline.timing."), value
            )
        elif key.startswith("retry."):
            config_manager.set_config("gui", key.replace("retry.", "retry."), value)
