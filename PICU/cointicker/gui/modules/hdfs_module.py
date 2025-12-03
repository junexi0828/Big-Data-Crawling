"""
HDFS 모듈
HDFS 작업을 관리하는 모듈
"""

from typing import Dict, Any
from pathlib import Path

from gui.core.module_manager import ModuleInterface
from shared.hdfs_client import HDFSClient
from shared.logger import setup_logger

logger = setup_logger(__name__)


class HDFSModule(ModuleInterface):
    """HDFS 모듈 클래스"""

    def __init__(self, name: str = "HDFSModule"):
        super().__init__(name)
        self.hdfs_client = None

    def initialize(self, config: dict) -> bool:
        """모듈 초기화"""
        try:
            self.config = config
            namenode = config.get("namenode", "hdfs://localhost:9000")
            self.hdfs_client = HDFSClient(namenode=namenode)
            logger.info("HDFS 모듈 초기화 완료")
            return True
        except Exception as e:
            logger.error(f"HDFS 모듈 초기화 실패: {e}")
            return False

    def start(self) -> bool:
        """모듈 시작"""
        self.status = "running"
        logger.info("HDFS 모듈 시작")
        return True

    def stop(self) -> bool:
        """모듈 중지"""
        self.status = "stopped"
        logger.info("HDFS 모듈 중지")
        return True

    def execute(self, command: str, params: dict = None) -> dict:
        """명령어 실행"""
        params = params or {}

        if not self.hdfs_client:
            return {"success": False, "error": "HDFS 클라이언트가 초기화되지 않았습니다"}

        if command == "upload":
            local_path = params.get("local_path")
            hdfs_path = params.get("hdfs_path")
            if not local_path or not hdfs_path:
                return {"success": False, "error": "local_path와 hdfs_path가 필요합니다"}

            success = self.hdfs_client.put(local_path, hdfs_path)
            return {"success": success}

        elif command == "download":
            hdfs_path = params.get("hdfs_path")
            local_path = params.get("local_path")
            if not hdfs_path or not local_path:
                return {"success": False, "error": "hdfs_path와 local_path가 필요합니다"}

            success = self.hdfs_client.get(hdfs_path, local_path)
            return {"success": success}

        elif command == "list_files":
            hdfs_path = params.get("hdfs_path", "/")
            files = self.hdfs_client.list_files(hdfs_path)
            return {"success": True, "files": files}

        elif command == "get_status":
            # HDFS 상태 확인
            return {
                "success": True,
                "namenode": self.hdfs_client.namenode,
                "status": "connected" if self.hdfs_client.exists("/") else "disconnected"
            }

        else:
            return {"success": False, "error": f"알 수 없는 명령어: {command}"}

