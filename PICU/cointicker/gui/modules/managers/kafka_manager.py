"""
Kafka 매니저
Kafka 브로커 관리를 담당하는 클래스
"""

import subprocess
import time
import socket
import os
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

                    # 환경 변수 준비 (Hadoop CLASSPATH 제거하여 Jackson 충돌 방지)
                    env = os.environ.copy()
                    if "CLASSPATH" in env:
                        # Hadoop 관련 경로만 제거
                        classpath_parts = env["CLASSPATH"].split(":")
                        filtered_parts = [
                            p for p in classpath_parts if "hadoop" not in p.lower()
                        ]
                        if filtered_parts:
                            env["CLASSPATH"] = ":".join(filtered_parts)
                        else:
                            # 모든 경로가 Hadoop 관련이면 CLASSPATH 제거
                            env.pop("CLASSPATH", None)
                        logger.debug("Hadoop CLASSPATH를 제거하여 Kafka 시작 시도")

                    # 백그라운드에서 실행
                    process = subprocess.Popen(
                        ["bash", str(script_path)],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        env=env,  # 정리된 환경 변수 사용
                        start_new_session=True,
                    )

                    # 스크립트가 완료되기를 기다림 (최대 35초 - 스크립트는 30초까지 대기)
                    try:
                        stdout, stderr = process.communicate(timeout=35)
                        if process.returncode == 0:
                            # 스크립트가 성공적으로 완료되면 Kafka가 시작된 것으로 간주
                            # (스크립트 내부에서 포트 확인 후 exit 0)
                            logger.info(
                                "✅ Kafka 브로커 시작 성공 (스크립트 확인 완료)"
                            )
                            return True
                        else:
                            # 스크립트가 실패했으면 오류 메시지 확인
                            error_msg = (
                                stderr.decode("utf-8", errors="ignore")
                                if stderr
                                else "알 수 없는 오류"
                            )
                            stdout_msg = (
                                stdout.decode("utf-8", errors="ignore")
                                if stdout
                                else ""
                            )
                            logger.warning(
                                f"Kafka 시작 스크립트 실패 (종료 코드: {process.returncode})"
                            )
                            if error_msg:
                                logger.warning(f"오류 메시지: {error_msg[:200]}")
                            if stdout_msg:
                                logger.debug(f"출력: {stdout_msg[:200]}")

                            # 로그 파일 확인하여 실제 오류 파악
                            log_file = Path("/tmp/kafka-server.log")
                            if log_file.exists():
                                try:
                                    log_content = log_file.read_text(
                                        encoding="utf-8", errors="ignore"
                                    )
                                    if log_content:
                                        # 마지막 10줄만 로그
                                        log_lines = log_content.strip().split("\n")
                                        last_lines = "\n".join(log_lines[-10:])
                                        logger.warning(f"Kafka 로그:\n{last_lines}")
                                except Exception:
                                    pass
                            return False
                    except subprocess.TimeoutExpired:
                        # 타임아웃 발생 시 스크립트를 종료하고 포트 확인
                        logger.debug("Kafka 시작 스크립트 타임아웃, 포트 확인으로 전환")
                        process.kill()
                        process.wait()

                        # 포트 확인 (재시도 메커니즘 적용)
                        def check_port():
                            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            sock.settimeout(1)
                            result = sock.connect_ex(("localhost", 9092))
                            sock.close()
                            return result == 0

                        # 재시도 횟수 증가 (최대 10초 대기)
                        port_available = execute_with_retry(
                            check_port,
                            max_retries=10,  # 10회 재시도 (약 10초)
                            delay=1.0,
                            exceptions=(socket.error, ConnectionRefusedError),
                        )
                        if port_available:
                            logger.info("✅ Kafka 브로커 시작 성공 (포트 확인 완료)")
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
                # 환경 변수 준비 (Hadoop CLASSPATH 제거하여 Jackson 충돌 방지)
                env = os.environ.copy()
                if "CLASSPATH" in env:
                    # Hadoop 관련 경로만 제거
                    classpath_parts = env["CLASSPATH"].split(":")
                    filtered_parts = [
                        p for p in classpath_parts if "hadoop" not in p.lower()
                    ]
                    if filtered_parts:
                        env["CLASSPATH"] = ":".join(filtered_parts)
                    else:
                        # 모든 경로가 Hadoop 관련이면 CLASSPATH 제거
                        env.pop("CLASSPATH", None)
                    logger.debug("Hadoop CLASSPATH를 제거하여 Kafka 시작 시도")

                process = subprocess.Popen(
                    [str(kafka_bin), str(kafka_config)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=env,  # 정리된 환경 변수 사용
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
