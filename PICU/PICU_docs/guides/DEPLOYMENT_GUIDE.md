# PICU 프로젝트 배포 가이드

**작성 일시**: 2025-11-29
**대상**: 라즈베리파이 클러스터 배포 및 Docker 배포
**버전**: 1.0

---

## 📋 목차

1. [개요](#개요)
2. [시스템 요구사항](#시스템-요구사항)
3. [컴포넌트별 설치 방식](#컴포넌트별-설치-방식)
4. [배포 전략](#배포-전략)
5. [라즈베리파이 클러스터 배포](#라즈베리파이-클러스터-배포)
6. [Docker 배포](#docker-배포)
7. [배포 시나리오 비교](#배포-시나리오-비교)
8. [문제 해결](#문제-해결)

---

## 개요

PICU 프로젝트는 라즈베리파이 4대를 활용한 분산 클러스터 시스템입니다. 이 문서는 프로젝트를 실제 환경에 배포하는 방법을 안내합니다.

### 배포 대상 환경

- **Tier 1**: 라즈베리파이 클러스터 (4대)
  - Master Node: Hadoop NameNode, YARN ResourceManager, Scrapyd Scheduler
  - Worker Nodes (3대): Hadoop DataNode, Scrapy Spiders, MapReduce
- **Tier 2**: 외부 서버 (선택적)
  - FastAPI Backend, MariaDB, React Frontend

---

## 시스템 요구사항

### 하드웨어

- **라즈베리파이 4대** (라즈베리파이 4 권장)
  - RAM: 4GB 이상
  - Storage: 32GB 이상 (SD 카드)
  - 네트워크: 이더넷 연결

### 소프트웨어

- **OS**: Raspberry Pi OS (Debian 기반) 또는 Ubuntu Server
- **Python**: 3.8 이상
- **Java**: JDK 8 이상 (Hadoop, Kafka용)
- **Maven**: 3.x (Kafka Java 프로젝트용, 선택적)

---

## 컴포넌트별 설치 방식

### 설치 방식 요약

| 컴포넌트     | 서버/바이너리 위치                         | 클라이언트/라이브러리 위치   | 설치 방식               |
| ------------ | ------------------------------------------ | ---------------------------- | ----------------------- |
| **하둡**     | `hadoop_project/hadoop-3.4.1/` (직접 설치) | 가상환경 (`pyarrow`, `hdfs`) | 바이너리 다운로드 + pip |
| **카프카**   | 시스템 (`/opt/homebrew/opt/kafka` - brew)  | 가상환경 (`kafka-python`)    | brew 설치 + pip         |
| **스크래피** | 없음 (Python 패키지)                       | 가상환경 (`scrapy`)          | pip                     |
| **셀레니움** | 없음 (Python 패키지)                       | 가상환경 (`selenium`)        | pip                     |

### 상세 설명

#### 1. 하둡 (Hadoop)

**바이너리 위치**: `bigdata/hadoop_project/hadoop-3.4.1/` (1.7GB)

- **설치 방식**: Apache 공식 바이너리 다운로드 및 압축 해제
- **가상환경 여부**: ❌ 아님 (Java 기반 바이너리 직접 설치)
- **Python 클라이언트**: 가상환경에 설치 (`pyarrow>=14.0.0`, `hdfs>=2.7.0`)
- **자동 감지**: PICU의 `HDFSManager`가 `hadoop_project/hadoop-3.4.1` 경로를 자동으로 검색

**설치 확인**:

```bash
# hadoop_project에 하둡 존재 확인
ls -la hadoop_project/hadoop-3.4.1/bin/hadoop

# HADOOP_HOME 자동 감지 확인
python -c "from PICU.cointicker.gui.modules.managers.hdfs_manager import HDFSManager; print(HDFSManager().check_and_start())"
```

#### 2. 카프카

**서버 위치**: 시스템에 brew/apt로 설치

- **macOS**: `brew install kafka` → `/opt/homebrew/opt/kafka`
- **Linux**: `apt install kafka` → 시스템 경로
- **Python 클라이언트**: 가상환경에 설치 (`kafka-python>=2.0.2`)

**설치 확인**:

```bash
# Kafka 서버 확인
which kafka-server-start

# Python 클라이언트 확인
pip list | grep kafka-python
```

#### 3. 스크래피 & 셀레니움

**설치 위치**: 가상환경에 pip로 설치

- **가상환경**:
  - `scrapy_env/` (프로젝트 루트)
  - `PICU/venv/` (PICU 프로젝트)
  - `PICU/cointicker/venv/` (코인티커 프로젝트)
- **설치 방법**: `pip install -r requirements.txt`

**설치 확인**:

```bash
source venv/bin/activate
scrapy version
python -c "import selenium; print(selenium.__version__)"
```

---

## 배포 전략

### 전략 비교

#### 옵션 1: 하이브리드 방식 (권장) ⭐

**각 컴포넌트별 배포 방식**:

| 컴포넌트              | 배포 방식             | 이유                                   |
| --------------------- | --------------------- | -------------------------------------- |
| **하둡**              | 직접 배포 (현재 방식) | 클러스터 구성 필요, 네트워크 설정 복잡 |
| **카프카**            | Docker 또는 직접 배포 | 클러스터 구성 가능, Docker로 관리 용이 |
| **스크래피/셀레니움** | Docker (권장)         | 가상환경 의존성 관리 간편              |
| **PICU 애플리케이션** | Docker (권장)         | 일관된 환경, 배포 간편                 |

**장점**:

- 각 컴포넌트의 특성에 맞는 최적의 배포 방식 선택
- 하둡 클러스터 구성의 복잡도 최소화
- PICU 애플리케이션의 의존성 관리 간편

**단점**:

- 배포 방식이 혼재되어 관리 복잡도 증가
- Docker와 직접 배포의 혼용

#### 옵션 2: 전체 Docker화

**모든 컴포넌트를 Docker로 배포**

**장점**:

- 일관된 환경
- 의존성 관리 간편
- 배포 자동화 용이

**단점**:

- 하둡 클러스터 구성 복잡 (네트워크, 볼륨 설정)
- 리소스 오버헤드
- 디버깅 어려움

### 권장 배포 전략

**하이브리드 방식 (옵션 1) 권장**

1. **하둡**: 직접 배포 (클러스터 구성 복잡도)
2. **PICU 애플리케이션**: Docker (의존성 관리)
3. **카프카**: 환경에 따라 선택 (시스템 설치 또는 Docker)

---

## 라즈베리파이 클러스터 배포

### 사전 준비

#### 1. 네트워크 설정

각 라즈베리파이에 고정 IP와 호스트명 설정:

```bash
# /etc/hosts 파일 수정 (각 노드에서)
192.168.1.100 raspberry-master
192.168.1.101 raspberry-worker1
192.168.1.102 raspberry-worker2
192.168.1.103 raspberry-worker3
```

#### 2. SSH 키 설정

개발 PC에서 각 노드로 패스워드 없는 SSH 접속 설정:

```bash
# SSH 키 생성 (이미 있으면 생략)
ssh-keygen -t rsa

# 각 노드에 키 복사
ssh-copy-id pi@raspberry-master
ssh-copy-id pi@raspberry-worker1
ssh-copy-id pi@raspberry-worker2
ssh-copy-id pi@raspberry-worker3
```

### 배포 단계

#### 1단계: 하둡 배포

```bash
# 개발 PC에서
cd hadoop_project

# 하둡 클러스터 배포
./deployment/deploy_all.sh
```

**이 스크립트가 하는 일**:

- NameNode에 `/opt/hadoop` 설치
- 설정 파일 배포 (`core-site.xml`, `hdfs-site.xml`)
- DataNode에 rsync로 복사
- 환경변수 설정

**수동 배포 (스크립트 사용 불가 시)**:

```bash
# NameNode에 하둡 설치
scp -r hadoop_project/hadoop-3.4.1 pi@raspberry-master:/opt/hadoop

# 각 노드에 설정 파일 배포
scp hadoop_project/config/*.xml pi@raspberry-master:/opt/hadoop/etc/hadoop/
```

#### 2단계: 카프카 배포 (선택)

**옵션 A: 시스템에 직접 설치**

```bash
# 각 노드에서
sudo apt update
sudo apt install kafka
```

**옵션 B: Docker로 배포**

```bash
# docker-compose.kafka.yml 생성 후
docker-compose -f docker-compose.kafka.yml up -d
```

#### 3단계: PICU 애플리케이션 배포

**방법 1: 배포 스크립트 사용 (권장)**

```bash
# 개발 PC에서
cd PICU

# Master Node 배포
./deployment/setup_master.sh

# Worker Nodes 배포
./deployment/setup_worker.sh raspberry-worker1 192.168.1.101
./deployment/setup_worker.sh raspberry-worker2 192.168.1.102
./deployment/setup_worker.sh raspberry-worker3 192.168.1.103

# 또는 모든 노드 한 번에
./deployment/setup_all_nodes.sh
```

**배포 스크립트가 하는 일**:

1. 코드 전송 (rsync)
2. 가상환경 생성
3. Python 의존성 설치 (`pip install -r requirements.txt`)
4. systemd 서비스 등록 (선택적)

**방법 2: 수동 배포**

```bash
# Master Node
rsync -avz --exclude 'venv' --exclude '__pycache__' \
    PICU/cointicker/master-node/ \
    pi@raspberry-master:/home/pi/cointicker/master-node/

# Worker Node
rsync -avz --exclude 'venv' --exclude '__pycache__' \
    PICU/cointicker/worker-nodes/ \
    pi@raspberry-worker1:/home/pi/cointicker/worker-nodes/
```

#### 4단계: 서비스 시작

**하둡 시작**:

```bash
# NameNode에서
ssh pi@raspberry-master
cd /opt/hadoop
./sbin/start-dfs.sh
./sbin/start-yarn.sh
```

**PICU 애플리케이션 시작**:

```bash
# Master Node
ssh pi@raspberry-master
cd /home/pi/cointicker
source venv/bin/activate
python master-node/orchestrator.py

# Worker Node
ssh pi@raspberry-worker1
cd /home/pi/cointicker
source venv/bin/activate
python worker-nodes/cointicker/spiders/run_spider.py
```

---

## Docker 배포

### Docker 배포 시나리오

**다른 사용자에게 전달할 때 Docker로 묶어서 배포하면, 라즈베리파이 4대만 연결하면 바로 사용 가능합니다.**

### Dockerfile 예시

#### Master Node Dockerfile

```dockerfile
# docker/Dockerfile.master
FROM python:3.11-slim

WORKDIR /app

# hadoop_project의 하둡을 컨테이너에 복사
COPY hadoop_project/hadoop-3.4.1 /opt/hadoop

# PICU 코드 복사
COPY PICU/cointicker/master-node /app/master-node
COPY PICU/cointicker/shared /app/shared
COPY PICU/cointicker/config /app/config

# 의존성 설치
COPY PICU/requirements/requirements-master.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 환경변수 설정
ENV HADOOP_HOME=/opt/hadoop
ENV PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin

CMD ["python", "master-node/orchestrator.py"]
```

#### Worker Node Dockerfile

```dockerfile
# docker/Dockerfile.worker
FROM python:3.11-slim

WORKDIR /app

# hadoop_project의 하둡을 컨테이너에 복사
COPY hadoop_project/hadoop-3.4.1 /opt/hadoop

# PICU 코드 복사
COPY PICU/cointicker/worker-nodes /app/worker-nodes
COPY PICU/cointicker/shared /app/shared
COPY PICU/cointicker/config /app/config

# 의존성 설치
COPY PICU/requirements/requirements-worker.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 환경변수 설정
ENV HADOOP_HOME=/opt/hadoop
ENV PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin

CMD ["python", "worker-nodes/cointicker/spiders/run_spider.py"]
```

### Docker Compose 예시

```yaml
# docker-compose.yml
version: "3.8"

services:
  # Hadoop NameNode
  hadoop-namenode:
    build:
      context: .
      dockerfile: docker/Dockerfile.hadoop-namenode
    networks:
      - hadoop-cluster
    volumes:
      - hadoop-namenode-data:/opt/hadoop/data

  # Hadoop DataNode
  hadoop-datanode:
    build:
      context: .
      dockerfile: docker/Dockerfile.hadoop-datanode
    networks:
      - hadoop-cluster
    depends_on:
      - hadoop-namenode

  # Kafka
  kafka:
    image: confluentinc/cp-kafka:latest
    networks:
      - kafka-cluster
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092

  # PICU Master
  picu-master:
    build:
      context: .
      dockerfile: docker/Dockerfile.master
    depends_on:
      - hadoop-namenode
      - kafka
    networks:
      - hadoop-cluster
      - kafka-cluster

  # PICU Worker
  picu-worker:
    build:
      context: .
      dockerfile: docker/Dockerfile.worker
    depends_on:
      - hadoop-datanode
      - kafka
    networks:
      - hadoop-cluster
      - kafka-cluster

networks:
  hadoop-cluster:
  kafka-cluster:

volumes:
  hadoop-namenode-data:
```

### Docker 배포 사용법

**이미지 빌드**:

```bash
# Master Node 이미지
docker build -t picu-master:latest -f docker/Dockerfile.master .

# Worker Node 이미지
docker build -t picu-worker:latest -f docker/Dockerfile.worker .
```

**배포 및 실행**:

```bash
# Docker Compose로 전체 실행
docker-compose up -d

# 또는 개별 실행
docker run -d --name picu-master picu-master:latest
docker run -d --name picu-worker picu-worker:latest
```

**사용자가 해야 할 일**:

```bash
# 1. Docker 이미지 받기
docker pull your-registry/picu-cluster:latest

# 2. docker-compose 실행
docker-compose up -d

# 끝! 바로 사용 가능
```

---

## 배포 시나리오 비교

### 시나리오 1: 라즈베리파이 클러스터 직접 배포 (현재 방식)

**대상**: 개발자가 직접 라즈베리파이 클러스터에 배포

**단계**:

1. 하둡 배포 (`hadoop_project/deployment/deploy_all.sh`)
2. 카프카 배포 (시스템 설치 또는 Docker)
3. PICU 애플리케이션 배포 (`PICU/deployment/setup_all_nodes.sh`)

**장점**:

- 각 노드의 상태를 직접 확인 가능
- 디버깅 용이
- 리소스 오버헤드 없음

**단점**:

- 수동 작업 필요
- 환경 차이 발생 가능
- 배포 시간 소요

### 시나리오 2: Docker 배포 (다른 사용자에게 전달)

**대상**: 다른 사용자가 라즈베리파이 4대만 연결하여 사용

**단계**:

1. Docker 이미지 빌드 (개발자가 수행)
2. Docker 이미지 배포 (레지스트리 또는 파일)
3. `docker-compose up -d` 실행

**장점**:

- ✅ **바로 사용 가능** (의존성 모두 포함)
- 환경 일관성
- 배포 간편

**단점**:

- Docker 이미지 크기 (하둡 포함 시 2GB+)
- Docker 리소스 오버헤드
- 하둡 클러스터 구성 복잡도

### 시나리오 3: Git 클론

**대상**: 소스 코드를 공개하고 사용자가 직접 설치

**단계**:

1. `git clone <repository>`
2. 하둡 설치
3. 카프카 설치
4. Python 의존성 설치
5. 설정 파일 수정
6. 네트워크 설정

**장점**:

- 소스 코드 공개/공유 용이
- 버전 관리 가능
- 커스터마이징 가능

**단점**:

- ❌ **바로 사용 불가** (모든 것을 수동 설치)
- 사용자 기술 수준 요구
- 환경 차이 발생 가능

### 비교표

| 시나리오        | 사용자 작업량             | 바로 사용 가능? | 의존성 포함? | 권장 대상                |
| --------------- | ------------------------- | --------------- | ------------ | ------------------------ |
| **직접 배포**   | 중간 (배포 스크립트 사용) | ⚠️ 부분적       | ❌ 별도 설치 | 개발자                   |
| **Docker 배포** | 최소 (docker-compose만)   | ✅ 예           | ✅ 모두 포함 | 일반 사용자              |
| **Git 클론**    | 많음 (모두 수동 설치)     | ❌ 아니오       | ❌ 별도 설치 | 개발자/커스터마이징 필요 |

---

## 문제 해결

### 하둡 관련

**문제**: HADOOP_HOME을 찾을 수 없음

**해결**:

```bash
# HDFSManager가 자동으로 hadoop_project 경로를 찾음
# 수동 설정이 필요한 경우:
export HADOOP_HOME=/path/to/hadoop_project/hadoop-3.4.1
```

**문제**: HDFS 연결 실패

**해결**:

```bash
# HDFS 서비스 실행 확인
jps | grep -E "NameNode|DataNode"

# HDFS 시작
cd /opt/hadoop
./sbin/start-dfs.sh
```

### Python 의존성 관련

**문제**: 가상환경에서 패키지를 찾을 수 없음

**해결**:

```bash
# 가상환경 활성화 확인
source venv/bin/activate

# 의존성 재설치
pip install -r requirements.txt
```

### 네트워크 관련

**문제**: SSH 연결 실패

**해결**:

```bash
# SSH 키 확인
ssh-copy-id pi@raspberry-master

# 호스트명 확인
cat /etc/hosts
```

### Docker 관련

**문제**: Docker 이미지 크기가 너무 큼

**해결**:

- 하둡을 볼륨 마운트로 분리
- 멀티 스테이지 빌드 사용
- 불필요한 파일 제외

---

## 참고 자료

- [HDFS 연동 문제 분석 보고서](../troubleshooting/HDFS_연동_문제_분석_보고서.md)
- [실습 통합 클러스터 구성](./실습통합클러스터구성.md)
- [GUI 가이드](./GUI_GUIDE.md)
- [통합 가이드](./INTEGRATION_GUIDE.md)

---

**작성자**: JUNS_AI_MCP
**최종 업데이트**: 2025-11-29
**버전**: 1.0
