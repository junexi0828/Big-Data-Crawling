#!/bin/bash
# Kafka 클러스터 통합 테스트 스크립트
# 강의 슬라이드에 따른 모든 테스트를 순차적으로 실행

echo "=========================================="
echo "  Kafka 클러스터 통합 테스트"
echo "=========================================="
echo ""

# 색상 코드
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 스크립트 디렉토리
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Kafka 서버 확인
echo -e "${BLUE}📋 Kafka 서버 연결 확인 중...${NC}"
BOOTSTRAP_SERVER="${BOOTSTRAP_SERVER:-localhost:9092}"
KAFKA_TOPICS="${KAFKA_TOPICS:-/opt/homebrew/bin/kafka-topics}"

if ! $KAFKA_TOPICS --list --bootstrap-server $BOOTSTRAP_SERVER &>/dev/null; then
    echo -e "${RED}❌ Kafka 서버에 연결할 수 없습니다.${NC}"
    echo -e "${YELLOW}   Kafka 서버가 실행 중인지 확인하세요:${NC}"
    echo "   /opt/homebrew/opt/kafka/bin/kafka-server-start /opt/homebrew/etc/kafka/server.properties &"
    exit 1
fi

echo -e "${GREEN}✅ Kafka 서버 연결 성공${NC}"
echo ""

# 테스트 실행
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}1. Topic with Partitions 테스트${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
bash "$SCRIPT_DIR/test_cluster_topics.sh"
echo ""

read -p "계속하시겠습니까? (Enter 키를 누르세요)..."

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}2. Producer 설정 테스트${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
bash "$SCRIPT_DIR/test_producer_config.sh"
echo ""

read -p "계속하시겠습니까? (Enter 키를 누르세요)..."

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}3. Consumer Groups 테스트${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
bash "$SCRIPT_DIR/test_consumer_groups.sh"
echo ""

read -p "계속하시겠습니까? (Enter 키를 누르세요)..."

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}4. Offset Management 테스트${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
bash "$SCRIPT_DIR/test_offset_management.sh"
echo ""

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ 모든 클러스터 테스트 완료!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}📚 참고 문서:${NC}"
echo "   - cluster_setup_guide.md: 클러스터 설정 가이드"
echo "   - KAFKA_TEST_RESULTS.md: 기본 테스트 결과"
echo ""

