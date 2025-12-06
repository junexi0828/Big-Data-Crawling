# PICU 프로젝트 통합 가이드

PICU (암호화폐 관련 프로젝트)를 통합 클러스터 템플릿에 통합하는 방법을 설명합니다.

## 📋 프로젝트 개요

PICU 프로젝트는 암호화폐 데이터 수집, 분석, 시각화를 위한 통합 플랫폼입니다.

### 주요 구성 요소

1. **CoinTicker**: 암호화폐 티커 데이터 수집 및 대시보드
2. **Finance Expect**: 재무 시뮬레이션
3. **Investment Dashboard**: 투자 인사이트 대시보드

## 🔗 통합 아키텍처

```
┌─────────────────────────────────────────────────────────┐
│                    PICU 통합 파이프라인                    │
└─────────────────────────────────────────────────────────┘

[데이터 수집 계층]
    │
    ├─ Scrapy → 암호화폐 뉴스, 시장 데이터 크롤링
    ├─ Selenium → 동적 콘텐츠 (TradingView, Upbit 등)
    └─ CoinTicker → 실시간 티커 데이터
    │
    ▼
[메시징 계층]
    │
    └─ Kafka → 실시간 데이터 스트리밍
    │   ├─ Topic: crypto-news
    │   ├─ Topic: crypto-ticker
    │   └─ Topic: crypto-market
    │
    ▼
[분산 저장 계층]
    │
    └─ HDFS → 대용량 데이터 저장
    │   ├─ /raw/crypto/news/
    │   ├─ /raw/crypto/ticker/
    │   └─ /raw/crypto/market/
    │
    ▼
[분산 처리 계층]
    │
    └─ MapReduce → 데이터 정제 및 집계
    │   ├─ 중복 제거
    │   ├─ 시간대별 집계
    │   └─ 감성 분석
    │
    ▼
[분석 및 시각화 계층]
    │
    ├─ PICU Dashboard → 실시간 대시보드
    ├─ Finance Expect → 재무 시뮬레이션
    └─ Investment Dashboard → 투자 인사이트
```

## 🚀 통합 단계

### 1단계: 데이터 수집 설정

#### 1.1 Scrapy 스파이더 생성

`scrapy_project/tutorial/spiders/crypto_spider.py` 생성:

```python
import scrapy
from tutorial.items import CryptoItem

class CryptoSpider(scrapy.Spider):
    name = 'crypto'
    allowed_domains = ['coinness.com', 'coindesk.com']
    start_urls = ['https://coinness.com/news']

    def parse(self, response):
        # 암호화폐 뉴스 크롤링 로직
        item = CryptoItem()
        item['title'] = response.css('h1::text').get()
        item['content'] = response.css('.content::text').get()
        item['timestamp'] = response.css('.time::text').get()
        yield item
```

#### 1.2 Selenium 통합

`selenium_project/crypto/upbit_scraper.py` 생성:

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
import json

def scrape_upbit_ticker():
    driver = webdriver.Chrome()
    driver.get('https://upbit.com/exchange')

    # 티커 데이터 추출
    tickers = driver.find_elements(By.CLASS_NAME, 'ticker')
    data = []

    for ticker in tickers:
        data.append({
            'symbol': ticker.find_element(By.CLASS_NAME, 'symbol').text,
            'price': ticker.find_element(By.CLASS_NAME, 'price').text,
            'change': ticker.find_element(By.CLASS_NAME, 'change').text
        })

    driver.quit()
    return data
```

### 2단계: Kafka 통합

#### 2.1 Kafka Producer 설정

`PICU/kafka_producer.py` 생성:

```python
from kafka import KafkaProducer
import json
import time

class CryptoProducer:
    def __init__(self, bootstrap_servers='localhost:9092'):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

    def send_news(self, news_data):
        self.producer.send('crypto-news', news_data)

    def send_ticker(self, ticker_data):
        self.producer.send('crypto-ticker', ticker_data)

    def send_market(self, market_data):
        self.producer.send('crypto-market', market_data)
```

#### 2.2 Kafka Consumer 설정

`PICU/kafka_consumer.py` 생성:

```python
from kafka import KafkaConsumer
import json

class CryptoConsumer:
    def __init__(self, bootstrap_servers='localhost:9092'):
        self.consumer = KafkaConsumer(
            'crypto-news',
            'crypto-ticker',
            'crypto-market',
            bootstrap_servers=bootstrap_servers,
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )

    def consume(self):
        for message in self.consumer:
            topic = message.topic
            data = message.value
            # HDFS에 저장하거나 대시보드에 전송
            self.process_message(topic, data)

    def process_message(self, topic, data):
        if topic == 'crypto-news':
            # 뉴스 데이터 처리
            pass
        elif topic == 'crypto-ticker':
            # 티커 데이터 처리
            pass
        elif topic == 'crypto-market':
            # 시장 데이터 처리
            pass
```

### 3단계: HDFS 통합

#### 3.1 HDFS 저장 스크립트

`PICU/hdfs_storage.py` 생성:

```python
from hdfs import InsecureClient
import json
from datetime import datetime

