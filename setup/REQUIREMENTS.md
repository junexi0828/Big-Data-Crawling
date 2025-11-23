# 프로젝트 전체 Requirements 가이드

Big Data 프로젝트 (Kafka, Scrapy, Selenium)의 모든 의존성 및 설치 요구사항을 정리한 문서입니다.

## 📋 전체 요구사항 요약

### 시스템 요구사항

- **운영체제**: Linux, macOS, Windows
- **Python**: 3.8 이상
- **Java**: JDK 8 이상 (Kafka용)
- **Maven**: 3.x (Kafka용)

## 🔧 프로젝트별 요구사항

### 1. Scrapy 프로젝트

#### Python 패키지

**파일**: `setup/requirements.txt`

```txt
Scrapy==2.13.3
requests==2.32.5
lxml==6.0.1
itemloaders==1.3.2
kafka-python==2.0.2  # Kafka 연동용
```

**주요 의존성:**

- `Scrapy>=2.13.3`: 웹 크롤링 프레임워크
- `requests>=2.32.5`: HTTP 라이브러리
- `lxml>=6.0.1`: XML/HTML 파서
- `itemloaders>=1.3.2`: 데이터 전처리
- `kafka-python==2.0.2`: Kafka Python 클라이언트

#### 설치 방법

```bash
# 가상환경 생성
python3 -m venv scrapy_env
source scrapy_env/bin/activate

# 의존성 설치
pip install -r setup/requirements.txt
```

### 2. Selenium 프로젝트

#### Python 패키지

**파일**: `selenium_project/requirements_selenium.txt`

```txt
selenium==4.15.2
webdriver-manager==4.0.1
pandas==2.1.3
```

**주요 의존성:**

- `selenium>=4.15.2`: 웹 자동화 프레임워크
- `webdriver-manager>=4.0.1`: WebDriver 자동 관리
- `pandas>=2.1.3`: 데이터 분석 (선택사항)

#### 추가 요구사항

- **Chrome/Chromium 브라우저**: Selenium WebDriver 사용 시 필요
- **ChromeDriver**: `webdriver-manager`가 자동으로 설치

#### 설치 방법

```bash
# 가상환경 활성화 (Scrapy와 동일한 환경 사용 가능)
source scrapy_env/bin/activate

# Selenium 의존성 설치
pip install -r selenium_project/requirements_selenium.txt
```

### 3. Kafka 프로젝트

#### Java/Maven 의존성

##### Kafka Demo (Producer/Consumer)

**파일**: `kafka_project/kafka_demo/pom.xml`

```xml
<dependencies>
    <dependency>
        <groupId>org.apache.kafka</groupId>
        <artifactId>kafka-clients</artifactId>
        <version>4.0.0</version>
    </dependency>
    <dependency>
        <groupId>org.apache.logging.log4j</groupId>
        <artifactId>log4j-slf4j2-impl</artifactId>
        <version>2.24.3</version>
    </dependency>
    <dependency>
        <groupId>com.fasterxml.jackson.core</groupId>
        <artifactId>jackson-databind</artifactId>
        <version>2.19.0</version>
    </dependency>
</dependencies>
```

##### Kafka Streams

**파일**: `kafka_project/kafka_streams/pom.xml`

```xml
<dependencies>
    <dependency>
        <groupId>org.apache.kafka</groupId>
        <artifactId>kafka-streams</artifactId>
        <version>4.0.0</version>
    </dependency>
</dependencies>
```

#### 시스템 요구사항

- **Java JDK**: 8 이상
- **Maven**: 3.x
- **Kafka 서버**: 4.0.0 (별도 설치 필요)

#### 설치 방법

##### Java 설치

```bash
# macOS (Homebrew)
brew install openjdk@8

# Ubuntu/Debian
sudo apt install default-jdk

# Windows
# Oracle JDK 또는 OpenJDK 다운로드 및 설치
```

##### Maven 설치

