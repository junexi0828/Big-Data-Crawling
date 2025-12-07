"""
systemd 서비스 관리 모듈
GUI 수동 제어와 systemd 서비스 간 충돌 방지
"""

import subprocess
from typing import Dict, Optional, Any
from shared.logger import setup_logger

logger = setup_logger(__name__)


class SystemdManager:
    """systemd 서비스 관리 클래스"""

    SERVICE_NAMES = {
        "tier1_orchestrator": "cointicker-orchestrator",
        "tier2_scheduler": "cointicker-tier2-scheduler",
    }

    @staticmethod
    def is_service_running(service_name: str) -> bool:
        """
        서비스가 실행 중인지 확인

        Args:
            service_name: 서비스 이름 (tier1_orchestrator 또는 tier2_scheduler)

        Returns:
            실행 중이면 True, 아니면 False
        """
        import platform

        system = platform.system()

        try:
            systemd_service = SystemdManager.SERVICE_NAMES.get(service_name)
            if not systemd_service:
                return False

            # Linux: systemctl 사용
            if system == "Linux":
                try:
                    result = subprocess.run(
                        ["systemctl", "is-active", systemd_service],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )
                    # 'active' 반환 시 실행 중
                    return result.stdout.strip() == "active"
                except FileNotFoundError:
                    # Linux인데 systemctl이 없는 경우 (싱글노드 등)
                    logger.warning(
                        f"⚠️ systemctl을 찾을 수 없습니다. ({service_name})\n"
                        "Linux 시스템에서는 systemctl이 필요합니다.\n"
                        "systemd가 설치되어 있는지 확인하세요."
                    )
                    return False

            # macOS: launchctl 시도
            elif system == "Darwin":
                try:
                    # launchctl로 서비스 확인 시도
                    # macOS에서는 plist 파일 이름으로 확인
                    plist_name = f"com.cointicker.{systemd_service}"
                    result = subprocess.run(
                        ["launchctl", "list", plist_name],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )
                    # launchctl list가 성공하면 서비스가 로드된 것
                    return result.returncode == 0
                except FileNotFoundError:
                    logger.debug(f"launchctl을 찾을 수 없습니다. ({service_name})")
                    return False
                except Exception as e:
                    logger.debug(f"launchctl 서비스 확인 오류 ({service_name}): {e}")
                    return False

            # 기타 OS
            else:
                logger.debug(f"지원하지 않는 OS입니다: {system}")
                return False

        except Exception as e:
            logger.debug(f"서비스 상태 확인 중 오류 ({service_name}): {e}")
            return False

    @staticmethod
    def is_service_enabled(service_name: str) -> bool:
        """
        서비스가 부팅 시 자동 시작으로 설정되어 있는지 확인

        Args:
            service_name: 서비스 이름

        Returns:
            활성화되어 있으면 True, 아니면 False
        """
        import platform

        system = platform.system()

        try:
            systemd_service = SystemdManager.SERVICE_NAMES.get(service_name)
            if not systemd_service:
                return False

            # Linux: systemctl 사용
            if system == "Linux":
                try:
                    result = subprocess.run(
                        ["systemctl", "is-enabled", systemd_service],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )
                    # 'enabled' 반환 시 활성화됨
                    return result.stdout.strip() == "enabled"
                except FileNotFoundError:
                    # Linux인데 systemctl이 없는 경우 (싱글노드 등)
                    logger.warning(
                        f"⚠️ systemctl을 찾을 수 없습니다. ({service_name})\n"
                        "Linux 시스템에서는 systemctl이 필요합니다.\n"
                        "systemd가 설치되어 있는지 확인하세요."
                    )
                    return False

            # macOS: launchctl 시도
            elif system == "Darwin":
                try:
                    # macOS에서는 plist 파일 존재 여부로 확인
                    plist_name = f"com.cointicker.{systemd_service}"
                    from pathlib import Path
                    import os

                    # LaunchAgents 디렉토리 확인
                    home = Path.home()
                    launch_agents = home / "Library" / "LaunchAgents"
                    plist_path = launch_agents / f"{plist_name}.plist"
                    return plist_path.exists()
                except Exception as e:
                    logger.debug(
                        f"launchctl 서비스 활성화 확인 오류 ({service_name}): {e}"
                    )
                    return False

            # 기타 OS
            else:
                logger.debug(f"지원하지 않는 OS입니다: {system}")
                return False

        except Exception as e:
            logger.debug(f"서비스 활성화 상태 확인 중 오류 ({service_name}): {e}")
            return False

    @staticmethod
    def get_service_status(service_name: str) -> Dict[str, Any]:
        """
        서비스 상태 정보 반환

        Args:
            service_name: 서비스 이름

        Returns:
            {"running": bool, "enabled": bool, "exists": bool}
        """
        import platform

        system = platform.system()

        try:
            systemd_service = SystemdManager.SERVICE_NAMES.get(service_name)
            if not systemd_service:
                return {"running": False, "enabled": False, "exists": False}

            # Linux: systemctl 사용
            if system == "Linux":
                try:
                    # 서비스 파일 존재 여부 확인
                    exists_result = subprocess.run(
                        ["systemctl", "cat", systemd_service],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )
                    exists = exists_result.returncode == 0

                    return {
                        "running": SystemdManager.is_service_running(service_name),
                        "enabled": SystemdManager.is_service_enabled(service_name),
                        "exists": exists,
                    }
                except FileNotFoundError:
                    # Linux인데 systemctl이 없는 경우 (싱글노드 등)
                    logger.warning(
                        f"⚠️ systemctl을 찾을 수 없습니다. ({service_name})\n"
                        "Linux 시스템에서는 systemctl이 필요합니다.\n"
                        "systemd가 설치되어 있는지 확인하세요."
                    )
                    return {"running": False, "enabled": False, "exists": False}

            # macOS: launchctl 사용
            elif system == "Darwin":
                try:
                    from pathlib import Path

                    # plist 파일 존재 여부 확인
                    plist_name = f"com.cointicker.{systemd_service}"
                    home = Path.home()
                    launch_agents = home / "Library" / "LaunchAgents"
                    plist_path = launch_agents / f"{plist_name}.plist"
                    exists = plist_path.exists()

                    return {
                        "running": SystemdManager.is_service_running(service_name),
                        "enabled": SystemdManager.is_service_enabled(service_name),
                        "exists": exists,
                    }
                except Exception as e:
                    logger.debug(
                        f"launchctl 서비스 상태 조회 오류 ({service_name}): {e}"
                    )
                    return {"running": False, "enabled": False, "exists": False}

            # 기타 OS
            else:
                logger.debug(f"지원하지 않는 OS입니다: {system}")
                return {"running": False, "enabled": False, "exists": False}

        except Exception as e:
            logger.debug(f"서비스 상태 조회 오류 ({service_name}): {e}")
            return {"running": False, "enabled": False, "exists": False}

    @staticmethod
    def check_conflict_with_gui(service_name: str) -> Optional[str]:
        """
        GUI 수동 제어와 systemd/launchctl 서비스 간 충돌 확인

        Args:
            service_name: 서비스 이름

        Returns:
            충돌 시 경고 메시지, 없으면 None
        """
        import platform

        system = platform.system()

        # Linux가 아니면 launchctl 확인 (macOS)
        if system != "Linux" and system != "Darwin":
            return None

        status = SystemdManager.get_service_status(service_name)

        if not status["exists"]:
            return None  # 서비스가 설치되지 않았으면 충돌 없음

        systemd_service = SystemdManager.SERVICE_NAMES[service_name]

        if status["running"]:
            if system == "Linux":
                return (
                    f"{service_name} systemd 서비스가 이미 실행 중입니다.\n\n"
                    f"GUI에서 수동으로 제어하려면 먼저 systemd 서비스를 중지하세요:\n"
                    f"sudo systemctl stop {systemd_service}\n\n"
                    f"또는 Config 탭에서 서비스를 중지할 수 있습니다."
                )
            elif system == "Darwin":
                return (
                    f"{service_name} launchctl 서비스가 이미 실행 중입니다.\n\n"
                    f"GUI에서 수동으로 제어하려면 먼저 launchctl 서비스를 중지하세요:\n"
                    f"launchctl unload ~/Library/LaunchAgents/com.cointicker.{systemd_service}.plist\n\n"
                    f"또는 Config 탭에서 서비스를 중지할 수 있습니다."
                )

        if status["enabled"]:
            if system == "Linux":
                return (
                    f"{service_name} systemd 서비스가 부팅 시 자동 시작으로 설정되어 있습니다.\n\n"
                    f"GUI에서 수동 제어 시 시스템 재부팅 후 서비스가 자동으로 시작될 수 있습니다.\n"
                    f"systemd 자동 시작을 비활성화하려면:\n"
                    f"sudo systemctl disable {systemd_service}"
                )
            elif system == "Darwin":
                return (
                    f"{service_name} launchctl 서비스가 부팅 시 자동 시작으로 설정되어 있습니다.\n\n"
                    f"GUI에서 수동 제어 시 시스템 재부팅 후 서비스가 자동으로 시작될 수 있습니다.\n"
                    f"launchctl 자동 시작을 비활성화하려면:\n"
                    f"launchctl unload ~/Library/LaunchAgents/com.cointicker.{systemd_service}.plist"
                )

        return None

    @staticmethod
    def stop_service(service_name: str) -> Dict[str, Any]:
        """
        서비스 중지

        Args:
            service_name: 서비스 이름

        Returns:
            {"success": bool, "message": str}
        """
        try:
            systemd_service = SystemdManager.SERVICE_NAMES.get(service_name)
            if not systemd_service:
                return {"success": False, "message": "알 수 없는 서비스"}

            result = subprocess.run(
                ["sudo", "systemctl", "stop", systemd_service],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                return {"success": True, "message": f"{service_name} 서비스 중지 완료"}
            else:
                return {
                    "success": False,
                    "message": f"서비스 중지 실패: {result.stderr}",
                }

        except Exception as e:
            logger.error(f"서비스 중지 오류 ({service_name}): {e}")
            return {"success": False, "message": str(e)}
