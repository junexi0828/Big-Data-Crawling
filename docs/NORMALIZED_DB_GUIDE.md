# 🗂️ 정규화된 데이터베이스 실습 가이드

## 📋 **빠른 시작 (Quick Start)**

### 🚀 **5분 만에 시작하기**

```bash
# 1. 프로젝트로 이동 및 환경 활성화
cd scrapy_project
source ../scrapy_env/bin/activate

# 2. MariaDB 컨테이너 확인/시작
docker ps | grep vault || docker start vault

# 3. 한 번에 4개 테이블 생성
docker exec vault mariadb -u crawler -pcrawler+ scrapy << 'EOF'
CREATE TABLE IF NOT EXISTS AUTHOR (
    AUTHOR_ID INT NOT NULL AUTO_INCREMENT,
    AUTHOR_NAME VARCHAR(50) NOT NULL,
    BIRTH_DATE DATETIME NOT NULL,
    BIRTH_PLACE VARCHAR(150) NOT NULL,
    BIO TEXT NOT NULL,
    CONSTRAINT AUTHOR_PK PRIMARY KEY (AUTHOR_ID)
);

CREATE TABLE IF NOT EXISTS QUOTE (
    QUOTE_ID INT NOT NULL AUTO_INCREMENT,
    CONTENT TEXT NOT NULL,
    AUTHOR_ID INT NOT NULL,
    CONSTRAINT QUOTE_PK PRIMARY KEY (QUOTE_ID),
    CONSTRAINT QUOTE_TO_AUTHOR_FK FOREIGN KEY (AUTHOR_ID) REFERENCES AUTHOR(AUTHOR_ID)
);

CREATE TABLE IF NOT EXISTS TAG (
    TAG_ID INT NOT NULL AUTO_INCREMENT,
    TAG_NAME VARCHAR(50),
    CONSTRAINT TAG_PK PRIMARY KEY (TAG_ID)
);

CREATE TABLE IF NOT EXISTS QUOTE_TAG_INT (
    QUOTE_ID INT NOT NULL,
    TAG_ID INT NOT NULL,
    CONSTRAINT QUOTE_TAG_INT_PK PRIMARY KEY (QUOTE_ID, TAG_ID),
    CONSTRAINT QTINT_TO_QUOTE_FK FOREIGN KEY (QUOTE_ID) REFERENCES QUOTE(QUOTE_ID),
    CONSTRAINT QTINT_TO_TAG_FK FOREIGN KEY (TAG_ID) REFERENCES TAG(TAG_ID)
);
EOF

# 4. 정규화된 파이프라인으로 크롤링
scrapy crawl complex_quotes -s CLOSESPIDER_ITEMCOUNT=10

# 5. 결과 확인
docker exec vault mariadb -u crawler -pcrawler+ scrapy -e "
SELECT
    (SELECT COUNT(*) FROM AUTHOR) as authors,
    (SELECT COUNT(*) FROM QUOTE) as quotes,
    (SELECT COUNT(*) FROM TAG) as tags,
    (SELECT COUNT(*) FROM QUOTE_TAG_INT) as relationships;"
```

---

## 📚 **상세 실습 가이드**

### 🎯 **학습 목표**

- 단일 테이블 구조의 문제점 이해
- 정규화된 관계형 데이터베이스 설계
- 다대다 관계 구현 및 활용
- 고급 SQL 쿼리 작성

### 📖 **실습 단계별 가이드**

#### **Phase 1: 환경 설정** ⏱️ 2분

```bash
# 현재 디렉토리 확인
pwd
# /Users/your-username/bigdata 에 있어야 함

# scrapy_project로 이동
cd scrapy_project

# 가상환경 활성화
source ../scrapy_env/bin/activate

# MariaDB 컨테이너 상태 확인
docker ps
```

**✅ 체크포인트**: `vault` 컨테이너가 `Up` 상태여야 함

---

#### **Phase 2: 스키마 생성** ⏱️ 3분

**방법 1: 개별 테이블 생성 (학습용)**

