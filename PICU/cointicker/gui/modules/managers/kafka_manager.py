"""
Kafka 매니저
Kafka 브로커 관리를 담당하는 클래스
"""

import subprocess
import time
import socket
from pathlib import Path
from typing import Dict

from shared.logger import setup_logger
from gui.core.timing_config import TimingConfig
from gui.core.retry_utils import execute_with_retry

logger = setup_logger(__name__)


class KafkaManager:
    """Kafka 브로커 관리 클래스"""

    def __init__(self):
        """초기화"""
        pass

    def start_broker(self) -> bool:
        """
        Kafka 브로커 자동 시작

        Returns:
            시작 성공 여부
        """
        try:
            # 프로젝트 루트 찾기
            # managers/kafka_manager.py -> modules/managers -> modules -> gui -> cointicker -> PICU -> bigdata
            current_file = Path(__file__)
            project_root = current_file.parent.parent.parent.parent.parent.parent

            # 여러 가능한 Kafka 시작 스크립트 경로 확인
            kafka_scripts = [
                project_root / "kafka_project" / "kafka_streams" / "start_kafka.sh",
                Path("/opt/homebrew/opt/kafka/bin/kafka-server-start.sh"),
                Path("/usr/local/kafka/bin/kafka-server-start.sh"),
            ]

            # 스크립트가 있으면 실행
            for script_path in kafka_scripts:
                if script_path.exists() and script_path.is_file():
                    logger.info(f"Kafka 브로커 시작 스크립트 발견: {script_path}")
                    # 백그라운드에서 실행
                    process = subprocess.Popen(
                        ["bash", str(script_path)],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        start_new_session=True,
                    )
                    # 시작 확인을 위해 잠시 대기
                    broker_start_delay = TimingConfig.get("kafka.broker_start_delay", 3)
                    time.sleep(broker_start_delay)

                    # 포트 확인 (재시도 메커니즘 적용)
                    def check_port():
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(1)
                        result = sock.connect_ex(("localhost", 9092))
                        sock.close()
                        return result == 0

                    port_available = execute_with_retry(
                        check_port,
                        max_retries=3,
                        delay=1.0,
                        exceptions=(socket.error, ConnectionRefusedError),
                    )
                    if port_available:
                        logger.info(f"✅ Kafka 브로커 시작 성공 (PID: {process.pid})")
                        return True
                    else:
                        logger.warning("Kafka 브로커 시작 후 포트 확인 실패")
                        return False

            # 스크립트가 없으면 직접 kafka-server-start 시도
            logger.info(
                "Kafka 시작 스크립트를 찾을 수 없습니다. 직접 시작을 시도합니다..."
            )
            # macOS Homebrew 경로
            kafka_bin = Path("/opt/homebrew/opt/kafka/bin/kafka-server-start")
            kafka_config = Path("/opt/homebrew/etc/kafka/server.properties")

            if kafka_bin.exists() and kafka_config.exists():
                process = subprocess.Popen(
                    [str(kafka_bin), str(kafka_config)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    start_new_session=True,
                )
                broker_start_delay = TimingConfig.get("kafka.broker_start_delay", 3)
                time.sleep(broker_start_delay)

                # 포트 확인 (재시도 메커니즘 적용)
                def check_port():
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    result = sock.connect_ex(("localhost", 9092))
                    sock.close()
                    return result == 0

                port_available = execute_with_retry(
                    check_port,
                    max_retries=3,
                    delay=1.0,
                    exceptions=(socket.error, ConnectionRefusedError),
                )
                if port_available:
                    logger.info(f"✅ Kafka 브로커 시작 성공 (PID: {process.pid})")
                    return True

            logger.warning(
                "Kafka 브로커를 자동으로 시작할 수 없습니다. 수동으로 시작해주세요."
            )
            return False
        except Exception as e:
            logger.error(f"Kafka 브로커 시작 중 오류: {e}")
            return False

    def check_broker_running(self, port: int = 9092) -> bool:
        """
        Kafka 브로커 실행 여부 확인

        Args:
            port: Kafka 포트 (기본: 9092)

        Returns:
            브로커 실행 여부
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(("localhost", port))
            sock.close()
            return result == 0
        except Exception as e:
            logger.debug(f"Kafka 브로커 확인 오류: {e}")
            return False
