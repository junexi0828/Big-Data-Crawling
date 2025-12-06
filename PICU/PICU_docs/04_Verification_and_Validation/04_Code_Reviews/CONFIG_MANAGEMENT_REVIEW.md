# Config 관리 로직 점검 보고서

**작성 일시**: 2025-12-02
**최종 업데이트**: 2025-12-06
**목적**: Config 관리 함수가 기본 config → example 파일 순서로 작동하는지 점검

---

## 📋 현재 구현 상태

### 1. ConfigManager 클래스 구조

**위치**: `PICU/cointicker/gui/core/config_manager.py`

**주요 메서드**:

1. `load_config()` - 설정 파일 로드 (캐싱 적용)
2. `_load_config_from_file()` - 실제 파일에서 로드
3. `create_default_configs()` - 기본 설정 파일 생성

---

## 🔍 로직 분석

### 현재 동작 흐름

```
1. GUI 시작
   ↓
2. app.py의 _load_config() 호출
   ↓
3. create_default_configs() 실행
   ├─ GUI 설정: 기본값으로 생성 (없으면)
   └─ 다른 설정: example 파일에서 복사 (없으면)
   ↓
4. load_config() 호출
   ↓
5. _load_config_from_file() 실행
   ├─ 실제 config 파일 존재? → 사용 ✅
   └─ 없으면? → example 파일 읽기 (하지만 생성 안 함) ⚠️
```

### 문제점 발견 ⚠️

**`_load_config_from_file()` 메서드 (라인 84-134)**:

```python
# 예제 파일이 있으면 사용
if not config_file.exists():
    example_file = self.config_dir / "examples" / (...)
    if example_file.exists():
        logger.warning("설정 파일이 없어 예제 파일을 사용합니다")
        config_file = example_file  # ⚠️ 단순히 읽기만 함
    else:
        return None
```

**문제**:

- ❌ example 파일을 읽기만 하고 실제 config 파일을 생성하지 않음
- ❌ 다음에 다시 로드할 때도 계속 example 파일을 읽게 됨
- ⚠️ `create_default_configs()`가 먼저 호출되므로 대부분 문제 없지만, 다른 경로에서 `load_config()`를 먼저 호출하면 문제 발생 가능

---

## ✅ 개선 방안

### 옵션 1: `_load_config_from_file()`에서 자동 생성 (권장)

**장점**:

- 어디서든 `load_config()`를 호출해도 자동으로 config 파일 생성
- 일관성 있는 동작 보장

**구현**:

```python
def _load_config_from_file(self, config_name: str) -> Optional[dict]:
    config_file = self.config_dir / self.config_files[config_name]

    # 실제 config 파일이 없으면 example에서 생성
    if not config_file.exists():
        example_file = self.config_dir / "examples" / (
            self.config_files[config_name] + ".example"
        )
        if example_file.exists():
            try:
                # example 파일을 config 파일로 복사
                shutil.copy2(example_file, config_file)
                logger.info(
                    f"예제 파일에서 설정 파일 생성: {config_name} ({config_file})"
                )
            except Exception as e:
                logger.error(f"설정 파일 생성 실패 {config_name}: {e}")
                # 복사 실패 시 example 파일 읽기 (폴백)
                config_file = example_file
        else:
            logger.error(f"설정 파일을 찾을 수 없습니다: {config_file}")
            return None

    # 실제 config 파일 읽기
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            # ... 읽기 로직
```

### 옵션 2: 현재 구조 유지 (선택)

**장점**:

- `create_default_configs()`가 먼저 호출되므로 대부분 문제 없음
- 코드 변경 최소화

**단점**:

- 다른 경로에서 `load_config()`를 먼저 호출하면 문제 발생 가능

---

## 🎯 권장 조치

### 즉시 개선 (권장)

**`_load_config_from_file()` 메서드 수정**:

- example 파일을 읽을 때 자동으로 실제 config 파일 생성
- 어디서든 `load_config()` 호출 시 안전하게 작동

**이유**:

- 방어적 프로그래밍 (Defensive Programming)
- 호출 순서에 의존하지 않는 안정적인 구조
- 보편적인 관행 (자동 설정 파일 생성)

---

## 📊 현재 상태 평가

