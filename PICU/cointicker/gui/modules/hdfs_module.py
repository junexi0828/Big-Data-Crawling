"""
HDFS 모듈
HDFS 작업을 관리하는 모듈 (자동 업로드 모니터링 포함)
"""

from typing import Dict, Any
from pathlib import Path
from datetime import datetime

from gui.core.module_manager import ModuleInterface
from shared.hdfs_client import HDFSClient
from shared.logger import setup_logger

logger = setup_logger(__name__)


class HDFSModule(ModuleInterface):
    """HDFS 모듈 클래스 (자동 업로드 모니터링 포함)"""

    def __init__(self, name: str = "HDFSModule"):
        super().__init__(name)
        self.hdfs_client = None
        self.temp_dir = Path("data/temp")

    def initialize(self, config: dict) -> bool:
        """모듈 초기화"""
        try:
            self.config = config
            namenode = config.get("namenode", "hdfs://localhost:9000")
            self.hdfs_client = HDFSClient(namenode=namenode)

            # 임시 디렉토리 설정
            temp_dir = config.get("temp_dir", "data/temp")
            self.temp_dir = Path(temp_dir)

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

    def _get_pending_files_count(self) -> int:
        """
        대기 중인 파일 개수 조회 (로컬 임시 디렉토리에서)

        Returns:
            대기 중인 파일 개수
        """
        try:
            if not self.temp_dir.exists():
                return 0

            # JSON 파일만 카운트 (대기 중인 업로드 파일)
            count = 0
            for file_path in self.temp_dir.rglob("*.json"):
                if file_path.is_file():
                    count += 1

            return count
        except Exception as e:
            logger.debug(f"대기 파일 수 조회 실패: {e}")
            return 0

    def execute(self, command: str, params: dict = None) -> dict:
        """명령어 실행"""
        params = params or {}

        if command == "get_pending_files_count":
            # 대기 중인 파일 개수 조회 (HDFS 클라이언트 없어도 가능)
            count = self._get_pending_files_count()
            return {
                "success": True,
                "pending_files_count": count,
            }

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
            # HDFS 상태 확인 (타임아웃 방지를 위해 예외 처리 강화)
            hdfs_connected = False
            try:
                # Java 기반 클라이언트가 있으면 우선 사용 (빠름)
                if self.hdfs_client.use_java and self.hdfs_client.fs:
                    hdfs_connected = self.hdfs_client.exists("/")
                else:
                    # CLI 사용 시 짧은 타임아웃으로 빠르게 실패 처리
                    hdfs_connected = self.hdfs_client.exists("/")
            except Exception as e:
                logger.debug(f"HDFS 연결 확인 실패: {e}")
                hdfs_connected = False

            # 대기 파일 수 조회
            pending_count = self._get_pending_files_count()

            return {
                "success": True,
                "namenode": self.hdfs_client.namenode if self.hdfs_client else "unknown",
                "status": "connected" if hdfs_connected else "disconnected",
                "connected": hdfs_connected,
                "pending_files_count": pending_count,
            }

        elif command == "get_auto_upload_status":
            # 자동 업로드 상태 조회 (HDFSUploadManager에서)
            try:
                from shared.hdfs_upload_manager import HDFSUploadManager
                # HDFSUploadManager는 실제로는 KafkaConsumer나 HDFSPipeline에서 관리됨
                # 여기서는 대기 파일 수만 반환
                pending_count = self._get_pending_files_count()
                return {
                    "success": True,
                    "pending_files_count": pending_count,
                    "auto_upload_enabled": pending_count > 0,  # 대기 파일이 있으면 활성화된 것으로 간주
                }
            except Exception as e:
                logger.debug(f"자동 업로드 상태 조회 실패: {e}")
                return {
                    "success": True,
                    "pending_files_count": self._get_pending_files_count(),
                    "auto_upload_enabled": False,
                }

        elif command == "list_directories":
            # HDFS 디렉토리 목록 조회
            hdfs_path = params.get("hdfs_path", "/")
            try:
                files = self.hdfs_client.list_files(hdfs_path)
                # 디렉토리만 필터링
                directories = [f for f in files if f.get("type") == "directory"]
                return {
                    "success": True,
                    "path": hdfs_path,
                    "directories": directories,
                }
            except Exception as e:
                logger.error(f"디렉토리 목록 조회 실패: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "directories": [],
            }

        else:
            return {"success": False, "error": f"알 수 없는 명령어: {command}"}

