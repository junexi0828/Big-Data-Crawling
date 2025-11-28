"""
캐시 관리자
TTL(Time To Live) 기반 캐싱 메커니즘 제공
"""

import time
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from threading import Lock
from shared.logger import setup_logger

logger = setup_logger(__name__)


class CacheEntry:
    """캐시 엔트리 클래스"""

    def __init__(self, value: Any, ttl_seconds: float):
        """
        초기화

        Args:
            value: 캐시 값
            ttl_seconds: TTL (초)
        """
        self.value = value
        self.created_at = datetime.now()
        self.ttl_seconds = ttl_seconds

    def is_expired(self) -> bool:
        """캐시가 만료되었는지 확인"""
        if self.ttl_seconds <= 0:
            return True  # TTL이 0 이하면 항상 만료
        elapsed = (datetime.now() - self.created_at).total_seconds()
        return elapsed >= self.ttl_seconds

    def get_age(self) -> float:
        """캐시 나이 (초)"""
        return (datetime.now() - self.created_at).total_seconds()


class CacheManager:
    """캐시 관리자 클래스"""

    def __init__(self):
        """초기화"""
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = Lock()

    def get(
        self,
        key: str,
        default: Any = None,
        ttl_seconds: Optional[float] = None,
        factory: Optional[Callable[[], Any]] = None,
    ) -> Any:
        """
        캐시에서 값 가져오기

        Args:
            key: 캐시 키
            default: 기본값 (캐시가 없거나 만료된 경우)
            ttl_seconds: TTL (초, None이면 기존 TTL 사용)
            factory: 캐시가 없을 때 값을 생성하는 함수

        Returns:
            캐시 값 또는 기본값
        """
        with self._lock:
            entry = self._cache.get(key)

            # 캐시가 있고 만료되지 않았으면 반환
            if entry and not entry.is_expired():
                logger.debug(f"캐시 히트: {key} (나이: {entry.get_age():.2f}초)")
                return entry.value

            # 캐시가 없거나 만료되었으면
            if factory:
                # 팩토리 함수로 새 값 생성
                try:
                    value = factory()
                    self.set(key, value, ttl_seconds=ttl_seconds)
                    logger.debug(f"캐시 미스 및 생성: {key}")
                    return value
                except Exception as e:
                    logger.error(f"캐시 팩토리 함수 실행 실패 ({key}): {e}")
                    return default
            else:
                # 만료된 캐시 삭제
                if entry:
                    del self._cache[key]
                    logger.debug(f"만료된 캐시 삭제: {key}")
                return default

    def set(self, key: str, value: Any, ttl_seconds: float = 60.0):
        """
        캐시에 값 저장

        Args:
            key: 캐시 키
            value: 저장할 값
            ttl_seconds: TTL (초, 기본: 60초)
        """
        with self._lock:
            self._cache[key] = CacheEntry(value, ttl_seconds)
            logger.debug(f"캐시 저장: {key} (TTL: {ttl_seconds}초)")

    def delete(self, key: str):
        """
        캐시에서 값 삭제

        Args:
            key: 캐시 키
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                logger.debug(f"캐시 삭제: {key}")

    def clear(self):
        """모든 캐시 삭제"""
        with self._lock:
            self._cache.clear()
            logger.debug("모든 캐시 삭제")

    def cleanup_expired(self):
        """만료된 캐시 정리"""
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items() if entry.is_expired()
            ]
            for key in expired_keys:
                del self._cache[key]
            if expired_keys:
                logger.debug(f"만료된 캐시 {len(expired_keys)}개 정리")

    def get_stats(self) -> Dict[str, Any]:
        """
        캐시 통계 가져오기

        Returns:
            캐시 통계 딕셔너리
        """
        with self._lock:
            total = len(self._cache)
            expired = sum(1 for entry in self._cache.values() if entry.is_expired())
            valid = total - expired

            return {
                "total": total,
                "valid": valid,
                "expired": expired,
                "keys": list(self._cache.keys()),
            }

    def invalidate(self, pattern: Optional[str] = None):
        """
        캐시 무효화

        Args:
            pattern: 무효화할 키 패턴 (None이면 모든 캐시 무효화)
        """
        with self._lock:
            if pattern is None:
                self._cache.clear()
                logger.debug("모든 캐시 무효화")
            else:
                keys_to_delete = [key for key in self._cache.keys() if pattern in key]
                for key in keys_to_delete:
                    del self._cache[key]
                if keys_to_delete:
                    logger.debug(
                        f"패턴 '{pattern}'에 해당하는 캐시 {len(keys_to_delete)}개 무효화"
                    )


# 전역 캐시 관리자 인스턴스
_global_cache: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """전역 캐시 관리자 인스턴스 가져오기 (싱글톤 패턴)"""
    global _global_cache
    if _global_cache is None:
        _global_cache = CacheManager()
    return _global_cache
