#!/bin/bash

# Kafka 서버 시작 스크립트

echo "=== Kafka 서버 시작 ==="

# Kafka 서버가 이미 실행 중인지 확인
if lsof -i :9092 > /dev/null 2>&1; then
    echo "✅ Kafka 서버가 이미 실행 중입니다 (포트 9092)"
    exit 0
fi

# Kafka 서버 시작
echo "Kafka 서버를 시작합니다..."
/opt/homebrew/opt/kafka/bin/kafka-server-start /opt/homebrew/etc/kafka/server.properties > /tmp/kafka-server.log 2>&1 &
KAFKA_PID=$!

# 서버가 시작될 때까지 대기
echo "Kafka 서버가 시작될 때까지 대기 중..."
for i in {1..30}; do
    if lsof -i :9092 > /dev/null 2>&1; then
        echo "✅ Kafka 서버가 성공적으로 시작되었습니다 (PID: $KAFKA_PID)"
        echo "로그 파일: /tmp/kafka-server.log"
        exit 0
    fi
    sleep 1
done

echo "❌ Kafka 서버 시작 실패 (30초 타임아웃)"
echo "로그를 확인하세요: /tmp/kafka-server.log"
exit 1

