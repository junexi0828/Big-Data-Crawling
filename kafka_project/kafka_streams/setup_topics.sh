#!/bin/bash

# Kafka 토픽 생성 스크립트

BOOTSTRAP_SERVER="localhost:9092"

echo "=== Kafka 토픽 생성 ==="

# Kafka 서버가 실행 중인지 확인
if ! lsof -i :9092 > /dev/null 2>&1; then
    echo "❌ Kafka 서버가 실행 중이 아닙니다."
    echo "먼저 ./start_kafka.sh를 실행하세요."
    exit 1
fi

# bigdata 토픽 생성
echo "1. bigdata 토픽 생성 중..."
kafka-topics --create --topic bigdata --bootstrap-server $BOOTSTRAP_SERVER --if-not-exists 2>/dev/null
if [ $? -eq 0 ]; then
    echo "   ✅ bigdata 토픽 생성 완료"
else
    echo "   ℹ️  bigdata 토픽이 이미 존재합니다"
fi

# analytics 토픽 생성
echo "2. analytics 토픽 생성 중..."
kafka-topics --create --topic analytics --bootstrap-server $BOOTSTRAP_SERVER --if-not-exists 2>/dev/null
if [ $? -eq 0 ]; then
    echo "   ✅ analytics 토픽 생성 완료"
else
    echo "   ℹ️  analytics 토픽이 이미 존재합니다"
fi

echo ""
echo "=== 생성된 토픽 목록 ==="
kafka-topics --list --bootstrap-server $BOOTSTRAP_SERVER

echo ""
echo "✅ 토픽 설정 완료!"

