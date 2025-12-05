"""
시스템 자원 모니터링 매니저
CPU, 메모리 사용량을 모니터링하는 클래스
"""

import sys
from typing import Dict, Any, Optional

try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None

from shared.logger import setup_logger

logger = setup_logger(__name__)


class SystemMonitor:
    """시스템 자원 (CPU, 메모리) 사용량을 모니터링하는 클래스"""

    def __init__(self):
        """
        초기화. psutil 사용 가능 여부 확인.
        """
        if not PSUTIL_AVAILABLE:
            logger.warning(
                "psutil 라이브러리가 설치되지 않았습니다. 시스템 모니터링이 비활성화됩니다."
            )
            self.available = False
            return

        if not hasattr(psutil, "cpu_percent"):
            logger.error("psutil 라이브러리 버전이 너무 낮습니다.")
            self.available = False
            return

        self.available = True
        # CPU 사용량 초기 측정 (비동기 모드)
        # interval=None: 마지막 호출 이후의 사용량 반환 (논블로킹)
        try:
            psutil.cpu_percent(interval=None)
        except Exception as e:
            logger.warning(f"CPU 사용량 초기 측정 실패: {e}")
            self.available = False

    def get_system_stats(self) -> Dict[str, Any]:
        """
        현재 시스템의 CPU 및 메모리 사용량을 가져옵니다.

        Returns:
            CPU 및 메모리 사용량 정보를 담은 딕셔너리
        """
        if not self.available:
            return {
                "success": False,
                "error": "psutil이 사용 불가능합니다.",
            }

        try:
            # CPU 사용량 (interval=None: 논블로킹, 마지막 호출 이후 사용량)
            # 첫 호출은 0을 반환할 수 있으므로, 두 번째 호출부터 정확한 값 반환
            cpu_percent = psutil.cpu_percent(interval=None)

            # 가상 메모리 사용량
            memory_info = psutil.virtual_memory()
            memory_percent = memory_info.percent
            memory_used_gb = round(memory_info.used / (1024**3), 2)
            memory_total_gb = round(memory_info.total / (1024**3), 2)

            # 디스크 사용량 (선택적, 루트 디렉토리)
            try:
                disk_info = psutil.disk_usage("/")
                disk_percent = disk_info.percent
                disk_used_gb = round(disk_info.used / (1024**3), 2)
                disk_total_gb = round(disk_info.total / (1024**3), 2)
            except Exception:
                disk_percent = None
                disk_used_gb = None
                disk_total_gb = None

            # 네트워크 I/O (초당 바이트)
            try:
                net_io = psutil.net_io_counters()
                net_sent_mb = round(net_io.bytes_sent / (1024**2), 2)
                net_recv_mb = round(net_io.bytes_recv / (1024**2), 2)
            except Exception:
                net_sent_mb = None
                net_recv_mb = None

            # 실행 중인 프로세스 수
            try:
                process_count = len(psutil.pids())
            except Exception:
                process_count = None

            return {
                "success": True,
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "memory_used_gb": memory_used_gb,
                "memory_total_gb": memory_total_gb,
                "disk_percent": disk_percent,
                "disk_used_gb": disk_used_gb,
                "disk_total_gb": disk_total_gb,
                "network_sent_mb": net_sent_mb,
                "network_recv_mb": net_recv_mb,
                "process_count": process_count,
            }
        except Exception as e:
            logger.warning(f"시스템 자원 정보 수집 실패: {e}")
            return {"success": False, "error": str(e)}

    def is_resource_critical(
        self, stats: Optional[Dict[str, Any]] = None
    ) -> Dict[str, bool]:
        """
        시스템 자원이 위험 수준인지 확인

        Args:
            stats: 시스템 통계 (None이면 자동 수집)

        Returns:
            각 자원의 위험 여부 딕셔너리
        """
        if stats is None:
            stats = self.get_system_stats()

        if not stats.get("success"):
            return {"cpu": False, "memory": False, "disk": False}

        cpu_percent = stats.get("cpu_percent", 0)
        memory_percent = stats.get("memory_percent", 0)
        disk_percent = stats.get("disk_percent", 0)

        return {
            "cpu": cpu_percent > 90,  # CPU 90% 이상
            "memory": memory_percent > 90,  # 메모리 90% 이상
            "disk": disk_percent is not None and disk_percent > 90,  # 디스크 90% 이상
        }


if __name__ == "__main__":
    # 테스트 코드
    monitor = SystemMonitor()
    if monitor.available:
        stats = monitor.get_system_stats()
        if stats["success"]:
            print(f"CPU 사용량: {stats['cpu_percent']}%")
            print(
                f"메모리 사용량: {stats['memory_percent']}% ({stats['memory_used_gb']}GB / {stats['memory_total_gb']}GB)"
            )
            if stats.get("disk_percent") is not None:
                print(
                    f"디스크 사용량: {stats['disk_percent']}% ({stats['disk_used_gb']}GB / {stats['disk_total_gb']}GB)"
                )

            critical = monitor.is_resource_critical(stats)
            if any(critical.values()):
                print("⚠️ 위험 수준 자원 감지:")
                if critical["cpu"]:
                    print("  - CPU 사용량이 90%를 초과했습니다")
                if critical["memory"]:
                    print("  - 메모리 사용량이 90%를 초과했습니다")
                if critical["disk"]:
                    print("  - 디스크 사용량이 90%를 초과했습니다")
    else:
        print("⚠️ psutil이 사용 불가능합니다. 시스템 모니터링이 비활성화됩니다.")
