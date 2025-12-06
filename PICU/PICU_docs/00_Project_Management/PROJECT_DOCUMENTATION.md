# 라즈베리파이 빅데이터 처리 프로젝트 종합 문서

> **프로젝트명**: 라즈베리파이 기반 24/7 데이터 크롤링 및 빅데이터 처리 시스템
>
> **목적**: 라즈베리파이 클러스터를 활용한 분산 데이터 수집, 저장, 처리 파이프라인 구축
>
> **기간**: 3개월 (12주)
>
> **최종 업데이트**: 2025-11-27

---

## 📑 목차

1. [프로젝트 개요](#1-프로젝트-개요)
2. [시스템 아키텍처](#2-시스템-아키텍처)
3. [기술 스택](#3-기술-스택)
4. [데이터 파이프라인](#4-데이터-파이프라인)
5. [개발 전략](#5-개발-전략)
6. [구현 일정](#6-구현-일정)
7. [프로젝트 구성](#7-프로젝트-구성)
8. [완성도 체크리스트](#8-완성도-체크리스트)
9. [참고 자료](#9-참고-자료)

---

## 1. 프로젝트 개요

### 1.1 프로젝트 목표

**핵심 목표**
- 라즈베리파이 클러스터 환경에서 Hadoop 기반 분산 데이터 처리 시스템 구축
- Scrapy를 활용한 24/7 무중단 웹 크롤링 파이프라인 구현
- 수집된 데이터의 저장, 정제, 분석 자동화
- 실시간 모니터링 및 시각화 대시보드 제공

**학습 목표**
1. 빅데이터 처리 기술 실습 (Hadoop, MapReduce)
2. 분산 시스템 설계 및 구축 경험
3. 웹 크롤링 자동화 (Scrapy)
4. 데이터 파이프라인 설계 및 구현
5. 라즈베리파이 클러스터 운영

### 1.2 프로젝트 범위

**포함 사항**
- ✅ 라즈베리파이 4대 기반 Hadoop 클러스터 구축
- ✅ Scrapy 기반 웹 크롤링 시스템 (5개 이상 데이터 소스)
- ✅ HDFS 분산 파일 시스템을 통한 데이터 저장
- ✅ MapReduce를 이용한 데이터 정제
- ✅ MariaDB/PostgreSQL 기반 데이터 웨어하우스
- ✅ Flask/FastAPI 백엔드 API 서버
- ✅ React 기반 실시간 모니터링 대시보드
- ✅ 24/7 무중단 운영을 위한 자동화 및 복구 메커니즘

**제외 사항**
- ❌ 프로덕션 수준의 보안 강화 (기본 인증만 구현)
- ❌ 대규모 트래픽 처리 (교육용 목적)
- ❌ 클라우드 배포 (로컬 환경 중심)

### 1.3 예상 성과

**기술적 성과**
- 분산 데이터 처리 시스템 구축 경험
- 일일 500~2,500개 데이터 자동 수집
- 실시간 데이터 모니터링 대시보드
- 안정적인 24/7 운영 시스템

**학습 성과**
- 빅데이터 기술 스택 (Hadoop, HDFS, MapReduce) 실무 경험
- 웹 크롤링 및 ETL 파이프라인 구현 능력
- 분산 시스템 아키텍처 설계 역량
- 라즈베리파이 클러스터 운영 노하우

---

## 2. 시스템 아키텍처

### 2.1 전체 시스템 구조

본 프로젝트는 **2-Tier 아키텍처**를 채택하여 라즈베리파이의 리소스 제약을 극복하면서도 확장 가능한 시스템을 구현합니다.

```
┌─────────────────────────────────────────────────────────────────┐
│                 Tier 1: 라즈베리파이 클러스터                      │
│                 (Data Collection & Storage Layer)               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐     │
│  │         Master Node (라즈베리파이 #1)                   │     │
│  ├────────────────────────────────────────────────────────┤     │
│  │  • Hadoop NameNode        (HDFS 메타데이터 관리)          │     │
│  │  • YARN ResourceManager   (작업 스케줄링)                │     │
│  │  • Scrapyd Scheduler      (크롤러 실행 관리)              │     │
│  │  • MariaDB (선택)         (메타데이터 저장)               │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │ Worker #1    │  │ Worker #2    │  │ Worker #3    │           │
│  │(라즈베리파이 #2)│  │(라즈베리파이 #3) │  │(라즈베리파이 #4)│           │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤           │
│  │• DataNode    │  │• DataNode    │  │• DataNode    │           │
│  │• Scrapy      │  │• Scrapy      │  │• Scrapy      │           │
│  │• MapReduce   │  │• MapReduce   │  │• MapReduce   │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
│                                                                 │
│  Data Flow: 크롤링 → HDFS 저장 → MapReduce 정제                    │
│  Output: /cleaned/YYYYMMDD/*.json                               │
│                                                                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ SSH/REST API
                             │ hdfs dfs -get /cleaned/* ./data
                             │
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                 Tier 2: 외부 서버 (일반 PC/NAS)                   │
│              (Data Analysis & Dashboard Layer)                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Data Processing Engine                     │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │  1. HDFS Fetcher (SSH로 데이터 다운로드)                    │   │
│  │  2. Data Loader (JSON 파싱 및 DB 적재)                     │   │
│  │  3. Data Validation (중복 체크, NULL 필터링)               │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │            Database (MariaDB/PostgreSQL)                │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │  • raw_data             (원시 데이터)                      │   │
│  │  • processed_data       (정제된 데이터)                    │   │
│  │  • metadata             (메타데이터)                       │   │
│  │  • system_logs          (시스템 로그)                      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │            Web Application Server                       │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │  Backend: Flask/FastAPI                                 │   │
│  │  • REST API 제공                                         │   │
│  │  • 데이터 통계 및 집계                                     │   │
│  │                                                         │   │
│  │  Frontend: React                                        │   │
│  │  • 실시간 대시보드 (60초 주기 업데이트)                      │   │
│  │  • Chart.js 시각화                                       │   │
│  │  • 반응형 디자인                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ↓
                    ┌─────────────────┐
                    │   최종 사용자      │
                    │  (모니터링)        │
                    └─────────────────┘
```

### 2.2 아키텍처 설계 이유

**2-Tier 아키텍처 선택 근거**

1. **라즈베리파이 리소스 최적화**
   - 데이터 수집과 저장에만 집중 (CPU/메모리 부담 최소화)
   - 분산 처리를 통한 작업 분산
   - 24/7 저전력 운영 가능

2. **외부 서버 활용**
   - 고부하 작업 (DB 쿼리, 시각화) 분리
   - 확장성 확보 (필요시 서버 스펙 업그레이드)
   - 개발 환경 유연성

3. **장애 격리**
   - 크롤러 장애가 대시보드에 영향 없음
   - 대시보드 장애가 데이터 수집에 영향 없음
   - 각 계층 독립적 복구 가능

### 2.3 데이터 흐름

```
[데이터 수집]
라즈베리파이 Worker → Scrapy 크롤링 → HDFS 원시 데이터 저장
                                          ↓
[데이터 정제]
                         MapReduce 정제 작업 → HDFS 정제 데이터 저장
                                          ↓
[데이터 전송]
              SSH/SFTP를 통한 데이터 전송 → 외부 서버 로컬 저장
                                          ↓
[데이터 적재]
                           JSON 파싱 → DB 저장 (MariaDB/PostgreSQL)
                                          ↓
[데이터 제공]
                         Flask API 서버 → REST API 엔드포인트
                                          ↓
[데이터 시각화]
                          React 대시보드 → 실시간 차트 및 통계
```

---

## 3. 기술 스택

### 3.1 라즈베리파이 클러스터 (Tier 1)

| 역할 | 기술 | 버전 | 용도 |
|-----|------|------|------|
| **OS** | Ubuntu Server | 20.04 LTS | 경량 CLI 환경 |
| **분산 파일 시스템** | Hadoop HDFS | 3.2.1+ | 데이터 분산 저장 |
| **리소스 관리** | YARN | 3.2.1+ | 작업 스케줄링 |
| **데이터 처리** | MapReduce | 3.2.1+ | 분산 데이터 정제 |
| **웹 크롤링** | Scrapy | 2.11+ | 데이터 수집 |
| **스케줄링** | Cron + APScheduler | - | 정기 작업 실행 |
| **언어** | Python | 3.8+ | 크롤러 및 스크립트 |

### 3.2 외부 서버 (Tier 2)

| 역할 | 기술 | 버전 | 용도 |
|-----|------|------|------|
| **백엔드 프레임워크** | Flask | 3.0+ | REST API 서버 |
| **대안 백엔드** | FastAPI | 0.110+ | 고성능 API (선택) |
| **데이터베이스** | MariaDB | 10.11+ | 정제 데이터 저장 |
| **대안 DB** | PostgreSQL | 15+ | RDBMS (선택) |
| **ORM** | SQLAlchemy | 2.0+ | DB 추상화 |
| **프론트엔드** | React | 18+ | 대시보드 UI |
| **차트 라이브러리** | Chart.js | 4.4+ | 데이터 시각화 |
| **HTTP 클라이언트** | Axios | 1.6+ | API 통신 |

### 3.3 공통 도구

| 역할 | 기술 | 용도 |
|-----|------|------|
| **버전 관리** | Git | 소스 코드 관리 |
| **컨테이너 (선택)** | Docker | 개발 환경 통일 |
| **프로세스 관리** | systemd | 서비스 자동 시작 |
| **로그 관리** | logrotate | 로그 순환 |
| **모니터링** | psutil | 시스템 메트릭 |

### 3.4 기술 선택 이유

**Hadoop 선택 이유**
- ✅ 분산 저장 및 복제로 데이터 안정성 보장
- ✅ MapReduce를 통한 병렬 처리
- ✅ 검증된 안정성
- ✅ 교육적 가치 (빅데이터 실습)

**Scrapy 선택 이유**
- ✅ 안정적이고 검증된 크롤링 프레임워크
- ✅ 비동기 처리로 효율성 높음
- ✅ 미들웨어 및 파이프라인 확장 용이
- ✅ 로봇 배제 표준(robots.txt) 준수

**Flask vs FastAPI**
- Flask: 간단한 API, 학습 곡선 낮음, 안정성
- FastAPI: 자동 문서화, 비동기 지원, 타입 검증 (추천)

**MariaDB vs PostgreSQL**
- MariaDB: 경량, 라즈베리파이 호환, 빠른 쿼리
- PostgreSQL: 복잡한 쿼리, JSON 지원, 확장성 (추천)

---

## 4. 데이터 파이프라인

### 4.1 파이프라인 개요

전체 데이터 파이프라인은 **7단계**로 구성되며, 30분 주기로 자동 실행됩니다.

```
T+0분    크롤링 시작 (라즈베리파이 Worker)
         ↓
T+1분    HDFS 원시 데이터 저장
         ↓
T+2분    MapReduce 정제 시작
         ↓
T+4분    정제 완료 (/cleaned/ 디렉토리)
         ↓
T+5분    외부 서버 데이터 fetch (SSH)
         ↓
T+6분    DB 적재 (MariaDB/PostgreSQL)
         ↓
T+7분    API 서버 캐시 업데이트
         ↓
T+8분    대시보드 자동 새로고침
```

### 4.2 각 단계 상세

#### Phase 1: 데이터 수집 (라즈베리파이)

**Scrapy 크롤링**
```python
# 예시: 뉴스 크롤링 Spider
class NewsSpider(scrapy.Spider):
    name = "news_spider"
    start_urls = ["https://example.com/news"]

    def parse(self, response):
        for article in response.css('.article'):
            yield {
                'title': article.css('.title::text').get(),
                'url': article.css('a::attr(href)').get(),
                'timestamp': datetime.now().isoformat(),
                'source': 'example'
            }
```

**HDFS 저장 Pipeline**
```python
class HDFSPipeline:
    def close_spider(self, spider):
        # 로컬에 임시 저장
        with open(filename, 'w') as f:
            json.dump(self.items, f)

        # HDFS 업로드
        hdfs_path = f"/raw/{spider.name}/{timestamp}.json"
        subprocess.run(f"hdfs dfs -put {filename} {hdfs_path}", shell=True)
```

#### Phase 2: 데이터 정제 (MapReduce)

**Mapper: 중복 제거 및 필터링**
```python
def mapper(line):
    data = json.loads(line)

    # 필수 필드 검증
    if not data.get('timestamp') or not data.get('source'):
        return

    # 해시 생성 (중복 체크용)
    data_hash = hashlib.md5(data['url'].encode()).hexdigest()

    # Key: source_date, Value: data
    key = f"{data['source']}_{data['timestamp'][:10]}"
    print(f"{key}\t{json.dumps({'hash': data_hash, 'data': data})}")
```

**Reducer: 시간대별 집계**
```python
def reducer():
    current_key = None
    data_bucket = []
    seen_hashes = set()

    for line in sys.stdin:
        key, value = line.strip().split('\t', 1)
        item = json.loads(value)

        # 중복 체크
        if item['hash'] not in seen_hashes:
            seen_hashes.add(item['hash'])
            data_bucket.append(item['data'])

    # 최종 출력
    print(json.dumps({'data': data_bucket, 'count': len(data_bucket)}))
```

#### Phase 3: 데이터 전송 (라즈베리파이 → 외부 서버)

**옵션 1: SSH/SCP**
```bash
#!/bin/bash
# 정제된 데이터 전송
scp -r /hdfs/cleaned/$(date +%Y%m%d) server:/import/
```

**옵션 2: REST API**
```python
import requests

data = load_from_hdfs('/cleaned/20251127/data.json')
requests.post('http://server:5000/api/ingest', json=data)
```

#### Phase 4: 데이터 적재 (외부 서버)

**Flask 백엔드**
```python
@app.route('/api/ingest', methods=['POST'])
def ingest_data():
    data = request.json

    # 검증
    if not validate_schema(data):
        return {"error": "Invalid schema"}, 400

    # DB 저장
    for item in data:
        record = RawData(
            source=item['source'],
            title=item['title'],
            url=item['url'],
            timestamp=item['timestamp']
        )
        db.session.add(record)

    db.session.commit()
    return {"status": "success", "count": len(data)}
```

#### Phase 5: API 제공

**REST API 엔드포인트**
```python
# 통계 조회
@app.route('/api/stats')
def get_stats():
    return {
        'total_records': db.session.query(RawData).count(),
        'sources': db.session.query(RawData.source).distinct().count(),
        'latest_timestamp': db.session.query(func.max(RawData.timestamp)).scalar()
    }

# 최신 데이터 조회
@app.route('/api/recent')
def get_recent():
    records = db.session.query(RawData)\
        .order_by(RawData.timestamp.desc())\
        .limit(50)\
        .all()
    return [r.to_dict() for r in records]
```

#### Phase 6: 대시보드 시각화

**React 컴포넌트**
```jsx
function Dashboard() {
  const [stats, setStats] = useState({});

  useEffect(() => {
    // 60초마다 자동 새로고침
    const interval = setInterval(() => {
      fetch('/api/stats')
        .then(res => res.json())
        .then(data => setStats(data));
    }, 60000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div>
      <h1>데이터 수집 대시보드</h1>
      <StatCard title="총 레코드" value={stats.total_records} />
      <Chart data={stats} />
    </div>
  );
}
```

### 4.3 파이프라인 자동화

**Cron 스케줄**
```bash
# 30분마다 크롤링 실행
*/30 * * * * /opt/scrapy/run_crawlers.sh

# 매일 00:00에 오래된 데이터 정리
0 0 * * * /opt/scripts/cleanup_old_data.sh

# 5분마다 시스템 메트릭 수집
*/5 * * * * python3 /opt/scripts/collect_metrics.py
```

**systemd 서비스**
```ini
[Unit]
Description=Flask API Server
After=network.target

[Service]
Type=simple
User=bigdata
WorkingDirectory=/opt/api-server
ExecStart=/usr/bin/python3 app.py
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
```

---

## 5. 개발 전략

### 5.1 설계 원칙

1. **관심사 분리 (Separation of Concerns)**
   - 라즈베리파이: 데이터 수집 및 저장
   - 외부 서버: 데이터 분석 및 시각화
   - 각 계층 독립적 개발 및 테스트 가능

2. **단계적 개발 (Incremental Development)**
   - Phase 1: 라즈베리파이 클러스터 구축
   - Phase 2: 크롤링 파이프라인 구현
   - Phase 3: 외부 서버 백엔드 개발
   - Phase 4: 프론트엔드 대시보드 구현

3. **테스트 주도 (Test-Driven)**
   - 각 단계마다 검증 및 테스트
   - 단위 테스트, 통합 테스트 작성
   - 로그 및 모니터링 체계 구축

4. **확장성 고려 (Scalability)**
   - 새로운 데이터 소스 추가 용이
   - Worker 노드 추가 가능
   - 모듈화된 코드 구조

### 5.2 개발 우선순위

**Phase 1: 인프라 구축 (Week 1-2)**
1. 라즈베리파이 Ubuntu 설치 및 네트워크 설정
2. Hadoop 클러스터 구성 (NameNode, DataNode)
3. HDFS 테스트 (파일 업로드/다운로드)
4. SSH 키 설정 및 원격 접속

**Phase 2: 데이터 수집 (Week 3-4)**
1. Scrapy 프로젝트 초기화
2. 첫 번째 Spider 구현 및 테스트
3. HDFS Pipeline 연동
4. Cron 스케줄 설정

**Phase 3: 데이터 정제 (Week 5-6)**
1. MapReduce Mapper 작성
2. MapReduce Reducer 작성
3. 정제 파이프라인 테스트
4. 성능 최적화

**Phase 4: 백엔드 개발 (Week 7-8)**
1. Flask 프로젝트 초기화
2. 데이터베이스 스키마 설계
3. REST API 엔드포인트 구현
4. 데이터 적재 로직 구현

**Phase 5: 프론트엔드 개발 (Week 9-10)**
1. React 프로젝트 초기화
2. 대시보드 레이아웃 설계
3. API 연동 및 데이터 시각화
4. 반응형 디자인 적용

**Phase 6: 통합 및 테스트 (Week 11-12)**
1. 전체 파이프라인 통합 테스트
2. 성능 최적화
3. 문서화
4. 발표 준비

### 5.3 위험 관리

| 위험 요소 | 영향도 | 대응 방안 |
|----------|--------|----------|
| **SD카드 고장** | 높음 | tmpfs 활용, 정기 백업, 백업 SD카드 준비 |
| **네트워크 장애** | 높음 | 로컬 큐잉, 자동 재시도, 오프라인 모드 |
| **크롤링 차단** | 중간 | User-Agent 회전, Rate Limiting, Proxy 사용 |
| **메모리 부족** | 중간 | 배치 크기 조정, 스왑 설정, 메모리 모니터링 |
| **디스크 풀** | 중간 | 로그 순환, 오래된 데이터 삭제, 모니터링 |

---

## 6. 구현 일정

### 6.1 전체 타임라인 (12주)

```
Week 1-2: 라즈베리파이 클러스터 구축
├─ Week 1: 하드웨어 준비 및 OS 설치
│  ├─ Day 1-2: Ubuntu Server 20.04 설치 (4대)
│  ├─ Day 3-4: 네트워크 구성 (SSH, 고정 IP)
│  └─ Day 5-7: 기본 설정 (사용자, 방화벽, 업데이트)
│
└─ Week 2: Hadoop 클러스터 구성
   ├─ Day 1-3: Hadoop 설치 및 설정
   ├─ Day 4-5: HDFS 테스트
   └─ Day 6-7: YARN 및 MapReduce 테스트

Week 3-4: Scrapy 크롤링 파이프라인
├─ Week 3: Scrapy 기본 구현
│  ├─ Day 1-2: Scrapy 프로젝트 초기화
│  ├─ Day 3-5: 첫 번째 Spider 구현 (뉴스 크롤링)
│  └─ Day 6-7: Item Pipeline 및 HDFS 연동
│
└─ Week 4: 크롤러 확장 및 자동화
   ├─ Day 1-3: 추가 Spider 구현 (3-4개)
   ├─ Day 4-5: Cron 스케줄 설정
   └─ Day 6-7: 에러 핸들링 및 로그

Week 5-6: MapReduce 데이터 정제
├─ Week 5: MapReduce 구현
│  ├─ Day 1-3: Mapper 및 Reducer 작성
│  ├─ Day 4-5: 테스트 및 디버깅
│  └─ Day 6-7: 성능 최적화
│
└─ Week 6: 데이터 전송 메커니즘
   ├─ Day 1-3: SSH/SFTP 스크립트 작성
   ├─ Day 4-5: REST API 전송 구현
   └─ Day 6-7: 통합 테스트

Week 7-8: 백엔드 개발
├─ Week 7: Flask API 서버
│  ├─ Day 1-2: Flask 프로젝트 초기화
│  ├─ Day 3-4: 데이터베이스 스키마 설계
│  └─ Day 5-7: REST API 엔드포인트 구현
│
└─ Week 8: 데이터 처리 로직
   ├─ Day 1-3: 데이터 적재 로직
   ├─ Day 4-5: 검증 및 필터링
   └─ Day 6-7: API 테스트

Week 9-10: 프론트엔드 개발
├─ Week 9: React 대시보드 기본
│  ├─ Day 1-2: React 프로젝트 초기화
│  ├─ Day 3-5: 컴포넌트 개발
│  └─ Day 6-7: API 연동
│
└─ Week 10: 시각화 및 UI/UX
   ├─ Day 1-3: Chart.js 차트 구현
   ├─ Day 4-5: 반응형 디자인
   └─ Day 6-7: 최종 디자인 완성

Week 11-12: 통합 및 마무리
├─ Week 11: 통합 테스트 및 최적화
│  ├─ Day 1-3: 전체 파이프라인 통합 테스트
│  ├─ Day 4-5: 성능 최적화
│  └─ Day 6-7: 버그 수정
│
└─ Week 12: 문서화 및 발표 준비
   ├─ Day 1-3: 사용자 가이드 작성
   ├─ Day 4-5: 발표 자료 준비
   └─ Day 6-7: 최종 점검 및 데모
```

### 6.2 마일스톤

| 주차 | 마일스톤 | 검증 기준 |
|-----|---------|----------|
| Week 2 | Hadoop 클러스터 구축 완료 | HDFS 파일 업로드/다운로드 성공 |
| Week 4 | 크롤링 파이프라인 완성 | 5개 Spider가 30분마다 자동 실행 |
| Week 6 | 데이터 정제 완료 | MapReduce로 중복 제거 및 집계 |
| Week 8 | 백엔드 API 서버 완성 | REST API 10개 엔드포인트 구현 |
| Week 10 | 프론트엔드 대시보드 완성 | 실시간 데이터 시각화 |
| Week 12 | 프로젝트 완료 | 24/7 안정적 운영 및 발표 |

---

## 7. 프로젝트 구성

### 7.1 디렉토리 구조

```
/Users/juns/code/personal/notion/pknu_workspace/bigdata/
├── README.md                           # 프로젝트 개요
├── PROJECT_DOCUMENTATION.md            # 본 문서
├── PROJECT_COMPLETION_CHECKLIST.md    # 완성도 체크리스트
├── INTEGRATED_CLUSTER_CHECKLIST.md    # 클러스터 통합 체크리스트
│
├── hadoop_project/                     # Hadoop 관련
│   ├── config/                         # Hadoop 설정 파일
│   ├── scripts/                        # 운영 스크립트
│   └── docs/                           # Hadoop 문서
│
├── scrapy_project/                     # Scrapy 크롤링
│   ├── tutorial/                       # Scrapy 프로젝트
│   │   ├── spiders/                    # Spider 모음
│   │   ├── pipelines.py                # Pipeline (HDFS 연동)
│   │   └── settings.py                 # Scrapy 설정
│   └── outputs/                        # 크롤링 결과
│
├── kafka_project/                      # Kafka (확장)
│   ├── kafka_demo/                     # Producer/Consumer
│   └── docs/                           # Kafka 문서
│
├── selenium_project/                   # Selenium (확장)
│   └── demos/                          # 동적 크롤링
│
├── PICU/                               # 백엔드 API 서버
│   ├── app.py                          # Flask/FastAPI 메인
│   ├── models.py                       # DB 모델
│   ├── routes.py                       # API 라우트
│   └── config.py                       # 설정
│
├── dashboard/                          # React 프론트엔드 (신규)
│   ├── src/
│   │   ├── components/                 # React 컴포넌트
│   │   ├── services/                   # API 통신
│   │   └── App.js
│   └── public/
│
├── scripts/                            # 유틸리티 스크립트
│   ├── setup_cluster.sh                # 클러스터 초기 설정
│   ├── run_crawlers.sh                 # 크롤러 실행
│   ├── cleanup_old_data.sh             # 데이터 정리
│   └── collect_metrics.py              # 메트릭 수집
│
└── docs/                               # 문서
    ├── INSTALLATION.md                 # 설치 가이드
    ├── API_DOCUMENTATION.md            # API 문서
    └── TROUBLESHOOTING.md              # 문제 해결
```

### 7.2 기존 프로젝트 통합

본 프로젝트는 기존에 학습한 Scrapy, Selenium, Kafka 프로젝트를 기반으로 구축됩니다.

**통합 포인트**
1. **Scrapy 프로젝트**: 크롤링 엔진의 핵심
2. **Hadoop 프로젝트**: 분산 저장 및 처리
3. **Kafka 프로젝트**: (선택) 실시간 스트리밍 확장
4. **Selenium 프로젝트**: (선택) 동적 웹사이트 크롤링

---

## 8. 완성도 체크리스트

### 8.1 필수 구현 사항

**인프라 (Tier 1 - 라즈베리파이)**
- [ ] 라즈베리파이 4대 Ubuntu 설치 및 네트워크 구성
- [ ] Hadoop 클러스터 구축 (1 Master + 3 Workers)
- [ ] HDFS 분산 파일 시스템 동작 확인
- [ ] YARN 및 MapReduce 환경 구성

**데이터 수집**
- [ ] Scrapy 프로젝트 초기화
- [ ] 5개 이상 Spider 구현
- [ ] HDFS Pipeline 연동
- [ ] Cron 스케줄 자동화 (30분 주기)
- [ ] 에러 핸들링 및 재시도 로직

**데이터 정제**
- [ ] MapReduce Mapper 구현 (중복 제거, 필터링)
- [ ] MapReduce Reducer 구현 (집계)
- [ ] 정제 데이터 검증

**데이터 전송 (Tier 1 → Tier 2)**
- [ ] SSH/SFTP 스크립트 작성
- [ ] 또는 REST API 전송 구현
- [ ] 전송 실패 시 재시도 로직

**백엔드 (Tier 2 - 외부 서버)**
- [ ] Flask/FastAPI 프로젝트 초기화
- [ ] 데이터베이스 스키마 설계 및 구현
- [ ] REST API 10개 이상 엔드포인트 구현
- [ ] 데이터 적재 및 검증 로직
- [ ] CORS 설정 (프론트엔드 연동)

**프론트엔드**
- [ ] React 프로젝트 초기화
- [ ] 대시보드 레이아웃 구현
- [ ] Chart.js 데이터 시각화
- [ ] 실시간 업데이트 (60초 주기)
- [ ] 반응형 디자인

**운영 및 모니터링**
- [ ] systemd 서비스 등록
- [ ] 로그 순환 설정
- [ ] 시스템 메트릭 수집
- [ ] 장애 알림 시스템 (선택)

### 8.2 선택 구현 사항

**고급 기능**
- [ ] Kafka를 통한 실시간 스트리밍
- [ ] Selenium 동적 크롤링 통합
- [ ] NLP 감성 분석 (FinBERT)
- [ ] 기술적 지표 계산 (RSI, MACD 등)
- [ ] 알림 시스템 (Email, Slack)

**최적화**
- [ ] Redis 캐싱
- [ ] WebSocket 실시간 통신
- [ ] Docker 컨테이너화
- [ ] CI/CD 파이프라인

---

## 9. 참고 자료

### 9.1 프로젝트 문서

- [기존 README.md](/Users/juns/code/personal/notion/pknu_workspace/bigdata/README.md)
- [프로젝트 완성도 체크리스트](/Users/juns/code/personal/notion/pknu_workspace/bigdata/PROJECT_COMPLETION_CHECKLIST.md)
- [통합 클러스터 체크리스트](/Users/juns/code/personal/notion/pknu_workspace/bigdata/INTEGRATED_CLUSTER_CHECKLIST.md)

### 9.2 노션 페이지

- [라즈베리파이 빅데이터처리](https://www.notion.so/2b8edd4b98c5801bafaceb9f20b1c5f3)
- [코인티커 프로젝트 종합 설명서](https://www.notion.so/2b8edd4b98c581389bb4d773002d4873)
- [파이프라인 아키텍처 설계](https://www.notion.so/2b8edd4b98c581bb9d6ec0a3aba7e37a)
- [구조변경 아이디어](https://www.notion.so/2b8edd4b98c581cb9e4ae4fb5b0dab2c)

### 9.3 기술 문서

**Hadoop**
- [Apache Hadoop 공식 문서](https://hadoop.apache.org/docs/)
- [HDFS Architecture Guide](https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-hdfs/HdfsDesign.html)

**Scrapy**
- [Scrapy 공식 문서](https://docs.scrapy.org/)
- [Scrapy 아키텍처](https://docs.scrapy.org/en/latest/topics/architecture.html)

**Flask**
- [Flask 공식 문서](https://flask.palletsprojects.com/)
- [Flask REST API 튜토리얼](https://flask-restful.readthedocs.io/)

**React**
- [React 공식 문서](https://react.dev/)
- [Chart.js 문서](https://www.chartjs.org/docs/)

### 9.4 학습 자료

- Hadoop 클러스터 구축: [라즈베리파이 Hadoop 클러스터 가이드](http://www.nigelpond.com/uploads/How-to-build-a-7-node-Raspberry-Pi-Hadoop-Cluster.pdf)
- Scrapy 고급 기능: 기존 프로젝트 `scrapy_project/` 참고
- Flask 대시보드: [Creating Dashboard Web Apps with Flask](https://dev.to/codesharedot/custom-dashboard-with-flask-41gl)

---

## 10. 다음 단계

### 10.1 즉시 시작 가능한 작업

1. **라즈베리파이 준비**
   ```bash
   # Ubuntu Server 20.04 다운로드
   # SD카드에 이미지 쓰기
   # 초기 부팅 및 네트워크 설정
   ```

2. **프로젝트 구조 생성**
   ```bash
   cd /Users/juns/code/personal/notion/pknu_workspace/bigdata
   mkdir -p PICU dashboard/{src,public} scripts
   ```

3. **의존성 설치**
   ```bash
   # 라즈베리파이
   pip install scrapy

   # 외부 서버
   pip install flask flask-cors flask-sqlalchemy
   ```

### 10.2 개발 시작

본 문서를 기반으로 **Week 1부터 순차적으로 진행**하시면 됩니다.

각 주차별 상세 가이드는 필요시 추가로 작성하겠습니다.

---

**프로젝트 성공을 기원합니다! 🚀**
