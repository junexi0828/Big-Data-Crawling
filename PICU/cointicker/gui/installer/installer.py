"""
설치 마법사
의존성 자동 설치 및 설정 자동화
"""

import sys
import subprocess
import platform
from pathlib import Path
from typing import List, Dict, Tuple
import json

from shared.logger import setup_logger

logger = setup_logger(__name__)


class DependencyInstaller:
    """의존성 설치 관리자"""

    def __init__(self, project_root: str = None):
        """
        초기화

        Args:
            project_root: 프로젝트 루트 경로 (None이면 자동 탐지)
        """
        self.system = platform.system()
        self.python_version = sys.version_info

        # 프로젝트 루트 찾기
        if project_root:
            self.project_root = Path(project_root)
        else:
            # 현재 파일 위치에서 PICU 또는 cointicker 루트 찾기
            current_path = Path(__file__).resolve()
            if "PICU" in current_path.parts:
                # PICU 루트 찾기
                picu_index = current_path.parts.index("PICU")
                self.project_root = Path("/").joinpath(
                    *current_path.parts[: picu_index + 1]
                )
            else:
                # cointicker 루트 찾기
                cointicker_index = current_path.parts.index("cointicker")
                self.project_root = Path("/").joinpath(
                    *current_path.parts[: cointicker_index + 1]
                )

        # requirements.txt 찾기 (PICU 루트 우선, 없으면 cointicker)
        picu_requirements = self.project_root / "requirements.txt"
        cointicker_requirements = self.project_root / "cointicker" / "requirements.txt"

        if picu_requirements.exists():
            self.requirements_file = picu_requirements
        elif cointicker_requirements.exists():
            self.requirements_file = cointicker_requirements
        else:
            self.requirements_file = Path("requirements.txt")  # 현재 디렉토리

        self.install_log = []

    def check_python_version(self) -> Tuple[bool, str]:
        """
        Python 버전 확인

        Returns:
            (호환 여부, 메시지)
        """
        if self.python_version.major < 3 or (
            self.python_version.major == 3 and self.python_version.minor < 8
        ):
            return (
                False,
                f"Python 3.8 이상이 필요합니다. 현재 버전: {self.python_version.major}.{self.python_version.minor}",
            )
        return (
            True,
            f"Python 버전 확인 완료: {self.python_version.major}.{self.python_version.minor}.{self.python_version.micro}",
        )

    def check_pip(self) -> Tuple[bool, str]:
        """
        pip 확인

        Returns:
            (설치 여부, 메시지)
        """
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                return True, f"pip 확인 완료: {result.stdout.strip()}"
            else:
                return False, "pip가 설치되지 않았습니다"
        except Exception as e:
            return False, f"pip 확인 실패: {str(e)}"

    def install_system_dependencies(self) -> Tuple[bool, List[str]]:
        """
        시스템 의존성 설치

        Returns:
            (성공 여부, 로그 목록)
        """
        logs = []

        if self.system == "Linux":
            # Linux 시스템 의존성
            packages = [
                "python3-tk",  # tkinter
                "python3-dev",
                "build-essential",
                "libssl-dev",
                "libffi-dev",
            ]

            try:
                # apt-get 업데이트
                subprocess.run(
                    ["sudo", "apt-get", "update"],
                    check=True,
                    capture_output=True,
                    timeout=300,
                )
                logs.append("패키지 목록 업데이트 완료")

                # 패키지 설치
                for package in packages:
                    try:
                        subprocess.run(
                            ["sudo", "apt-get", "install", "-y", package],
                            check=True,
                            capture_output=True,
                            timeout=300,
                        )
                        logs.append(f"패키지 설치 완료: {package}")
                    except subprocess.CalledProcessError as e:
                        logs.append(f"패키지 설치 실패: {package} - {e}")
                        return False, logs

                return True, logs
            except Exception as e:
                logs.append(f"시스템 의존성 설치 실패: {str(e)}")
                return False, logs

        elif self.system == "Darwin":  # macOS
            # macOS는 Homebrew 사용
            try:
                # Homebrew 확인
                subprocess.run(
                    ["brew", "--version"], check=True, capture_output=True, timeout=10
                )
                logs.append("Homebrew 확인 완료")

                # Python-tk는 macOS에 기본 포함되어 있지만, PyQt5는 별도 설치 필요
                logs.append("macOS는 기본 Python-tk 지원 (PyQt5는 pip로 설치)")
                return True, logs
            except FileNotFoundError:
                logs.append("Homebrew가 설치되지 않았습니다. 수동으로 설치해주세요.")
                return False, logs
            except Exception as e:
                logs.append(f"시스템 의존성 확인 실패: {str(e)}")
                return False, logs

        elif self.system == "Windows":
            # Windows는 별도 시스템 의존성 없음
            logs.append("Windows는 시스템 의존성 설치 불필요")
            return True, logs

        else:
            logs.append(f"지원하지 않는 시스템: {self.system}")
            return False, logs

    def install_python_dependencies(
        self, use_venv: bool = True
    ) -> Tuple[bool, List[str]]:
        """
        Python 의존성 설치

        Args:
            use_venv: 가상환경 사용 여부

        Returns:
            (성공 여부, 로그 목록)
        """
        logs = []

        if not self.requirements_file.exists():
            logs.append(
                f"requirements.txt 파일을 찾을 수 없습니다: {self.requirements_file}"
            )
            return False, logs

        try:
            # pip 업그레이드
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
                check=True,
                capture_output=True,
                timeout=300,
            )
            logs.append("pip 업그레이드 완료")

            # requirements.txt 설치
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "-r",
                    str(self.requirements_file),
                ],
                capture_output=True,
                text=True,
                timeout=1800,  # 30분 타임아웃
            )

            if result.returncode == 0:
                logs.append("Python 의존성 설치 완료")
                logs.extend(result.stdout.split("\n")[-10:])  # 마지막 10줄만
                return True, logs
            else:
                logs.append("Python 의존성 설치 실패")
                logs.extend(result.stderr.split("\n")[-10:])
                return False, logs
        except subprocess.TimeoutExpired:
            logs.append("의존성 설치 타임아웃 (30분 초과)")
            return False, logs
        except Exception as e:
            logs.append(f"Python 의존성 설치 오류: {str(e)}")
            return False, logs

    def create_virtual_environment(
        self, venv_path: str = "venv"
    ) -> Tuple[bool, List[str]]:
        """
        가상환경 생성

        Args:
            venv_path: 가상환경 경로

        Returns:
            (성공 여부, 로그 목록)
        """
        logs = []
        venv_dir = Path(venv_path)

        if venv_dir.exists():
            logs.append(f"가상환경이 이미 존재합니다: {venv_path}")
            return True, logs

        try:
            subprocess.run(
                [sys.executable, "-m", "venv", venv_path],
                check=True,
                capture_output=True,
                timeout=60,
            )
            logs.append(f"가상환경 생성 완료: {venv_path}")
            return True, logs
        except Exception as e:
            logs.append(f"가상환경 생성 실패: {str(e)}")
            return False, logs

    def verify_installation(self) -> Tuple[bool, List[str]]:
        """
        설치 확인

        Returns:
            (성공 여부, 로그 목록)
        """
        logs = []
        # 패키지 이름과 import 이름 매핑
        required_packages = {
            "scrapy": "scrapy",
            "fastapi": "fastapi",
            "sqlalchemy": "sqlalchemy",
            "pandas": "pandas",
            "transformers": "transformers",
            "paramiko": "paramiko",
            "pyyaml": "yaml",  # pyyaml은 yaml로 import됨
            "PyQt5": "PyQt5",
        }

        failed = []
        for package_name, import_name in required_packages.items():
            try:
                result = subprocess.run(
                    [sys.executable, "-c", f"import {import_name}; print('OK')"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode == 0:
                    logs.append(f"✓ {package_name} 설치 확인")
                else:
                    logs.append(f"✗ {package_name} 설치 확인 실패")
                    failed.append(package_name)
            except Exception as e:
                logs.append(f"✗ {package_name} 확인 오류: {str(e)}")
                failed.append(package_name)

        if len(failed) > 0:
            return False, logs
        return True, logs

    def run_full_installation(self, create_venv: bool = True) -> Dict[str, any]:
        """
        전체 설치 프로세스 실행

        Args:
            create_venv: 가상환경 생성 여부

        Returns:
            설치 결과
        """
        result = {"success": False, "steps": [], "errors": [], "logs": []}

        # 1. Python 버전 확인
        success, msg = self.check_python_version()
        result["steps"].append(
            {"name": "Python 버전 확인", "success": success, "message": msg}
        )
        if not success:
            result["errors"].append(msg)
            return result

        # 2. pip 확인
        success, msg = self.check_pip()
        result["steps"].append({"name": "pip 확인", "success": success, "message": msg})
        if not success:
            result["errors"].append(msg)
            return result

        # 3. 가상환경 생성 (선택)
        if create_venv:
            success, logs = self.create_virtual_environment()
            result["steps"].append(
                {"name": "가상환경 생성", "success": success, "logs": logs}
            )
            if not success:
                result["errors"].extend(logs)

        # 4. 시스템 의존성 설치
        success, logs = self.install_system_dependencies()
        result["steps"].append(
            {"name": "시스템 의존성 설치", "success": success, "logs": logs}
        )
        result["logs"].extend(logs)
        if not success:
            result["errors"].extend(
                [log for log in logs if "실패" in log or "오류" in log]
            )

        # 5. Python 의존성 설치
        success, logs = self.install_python_dependencies(use_venv=create_venv)
        result["steps"].append(
            {"name": "Python 의존성 설치", "success": success, "logs": logs}
        )
        result["logs"].extend(logs)
        if not success:
            result["errors"].extend(
                [log for log in logs if "실패" in log or "오류" in log]
            )

        # 6. 설치 확인
        success, logs = self.verify_installation()
        result["steps"].append({"name": "설치 확인", "success": success, "logs": logs})
        result["logs"].extend(logs)
        if not success:
            result["errors"].extend([log for log in logs if "✗" in log])

        result["success"] = len(result["errors"]) == 0
        return result
