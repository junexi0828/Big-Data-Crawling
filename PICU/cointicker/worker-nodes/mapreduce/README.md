# MapReduce 데이터 정제 작업

## 개요

원시 크롤링 데이터를 정제하고 집계하는 MapReduce 작업입니다.

## 파일 구조

- `cleaner_mapper.py` - Mapper: 데이터 정제 및 중복 제거
- `cleaner_reducer.py` - Reducer: 시간대별 집계
- `run_cleaner.sh` - 실행 스크립트

## Mapper 기능

1. **데이터 검증**: 필수 필드 확인
2. **NULL 필터링**: 빈 값 제거
3. **형식 통일**: 타임스탬프 형식 통일
4. **중복 체크**: 해시 기반 중복 식별
5. **Key 생성**: `source_date` 형식

## Reducer 기능

1. **중복 제거**: 해시 기반 중복 제거
2. **시간대별 집계**: 시간별 데이터 그룹화
3. **통계 생성**: 총 개수, 고유 개수 등

## 실행 방법

### 로컬 테스트

```bash
# Mapper 테스트
cat input.json | python3 cleaner_mapper.py

# 전체 파이프라인 테스트
cat input.json | python3 cleaner_mapper.py | sort | python3 cleaner_reducer.py
```

### Hadoop 클러스터에서 실행

```bash
# 스크립트 실행
./run_cleaner.sh

# 또는 수동 실행
hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar \
  -mapper cleaner_mapper.py \
  -reducer cleaner_reducer.py \
  -input /raw \
  -output /cleaned \
  -file cleaner_mapper.py \
  -file cleaner_reducer.py
```

## 입력 형식

JSON Lines 형식:
```json
{"source": "upbit", "symbol": "BTC", "price": 50000, "timestamp": "2025-11-27T10:00:00"}
{"source": "coinness", "title": "Bitcoin News", "url": "https://...", "timestamp": "2025-11-27T10:05:00"}
```

## 출력 형식

```json
{
  "key": "upbit_20251127",
  "source": "upbit",
  "date": "20251127",
  "total_count": 150,
  "unique_count": 145,
  "hourly_data": {
    "20251127_10": [...],
    "20251127_11": [...]
  },
  "data": [...]
}
```

