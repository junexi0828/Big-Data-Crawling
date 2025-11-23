# Kafka 프로젝트 문서 가이드

이 디렉토리에는 Kafka 프로젝트의 모든 문서가 포함되어 있습니다.

## 📚 문서 목록

### 설정 가이드

- **[cluster_setup_guide.md](cluster_setup_guide.md)**: 3-node Kafka 클러스터 설정 가이드

  - KRaft Quorum 설정
  - 각 노드별 server.properties 설정
  - 클러스터 초기화 및 시작 절차

- **[WINDOWS_SINGLE_MACHINE_SETUP.md](WINDOWS_SINGLE_MACHINE_SETUP.md)**: Windows 단일 머신 설정 가이드
  - Windows에서 Kafka 서버 설정
  - UUID 생성 및 로그 디렉토리 포맷
  - Linux/Mac 단일 머신 설정도 포함

### 프로젝트 구조

- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)**: 상세 프로젝트 구조 설명
  - 전체 디렉토리 구조
  - 각 파일의 역할 및 설명
  - 데이터 흐름 다이어그램
  - 학습 경로

### 테스트 결과

- **[KAFKA_TEST_RESULTS.md](KAFKA_TEST_RESULTS.md)**: 기본 Kafka 기능 테스트 결과

  - Topic 생성/삭제 테스트
  - Producer/Consumer 테스트 결과
  - macOS vs Windows 명령어 차이

- **[CLUSTER_TEST_RESULTS.md](CLUSTER_TEST_RESULTS.md)**: 3-node 클러스터 테스트 결과
  - Topic with Partitions 테스트
  - Producer 설정 테스트
  - Consumer Groups 테스트
  - Offset 관리 테스트

## 🔗 관련 문서

프로젝트의 다른 디렉토리에도 추가 문서가 있습니다:

- **[../README.md](../README.md)**: 프로젝트 전체 개요 및 빠른 시작
- **[../kafka_demo/README.md](../kafka_demo/README.md)**: Producer/Consumer 가이드
- **[../kafka_demo/DEPLOYMENT.md](../kafka_demo/DEPLOYMENT.md)**: Runnable JAR 배포 가이드
- **[../kafka_streams/README.md](../kafka_streams/README.md)**: Streams 가이드

## 📖 문서 읽기 순서

### 초보자를 위한 추천 순서

1. [프로젝트 전체 개요](../README.md)
2. [Windows 단일 머신 설정](WINDOWS_SINGLE_MACHINE_SETUP.md) 또는 [클러스터 설정](cluster_setup_guide.md)
3. [프로젝트 구조](PROJECT_STRUCTURE.md)
4. [Producer/Consumer 가이드](../kafka_demo/README.md)
5. [Streams 가이드](../kafka_streams/README.md)

### 고급 사용자를 위한 추천 순서

1. [프로젝트 구조](PROJECT_STRUCTURE.md)
2. [클러스터 설정](cluster_setup_guide.md)
3. [테스트 결과](CLUSTER_TEST_RESULTS.md)
4. [배포 가이드](../kafka_demo/DEPLOYMENT.md)
