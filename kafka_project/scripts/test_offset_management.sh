#!/bin/bash
# Kafka Offset Management 테스트 스크립트
# 강의 슬라이드: Offset Management

echo "=== Kafka Offset Management 테스트 ==="
echo ""

# Bootstrap 서버 설정
BOOTSTRAP_SERVER="${BOOTSTRAP_SERVER:-localhost:9092}"

# Kafka 명령어 경로
KAFKA_CONSUMER_GROUPS="${KAFKA_CONSUMER_GROUPS:-/opt/homebrew/bin/kafka-consumer-groups}"
KAFKA_CONSOLE_CONSUMER="${KAFKA_CONSOLE_CONSUMER:-/opt/homebrew/bin/kafka-console-consumer}"

# 색상 코드
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

TOPIC="${TOPIC:-test}"
GROUP="${GROUP:-graduates}"

echo -e "${BLUE}1. Consumer Groups 목록${NC}"
$KAFKA_CONSUMER_GROUPS --list --bootstrap-server $BOOTSTRAP_SERVER

echo ""
echo -e "${BLUE}2. Consumer Group '$GROUP' 상세 정보 (Offset 확인)${NC}"
$KAFKA_CONSUMER_GROUPS --describe \
  --group $GROUP \
  --bootstrap-server $BOOTSTRAP_SERVER

echo ""
echo -e "${BLUE}3. Offset 리셋: 가장 처음으로 (--to-earliest)${NC}"
echo -e "${YELLOW}   명령어:${NC}"
echo "$KAFKA_CONSUMER_GROUPS --topic $TOPIC --group $GROUP --bootstrap-server $BOOTSTRAP_SERVER \\"
echo "  --reset-offsets --to-earliest --execute"
echo ""
read -p "실제로 실행하시겠습니까? (y/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    $KAFKA_CONSUMER_GROUPS --topic $TOPIC --group $GROUP \
      --bootstrap-server $BOOTSTRAP_SERVER \
      --reset-offsets --to-earliest --execute
    echo -e "${GREEN}✅ Offset이 earliest로 리셋되었습니다.${NC}"
else
    echo -e "${YELLOW}⚠️  실행을 건너뜁니다.${NC}"
fi

echo ""
echo -e "${BLUE}4. Offset 리셋: 현재 위치에서 2만큼 뒤로 (--shift-by -2)${NC}"
echo -e "${YELLOW}   명령어:${NC}"
echo "$KAFKA_CONSUMER_GROUPS --topic $TOPIC --group $GROUP --bootstrap-server $BOOTSTRAP_SERVER \\"
echo "  --reset-offsets --shift-by -2 --execute"
echo ""
read -p "실제로 실행하시겠습니까? (y/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    $KAFKA_CONSUMER_GROUPS --topic $TOPIC --group $GROUP \
      --bootstrap-server $BOOTSTRAP_SERVER \
      --reset-offsets --shift-by -2 --execute
    echo -e "${GREEN}✅ Offset이 2만큼 뒤로 이동되었습니다.${NC}"
else
    echo -e "${YELLOW}⚠️  실행을 건너뜁니다.${NC}"
fi

echo ""
echo -e "${BLUE}5. Consumer 실행 (리셋된 Offset부터 메시지 수신)${NC}"
echo -e "${YELLOW}   'undergraduates' 그룹으로 모든 파티션의 지연된 메시지 수신:${NC}"
echo "$KAFKA_CONSOLE_CONSUMER --topic $TOPIC --group undergraduates --bootstrap-server $BOOTSTRAP_SERVER"
echo ""
echo -e "${YELLOW}   실제로 실행하려면 위 명령어를 별도 터미널에서 실행하세요.${NC}"

echo ""
echo -e "${BLUE}6. 리셋 후 Consumer Group 상태 확인${NC}"
$KAFKA_CONSUMER_GROUPS --describe \
  --group $GROUP \
  --bootstrap-server $BOOTSTRAP_SERVER

echo ""
echo -e "${GREEN}✅ Offset Management 테스트 완료!${NC}"
echo ""
echo -e "${YELLOW}주요 Offset 리셋 옵션:${NC}"
echo "- --to-earliest: 가장 오래된 메시지로 리셋"
echo "- --to-latest: 가장 최신 메시지로 리셋"
echo "- --shift-by -N: N만큼 뒤로 이동 (이전 메시지)"
echo "- --shift-by +N: N만큼 앞으로 이동 (다음 메시지)"
echo "- --to-offset <offset>: 특정 오프셋으로 이동"
echo "- --to-datetime <datetime>: 특정 시간 이후 메시지로 이동"

