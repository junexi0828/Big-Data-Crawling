"""
HDFS 클라이언트 유틸리티
Java FileSystem API를 기본으로 사용하고, 실패 시 Python CLI로 폴백
"""

import subprocess
import logging
from pathlib import Path
from typing import Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

# Hadoop 환경 자동 설정 (HADOOP_HOME, PATH)
try:
    from shared.path_utils import setup_hadoop_env

    setup_hadoop_env()
except ImportError:
    # path_utils를 import할 수 없는 경우 스킵 (fallback 모드)
    pass

# Java 기반 HDFS 클라이언트 (pyarrow 사용)
try:
    import pyarrow.fs as pafs  # type: ignore

    PYARROW_AVAILABLE = True
except ImportError:
    PYARROW_AVAILABLE = False
    pafs = None  # type: ignore
    logger.warning("pyarrow not available, will use CLI fallback")


class HDFSClient:
    """
    HDFS 클라이언트 래퍼
    Java FileSystem API (pyarrow)를 기본으로 사용하고, 실패 시 CLI로 폴백
    """

    def __init__(
        self,
        namenode: str = "hdfs://localhost:9000",
        use_java: bool = True,
    ):
        """
        HDFS 클라이언트 초기화

        Args:
            namenode: NameNode 주소
            use_java: Java 기반 클라이언트 사용 여부 (기본값: True)
        """
        self.namenode = namenode
        self.hadoop_home = self._get_hadoop_home()
        self.use_java = use_java and PYARROW_AVAILABLE
        self.fs = None

        # Java 기반 클라이언트 초기화 시도
        if self.use_java and pafs:
            try:
                self.fs = pafs.HadoopFileSystem.from_uri(namenode)
                logger.info(f"Java-based HDFS client initialized: {namenode}")
            except Exception as e:
                # macOS에서는 libhdfs.dylib가 없을 수 있으므로 DEBUG 레벨로 로깅
                import sys
                import platform

                is_macos = sys.platform == "darwin"
                log_level = logger.debug if is_macos else logger.warning
                log_level(
                    f"Failed to initialize Java-based HDFS client: {e}. "
                    f"Falling back to CLI mode."
                )
                self.use_java = False
                self.fs = None
        else:
            logger.info("Using CLI-based HDFS client (fallback mode)")

    def _get_hadoop_home(self) -> Optional[str]:
        """HADOOP_HOME 환경변수 확인"""
        import os

        return os.environ.get("HADOOP_HOME", "/opt/hadoop")

    def _run_command(self, command: str) -> tuple[bool, str, str]:
        """
        HDFS 명령어 실행

        Args:
            command: 실행할 명령어

        Returns:
            (성공 여부, stdout, stderr) 튜플
        """
        import os

        try:
            # 현재 환경변수 복사 (HADOOP_HOME과 PATH 포함)
            env = os.environ.copy()

            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60,
                env=env,  # 환경변수 명시적 전달
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
        로컬 파일을 HDFS에 업로드 (hadoop_project의 PutFile.java 패턴)
        Java FileSystem API를 기본으로 사용하고, 실패 시 CLI로 폴백

        Args:
            local_path: 로컬 파일 경로
            hdfs_path: HDFS 경로

        Returns:
            성공 여부
        """
        # Java 기반 클라이언트 사용 시도
        if self.use_java and self.fs:
            try:
                with open(local_path, "rb") as local_file:
                    with self.fs.open_output_stream(hdfs_path) as hdfs_file:
                        hdfs_file.write(local_file.read())
                logger.info(f"HDFS 업로드 성공 (Java): {local_path} -> {hdfs_path}")
                return True
            except Exception as e:
                logger.warning(f"Java-based upload failed: {e}. Falling back to CLI.")

        # CLI 폴백
        command = f"hdfs dfs -put {local_path} {hdfs_path}"
        success, stdout, stderr = self._run_command(command)

        if success:
            logger.info(f"HDFS 업로드 성공 (CLI): {local_path} -> {hdfs_path}")
        else:
            logger.error(f"HDFS 업로드 실패: {stderr}")

        return success

    def get(self, hdfs_path: str, local_path: str) -> bool:
        """
        HDFS 파일을 로컬로 다운로드
        Java FileSystem API를 기본으로 사용하고, 실패 시 CLI로 폴백

        Args:
            hdfs_path: HDFS 경로
            local_path: 로컬 경로

        Returns:
            성공 여부
        """
        # Java 기반 클라이언트 사용 시도
        if self.use_java and self.fs:
            try:
                with self.fs.open_input_stream(hdfs_path) as hdfs_file:
                    with open(local_path, "wb") as local_file:
                        local_file.write(hdfs_file.read())
                logger.info(f"HDFS 다운로드 성공 (Java): {hdfs_path} -> {local_path}")
                return True
            except Exception as e:
                logger.warning(f"Java-based download failed: {e}. Falling back to CLI.")

        # CLI 폴백
        command = f"hdfs dfs -get {hdfs_path} {local_path}"
        success, stdout, stderr = self._run_command(command)

        if success:
            logger.info(f"HDFS 다운로드 성공 (CLI): {hdfs_path} -> {local_path}")
        else:
            logger.error(f"HDFS 다운로드 실패: {stderr}")

        return success

    def mkdir(self, hdfs_path: str) -> bool:
        """
        HDFS 디렉토리 생성
        Java FileSystem API를 기본으로 사용하고, 실패 시 CLI로 폴백

        Args:
            hdfs_path: HDFS 경로

        Returns:
            성공 여부
        """
        # Java 기반 클라이언트 사용 시도
        if self.use_java and self.fs:
            try:
                self.fs.create_dir(hdfs_path, recursive=True)
                logger.info(f"HDFS 디렉토리 생성 성공 (Java): {hdfs_path}")
                return True
            except FileExistsError:
                # 이미 존재하면 성공으로 간주
                logger.debug(f"HDFS 디렉토리 이미 존재: {hdfs_path}")
                return True
            except Exception as e:
                logger.warning(f"Java-based mkdir failed: {e}. Falling back to CLI.")

        # CLI 폴백
        command = f"hdfs dfs -mkdir -p {hdfs_path}"
        success, stdout, stderr = self._run_command(command)

        if success:
            logger.info(f"HDFS 디렉토리 생성 성공 (CLI): {hdfs_path}")
        else:
            logger.error(f"HDFS 디렉토리 생성 실패: {stderr}")

        return success

    def exists(self, hdfs_path: str) -> bool:
        """
        HDFS 경로 존재 여부 확인 (hadoop_project의 FileSystemAccess.java 패턴)
        Java FileSystem API를 기본으로 사용하고, 실패 시 CLI로 폴백

        Args:
            hdfs_path: HDFS 경로

        Returns:
            존재하면 True
        """
        # Java 기반 클라이언트 사용 시도
        if self.use_java and self.fs and pafs:
            try:
                file_info = self.fs.get_file_info(hdfs_path)
                return file_info.type != pafs.FileType.NotFound
            except Exception as e:
                logger.warning(
                    f"Java-based exists check failed: {e}. Falling back to CLI."
                )

        # CLI 폴백
        command = f"hdfs dfs -test -e {hdfs_path}"
        success, _, _ = self._run_command(command)
        return success

    def list_files(self, hdfs_path: str) -> List[str]:
        """
        HDFS 디렉토리 파일 목록 조회
        Java FileSystem API를 기본으로 사용하고, 실패 시 CLI로 폴백

        Args:
            hdfs_path: HDFS 경로

        Returns:
            파일 경로 리스트
        """
        # Java 기반 클라이언트 사용 시도
        if self.use_java and self.fs and pafs:
            try:
                file_info = self.fs.get_file_info(hdfs_path)
                if file_info.type == pafs.FileType.Directory:
                    selector = pafs.FileSelector(hdfs_path, recursive=False)
                    file_infos = self.fs.get_file_info(selector)
                    files = [
                        info.path
                        for info in file_infos
                        if info.type == pafs.FileType.File
                    ]
                    logger.debug(f"HDFS 파일 목록 조회 성공 (Java): {len(files)}개")
                    return files
                else:
                    return [hdfs_path]
            except Exception as e:
                logger.warning(
                    f"Java-based list_files failed: {e}. Falling back to CLI."
                )

        # CLI 폴백
        command = f"hdfs dfs -ls {hdfs_path}"
        success, stdout, stderr = self._run_command(command)

        if not success:
            logger.error(f"HDFS 파일 목록 조회 실패: {stderr}")
            return []

        # 출력 파싱
        files = []
        for line in stdout.strip().split("\n"):
            if line and not line.startswith("Found"):
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

        date_str = date.strftime("%Y%m%d")
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

        date_str = date.strftime("%Y%m%d")
        return f"/cleaned/{date_str}"

    def rm(self, hdfs_path: str, recursive: bool = False) -> bool:
        """
        HDFS 파일/디렉토리 삭제 (hadoop_project의 run_wordcount_example.sh 참고)
        Java FileSystem API를 기본으로 사용하고, 실패 시 CLI로 폴백

        Args:
            hdfs_path: HDFS 경로
            recursive: 재귀적 삭제 여부 (디렉토리 삭제 시 True)

        Returns:
            성공 여부
        """
        # Java 기반 클라이언트 사용 시도
        if self.use_java and self.fs and pafs:
            try:
                file_info = self.fs.get_file_info(hdfs_path)
                if file_info.type == pafs.FileType.Directory:
                    if recursive:
                        self.fs.delete_dir(hdfs_path)
                    else:
                        logger.warning("Directory deletion requires recursive=True")
                        return False
                else:
                    self.fs.delete_file(hdfs_path)
                logger.info(f"HDFS 삭제 성공 (Java): {hdfs_path}")
                return True
            except Exception as e:
                logger.warning(f"Java-based rm failed: {e}. Falling back to CLI.")

        # CLI 폴백
        if recursive:
            command = f"hdfs dfs -rm -r {hdfs_path}"
        else:
            command = f"hdfs dfs -rm {hdfs_path}"

        success, stdout, stderr = self._run_command(command)

        if success:
            logger.info(f"HDFS 삭제 성공 (CLI): {hdfs_path}")
        else:
            logger.error(f"HDFS 삭제 실패: {stderr}")

        return success

    def cat(self, hdfs_path: str) -> Optional[str]:
        """
        HDFS 파일 내용 읽기 (hadoop_project의 FileSystemAccess.java, URLAccess.java 패턴)
        Java FileSystem API를 기본으로 사용하고, 실패 시 CLI로 폴백

        Args:
            hdfs_path: HDFS 파일 경로

        Returns:
            파일 내용 (실패 시 None)
        """
        # Java 기반 클라이언트 사용 시도
        if self.use_java and self.fs:
            try:
                with self.fs.open_input_stream(hdfs_path) as stream:
                    content = stream.read().decode("utf-8")
                logger.debug(f"HDFS 파일 읽기 성공 (Java): {hdfs_path}")
                return content
            except Exception as e:
                logger.warning(f"Java-based cat failed: {e}. Falling back to CLI.")

        # CLI 폴백
        command = f"hdfs dfs -cat {hdfs_path}"
        success, stdout, stderr = self._run_command(command)

        if success:
            logger.debug(f"HDFS 파일 읽기 성공 (CLI): {hdfs_path}")
            return stdout
        else:
            logger.error(f"HDFS 파일 읽기 실패: {stderr}")
            return None

    def copy(self, src_path: str, dst_path: str) -> bool:
        """
        HDFS 내부 파일 복사
        Java FileSystem API를 기본으로 사용하고, 실패 시 CLI로 폴백

        Args:
            src_path: 원본 HDFS 경로
            dst_path: 대상 HDFS 경로

        Returns:
            성공 여부
        """
        # Java 기반 클라이언트 사용 시도
        if self.use_java and self.fs:
            try:
                with self.fs.open_input_stream(src_path) as src_stream:
                    with self.fs.open_output_stream(dst_path) as dst_stream:
                        dst_stream.write(src_stream.read())
                logger.info(f"HDFS 복사 성공 (Java): {src_path} -> {dst_path}")
                return True
            except Exception as e:
                logger.warning(f"Java-based copy failed: {e}. Falling back to CLI.")

        # CLI 폴백
        command = f"hdfs dfs -cp {src_path} {dst_path}"
        success, stdout, stderr = self._run_command(command)

        if success:
            logger.info(f"HDFS 복사 성공 (CLI): {src_path} -> {dst_path}")
        else:
            logger.error(f"HDFS 복사 실패: {stderr}")

        return success

    def move(self, src_path: str, dst_path: str) -> bool:
        """
        HDFS 내부 파일 이동
        Java FileSystem API를 기본으로 사용하고, 실패 시 CLI로 폴백

        Args:
            src_path: 원본 HDFS 경로
            dst_path: 대상 HDFS 경로

        Returns:
            성공 여부
        """
        # Java 기반 클라이언트 사용 시도
        if self.use_java and self.fs:
            try:
                # 복사 후 삭제로 이동 구현
                if self.copy(src_path, dst_path):
                    self.rm(src_path)
                    logger.info(f"HDFS 이동 성공 (Java): {src_path} -> {dst_path}")
                    return True
            except Exception as e:
                logger.warning(f"Java-based move failed: {e}. Falling back to CLI.")

        # CLI 폴백
        command = f"hdfs dfs -mv {src_path} {dst_path}"
        success, stdout, stderr = self._run_command(command)

        if success:
            logger.info(f"HDFS 이동 성공 (CLI): {src_path} -> {dst_path}")
        else:
            logger.error(f"HDFS 이동 실패: {stderr}")

        return success
