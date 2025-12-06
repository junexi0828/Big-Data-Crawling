# PICU 하둡 배포 전략 및 구조 분석

**작성 일시**: 2025-12-03
**분석 범위**: 하둡 바이너리 위치, 배포 방식, Java 파일 존재 여부

---

## 📋 질문에 대한 답변

### 1. hadoop-3.4.1을 빌려오는 거면 여기에 저장되고 있는 건가요?

**답변**: ✅ **네, 맞습니다.**

**현재 저장 위치**:

- **개발 PC**: `bigdata/hadoop_project/hadoop-3.4.1/` (1.7GB)
- **라즈베리파이**: 배포 시 `/opt/hadoop/`로 복사됨

**저장 방식**:

- 개발 PC에서 `hadoop_project/hadoop-3.4.1/`에 Apache 공식 바이너리 저장
- PICU의 `HDFSManager`가 이 경로를 자동으로 감지하여 사용
- 라즈베리파이 배포 시 배포 스크립트가 자동으로 복사

---

### 2. PICU의 자바 파일은 어디 있나요?

**답변**: ❌ **PICU에는 Java 파일이 없습니다.**

**확인 결과**:

```bash
find PICU -name "*.java"
# 결과: 없음
```

**PICU의 하둡 사용 방식**:

- ✅ **Python으로만 하둡 제어**: `HDFSClient`, `HDFSManager` 모두 Python
- ✅ **Java API 사용**: `pyarrow.fs.HadoopFileSystem` (Java 기반이지만 Python 래퍼)
- ✅ **CLI 폴백**: `hdfs dfs` 명령어 사용 (하둡 바이너리의 Java 프로그램 호출)

**Java 파일이 있는 곳**:

- ❌ PICU 프로젝트: 없음
- ✅ `hadoop_project/hadoop-3.4.1/`: 하둡 바이너리 내부에 Java 클래스 파일 포함
- ✅ `hadoop_project/examples/src/main/java/`: 예제 Java 소스 코드 (실습용)

**PICU는 하둡을 "사용"만 하지, Java로 "구현"하지 않습니다.**

---

### 3. hadoop-3.4.1을 통째로 PICU에 옮기는 게 좋나요?

**답변**: ❌ **옮길 필요 없습니다. 현재 구조가 올바릅니다.**

**현재 구조** (권장):

```
bigdata/
├── hadoop_project/          # 하둡 바이너리 (독립 프로젝트)
│   └── hadoop-3.4.1/        # 1.7GB
│
└── PICU/                    # PICU 프로젝트 (하둡 사용)
    └── cointicker/
        ├── shared/
        │   └── hdfs_client.py    # 하둡 클라이언트 (Python)
        └── gui/modules/managers/
            └── hdfs_manager.py   # 하둡 매니저 (Python)
```

**이유**:

1. **자동 감지 기능**:

   - `HDFSManager`가 `hadoop_project/hadoop-3.4.1` 경로를 자동으로 찾음
   - 환경변수 설정 불필요

2. **배포 스크립트 자동 처리**:

   - `setup_master.sh`, `setup_worker.sh`가 자동으로 하둡을 복사
   - 라즈베리파이에 `/opt/hadoop/`로 배포

3. **프로젝트 분리**:

   - `hadoop_project/`: 하둡 바이너리 및 실습 예제
   - `PICU/`: 하둡을 사용하는 애플리케이션
   - 역할 분리로 관리 용이

4. **용량 문제**:
   - 하둡 바이너리: 1.7GB
   - PICU 프로젝트에 포함 시 Git 저장소 크기 증가
   - 별도 관리가 효율적

---

## 📁 현재 구조 상세

### 개발 PC 구조

```
bigdata/
├── hadoop_project/                    # 하둡 프로젝트 (독립)
│   ├── hadoop-3.4.1/                  # 하둡 바이너리 (1.7GB)
│   │   ├── bin/                       # 실행 파일
│   │   ├── sbin/                      # 관리 스크립트
│   │   ├── etc/hadoop/                # 설정 파일
│   │   └── share/                     # 라이브러리
│   ├── examples/                      # Java 예제 코드
│   │   └── src/main/java/
│   └── deployment/                     # 배포 스크립트
│
└── PICU/                              # PICU 프로젝트
    └── cointicker/
        ├── shared/
        │   └── hdfs_client.py         # 하둡 클라이언트 (Python)
        ├── gui/modules/managers/
        │   └── hdfs_manager.py        # 하둡 매니저 (Python)
        └── deployment/                 # 배포 스크립트
            ├── setup_master.sh         # 하둡을 /opt/hadoop으로 복사
            └── setup_worker.sh         # 하둡을 /opt/hadoop으로 복사
```

### 라즈베리파이 구조 (배포 후)

```
라즈베리파이 (Master/Worker)
├── /opt/hadoop/                       # 하둡 바이너리 (배포 스크립트가 복사)
│   ├── bin/
│   ├── sbin/
│   └── etc/hadoop/
│
└── /home/ubuntu/cointicker/            # PICU 코드
    ├── master-node/                    # 또는 worker-nodes/
    ├── shared/
    └── config/
```

---

## 🔄 배포 프로세스

