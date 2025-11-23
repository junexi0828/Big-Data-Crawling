#!/bin/bash
# Kafka Consumer Groups 테스트 스크립트
# 강의 슬라이드: Consumers and Consumer Groups

echo "=== Kafka Consumer Groups 테스트 ==="
echo ""

# Bootstrap 서버 설정
BOOTSTRAP_SERVER="${BOOTSTRAP_SERVER:-localhost:9092}"

# Kafka 명령어 경로
KAFKA_CONSOLE_CONSUMER="${KAFKA_CONSOLE_CONSUMER:-/opt/homebrew/bin/kafka-console-consumer}"
KAFKA_CONSUMER_GROUPS="${KAFKA_CONSUMER_GROUPS:-/opt/homebrew/bin/kafka-consumer-groups}"

# 색상 코드
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

TOPIC="${TOPIC:-test}"

echo -e "${BLUE}1. Consumer Groups 목록 조회${NC}"
$KAFKA_CONSUMER_GROUPS --list --bootstrap-server $BOOTSTRAP_SERVER

echo ""
echo -e "${BLUE}2. 기본 Consumer (그룹 없이)${NC}"
echo -e "${YELLOW}   - 이후 도착하는 메시지만 수신${NC}"
echo -e "${YELLOW}   명령어 예시:${NC}"
echo "$KAFKA_CONSOLE_CONSUMER --topic $TOPIC --bootstrap-server $BOOTSTRAP_SERVER"
echo ""
echo -e "${YELLOW}   - 처음부터 모든 메시지 수신${NC}"
echo -e "${YELLOW}   명령어 예시:${NC}"
echo "$KAFKA_CONSOLE_CONSUMER --topic $TOPIC --bootstrap-server $BOOTSTRAP_SERVER --from-beginning"

echo ""
echo -e "${BLUE}3. Consumer Group: 'graduates'${NC}"
echo -e "${YELLOW}   같은 그룹의 여러 consumer가 메시지를 독점적이고 완전하게 분산 수신${NC}"
echo -e "${YELLOW}   명령어 예시:${NC}"
echo "$KAFKA_CONSOLE_CONSUMER --topic $TOPIC --group graduates --bootstrap-server $BOOTSTRAP_SERVER"
echo ""
echo -e "${YELLOW}   여러 consumer가 같은 그룹을 사용하면 파티션별로 분산 수신됩니다.${NC}"

echo ""
echo -e "${BLUE}4. Consumer Group 상태 확인${NC}"
echo -e "${YELLOW}   'graduates' 그룹 상세 정보:${NC}"
$KAFKA_CONSUMER_GROUPS --describe \
  --group graduates \
  --bootstrap-server $BOOTSTRAP_SERVER 2>&1 | head -20

echo ""
echo -e "${YELLOW}   'undergraduates' 그룹 상세 정보:${NC}"
$KAFKA_CONSUMER_GROUPS --describe \
  --group undergraduates \
  --bootstrap-server $BOOTSTRAP_SERVER 2>&1 | head -20

echo ""
echo -e "${GREEN}✅ Consumer Groups 테스트 스크립트 완료!${NC}"
echo ""
echo -e "${YELLOW}실제 Consumer 실행 예시:${NC}"
echo ""
echo -e "${BLUE}# Consumer Group 'graduates' 사용 (이후 메시지 수신)${NC}"
echo "$KAFKA_CONSOLE_CONSUMER --topic $TOPIC --group graduates --bootstrap-server $BOOTSTRAP_SERVER"
echo ""
echo -e "${BLUE}# Consumer Group 'undergraduates' 사용 (처음부터 수신)${NC}"
echo "$KAFKA_CONSOLE_CONSUMER --topic $TOPIC --group undergraduates --bootstrap-server $BOOTSTRAP_SERVER --from-beginning"

