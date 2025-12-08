#!/bin/bash
# MapReduce 데이터 정제 작업 실행 스크립트

# 프로젝트 루트 확인 (선택적, 현재 디렉토리 기준으로도 동작)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# worker-nodes/mapreduce/run_cleaner.sh -> worker-nodes/mapreduce/ -> worker-nodes/ -> cointicker/ -> PICU/
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
COINTICKER_ROOT="$PROJECT_ROOT/cointicker"

# 스크립트 디렉토리로 이동 (mapper/reducer 파일이 같은 디렉토리에 있음)
cd "$SCRIPT_DIR"

# Hadoop 설정 - hadoop_project 경로 자동 감지
if [ -z "$HADOOP_HOME" ]; then
    # 스크립트 위치에서 프로젝트 루트 찾기
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
    PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

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
            echo "✅ HADOOP_HOME 자동 감지: $HADOOP_HOME"
            break
        fi
    done

    # 자동 감지 실패 시 기본값
    if [ -z "$HADOOP_HOME" ]; then
        HADOOP_HOME="/opt/hadoop"
    fi
fi
HDFS_NAMENODE=${HDFS_NAMENODE:-hdfs://localhost:9000}

# 입력/출력 경로
INPUT_PATH="/raw"
OUTPUT_PATH="/cleaned/$(date +%Y%m%d)"
DATE=$(date +%Y%m%d)

echo "=========================================="
echo "MapReduce 데이터 정제 작업 시작"
echo "=========================================="
echo "입력 경로: ${HDFS_NAMENODE}${INPUT_PATH}"
echo "출력 경로: ${HDFS_NAMENODE}${OUTPUT_PATH}"
echo "날짜: ${DATE}"
echo "=========================================="

# HDFS에서 데이터 가져오기
echo "Step 1: HDFS에서 원시 데이터 다운로드..."
LOCAL_INPUT="./data/input_${DATE}"
mkdir -p ${LOCAL_INPUT}

${HADOOP_HOME}/bin/hdfs dfs -get ${INPUT_PATH}/*/${DATE}/* ${LOCAL_INPUT}/ 2>/dev/null || {
    echo "경고: HDFS에서 데이터를 가져올 수 없습니다. 로컬 파일을 사용합니다."
}

# MapReduce 작업 실행
echo "Step 2: MapReduce 작업 실행..."

# Python Mapper/Reducer 실행 - 각 파일을 JSON Lines 형식으로 변환
for file in ${LOCAL_INPUT}/*.json; do
    if [ -f "$file" ]; then
        # jq가 있으면 사용 (배열의 각 요소를 개별 줄로 출력)
        if command -v jq &> /dev/null; then
            # 배열인 경우 각 요소를 개별 줄로, 객체인 경우 그대로 출력
            jq -c 'if type == "array" then .[] else . end' "$file" 2>/dev/null
        else
            # Python으로 배열의 각 요소를 개별 줄로 출력
            python3 -c "
import json
import sys
try:
    with open('$file', 'r') as f:
        data = json.load(f)
        if isinstance(data, list):
            for item in data:
                print(json.dumps(item, ensure_ascii=False))
        else:
            print(json.dumps(data, ensure_ascii=False))
except Exception as e:
    sys.stderr.write(f'Error processing $file: {e}\n')
" 2>/dev/null
        fi
    fi
done | \
    python3 cleaner_mapper.py | \
    sort | \
    python3 cleaner_reducer.py > ./data/output_${DATE}.json

# 결과 확인
if [ -f "./data/output_${DATE}.json" ]; then
    echo "Step 3: 정제된 데이터를 HDFS에 업로드..."

    # HDFS 출력 디렉토리 생성
    ${HADOOP_HOME}/bin/hdfs dfs -mkdir -p ${OUTPUT_PATH}

    # 결과 업로드
    ${HADOOP_HOME}/bin/hdfs dfs -put ./data/output_${DATE}.json ${OUTPUT_PATH}/cleaned_${DATE}.json

    echo "=========================================="
    echo "작업 완료!"
    echo "출력 파일: ${HDFS_NAMENODE}${OUTPUT_PATH}/cleaned_${DATE}.json"
    echo "=========================================="
else
    echo "오류: MapReduce 작업 실패"
    exit 1
fi

