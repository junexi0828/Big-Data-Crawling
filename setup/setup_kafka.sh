#!/bin/bash

# 📨 Kafka 프로젝트 설치 스크립트

set -e

PROJECT_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$PROJECT_ROOT"

echo "📨 Kafka 프로젝트 설치를 시작합니다..."

# 운영체제 감지
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -f /etc/os-release ]; then
            . /etc/os-release
            if [[ "$ID" == "ubuntu" ]] || [[ "$ID" == "debian" ]]; then
                echo "ubuntu"
            else
                echo "linux"
            fi
        else
            echo "linux"
        fi
    else
        echo "unknown"
    fi
}

OS_TYPE=$(detect_os)

# Java 확인 및 설치
if ! command -v java &> /dev/null; then
    echo "⚠️  Java가 설치되지 않았습니다."
    echo "   자동 설치를 시도합니다..."

    case $OS_TYPE in
        macos)
            if command -v brew &> /dev/null; then
                brew install openjdk@17 || brew install openjdk@8
            else
                echo "❌ Homebrew가 없어 Java를 자동 설치할 수 없습니다."
                exit 1
            fi
            ;;
        ubuntu)
            sudo apt update
            sudo apt install -y default-jdk
            ;;
        *)
            echo "❌ 자동 설치를 지원하지 않는 운영체제입니다."
            exit 1
            ;;
    esac
fi

# Maven 확인 및 설치
if ! command -v mvn &> /dev/null; then
    echo "⚠️  Maven이 설치되지 않았습니다."
    echo "   자동 설치를 시도합니다..."

    case $OS_TYPE in
        macos)
            if command -v brew &> /dev/null; then
                brew install maven
            else
                echo "❌ Homebrew가 없어 Maven을 자동 설치할 수 없습니다."
                exit 1
            fi
            ;;
        ubuntu)
            sudo apt update
            sudo apt install -y maven
            ;;
        *)
            echo "❌ 자동 설치를 지원하지 않는 운영체제입니다."
            exit 1
            ;;
    esac
fi

JAVA_VERSION=$(java -version 2>&1 | head -n 1 | cut -d'"' -f2)
MVN_VERSION=$(mvn -version | head -n 1 | cut -d' ' -f3)

echo "✅ Java: $JAVA_VERSION"
echo "✅ Maven: $MVN_VERSION"
echo ""

# Kafka Demo 빌드
if [ -f "kafka_project/kafka_demo/pom.xml" ]; then
    echo "📦 Kafka Demo 빌드 중..."
    cd kafka_project/kafka_demo
    mvn clean install -DskipTests
    echo "✅ Kafka Demo 빌드 완료"
    cd "$PROJECT_ROOT"
else
    echo "❌ kafka_project/kafka_demo/pom.xml 파일을 찾을 수 없습니다."
    exit 1
fi

# Kafka Streams 빌드
if [ -f "kafka_project/kafka_streams/pom.xml" ]; then
    echo "📦 Kafka Streams 빌드 중..."
    cd kafka_project/kafka_streams
    mvn clean install -DskipTests
    echo "✅ Kafka Streams 빌드 완료"
    cd "$PROJECT_ROOT"
else
    echo "❌ kafka_project/kafka_streams/pom.xml 파일을 찾을 수 없습니다."
    exit 1
fi

echo ""
echo "🎉 Kafka 프로젝트 빌드 완료!"
echo ""
echo "⚠️  참고: Kafka 서버는 별도로 설치 및 시작해야 합니다."
echo "   - macOS: brew install kafka && brew services start kafka"
echo "   - Linux: kafka_project/docs/cluster_setup_guide.md 참조"
echo ""
echo "다음 명령어로 테스트하세요:"
echo "  cd kafka_project && ./scripts/test_kafka.sh"

