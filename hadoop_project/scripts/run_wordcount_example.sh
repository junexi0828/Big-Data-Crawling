#!/bin/bash

# Hadoop Wordcount 예제 실행 스크립트

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 변수 설정
HADOOP_VERSION="3.4.1"
INPUT_DIR="input"
OUTPUT_DIR="output"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Hadoop Wordcount 예제${NC}"
echo -e "${GREEN}========================================${NC}"

# HADOOP_HOME 확인 및 자동 설정
if [ -z "$HADOOP_HOME" ]; then
    # 스크립트 위치에서 hadoop 디렉토리 찾기
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

    # hadoop-3.4.1 디렉토리 찾기
    if [ -d "$PROJECT_DIR/hadoop-3.4.1" ]; then
        export HADOOP_HOME="$PROJECT_DIR/hadoop-3.4.1"
        echo -e "${YELLOW}HADOOP_HOME 자동 설정: $HADOOP_HOME${NC}"
    elif [ -d "$PROJECT_DIR/hadoop-3.4.1" ]; then
        export HADOOP_HOME="$PROJECT_DIR/hadoop-3.4.1"
        echo -e "${YELLOW}HADOOP_HOME 자동 설정: $HADOOP_HOME${NC}"
    else
        echo -e "${RED}HADOOP_HOME이 설정되지 않았고 hadoop 디렉토리를 찾을 수 없습니다.${NC}"
        echo -e "${YELLOW}환경 변수를 설정하거나 스크립트 내 경로를 수정하세요.${NC}"
        exit 1
    fi
fi

# 입력 파일 생성
echo -e "\n${YELLOW}[Step 1] 입력 파일 생성${NC}"
mkdir -p "$INPUT_DIR"

cat > "$INPUT_DIR/file01.txt" << EOF
Hello Hadoop Bye Bye This is a test for mapreduce
EOF

cat > "$INPUT_DIR/file02.txt" << EOF
Hello Hadoop Bye Hadoop This is another test for hadoop
EOF

echo -e "${GREEN}입력 파일 생성 완료${NC}"

# Local Mode 실행
if [ "$1" == "local" ]; then
    echo -e "\n${YELLOW}[Step 2] Local Mode로 Wordcount 실행${NC}"

    # 기존 output 삭제
    if [ -d "$OUTPUT_DIR" ]; then
        rm -rf "$OUTPUT_DIR"
    fi

    $HADOOP_HOME/bin/hadoop jar \
        $HADOOP_HOME/share/hadoop/mapreduce/hadoop-mapreduce-examples-${HADOOP_VERSION}.jar \
        wordcount "$INPUT_DIR" "$OUTPUT_DIR"

    echo -e "\n${GREEN}결과:${NC}"
    cat "$OUTPUT_DIR/part-r-00000"

# HDFS Mode 실행
else
    echo -e "\n${YELLOW}[Step 2] HDFS에 입력 파일 업로드${NC}"

    # HDFS 디렉토리 생성
    $HADOOP_HOME/bin/hdfs dfs -mkdir -p /user/$(whoami)/input

    # 파일 업로드
    $HADOOP_HOME/bin/hdfs dfs -put "$INPUT_DIR"/* /user/$(whoami)/input/

    echo -e "${GREEN}파일 업로드 완료${NC}"

    # 기존 output 삭제
    echo -e "\n${YELLOW}[Step 3] 기존 output 삭제${NC}"
    $HADOOP_HOME/bin/hdfs dfs -rm -r /user/$(whoami)/output 2>/dev/null || true

    # Wordcount 실행
    echo -e "\n${YELLOW}[Step 4] Wordcount 실행${NC}"
    $HADOOP_HOME/bin/hadoop jar \
        $HADOOP_HOME/share/hadoop/mapreduce/hadoop-mapreduce-examples-${HADOOP_VERSION}.jar \
        wordcount /user/$(whoami)/input /user/$(whoami)/output

    # 결과 확인
    echo -e "\n${GREEN}결과:${NC}"
    $HADOOP_HOME/bin/hdfs dfs -cat /user/$(whoami)/output/*

    # 결과를 로컬로 가져오기 (선택사항)
    echo -e "\n${YELLOW}[Step 5] 결과를 로컬로 가져오기${NC}"
    $HADOOP_HOME/bin/hdfs dfs -get /user/$(whoami)/output ./result
    echo -e "${GREEN}결과가 ./result 디렉토리에 저장되었습니다.${NC}"
fi

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}Wordcount 예제 완료!${NC}"
echo -e "${GREEN}========================================${NC}"

