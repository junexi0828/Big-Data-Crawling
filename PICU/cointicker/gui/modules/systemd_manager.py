"""
systemd 서비스 관리 모듈
GUI 수동 제어와 systemd 서비스 간 충돌 방지
"""

import subprocess
from typing import Dict, Optional
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
        try:
            systemd_service = SystemdManager.SERVICE_NAMES.get(service_name)
            if not systemd_service:
                return False

            result = subprocess.run(
                ["systemctl", "is-active", systemd_service],
                capture_output=True,
                text=True,
                timeout=5,
            )

            # 'active' 반환 시 실행 중
            return result.stdout.strip() == "active"

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
        try:
            systemd_service = SystemdManager.SERVICE_NAMES.get(service_name)
            if not systemd_service:
                return False

            result = subprocess.run(
                ["systemctl", "is-enabled", systemd_service],
                capture_output=True,
                text=True,
                timeout=5,
            )

            # 'enabled' 반환 시 활성화됨
            return result.stdout.strip() == "enabled"

        except Exception as e:
            logger.debug(f"서비스 활성화 상태 확인 중 오류 ({service_name}): {e}")
            return False

    @staticmethod
    def get_service_status(service_name: str) -> Dict[str, any]:
        """
        서비스 상태 정보 반환

        Args:
            service_name: 서비스 이름

        Returns:
            {"running": bool, "enabled": bool, "exists": bool}
        """
        try:
            systemd_service = SystemdManager.SERVICE_NAMES.get(service_name)
            if not systemd_service:
                return {"running": False, "enabled": False, "exists": False}

            # 서비스 파일 존재 여부 확인
            exists_result = subprocess.run(
                ["systemctl", "cat", systemd_service],
                capture_output=True,
                timeout=5,
            )
            exists = exists_result.returncode == 0

            return {
                "running": SystemdManager.is_service_running(service_name),
                "enabled": SystemdManager.is_service_enabled(service_name),
                "exists": exists,
            }

        except Exception as e:
            logger.error(f"서비스 상태 조회 오류 ({service_name}): {e}")
            return {"running": False, "enabled": False, "exists": False}

    @staticmethod
    def check_conflict_with_gui(service_name: str) -> Optional[str]:
        """
        GUI 수동 제어와 systemd 서비스 간 충돌 확인

        Args:
            service_name: 서비스 이름

        Returns:
            충돌 시 경고 메시지, 없으면 None
        """
        status = SystemdManager.get_service_status(service_name)

        if not status["exists"]:
            return None  # 서비스가 설치되지 않았으면 충돌 없음

        if status["running"]:
            return (
                f"{service_name} systemd 서비스가 이미 실행 중입니다.\n\n"
                f"GUI에서 수동으로 제어하려면 먼저 systemd 서비스를 중지하세요:\n"
                f"sudo systemctl stop {SystemdManager.SERVICE_NAMES[service_name]}\n\n"
                f"또는 Config 탭에서 서비스를 중지할 수 있습니다."
            )

        if status["enabled"]:
            return (
                f"{service_name} systemd 서비스가 부팅 시 자동 시작으로 설정되어 있습니다.\n\n"
                f"GUI에서 수동 제어 시 시스템 재부팅 후 서비스가 자동으로 시작될 수 있습니다.\n"
                f"systemd 자동 시작을 비활성화하려면:\n"
                f"sudo systemctl disable {SystemdManager.SERVICE_NAMES[service_name]}"
            )

        return None

    @staticmethod
    def stop_service(service_name: str) -> Dict[str, any]:
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
