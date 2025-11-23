# Hadoop 프로젝트 구조

## 📁 디렉토리 구조

```
hadoop_project/
├── docs/                          # 문서 디렉토리
│   ├── HADOOP_CONCEPTS.md         # Hadoop 개념 정리
│   ├── SETUP_GUIDE.md            # 상세 설정 가이드
│   └── PROJECT_STRUCTURE.md      # 이 파일
│
├── config/                        # 설정 파일 템플릿
│   ├── core-site.xml.example     # 파일시스템 기본 설정
│   ├── hdfs-site.xml.example     # HDFS 설정
│   ├── mapred-site.xml.example   # MapReduce 설정
│   └── yarn-site.xml.example     # YARN 설정
│
├── scripts/                       # 실습 스크립트
│   ├── setup_local_mode.sh       # Local Mode 설정
│   ├── setup_single_node_wo_yarn.sh    # Single-Node (w/o YARN)
│   ├── setup_single_node_with_yarn.sh  # Single-Node (with YARN)
│   ├── setup_multi_node_cluster.sh     # Multi-Node Cluster
│   └── run_wordcount_example.sh        # Wordcount 예제 실행
│
└── README.md                      # 프로젝트 메인 README
```

---

## 📚 문서 디렉토리 (`docs/`)

### `HADOOP_CONCEPTS.md`
Hadoop의 핵심 개념을 정리한 문서입니다.

**주요 내용:**
- Hadoop 개요 및 기원
- Hadoop Systems and Variants (Cloudera, Hortonworks, MapR 등)
- Apache Hadoop Architecture (Hadoop 1, 2, 3 비교)
- Key Features and Advantages
- Hadoop's Core Components:
  - HDFS (Hadoop Distributed File System)
  - MapReduce
  - YARN (Yet Another Resource Negotiator)
- The Expanding Hadoop Ecosystem

### `SETUP_GUIDE.md`
상세한 설정 가이드 문서입니다.

**주요 내용:**
- 사전 준비사항
- Local (Standalone) Mode Setup
- Single-Node Cluster Mode Setup (w/o YARN)
- Single-Node Cluster Mode Setup (with YARN)
- Multi-Node Cluster Mode Setup
- 트러블슈팅

### `PROJECT_STRUCTURE.md`
이 파일입니다. 프로젝트 구조를 설명합니다.

---

## ⚙️ 설정 파일 디렉토리 (`config/`)

### `core-site.xml.example`
Hadoop의 기본 파일시스템 설정 템플릿입니다.

**주요 설정:**
- `fs.defaultFS`: 기본 파일시스템 URI
  - Single-Node: `hdfs://localhost:9000`
  - Multi-Node: `hdfs://bigpie1:9000`

**사용 방법:**
```bash
cp config/core-site.xml.example $HADOOP_HOME/etc/hadoop/core-site.xml
# 환경에 맞게 수정
```

### `hdfs-site.xml.example`
HDFS 설정 템플릿입니다.

**주요 설정:**
- `dfs.replication`: 데이터 블록 복제 팩터
  - Single-Node: `1`
  - Multi-Node: `3`
- `dfs.datanode.data.dir`: DataNode 데이터 디렉토리
- `dfs.namenode.name.dir`: NameNode 메타데이터 디렉토리

### `mapred-site.xml.example`
MapReduce 설정 템플릿입니다.

**주요 설정:**
- `mapreduce.framework.name`: `yarn` (YARN 사용)
- `mapreduce.application.classpath`: MapReduce 클래스패스
- 메모리 설정 (Java heap space 오류 대응)
- JobHistory 서버 설정 (Multi-Node)

### `yarn-site.xml.example`
YARN 설정 템플릿입니다.

**주요 설정:**
- `yarn.resourcemanager.hostname`: ResourceManager 호스트명
- `yarn.nodemanager.aux-services`: `mapreduce_shuffle`
- 리소스 관리 설정 (메모리 할당)

---

## 🔧 스크립트 디렉토리 (`scripts/`)

### `setup_local_mode.sh`
Local (Standalone) Mode 설정 스크립트입니다.

**기능:**
- Java 확인
- Hadoop 다운로드 및 압축 해제
- JAVA_HOME 설정
- 버전 확인

**실행 방법:**
```bash
chmod +x scripts/setup_local_mode.sh
./scripts/setup_local_mode.sh
```

### `setup_single_node_wo_yarn.sh`
Single-Node Cluster Mode (YARN 없음) 설정 스크립트입니다.

**기능:**
- Hadoop 다운로드 및 설정
- `core-site.xml`, `hdfs-site.xml` 설정
- SSH 설정
- NameNode 포맷

**실행 방법:**
```bash
chmod +x scripts/setup_single_node_wo_yarn.sh
./scripts/setup_single_node_wo_yarn.sh
```

### `setup_single_node_with_yarn.sh`
Single-Node Cluster Mode (YARN 포함) 설정 스크립트입니다.