### 1. 개발 PC에서 배포 스크립트 실행

```bash
cd PICU/deployment
./setup_master.sh    # Master Node 배포
./setup_worker.sh    # Worker Node 배포
```

### 2. 배포 스크립트가 자동으로 수행

**코드 확인** (`setup_master.sh:84-92`):

```bash
# 3. Hadoop 배포 (NameNode용)
if [ -d "$HADOOP_ROOT" ]; then
    # Hadoop 바이너리 전송
    rsync -avz --delete \
        --exclude='logs' \
        --exclude='*.log' \
        "$HADOOP_ROOT/" \
        "$MASTER_USER@$MASTER_IP:$HADOOP_INSTALL_DIR/"
    # $HADOOP_INSTALL_DIR = /opt/hadoop
fi
```

**동작**:

1. `hadoop_project/hadoop-3.4.1/` 경로 자동 감지
2. `rsync`로 라즈베리파이의 `/opt/hadoop/`로 복사
3. 설정 파일 자동 생성 (`core-site.xml`, `hdfs-site.xml`)
4. 환경변수 자동 설정 (`~/.bashrc`)

---

## 💡 권장 사항

### ✅ 현재 구조 유지 (권장)

**이유**:

1. **자동 감지**: PICU가 `hadoop_project/` 경로를 자동으로 찾음
2. **배포 자동화**: 배포 스크립트가 자동으로 복사
3. **프로젝트 분리**: 역할 분리로 관리 용이
4. **Git 효율성**: 하둡 바이너리(1.7GB)를 Git에 포함하지 않음

### ❌ PICU에 옮기지 말 것

**이유**:

1. **Git 저장소 크기 증가**: 1.7GB 바이너리를 Git에 포함하면 비효율적
2. **중복 관리**: 하둡은 독립 프로젝트로 관리하는 것이 효율적
3. **배포 스크립트 수정 필요**: 현재 배포 스크립트가 `hadoop_project/` 경로를 가정

---

## 🔍 HDFS Manager의 자동 감지 로직

**구현 위치**: `gui/modules/managers/hdfs_manager.py:709-725`

**검색 경로** (우선순위 순):

1. `project_root/hadoop_project/hadoop-3.4.1` ✅ (현재 사용 중)
2. `project_root.parent/hadoop_project/hadoop-3.4.1`
3. `/opt/hadoop`
4. `/usr/local/hadoop`
5. `/home/bigdata/hadoop-3.4.1`
6. `/usr/lib/hadoop`
7. `/opt/homebrew/opt/hadoop` (macOS)
8. `/usr/local/opt/hadoop` (macOS)

**동작**:

- 환경변수 `HADOOP_HOME`이 없으면 자동으로 위 경로들을 검색
- 첫 번째로 발견된 경로를 `HADOOP_HOME`으로 설정

---

## 📊 배포 시나리오

### 시나리오 1: 개발 PC (현재)

**구조**:

```
bigdata/
├── hadoop_project/hadoop-3.4.1/  ← 하둡 바이너리
└── PICU/                          ← PICU 코드
```

**사용 방식**:

- `HDFSManager`가 `hadoop_project/hadoop-3.4.1` 자동 감지
- GUI에서 HDFS 시작 시 이 경로 사용

---

### 시나리오 2: 라즈베리파이 배포

**배포 전** (개발 PC):

```
hadoop_project/hadoop-3.4.1/  (1.7GB)
```

**배포 후** (라즈베리파이):

```
/opt/hadoop/  (배포 스크립트가 복사)
```

**배포 스크립트**:

```bash
# setup_master.sh 또는 setup_worker.sh
rsync -avz hadoop_project/hadoop-3.4.1/ \
    ubuntu@raspberry-master:/opt/hadoop/
```

**사용 방식**:

- 라즈베리파이에서 `/opt/hadoop` 경로 사용
- 환경변수 `HADOOP_HOME=/opt/hadoop` 자동 설정

---

## 🎯 결론

### 1. 하둡 저장 위치

✅ **개발 PC**: `bigdata/hadoop_project/hadoop-3.4.1/` (1.7GB)

- PICU가 자동으로 이 경로를 감지하여 사용
- 라즈베리파이 배포 시 배포 스크립트가 자동으로 복사

### 2. PICU의 Java 파일

❌ **PICU에는 Java 파일이 없습니다.**

- PICU는 Python으로만 하둡을 제어
- 하둡 바이너리 내부의 Java 프로그램을 호출하는 방식

### 3. 하둡을 PICU에 옮길 필요?

❌ **옮길 필요 없습니다.**

- 현재 구조가 올바름
- 자동 감지 및 배포 스크립트가 모두 작동
- 프로젝트 분리로 관리 효율적

### 권장 사항

**현재 구조를 그대로 유지하세요.**

1. ✅ `hadoop_project/hadoop-3.4.1/`에 하둡 바이너리 유지
2. ✅ PICU는 하둡을 "사용"만 하지, 포함하지 않음
3. ✅ 배포 스크립트가 자동으로 라즈베리파이에 복사
4. ✅ 라즈베리파이에서는 `/opt/hadoop` 경로 사용

---

**작성자**: JUNS_AI_MCP
**최종 업데이트**: 2025-12-03
