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

## 🗂️ **정규화된 데이터베이스 실습**

이 섹션에서는 단일 테이블에서 **정규화된 4개 테이블 구조**로 발전시키는 완전한 실습을 진행합니다.

> 📖 **상세 가이드**: [정규화된 데이터베이스 실습 가이드](docs/NORMALIZED_DB_GUIDE.md)

### 📋 **실습 개요**

**기존 구조 (단일 테이블):**

```sql
quotes (id, quote_content, author_name, birthdate, birthplace, bio, tags, created_at)
```

**정규화된 구조 (4개 테이블):**

```sql
AUTHOR (AUTHOR_ID, AUTHOR_NAME, BIRTH_DATE, BIRTH_PLACE, BIO)
QUOTE (QUOTE_ID, CONTENT, AUTHOR_ID)
TAG (TAG_ID, TAG_NAME)
QUOTE_TAG_INT (QUOTE_ID, TAG_ID)  -- 다대다 관계 테이블
```

### 🚀 **Step 1: 환경 준비**

```bash
# 1. 프로젝트 디렉토리로 이동
cd scrapy_project

# 2. 가상환경 활성화
source ../scrapy_env/bin/activate

# 3. MariaDB 컨테이너 상태 확인
docker ps
# vault 컨테이너가 실행 중인지 확인

# 4. 필요시 MariaDB 컨테이너 시작
docker start vault
```

### 🗄️ **Step 2: 정규화된 스키마 생성**

```bash
# MariaDB에 4개 테이블 생성
docker exec vault mariadb -u crawler -pcrawler+ scrapy -e "
CREATE TABLE AUTHOR (
    AUTHOR_ID INT NOT NULL AUTO_INCREMENT,
    AUTHOR_NAME VARCHAR(50) NOT NULL,
    BIRTH_DATE DATETIME NOT NULL,
    BIRTH_PLACE VARCHAR(150) NOT NULL,
    BIO TEXT NOT NULL,
    CONSTRAINT AUTHOR_PK PRIMARY KEY (AUTHOR_ID)
);"

docker exec vault mariadb -u crawler -pcrawler+ scrapy -e "
CREATE TABLE QUOTE (
    QUOTE_ID INT NOT NULL AUTO_INCREMENT,
    CONTENT TEXT NOT NULL,
    AUTHOR_ID INT NOT NULL,
    CONSTRAINT QUOTE_PK PRIMARY KEY (QUOTE_ID),
    CONSTRAINT QUOTE_TO_AUTHOR_FK FOREIGN KEY (AUTHOR_ID) REFERENCES AUTHOR(AUTHOR_ID)
);"

docker exec vault mariadb -u crawler -pcrawler+ scrapy -e "
CREATE TABLE TAG (
    TAG_ID INT NOT NULL AUTO_INCREMENT,
    TAG_NAME VARCHAR(50),
    CONSTRAINT TAG_PK PRIMARY KEY (TAG_ID)
);"

docker exec vault mariadb -u crawler -pcrawler+ scrapy -e "
CREATE TABLE QUOTE_TAG_INT (
    QUOTE_ID INT NOT NULL,
    TAG_ID INT NOT NULL,
    CONSTRAINT QUOTE_TAG_INT_PK PRIMARY KEY (QUOTE_ID, TAG_ID),
    CONSTRAINT QTINT_TO_QUOTE_FK FOREIGN KEY (QUOTE_ID) REFERENCES QUOTE(QUOTE_ID),
    CONSTRAINT QTINT_TO_TAG_FK FOREIGN KEY (TAG_ID) REFERENCES TAG(TAG_ID)
);"
```

### 🔧 **Step 3: 정규화된 파이프라인 실행**

```bash
# 정규화된 파이프라인으로 크롤링 실행
scrapy crawl complex_quotes -o normalized_result.jl -s CLOSESPIDER_ITEMCOUNT=10

# 더 많은 데이터 수집 (전체 페이지)
scrapy crawl complex_quotes -o normalized_full.jl -s CLOSESPIDER_PAGECOUNT=3
```

### 📊 **Step 4: 결과 확인 및 분석**

#### 기본 데이터 확인

```bash
# 각 테이블의 데이터 개수 확인
docker exec vault mariadb -u crawler -pcrawler+ scrapy -e "
SELECT
    (SELECT COUNT(*) FROM AUTHOR) as authors,
    (SELECT COUNT(*) FROM QUOTE) as quotes,
    (SELECT COUNT(*) FROM TAG) as tags,
    (SELECT COUNT(*) FROM QUOTE_TAG_INT) as relationships;"

# 작가별 명언 수 확인
docker exec vault mariadb -u crawler -pcrawler+ scrapy -e "
SELECT A.AUTHOR_NAME, COUNT(Q.QUOTE_ID) as quote_count
FROM AUTHOR A
LEFT JOIN QUOTE Q ON A.AUTHOR_ID = Q.AUTHOR_ID
GROUP BY A.AUTHOR_ID, A.AUTHOR_NAME
ORDER BY quote_count DESC;"
```

#### 고급 분석 쿼리

