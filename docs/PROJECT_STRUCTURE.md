# 🕷️ Scrapy 프로젝트 구조

## 📁 전체 폴더 구조

```
/Users/juns/bigdata/
├── 🕷️ 실제 크롤링 코드
│   ├── quotes_spider.py          # response.follow() 방식 명언 크롤러
│   ├── author_spider.py          # 작가 정보 크롤러
│   └── test_spider.py            # 테스트 및 데모 스크립트
│
├── 📊 크롤링 결과 데이터
│   ├── quotes_follow_output.json     # response.follow() 방식 명언 데이터 (110개)
│   ├── authors_output.json           # 작가 상세 정보 데이터
│   ├── quotes_from_standalone.json   # 독립 스파이더 결과 (120개)
│   └── test_quotes_output.json       # 테스트 결과 데이터
│
├── 🎓 Scrapy 튜토리얼 프로젝트
│   └── tutorial/                     # 공식 Scrapy 튜토리얼 프로젝트
│       ├── scrapy.cfg
│       ├── tutorial/
│       │   ├── spiders/
│       │   │   ├── quotes_spider.py  # 프로젝트 내 스파이더
│       │   │   ├── AuthorSpider.py   # 작가 스파이더
│       │   │   └── mybot.py
│       │   ├── items.py
│       │   ├── middlewares.py
│       │   ├── pipelines.py
│       │   └── settings.py
│       └── result files...
│
├── 📚 실습 설명 자료
│   └── tutorial_explanations/        # 학습용 설명 파일들
│       ├── README.md                 # 설명 자료 가이드
│       ├── follow_explanation.py     # response.follow() 상세 설명
│       └── comparison_demo.py        # 기존 vs 새로운 방식 비교
│
├── 🐍 Python 가상환경
│   └── scrapy_env/                   # Scrapy 가상환경
│
└── 📋 프로젝트 정보
    ├── README.md                     # 프로젝트 메인 설명서
    ├── requirements.txt              # 필요한 패키지 목록
    └── PROJECT_STRUCTURE.md          # 이 파일 (프로젝트 구조 설명)
```

## 🎯 주요 파일별 역할

### 실제 크롤링 코드

- **quotes_spider.py**: response.follow() 방식을 사용한 최신 명언 크롤러
- **author_spider.py**: 작가 링크를 따라가며 상세 정보를 수집하는 크롤러
- **test_spider.py**: 다양한 스파이더를 테스트할 수 있는 통합 스크립트

### 크롤링 결과

- **quotes_follow_output.json**: 110개의 명언 (response.follow 방식)
- **authors_output.json**: 다수 작가의 상세 정보 (이름, 생년월일, 출생지, 전기)
- **quotes_from_standalone.json**: 120개의 명언 (독립 실행 결과)

### 학습 자료

- **tutorial_explanations/**: 실습 과정에서 만든 모든 설명 자료
- 실제 코드와 분리하여 학습 목적으로만 사용

## 🚀 실행 방법

### 1. 가상환경 활성화

```bash
source scrapy_env/bin/activate
```

### 2. 독립 스파이더 실행

```bash
# 명언 크롤링
scrapy runspider quotes_spider.py -O output.json

# 작가 정보 크롤링
scrapy runspider author_spider.py -O authors.json
```

### 3. 테스트 스크립트 실행

```bash
python3 test_spider.py
# 1번 선택: 명언 스파이더
# 2번 선택: 작가 스파이더
```

### 4. 튜토리얼 프로젝트 실행

```bash
cd tutorial
scrapy crawl quotes -O output.json
```

## 📊 학습 성과

- ✅ 기존 Request 방식 → response.follow() 방식 전환
- ✅ 페이지 네비게이션 자동화 구현
- ✅ 작가 상세 정보 크롤링 구현
- ✅ 총 230개 이상의 데이터 수집 성공
- ✅ 현대적 Scrapy 패턴 학습 완료

---

> 💡 이 프로젝트는 Scrapy의 **response.follow() 방식**을 중심으로 한 현대적 웹 크롤링 학습 프로젝트입니다!
