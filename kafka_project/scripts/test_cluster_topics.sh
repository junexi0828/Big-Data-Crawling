#!/bin/bash
# Kafka 클러스터 Topic 테스트 스크립트
# 강의 슬라이드: "Topic with partitions"

echo "=== Kafka 클러스터 Topic 테스트 ==="
echo ""

# Bootstrap 서버 설정 (로컬 환경에서는 localhost 사용)
BOOTSTRAP_SERVER="${BOOTSTRAP_SERVER:-localhost:9092}"

# Kafka 명령어 경로 설정 (macOS brew 설치 기준)
KAFKA_TOPICS="${KAFKA_TOPICS:-/opt/homebrew/bin/kafka-topics}"
KAFKA_CONSOLE_PRODUCER="${KAFKA_CONSOLE_PRODUCER:-/opt/homebrew/bin/kafka-console-producer}"
KAFKA_CONSOLE_CONSUMER="${KAFKA_CONSOLE_CONSUMER:-/opt/homebrew/bin/kafka-console-consumer}"

# 색상 코드
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}1. Topic 'bigdata' 생성 (replication-factor 3, partitions 3)${NC}"
$KAFKA_TOPICS --create \
  --topic bigdata \
  --bootstrap-server $BOOTSTRAP_SERVER \
  --replication-factor 3 \
  --partitions 3 2>&1 | grep -v "^WARN\|^INFO" || echo "Topic이 이미 존재할 수 있습니다."

echo ""
echo -e "${BLUE}2. Topic 'bigdata' 상세 정보${NC}"
$KAFKA_TOPICS --describe \
  --topic bigdata \
  --bootstrap-server $BOOTSTRAP_SERVER

echo ""
echo -e "${BLUE}3. Topic 'datascience' 생성 (기본 설정)${NC}"
$KAFKA_TOPICS --create \
  --topic datascience \
  --bootstrap-server $BOOTSTRAP_SERVER 2>&1 | grep -v "^WARN\|^INFO" || echo "Topic이 이미 존재할 수 있습니다."

echo ""
echo -e "${BLUE}4. Topic 'datascience' 상세 정보${NC}"
$KAFKA_TOPICS --describe \
  --topic datascience \
  --bootstrap-server $BOOTSTRAP_SERVER

echo ""
echo -e "${BLUE}5. 모든 Topic 리스트${NC}"
$KAFKA_TOPICS --list --bootstrap-server $BOOTSTRAP_SERVER

echo ""
echo -e "${YELLOW}6. Topic 'test' 생성 (producer에서 자동 생성될 예정)${NC}"
echo -e "${YELLOW}   Producer로 메시지 전송하여 토픽 자동 생성 테스트${NC}"

# Producer로 메시지 전송 (백그라운드)
(
  sleep 1
  echo "test message 1"
  echo "test message 2"
  echo "test message 3"
) | $KAFKA_CONSOLE_PRODUCER --topic test --bootstrap-server $BOOTSTRAP_SERVER 2>&1 &
PRODUCER_PID=$!

sleep 2

echo ""
echo -e "${BLUE}7. Topic 'test' 상세 정보 (자동 생성 확인)${NC}"
$KAFKA_TOPICS --describe \
  --topic test \
  --bootstrap-server $BOOTSTRAP_SERVER 2>&1 | head -20

# Producer 프로세스 정리
wait $PRODUCER_PID 2>/dev/null

echo ""
echo -e "${GREEN}✅ Topic 테스트 완료!${NC}"
echo ""
echo -e "${YELLOW}참고: Topic 삭제는 다음 명령어로 가능합니다:${NC}"
echo "$KAFKA_TOPICS --delete --topic datascience --bootstrap-server $BOOTSTRAP_SERVER"
echo -e "${YELLOW}⚠️  주의: Windows 서버에서 토픽 삭제 시 서버 크래시 가능${NC}"

