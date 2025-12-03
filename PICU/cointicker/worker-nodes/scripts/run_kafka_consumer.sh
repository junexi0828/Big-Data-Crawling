#!/bin/bash
# Kafka Consumer 서비스 실행 스크립트

set -e

# 색상 정의
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 프로젝트 루트 확인
# worker-nodes/scripts/run_kafka_consumer.sh -> worker-nodes/ -> cointicker/ -> PICU/
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
cd "$PROJECT_ROOT"

echo "=========================================="
echo "Kafka Consumer 서비스 실행"
echo "=========================================="
echo ""

# 가상환경 확인 (PICU 루트 venv 우선)
if [ -d "$PROJECT_ROOT/venv" ]; then
    echo -e "${GREEN}가상환경 활성화 중...${NC}"
    source "$PROJECT_ROOT/venv/bin/activate"
elif [ -d "$PROJECT_ROOT/cointicker/venv" ]; then
    echo -e "${GREEN}cointicker 가상환경 활성화 중...${NC}"
    source "$PROJECT_ROOT/cointicker/venv/bin/activate"
else
    echo -e "${YELLOW}경고: 가상환경을 찾을 수 없습니다.${NC}"
    echo -e "${YELLOW}PICU 루트에서 'bash scripts/start.sh'를 실행하여 설치하세요.${NC}"
fi

# 통합 환경 설정 스크립트 사용
if [ -f "$PROJECT_ROOT/scripts/setup_env.sh" ]; then
    source "$PROJECT_ROOT/scripts/setup_env.sh"
    echo -e "${GREEN}✅ 통합 환경 설정 완료${NC}"
else
    # Fallback: 하드코딩 경로 사용
    export PYTHONPATH="$PROJECT_ROOT/cointicker:$PYTHONPATH"
fi

# Kafka Consumer 실행
echo -e "${GREEN}Kafka Consumer 서비스 시작...${NC}"
echo ""

python "$PROJECT_ROOT/cointicker/worker-nodes/kafka/kafka_consumer.py" \
    --bootstrap-servers "${KAFKA_BOOTSTRAP_SERVERS:-localhost:9092}" \
    --topics "${KAFKA_TOPICS:-cointicker.raw.*}" \
    --group-id "${KAFKA_GROUP_ID:-cointicker-consumer}" \
    --hdfs-namenode "${HDFS_NAMENODE:-hdfs://localhost:9000}" \
    "$@"