| 항목                  | 상태 | 평가                                      |
| --------------------- | ---- | ----------------------------------------- |
| 기본 config 파일 사용 | ✅   | 정상 작동                                 |
| example 파일에서 생성 | ⚠️   | 부분 구현 (자동 생성 없음)                |
| 호출 순서 의존성      | ⚠️   | `create_default_configs()` 먼저 호출 필요 |
| 방어적 프로그래밍     | ❌   | 호출 순서에 의존                          |

---

## 💡 결론

**현재 상태**: ⚠️ **부분적으로 작동하지만 개선 필요**

**문제점**:

- `_load_config_from_file()`에서 example 파일을 읽기만 하고 실제 파일을 생성하지 않음
- `create_default_configs()`가 먼저 호출되므로 대부분 문제 없지만, 방어적이지 않음

**권장 조치**:

- `_load_config_from_file()` 메서드 수정하여 example 파일 발견 시 자동으로 config 파일 생성
- 호출 순서에 의존하지 않는 안정적인 구조로 개선

---

## 레거시 하드코딩 제거 및 환경 변수 지원 추가 (2025-12-06)

### 발견된 문제

여러 모듈에서 설정 파일이 존재함에도 불구하고 하드코딩된 값을 사용하고 있었습니다:

1. **`backend/config.py`**: 환경 변수만 사용, `database_config.yaml` 미사용
2. **`worker-nodes/cointicker/settings.py`**: 하드코딩된 Kafka/HDFS 설정
3. **`master-node/orchestrator.py`**: 하드코딩된 Spider 목록
4. **`master-node/scheduler.py`**: 하드코딩된 스케줄 및 Scrapyd URL

### 해결 방안

모든 모듈이 설정 파일을 읽도록 수정하고, 환경 변수 우선순위를 추가했습니다:

#### 1. `backend/config.py` 개선

**이전**:

```python
DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
DATABASE_PORT = os.getenv("DATABASE_PORT", "3306")
# 설정 파일 미사용
```

**현재**:

```python
# 설정 파일에서 로드 시도
_db_config = _load_database_config()

# 환경 변수 우선, 설정 파일 fallback
DATABASE_HOST = os.getenv("DATABASE_HOST",
    _db_config.get("host", "localhost") if _db_config else "localhost")
```

#### 2. `worker-nodes/cointicker/settings.py` 개선

**이전**:

```python
KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"  # 하드코딩
HDFS_NAMENODE = "hdfs://localhost:9000"  # 하드코딩
```

**현재**:

```python
# 설정 파일에서 로드
_kafka_config = _load_kafka_config()
_cluster_config = _load_cluster_config()

# 환경 변수 우선, 설정 파일 fallback, 기본값
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS",
    _kafka_config.get("bootstrap_servers", ["localhost:9092"]) if _kafka_config else "localhost:9092")
```

#### 3. `master-node/orchestrator.py` 개선

**이전**:

```python
spiders = [
    "upbit_trends",  # 하드코딩
    "coinness",
    # ...
]
```

**현재**:

```python
# spider_config.yaml에서 활성화된 Spider 목록 로드
self.spiders = self._load_spider_config()
```

#### 4. `master-node/scheduler.py` 개선

**이전**:

```python
def __init__(self, scrapyd_url: str = "http://localhost:6800"):
    # 하드코딩된 URL
    self.scrapyd_url = scrapyd_url
```

**현재**:

```python
def __init__(self, scrapyd_url: str = None):
    # 설정 파일 또는 환경 변수에서 로드
    if scrapyd_url is None:
        scrapyd_url = self._load_scrapyd_url()
    self.scrapyd_url = scrapyd_url
    self.spiders = self._load_spider_config()  # 스케줄도 설정 파일에서 로드
```

### 환경 변수 우선순위

모든 모듈에서 다음 우선순위로 설정 값을 읽습니다:

1. **환경 변수** (최우선)
2. **설정 파일** (fallback)
3. **기본값** (최종 fallback)

### 결과

- ✅ 모든 모듈이 설정 파일과 환경 변수를 일관되게 사용
- ✅ 배포 환경에서 환경 변수로 쉽게 오버라이드 가능
- ✅ 개발 환경에서는 설정 파일 사용, 프로덕션에서는 환경 변수 사용 가능
- ✅ 레거시 하드코딩 완전 제거

---

**마지막 업데이트**: 2025-12-06
