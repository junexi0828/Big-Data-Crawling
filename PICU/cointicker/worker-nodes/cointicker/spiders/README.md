# Scrapy Spiders

## 구현된 Spider 목록

### ✅ 완료된 Spider (5개)

1. **upbit_trends.py** - Upbit 거래소 트렌드 데이터
   - 수집 데이터: 거래량 급증 코인, 가격 정보
   - 업데이트 주기: 5분
   - API 사용: Upbit Public API

2. **coinness.py** - 코인니스 암호화폐 뉴스
   - 수집 데이터: 뉴스 제목, 본문, 발행 시간, 키워드
   - 업데이트 주기: 10분
   - 크롤링 방식: HTML 파싱

3. **saveticker.py** - SaveTicker/Yahoo Finance 가격 정보
   - 수집 데이터: 코인 가격, 거래량, 변동률
   - 업데이트 주기: 5분
   - 데이터 소스: SaveTicker, Yahoo Finance API

4. **perplexity.py** - Perplexity AI 금융 분석
   - 수집 데이터: AI 기반 시장 분석 요약
   - 업데이트 주기: 1시간
   - 크롤링 방식: HTML 파싱 (Selenium 필요할 수 있음)

5. **cnn_fear_greed.py** - CNN 공포·탐욕 지수
   - 수집 데이터: 공포·탐욕 지수 (0-100), 분류
   - 업데이트 주기: 1일 1회
   - 데이터 소스: alternative.me API

## 실행 방법

```bash
# 개별 Spider 실행
cd worker-nodes
scrapy crawl upbit_trends
scrapy crawl coinness
scrapy crawl saveticker
scrapy crawl perplexity
scrapy crawl cnn_fear_greed

# JSON 출력
scrapy crawl upbit_trends -o output.json

# 로그 레벨 조정
scrapy crawl upbit_trends -L DEBUG
```

## 다음 단계

- [ ] Spider 테스트 및 검증
- [ ] HDFS Pipeline 연동 확인
- [ ] 스케줄링 설정 (Cron/Scrapyd)
- [ ] 에러 핸들링 개선

