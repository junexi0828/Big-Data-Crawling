# PICU 데이터베이스 구축 및 사용 현황

## 📊 현재 상태 요약

### ✅ 데이터베이스 구축 완료

1. **데이터베이스 모델 정의**

   - 위치: `backend/models/__init__.py`
   - 테이블:
     - `raw_news`: 뉴스 데이터
     - `market_trends`: 시장 트렌드
     - `fear_greed_index`: 공포·탐욕 지수
     - `sentiment_analysis`: 감성 분석 결과
     - `technical_indicators`: 기술적 지표
     - `crypto_insights`: 암호화폐 인사이트

2. **데이터베이스 초기화**

   - 자동 초기화: `backend/app.py`의 `startup_event()`에서 테이블 자동 생성
   - 수동 초기화: `backend/init_db.py` 스크립트로도 가능

3. **데이터베이스 연결 설정**
   - 위치: `backend/config.py`
   - 지원 DB: MariaDB, MySQL, PostgreSQL, SQLite
   - 환경 변수 또는 설정 파일로 관리

### ✅ 데이터베이스 사용 중

**API 엔드포인트에서 실제로 DB를 사용하고 있습니다:**

1. **Dashboard API** (`backend/api/dashboard.py`)

   ```python
   # 공포·탐욕 지수 조회
   fgi = db.query(FearGreedIndex).order_by(desc(FearGreedIndex.timestamp)).first()

   # 감성 분석 평균
   sentiment_avg = db.query(func.avg(SentimentAnalysis.sentiment_score))...

   # 거래량 Top 5
   top_volume = db.query(MarketTrends).order_by(desc(MarketTrends.volume_24h)).limit(5).all()
   ```

2. **News API** (`backend/api/news.py`)

   ```python
   # 최신 뉴스 목록
   news_list = db.query(RawNews).order_by(desc(RawNews.published_at)).limit(limit).all()

   # 감성 분석 결과
   sentiment = db.query(SentimentAnalysis).filter_by(news_id=news_id).first()
   ```

3. **Health Check** (`backend/app.py`)
   ```python
   # DB 연결 상태 확인
   db.execute(text("SELECT 1"))
   ```

---

## 🔄 데이터 저장 흐름

### 현재 구현된 흐름

```
1. Scrapy Spider (데이터 수집)
   ↓
2. ValidationPipeline (검증)
   ↓
3. DuplicatesPipeline (중복 제거)
   ↓
4. HDFSPipeline → HDFS (/raw/) ✅ 자동 실행
   ↓
5. MapReduce (정제 및 집계) → HDFS (/cleaned/)
   ↓
6. DataLoader → MariaDB ⚠️ 수동 실행 필요
```

### 저장 방식 비교

| 단계                | 저장 위치        | 형식      | 자동화  | 상태                      |
| ------------------- | ---------------- | --------- | ------- | ------------------------- |
| **원시 데이터**     | HDFS `/raw/`     | JSON 파일 | ✅ 자동 | 실행 중                   |
| **정제된 데이터**   | HDFS `/cleaned/` | JSON 파일 | ✅ 자동 | 실행 중                   |
| **구조화된 데이터** | MariaDB          | DB 레코드 | ⚠️ 수동 | 구축 완료, 수동 실행 필요 |

---

## 📝 DataLoader 사용 현황

### DataLoader 클래스

**위치**: `backend/services/data_loader.py`

**기능**:

- HDFS에서 정제된 데이터 다운로드
- JSON 파싱 및 타입별 분류
- MariaDB에 적재 (중복 체크 포함)

**사용 방법**:

```python
from backend.config import get_db
from backend.services.data_loader import DataLoader
from shared.hdfs_client import HDFSClient

db = next(get_db())
hdfs_client = HDFSClient()
data_loader = DataLoader(db, hdfs_client)
data_loader.load_from_hdfs()  # HDFS → MariaDB 적재
```

### 실행 스크립트

**위치**: `scripts/run_pipeline.py`

**전체 파이프라인 실행**:

```bash
python scripts/run_pipeline.py
```

**실행 단계**:

1. HDFS에서 데이터 로드 → MariaDB 적재
2. 감성 분석 실행
3. 기술적 지표 계산
4. 인사이트 생성

