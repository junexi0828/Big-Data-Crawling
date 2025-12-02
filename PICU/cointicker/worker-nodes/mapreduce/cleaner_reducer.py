#!/usr/bin/env python3
"""
MapReduce Reducer: 시간대별 데이터 집계 및 중복 제거
입력: Mapper 출력 (Key-Value 쌍)
출력: 집계된 JSON 데이터
"""

import sys
import json
from typing import Dict, Any, List, Set
from collections import defaultdict


def remove_duplicates(data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """중복 제거 (해시 기반)"""
    seen_hashes: Set[str] = set()
    unique_data: List[Dict[str, Any]] = []

    for item in data_list:
        item_hash = item.get('_hash')
        if item_hash and item_hash not in seen_hashes:
            seen_hashes.add(item_hash)
            # 내부 해시 필드 제거
            item_clean = {k: v for k, v in item.items() if k != '_hash'}
            unique_data.append(item_clean)
        elif not item_hash:
            # 해시가 없는 경우도 포함 (안전장치)
            unique_data.append(item)

    return unique_data


def aggregate_by_hour(data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    """시간대별 집계"""
    from datetime import datetime

    hourly_data = defaultdict(list)

    for item in data_list:
        timestamp = item.get('timestamp')
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                hour_key = dt.strftime('%Y%m%d_%H')
                hourly_data[hour_key].append(item)
            except:
                # 타임스탬프 파싱 실패 시 전체에 포함
                hourly_data['unknown'].append(item)
        else:
            hourly_data['unknown'].append(item)

    return dict(hourly_data)


def reducer():
    """Reducer 메인 함수"""
    current_key = None
    data_bucket: List[Dict[str, Any]] = []

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            # Key-Value 분리 (탭으로 구분)
            parts = line.split('\t', 1)
            if len(parts) != 2:
                continue

            key, value_str = parts

            # 이전 키와 다른 경우 처리
            if current_key and current_key != key:
                # 이전 키 데이터 처리
                process_key_data(current_key, data_bucket)
                data_bucket = []

            current_key = key

            # Value 파싱
            value = json.loads(value_str)
            data_bucket.append(value)

        except json.JSONDecodeError:
            continue
        except Exception as e:
            print(f"Error processing line: {e}", file=sys.stderr)
            continue

    # 마지막 키 처리
    if current_key:
        process_key_data(current_key, data_bucket)


def process_key_data(key: str, data_bucket: List[Dict[str, Any]]):
    """키별 데이터 처리 및 출력"""
    if not data_bucket:
        return

    # 중복 제거
    unique_data = remove_duplicates(data_bucket)

    # 시간대별 집계
    hourly_data = aggregate_by_hour(unique_data)

    # 최종 출력
    output = {
        'key': key,
        'source': key.split('_')[0] if '_' in key else 'unknown',
        'date': key.split('_', 1)[1] if '_' in key else 'unknown',
        'total_count': len(unique_data),
        'unique_count': len(unique_data),
        'hourly_data': hourly_data,
        'data': unique_data[:100]  # 최대 100개만 포함 (성능 고려)
    }

    # JSON 출력
    print(json.dumps(output, ensure_ascii=False))


if __name__ == "__main__":
    reducer()

