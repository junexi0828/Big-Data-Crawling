# 프로젝트별 데이터 저장 방식 비교 분석

## 📊 전체 비교표

| 프로젝트             | 저장 방식       | 저장 위치                    | 데이터 형식             | 처리 단계       | 특징                       |
| -------------------- | --------------- | ---------------------------- | ----------------------- | --------------- | -------------------------- |
| **hadoop_project**   | HDFS            | HDFS 분산 파일시스템         | 텍스트 파일 (블록 단위) | MapReduce 처리  | 분산 저장, 복제, WORM      |
| **kafka_project**    | Kafka Topic     | Kafka 브로커 (메모리/디스크) | 메시지 (Key-Value)      | Consumer가 소비 | 실시간 스트리밍, 토픽 기반 |
| **selenium_project** | 로컬 파일       | 로컬 디스크 (`outputs/`)     | JSON 파일               | 직접 저장       | 단순 파일 저장             |
| **scrapy_project**   | 다중 저장소     | JSON/SQLite/MariaDB          | JSON/DB 레코드          | Pipeline 처리   | 다중 저장 옵션             |
| **PICU**             | 통합 파이프라인 | HDFS → MariaDB               | JSON → 정제된 DB 레코드 | 다단계 처리     | 엔터프라이즈급 통합        |

---

## 🔍 상세 분석

### 1. hadoop_project

#### 저장 방식

- **저장소**: HDFS (Hadoop Distributed File System)
- **형식**: 블록 기반 파일 저장 (기본 128MB/256MB 블록)
- **복제**: 기본 3회 복제 (장애 허용)

#### 특징

```java
// 예제: HDFS에 파일 업로드
hadoop fs -put local_file.txt /hdfs/path/
```

- **WORM (Write-Once, Read-Many)**: 한 번 쓰고 여러 번 읽기
- **분산 저장**: 여러 DataNode에 블록 분산 저장
- **MapReduce 처리**: 저장된 데이터를 MapReduce로 처리

#### 데이터 흐름

```
로컬 파일 → HDFS 업로드 → MapReduce 처리 → 결과 저장
```

#### 장점

- ✅ 대용량 데이터 처리 (PB 단위)
- ✅ 장애 허용 (복제)
- ✅ 확장 가능

#### 단점

- ❌ 실시간 처리 부적합
- ❌ 랜덤 쓰기 불가 (Append만 가능)

---

### 2. kafka_project

#### 저장 방식

- **저장소**: Kafka Topic (브로커의 로그 세그먼트)
- **형식**: 메시지 (Key-Value 쌍)
- **보존**: 설정된 retention 기간 동안 보관

#### 특징

```python
# Producer: 메시지 전송
producer.send(topic='bigdata', key=b'key', value=b'message')

# Consumer: 메시지 소비
consumer = KafkaConsumer('bigdata', group_id='group1')
for message in consumer:
    print(message.value)
```

- **토픽 기반**: 여러 토픽으로 데이터 분류
- **Consumer Group**: 여러 Consumer가 메시지 소비
- **Offset 관리**: 읽은 위치 추적

#### 데이터 흐름

```
Producer → Kafka Topic → Consumer → 처리/저장
```

#### 장점

- ✅ 실시간 스트리밍
- ✅ 높은 처리량
- ✅ 메시지 순서 보장
- ✅ 여러 Consumer가 동시 소비 가능

#### 단점

- ❌ 영구 저장소가 아님 (retention 기간 제한)
- ❌ 단순 메시징 시스템 (복잡한 쿼리 불가)

---

### 3. selenium_project

#### 저장 방식

- **저장소**: 로컬 파일시스템
- **형식**: JSON 파일
- **위치**: `outputs/json/` 디렉토리

#### 특징

```python
# JSON 파일로 저장
def save_to_json(self, data, filename=None):
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"outputs/json/exchange_rates_{timestamp}.json"

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
```

- **단순 저장**: 크롤링 후 즉시 JSON 파일로 저장
- **타임스탬프 파일명**: 중복 방지
- **Scrapy 통합**: Scrapy Middleware로도 사용 가능

