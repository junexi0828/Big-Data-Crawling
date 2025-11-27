#!/bin/bash
# 프로세스 흐름 테스트 스크립트
# Spider -> Kafka -> HDFS -> Backend -> Frontend 순서로 실행 및 분석

set -e

# 색상 정의
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# 프로젝트 루트
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

echo "=========================================="
echo "프로세스 흐름 테스트 및 분석"
echo "=========================================="
echo ""

# 가상환경 활성화
if [ -d "venv" ]; then
    source venv/bin/activate
    echo -e "${GREEN}✅ 가상환경 활성화${NC}"
else
    echo -e "${RED}❌ 가상환경을 찾을 수 없습니다.${NC}"
    exit 1
fi

# 테스트 결과 저장
TEST_RESULTS_DIR="$PROJECT_ROOT/cointicker/tests/process_flow_results"
mkdir -p "$TEST_RESULTS_DIR"

echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}1단계: Spider (Scrapy) 테스트${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

cd "$PROJECT_ROOT/cointicker/worker-nodes"

# Spider 실행 테스트
echo -e "${YELLOW}Spider 실행 중...${NC}"
SPIDER_OUTPUT="$TEST_RESULTS_DIR/spider_output.log"

# macOS에서는 timeout 명령어가 없을 수 있으므로 gtimeout 또는 직접 실행
if command -v gtimeout &> /dev/null; then
    TIMEOUT_CMD="gtimeout"
elif command -v timeout &> /dev/null; then
    TIMEOUT_CMD="timeout"
else
    # timeout이 없으면 직접 실행 (Ctrl+C로 중단)
    TIMEOUT_CMD=""
fi

if [ -n "$TIMEOUT_CMD" ]; then
    $TIMEOUT_CMD 30 scrapy crawl upbit_trends -L INFO 2>&1 | tee "$SPIDER_OUTPUT" || true
else
    scrapy crawl upbit_trends -L INFO 2>&1 | head -100 | tee "$SPIDER_OUTPUT" || true
fi

if [ -f "$SPIDER_OUTPUT" ]; then
    ITEMS_COUNT=$(grep -c "item_scraped_count" "$SPIDER_OUTPUT" || echo "0")
    ERRORS_COUNT=$(grep -c "ERROR" "$SPIDER_OUTPUT" || echo "0")
    echo -e "${GREEN}✅ Spider 실행 완료${NC}"
    echo "  - 아이템 수집: $ITEMS_COUNT"
    echo "  - 에러 수: $ERRORS_COUNT"
else
    echo -e "${RED}❌ Spider 실행 실패${NC}"
fi

echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}2단계: Kafka Consumer 테스트${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

cd "$PROJECT_ROOT"

# Kafka Consumer 상태 확인
echo -e "${YELLOW}Kafka Consumer 상태 확인 중...${NC}"
KAFKA_OUTPUT="$TEST_RESULTS_DIR/kafka_status.log"

# Kafka 브로커 확인
if command -v kafka-topics.sh &> /dev/null; then
    kafka-topics.sh --list --bootstrap-server localhost:9092 2>&1 | tee "$KAFKA_OUTPUT" || echo "Kafka 브로커 연결 실패" | tee "$KAFKA_OUTPUT"
else
    echo "Kafka 명령어를 찾을 수 없습니다. Kafka가 설치되어 있는지 확인하세요." | tee "$KAFKA_OUTPUT"
fi

echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}3단계: HDFS 상태 확인${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

HDFS_OUTPUT="$TEST_RESULTS_DIR/hdfs_status.log"

# HDFS 상태 확인
if command -v hdfs &> /dev/null; then
    hdfs dfsadmin -report 2>&1 | tee "$HDFS_OUTPUT" || echo "HDFS 연결 실패" | tee "$HDFS_OUTPUT"
else
    echo "HDFS 명령어를 찾을 수 없습니다. Hadoop이 설치되어 있는지 확인하세요." | tee "$HDFS_OUTPUT"
fi

echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}4단계: Backend API 테스트${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

BACKEND_OUTPUT="$TEST_RESULTS_DIR/backend_status.log"

# Backend 서버가 실행 중인지 확인
if curl -s http://localhost:5000/health > "$BACKEND_OUTPUT" 2>&1; then
    echo -e "${GREEN}✅ Backend 서버 실행 중${NC}"
    cat "$BACKEND_OUTPUT"
else
    echo -e "${YELLOW}⚠️  Backend 서버가 실행 중이 아닙니다.${NC}"
    echo "  실행 방법: bash cointicker/backend/run_server.sh"
fi

echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}5단계: Frontend 서버 테스트${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

FRONTEND_OUTPUT="$TEST_RESULTS_DIR/frontend_status.log"

# Frontend 서버가 실행 중인지 확인
if curl -s http://localhost:3000 > "$FRONTEND_OUTPUT" 2>&1; then
    echo -e "${GREEN}✅ Frontend 서버 실행 중${NC}"
else
    echo -e "${YELLOW}⚠️  Frontend 서버가 실행 중이 아닙니다.${NC}"
    echo "  실행 방법: bash cointicker/frontend/run_dev.sh"
fi

echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}테스트 결과 요약${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "테스트 결과는 다음 디렉토리에 저장되었습니다:"
echo "  $TEST_RESULTS_DIR"
echo ""
echo "파일 목록:"
ls -lh "$TEST_RESULTS_DIR" | tail -n +2 | awk '{print "  - " $9 " (" $5 ")"}'

