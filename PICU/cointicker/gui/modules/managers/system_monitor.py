"""
시스템 자원 모니터링 매니저
CPU, 메모리 사용량을 모니터링하는 클래스
"""

import sys
import time
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

    def __init__(self, cache_ttl: float = 5.0):
        """
        초기화. psutil 사용 가능 여부 확인.

        Args:
            cache_ttl: 캐시 유효 시간 (초) - 기본 5초
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
        self.cache_ttl = cache_ttl
        self._cached_stats: Optional[Dict[str, Any]] = None
        self._last_update_time: float = 0

        # CPU 사용량 초기 측정 (비동기 모드)
        # interval=None: 마지막 호출 이후의 사용량 반환 (논블로킹)
        try:
            psutil.cpu_percent(interval=None)
        except Exception as e:
            logger.warning(f"CPU 사용량 초기 측정 실패: {e}")
            self.available = False

    def get_system_stats(self, use_cache: bool = True) -> Dict[str, Any]:
        """
        현재 시스템의 CPU 및 메모리 사용량을 가져옵니다.

        Args:
            use_cache: 캐시 사용 여부 (기본 True)

        Returns:
            CPU 및 메모리 사용량 정보를 담은 딕셔너리
        """
        if not self.available:
            return {
                "success": False,
                "error": "psutil이 사용 불가능합니다.",
            }

        # 캐시 확인 (TTL 이내면 캐시 반환)
        current_time = time.time()
        if (
            use_cache
            and self._cached_stats is not None
            and (current_time - self._last_update_time) < self.cache_ttl
        ):
            return self._cached_stats

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

            stats = {
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

            # 캐시 업데이트
            self._cached_stats = stats
            self._last_update_time = current_time

            return stats
        except Exception as e:
            logger.warning(f"시스템 자원 정보 수집 실패: {e}")
            return {"success": False, "error": str(e)}

    def is_resource_critical(
        self, stats: Optional[Dict[str, Any]] = None, cpu_threshold: float = 90.0, memory_threshold: float = 90.0
    ) -> Dict[str, bool]:
        """
        시스템 자원이 위험 수준인지 확인

        Args:
            stats: 시스템 통계 (None이면 자동 수집)
            cpu_threshold: CPU 임계값 (기본 90%)
            memory_threshold: 메모리 임계값 (기본 90%)

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
            "cpu": cpu_percent > cpu_threshold,
            "memory": memory_percent > memory_threshold,
            "disk": disk_percent is not None and disk_percent > 90,  # 디스크는 90% 고정
        }

    def is_extremely_critical(
        self, stats: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        시스템 자원이 극도로 위험한 수준인지 확인 (CPU > 97% AND RAM > 98%)

        Args:
            stats: 시스템 통계 (None이면 자동 수집)

        Returns:
            극도로 위험한 상태 여부
        """
        if stats is None:
            stats = self.get_system_stats()

        if not stats.get("success"):
            return False

        cpu_percent = stats.get("cpu_percent", 0)
        memory_percent = stats.get("memory_percent", 0)

        # CPU > 97% AND RAM > 98% 동시 만족 시
        return cpu_percent > 97.0 and memory_percent > 98.0


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
