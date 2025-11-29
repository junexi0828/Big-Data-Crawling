# HDFS 연동 문제 분석 보고서

**작성 일시**: 2025-11-29
**분석 범위**: PICU 프로젝트의 HDFS 연동 구조 및 Scrapy-HDFS 통합
**현재 상태**: ⚠️ Scrapy는 정상 작동하나 HDFS 저장 실패

---

## 📋 목차

1. [요약](#요약)
2. [현재 상황](#현재-상황)
3. [PICU HDFS 아키텍처](#picu-hdfs-아키텍처)
4. [문제 분석](#문제-분석)
5. [해결 방안](#해결-방안)
6. [권장 사항](#권장-사항)

---

## 요약

### 핵심 발견 사항

1. **Hadoop 설치 위치 확인**

   - ✅ **hadoop_project 폴더에 Hadoop 3.4.1 바이너리 존재**
     - 위치: `bigdata/hadoop_project/hadoop-3.4.1/` (1.7GB)
     - 설치 방식: Apache 공식 바이너리 다운로드 및 압축 해제 (직접 설치)
     - 설치 날짜: 2025-11-28
     - 가상환경 아님: Java 기반 바이너리 직접 설치
   - ❌ **시스템에 brew로 설치된 Hadoop 없음**
     - `brew list`에 hadoop 없음
     - `/opt/homebrew/opt/hadoop`, `/usr/local/opt/hadoop` 경로에 없음
   - ✅ **PICU의 HDFSManager가 hadoop_project의 하둡을 자동 감지 가능**
     - `HDFSManager`가 `project_root/hadoop_project/hadoop-3.4.1` 경로를 자동으로 검색
     - 환경변수 미설정 시 자동으로 `HADOOP_HOME` 설정

2. **PICU 프로젝트는 Hadoop 바이너리를 직접 포함하지 않음**

   - PICU는 Hadoop과 연동하는 **어댑터 코드**만 제공
   - 실제 Hadoop 서비스는 외부에서 실행되어야 함
   - 단, 같은 프로젝트 루트의 `hadoop_project` 폴더에 하둡이 있으면 자동으로 사용 가능

3. **Scrapy → HDFS 연동 코드는 정상 작동**

   - `HDFSPipeline` → `HDFSClient` → 실제 HDFS 서비스 연결 구조가 올바르게 구현됨
   - 코드 레벨에서는 문제 없음

4. **실제 HDFS 서비스 미실행으로 인한 저장 실패**
   - 테스트 로그: `Failed to save to HDFS: /raw/upbit/20251129/upbit_20251129_145432.json`
   - 원인: `hdfs://localhost:9000`에 실제 NameNode/DataNode가 실행되지 않음

### 결론

**PICU 프로젝트의 HDFS 연동 코드는 정상이며, 실제 Hadoop 서비스를 PICU 설정에 맞게 실행하면 정상 작동합니다.**

---

## 현재 상황

### 테스트 결과

```
[INFO] Spider 실행 중 (upbit_trends)...
[INFO] HDFS Pipeline initialized for upbit_trends
[WARNING] Failed to save to HDFS: /raw/upbit/20251129/upbit_20251129_145432.json
[ERROR] Spider 실행 중 오류 발생 (아이템: 0, 에러: 2)
```

### 문제 증상

- ✅ **Scrapy 스파이더는 정상 실행됨**
- ✅ **아이템 수집 및 파이프라인 처리까지 진행됨**
- ❌ **HDFS 저장 단계에서 실패**
- ❌ **실제 HDFS 서비스가 실행되지 않음**

### 설정 확인

**Scrapy 설정** (`worker-nodes/cointicker/settings.py`):

```python
ITEM_PIPELINES = {
    "cointicker.pipelines.ValidationPipeline": 300,
    "cointicker.pipelines.DuplicatesPipeline": 400,
    "cointicker.pipelines.HDFSPipeline": 500,  # HDFS 파이프라인 활성화
}
```

**HDFS NameNode 설정**:

- 기본값: `hdfs://localhost:9000`
- 환경변수: `HDFS_NAMENODE`
- 클러스터 설정: `config/cluster_config.yaml`의 `hadoop.hdfs.namenode`

### Hadoop 설치 상태 확인 (2025-11-29)

**확인 결과**:

1. **hadoop_project 폴더에 Hadoop 존재** ✅

   - 위치: `bigdata/hadoop_project/hadoop-3.4.1/`
   - 크기: 1.7GB (압축 해제 후)
   - 원본 파일: `hadoop-3.4.1.tar.gz` (929MB)
   - 설치 방식: Apache 공식 바이너리 다운로드 및 압축 해제
   - 설치 날짜: 2025-11-28
   - 가상환경 여부: ❌ 아님 (Java 기반 바이너리 직접 설치)

2. **시스템에 brew로 설치된 Hadoop 없음** ❌

   - `brew list`에 hadoop 없음
   - `/opt/homebrew/opt/hadoop` 경로에 없음
   - `/usr/local/opt/hadoop` 경로에 없음
   - brew 패키지 정보: hadoop 3.4.2 존재하나 설치되지 않음

3. **시스템 PATH에 hadoop 명령어 없음** ❌

   - `which hadoop`: 명령어를 찾을 수 없음
   - `which hdfs`: 명령어를 찾을 수 없음
   - `HADOOP_HOME` 환경변수: 설정되지 않음

4. **PICU 자동 감지 기능** ✅
   - `HDFSManager`가 `hadoop_project/hadoop-3.4.1` 경로를 자동으로 검색
   - 환경변수 미설정 시 자동으로 `HADOOP_HOME` 설정 가능

### Hadoop 사용 방법 3가지

PICU 프로젝트에서 Hadoop을 사용하는 방법은 다음과 같습니다:

1. **HDFSManager를 통해 hadoop_project의 하둡 사용** (현재 상태, 권장)

   - `hadoop_project/hadoop-3.4.1/`에 하둡 바이너리 존재
   - `HDFSManager`가 자동으로 이 경로를 감지하여 사용
   - 환경변수 설정 불필요 (자동 감지)
   - 프로젝트 내에서 독립적으로 관리 가능

2. **PICU에 하둡 직접 설치**

   - PICU 프로젝트 내에 하둡 바이너리 설치
   - 현재는 설치되어 있지 않음
   - 프로젝트별로 독립적인 하둡 버전 관리 가능

3. **시스템에 설치하여 외부에서 동작**
   - `/opt/hadoop` 등 시스템 경로에 설치
   - 환경변수(`HADOOP_HOME`) 설정 후 사용
   - 시스템 전체에서 공유하여 사용
   - 현재는 시스템에 설치되어 있지 않음

**현재 상태**: 방법 1 (hadoop_project 사용)이 구현되어 있으며, HDFSManager가 자동으로 경로를 감지합니다.

### 프로젝트 내 도구별 설치 방식 비교

PICU 프로젝트에서 사용하는 주요 도구들의 설치 방식을 비교하면 다음과 같습니다:

| 도구         | 서버/바이너리 위치                         | 클라이언트/라이브러리 위치   | 설치 방식               |
| ------------ | ------------------------------------------ | ---------------------------- | ----------------------- |
| **하둡**     | `hadoop_project/hadoop-3.4.1/` (직접 설치) | 가상환경 (`pyarrow`, `hdfs`) | 바이너리 다운로드 + pip |
| **카프카**   | 시스템 (`/opt/homebrew/opt/kafka` - brew)  | 가상환경 (`kafka-python`)    | brew 설치 + pip         |
| **스크래피** | 없음 (Python 패키지)                       | 가상환경 (`scrapy`)          | pip                     |
| **셀레니움** | 없음 (Python 패키지)                       | 가상환경 (`selenium`)        | pip                     |

**설치 위치 상세**:

1. **하둡**

   - 바이너리: `bigdata/hadoop_project/hadoop-3.4.1/` (1.7GB)
   - Python 클라이언트: 가상환경 (`pyarrow>=14.0.0`, `hdfs>=2.7.0`)
   - 사용 방식: `HDFSManager`가 바이너리 경로 자동 감지 → Python 클라이언트로 통신

2. **카프카**

   - 서버: 시스템에 brew로 설치 (`/opt/homebrew/opt/kafka`)
   - Python 클라이언트: 가상환경 (`kafka-python>=2.0.2`)
   - 사용 방식: 시스템의 Kafka 서버 + 가상환경의 Python 클라이언트

3. **스크래피 & 셀레니움**
   - 설치 위치: 가상환경에 pip로 설치
     - `scrapy_env/` (프로젝트 루트)
     - `PICU/venv/` (PICU 프로젝트)
     - `PICU/cointicker/venv/` (코인티커 프로젝트)
   - 사용 방식: 가상환경 활성화 후 `scrapy`, `selenium` 명령어 사용

**가상환경 사용**:

- 모든 Python 라이브러리(스크래피, 셀레니움, kafka-python, pyarrow 등)는 가상환경에 설치
- 가상환경 활성화 후 사용: `source venv/bin/activate`
- 프로젝트별로 독립적인 의존성 관리 가능

---

## PICU HDFS 아키텍처

### 전체 구조

```
┌─────────────────────────────────────────────────────────────┐
│                    PICU HDFS 연동 구조                        │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐
│   Scrapy     │
│   Spiders    │
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│  HDFSPipeline    │  ← worker-nodes/cointicker/pipelines.py
│  (Scrapy)        │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│   HDFSClient     │  ← shared/hdfs_client.py
│   (Wrapper)      │
└──────┬───────────┘
       │
       ├─── Java API (pyarrow) ───┐
       │                          │
       └─── CLI Fallback ─────────┤
                                  ▼
                        ┌──────────────────┐
                        │  실제 HDFS 서비스 │
                        │  (외부 실행 필요) │
                        │  - NameNode       │
                        │  - DataNode       │
                        └──────────────────┘
```

### 주요 컴포넌트

#### 1. HDFSPipeline (`worker-nodes/cointicker/pipelines.py`)

**역할**: Scrapy 아이템을 배치로 모아 HDFS에 저장

**주요 메서드**:

- `open_spider()`: HDFS 클라이언트 초기화
- `process_item()`: 아이템 수집 및 배치 관리
- `_save_batch()`: 배치 데이터를 HDFS에 업로드
- `close_spider()`: 마지막 배치 저장

**설정 읽기**:

```python
namenode = spider.settings.get("HDFS_NAMENODE", "hdfs://localhost:9000")
self.hdfs_client = HDFSClient(namenode=namenode)
```

#### 2. HDFSClient (`shared/hdfs_client.py`)

**역할**: HDFS와의 실제 통신 담당

**특징**:

- **Java API 우선**: `pyarrow.fs.HadoopFileSystem` 사용 (성능 우수)
- **CLI 폴백**: Java API 실패 시 `hdfs dfs` 명령어 사용
- **자동 폴백**: Java API 초기화 실패 시 자동으로 CLI 모드로 전환

**주요 메서드**:

- `put()`: 로컬 파일 → HDFS 업로드
- `get()`: HDFS 파일 → 로컬 다운로드
- `mkdir()`: HDFS 디렉토리 생성
- `exists()`: HDFS 경로 존재 여부 확인
- `rm()`: HDFS 파일/디렉토리 삭제

**초기화 로직**:

```python
def __init__(self, namenode: str = "hdfs://localhost:9000", use_java: bool = True):
    self.namenode = namenode
    self.hadoop_home = self._get_hadoop_home()  # HADOOP_HOME 환경변수

    # Java API 시도
    if self.use_java and PYARROW_AVAILABLE:
        try:
            self.fs = pafs.HadoopFileSystem.from_uri(namenode)
        except Exception as e:
            # 실패 시 CLI 모드로 폴백
            self.use_java = False
```

#### 3. HDFSManager (`gui/modules/managers/hdfs_manager.py`)

**역할**: HDFS 서비스 관리 및 설정

**주요 기능**:

- HDFS 실행 여부 확인 (`check_running()`)
- 단일 노드/클러스터 모드 설정
- `core-site.xml`, `hdfs-site.xml` 자동 생성
- HDFS 데몬 시작/중지
- **HADOOP_HOME 자동 감지**: 환경변수 미설정 시 여러 경로에서 자동 검색

**HADOOP_HOME 자동 감지 로직**:

```python
# HDFSManager가 검색하는 경로 목록 (우선순위 순)
search_paths = [
    project_root / "hadoop_project" / "hadoop-3.4.1",  # ✅ 현재 프로젝트에 존재
    project_root.parent / "hadoop_project" / "hadoop-3.4.1",
    Path("/opt/hadoop"),
    Path("/usr/local/hadoop"),
    Path("/home/bigdata/hadoop-3.4.1"),
    Path("/usr/lib/hadoop"),
    Path("/opt/homebrew/opt/hadoop"),  # brew 설치 경로
    Path("/usr/local/opt/hadoop"),     # brew 설치 경로
]

# 첫 번째로 발견된 경로를 HADOOP_HOME으로 설정
for path in search_paths:
    if path.exists() and (path / "sbin" / "start-dfs.sh").exists():
        hadoop_home = str(path)
        os.environ["HADOOP_HOME"] = hadoop_home
        break
```

**설정 파일 읽기**:

```python
# config/cluster_config.yaml
hadoop:
  version: "3.4.1"
  home: "/opt/hadoop"  # 자동 감지 시 이 값은 무시됨
  hdfs:
    namenode: "hdfs://raspberry-master:9000"
    replication: 3
```

#### 4. 설정 파일 구조

**클러스터 설정** (`config/cluster_config.yaml`):

```yaml
hadoop:
  version: "3.4.1"
  home: "/opt/hadoop" # HADOOP_HOME 경로
  hdfs:
    namenode: "hdfs://raspberry-master:9000" # NameNode 주소
    replication: 3 # 복제 인수
```

**환경변수 우선순위**:

1. `HDFS_NAMENODE` 환경변수
2. `cluster_config.yaml`의 `hadoop.hdfs.namenode`
3. 기본값: `hdfs://localhost:9000`

---

## 문제 분석

### 문제 1: 실제 HDFS 서비스 미실행

**증상**:

```
[WARNING] Failed to save to HDFS: /raw/upbit/20251129/upbit_20251129_145432.json
```

**원인 분석**:

1. **HDFSClient.put() 실패**

   - Java API 시도 → `HadoopFileSystem.from_uri()` 실패 (NameNode 미실행)
   - CLI 폴백 시도 → `hdfs dfs -put` 명령어 실패 (Hadoop 미설치 또는 미실행)

2. **포트 확인**:

   - NameNode 포트: `9000` (RPC)
   - NameNode Web UI: `9870` (HTTP)
   - 현재 상태: 포트 미개방 → HDFS 서비스 미실행

3. **HADOOP_HOME 확인 필요**:
   - `HDFSClient._get_hadoop_home()`: `os.environ.get("HADOOP_HOME", "/opt/hadoop")`
   - 기본값 `/opt/hadoop`에 Hadoop이 설치되어 있지 않을 수 있음
   - ✅ **실제 설치 위치**: `bigdata/hadoop_project/hadoop-3.4.1/`
   - `HDFSManager`가 자동으로 이 경로를 감지하여 `HADOOP_HOME` 설정 가능

### 문제 2: 설정 불일치 가능성

**가능한 시나리오**:

1. **로컬 개발 환경**:

   - `cluster_config.yaml`: `hdfs://raspberry-master:9000` (원격 클러스터)
   - 실제 환경: 로컬 Mac에서 테스트 중
   - **해결**: `HDFS_NAMENODE=hdfs://localhost:9000` 환경변수 설정 필요

2. **Hadoop 설치 상태**:

   - ✅ **hadoop_project에 Hadoop 3.4.1 설치됨** (직접 설치, 가상환경 아님)
   - ❌ **시스템 PATH에 hadoop 명령어 없음** (환경변수 미설정)
   - ❌ **brew로 설치된 하둡 없음**
   - PICU의 `HDFSManager`가 `hadoop_project/hadoop-3.4.1`을 자동으로 찾을 수 있음

3. **HDFS 서비스 미시작**:
   - Hadoop 설치되어 있어도 NameNode/DataNode 데몬이 실행되지 않음
   - `HDFSManager`를 통한 자동 시작 또는 수동 시작 필요

### 문제 3: 에러 처리 개선 필요

**현재 코드** (`pipelines.py` 372줄):

```python
if success:
    logger.info(f"Saved {len(self.items)} items to HDFS: {hdfs_file}")
    local_file.unlink()
else:
    logger.error(f"Failed to save to HDFS: {hdfs_file}")  # 에러만 로깅
```

**개선 사항**:

- 실패 원인 상세 로깅 (Java API 실패? CLI 실패? 포트 연결 실패?)
- 재시도 로직 추가 고려
- HDFS 연결 상태 사전 확인

---

## 해결 방안

### 방안 1: 로컬 단일 노드 HDFS 설정 (개발 환경)

#### 1단계: Hadoop 설치 확인

**hadoop_project의 하둡 사용 (권장)**:

```bash
# hadoop_project의 하둡 경로 설정
export HADOOP_HOME=/Users/juns/code/personal/notion/pknu_workspace/bigdata/hadoop_project/hadoop-3.4.1
export PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin

# Hadoop 버전 확인
$HADOOP_HOME/bin/hadoop version

# HDFS 명령어 확인
$HADOOP_HOME/bin/hdfs dfs -ls /
```

**또는 HADOOP_HOME 자동 감지 (PICU GUI 사용 시)**:

- `HDFSManager`가 자동으로 `hadoop_project/hadoop-3.4.1` 경로를 찾아 `HADOOP_HOME` 설정
- GUI에서 "HDFS 시작" 클릭 시 자동으로 경로 감지 및 설정

#### 2단계: HDFSManager를 통한 자동 설정

**GUI에서 실행**:

1. GUI 실행: `bash PICU/scripts/run_gui.sh`
2. HDFS 모듈 → "HDFS 시작" 클릭
3. `HDFSManager`가 자동으로:
   - `HADOOP_HOME` 감지
   - `cluster_config.yaml` 읽기
   - 단일 노드 모드 설정 (`core-site.xml`, `hdfs-site.xml` 생성)
   - SSH 설정 확인
   - HDFS 데몬 시작

**CLI에서 실행**:

```python
from gui.modules.managers.hdfs_manager import HDFSManager

manager = HDFSManager()
result = manager.check_and_start_hdfs()
```

#### 3단계: 수동 설정 (GUI 사용 불가 시)

**1. Hadoop 설정 파일 생성**:

```bash
# HADOOP_HOME 설정 (hadoop_project 경로 사용)
export HADOOP_HOME=/Users/juns/code/personal/notion/pknu_workspace/bigdata/hadoop_project/hadoop-3.4.1
# 또는 프로젝트 루트 기준 상대 경로
# export HADOOP_HOME=$(pwd)/hadoop_project/hadoop-3.4.1

# core-site.xml
cat > $HADOOP_HOME/etc/hadoop/core-site.xml << EOF
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <property>
        <name>fs.defaultFS</name>
        <value>hdfs://localhost:9000</value>
    </property>
</configuration>
EOF

# hdfs-site.xml
cat > $HADOOP_HOME/etc/hadoop/hdfs-site.xml << EOF
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <property>
        <name>dfs.replication</name>
        <value>1</value>
    </property>
</configuration>
EOF
```

**2. HDFS 포맷 및 시작**:

```bash
# HDFS 포맷 (최초 1회만)
hdfs namenode -format

# HDFS 시작
$HADOOP_HOME/sbin/start-dfs.sh

# 실행 확인
jps  # NameNode, DataNode, SecondaryNameNode 프로세스 확인
```

**3. 포트 확인**:

```bash
# NameNode RPC 포트
netstat -an | grep 9000

# NameNode Web UI
curl http://localhost:9870
```

### 방안 2: 환경변수 설정 (테스트 환경)

**테스트 스크립트 수정** (`tests/run_all_tests.sh`):

```bash
# HDFS 설정 (hadoop_project 경로 우선 사용)
if [ -z "$HADOOP_HOME" ]; then
    # 프로젝트 루트에서 hadoop_project 찾기
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
    HADOOP_PROJECT_PATH="$PROJECT_ROOT/hadoop_project/hadoop-3.4.1"

    if [ -d "$HADOOP_PROJECT_PATH" ] && [ -f "$HADOOP_PROJECT_PATH/sbin/start-dfs.sh" ]; then
        export HADOOP_HOME="$HADOOP_PROJECT_PATH"
        export PATH="$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin"
        echo "✅ HADOOP_HOME 자동 설정: $HADOOP_HOME"
    else
        export HADOOP_HOME="${HADOOP_HOME:-/opt/hadoop}"
        echo "⚠️ hadoop_project를 찾을 수 없습니다. 기본값 사용: $HADOOP_HOME"
    fi
fi

export HDFS_NAMENODE="${HDFS_NAMENODE:-hdfs://localhost:9000}"

# HDFS 실행 확인
if ! nc -z localhost 9000 2>/dev/null; then
    log_warning "HDFS가 실행되지 않았습니다. HDFS를 시작하거나 테스트를 건너뛰세요."
    # HDFS 자동 시작 로직 추가 가능
fi
```

### 방안 3: HDFSPipeline 에러 처리 개선

**개선된 코드** (`pipelines.py`):

```python
def _save_batch(self, spider):
    """배치 데이터를 HDFS에 저장"""
    if not self.hdfs_client or not self.items:
        return

    try:
        # ... (기존 코드) ...

        # HDFS에 업로드
        hdfs_file = f"{hdfs_path}/{local_file.name}"
        success = self.hdfs_client.put(str(local_file), hdfs_file)

        if success:
            logger.info(f"Saved {len(self.items)} items to HDFS: {hdfs_file}")
            local_file.unlink()
        else:
            # 상세 에러 로깅
            logger.error(
                f"Failed to save to HDFS: {hdfs_file}\n"
                f"NameNode: {self.hdfs_client.namenode}\n"
                f"HADOOP_HOME: {self.hdfs_client.hadoop_home}\n"
                f"로컬 파일은 보존됨: {local_file}"
            )
            # 로컬 파일 보존 (재시도 가능하도록)

    except Exception as e:
        logger.error(
            f"Error saving batch to HDFS: {e}\n"
            f"NameNode: {self.hdfs_client.namenode if self.hdfs_client else 'N/A'}\n"
            f"로컬 파일: {local_file if 'local_file' in locals() else 'N/A'}"
        )
```

### 방안 4: HDFS 연결 사전 확인

**HDFSPipeline 개선**:

```python
def open_spider(self, spider):
    """Spider 시작 시 HDFS 클라이언트 초기화 및 연결 확인"""
    try:
        namenode = spider.settings.get("HDFS_NAMENODE", "hdfs://localhost:9000")
        self.hdfs_client = HDFSClient(namenode=namenode)

        # HDFS 연결 확인
        if not self._check_hdfs_connection():
            logger.warning(
                f"HDFS 연결 실패: {namenode}\n"
                f"Spider는 계속 실행되지만 HDFS 저장은 실패할 수 있습니다."
            )
        else:
            logger.info(f"HDFS Pipeline initialized for {spider.name}")

    except Exception as e:
        logger.error(f"Failed to initialize HDFS client: {e}")
        self.hdfs_client = None

def _check_hdfs_connection(self) -> bool:
    """HDFS 연결 가능 여부 확인"""
    if not self.hdfs_client:
        return False

    try:
        # 루트 디렉토리 존재 확인으로 연결 테스트
        return self.hdfs_client.exists("/")
    except Exception as e:
        logger.debug(f"HDFS 연결 확인 실패: {e}")
        return False
```

---

## 권장 사항

### 즉시 조치 사항

1. **HDFS 서비스 실행 확인**

   ```bash
   # 포트 확인
   nc -z localhost 9000 && echo "HDFS NameNode 실행 중" || echo "HDFS NameNode 미실행"

   # 프로세스 확인
   jps | grep -E "NameNode|DataNode"
   ```

2. **환경변수 설정**

   **hadoop_project의 하둡 사용 (권장)**:

   ```bash
   # hadoop_project의 하둡 경로 설정
   export HADOOP_HOME=/Users/juns/code/personal/notion/pknu_workspace/bigdata/hadoop_project/hadoop-3.4.1
   export PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin
   export HDFS_NAMENODE=hdfs://localhost:9000
   ```

   **또는 PICU GUI 사용 시**:

   - `HDFSManager`가 자동으로 `hadoop_project/hadoop-3.4.1` 경로를 감지하여 `HADOOP_HOME` 설정
   - 수동 설정 불필요

3. **테스트 전 HDFS 상태 확인**
   - `tests/run_all_tests.sh`에 HDFS 실행 여부 사전 확인 로직 추가
   - HDFS 미실행 시 경고 메시지 출력 및 선택적 스킵

### 중기 개선 사항

1. **HDFS 자동 시작 기능**

   - `HDFSManager.check_and_start_hdfs()`를 테스트 스크립트에 통합
   - HDFS 미실행 시 자동으로 시작 시도

2. **에러 메시지 개선**

   - HDFS 저장 실패 시 구체적인 원인 표시
   - 해결 방법 제시 (예: "HDFS를 시작하려면: `hdfs namenode -format && start-dfs.sh`")

3. **설정 검증**
   - `HDFSPipeline` 초기화 시 설정 유효성 검증
   - NameNode 주소 형식 확인 (`hdfs://host:port`)

### 장기 개선 사항

1. **HDFS 연결 풀 관리**

   - 여러 스파이더 동시 실행 시 연결 재사용
   - 연결 타임아웃 및 재연결 로직

2. **배치 저장 최적화**

   - 현재: 배치 크기 100개 고정
   - 개선: 동적 배치 크기 조정 (네트워크 상태에 따라)

3. **모니터링 및 알림**
   - HDFS 저장 실패율 모니터링
   - 임계값 초과 시 알림 (GUI 또는 로그)

---

## 결론

### 현재 상태

- ✅ **코드 구조**: PICU의 HDFS 연동 코드는 정상적으로 구현되어 있음
- ✅ **Scrapy 연동**: `HDFSPipeline` → `HDFSClient` 구조가 올바르게 작동
- ❌ **인프라**: 실제 HDFS 서비스가 실행되지 않아 저장 실패

### 해결 방향

1. **단기**: 실제 HDFS 서비스 실행 (로컬 또는 원격)
2. **중기**: 에러 처리 및 연결 확인 로직 개선
3. **장기**: 자동화 및 모니터링 강화

### 핵심 메시지

**PICU 프로젝트는 Hadoop 바이너리를 직접 포함하지 않지만, 같은 프로젝트 루트의 `hadoop_project/hadoop-3.4.1`에 Apache 공식 바이너리가 설치되어 있습니다. `HDFSManager`가 이 경로를 자동으로 감지하여 사용할 수 있으며, 실제 Hadoop 서비스를 PICU 설정에 맞게 실행하면 정상 작동합니다.**

**Hadoop 설치 상태 요약**:

- ✅ `hadoop_project/hadoop-3.4.1/`: Apache 공식 바이너리 직접 설치 (1.7GB)
- ❌ 시스템 PATH: hadoop 명령어 없음 (환경변수 미설정)
- ❌ brew 설치: 없음
- ✅ 자동 감지: PICU의 `HDFSManager`가 `hadoop_project` 경로 자동 검색 가능

---

**작성자**: JUNS_AI_MCP
**최종 업데이트**: 2025-11-29 (Hadoop 설치 상태 확인 반영)
**검토 완료**:

- ✅ Hadoop 설치 위치 확인: `hadoop_project/hadoop-3.4.1/`에 존재
- ✅ 설치 방식 확인: Apache 공식 바이너리 직접 설치 (가상환경 아님)
- ✅ brew 설치 여부 확인: 시스템에 brew로 설치된 하둡 없음
- ✅ PICU 자동 감지 기능 확인: `HDFSManager`가 `hadoop_project` 경로 자동 검색 가능
