"""
SSH 매니저
SSH 연결 및 설정을 관리하는 클래스
"""

import subprocess
import getpass
import platform
from pathlib import Path
from typing import Optional

from shared.logger import setup_logger
from gui.core.timing_config import TimingConfig

logger = setup_logger(__name__)


class SSHManager:
    """SSH 연결 및 설정 관리 클래스"""

    def __init__(self):
        """초기화"""
        pass

    def test_connection(self, hostname: str = "localhost", timeout: int = 2) -> bool:
        """
        SSH 연결 테스트

        Args:
            hostname: 호스트명 (기본: localhost)
            timeout: 연결 타임아웃 (초)

        Returns:
            SSH 연결 성공 여부
        """
        try:
            ssh_test = subprocess.run(
                [
                    "ssh",
                    "-o",
                    "StrictHostKeyChecking=no",
                    "-o",
                    f"ConnectTimeout={timeout}",
                    hostname,
                    "exit",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout + 3,
            )
            return ssh_test.returncode == 0
        except Exception as e:
            logger.debug(f"SSH 연결 테스트 실패 {hostname}: {e}")
            return False

    def setup_local_ssh(self) -> bool:
        """
        단일 노드 모드를 위한 로컬 SSH 자동 설정

        Returns:
            SSH 설정 성공 여부
        """
        try:
            home_dir = Path.home()
            ssh_dir = home_dir / ".ssh"

            # .ssh 디렉토리 생성
            ssh_dir.mkdir(mode=0o700, exist_ok=True)

            # macOS에서 SSH 서버 활성화 확인 및 시도
            if platform.system() == "Darwin":  # macOS
                logger.info("macOS 감지: SSH 서버 활성화 확인 중...")
                # SSH 서버 상태 확인
                ssh_status = subprocess.run(
                    ["sudo", "systemsetup", "-getremotelogin"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=300,  # 타임아웃: 5분 (비밀번호 입력 대기)
                )

                if ssh_status.returncode == 0:
                    status_output = ssh_status.stdout.decode(
                        "utf-8", errors="ignore"
                    ).strip()
                    if "On" not in status_output:
                        logger.info(
                            "SSH 서버가 비활성화되어 있습니다. 활성화를 시도합니다..."
                        )
                        logger.warning(
                            "⚠️ SSH 서버 활성화는 관리자 권한이 필요합니다. "
                            "수동으로 활성화하려면: sudo systemsetup -setremotelogin on"
                        )
                        # 비대화형으로 활성화 시도 (비밀번호 필요하므로 실패할 수 있음)
                        enable_ssh = subprocess.run(
                            ["sudo", "systemsetup", "-setremotelogin", "on"],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            timeout=300,  # 타임아웃: 5분 (비밀번호 입력 대기)
                            input=b"\n",  # 비밀번호 프롬프트에 빈 입력
                        )
                        if enable_ssh.returncode == 0:
                            logger.info("✅ SSH 서버 활성화 완료")
                            import time

                            ssh_server_delay = TimingConfig.get(
                                "ssh.server_start_delay", 2
                            )
                            time.sleep(ssh_server_delay)
                        else:
                            logger.warning(
                                "SSH 서버 자동 활성화 실패. 수동으로 활성화해야 합니다."
                            )
                    else:
                        logger.debug("SSH 서버가 이미 활성화되어 있습니다.")
                else:
                    logger.debug(
                        "SSH 서버 상태 확인 실패 (권한 필요). 계속 진행합니다."
                    )

            # SSH 키 생성 (없는 경우)
            private_key = ssh_dir / "id_rsa"
            public_key = ssh_dir / "id_rsa.pub"

            if not private_key.exists():
                logger.info("SSH 키 생성 중...")
                keygen_result = subprocess.run(
                    ["ssh-keygen", "-t", "rsa", "-P", "", "-f", str(private_key)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=10,
                )
                if keygen_result.returncode != 0:
                    logger.error(
                        f"SSH 키 생성 실패: {keygen_result.stderr.decode('utf-8', errors='ignore')}"
                    )
                    return False
                logger.info("✅ SSH 키 생성 완료")
            else:
                logger.debug("SSH 키가 이미 존재합니다.")

            # authorized_keys에 공개키 추가
            if public_key.exists():
                authorized_keys = ssh_dir / "authorized_keys"
                public_key_content = public_key.read_text().strip()

                # authorized_keys 파일이 없거나 현재 키가 없으면 추가
                if not authorized_keys.exists():
                    authorized_keys.write_text(public_key_content + "\n")
                    authorized_keys.chmod(0o600)
                    logger.info("✅ authorized_keys 파일 생성 및 공개키 추가 완료")
                else:
                    authorized_keys_content = authorized_keys.read_text()
                    if public_key_content not in authorized_keys_content:
                        with authorized_keys.open("a") as f:
                            f.write(public_key_content + "\n")
                        authorized_keys.chmod(0o600)
                        logger.info("✅ authorized_keys에 공개키 추가 완료")
                    else:
                        logger.debug("공개키가 이미 authorized_keys에 있습니다.")

                # known_hosts에 localhost 추가 (StrictHostKeyChecking 우회)
                known_hosts = ssh_dir / "known_hosts"
                if (
                    not known_hosts.exists()
                    or "localhost" not in known_hosts.read_text()
                ):
                    logger.debug("known_hosts에 localhost 추가 중...")
                    # ssh-keyscan으로 localhost 키 추가
                    keyscan_result = subprocess.run(
                        ["ssh-keyscan", "-H", "localhost"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        timeout=5,
                    )
                    if keyscan_result.returncode == 0:
                        keys = keyscan_result.stdout.decode("utf-8", errors="ignore")
                        with known_hosts.open("a") as f:
                            f.write(keys)
                        known_hosts.chmod(0o600)
                        logger.debug("✅ known_hosts에 localhost 추가 완료")

                return True
            else:
                logger.error("공개키 파일을 찾을 수 없습니다.")
                return False

        except Exception as e:
            logger.error(f"로컬 SSH 설정 중 오류: {e}")
            return False
