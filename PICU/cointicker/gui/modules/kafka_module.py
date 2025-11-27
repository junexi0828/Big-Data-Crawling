"""
Kafka 모듈
Kafka Producer/Consumer를 관리하는 모듈
"""
import subprocess
import signal
import os
from typing import Dict, Any, Optional
from pathlib import Path

from gui.core.module_manager import ModuleInterface
from shared.logger import setup_logger

logger = setup_logger(__name__)


class KafkaModule(ModuleInterface):
    """Kafka 모듈 클래스"""

    def __init__(self, name: str = "KafkaModule"):
        super().__init__(name)
        self.consumer_path = Path("worker-nodes/kafka_consumer.py")
        self.consumer_process: Optional[subprocess.Popen] = None
        self.bootstrap_servers = ["localhost:9092"]
        self.topics = ["cointicker.raw.*"]
        self.group_id = "cointicker-consumer"

    def initialize(self, config: dict) -> bool:
        """모듈 초기화"""
        try:
            self.config = config
            self.consumer_path = Path(
                config.get("consumer_path", "worker-nodes/kafka_consumer.py")
            )
            self.bootstrap_servers = config.get(
                "bootstrap_servers", ["localhost:9092"]
            )
            self.topics = config.get("topics", ["cointicker.raw.*"])
            self.group_id = config.get("group_id", "cointicker-consumer")
            logger.info("Kafka 모듈 초기화 완료")
            return True
        except Exception as e:
            logger.error(f"Kafka 모듈 초기화 실패: {e}")
            return False

    def start(self) -> bool:
        """Consumer 서비스 시작"""
        if self.consumer_process and self.consumer_process.poll() is None:
            logger.warning("Kafka Consumer가 이미 실행 중입니다")
            return False

        try:
            # Consumer 실행
            cmd = [
                "python",
                str(self.consumer_path),
                "--bootstrap-servers",
                ",".join(self.bootstrap_servers),
                "--topics",
                *self.topics,
                "--group-id",
                self.group_id,
            ]

            self.consumer_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=Path(self.consumer_path).parent.parent,
            )

            self.status = "running"
            logger.info(f"Kafka Consumer 시작: PID {self.consumer_process.pid}")
            return True

        except Exception as e:
            logger.error(f"Kafka Consumer 시작 실패: {e}")
            return False

    def stop(self) -> bool:
        """Consumer 서비스 중지"""
        if not self.consumer_process:
            logger.warning("Kafka Consumer가 실행 중이 아닙니다")
            return False

        try:
            # 프로세스 종료
            self.consumer_process.terminate()
            try:
                self.consumer_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.consumer_process.kill()
                self.consumer_process.wait()

            self.consumer_process = None
            self.status = "stopped"
            logger.info("Kafka Consumer 중지 완료")
            return True

        except Exception as e:
            logger.error(f"Kafka Consumer 중지 실패: {e}")
            return False

    def restart(self) -> bool:
        """Consumer 서비스 재시작"""
        self.stop()
        return self.start()

    def execute(self, command: str, params: dict = None) -> dict:
        """
        명령어 실행

        지원 명령어:
        - start_consumer: Consumer 시작
        - stop_consumer: Consumer 중지
        - restart_consumer: Consumer 재시작
        - get_status: Consumer 상태 조회
        - get_stats: Consumer 통계 조회
        """
        params = params or {}

        if command == "start_consumer":
            success = self.start()
            return {"success": success, "status": self.status}

        elif command == "stop_consumer":
            success = self.stop()
            return {"success": success, "status": self.status}

        elif command == "restart_consumer":
            success = self.restart()
            return {"success": success, "status": self.status}

        elif command == "get_status":
            if self.consumer_process:
                is_running = self.consumer_process.poll() is None
                return {
                    "success": True,
                    "running": is_running,
                    "pid": self.consumer_process.pid if is_running else None,
                    "status": "running" if is_running else "stopped",
                }
            else:
                return {"success": True, "running": False, "status": "stopped"}

        elif command == "get_stats":
            # Consumer 통계 조회 (실제 구현 필요)
            return {
                "success": True,
                "processed_count": 0,
                "error_count": 0,
                "topics": self.topics,
                "group_id": self.group_id,
            }

        else:
            return {"success": False, "error": f"Unknown command: {command}"}

    def get_info(self) -> dict:
        """모듈 정보 조회"""
        status_info = self.execute("get_status")
        return {
            "name": self.name,
            "status": status_info.get("status", "unknown"),
            "bootstrap_servers": self.bootstrap_servers,
            "topics": self.topics,
            "group_id": self.group_id,
            "consumer_path": str(self.consumer_path),
        }

