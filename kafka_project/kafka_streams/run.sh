#!/bin/bash

# Kafka Streams 애플리케이션 실행 스크립트

echo "=== Kafka Streams SimplePipe 실행 ==="
echo ""

# Maven으로 컴파일
echo "1. 프로젝트 컴파일 중..."
mvn clean compile

if [ $? -ne 0 ]; then
    echo "컴파일 실패!"
    exit 1
fi

echo ""
echo "2. 애플리케이션 실행 중..."
echo ""

# 클래스패스 구성
CLASSPATH="target/classes"
for jar in $(mvn dependency:build-classpath -q -Dmdep.outputFile=/dev/stdout | tr ':' '\n'); do
    CLASSPATH="$CLASSPATH:$jar"
done

# 애플리케이션 실행
java -cp "$CLASSPATH" bigdata.kstream.demo.SimplePipe