class HDFSStorage:
    def __init__(self, hdfs_url='http://bigpie1:9870'):
        self.client = InsecureClient(hdfs_url, user='bigdata')

    def save_news(self, news_data):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        path = f'/raw/crypto/news/{timestamp}.json'
        self.client.write(path, json.dumps(news_data), encoding='utf-8')

    def save_ticker(self, ticker_data):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        path = f'/raw/crypto/ticker/{timestamp}.json'
        self.client.write(path, json.dumps(ticker_data), encoding='utf-8')

    def save_market(self, market_data):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        path = f'/raw/crypto/market/{timestamp}.json'
        self.client.write(path, json.dumps(market_data), encoding='utf-8')
```

### 4단계: MapReduce 통합

#### 4.1 MapReduce 작업 생성

`hadoop_project/examples/src/main/java/bigdata/hadoop/demo/CryptoAggregator.java` 생성:

```java
package bigdata.hadoop.demo;

import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.Job;
// ... 기타 import

public class CryptoAggregator {
    public static class CryptoMapper extends Mapper<...> {
        // 중복 제거, NULL 필터링
    }

    public static class CryptoReducer extends Reducer<...> {
        // 시간대별 집계
    }

    public static void main(String[] args) {
        // MapReduce 작업 설정
    }
}
```

### 5단계: 대시보드 연동

#### 5.1 실시간 데이터 API

`PICU/api_server.py` 생성:

```python
from flask import Flask, jsonify
from kafka import KafkaConsumer
import json

app = Flask(__name__)

@app.route('/api/crypto/ticker')
def get_ticker():
    # HDFS 또는 Kafka에서 최신 티커 데이터 조회
    return jsonify(ticker_data)

@app.route('/api/crypto/news')
def get_news():
    # 최신 뉴스 데이터 조회
    return jsonify(news_data)

if __name__ == '__main__':
    app.run(port=5000)
```

#### 5.2 대시보드 업데이트

`PICU/CoinTicker/dashboard.html` 수정:

```javascript
// API에서 실시간 데이터 가져오기
async function updateDashboard() {
  const response = await fetch("http://localhost:5000/api/crypto/ticker");
  const data = await response.json();

  // 차트 업데이트
  updateChart(data);
}

setInterval(updateDashboard, 5000); // 5초마다 업데이트
```

## 📦 의존성 추가

### requirements.txt에 추가

```txt
# PICU 프로젝트 의존성
hdfs3>=0.3.1
flask>=2.0.0
flask-cors>=3.0.0
```

## 🔧 실행 순서

### 1. 전체 환경 설정

```bash
# 통합 설치
./setup/setup_all.sh

# Hadoop 클러스터 시작
cd hadoop_project
./scripts/setup_single_node_with_yarn.sh
start-dfs.sh && start-yarn.sh

# Kafka 서버 시작
brew services start kafka  # macOS
# 또는
kafka-server-start.sh config/server.properties  # Linux
```

### 2. Kafka Topic 생성

```bash
kafka-topics.sh --create \
  --bootstrap-server localhost:9092 \
  --replication-factor 1 \
  --partitions 3 \
  --topic crypto-news

kafka-topics.sh --create \
  --bootstrap-server localhost:9092 \
  --replication-factor 1 \
  --partitions 3 \
  --topic crypto-ticker

kafka-topics.sh --create \
  --bootstrap-server localhost:9092 \
  --replication-factor 1 \
  --partitions 3 \
  --topic crypto-market
```

### 3. 데이터 수집 시작

```bash
# Scrapy 스파이더 실행
cd scrapy_project
scrapy crawl crypto

# Selenium 스크래퍼 실행
cd selenium_project
python crypto/upbit_scraper.py
```

### 4. Kafka Consumer 시작

```bash
cd PICU
python kafka_consumer.py
```

### 5. 대시보드 실행

```bash
# API 서버 시작
python api_server.py

# 대시보드 열기
open CoinTicker/dashboard.html
```

## 📊 모니터링

### Kafka 모니터링

```bash
# Topic 상태 확인
kafka-topics.sh --list --bootstrap-server localhost:9092

# Consumer Group 확인
kafka-consumer-groups.sh --bootstrap-server localhost:9092 --list
```

### HDFS 모니터링

```bash
# HDFS 파일 확인
hdfs dfs -ls /raw/crypto/

# 디스크 사용량 확인
hdfs dfs -du -h /raw/crypto/
```

### YARN 모니터링

```bash
# 실행 중인 작업 확인
yarn application -list

# 작업 로그 확인
yarn logs -applicationId <application_id>
```

## 🎯 다음 단계

1. **실시간 데이터 파이프라인 완성**

   - Scrapy → Kafka → HDFS → Dashboard

2. **배치 처리 파이프라인 추가**

   - HDFS → MapReduce → 정제된 데이터 → Dashboard

3. **감성 분석 추가**

   - 뉴스 데이터 감성 분석
   - 투자 인사이트 생성

4. **알림 시스템 구축**
   - 중요한 시장 변동 알림
   - 뉴스 알림

---

**통합 완료 후**: PICU 프로젝트는 통합 클러스터 템플릿의 모든 기능을 활용할 수 있습니다.