---

## ⚠️ 현재 문제점 및 개선 사항

### 문제점

1. **수동 실행 필요**

   - DataLoader가 자동으로 실행되지 않음
   - HDFS → MariaDB 적재를 수동으로 실행해야 함

2. **스케줄링 부재**
   - 정기적인 데이터 적재 스케줄이 없음
   - Cron job이나 스케줄러 설정 필요

### 개선 방안

1. **✅ GUI 자동화 추가 (완료)**

   - ControlTab에 "🔄 HDFS → DB 적재 실행" 버튼 추가
   - 버튼 클릭으로 `scripts/run_pipeline.py` 실행
   - 실행 상태 및 로그 실시간 표시

2. **자동화 스크립트 추가 (선택사항)**

   ```python
   # scripts/scheduled_loader.py
   import schedule
   from scripts.run_pipeline import run_full_pipeline

   # 매 30분마다 실행
   schedule.every(30).minutes.do(run_full_pipeline)
   ```

3. **Cron Job 설정 (선택사항)**

   ```bash
   # 매 30분마다 실행
   */30 * * * * cd /path/to/PICU/cointicker && python scripts/run_pipeline.py
   ```

4. **백엔드 API에 적재 엔드포인트 추가 (선택사항)**
   ```python
   @router.post("/api/data/load-from-hdfs")
   async def load_from_hdfs(db: Session = Depends(get_db)):
       """HDFS에서 데이터를 DB로 적재"""
       hdfs_client = HDFSClient()
       data_loader = DataLoader(db, hdfs_client)
       success = data_loader.load_from_hdfs()
       return {"success": success}
   ```

---

## ✅ 결론

### 현재 상태

- ✅ **데이터베이스 구축**: 완료
- ✅ **데이터베이스 사용**: API에서 활발히 사용 중
- ✅ **JSON 저장 (HDFS)**: 자동으로 실행 중
- ✅ **DB 적재 (HDFS → MariaDB)**: GUI 버튼으로 실행 가능

### 데이터 저장 현황

1. **HDFS에 JSON 저장**: ✅ 자동 실행 중

   - Scrapy → HDFSPipeline → HDFS (`/raw/`)
   - MapReduce 정제 → HDFS (`/cleaned/`)

2. **MariaDB에 구조화된 데이터 저장**: ⚠️ 수동 실행 필요
   - DataLoader를 통해 HDFS → MariaDB 적재
   - `scripts/run_pipeline.py` 실행 필요

### 권장 사항

1. **✅ GUI를 통한 실행 (권장)**: ControlTab에서 "🔄 HDFS → DB 적재 실행" 버튼 클릭
2. **명령줄 실행**: `python scripts/run_pipeline.py`로 수동 실행
3. **자동화 (선택사항)**: Cron job 또는 스케줄러 설정
4. **모니터링 추가**: 적재 상태 모니터링 및 알림 설정

---

## 📋 확인 방법

### 1. 데이터베이스 연결 확인

```bash
# Health Check API 호출
curl http://localhost:5000/health

# 응답 예시
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-11-27T14:30:00"
}
```

### 2. 데이터베이스 테이블 확인

```python
# Python에서 확인
from backend.config import get_db
from backend.models import RawNews, MarketTrends

db = next(get_db())
news_count = db.query(RawNews).count()
trends_count = db.query(MarketTrends).count()

print(f"뉴스 데이터: {news_count}개")
print(f"시장 트렌드: {trends_count}개")
```

### 3. API를 통한 데이터 확인

```bash
# 최신 뉴스 조회
curl http://localhost:5000/api/news/latest

# 대시보드 요약
curl http://localhost:5000/api/dashboard/summary
```

---

## 📚 관련 파일

- `backend/models/__init__.py`: 데이터베이스 모델 정의
- `backend/config.py`: 데이터베이스 연결 설정
- `backend/init_db.py`: 데이터베이스 초기화 스크립트
- `backend/services/data_loader.py`: HDFS → MariaDB 적재 서비스
- `scripts/run_pipeline.py`: 전체 파이프라인 실행 스크립트
- `backend/api/dashboard.py`: 대시보드 API (DB 사용)
- `backend/api/news.py`: 뉴스 API (DB 사용)
