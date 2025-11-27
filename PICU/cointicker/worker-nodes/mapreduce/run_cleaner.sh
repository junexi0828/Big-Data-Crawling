#!/bin/bash
# MapReduce 데이터 정제 작업 실행 스크립트

# Hadoop 설정
HADOOP_HOME=${HADOOP_HOME:-/opt/hadoop}
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

# Python Mapper/Reducer 실행
cat ${LOCAL_INPUT}/*.json 2>/dev/null | \
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

