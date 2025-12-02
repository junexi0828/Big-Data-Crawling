"""
HDFS 매니저
HDFS 설정 및 관리를 담당하는 클래스
"""

import os
import subprocess
import time
import socket
import getpass
from pathlib import Path
from typing import Dict, List, Optional, Callable

from shared.logger import setup_logger
from gui.modules.managers.ssh_manager import SSHManager
from gui.core.timing_config import TimingConfig
from gui.core.retry_utils import execute_with_retry

logger = setup_logger(__name__)


class HDFSManager:
    """HDFS 관리 클래스"""

    def __init__(
        self,
        user_confirm_callback: Optional[Callable[[str, str], bool]] = None,
        user_password_callback: Optional[Callable[[str, str], Optional[str]]] = None,
    ):
        """
        초기화

        Args:
            user_confirm_callback: 사용자 확인 콜백 함수
            user_password_callback: 사용자 비밀번호 입력 콜백 함수
                - 보안: 비밀번호는 메모리에만 저장되고 사용 후 즉시 삭제됨
                - 서버나 파일에 저장되지 않음
        """
        self.user_confirm_callback = user_confirm_callback
        self.user_password_callback = user_password_callback
        self.ssh_manager = SSHManager()

    def check_running(self, ports: Optional[List[int]] = None) -> bool:
        """
        HDFS 실행 여부 확인

        Args:
            ports: 확인할 포트 목록 (기본: [9000, 9870])

        Returns:
            HDFS 실행 여부
        """
        if ports is None:
            ports = [9000, 9870]

        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(("localhost", port))
                sock.close()
                if result == 0:
                    logger.info(f"HDFS가 실행 중입니다 (포트 {port})")
                    return True
            except:
                pass
        return False

    def stop_all_daemons(self, hadoop_home: str) -> bool:
        """
        실행 중인 모든 HDFS 데몬 중지

        Args:
            hadoop_home: HADOOP_HOME 경로

        Returns:
            중지 성공 여부
        """
        try:
            hadoop_path = Path(hadoop_home)

            # 하둡 경로 검증
            if not hadoop_path.exists():
                logger.warning(f"HADOOP_HOME 경로가 존재하지 않습니다: {hadoop_home}")
                return False

            bin_dir = hadoop_path / "bin"
            sbin_dir = hadoop_path / "sbin"

            if not bin_dir.exists():
                logger.warning(f"Hadoop bin 디렉토리를 찾을 수 없습니다: {bin_dir}")
                return False

            # HDFS 환경 변수 설정
            hdfs_env = {**os.environ, "HADOOP_HOME": str(hadoop_home)}
            current_user = getpass.getuser()
            hdfs_env["HDFS_NAMENODE_USER"] = current_user
            hdfs_env["HDFS_DATANODE_USER"] = current_user
            hdfs_env["HDFS_SECONDARYNAMENODE_USER"] = current_user

            logger.info("실행 중인 HDFS 데몬을 중지합니다...")

            # 1. stop-dfs.sh 스크립트 사용 (가장 안전한 방법)
            stop_dfs_script = sbin_dir / "stop-dfs.sh"
            if stop_dfs_script.exists():
                try:
                    stop_result = subprocess.run(
                        ["bash", str(stop_dfs_script)],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        timeout=30,
                        env=hdfs_env,
                        cwd=str(hadoop_path),  # 하둡 경로에서 실행
                    )
                    if stop_result.returncode == 0:
                        logger.info("✅ stop-dfs.sh로 HDFS 데몬 중지 완료")
                    else:
                        stderr_text = stop_result.stderr.decode(
                            "utf-8", errors="ignore"
                        )
                        logger.debug(f"stop-dfs.sh 실행 결과: {stderr_text[:200]}")
                except subprocess.TimeoutExpired:
                    logger.warning("stop-dfs.sh 실행 타임아웃")
                except Exception as e:
                    logger.warning(f"stop-dfs.sh 실행 중 오류: {e}")

            # 2. 개별 데몬 중지 시도 (stop-dfs.sh가 실패한 경우 대비)
            hdfs_cmd = bin_dir / "hdfs"
            if hdfs_cmd.exists():
                daemons = ["namenode", "datanode", "secondarynamenode"]
                for daemon in daemons:
                    try:
                        stop_result = subprocess.run(
                            [
                                str(hdfs_cmd),
                                "--daemon",
                                "stop",
                                daemon,
                            ],  # 검증된 hdfs 명령어 사용
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            timeout=10,
                            env=hdfs_env,
                            cwd=str(hadoop_path),  # 하둡 경로에서 실행
                        )
                        if stop_result.returncode == 0:
                            logger.debug(f"✅ {daemon} 중지 완료")
                        else:
                            stderr_text = stop_result.stderr.decode(
                                "utf-8", errors="ignore"
                            )
                            # "no such process" 같은 에러는 무시 (이미 중지된 경우)
                            if "no such process" not in stderr_text.lower():
                                logger.debug(f"{daemon} 중지 결과: {stderr_text[:100]}")
                    except Exception as e:
                        logger.debug(f"{daemon} 중지 중 오류 (무시): {e}")

            # 3. 프로세스가 완전히 종료될 때까지 대기
            time.sleep(2)

            # 4. jps로 남아있는 프로세스 확인 및 강제 종료
            try:
                jps_result = subprocess.run(
                    ["jps"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=5,
                )
                if jps_result.returncode == 0:
                    jps_output = jps_result.stdout.decode("utf-8", errors="ignore")
                    hdfs_processes = [
                        "NameNode",
                        "DataNode",
                        "SecondaryNameNode",
                    ]
                    for process_name in hdfs_processes:
                        for line in jps_output.split("\n"):
                            if process_name in line:
                                parts = line.strip().split()
                                if parts:
                                    try:
                                        pid = int(parts[0])
                                        logger.warning(
                                            f"남아있는 {process_name} 프로세스 발견 (PID: {pid}). 강제 종료합니다."
                                        )
                                        os.kill(pid, 15)  # SIGTERM
                                        time.sleep(1)
                                        # 여전히 실행 중이면 SIGKILL
                                        try:
                                            os.kill(pid, 0)  # 프로세스 존재 확인
                                            logger.warning(
                                                f"{process_name} (PID: {pid})가 종료되지 않아 SIGKILL을 보냅니다."
                                            )
                                            os.kill(pid, 9)  # SIGKILL
                                        except ProcessLookupError:
                                            pass  # 이미 종료됨
                                    except (ValueError, ProcessLookupError, OSError):
                                        pass
            except Exception as e:
                logger.debug(f"jps 실행 중 오류 (무시): {e}")

            logger.info("✅ HDFS 데몬 정리 완료")
            return True

        except Exception as e:
            logger.error(f"HDFS 데몬 중지 중 오류: {e}")
            return False

    def wait_for_ports(
        self,
        ports: Optional[List[int]] = None,
        max_retries: Optional[int] = None,
        retry_interval: Optional[int] = None,
    ) -> Dict:
        """
        HDFS 포트가 열릴 때까지 대기

        Args:
            ports: 확인할 포트 목록 (기본: [9000, 9870])
            max_retries: 최대 재시도 횟수 (None이면 설정에서 가져옴)
            retry_interval: 재시도 간격 (초, None이면 설정에서 가져옴)

        Returns:
            성공 여부와 메시지
        """
        if ports is None:
            ports = [9000, 9870]

        if max_retries is None:
            max_retries = TimingConfig.get("hdfs.port_check_max_retries", 15)
        if retry_interval is None:
            retry_interval = TimingConfig.get("hdfs.port_check_retry_interval", 2)

        for attempt in range(max_retries):
            time.sleep(retry_interval)

            for port in ports:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    result = sock.connect_ex(("localhost", port))
                    sock.close()
                    if result == 0:
                        logger.info(
                            f"✅ HDFS 시작 성공 (포트 {port}, 시도 {attempt + 1}/{max_retries})"
                        )
                        return {
                            "success": True,
                            "message": f"HDFS가 시작되었습니다 (포트 {port})",
                        }
                except Exception as e:
                    logger.debug(f"HDFS 포트 확인 오류 (포트 {port}): {e}")

            if attempt < max_retries - 1:
                logger.debug(f"HDFS 시작 대기 중... ({attempt + 1}/{max_retries})")

        return {
            "success": False,
            "error": f"HDFS 시작 후 포트 확인 실패 (최대 {max_retries * retry_interval}초 대기)",
        }

    def get_cluster_config(self) -> Optional[Dict]:
        """클러스터 설정 파일 읽기 (cluster_config.yaml 자동 읽기)"""
        try:
            from gui.core.config_manager import ConfigManager

            config_manager = ConfigManager()
            cluster_config = config_manager.load_config("cluster")

            if cluster_config:
                logger.debug(
                    f"클러스터 설정 파일 로드 성공: {config_manager.config_dir / 'cluster_config.yaml'}"
                )
            else:
                logger.debug("클러스터 설정 파일이 없거나 비어있습니다.")

            return cluster_config
        except Exception as e:
            logger.debug(f"클러스터 설정 파일 읽기 실패: {e}")
            return None

    def setup_single_node_mode(
        self, hadoop_home: str, cluster_config: Optional[Dict], replication: int
    ) -> bool:
        """
        단일 노드 모드 설정 (replication=1)

        Args:
            hadoop_home: HADOOP_HOME 경로
            cluster_config: 클러스터 설정 딕셔너리 (없을 수 있음)
            replication: 복제 인수 (단일 노드 모드에서는 1)

        Returns:
            설정 성공 여부
        """
        try:
            hadoop_path = Path(hadoop_home)

            # 하둡 경로 검증
            if not hadoop_path.exists():
                logger.error(f"HADOOP_HOME 경로가 존재하지 않습니다: {hadoop_home}")
                return False

            etc_hadoop = hadoop_path / "etc" / "hadoop"

            if not etc_hadoop.exists():
                logger.error(f"Hadoop 설정 디렉토리를 찾을 수 없습니다: {etc_hadoop}")
                return False

            # namenode URL 결정 (단일 노드 모드에서는 항상 localhost 사용)
            namenode_url = "hdfs://localhost:9000"

            # 1. core-site.xml 생성/업데이트
            core_site = etc_hadoop / "core-site.xml"
            logger.info(f"core-site.xml 설정 중 (단일 노드): {namenode_url}")
            core_site.write_text(
                f"""<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
    <property>
        <name>fs.defaultFS</name>
        <value>{namenode_url}</value>
    </property>
</configuration>
"""
            )

            # 2. hdfs-site.xml 생성/업데이트 (단일 노드 모드에서는 항상 replication=1)
            hdfs_site = etc_hadoop / "hdfs-site.xml"
            single_node_replication = 1  # 단일 노드 모드에서는 항상 1
            logger.info(
                f"hdfs-site.xml 설정 중 (단일 노드): replication={single_node_replication}"
            )
            hdfs_site.write_text(
                f"""<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
    <property>
        <name>dfs.replication</name>
        <value>{single_node_replication}</value>
    </property>
</configuration>
"""
            )

            logger.info("✅ 단일 노드 모드 설정 완료")
            return True

        except Exception as e:
            logger.error(f"단일 노드 모드 설정 중 오류: {e}")
            return False

    def setup_cluster_mode(self, hadoop_home: str, cluster_config: Dict) -> bool:
        """
        클러스터 모드 설정 (유선 연결 시 자동 설정)

        Args:
            hadoop_home: HADOOP_HOME 경로
            cluster_config: 클러스터 설정 딕셔너리

        Returns:
            설정 성공 여부
        """
        try:
            hadoop_path = Path(hadoop_home)

            # 하둡 경로 검증
            if not hadoop_path.exists():
                logger.error(f"HADOOP_HOME 경로가 존재하지 않습니다: {hadoop_home}")
                return False

            etc_hadoop = hadoop_path / "etc" / "hadoop"

            if not etc_hadoop.exists():
                logger.error(f"Hadoop 설정 디렉토리를 찾을 수 없습니다: {etc_hadoop}")
                return False

            cluster_info = cluster_config.get("cluster", {})
            hadoop_info = cluster_config.get("hadoop", {})

            if not cluster_info or not hadoop_info:
                logger.warning("클러스터 설정이 불완전합니다.")
                return False

            master = cluster_info.get("master", {})
            workers = cluster_info.get("workers", [])
            namenode_url = hadoop_info.get("hdfs", {}).get("namenode", "")
            replication = hadoop_info.get("hdfs", {}).get("replication", 3)

            if not master or not workers:
                logger.warning("마스터 또는 워커 노드 정보가 없습니다.")
                return False

            master_hostname = master.get("hostname", "localhost")

            # 1. 각 노드에 SSH 연결 테스트
            logger.info("클러스터 노드 SSH 연결 테스트 중...")
            all_nodes_accessible = True

            # localhost SSH 테스트
            logger.debug("localhost SSH 연결 테스트 중...")
            if not self.ssh_manager.test_connection("localhost", timeout=5):
                logger.warning("localhost SSH 연결 실패")
                all_nodes_accessible = False

            # 마스터 노드 테스트
            if not self.ssh_manager.test_connection(master_hostname, timeout=5):
                logger.warning(f"마스터 노드({master_hostname}) SSH 연결 실패")
                all_nodes_accessible = False

            # 워커 노드 테스트
            for worker in workers:
                worker_hostname = worker.get("hostname", "")
                if worker_hostname:
                    if not self.ssh_manager.test_connection(worker_hostname, timeout=5):
                        logger.warning(f"워커 노드({worker_hostname}) SSH 연결 실패")
                        all_nodes_accessible = False

            if not all_nodes_accessible:
                logger.warning(
                    "일부 노드에 SSH 연결할 수 없습니다. 클러스터 모드 설정을 건너뜁니다."
                )
                return False

            # 2. core-site.xml 생성/업데이트
            core_site = etc_hadoop / "core-site.xml"
            logger.info(f"core-site.xml 설정 중: {namenode_url}")
            core_site.write_text(
                f"""<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
    <property>
        <name>fs.defaultFS</name>
        <value>{namenode_url}</value>
    </property>
</configuration>
"""
            )

            # 3. hdfs-site.xml 생성/업데이트
            hdfs_site = etc_hadoop / "hdfs-site.xml"
            logger.info(f"hdfs-site.xml 설정 중: replication={replication}")
            hdfs_site.write_text(
                f"""<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
    <property>
        <name>dfs.replication</name>
        <value>{replication}</value>
    </property>
</configuration>
"""
            )

            # 4. workers 파일 생성
            workers_file = etc_hadoop / "workers"
            worker_hostnames = [
                w.get("hostname", "") for w in workers if w.get("hostname")
            ]
            if worker_hostnames:
                logger.info(f"workers 파일 생성 중: {', '.join(worker_hostnames)}")
                workers_file.write_text("\n".join(worker_hostnames) + "\n")

            # 5. master 파일 생성 (SecondaryNameNode용)
            master_file = etc_hadoop / "master"
            logger.info(f"master 파일 생성 중: {master_hostname}")
            master_file.write_text(master_hostname + "\n")

            logger.info("✅ 클러스터 모드 설정 완료")
            return True

        except Exception as e:
            logger.error(f"클러스터 모드 설정 중 오류: {e}")
            return False

    def start_daemons_direct(
        self, hadoop_home: str, hdfs_env: Dict, namenode_ports: List[int]
    ) -> Dict:
        """
        SSH 없이 HDFS 데몬을 직접 시작 (단일 노드 모드)

        Args:
            hadoop_home: HADOOP_HOME 경로
            hdfs_env: HDFS 환경 변수 딕셔너리
            namenode_ports: NameNode 포트 목록

        Returns:
            시작 결과
        """
        try:
            hadoop_path = Path(hadoop_home)

            # 하둡 경로 검증
            if not hadoop_path.exists():
                logger.error(f"HADOOP_HOME 경로가 존재하지 않습니다: {hadoop_home}")
                return {
                    "success": False,
                    "error": f"HADOOP_HOME 경로가 존재하지 않습니다: {hadoop_home}",
                }

            bin_dir = hadoop_path / "bin"

            if not bin_dir.exists():
                logger.error(f"Hadoop bin 디렉토리를 찾을 수 없습니다: {bin_dir}")
                return {
                    "success": False,
                    "error": f"Hadoop bin 디렉토리를 찾을 수 없습니다: {bin_dir}",
                }

            # hdfs 명령어 파일 존재 확인
            hdfs_cmd = bin_dir / "hdfs"
            if not hdfs_cmd.exists():
                logger.error(f"HDFS 명령어를 찾을 수 없습니다: {hdfs_cmd}")
                return {
                    "success": False,
                    "error": f"HDFS 명령어를 찾을 수 없습니다: {hdfs_cmd}",
                }

            # NameNode 포맷 확인 (필요시)
            namenode_dir = hadoop_path / "tmp" / "dfs" / "name"
            if not namenode_dir.exists() or not any(namenode_dir.iterdir()):
                logger.info("NameNode 포맷이 필요합니다. 포맷을 시도합니다...")
                format_result = subprocess.run(
                    [
                        str(hdfs_cmd),  # 검증된 hdfs 명령어 사용
                        "namenode",
                        "-format",
                        "-force",
                        "-nonInteractive",
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=30,
                    env=hdfs_env,
                    cwd=str(hadoop_path),  # 하둡 경로에서 실행
                )
                if format_result.returncode == 0:
                    logger.info("✅ NameNode 포맷 완료")
                else:
                    stderr_text = format_result.stderr.decode("utf-8", errors="ignore")
                    if "already formatted" not in stderr_text.lower():
                        logger.warning(f"NameNode 포맷 실패: {stderr_text[:200]}")
                    # 포맷 실패해도 계속 진행 (이미 포맷되어 있을 수 있음)

            # 데몬 직접 시작
            logger.info("HDFS 데몬 직접 시작 중...")
            daemons = []

            # NameNode 시작
            namenode_process = subprocess.Popen(
                [
                    str(hdfs_cmd),
                    "--daemon",
                    "start",
                    "namenode",
                ],  # 검증된 hdfs 명령어 사용
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True,
                env=hdfs_env,
                cwd=str(hadoop_path),  # 하둡 경로에서 실행
            )
            daemons.append(("namenode", namenode_process))
            logger.info("NameNode 데몬 시작 중...")
            daemon_start_delay = TimingConfig.get("hdfs.daemon_start_delay", 2)
            time.sleep(daemon_start_delay)

            # DataNode 시작
            datanode_process = subprocess.Popen(
                [
                    str(hdfs_cmd),
                    "--daemon",
                    "start",
                    "datanode",
                ],  # 검증된 hdfs 명령어 사용
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True,
                env=hdfs_env,
                cwd=str(hadoop_path),  # 하둡 경로에서 실행
            )
            daemons.append(("datanode", datanode_process))
            logger.info("DataNode 데몬 시작 중...")
            time.sleep(daemon_start_delay)

            # SecondaryNameNode 시작
            secondary_namenode_process = subprocess.Popen(
                [
                    str(hdfs_cmd),
                    "--daemon",
                    "start",
                    "secondarynamenode",
                ],  # 검증된 hdfs 명령어 사용
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True,
                env=hdfs_env,
                cwd=str(hadoop_path),  # 하둡 경로에서 실행
            )
            daemons.append(("secondarynamenode", secondary_namenode_process))
            logger.info("SecondaryNameNode 데몬 시작 중...")
            secondary_namenode_delay = TimingConfig.get(
                "hdfs.secondary_namenode_delay", 3
            )
            time.sleep(secondary_namenode_delay)

            # 포트 확인
            port_check_result = self.wait_for_ports(namenode_ports)
            if port_check_result.get("success"):
                return port_check_result

            # 실패 시 데몬 정리
            logger.warning("HDFS 데몬 시작 실패. 데몬을 정리합니다...")
            for daemon_name, proc in daemons:
                try:
                    proc.terminate()
                    proc.wait(timeout=5)
                except:
                    pass

            return {
                "success": False,
                "error": "HDFS 데몬 시작 후 포트 확인 실패 (최대 30초 대기)",
            }

        except Exception as e:
            logger.error(f"HDFS 데몬 직접 시작 중 오류: {e}")
            return {"success": False, "error": f"HDFS 데몬 시작 중 오류: {str(e)}"}

    def check_and_start(
        self,
        user_confirm_callback: Optional[Callable[[str, str], bool]] = None,
        user_password_callback: Optional[Callable[[str, str], Optional[str]]] = None,
    ) -> Dict:
        """
        HDFS 체크 및 자동 시작 시도

        Args:
            user_confirm_callback: 사용자 확인 콜백 함수 (기본: self.user_confirm_callback)
            user_password_callback: 사용자 비밀번호 입력 콜백 함수
                - 보안: 비밀번호는 메모리에만 저장되고 사용 후 즉시 삭제됨
                - 서버나 파일에 저장되지 않음

        Returns:
            시작 결과
        """
        # 콜백 함수 업데이트 (호출 시 전달된 콜백 우선 사용)
        if user_confirm_callback:
            self.user_confirm_callback = user_confirm_callback
        if user_password_callback:
            self.user_password_callback = user_password_callback

        if user_confirm_callback is None:
            user_confirm_callback = self.user_confirm_callback

        try:
            # HDFS NameNode 포트 확인 (기본: 9000, 웹 UI: 9870)
            namenode_ports = [9000, 9870]

            if self.check_running(namenode_ports):
                return {"success": True, "message": "HDFS가 이미 실행 중입니다."}

            # HDFS 시작 시도
            logger.info("HDFS가 실행 중이 아닙니다. 자동으로 시작을 시도합니다...")

            # 클러스터 설정 확인
            cluster_config = self.get_cluster_config()

            # replication 값 확인
            replication = 3  # 기본값: 멀티노드 모드
            if cluster_config:
                replication = (
                    cluster_config.get("hadoop", {})
                    .get("hdfs", {})
                    .get("replication", 3)
                )

            # 기본 동작: cluster 섹션이 있으면 멀티노드 모드로 시도
            has_cluster_config = (
                cluster_config is not None and cluster_config.get("cluster") is not None
            )

            if has_cluster_config and cluster_config:
                master_hostname = (
                    cluster_config.get("cluster", {})
                    .get("master", {})
                    .get("hostname", "unknown")
                )
                worker_count = len(cluster_config.get("cluster", {}).get("workers", []))
                logger.info(
                    "✅ 클러스터 설정 파일 감지됨. 멀티노드 모드로 클러스터 구성을 시도합니다."
                )
                logger.info(
                    f"   마스터: {master_hostname}, 워커 노드: {worker_count}개, Replication: {replication}"
                )
            else:
                logger.debug(
                    "클러스터 설정 파일이 없거나 불완전합니다. 단일 노드 모드로 진행합니다."
                )

            # HADOOP_HOME 환경 변수 확인 및 자동 설정
            hadoop_home = os.environ.get("HADOOP_HOME")
            if not hadoop_home:
                # 프로젝트 루트 찾기
                current_file = Path(__file__)
                project_root = current_file.parent.parent.parent.parent.parent.parent

                # 검색할 경로 목록
                search_paths = [
                    project_root / "hadoop_project" / "hadoop-3.4.1",
                    project_root.parent / "hadoop_project" / "hadoop-3.4.1",
                    Path("/opt/hadoop"),
                    Path("/usr/local/hadoop"),
                    Path("/home/bigdata/hadoop-3.4.1"),
                    Path("/usr/lib/hadoop"),
                    Path("/opt/homebrew/opt/hadoop"),
                    Path("/usr/local/opt/hadoop"),
                ]

                for path in search_paths:
                    if path.exists() and (path / "sbin" / "start-dfs.sh").exists():
                        hadoop_home = str(path)
                        logger.info(f"✅ HADOOP_HOME 자동 감지: {hadoop_home}")
                        os.environ["HADOOP_HOME"] = hadoop_home
                        break

            if hadoop_home:
                # 하둡 경로 검증
                hadoop_path = Path(hadoop_home)
                if not hadoop_path.exists():
                    logger.error(f"HADOOP_HOME 경로가 존재하지 않습니다: {hadoop_home}")
                    return {
                        "success": False,
                        "error": f"HADOOP_HOME 경로가 존재하지 않습니다: {hadoop_home}",
                    }

                bin_dir = hadoop_path / "bin"
                sbin_dir = hadoop_path / "sbin"

                if not bin_dir.exists() or not sbin_dir.exists():
                    logger.error(
                        f"Hadoop bin 또는 sbin 디렉토리를 찾을 수 없습니다: {hadoop_home}"
                    )
                    return {
                        "success": False,
                        "error": f"Hadoop bin 또는 sbin 디렉토리를 찾을 수 없습니다: {hadoop_home}",
                    }

                start_dfs_script = sbin_dir / "start-dfs.sh"
                if start_dfs_script.exists():
                    logger.info(f"HDFS 시작 스크립트 발견: {start_dfs_script}")

                    # 기존 HDFS 프로세스 정리 (포트는 닫혀있지만 프로세스가 남아있을 수 있음)
                    logger.info("기존 HDFS 프로세스 정리 중...")
                    self.stop_all_daemons(hadoop_home)

                    # HDFS 환경 변수 설정
                    hdfs_env = {**os.environ, "HADOOP_HOME": hadoop_home}
                    current_user = getpass.getuser()
                    hdfs_env["HDFS_NAMENODE_USER"] = current_user
                    hdfs_env["HDFS_DATANODE_USER"] = current_user
                    hdfs_env["HDFS_SECONDARYNAMENODE_USER"] = current_user

                    # 1단계: 기본 동작 - 멀티노드 모드로 클러스터 구성 시도
                    if has_cluster_config and cluster_config:
                        logger.info("멀티노드 모드: 클러스터 설정을 확인합니다...")
                        cluster_setup_success = self.setup_cluster_mode(
                            hadoop_home, cluster_config
                        )
                        if cluster_setup_success:
                            logger.info(
                                "✅ 멀티노드 모드 설정 완료. localhost SSH 연결을 확인합니다."
                            )
                            ssh_available = self.ssh_manager.test_connection(
                                "localhost", timeout=2
                            )
                            if not ssh_available:
                                logger.warning(
                                    "⚠️ 원격 노드 SSH는 성공했지만 localhost SSH 연결 실패"
                                )
                        else:
                            # 멀티노드 모드 실패 시 사용자 확인
                            logger.warning(
                                "⚠️ 멀티노드 모드 설정 실패. 클러스터 노드에 연결할 수 없습니다."
                            )

                            use_single_node = False
                            if user_confirm_callback:
                                try:
                                    use_single_node = user_confirm_callback(
                                        "클러스터 연결 실패",
                                        "멀티노드 모드로 클러스터 구성에 실패했습니다.\n\n"
                                        "개발/테스트를 위해 단일 노드 모드로 진행하시겠습니까?\n\n"
                                        "예: 단일 노드 모드로 진행\n"
                                        "아니오: 멀티노드 모드 재시도",
                                    )
                                except Exception as e:
                                    logger.error(f"사용자 확인 콜백 실행 중 오류: {e}")
                                    use_single_node = True
                            else:
                                logger.info(
                                    "사용자 확인 콜백이 없습니다. 자동으로 단일 노드 모드로 전환합니다."
                                )
                                use_single_node = True

                            if use_single_node:
                                logger.info(
                                    "✅ 사용자 확인: 단일 노드 모드로 진행합니다."
                                )
                                self.setup_single_node_mode(
                                    hadoop_home, cluster_config, replication
                                )
                                ssh_available = self.ssh_manager.test_connection(
                                    "localhost", timeout=2
                                )
                            else:
                                logger.info(
                                    "사용자가 멀티노드 모드를 유지하기로 선택했습니다."
                                )
                                return {
                                    "success": False,
                                    "error": "멀티노드 모드 설정 실패. 클러스터 노드에 연결할 수 없습니다.",
                                }
                    else:
                        # 클러스터 설정이 없으면 처음부터 단일 노드 모드
                        logger.info("단일 노드 모드: HDFS 설정 파일 생성 중...")
                        self.setup_single_node_mode(
                            hadoop_home, cluster_config, replication
                        )
                        ssh_available = self.ssh_manager.test_connection(
                            "localhost", timeout=2
                        )

                    # 2단계: SSH 실패 시 단일 노드 모드로 분기 - 로컬 SSH 자동 설정
                    if not ssh_available:
                        logger.info(
                            "SSH 연결 실패. 단일 노드 모드로 전환하여 로컬 SSH 설정을 시도합니다..."
                        )
                        ssh_setup_success = self.ssh_manager.setup_local_ssh()

                        if ssh_setup_success:
                            ssh_available = self.ssh_manager.test_connection(
                                "localhost", timeout=2
                            )

                            if ssh_available:
                                logger.info("✅ 로컬 SSH 설정 완료. HDFS를 시작합니다.")
                            else:
                                logger.warning(
                                    "⚠️ SSH 설정 후에도 연결 실패. SSH 없이 HDFS 데몬을 직접 시작합니다."
                                )
                                ssh_available = False
                        else:
                            logger.warning(
                                "⚠️ 로컬 SSH 설정 실패. SSH 없이 HDFS 데몬을 직접 시작합니다."
                            )
                            ssh_available = False
                    else:
                        logger.info(
                            "✅ SSH 연결 성공. 클러스터 모드로 HDFS를 시작합니다."
                        )

                    # HDFS 시작
                    if not ssh_available:
                        # SSH 없이 데몬 직접 시작 (단일 노드 모드)
                        logger.info("SSH 없이 HDFS 데몬을 직접 시작합니다...")
                        return self.start_daemons_direct(
                            hadoop_home, hdfs_env, namenode_ports
                        )
                    else:
                        # SSH를 통한 일반 시작 (클러스터 모드)
                        logger.info("HDFS 시작 중...")

                        # sudo 비밀번호가 필요한 경우 GUI에서 입력받기 (검증 포함)
                        password = None
                        max_password_attempts = 3
                        password_attempt = 0

                        if self.user_password_callback:
                            while password_attempt < max_password_attempts:
                                try:
                                    # 비밀번호 입력 요청
                                    if password_attempt == 0:
                                        message = (
                                            "HDFS를 시작하기 위해 시스템 비밀번호가 필요합니다.\n\n"
                                            "⚠️ 보안 안내:\n"
                                            "- 비밀번호는 메모리에만 저장됩니다\n"
                                            "- 사용 후 즉시 삭제됩니다\n"
                                            "- 서버나 파일에 저장되지 않습니다\n\n"
                                            "비밀번호를 입력하세요:"
                                        )
                                    else:
                                        message = (
                                            f"비밀번호가 올바르지 않습니다. ({password_attempt}/{max_password_attempts - 1} 시도)\n\n"
                                            "다시 입력하세요:"
                                        )

                                    password = self.user_password_callback(
                                        "HDFS 시작 - 관리자 권한 필요",
                                        message,
                                    )

                                    if not password:
                                        logger.warning(
                                            "비밀번호 입력이 취소되었습니다."
                                        )
                                        return {
                                            "success": False,
                                            "error": "비밀번호 입력이 취소되었습니다. HDFS를 시작할 수 없습니다.",
                                        }

                                    # 비밀번호 검증 (sudo -S로 테스트)
                                    logger.info("비밀번호 검증 중...")
                                    test_process = subprocess.Popen(
                                        ["sudo", "-S", "echo", "test"],
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        env=hdfs_env,
                                    )

                                    try:
                                        test_process.stdin.write(
                                            (password + "\n").encode()
                                        )
                                        test_process.stdin.flush()
                                        test_process.stdin.close()

                                        # 비밀번호 검증 대기 (최대 5초)
                                        stdout, stderr = test_process.communicate(
                                            timeout=5
                                        )

                                        if test_process.returncode == 0:
                                            logger.info("✅ 비밀번호 검증 성공")
                                            break  # 비밀번호가 올바름
                                        else:
                                            stderr_text = stderr.decode(
                                                "utf-8", errors="ignore"
                                            )
                                            if (
                                                "incorrect password"
                                                in stderr_text.lower()
                                                or "sorry" in stderr_text.lower()
                                            ):
                                                logger.warning(
                                                    f"❌ 비밀번호가 올바르지 않습니다. (시도 {password_attempt + 1}/{max_password_attempts})"
                                                )
                                                password_attempt += 1
                                                password = None  # 비밀번호 초기화
                                                continue  # 재입력 요청
                                            else:
                                                # 다른 오류 (sudo 권한 없음 등)
                                                logger.warning(
                                                    f"비밀번호 검증 중 오류: {stderr_text[:200]}"
                                                )
                                                password_attempt += 1
                                                password = None
                                                continue
                                    except subprocess.TimeoutExpired:
                                        test_process.kill()
                                        logger.warning("비밀번호 검증 타임아웃")
                                        password_attempt += 1
                                        password = None
                                        continue
                                    except Exception as e:
                                        logger.error(f"비밀번호 검증 중 예외: {e}")
                                        password_attempt += 1
                                        password = None
                                        continue
                                    finally:
                                        # 보안: 테스트용 비밀번호 즉시 삭제
                                        if password:
                                            # 검증 성공 시 password는 유지, 실패 시 None으로 설정됨
                                            pass

                                except Exception as e:
                                    logger.error(f"비밀번호 입력 중 오류: {e}")
                                    password_attempt += 1
                                    password = None
                                    continue

                            # 최대 시도 횟수 초과
                            if password_attempt >= max_password_attempts:
                                logger.error(
                                    f"비밀번호 입력 실패: 최대 시도 횟수({max_password_attempts}) 초과"
                                )
                                return {
                                    "success": False,
                                    "error": f"비밀번호 입력 실패: 최대 시도 횟수({max_password_attempts}) 초과",
                                }

                            if not password:
                                return {
                                    "success": False,
                                    "error": "비밀번호를 입력할 수 없습니다.",
                                }

                        # 비밀번호가 있으면 stdin을 통해 sudo -S로 전달 (보안: shell 명령에 포함하지 않음)
                        if password:
                            # sudo -S는 stdin에서 비밀번호를 읽음
                            process = subprocess.Popen(
                                ["sudo", "-S", "bash", str(start_dfs_script)],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                stdin=subprocess.PIPE,
                                start_new_session=True,
                                env=hdfs_env,
                                cwd=str(hadoop_path),  # 하둡 경로에서 실행
                            )
                            # 비밀번호를 stdin으로 전달 (보안: 즉시 메모리에서 삭제)
                            try:
                                process.stdin.write((password + "\n").encode())
                                process.stdin.flush()
                            finally:
                                # 보안: 비밀번호 즉시 삭제
                                temp_password = password
                                password = None
                                del temp_password
                                if process.stdin:
                                    process.stdin.close()
                        else:
                            # 비밀번호 없이 실행 (sudo 없이 실행 가능한 경우)
                            process = subprocess.Popen(
                                ["bash", str(start_dfs_script)],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                start_new_session=True,
                                env=hdfs_env,
                                cwd=str(hadoop_path),  # 하둡 경로에서 실행
                            )

                        # HDFS 시작 대기 및 포트 확인
                        max_retries = 15
                        retry_interval = 2

                        for attempt in range(max_retries):
                            time.sleep(retry_interval)

                            # 프로세스가 종료되었는지 확인
                            if process.poll() is not None:
                                stdout, stderr = process.communicate()
                                if stderr:
                                    stderr_text = stderr.decode(
                                        "utf-8", errors="ignore"
                                    )
                                    # 예상된 경고 메시지 필터링
                                    expected_warnings = [
                                        "ssh:",
                                        "connection refused",
                                        "nativecodeloader",
                                        "unable to load native-hadoop library",
                                        "using builtin-java classes",
                                    ]
                                    is_expected_warning = any(
                                        warning in stderr_text.lower()
                                        for warning in expected_warnings
                                    )

                                    if is_expected_warning:
                                        # 예상된 경고는 DEBUG 레벨로만 로깅 (단일 노드 모드에서는 정상)
                                        logger.debug(
                                            f"HDFS 시작 경고 (정상, 무시 가능): {stderr_text[:300]}"
                                        )
                                    else:
                                        # 예상치 못한 에러만 WARNING으로 로깅
                                        logger.warning(
                                            f"HDFS 시작 스크립트 오류: {stderr_text[:500]}"
                                        )
                                        break

                            # 포트 확인
                            for port in namenode_ports:
                                try:
                                    sock = socket.socket(
                                        socket.AF_INET, socket.SOCK_STREAM
                                    )
                                    sock.settimeout(1)
                                    result = sock.connect_ex(("localhost", port))
                                    sock.close()
                                    if result == 0:
                                        logger.info(
                                            f"✅ HDFS 시작 성공 (포트 {port}, 시도 {attempt + 1}/{max_retries})"
                                        )
                                        return {
                                            "success": True,
                                            "message": f"HDFS가 시작되었습니다 (포트 {port})",
                                        }
                                except Exception as e:
                                    logger.debug(
                                        f"HDFS 포트 확인 오류 (포트 {port}): {e}"
                                    )

                        return {
                            "success": False,
                            "error": f"HDFS 시작 후 포트 확인 실패 (최대 {max_retries * retry_interval}초 대기)",
                        }
                else:
                    return {
                        "success": False,
                        "error": f"HDFS 시작 스크립트를 찾을 수 없습니다: {start_dfs_script}",
                    }
            else:
                logger.warning(
                    "HADOOP_HOME 환경 변수가 설정되지 않았고 일반 경로에서도 찾을 수 없습니다. "
                    "HDFS는 수동으로 시작해야 합니다."
                )
                return {
                    "success": False,
                    "error": "HADOOP_HOME 환경 변수가 설정되지 않았고 일반 경로에서도 찾을 수 없습니다. HDFS는 수동으로 시작해야 합니다.",
                }
        except Exception as e:
            logger.error(f"HDFS 체크 및 시작 중 오류: {e}")
            return {"success": False, "error": f"HDFS 시작 중 오류: {str(e)}"}
