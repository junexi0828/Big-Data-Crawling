"""
재시도 유틸리티
에러 발생 시 자동 재시도 메커니즘 제공
"""

import time
from typing import Callable, Any, Optional, TypeVar, Tuple, Union, Type
from functools import wraps
from shared.logger import setup_logger

logger = setup_logger(__name__)

T = TypeVar("T")
ExceptionType = Union[Type[Exception], Tuple[Type[Exception], ...]]


def execute_with_retry(
    func: Callable[[], T],
    max_retries: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 1.5,
    exceptions: ExceptionType = (Exception,),
    on_retry: Optional[Callable[[int, Exception], None]] = None,
) -> T:
    """
    함수 실행 시 자동 재시도 메커니즘 적용

    Args:
        func: 실행할 함수 (인자 없음)
        max_retries: 최대 재시도 횟수 (기본: 3)
        delay: 초기 재시도 지연 시간 (초, 기본: 1.0)
        backoff_factor: 재시도 간격 증가 배수 (기본: 1.5)
        exceptions: 재시도할 예외 타입 (기본: 모든 Exception)
        on_retry: 재시도 시 호출할 콜백 함수 (시도 횟수, 예외)

    Returns:
        함수 실행 결과

    Raises:
        마지막 시도에서 발생한 예외
    """
    last_exception = None
    current_delay = delay

    for attempt in range(max_retries):
        try:
            return func()
        except exceptions as e:
            last_exception = e

            # Connection refused 에러는 서버가 종료된 상태이므로 재시도 없이 즉시 실패
            error_str = str(e)
            if "Connection refused" in error_str or "Errno 61" in error_str:
                logger.debug(f"서버가 종료된 상태로 감지됨, 재시도 중단: {e}")
                raise e

            if attempt < max_retries - 1:
                if on_retry:
                    try:
                        on_retry(attempt + 1, e)
                    except Exception:
                        pass  # 콜백 오류는 무시

                # 첫 번째 시도만 WARNING, 이후는 DEBUG 레벨로 변경
                if attempt == 0:
                    logger.warning(
                        f"실행 실패 (시도 {attempt + 1}/{max_retries}): {e}. "
                        f"{current_delay:.2f}초 후 재시도..."
                    )
                else:
                    logger.debug(
                        f"실행 실패 (시도 {attempt + 1}/{max_retries}): {e}. "
                        f"{current_delay:.2f}초 후 재시도..."
                    )
                time.sleep(current_delay)
                current_delay *= backoff_factor
            else:
                # 최대 재시도 횟수 초과 시에만 ERROR 로그 출력
                logger.error(f"최대 재시도 횟수({max_retries}) 초과. 마지막 오류: {e}")

    # 모든 재시도 실패
    if last_exception:
        raise last_exception
    raise RuntimeError("재시도 실패 (알 수 없는 오류)")


def retry_decorator(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 1.5,
    exceptions: ExceptionType = (Exception,),
):
    """
    함수에 재시도 메커니즘을 적용하는 데코레이터

    Args:
        max_retries: 최대 재시도 횟수
        delay: 초기 재시도 지연 시간 (초)
        backoff_factor: 재시도 간격 증가 배수
        exceptions: 재시도할 예외 타입

    Returns:
        데코레이터 함수
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            def _func():
                return func(*args, **kwargs)

            return execute_with_retry(
                _func,
                max_retries=max_retries,
                delay=delay,
                backoff_factor=backoff_factor,
                exceptions=exceptions,
            )

        return wrapper

    return decorator


def execute_with_retry_async(
    func: Callable[[], Any],
    max_retries: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 1.5,
    exceptions: ExceptionType = (Exception,),
) -> Any:
    """
    비동기 함수 실행 시 자동 재시도 메커니즘 적용

    Args:
        func: 실행할 비동기 함수 (인자 없음)
        max_retries: 최대 재시도 횟수
        delay: 초기 재시도 지연 시간 (초)
        backoff_factor: 재시도 간격 증가 배수
        exceptions: 재시도할 예외 타입

    Returns:
        함수 실행 결과
    """
    import asyncio

    last_exception = None
    current_delay = delay

    for attempt in range(max_retries):
        try:
            if asyncio.iscoroutinefunction(func):
                return asyncio.run(func())
            else:
                return func()
        except exceptions as e:
            last_exception = e
            if attempt < max_retries - 1:
                logger.warning(
                    f"비동기 실행 실패 (시도 {attempt + 1}/{max_retries}): {e}. "
                    f"{current_delay:.2f}초 후 재시도..."
                )
                time.sleep(current_delay)
                current_delay *= backoff_factor
            else:
                logger.error(f"최대 재시도 횟수({max_retries}) 초과. 마지막 오류: {e}")

    if last_exception:
        raise last_exception
    raise RuntimeError("재시도 실패 (알 수 없는 오류)")
