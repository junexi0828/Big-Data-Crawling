# 설치 및 환경 설정 가이드

프로젝트 설치 및 환경 설정을 위한 스크립트와 문서 모음입니다.

## 📋 파일 목록

### 설치 스크립트

#### `setup_all.sh` ⭐ **권장**

**모든 프로젝트 (Kafka, Scrapy, Selenium) 통합 설치**

```bash
./setup/setup_all.sh
```

**기능:**

- ✅ Python 가상환경 생성 및 설정
- ✅ Scrapy 프로젝트 의존성 설치
- ✅ Selenium 프로젝트 의존성 설치
- ✅ Kafka 프로젝트 Maven 빌드 (Java/Maven 필요)
- ✅ Hadoop 설치 (선택사항, Java 필요)
- ✅ 프로젝트 구조 확인 및 디렉토리 생성

**사용 시나리오:**

- 처음 프로젝트를 클론한 후 전체 환경 설정
- 모든 프로젝트를 한 번에 설치하고 싶을 때

#### `setup_scrapy.sh`

**Scrapy 프로젝트만 설치**

```bash
./setup/setup_scrapy.sh
```

**기능:**

- ✅ Python 가상환경 생성
- ✅ Scrapy 의존성 설치
- ✅ 출력 디렉토리 생성

#### `setup_selenium.sh`

**Selenium 프로젝트만 설치**

```bash
./setup/setup_selenium.sh
```

**주의:** Scrapy 가상환경이 먼저 생성되어 있어야 합니다.

**기능:**

- ✅ Selenium 의존성 설치
- ✅ 출력 디렉토리 생성

#### `setup_kafka.sh`

**Kafka 프로젝트만 빌드**

```bash
./setup/setup_kafka.sh
```

**요구사항:** Java JDK 8+ 및 Maven 3.x 필요

**기능:**

- ✅ Kafka Demo Maven 빌드
- ✅ Kafka Streams Maven 빌드

#### `setup_hadoop.sh`

**Hadoop 설치**

```bash
./setup/setup_hadoop.sh
```

**요구사항:** Java JDK 8+ 필요

**기능:**

- ✅ Java 확인 및 JAVA_HOME 설정
- ✅ Hadoop 바이너리 다운로드 (3.4.1)
- ✅ Local Mode 기본 설정
- ✅ hadoop-env.sh에 JAVA_HOME 설정

### 의존성 파일

#### `requirements.txt`

**Python 기본 패키지**

- Scrapy 및 관련 패키지
- kafka-python (Kafka Python 클라이언트)

#### `requirements-dev.txt`

**개발 환경용 추가 패키지**

- 코드 품질 도구 (black, flake8, mypy)
- 테스트 도구 (pytest)
- 문서화 도구 (sphinx)
- 개발 유틸리티 (ipython, jupyter)

### 문서

#### `REQUIREMENTS.md`

**전체 Requirements 가이드**

- 모든 프로젝트의 의존성 및 설치 요구사항
- 프로젝트별 설치 방법
- 플랫폼별 설치 가이드

#### `INSTALLATION.md`

**Scrapy 설치 가이드**

- Scrapy 프로젝트 설치 방법
- 문제 해결 가이드
- 플랫폼별 설치

## 🚀 사용 방법

### 전체 프로젝트 설치 (권장)

```bash
# 프로젝트 루트에서 실행
./setup/setup_all.sh
```

### 개별 프로젝트 설치

```bash
# Scrapy만 설치
./setup/setup_scrapy.sh

# Selenium만 설치 (Scrapy 환경 필요)
./setup/setup_selenium.sh

# Kafka만 빌드 (Java/Maven 필요)
./setup/setup_kafka.sh

# Hadoop만 설치 (Java 필요)
./setup/setup_hadoop.sh
```

## 📋 설치 순서

### 권장 순서

1. **전체 설치 (권장)**

   ```bash
   ./setup/setup_all.sh
   ```

2. **개별 설치 (선택적)**

   ```bash
   # 1. Scrapy 설치
   ./setup/setup_scrapy.sh

   # 2. Selenium 설치 (Scrapy 환경 사용)
   ./setup/setup_selenium.sh

   # 3. Kafka 빌드 (Java/Maven 필요)
   ./setup/setup_kafka.sh
   ```

## 🔍 설치 확인

### Python 패키지 확인

```bash
source scrapy_env/bin/activate
pip list | grep -E "scrapy|selenium|kafka-python"
```

### Java/Maven 확인

```bash
java -version
mvn -version
```

### 프로젝트별 테스트

```bash
# Scrapy
cd scrapy_project && scrapy list

# Selenium
cd selenium_project && python selenium_basics/webdriver_config.py

# Kafka
cd kafka_project && ./scripts/test_kafka.sh

# Hadoop
cd hadoop_project/hadoop-3.4.1 && ./bin/hadoop version
```

## ⚠️ 주의사항

1. **가상환경**: 모든 Python 프로젝트는 `scrapy_env` 가상환경을 공유합니다.
2. **Java/Maven**: Kafka 및 Hadoop 프로젝트는 Java JDK 8+가 필요합니다. Kafka는 Maven 3.x도 필요합니다.
3. **Kafka 서버**: Kafka 서버는 별도로 설치 및 시작해야 합니다.
   - macOS: `brew install kafka && brew services start kafka`
   - Linux: `kafka_project/docs/cluster_setup_guide.md` 참조
4. **Hadoop**: Hadoop은 기본적으로 Local Mode로 설치됩니다. Cluster Mode를 사용하려면 추가 설정이 필요합니다.
   - `hadoop_project/scripts/setup_single_node_wo_yarn.sh` 또는
   - `hadoop_project/docs/SETUP_GUIDE.md` 참조

## 🔗 관련 문서

- [전체 Requirements 가이드](REQUIREMENTS.md)
- [Scrapy 설치 가이드](INSTALLATION.md)
- [Kafka 클러스터 설정](../kafka_project/docs/cluster_setup_guide.md)
