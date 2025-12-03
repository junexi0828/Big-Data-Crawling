#!/usr/bin/env python3
"""
MapReduce Mapper: 데이터 정제 및 중복 제거
입력: JSON Lines 형식의 원시 데이터
출력: Key-Value 쌍 (source_date, cleaned_data)
"""

import sys
import json
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional


def generate_hash(data: Dict[str, Any]) -> str:
    """데이터의 고유 해시 생성"""
    # URL 또는 제목을 기반으로 해시 생성
    identifier = data.get('url') or data.get('title') or str(data.get('timestamp', ''))
    return hashlib.md5(identifier.encode('utf-8')).hexdigest()


def clean_data(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """데이터 정제 및 검증"""
    # 필수 필드 검증
    if not data.get('source') or not data.get('timestamp'):
        return None

    # NULL 값 필터링
    cleaned = {}
    for key, value in data.items():
        if value is not None and value != '':
            cleaned[key] = value

    # 타임스탬프 형식 통일
    if 'timestamp' in cleaned:
        try:
            # ISO 형식으로 변환
            if isinstance(cleaned['timestamp'], str):
                # 이미 ISO 형식인지 확인
                datetime.fromisoformat(cleaned['timestamp'].replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            # 형식 변환 실패 시 현재 시간 사용
            cleaned['timestamp'] = datetime.now().isoformat()

    # 해시 추가 (중복 체크용)
    cleaned['_hash'] = generate_hash(cleaned)

    return cleaned


def mapper():
    """Mapper 메인 함수"""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            # JSON 파싱
            data = json.loads(line)

            # 데이터 정제
            cleaned = clean_data(data)
            if not cleaned:
                continue

            # Key 생성: source + date (시간대별 집계용)
            source = cleaned.get('source', 'unknown')
            timestamp = cleaned.get('timestamp', datetime.now().isoformat())

            # 날짜 추출 (YYYYMMDD 형식)
            try:
                date_obj = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                date_str = date_obj.strftime('%Y%m%d')
            except:
                date_str = datetime.now().strftime('%Y%m%d')

            key = f"{source}_{date_str}"

            # Key-Value 출력 (탭으로 구분)
            value = json.dumps(cleaned, ensure_ascii=False)
            print(f"{key}\t{value}")

        except json.JSONDecodeError:
            # JSON 파싱 실패 시 스킵
            continue
        except Exception as e:
            # 기타 오류는 stderr로 출력
            print(f"Error processing line: {e}", file=sys.stderr)
            continue


if __name__ == "__main__":
    mapper()

