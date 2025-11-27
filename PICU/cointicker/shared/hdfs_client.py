"""
HDFS 클라이언트 유틸리티
"""
import subprocess
import logging
from pathlib import Path
from typing import Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class HDFSClient:
    """HDFS 클라이언트 래퍼"""

    def __init__(self, namenode: str = "hdfs://localhost:9000"):
        """
        HDFS 클라이언트 초기화

        Args:
            namenode: NameNode 주소
        """
        self.namenode = namenode
        self.hadoop_home = self._get_hadoop_home()

    def _get_hadoop_home(self) -> Optional[str]:
        """HADOOP_HOME 환경변수 확인"""
        import os
        return os.environ.get('HADOOP_HOME', '/opt/hadoop')

    def _run_command(self, command: str) -> tuple[bool, str, str]:
        """
        HDFS 명령어 실행

        Args:
            command: 실행할 명령어

        Returns:
            (성공 여부, stdout, stderr) 튜플
        """
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )
            return (result.returncode == 0, result.stdout, result.stderr)
        except subprocess.TimeoutExpired:
            logger.error(f"HDFS 명령어 타임아웃: {command}")
            return (False, "", "Command timeout")
        except Exception as e:
            logger.error(f"HDFS 명령어 실행 오류: {e}")
            return (False, "", str(e))

    def put(self, local_path: str, hdfs_path: str) -> bool:
        """
        로컬 파일을 HDFS에 업로드

        Args:
            local_path: 로컬 파일 경로
            hdfs_path: HDFS 경로

        Returns:
            성공 여부
        """
        command = f"hdfs dfs -put {local_path} {hdfs_path}"
        success, stdout, stderr = self._run_command(command)

        if success:
            logger.info(f"HDFS 업로드 성공: {local_path} -> {hdfs_path}")
        else:
            logger.error(f"HDFS 업로드 실패: {stderr}")

        return success

    def get(self, hdfs_path: str, local_path: str) -> bool:
        """
        HDFS 파일을 로컬로 다운로드

        Args:
            hdfs_path: HDFS 경로
            local_path: 로컬 경로

        Returns:
            성공 여부
        """
        command = f"hdfs dfs -get {hdfs_path} {local_path}"
        success, stdout, stderr = self._run_command(command)

        if success:
            logger.info(f"HDFS 다운로드 성공: {hdfs_path} -> {local_path}")
        else:
            logger.error(f"HDFS 다운로드 실패: {stderr}")

        return success

    def mkdir(self, hdfs_path: str) -> bool:
        """
        HDFS 디렉토리 생성

        Args:
            hdfs_path: HDFS 경로

        Returns:
            성공 여부
        """
        command = f"hdfs dfs -mkdir -p {hdfs_path}"
        success, stdout, stderr = self._run_command(command)

        if success:
            logger.info(f"HDFS 디렉토리 생성 성공: {hdfs_path}")
        else:
            logger.error(f"HDFS 디렉토리 생성 실패: {stderr}")

        return success

    def exists(self, hdfs_path: str) -> bool:
        """
        HDFS 경로 존재 여부 확인

        Args:
            hdfs_path: HDFS 경로

        Returns:
            존재하면 True
        """
        command = f"hdfs dfs -test -e {hdfs_path}"
        success, _, _ = self._run_command(command)
        return success

    def list_files(self, hdfs_path: str) -> List[str]:
        """
        HDFS 디렉토리 파일 목록 조회

        Args:
            hdfs_path: HDFS 경로

        Returns:
            파일 경로 리스트
        """
        command = f"hdfs dfs -ls {hdfs_path}"
        success, stdout, stderr = self._run_command(command)

        if not success:
            logger.error(f"HDFS 파일 목록 조회 실패: {stderr}")
            return []

        # 출력 파싱
        files = []
        for line in stdout.strip().split('\n'):
            if line and not line.startswith('Found'):
                parts = line.split()
                if len(parts) >= 8:
                    files.append(parts[-1])

        return files

    def get_raw_path(self, source: str, date: Optional[datetime] = None) -> str:
        """
        원시 데이터 HDFS 경로 생성

        Args:
            source: 데이터 소스 이름
            date: 날짜 (None이면 오늘)

        Returns:
            HDFS 경로
        """
        if date is None:
            date = datetime.now()

        date_str = date.strftime('%Y%m%d')
        return f"/raw/{source}/{date_str}"

    def get_cleaned_path(self, date: Optional[datetime] = None) -> str:
        """
        정제된 데이터 HDFS 경로 생성

        Args:
            date: 날짜 (None이면 오늘)

        Returns:
            HDFS 경로
        """
        if date is None:
            date = datetime.now()

        date_str = date.strftime('%Y%m%d')
        return f"/cleaned/{date_str}"

