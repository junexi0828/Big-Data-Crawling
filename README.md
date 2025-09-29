# 🕷️ Scrapy 고급 기능 완전 실습 프로젝트

이 프로젝트는 **Scrapy의 모든 고급 기능**을 학습하고 실습할 수 있는 **완전한 가이드**입니다.

## 🎯 **프로젝트 개요**

본 프로젝트는 다음과 같은 Scrapy 고급 기능들을 포함합니다:

- ✅ **Spider Arguments** - 명령줄 인자를 통한 동적 크롤링
- ✅ **ItemLoader** - 데이터 전처리 및 검증
- ✅ **Item Pipeline** - 데이터 저장 및 후처리
- ✅ **MariaDB Pipeline** - 관계형 데이터베이스 연동
- ✅ **Duplication Filter** - 중복 데이터 제거
- ✅ **Ethical Crawling** - 윤리적 크롤링 원칙 준수
- ✅ **User-Agent 회전** - 차단 우회 기술

## 📁 **프로젝트 구조**

```
📁 scrapy-advanced-tutorial/
├── 📁 scrapy_project/                 # 🕷️ 메인 Scrapy 프로젝트 (정리된 버전)
│   ├── scrapy.cfg                     # Scrapy 설정
│   ├── tutorial/                      # 메인 패키지
│   │   ├── settings.py               # 윤리적 크롤링 + MariaDB 설정
│   │   ├── items.py                  # ItemLoader 적용 아이템
│   │   ├── itemloaders.py            # 전처리 함수들
│   │   ├── pipelines.py              # JSON/SQLite/MariaDB 파이프라인
│   │   ├── testDBConn.py             # MariaDB 연결 테스트
│   │   └── spiders/                  # 🕷️ 모든 스파이더
│   │       ├── quotes_spider.py      # 기본 크롤링
│   │       ├── complex_quotes.py     # ItemLoader + 중복필터
│   │       ├── useragent_spider.py   # User-Agent 회전
│   │       └── ethical_spider.py     # 윤리적 크롤링
│   └── outputs/                      # 📊 크롤링 결과
│       ├── json/                     # JSON 결과
│       ├── csv/                      # CSV 결과
│       └── databases/                # SQLite 데이터베이스
│
├── 📁 tutorial/                       # 📚 원본 개발 과정 (학습 참고용)
│   ├── scrapy.cfg                     # 원본 Scrapy 설정
│   └── tutorial/                      # 개발 과정의 모든 파일들
│
├── 📁 demos/                          # 🎮 학습용 데모
│   ├── basic_features/               # 기본 기능 데모 (pagination, follow 등)
│   ├── advanced_features/            # 고급 기능 데모 (ItemLoader, User-Agent 등)
│   └── scrapy_shell/                 # Shell 명령어 데모
│
├── 📁 docs/                          # 📖 프로젝트 문서
│   ├── README.md                     # 상세 가이드
│   ├── INSTALLATION.md               # 설치 가이드
│   ├── DEPLOYMENT_GUIDE.md          # 배포 가이드
│   └── PROJECT_STRUCTURE.md         # 구조 설명
│
├── 📁 scripts/                       # 🔧 유틸리티 스크립트
│   ├── setup_environment.sh         # 환경 설정 자동화
│   ├── run_all_spiders.py           # 모든 스파이더 실행
│   └── clean_outputs.py             # 결과 파일 정리
│
├── 📁 requirements/                  # 📦 의존성 관리
│   ├── requirements.txt             # 기본 패키지
│   └── requirements-dev.txt         # 개발용 패키지
│
├── scrapy_env/                      # 🐍 Python 가상환경
├── index.html                       # 🌐 프로젝트 웹 인터페이스
└── README.md                        # 📋 프로젝트 메인 가이드
```

## 🚀 **빠른 시작**

### 1. 가상환경 활성화

```bash
source scrapy_env/bin/activate
```

### 2. 환경 설정 (자동)

```bash
./scripts/setup_environment.sh
```

### 3. 기본 크롤링 실행

```bash
cd scrapy_project
scrapy crawl quotes -o outputs/json/basic_quotes.json
```

### 4. 고급 기능 실행

