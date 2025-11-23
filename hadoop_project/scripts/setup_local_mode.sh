#!/bin/bash

# Hadoop Local (Standalone) Mode Setup Script
# 강의 슬라이드 Page 10 기반

set -e  # 오류 발생 시 스크립트 중단

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 변수 설정
HADOOP_VERSION="3.4.1"
HADOOP_DIR="hadoop-${HADOOP_VERSION}"
HADOOP_TAR="${HADOOP_DIR}.tar.gz"
HADOOP_URL="https://dlcdn.apache.org/hadoop/common/hadoop-${HADOOP_VERSION}/${HADOOP_TAR}"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Hadoop Local (Standalone) Mode Setup${NC}"
echo -e "${GREEN}========================================${NC}"

# 1. Java 확인
echo -e "\n${YELLOW}[Step 1] Java 확인${NC}"
if ! command -v java &> /dev/null; then
    echo -e "${RED}Java가 설치되어 있지 않습니다. JDK v8 이상을 설치해주세요.${NC}"
    exit 1
fi

JAVA_VERSION=$(java -version 2>&1 | head -n 1)
echo -e "${GREEN}Java 버전: ${JAVA_VERSION}${NC}"

# 2. JAVA_HOME 확인
echo -e "\n${YELLOW}[Step 2] JAVA_HOME 확인${NC}"
if [ -z "$JAVA_HOME" ]; then
    echo -e "${YELLOW}JAVA_HOME이 설정되지 않았습니다.${NC}"

    # macOS에서 JAVA_HOME 찾기
    if [[ "$OSTYPE" == "darwin"* ]]; then
        JAVA_HOME=$(/usr/libexec/java_home 2>/dev/null || echo "")
        if [ -z "$JAVA_HOME" ]; then
            echo -e "${RED}JAVA_HOME을 수동으로 설정해주세요.${NC}"
            echo -e "${YELLOW}예시: export JAVA_HOME=/Library/Java/JavaVirtualMachines/jdk-11.0.12.jdk/Contents/Home${NC}"
            exit 1
        fi
    else
        # Linux에서 JAVA_HOME 찾기
        JAVA_HOME=$(readlink -f /usr/bin/java | sed "s:bin/java::")
        if [ -z "$JAVA_HOME" ]; then
            echo -e "${RED}JAVA_HOME을 수동으로 설정해주세요.${NC}"
            echo -e "${YELLOW}예시: export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-arm64${NC}"
            exit 1
        fi
    fi
    echo -e "${GREEN}JAVA_HOME: ${JAVA_HOME}${NC}"
else
    echo -e "${GREEN}JAVA_HOME: ${JAVA_HOME}${NC}"
fi

# 3. Hadoop 다운로드 확인
echo -e "\n${YELLOW}[Step 3] Hadoop 다운로드 확인${NC}"
if [ ! -f "$HADOOP_TAR" ]; then
    echo -e "${YELLOW}Hadoop 다운로드 중...${NC}"
    wget "$HADOOP_URL" || {
        echo -e "${RED}Hadoop 다운로드 실패${NC}"
        exit 1
    }
else
    echo -e "${GREEN}Hadoop 파일이 이미 존재합니다: ${HADOOP_TAR}${NC}"
fi

# 4. 압축 해제
echo -e "\n${YELLOW}[Step 4] Hadoop 압축 해제${NC}"
if [ ! -d "$HADOOP_DIR" ]; then
    tar -zxvf "$HADOOP_TAR"
    echo -e "${GREEN}압축 해제 완료${NC}"
else
    echo -e "${GREEN}Hadoop 디렉토리가 이미 존재합니다: ${HADOOP_DIR}${NC}"
fi

cd "$HADOOP_DIR"

# 5. JAVA_HOME 설정
echo -e "\n${YELLOW}[Step 5] hadoop-env.sh에 JAVA_HOME 설정${NC}"
HADOOP_ENV_FILE="./etc/hadoop/hadoop-env.sh"

if [[ "$OSTYPE" == "darwin"* ]]; then
    HADOOP_ENV_FILE="./etc/hadoop/hadoop-env.sh"
else
    HADOOP_ENV_FILE="./etc/hadoop/hadoop-env.sh"
fi

# JAVA_HOME 설정 확인 및 업데이트
if grep -q "^export JAVA_HOME=" "$HADOOP_ENV_FILE"; then
    # 기존 JAVA_HOME 주석 처리
    sed -i.bak "s|^export JAVA_HOME=.*|export JAVA_HOME=${JAVA_HOME}|" "$HADOOP_ENV_FILE"
    echo -e "${GREEN}JAVA_HOME 업데이트 완료${NC}"
else
    # JAVA_HOME 추가
    echo "export JAVA_HOME=${JAVA_HOME}" >> "$HADOOP_ENV_FILE"
    echo -e "${GREEN}JAVA_HOME 추가 완료${NC}"
fi

# 6. 버전 확인
echo -e "\n${YELLOW}[Step 6] Hadoop 버전 확인${NC}"
bin/hadoop version

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}Local Mode 설정 완료!${NC}"
echo -e "${GREEN}========================================${NC}"

# 7. 예제 실행 안내
echo -e "\n${YELLOW}예제 실행 방법:${NC}"
echo -e "${GREEN}# Wordcount 예제${NC}"
echo "mkdir input"
echo "echo 'Hello Hadoop Bye Bye This is a test for mapreduce' > input/file01.txt"
echo "echo 'Hello Hadoop Bye Hadoop This is another test for hadoop' > input/file02.txt"
echo "bin/hadoop jar share/hadoop/mapreduce/hadoop-mapreduce-examples-${HADOOP_VERSION}.jar wordcount input output"
echo "cat ./output/part-r-00000"
echo ""
echo -e "${GREEN}# Pi 예제${NC}"
echo "bin/hadoop jar share/hadoop/mapreduce/hadoop-mapreduce-examples-${HADOOP_VERSION}.jar pi 10 1000"

