#!/bin/bash
# Kafka Producer 설정 테스트 스크립트
# 강의 슬라이드: Producer with custom properties

echo "=== Kafka Producer 설정 테스트 ==="
echo ""

# Bootstrap 서버 설정
BOOTSTRAP_SERVER="${BOOTSTRAP_SERVER:-localhost:9092}"

# Kafka 명령어 경로
KAFKA_CONSOLE_PRODUCER="${KAFKA_CONSOLE_PRODUCER:-/opt/homebrew/bin/kafka-console-producer}"
KAFKA_TOPICS="${KAFKA_TOPICS:-/opt/homebrew/bin/kafka-topics}"

# Producer 설정 파일 경로
PRODUCER_CONFIG="config/producer.properties"
KAFKA_HOME="${KAFKA_HOME:-/opt/homebrew/opt/kafka}"

# 색상 코드
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Producer 설정 파일 생성
echo -e "${BLUE}1. Producer 설정 파일 생성: $PRODUCER_CONFIG${NC}"

mkdir -p config

cat > $PRODUCER_CONFIG << 'EOF'
# Compression Type: gzip
compression.type=gzip

# Partitioner: Round Robin (기본값: sticky)
partitioner.class=org.apache.kafka.clients.producer.RoundRobinPartitioner

# Linger time: 100ms (메시지를 버퍼링하는 최대 시간)
linger.ms=100

# Acks: all (모든 replica가 메시지를 수신할 때까지 대기)
# 옵션: acks=0 (즉시 반환), acks=1 (leader만 확인), acks=all (모든 replica 확인)
acks=all
EOF

echo -e "${GREEN}✅ Producer 설정 파일 생성 완료${NC}"
echo ""
cat $PRODUCER_CONFIG

echo ""
echo -e "${BLUE}2. Topic 'test' 확인${NC}"
$KAFKA_TOPICS --describe --topic test --bootstrap-server $BOOTSTRAP_SERVER 2>&1 | head -10

echo ""
echo -e "${BLUE}3. Producer 실행 (커스텀 설정 사용)${NC}"
echo -e "${YELLOW}   설정 내용:${NC}"
echo -e "${YELLOW}   - compression.type: gzip${NC}"
echo -e "${YELLOW}   - partitioner.class: RoundRobinPartitioner (기본: sticky → round robin)${NC}"
echo -e "${YELLOW}   - linger.ms: 100${NC}"
echo -e "${YELLOW}   - acks: all${NC}"
echo ""

# macOS 환경에서는 절대 경로로 producer.properties를 지정해야 할 수 있음
if [ -f "$KAFKA_HOME/$PRODUCER_CONFIG" ]; then
    PRODUCER_CONFIG_PATH="$KAFKA_HOME/$PRODUCER_CONFIG"
elif [ -f "$PRODUCER_CONFIG" ]; then
    PRODUCER_CONFIG_PATH="$(pwd)/$PRODUCER_CONFIG"
else
    echo -e "${RED}⚠️  Producer 설정 파일을 찾을 수 없습니다.${NC}"
    echo -e "${YELLOW}   직접 다음 명령어로 실행하세요:${NC}"
    echo "$KAFKA_CONSOLE_PRODUCER --topic test \\"
    echo "  --producer.config $PRODUCER_CONFIG_PATH \\"
    echo "  --bootstrap-server $BOOTSTRAP_SERVER"
    exit 1
fi

echo -e "${YELLOW}테스트 메시지 전송 중... (Ctrl+C로 종료)${NC}"
echo ""

# 테스트 메시지 전송
(
  echo "Message 1 for partition test"
  echo "Message 2 for partition test"
  echo "Message 3 for partition test"
  echo "Message 4 for partition test"
  echo "Message 5 for partition test"
) | $KAFKA_CONSOLE_PRODUCER \
  --topic test \
  --producer.config $PRODUCER_CONFIG_PATH \
  --bootstrap-server $BOOTSTRAP_SERVER 2>&1

echo ""
echo -e "${GREEN}✅ Producer 테스트 완료!${NC}"
echo ""
echo -e "${YELLOW}참고 사항:${NC}"
echo "- Message distribution policy가 sticky (기본값) → round robin으로 변경되었습니다."
echo "- 모든 메시지가 round-robin 방식으로 파티션에 분산됩니다."
echo "- gzip 압축이 적용되어 메시지 크기가 감소합니다."