```bash
# 가장 인기 있는 태그 TOP 10
docker exec vault mariadb -u crawler -pcrawler+ scrapy -e "
SELECT T.TAG_NAME, COUNT(QTI.QUOTE_ID) as usage_count
FROM TAG T
LEFT JOIN QUOTE_TAG_INT QTI ON T.TAG_ID = QTI.TAG_ID
GROUP BY T.TAG_ID, T.TAG_NAME
ORDER BY usage_count DESC
LIMIT 10;"

# 특정 명언의 완전한 정보 (명언 + 작가 + 태그들)
docker exec vault mariadb -u crawler -pcrawler+ scrapy -e "
SELECT
    Q.CONTENT,
    A.AUTHOR_NAME,
    A.BIRTH_DATE,
    GROUP_CONCAT(T.TAG_NAME SEPARATOR ', ') as tags
FROM QUOTE Q
JOIN AUTHOR A ON Q.AUTHOR_ID = A.AUTHOR_ID
LEFT JOIN QUOTE_TAG_INT QTI ON Q.QUOTE_ID = QTI.QUOTE_ID
LEFT JOIN TAG T ON QTI.TAG_ID = T.TAG_ID
GROUP BY Q.QUOTE_ID
LIMIT 5;"
```

#### 관계형 데이터베이스의 장점 확인

```bash
# 특정 태그가 포함된 모든 명언과 작가
docker exec vault mariadb -u crawler -pcrawler+ scrapy -e "
SELECT DISTINCT A.AUTHOR_NAME, Q.CONTENT
FROM AUTHOR A
JOIN QUOTE Q ON A.AUTHOR_ID = Q.AUTHOR_ID
JOIN QUOTE_TAG_INT QTI ON Q.QUOTE_ID = QTI.QUOTE_ID
JOIN TAG T ON QTI.TAG_ID = T.TAG_ID
WHERE T.TAG_NAME = 'inspirational';"

# 가장 다양한 태그를 가진 명언 찾기
docker exec vault mariadb -u crawler -pcrawler+ scrapy -e "
SELECT
    LEFT(Q.CONTENT, 50) as quote_preview,
    A.AUTHOR_NAME,
    COUNT(T.TAG_ID) as tag_count
FROM QUOTE Q
JOIN AUTHOR A ON Q.AUTHOR_ID = A.AUTHOR_ID
LEFT JOIN QUOTE_TAG_INT QTI ON Q.QUOTE_ID = QTI.QUOTE_ID
LEFT JOIN TAG T ON QTI.TAG_ID = T.TAG_ID
GROUP BY Q.QUOTE_ID
ORDER BY tag_count DESC
LIMIT 5;"
```

### 🎯 **Step 5: 결과 비교 및 검증**

#### 정규화 전후 비교

```bash
# 기존 단일 테이블 (quotes)의 데이터 확인
docker exec vault mariadb -u crawler -pcrawler+ scrapy -e "SELECT COUNT(*) as old_quotes FROM quotes;"

# 새로운 정규화된 구조의 데이터 확인
docker exec vault mariadb -u crawler -pcrawler+ scrapy -e "SELECT COUNT(*) as new_quotes FROM QUOTE;"
```

#### 데이터 무결성 검증

```bash
# 외래키 제약조건 확인
docker exec vault mariadb -u crawler -pcrawler+ scrapy -e "
SELECT
    TABLE_NAME,
    CONSTRAINT_NAME,
    COLUMN_NAME,
    REFERENCED_TABLE_NAME,
    REFERENCED_COLUMN_NAME
FROM information_schema.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = 'scrapy'
AND REFERENCED_TABLE_NAME IS NOT NULL;"
```

### 🔄 **Step 6: 추가 실험**

#### 중복 데이터 테스트

```bash
# 동일한 크롤링을 다시 실행해서 중복 제거 확인
scrapy crawl complex_quotes -s CLOSESPIDER_ITEMCOUNT=5

# 로그에서 "Duplicate item found" 메시지 확인
```

#### 다른 스파이더와 비교

```bash
# 기본 스파이더로 단일 테이블에 저장 (비교용)
# settings.py에서 파이프라인을 MariaDBPipeline으로 일시 변경 후
scrapy crawl quotes -s CLOSESPIDER_ITEMCOUNT=5
```

### 📈 **예상 결과**

성공적으로 완료되면 다음과 같은 결과를 얻을 수 있습니다:

- **AUTHOR 테이블**: 8-10명의 고유 작가
- **QUOTE 테이블**: 10-15개의 명언
- **TAG 테이블**: 30-40개의 고유 태그
- **QUOTE_TAG_INT**: 40-60개의 관계 레코드

### 🚨 **문제 해결**

#### 일반적인 오류와 해결책

```bash
# 1. MariaDB 연결 오류
docker ps  # 컨테이너 상태 확인
docker start vault  # 컨테이너 시작

# 2. 권한 오류
docker exec vault mariadb -u root -pbigdata+ -e "FLUSH PRIVILEGES;"

# 3. 테이블 초기화 (필요시)
docker exec vault mariadb -u crawler -pcrawler+ scrapy -e "
DROP TABLE IF EXISTS QUOTE_TAG_INT;
DROP TABLE IF EXISTS TAG;
DROP TABLE IF EXISTS QUOTE;
DROP TABLE IF EXISTS AUTHOR;"
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

### 📚 **프로젝트 문서**

- [설치 가이드](docs/INSTALLATION.md) - 환경 설정 및 패키지 설치
- [프로젝트 구조](docs/PROJECT_STRUCTURE.md) - 디렉토리 구조 설명
- [배포 가이드](docs/DEPLOYMENT_GUIDE.md) - 운영 환경 배포
- [정규화 DB 실습](docs/NORMALIZED_DB_GUIDE.md) - 관계형 데이터베이스 설계

### 🌐 **외부 자료**

- [Scrapy 공식 문서](https://docs.scrapy.org/)
- [MariaDB 공식 문서](https://mariadb.org/documentation/)
- [프로젝트 깃허브](https://github.com/junexi0828/Big-Data-Crawling)

---

**Happy Scraping! 🎉**