#### 데이터 흐름

```
Selenium 크롤링 → 데이터 수집 → JSON 파일 저장
```

#### 장점

- ✅ 구현 간단
- ✅ 빠른 개발
- ✅ 디버깅 용이

#### 단점

- ❌ 확장성 제한
- ❌ 분산 처리 불가
- ❌ 데이터베이스 기능 없음

---

### 4. scrapy_project

#### 저장 방식

- **다중 저장소 지원**:
  1. **JSON 파일**: `JsonWriterPipeline`
  2. **SQLite**: `SQLitePipeline`
  3. **MariaDB**: `MariaDBPipeline`
  4. **정규화된 DB**: `NormalizedTutorialPipeline`

#### 특징

```python
# Pipeline 설정 (settings.py)
ITEM_PIPELINES = {
    "tutorial.pipelines.QuotesValidationPipeline": 200,  # 검증
    "tutorial.pipelines.JsonWriterPipeline": 400,         # JSON 저장
    "tutorial.pipelines.SQLitePipeline": 500,            # SQLite 저장
    "tutorial.pipelines.MariaDBPipeline": 600,           # MariaDB 저장
    "tutorial.pipelines.NormalizedTutorialPipeline": 700, # 정규화된 DB 저장
}
```

#### 데이터 흐름

```
Scrapy Spider → ValidationPipeline → DuplicatesPipeline →
JsonWriterPipeline → SQLitePipeline → MariaDBPipeline
```

#### 저장 예시

**SQLite 저장:**

```python
self.cursor.execute(
    "INSERT INTO quotes (quote_content, author_name, ...) VALUES (?, ?, ...)",
    (adapter.get("quote_content"), adapter.get("author_name"), ...)
)
```

**MariaDB 저장:**

```python
self.cursor.execute(
    "INSERT INTO quotes (quote_content, author_name, tags) VALUES (?, ?, ?)",
    (adapter.get("quote_content"), adapter.get("author_name"), tags_json)
)
```

#### 장점

- ✅ 유연한 저장 옵션
- ✅ Pipeline 체인으로 다단계 처리
- ✅ 데이터 검증 및 정제 가능

#### 단점

- ❌ 각 저장소별 개별 관리 필요
- ❌ 분산 저장 미지원

---

### 5. PICU (통합 프로젝트)

#### 저장 방식

- **통합 파이프라인**:
  1. **HDFS**: 원시 데이터 저장
  2. **MapReduce**: 데이터 정제 및 집계
  3. **MariaDB**: 정제된 데이터 최종 저장

#### 특징

```python
# 1단계: Scrapy → HDFS
class HDFSPipeline:
    def process_item(self, item, spider):
        # 배치로 모아서 HDFS에 저장
        self.items.append(item_dict)
        if len(self.items) >= self.batch_size:
            self._save_batch(spider)

# 2단계: MapReduce 정제
# cleaner_mapper.py: 데이터 정제 및 중복 제거
# cleaner_reducer.py: 시간대별 집계

# 3단계: HDFS → MariaDB
class DataLoader:
    def load_from_hdfs(self, date):
        # HDFS에서 정제된 데이터 다운로드
        files = self.hdfs.list_files(hdfs_path)
        for file_path in files:
            self._load_json_file(local_file)
            # MariaDB에 적재
            self._load_item(item)
```

#### 데이터 흐름

```
Scrapy Spider
    ↓
ValidationPipeline (검증)
    ↓
DuplicatesPipeline (중복 제거)
    ↓
HDFSPipeline → HDFS (/raw/)
    ↓
MapReduce (정제 및 집계)
    ↓
HDFS (/cleaned/)
    ↓
DataLoader → MariaDB (raw_news, market_trends, fear_greed_index)
```

#### 저장 구조

**HDFS 경로:**

```
/raw/
  ├── coinness/
  │   └── 20251127/
  │       └── coinness_20251127_143000.json
  ├── upbit/
  │   └── 20251127/
  │       └── upbit_20251127_143000.json
  └── ...

/cleaned/
  └── 20251127/
      └── aggregated_14.json
```

