#!/bin/bash
# MapReduce 작업 실행 스크립트
# 사용법: ./run_mapreduce.sh [INPUT_PATH] [OUTPUT_PATH]

set -e

# 색상 코드
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 스크립트 디렉토리 확인
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Hadoop 설정 - hadoop_project 경로 자동 감지
if [ -z "$HADOOP_HOME" ]; then
    # 검색할 경로 목록 (우선순위 순)
    SEARCH_PATHS=(
        "$PROJECT_ROOT/../hadoop_project/hadoop-3.4.1"
        "$PROJECT_ROOT/../../hadoop_project/hadoop-3.4.1"
        "/opt/hadoop"
        "/usr/local/hadoop"
        "/home/bigdata/hadoop-3.4.1"
        "/usr/lib/hadoop"
        "/opt/homebrew/opt/hadoop"
        "/usr/local/opt/hadoop"
    )

    for path in "${SEARCH_PATHS[@]}"; do
        if [ -d "$path" ] && [ -f "$path/sbin/start-dfs.sh" ]; then
            HADOOP_HOME="$path"
            echo -e "${GREEN}✅ HADOOP_HOME 자동 감지: $HADOOP_HOME${NC}"
            break
        fi
    done

    # 자동 감지 실패 시 기본값
    if [ -z "$HADOOP_HOME" ]; then
        HADOOP_HOME="/opt/hadoop"
    fi
fi

HADOOP_STREAMING_JAR="${HADOOP_STREAMING_JAR:-$HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar}"

# 기본 경로 설정
INPUT_PATH="${1:-/user/cointicker/raw}"
OUTPUT_PATH="${2:-/user/cointicker/cleaned}"

# MapReduce 스크립트 경로
MAPPER_SCRIPT="$PROJECT_ROOT/worker-nodes/mapreduce/cleaner_mapper.py"
REDUCER_SCRIPT="$PROJECT_ROOT/worker-nodes/mapreduce/cleaner_reducer.py"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}MapReduce 작업 실행${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}설정:${NC}"
echo "  HADOOP_HOME: $HADOOP_HOME"
echo "  INPUT_PATH: $INPUT_PATH"
echo "  OUTPUT_PATH: $OUTPUT_PATH"
echo "  MAPPER: $MAPPER_SCRIPT"
echo "  REDUCER: $REDUCER_SCRIPT"
echo ""

# Hadoop 경로 확인
if [ ! -d "$HADOOP_HOME" ]; then
    echo -e "${RED}❌ HADOOP_HOME을 찾을 수 없습니다: $HADOOP_HOME${NC}"
    echo -e "${YELLOW}   환경 변수 HADOOP_HOME을 설정하거나 스크립트를 수정하세요.${NC}"
    exit 1
fi

# Hadoop Streaming JAR 확인
STREAMING_JAR_FILE=$(ls $HADOOP_STREAMING_JAR 2>/dev/null | head -1)
if [ -z "$STREAMING_JAR_FILE" ]; then
    echo -e "${RED}❌ Hadoop Streaming JAR를 찾을 수 없습니다: $HADOOP_STREAMING_JAR${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Hadoop Streaming JAR 발견: $STREAMING_JAR_FILE${NC}"
echo ""

# Mapper/Reducer 스크립트 확인
if [ ! -f "$MAPPER_SCRIPT" ]; then
    echo -e "${RED}❌ Mapper 스크립트를 찾을 수 없습니다: $MAPPER_SCRIPT${NC}"
    exit 1
fi

if [ ! -f "$REDUCER_SCRIPT" ]; then
    echo -e "${RED}❌ Reducer 스크립트를 찾을 수 없습니다: $REDUCER_SCRIPT${NC}"
    exit 1
fi

# 실행 권한 확인
chmod +x "$MAPPER_SCRIPT" "$REDUCER_SCRIPT"

# HDFS 입력 경로 확인
echo -e "${YELLOW}HDFS 입력 경로 확인 중...${NC}"
if ! $HADOOP_HOME/bin/hdfs dfs -test -e "$INPUT_PATH" 2>/dev/null; then
    echo -e "${RED}❌ HDFS 입력 경로가 존재하지 않습니다: $INPUT_PATH${NC}"
    echo -e "${YELLOW}   먼저 데이터를 HDFS에 업로드하세요.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ HDFS 입력 경로 확인: $INPUT_PATH${NC}"
echo ""

# 출력 디렉토리 삭제 (이미 존재하면)
echo -e "${YELLOW}기존 출력 디렉토리 삭제 중...${NC}"
if $HADOOP_HOME/bin/hdfs dfs -test -e "$OUTPUT_PATH" 2>/dev/null; then
    $HADOOP_HOME/bin/hdfs dfs -rm -r -f "$OUTPUT_PATH"
    echo -e "${GREEN}✅ 기존 출력 디렉토리 삭제 완료${NC}"
else
    echo -e "${YELLOW}   출력 디렉토리가 없습니다 (새로 생성됩니다)${NC}"
fi
echo ""

# MapReduce 실행
echo -e "${GREEN}MapReduce 작업 시작...${NC}"
echo ""

$HADOOP_HOME/bin/hadoop jar \
    "$STREAMING_JAR_FILE" \
    -mapper "python3 $MAPPER_SCRIPT" \
    -reducer "python3 $REDUCER_SCRIPT" \
    -input "$INPUT_PATH" \
    -output "$OUTPUT_PATH" \
    -file "$MAPPER_SCRIPT" \
    -file "$REDUCER_SCRIPT" \
    -cmdenv PYTHONUNBUFFERED=1

MAPREDUCE_EXIT_CODE=$?

if [ $MAPREDUCE_EXIT_CODE -eq 0 ]; then
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}✅ MapReduce 작업 완료!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "${YELLOW}출력 경로: $OUTPUT_PATH${NC}"
    echo ""
    echo -e "${YELLOW}결과 확인:${NC}"
    echo "  $HADOOP_HOME/bin/hdfs dfs -ls $OUTPUT_PATH"
    echo "  $HADOOP_HOME/bin/hdfs dfs -cat $OUTPUT_PATH/part-00000 | head -20"
    exit 0
else
    echo ""
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}❌ MapReduce 작업 실패 (종료 코드: $MAPREDUCE_EXIT_CODE)${NC}"
    echo -e "${RED}========================================${NC}"
    exit $MAPREDUCE_EXIT_CODE
fi

