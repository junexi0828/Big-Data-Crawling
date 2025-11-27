"""
공통 유틸리티 함수
"""

import hashlib
import json
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path


def generate_hash(data: str) -> str:
    """
    데이터의 MD5 해시 생성

    Args:
        data: 해시할 데이터 문자열

    Returns:
        MD5 해시값 (hex)
    """
    return hashlib.md5(data.encode("utf-8")).hexdigest()


def get_timestamp(format: str = "%Y%m%d_%H%M%S") -> str:
    """
    현재 시간의 타임스탬프 문자열 생성

    Args:
        format: 시간 포맷 (기본값: '%Y%m%d_%H%M%S')

    Returns:
        포맷된 타임스탬프 문자열
    """
    return datetime.now().strftime(format)


def get_date_path(base_path: str, date: Optional[datetime] = None) -> Path:
    """
    날짜별 디렉토리 경로 생성

    Args:
        base_path: 기본 경로
        date: 날짜 (None이면 오늘)

    Returns:
        날짜별 경로 Path 객체
    """
    if date is None:
        date = datetime.now()

    date_str = date.strftime("%Y%m%d")
    return Path(base_path) / date_str


def clean_text(text: str) -> str:
    """
    텍스트 정제 (공백 제거, 특수문자 처리)

    Args:
        text: 정제할 텍스트

    Returns:
        정제된 텍스트
    """
    if not text:
        return ""

    # 공백 정리
    text = " ".join(text.split())
    # 앞뒤 공백 제거
    text = text.strip()

    return text


def validate_json(data: Dict[str, Any]) -> bool:
    """
    JSON 데이터 유효성 검사

    Args:
        data: 검사할 딕셔너리

    Returns:
        유효하면 True
    """
    try:
        json.dumps(data)
        return True
    except (TypeError, ValueError):
        return False


def safe_get(data: Dict[str, Any], *keys, default: Any = None) -> Any:
    """
    중첩 딕셔너리에서 안전하게 값 가져오기

    Args:
        data: 딕셔너리
        *keys: 키 경로
        default: 기본값

    Returns:
        찾은 값 또는 기본값

    Example:
        >>> data = {'a': {'b': {'c': 1}}}
        >>> safe_get(data, 'a', 'b', 'c')
        1
        >>> safe_get(data, 'a', 'b', 'd', default=0)
        0
    """
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current