```bash
# AUTHOR 테이블 생성
docker exec vault mariadb -u crawler -pcrawler+ scrapy -e "
CREATE TABLE AUTHOR (
    AUTHOR_ID INT NOT NULL AUTO_INCREMENT,
    AUTHOR_NAME VARCHAR(50) NOT NULL,
    BIRTH_DATE DATETIME NOT NULL,
    BIRTH_PLACE VARCHAR(150) NOT NULL,
    BIO TEXT NOT NULL,
    CONSTRAINT AUTHOR_PK PRIMARY KEY (AUTHOR_ID)
);"

# 생성 확인
docker exec vault mariadb -u crawler -pcrawler+ scrapy -e "DESCRIBE AUTHOR;"
```

```bash
# QUOTE 테이블 생성 (외래키 포함)
docker exec vault mariadb -u crawler -pcrawler+ scrapy -e "
CREATE TABLE QUOTE (
    QUOTE_ID INT NOT NULL AUTO_INCREMENT,
    CONTENT TEXT NOT NULL,
    AUTHOR_ID INT NOT NULL,
    CONSTRAINT QUOTE_PK PRIMARY KEY (QUOTE_ID),
    CONSTRAINT QUOTE_TO_AUTHOR_FK FOREIGN KEY (AUTHOR_ID) REFERENCES AUTHOR(AUTHOR_ID)
);"

# 외래키 확인
docker exec vault mariadb -u crawler -pcrawler+ scrapy -e "
SHOW CREATE TABLE QUOTE;"
```

```bash
# TAG 테이블 생성
docker exec vault mariadb -u crawler -pcrawler+ scrapy -e "
CREATE TABLE TAG (
    TAG_ID INT NOT NULL AUTO_INCREMENT,
    TAG_NAME VARCHAR(50),
    CONSTRAINT TAG_PK PRIMARY KEY (TAG_ID)
);"
```

```bash
# QUOTE_TAG_INT 관계 테이블 생성 (다대다 관계)
docker exec vault mariadb -u crawler -pcrawler+ scrapy -e "
CREATE TABLE QUOTE_TAG_INT (
    QUOTE_ID INT NOT NULL,
    TAG_ID INT NOT NULL,
    CONSTRAINT QUOTE_TAG_INT_PK PRIMARY KEY (QUOTE_ID, TAG_ID),
    CONSTRAINT QTINT_TO_QUOTE_FK FOREIGN KEY (QUOTE_ID) REFERENCES QUOTE(QUOTE_ID),
    CONSTRAINT QTINT_TO_TAG_FK FOREIGN KEY (TAG_ID) REFERENCES TAG(TAG_ID)
);"
```

**✅ 체크포인트**: 4개 테이블 모두 생성 확인

```bash
docker exec vault mariadb -u crawler -pcrawler+ scrapy -e "SHOW TABLES;"
```

---

#### **Phase 3: 데이터 수집** ⏱️ 5분

```bash
# 테스트 크롤링 (10개 아이템)
scrapy crawl complex_quotes -o test_normalized.jl -s CLOSESPIDER_ITEMCOUNT=10

# 실제 크롤링 (더 많은 데이터)
scrapy crawl complex_quotes -o full_normalized.jl -s CLOSESPIDER_PAGECOUNT=3
```

**✅ 체크포인트**: 크롤링 로그에서 다음 메시지 확인

- `Successfully connected to MariaDB for normalized schema`
- `Validated item: [작가명]`

---

#### **Phase 4: 데이터 분석** ⏱️ 10분

**기본 통계**

```bash
# 전체 데이터 요약
docker exec vault mariadb -u crawler -pcrawler+ scrapy -e "
SELECT
    '📊 데이터 요약' as category,
    (SELECT COUNT(*) FROM AUTHOR) as authors,
    (SELECT COUNT(*) FROM QUOTE) as quotes,
    (SELECT COUNT(*) FROM TAG) as tags,
    (SELECT COUNT(*) FROM QUOTE_TAG_INT) as relationships;"
```

**작가 분석**

```bash
# 작가별 명언 수 (인기 작가 순)
docker exec vault mariadb -u crawler -pcrawler+ scrapy -e "
SELECT
    A.AUTHOR_NAME as '작가',
    A.BIRTH_DATE as '생년월일',
    COUNT(Q.QUOTE_ID) as '명언_수'
FROM AUTHOR A
LEFT JOIN QUOTE Q ON A.AUTHOR_ID = Q.AUTHOR_ID
GROUP BY A.AUTHOR_ID
ORDER BY 명언_수 DESC;"
```

