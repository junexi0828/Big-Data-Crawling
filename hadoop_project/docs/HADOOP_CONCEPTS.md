# Apache Hadoop 개념 정리

## 📚 목차

1. [Hadoop 개요](#hadoop-개요)
2. [Hadoop Systems and Variants](#hadoop-systems-and-variants)
3. [Apache Hadoop Architecture](#apache-hadoop-architecture)
4. [Key Features and Advantages](#key-features-and-advantages)
5. [Hadoop's Core Components](#hadoops-core-components)
6. [The Expanding Hadoop Ecosystem](#the-expanding-hadoop-ecosystem)

---

## Hadoop 개요

### 정의

Apache Hadoop은 **대규모 데이터셋(PB 이상)의 분산 저장 및 처리**를 위한 오픈소스 프레임워크입니다.

### 기원

- **GFS (Google File System)**와 **MapReduce 메커니즘**에서 파생
- 저렴한 Linux 머신을 사용한 DFS 구현
- 빅데이터 분석을 위한 저장 및 처리 프레임워크 제공

### 현재 버전

- **Hadoop 3.4.x** (최신 안정 버전)
- Apache Spark 통합으로 강력한 처리 기능 제공

---

## Hadoop Systems and Variants

### Apache Hadoop

- **핵심 오픈소스 프로젝트**
- 모든 Hadoop 배포판의 기반

### 주요 배포판 (Major Distributions)

#### 1. Cloudera

- **특징**: Cloudera Manager 제공
- **역사**: 2018년 Hortonworks와 합병

#### 2. Hortonworks

- **특징**: 오픈소스 Hadoop 지원, Ambari 제공
- **역사**: 2018년 Cloudera와 합병

#### 3. MapR Technologies

- **특징**: MapR Distribution
- **역사**: 2019년 HPE에 인수

#### 4. Pivotal Software

- **특징**: HAWQ, Greenplum
- **역사**: 2019년 VMware에 인수

#### 5. Teradata

- **특징**: Hortonworks 기반 데이터 관리 → Teradata Vantage

#### 6. IBM

- **특징**: InfoSphere BigInsights

#### 7. Microsoft

- **특징**: Azure HDInsight (Hadoop 기반 관리형 서비스)

#### 8. Amazon

- **특징**:
  - EMR (Elastic MapReduce)
  - RedShift
  - Kinesis

---

## Apache Hadoop Architecture

### 설계 목표

- **확장 가능한 저장 및 처리**: 대규모 데이터셋(PB ↑) 처리
- **기반 기술**:
  - **HDFS**: 분산 저장
  - **YARN**: 리소스 관리

### 데이터 접근 패턴

- **Write-once, Read-many (WORM)**: 대규모 데이터 분석에 최적화

### 아키텍처 진화

#### Hadoop 1

- **특징**:
  - Silos & Largely batch
  - Single Processing engine
- **구조**:
  ```
  Applications (Pig, Hive, HBase, Storm, etc.)
         ↓
  MapReduce (Cluster Resource Management & Data Processing)
         ↓
  HDFS (Hadoop Distributed File System)
  ```

#### Hadoop 2 (YARN 도입)

- **특징**:
  - Multiple Engines, Single Data Set
  - Batch, Interactive & Real-Time
- **주요 변화**:
  - YARN 도입으로 리소스 관리와 MapReduce 분리
  - 다양한 워크로드 지원 (batch, interactive, in-memory, stream)
- **구조**:
  ```
  Applications (Pig, Hive, HBase, Storm, Spark, etc.)
         ↓
  YARN: Data Operating System (Cluster Resource Management)
         ↓
  HDFS (Hadoop Distributed File System)
  ```

#### Hadoop 3

- **주요 개선사항**:
  - **Erasure Coding**: 저장 공간 효율성 향상
  - **Containerization**: 컨테이너 지원
  - **GPU-aware scheduling**: GPU 스케줄링 지원

---

## Key Features and Advantages

### 1. Fault Tolerance (장애 허용)

- **데이터 중복 저장**: 여러 노드에 데이터 저장
- **방식**:
  - **Replication**: 데이터 복제 (기본 3회)
  - **Erasure Coding**: 패리티 블록 사용 (N-data block + M-parity block)

### 2. Parallelization (병렬화)

- **분산 컴퓨팅**: MapReduce 또는 Spark를 통한 병렬 처리
- **데이터 로컬리티**: 데이터를 계산으로 이동 (반대가 아님)

### 3. Handles Large Datasets (대용량 데이터 처리)

- **파일 크기 제한 없음**: 블록 기반 저장으로 인한 제한 없음

### 4. Immutable File System (불변 파일 시스템)

- **WORM (Write-Once, Read-Many)**:
  - 파일은 한 번만 쓰기 가능
  - 여러 번 읽기 가능
  - 대규모 순차 읽기에 최적화
- **추가 기능**: 현재는 부분적으로 append 지원

---

## Hadoop's Core Components

### 1. HDFS (Hadoop Distributed File System)

#### 정의

- **분산형, 장애 허용, 확장 가능한 파일 시스템**
- **상용 하드웨어**에서 실행되도록 설계

#### Master-Slave 아키텍처

##### NameNode (마스터)

- **역할**:
  - 파일시스템 네임스페이스 및 메타데이터 관리
  - 파일명, 디렉토리, 블록 위치, 권한 정보 저장
- **특징**:
  - Single Point of Failure (단일 장애점)
  - **Stand-by NameNode**로 고가용성 제공

##### DataNode (슬레이브)

- **역할**: 실제 데이터 블록 저장
- **기능**:
  - 주기적으로 NameNode에 **heartbeat** 전송
  - **block report** 전송

#### 데이터 저장 방식

##### Blocks (블록)

- 파일을 큰 블록으로 분할
- **기본 블록 크기**: 128MB 또는 256MB

##### Replication (복제)

- 각 블록을 여러 DataNode에 복제
- **기본 복제 팩터**: 3회
- 장애 허용을 위한 중복 저장

#### WORM 시스템 설계

- **Write-once, Read-many**:
  - 대규모 순차 읽기에 최적화
  - Append 지원 (랜덤 쓰기는 불가)

---

### 2. MapReduce

#### 정의

- **프로그래밍 모델 및 처리 엔진**
- 대규모 분산 처리용

#### 기능

- 큰 문제를 작고 독립적인 하위 문제로 분할
- 병렬 처리 가능

#### 처리 단계

##### 1. Map Phase

- **입력**: key-value 쌍
- **출력**: 중간 key-value 쌍
- **기능**: 필터링, 정렬

##### 2. Shuffle & Sort Phase

- **기능**:
  - 모든 중간 값을 키별로 그룹화
  - MapReduce 프레임워크가 자동 수행

##### 3. Reduce Phase

- **입력**: 같은 키를 가진 중간 값들
- **출력**: 최종 결과
- **기능**: 집계, 요약

#### 장점 (+)

- 높은 확장성
- 장애 허용
- 배치 처리용 간단한 프로그래밍 모델

#### 단점 (-)

- 반복 알고리즘에 부적합
- 실시간 처리에 부적합

#### 예제: Word Counting

```
Input → Map → (Shuffle & Sort) → Reduce → Output
```

**예시**: 분산 데이터베이스의 모든 단어에서 가장 많이 나타나는 3개 문자 찾기

---

### 3. YARN (Yet Another Resource Negotiator)

#### 역할

- **클러스터 리소스 관리**
- Hadoop 2에서 도입

#### 주요 기능

- 리소스 할당 및 관리
- 다양한 워크로드 지원:
  - Batch (MapReduce)
  - Interactive (Hive, Impala)
  - In-memory (Spark)
  - Stream (Storm, Flink)

#### 구성 요소

##### ResourceManager

- **역할**: 클러스터 전체 리소스 관리
- **기능**: 애플리케이션 리소스 할당

##### NodeManager

- **역할**: 각 노드의 리소스 사용 및 작업 실행 감독
- **기능**:
  - 노드별 리소스 모니터링
  - 컨테이너 관리

---

## The Expanding Hadoop Ecosystem

### 개요

Hadoop은 HDFS와 MapReduce만이 아닌 **광범위한 도구 모음**입니다. 각 도구는 HDFS/MapReduce의 특정 격차를 해결합니다.

### Hadoop 생태계 구성 요소

#### 1. Resource Management (리소스 관리)

- **YARN**: 클러스터 및 리소스 관리

#### 2. Data Access & Querying (데이터 접근 및 쿼리)

- **Hive**: SQL 인터페이스
- **Pig**: 데이터플로우 언어
- **Impala**: 대화형 SQL 쿼리 엔진

#### 3. NoSQL Databases (NoSQL 데이터베이스)

- **HBase**: 컬럼 기반 데이터베이스
- **Cassandra**: 분산 NoSQL 데이터베이스

#### 4. Stream Processing (스트림 처리)

- **Spark Streaming**: 실시간 스트림 처리
- **Flink**: 분산 스트림 처리
- **Storm**: 실시간 계산 시스템
- **Kafka Streams**: Kafka 기반 스트림 처리

#### 5. Orchestration & Workflow (오케스트레이션 및 워크플로우)

- **Oozie**: 워크플로우 모니터링 및 관리

#### 6. Machine Learning (머신러닝)

- **Mahout**: 분산 머신러닝 라이브러리

#### 7. Data Ingestion (데이터 수집)

- **Sqoop**: RDBMS 커넥터
- **Flume**: 로그 데이터 수집
- **Kafka**: 분산 메시징 시스템

#### 8. Coordination (조정)

- **ZooKeeper**: 분산 시스템 조정 서비스

### 생태계 아키텍처 레이어

```
┌─────────────────────────────────────────┐
│  Data Management                        │
│  (Oozie, Chukwa, Flume, ZooKeeper)     │
├─────────────────────────────────────────┤
│  Data Access                            │
│  (Hive, Pig, Mahout, Avro, Sqoop)      │
├─────────────────────────────────────────┤
│  Data Processing                        │
│  (MapReduce, YARN)                      │
├─────────────────────────────────────────┤
│  Data Storage                           │
│  (HDFS, HBase)                          │
└─────────────────────────────────────────┘
```

---

## 참고 자료

- [Hadoop Ecosystem Components](www.turing.com/kb/hadoop-ecosystem-and-hadoop-components-for-big-data-problems)
- Apache Hadoop 공식 문서: https://hadoop.apache.org/
