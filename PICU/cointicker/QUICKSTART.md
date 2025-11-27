# 코인티커 프로젝트 빠른 시작 가이드

## 📋 현재 상태

✅ **완료된 작업**
- 프로젝트 구조 생성
- 기본 설정 파일 생성
- 공통 라이브러리 구현 (logger, utils, hdfs_client)
- Scrapy 프로젝트 초기화
- 첫 번째 Spider 구현 (Upbit Trends)

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 프로젝트 디렉토리로 이동
cd PICU/cointicker

# Python 가상환경 생성 (선택사항)
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate  # Windows

# 의존성 설치
pip install -r requirements.txt
```

### 2. 설정 파일 구성

```bash
# 설정 파일 복사 및 수정
cp config/cluster_config.yaml.example config/cluster_config.yaml
cp config/spider_config.yaml.example config/spider_config.yaml
cp config/database_config.yaml.example config/database_config.yaml

# 실제 값으로 수정
nano config/cluster_config.yaml
nano config/spider_config.yaml
nano config/database_config.yaml
```

### 3. Spider 테스트 (로컬)

```bash
# worker-nodes 디렉토리로 이동
cd worker-nodes

# Upbit Trends Spider 실행
scrapy crawl upbit_trends

# JSON 출력으로 실행
scrapy crawl upbit_trends -o output.json

# 로그 레벨 조정
scrapy crawl upbit_trends -L DEBUG
```

### 4. HDFS 연동 테스트

**전제 조건**
- Hadoop 클러스터가 실행 중이어야 함
- `HADOOP_HOME` 환경변수 설정
- HDFS에 접근 가능해야 함

```bash
# 환경변수 설정
export HADOOP_HOME=/opt/hadoop
export PATH=$PATH:$HADOOP_HOME/bin

# HDFS 연결 테스트
hdfs dfs -ls /

# Spider 실행 (HDFS Pipeline 활성화)
cd worker-nodes
scrapy crawl upbit_trends -s HDFS_NAMENODE=hdfs://localhost:9000
```

## 📁 프로젝트 구조

```
cointicker/
├── README.md                    # 프로젝트 개요
├── requirements.txt             # Python 의존성
├── QUICKSTART.md               # 이 파일
│
├── config/                      # 설정 파일
│   ├── cluster_config.yaml.example
│   ├── spider_config.yaml.example
│   └── database_config.yaml.example
│
├── shared/                      # 공통 라이브러리
│   ├── __init__.py
│   ├── logger.py               # 로깅 유틸리티
│   ├── utils.py                # 공통 함수
│   └── hdfs_client.py          # HDFS 클라이언트
│
├── worker-nodes/                # 워커 노드 코드
│   ├── scrapy.cfg              # Scrapy 설정
│   ├── cointicker/
│   │   ├── __init__.py
│   │   ├── items.py            # Item 정의
│   │   ├── settings.py         # Scrapy 설정
│   │   ├── middlewares.py      # 미들웨어
│   │   ├── pipelines.py        # 파이프라인 (HDFS 저장)
│   │   └── spiders/
│   │       ├── __init__.py
│   │       └── upbit_trends.py # Upbit Trends Spider
│   ├── logs/                   # 로그 디렉토리
│   └── data/                   # 임시 데이터 디렉토리
│
├── master-node/                 # 마스터 노드 코드 (예정)
├── backend/                     # 백엔드 코드 (예정)
├── frontend/                    # 프론트엔드 코드 (예정)
└── deployment/                  # 배포 스크립트 (예정)
```

## 🔧 다음 단계

### 즉시 구현 가능

1. **추가 Spider 구현**
   - Coinness News Spider
   - SaveTicker Spider
   - Perplexity Finance Spider
   - CNN Fear & Greed Spider

2. **MapReduce 작업 구현**
   - 데이터 정제 Mapper
   - 데이터 집계 Reducer

3. **백엔드 기본 구조**
   - FastAPI 프로젝트 초기화
   - MariaDB 스키마 설계

### 참고 문서

- [개발 로드맵](../PICU_docs/DEVELOPMENT_ROADMAP.md)
- [개발 흐름 분석](../PICU_docs/DEVELOPMENT_ANALYSIS.md)

## ⚠️ 주의사항

1. **HDFS 연결**
   - Hadoop 클러스터가 실행 중이어야 함
   - 네트워크 연결 확인 필요

2. **API 제한**
   - Upbit API는 요청 제한이 있음
   - `DOWNLOAD_DELAY` 설정 확인

3. **로컬 테스트**
   - HDFS 없이도 Spider는 테스트 가능
   - JSON 파일로 출력하여 확인

## 🐛 문제 해결

### HDFS 연결 실패
```bash
# HDFS 상태 확인
hdfs dfsadmin -report

# NameNode 확인
jps | grep NameNode
```

### Spider 실행 오류
```bash
# 상세 로그 확인
scrapy crawl upbit_trends -L DEBUG

# 설정 확인
scrapy settings --get HDFS_NAMENODE
```

## 📞 지원

문제가 발생하면 다음을 확인하세요:
1. 로그 파일 (`worker-nodes/logs/scrapy.log`)
2. 설정 파일 값 확인
3. 네트워크 연결 상태