**MariaDB 테이블:**

```sql
-- 뉴스 데이터
raw_news (id, source, title, url, content, published_at, keywords, collected_at)

-- 시장 트렌드
market_trends (id, source, symbol, price, volume_24h, change_24h, timestamp)

-- 공포·탐욕 지수
fear_greed_index (id, value, classification, timestamp)
```

#### 장점

- ✅ **엔터프라이즈급 통합**: HDFS + MapReduce + DB
- ✅ **다단계 검증**: ValidationPipeline → MapReduce → DB
- ✅ **확장 가능**: 분산 저장 및 처리
- ✅ **데이터 정제**: MapReduce로 중복 제거 및 집계
- ✅ **최종 저장소**: MariaDB로 구조화된 데이터 저장

#### 단점

- ❌ 복잡한 아키텍처 (설정 및 관리 필요)
- ❌ 여러 시스템 의존성

---

## 📈 비교 요약

### 저장소 유형별 분류

| 저장소 유형         | 프로젝트             | 용도                    |
| ------------------- | -------------------- | ----------------------- |
| **분산 파일시스템** | hadoop_project, PICU | 대용량 원시 데이터 저장 |
| **메시징 시스템**   | kafka_project        | 실시간 데이터 스트리밍  |
| **로컬 파일**       | selenium_project     | 단순 크롤링 결과 저장   |
| **관계형 DB**       | scrapy_project, PICU | 구조화된 데이터 저장    |
| **NoSQL/문서 DB**   | -                    | (현재 미사용)           |

### 데이터 처리 단계 비교

| 프로젝트             | 수집     | 검증               | 정제      | 저장                | 특징            |
| -------------------- | -------- | ------------------ | --------- | ------------------- | --------------- |
| **hadoop_project**   | -        | -                  | MapReduce | HDFS                | 배치 처리 중심  |
| **kafka_project**    | Producer | -                  | Consumer  | Topic               | 실시간 스트리밍 |
| **selenium_project** | Selenium | -                  | -         | JSON 파일           | 단순 저장       |
| **scrapy_project**   | Scrapy   | ValidationPipeline | -         | JSON/SQLite/MariaDB | 다중 저장 옵션  |
| **PICU**             | Scrapy   | ValidationPipeline | MapReduce | HDFS → MariaDB      | 통합 파이프라인 |

### 확장성 및 성능

| 프로젝트             | 확장성     | 성능       | 실시간 처리 | 배치 처리 |
| -------------------- | ---------- | ---------- | ----------- | --------- |
| **hadoop_project**   | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐   | ❌          | ✅        |
| **kafka_project**    | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅          | ⚠️        |
| **selenium_project** | ⭐         | ⭐⭐       | ❌          | ❌        |
| **scrapy_project**   | ⭐⭐⭐     | ⭐⭐⭐     | ❌          | ✅        |
| **PICU**             | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐   | ⚠️          | ✅        |

---

## 🎯 결론 및 권장사항

### 프로젝트별 적합한 사용 사례

1. **hadoop_project**: 대용량 배치 데이터 처리 및 분석
2. **kafka_project**: 실시간 이벤트 스트리밍 및 메시징
3. **selenium_project**: 단순 크롤링 및 프로토타이핑
4. **scrapy_project**: 중소규모 크롤링 및 다중 저장소 필요 시
5. **PICU**: 엔터프라이즈급 통합 데이터 파이프라인

### PICU의 우수성

PICU는 다른 프로젝트들의 장점을 통합한 **엔터프라이즈급 솔루션**입니다:

- ✅ **HDFS**: hadoop_project의 분산 저장 활용
- ✅ **Kafka**: 실시간 스트리밍 지원 (선택적)
- ✅ **Scrapy**: scrapy_project의 검증 및 Pipeline 활용
- ✅ **MapReduce**: 데이터 정제 및 집계
- ✅ **MariaDB**: 최종 구조화된 데이터 저장

이러한 통합으로 **확장 가능하고 안정적인 데이터 파이프라인**을 구축할 수 있습니다.