**태그 분석**

```bash
# 인기 태그 TOP 10
docker exec vault mariadb -u crawler -pcrawler+ scrapy -e "
SELECT
    T.TAG_NAME as '태그',
    COUNT(QTI.QUOTE_ID) as '사용_횟수'
FROM TAG T
LEFT JOIN QUOTE_TAG_INT QTI ON T.TAG_ID = QTI.TAG_ID
GROUP BY T.TAG_ID
ORDER BY 사용_횟수 DESC
LIMIT 10;"
```

**복합 분석**

```bash
# 명언-작가-태그 통합 정보
docker exec vault mariadb -u crawler -pcrawler+ scrapy -e "
SELECT
    LEFT(Q.CONTENT, 60) as '명언_미리보기',
    A.AUTHOR_NAME as '작가',
    GROUP_CONCAT(T.TAG_NAME ORDER BY T.TAG_NAME SEPARATOR ', ') as '태그들'
FROM QUOTE Q
JOIN AUTHOR A ON Q.AUTHOR_ID = A.AUTHOR_ID
LEFT JOIN QUOTE_TAG_INT QTI ON Q.QUOTE_ID = QTI.QUOTE_ID
LEFT JOIN TAG T ON QTI.TAG_ID = T.TAG_ID
GROUP BY Q.QUOTE_ID
LIMIT 5;"
```

---

#### **Phase 5: 고급 쿼리** ⏱️ 15분

**특정 조건 검색**

```bash
# 'inspirational' 태그가 있는 모든 명언과 작가
docker exec vault mariadb -u crawler -pcrawler+ scrapy -e "
SELECT DISTINCT
    A.AUTHOR_NAME as '작가',
    Q.CONTENT as '영감을_주는_명언'
FROM AUTHOR A
JOIN QUOTE Q ON A.AUTHOR_ID = Q.AUTHOR_ID
JOIN QUOTE_TAG_INT QTI ON Q.QUOTE_ID = QTI.QUOTE_ID
JOIN TAG T ON QTI.TAG_ID = T.TAG_ID
WHERE T.TAG_NAME = 'inspirational';"
```

**통계 분석**

```bash
# 태그 개수별 명언 분포
docker exec vault mariadb -u crawler -pcrawler+ scrapy -e "
SELECT
    tag_count as '태그_개수',
    COUNT(*) as '명언_수',
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM QUOTE), 2) as '비율_%'
FROM (
    SELECT Q.QUOTE_ID, COUNT(T.TAG_ID) as tag_count
    FROM QUOTE Q
    LEFT JOIN QUOTE_TAG_INT QTI ON Q.QUOTE_ID = QTI.QUOTE_ID
    LEFT JOIN TAG T ON QTI.TAG_ID = T.TAG_ID
    GROUP BY Q.QUOTE_ID
) tag_stats
GROUP BY tag_count
ORDER BY tag_count;"
```

**데이터 품질 검증**

```bash
# 외래키 무결성 검증
docker exec vault mariadb -u crawler -pcrawler+ scrapy -e "
SELECT
    '외래키_무결성_검증' as 검증_항목,
    CASE
        WHEN (SELECT COUNT(*) FROM QUOTE Q LEFT JOIN AUTHOR A ON Q.AUTHOR_ID = A.AUTHOR_ID WHERE A.AUTHOR_ID IS NULL) = 0
        THEN '✅ 통과'
        ELSE '❌ 실패'
    END as QUOTE_AUTHOR_FK,
    CASE
        WHEN (SELECT COUNT(*) FROM QUOTE_TAG_INT QTI LEFT JOIN QUOTE Q ON QTI.QUOTE_ID = Q.QUOTE_ID WHERE Q.QUOTE_ID IS NULL) = 0
        THEN '✅ 통과'
        ELSE '❌ 실패'
    END as QTI_QUOTE_FK,
    CASE
        WHEN (SELECT COUNT(*) FROM QUOTE_TAG_INT QTI LEFT JOIN TAG T ON QTI.TAG_ID = T.TAG_ID WHERE T.TAG_ID IS NULL) = 0
        THEN '✅ 통과'
        ELSE '❌ 실패'
    END as QTI_TAG_FK;"
```

