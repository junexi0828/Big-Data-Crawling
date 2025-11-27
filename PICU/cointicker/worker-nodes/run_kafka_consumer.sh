#!/bin/bash
# Kafka Consumer 서비스 실행 스크립트

set -e

# 색상 정의
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 프로젝트 루트 확인
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

echo "=========================================="
echo "Kafka Consumer 서비스 실행"
echo "=========================================="
echo ""

# 가상환경 확인
if [ -d "venv" ]; then
    echo -e "${GREEN}가상환경 활성화 중...${NC}"
    source venv/bin/activate
elif [ -d "../venv" ]; then
    echo -e "${GREEN}상위 디렉토리 가상환경 활성화 중...${NC}"
    source ../venv/bin/activate
else
    echo -e "${YELLOW}경고: 가상환경을 찾을 수 없습니다.${NC}"
fi

# Kafka Consumer 실행
echo -e "${GREEN}Kafka Consumer 서비스 시작...${NC}"
echo ""

python worker-nodes/kafka_consumer.py \
    --bootstrap-servers "${KAFKA_BOOTSTRAP_SERVERS:-localhost:9092}" \
    --topics "${KAFKA_TOPICS:-cointicker.raw.*}" \
    --group-id "${KAFKA_GROUP_ID:-cointicker-consumer}" \
    --hdfs-namenode "${HDFS_NAMENODE:-hdfs://localhost:9000}" \
    "$@"