```bash
# ItemLoader 사용
scrapy crawl complex_quotes -o outputs/json/complex_quotes.json

# User-Agent 회전
scrapy crawl useragent_spider -o outputs/json/useragent_test.json

# 윤리적 크롤링
scrapy crawl ethical_crawler -o outputs/json/ethical_crawling.json

# MariaDB 파이프라인 (복합 기능 포함)
scrapy crawl complex_quotes -s CLOSESPIDER_ITEMCOUNT=10
```

### 5. 모든 스파이더 한번에 실행

```bash
python scripts/run_all_spiders.py
```

## 🗄️ **MariaDB 데이터베이스 연동**

### MariaDB 환경 설정

```bash
# 1. MariaDB Docker 컨테이너 실행
docker run -d -p 3306:3306 --detach --name vault \
  -e MARIADB_USER=bigdata \
  -e MARIADB_PASSWORD=bigdata+ \
  -e MARIADB_DATABASE=webscrap \
  -e MARIADB_ROOT_PASSWORD=bigdata+ \
  mariadb:latest

# 2. crawler 사용자 및 scrapy 데이터베이스 생성
docker exec vault mariadb -u root -pbigdata+ -e "CREATE USER 'crawler'@'%' IDENTIFIED BY 'crawler+';"
docker exec vault mariadb -u root -pbigdata+ -e "CREATE DATABASE scrapy;"
docker exec vault mariadb -u root -pbigdata+ -e "GRANT ALL PRIVILEGES ON scrapy.* TO 'crawler'@'%';"
docker exec vault mariadb -u root -pbigdata+ -e "FLUSH PRIVILEGES;"
```

### MariaDB 연결 테스트

```bash
# Python에서 MariaDB 연결 테스트
cd scrapy_project
python tutorial/testDBConn.py
```

### 데이터베이스 결과 확인

```bash
# MariaDB에 저장된 데이터 확인
docker exec vault mariadb -u crawler -pcrawler+ scrapy -e "SELECT COUNT(*) FROM quotes;"
docker exec vault mariadb -u crawler -pcrawler+ scrapy -e "SELECT author_name, COUNT(*) FROM quotes GROUP BY author_name;"
```

## 🎮 **데모 실행**

### 기본 기능 데모

```bash
python demos/basic_features/tutorial_explanations/follow_explanation.py
```

### 고급 기능 데모

```bash
# ItemLoader 데모
python demos/advanced_features/itemloader_demo.py

# 중복 필터 데모
python demos/advanced_features/duplication_filter_demo.py

# User-Agent 데모
python demos/advanced_features/useragent_demo.py

# 윤리적 크롤링 데모
python demos/advanced_features/ethical_crawling_complete_demo.py
```

## 📖 **학습 가이드**

1. **기초 학습**: `demos/basic_features/` 에서 시작
2. **고급 기능**: `demos/advanced_features/` 로 진행
3. **실전 적용**: `scrapy_project/` 에서 실습
4. **심화 학습**: `docs/` 에서 상세 가이드 확인

## 🛡️ **윤리적 크롤링**

본 프로젝트는 **윤리적 크롤링 4원칙**을 준수합니다:

1. ✅ **robots.txt 준수** - `ROBOTSTXT_OBEY = True`
2. ✅ **성능 저하 방지** - `DOWNLOAD_DELAY`, `CONCURRENT_REQUESTS` 제한
3. ✅ **신원 확인** - 적절한 `USER_AGENT` 설정
4. ✅ **관리자 배려** - AutoThrottle, HTTP 캐시 활용

## 📊 **결과 확인**

크롤링 결과는 다음 위치에서 확인할 수 있습니다:

- **JSON**: `scrapy_project/outputs/json/*.json`
- **CSV**: `scrapy_project/outputs/csv/*.csv`
- **SQLite**: `scrapy_project/outputs/databases/*.db`
- **MariaDB**: Docker 컨테이너 `vault`의 `scrapy` 데이터베이스

### 데이터베이스 스키마

**quotes 테이블 구조:**

```sql
CREATE TABLE quotes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    quote_content TEXT NOT NULL,
    author_name VARCHAR(255) NOT NULL,
    birthdate VARCHAR(100),
    birthplace TEXT,
    bio TEXT,
    tags JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔗 **유용한 링크**

- [Scrapy 공식 문서](https://docs.scrapy.org/)
- [프로젝트 깃허브](https://github.com/junexi0828/Big-Data-Crawling)
- [설치 가이드](docs/INSTALLATION.md)
- [배포 가이드](docs/DEPLOYMENT_GUIDE.md)

---

**Happy Scraping! 🎉**