---

### 🎯 **실습 미션**

#### **미션 1: 중복 테스트** 🎮

```bash
# 같은 크롤링을 다시 실행
scrapy crawl complex_quotes -s CLOSESPIDER_ITEMCOUNT=5

# 로그에서 "Duplicate item found" 메시지 확인
# 데이터베이스 카운트가 증가하지 않음을 확인
```

#### **미션 2: 성능 비교** 📊

```bash
# 정규화 전후 스토리지 사용량 비교
docker exec vault mariadb -u crawler -pcrawler+ scrapy -e "
SELECT
    table_name as '테이블',
    ROUND(((data_length + index_length) / 1024 / 1024), 2) as '크기_MB'
FROM information_schema.tables
WHERE table_schema = 'scrapy'
ORDER BY (data_length + index_length) DESC;"
```

#### **미션 3: 데이터 마이그레이션** 🔄

```bash
# 기존 quotes 테이블에서 정규화된 구조로 데이터 이전
# (고급 실습 - 선택사항)
```

---

### 🚨 **FAQ & 문제해결**

#### Q1: "Can't connect to MariaDB" 오류

```bash
# 해결책
docker ps  # vault 컨테이너 상태 확인
docker start vault  # 컨테이너 시작
docker logs vault  # 에러 로그 확인
```

#### Q2: "Foreign key constraint fails" 오류

```bash
# 해결책 - 테이블 생성 순서 확인
# 1. AUTHOR → 2. QUOTE → 3. TAG → 4. QUOTE_TAG_INT

# 초기화 후 재생성
docker exec vault mariadb -u crawler -pcrawler+ scrapy -e "
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS QUOTE_TAG_INT, TAG, QUOTE, AUTHOR;
SET FOREIGN_KEY_CHECKS = 1;"
```

#### Q3: "Duplicate entry" 오류

```bash
# 해결책 - 정상적인 중복 제거 동작
# 로그에서 "Duplicate item found" 메시지 확인
```

#### Q4: 데이터가 저장되지 않음

```bash
# 체크리스트
# 1. 파이프라인 설정 확인
grep -n "NormalizedTutorialPipeline" tutorial/settings.py

# 2. 데이터베이스 연결 확인
docker exec vault mariadb -u crawler -pcrawler+ scrapy -e "SELECT 1;"

# 3. 로그 레벨 상세화
scrapy crawl complex_quotes -L DEBUG -s CLOSESPIDER_ITEMCOUNT=1
```

---

### 🎉 **성공 기준**

완료 후 다음 결과를 얻어야 합니다:

| 테이블        | 예상 레코드 수 | 설명           |
| ------------- | -------------- | -------------- |
| AUTHOR        | 8-12개         | 고유 작가들    |
| QUOTE         | 10-20개        | 수집된 명언들  |
| TAG           | 30-50개        | 다양한 태그들  |
| QUOTE_TAG_INT | 40-80개        | 명언-태그 관계 |

**최종 검증 쿼리:**

```bash
docker exec vault mariadb -u crawler -pcrawler+ scrapy -e "
SELECT
    '🎉 실습 완료!' as 상태,
    (SELECT COUNT(*) FROM AUTHOR) as 작가수,
    (SELECT COUNT(*) FROM QUOTE) as 명언수,
    (SELECT COUNT(*) FROM TAG) as 태그수,
    (SELECT COUNT(*) FROM QUOTE_TAG_INT) as 관계수,
    CASE
        WHEN (SELECT COUNT(*) FROM AUTHOR) > 5 AND
             (SELECT COUNT(*) FROM QUOTE) > 8 AND
             (SELECT COUNT(*) FROM TAG) > 20
        THEN '✅ 성공'
        ELSE '❌ 재시도 필요'
    END as 결과;"
```

---

### 📚 **추가 학습 자료**

- **관계형 데이터베이스 이론**: 1NF, 2NF, 3NF 정규화
- **SQL 고급 쿼리**: JOIN, GROUP BY, 집계 함수
- **인덱스 최적화**: 성능 향상 기법
- **데이터 무결성**: 외래키, 제약조건

**Happy Database Modeling! 🗂️✨**
