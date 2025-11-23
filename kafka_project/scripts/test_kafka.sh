#!/bin/bash
# Kafka 테스트 스크립트

echo "=== Kafka Producer/Consumer 테스트 ==="

# 1. Producer로 메시지 전송
echo "📤 Producer로 메시지 전송 중..."
(echo "Hello Kafka"; echo "This is a test message"; echo "Big Data is awesome!") | \
  /opt/homebrew/bin/kafka-console-producer --topic bigdata --bootstrap-server localhost:9092

sleep 1

# 2. Consumer로 메시지 수신
echo ""
echo "📥 Consumer로 메시지 수신 중..."
/opt/homebrew/bin/kafka-console-consumer --topic bigdata --bootstrap-server localhost:9092 \
  --from-beginning --max-messages 3 --timeout-ms 5000 2>&1 | grep -v "ERROR\|WARN\|INFO" | head -5

echo ""
echo "✅ 테스트 완료"