```bash
# macOS (Homebrew)
brew install maven

# Ubuntu/Debian
sudo apt install maven

# Windows
# Apache Maven 다운로드 및 설치
```

##### Kafka 서버 설치

```bash
# macOS (Homebrew)
brew install kafka

# Linux
wget https://dlcdn.apache.org/kafka/4.0.0/kafka_2.13-4.0.0.tgz
tar -xvf kafka_2.13-4.0.0.tgz
cd kafka_2.13-4.0.0

# Windows
# Kafka 바이너리 다운로드 및 압축 해제
```

##### Maven 프로젝트 빌드

```bash
# Kafka Demo
cd kafka_project/kafka_demo
mvn clean install

# Kafka Streams
cd kafka_project/kafka_streams
mvn clean install
```

## 📦 통합 설치 순서

### 1단계: 시스템 도구 설치

```bash
# Python 3 확인
python3 --version  # 3.8 이상 필요

# Java 확인
java -version  # JDK 8 이상 필요

# Maven 확인
mvn -version  # 3.x 필요
```

### 2단계: Python 가상환경 설정

```bash
# 가상환경 생성
python3 -m venv scrapy_env
source scrapy_env/bin/activate

# 모든 Python 의존성 설치
pip install -r setup/requirements.txt
pip install -r selenium_project/requirements_selenium.txt
```

### 3단계: Kafka 서버 설정

```bash
# Kafka 서버 설치 및 시작
# macOS
brew services start kafka

# Linux
# kafka_project/docs/cluster_setup_guide.md 참조
```

### 4단계: Maven 프로젝트 빌드

```bash
# Kafka Demo 빌드
cd kafka_project/kafka_demo
mvn clean install

# Kafka Streams 빌드
cd ../kafka_streams
mvn clean install
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

### Kafka 확인

```bash
# Kafka 서버 실행 확인
# macOS
brew services list | grep kafka

# Linux
ps aux | grep kafka
```

### 프로젝트별 테스트

```bash
# Scrapy 테스트
cd scrapy_project
scrapy list

# Selenium 테스트
cd selenium_project
python selenium_basics/webdriver_config.py

# Kafka 테스트
cd kafka_project
./scripts/test_kafka.sh
```

## 🚨 문제 해결

### Python 패키지 설치 오류

```bash
# pip 업그레이드
pip install --upgrade pip

# 특정 패키지 재설치
pip install --force-reinstall scrapy
```

### Java 버전 문제

```bash
# JAVA_HOME 설정 확인
echo $JAVA_HOME

# macOS에서 Java 버전 변경
export JAVA_HOME=$(/usr/libexec/java_home -v 1.8)
```

### Maven 빌드 오류

```bash
# Maven 캐시 정리
mvn clean

# 의존성 강제 업데이트
mvn clean install -U
```

### Kafka 서버 연결 오류

```bash
# Kafka 서버 실행 확인
# macOS
brew services start kafka

# 포트 확인
lsof -i :9092
```

## 📝 플랫폼별 설치 가이드

### macOS

- Python: `brew install python3`
- Java: `brew install openjdk@8`
- Maven: `brew install maven`
- Kafka: `brew install kafka`

### Ubuntu/Debian

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip
sudo apt install default-jdk maven
# Kafka는 수동 설치 필요
```

### Windows

- Python: [python.org](https://www.python.org/downloads/)
- Java: [Oracle JDK](https://www.oracle.com/java/technologies/downloads/) 또는 [OpenJDK](https://adoptium.net/)
- Maven: [Apache Maven](https://maven.apache.org/download.cgi)
- Kafka: [Apache Kafka](https://kafka.apache.org/downloads)

## 🔗 관련 문서

- [Scrapy 설치 가이드](docs/INSTALLATION.md)
- [Kafka 클러스터 설정](kafka_project/docs/cluster_setup_guide.md)
- [Windows Kafka 설정](kafka_project/docs/WINDOWS_SINGLE_MACHINE_SETUP.md)
- [통합 설치 스크립트](../setup/setup_all.sh)