**기능:**
- `setup_single_node_wo_yarn.sh`의 모든 기능
- `mapred-site.xml`, `yarn-site.xml` 추가 설정
- YARN 데몬 시작 안내

**실행 방법:**
```bash
chmod +x scripts/setup_single_node_with_yarn.sh
./scripts/setup_single_node_with_yarn.sh
```

### `setup_multi_node_cluster.sh`
Multi-Node Cluster Mode 설정 스크립트입니다.

**기능:**
- 사전 준비사항 확인 (Java, ssh, pdsh)
- `/etc/hosts` 파일 편집 안내
- SSH 설정 및 키 배포
- 클러스터 관리 함수 추가
- Hadoop 설치 및 배포
- 환경 변수 설정

**⚠️ 주의:**
스크립트 내 변수를 실제 환경에 맞게 수정해야 합니다:
- `NAMENODE`: NameNode 호스트명
- `DATANODES`: DataNode 호스트명 배열
- `NODE_IPS`: 노드별 IP 주소

**실행 방법:**
```bash
# 스크립트 내 변수 수정 후
chmod +x scripts/setup_multi_node_cluster.sh
./scripts/setup_multi_node_cluster.sh
```

### `run_wordcount_example.sh`
Wordcount 예제 실행 스크립트입니다.

**기능:**
- 입력 파일 자동 생성
- Local Mode 또는 HDFS Mode 실행
- 결과 출력

**실행 방법:**
```bash
chmod +x scripts/run_wordcount_example.sh

# Local Mode
./scripts/run_wordcount_example.sh local

# HDFS Mode
./scripts/run_wordcount_example.sh
```

---

## 📋 파일별 역할 요약

| 파일 | 역할 | 모드 |
|------|------|------|
| `HADOOP_CONCEPTS.md` | 개념 정리 | - |
| `SETUP_GUIDE.md` | 설정 가이드 | 모든 모드 |
| `core-site.xml.example` | 파일시스템 설정 | 모든 모드 |
| `hdfs-site.xml.example` | HDFS 설정 | Cluster 모드 |
| `mapred-site.xml.example` | MapReduce 설정 | YARN 모드 |
| `yarn-site.xml.example` | YARN 설정 | YARN 모드 |
| `setup_local_mode.sh` | Local Mode 설정 | Local |
| `setup_single_node_wo_yarn.sh` | Single-Node 설정 | Single-Node |
| `setup_single_node_with_yarn.sh` | Single-Node + YARN 설정 | Single-Node |
| `setup_multi_node_cluster.sh` | Multi-Node 설정 | Multi-Node |
| `run_wordcount_example.sh` | 예제 실행 | 모든 모드 |

---

## 🔄 데이터 흐름

### Local Mode
```
입력 파일 → MapReduce → 출력 파일
```

### Single-Node Cluster Mode
```
입력 파일 → HDFS → MapReduce → HDFS → 출력 확인
```

### Multi-Node Cluster Mode
```
입력 파일 → HDFS (분산) → MapReduce (분산) → HDFS (분산) → 출력 확인
```

---

## 📝 사용 시나리오

### 시나리오 1: 처음 시작하는 사용자
1. `HADOOP_CONCEPTS.md` 읽기
2. `setup_local_mode.sh` 실행
3. `run_wordcount_example.sh local` 실행

### 시나리오 2: HDFS 학습
1. `setup_single_node_wo_yarn.sh` 실행
2. `sbin/start-dfs.sh` 실행
3. HDFS 명령어 연습
4. `run_wordcount_example.sh` 실행

### 시나리오 3: YARN 학습
1. `setup_single_node_with_yarn.sh` 실행
2. `sbin/start-dfs.sh && sbin/start-yarn.sh` 실행
3. 웹 인터페이스 확인
4. MapReduce 작업 실행

### 시나리오 4: 프로덕션 환경
1. `setup_multi_node_cluster.sh` 내 변수 수정
2. 스크립트 실행
3. 설정 파일 수동 편집
4. 클러스터 시작 및 테스트

---

## 🛠️ 커스터마이징

### 설정 파일 수정
1. `config/` 디렉토리의 예제 파일 복사
2. `.example` 확장자 제거
3. 환경에 맞게 수정
4. `$HADOOP_HOME/etc/hadoop/`에 배치

### 스크립트 수정
- 노드 IP 주소 및 호스트명
- Hadoop 버전
- 설치 경로
- 메모리 설정

---

## 📖 참고 자료

- [Apache Hadoop 공식 문서](https://hadoop.apache.org/docs/current/)
- [Hadoop 설정 가이드](https://hadoop.apache.org/docs/current/hadoop-project-dist/hadoop-common/SingleCluster.html)
- [Hadoop Ecosystem](www.turing.com/kb/hadoop-ecosystem-and-hadoop-components-for-big-data-problems)

