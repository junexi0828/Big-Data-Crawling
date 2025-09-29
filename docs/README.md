# 🕷️ 빅데이터 크롤링 프로젝트

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://python.org)
[![Scrapy](https://img.shields.io/badge/Scrapy-2.13.3-green.svg)](https://scrapy.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 프로젝트 개요

**현대적 Scrapy 패턴을 활용한 웹 크롤링 실습 프로젝트**

이 프로젝트는 Python Scrapy의 **response.follow() 방식**을 중심으로 한 고급 웹 크롤링 기법을 학습하고 실습하는 프로젝트입니다.

## ✨ 주요 특징

- 🚀 **response.follow() 방식** - 현대적 Scrapy 패턴 적용
- 🔄 **자동 페이지 네비게이션** - 링크 따라가기 자동화
- 👤 **작가 상세 정보 크롤링** - 다층 데이터 수집
- 📊 **실시간 모니터링** - 크롤링 과정 시각화
- 📚 **상세한 학습 자료** - 코드 설명과 비교 분석

## 🛠️ 사용 기술 스택

| 기술 | 버전 | 용도 |
|------|------|------|
| **Python** | 3.13 | 메인 언어 |
| **Scrapy** | 2.13.3 | 웹 크롤링 프레임워크 |
| **CSS Selectors** | - | 요소 선택 |
| **XPath** | - | 고급 요소 선택 |

## 📁 프로젝트 구조

```
📦 빅데이터크롤링/
├── 🕷️ 크롤링 코드
│   ├── quotes_spider.py          # response.follow() 명언 크롤러
│   ├── author_spider.py          # 작가 정보 크롤러
│   └── test_spider.py            # 통합 테스트 스크립트
│
├── 📊 수집 데이터
│   ├── quotes_follow_output.json    # 명언 데이터 (110개)
│   ├── authors_output.json         # 작가 정보 데이터
│   └── 기타 결과 파일들...
│
├── 📚 학습 자료
│   └── tutorial_explanations/      # 상세 설명 및 비교 자료
│       ├── README.md               # 학습 가이드
│       ├── follow_explanation.py   # response.follow() 설명
│       └── comparison_demo.py      # 방식 비교
│
├── 🎓 Scrapy 튜토리얼
│   └── tutorial/                   # 공식 튜토리얼 프로젝트
│
└── 📋 프로젝트 문서
    ├── README.md                   # 메인 문서
    ├── PROJECT_STRUCTURE.md        # 구조 설명
    └── requirements.txt            # 의존성 목록
```

## 🚀 빠른 시작

### 1. 저장소 클론
```bash
git clone https://github.com/junexi0828/빅데이터크롤링.git
cd 빅데이터크롤링
```

### 2. 가상환경 설정
```bash
python -m venv scrapy_env
source scrapy_env/bin/activate  # macOS/Linux
# 또는
scrapy_env\Scripts\activate     # Windows
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 스파이더 실행
```bash
# 명언 크롤링 (response.follow 방식)
scrapy runspider quotes_spider.py -O quotes.json

# 작가 정보 크롤링
scrapy runspider author_spider.py -O authors.json

# 통합 테스트 (선택형)
python test_spider.py
```

## 📊 크롤링 성과

| 항목 | 결과 | 설명 |
|------|------|------|
| **명언 수집** | 110개 | response.follow() 방식으로 수집 |
| **작가 정보** | 다수 | 이름, 생년월일, 출생지, 전기 |
| **처리 속도** | 1100개/분 | 높은 성능 달성 |
| **페이지 수** | 11페이지 | 자동 네비게이션 |

## 🎓 학습 포인트

### 기존 방식 vs response.follow() 방식

**Before (기존 방식)**
```python
next_page = response.css("li.next a::attr(href)").get()
if next_page is not None:
    next_page = response.urljoin(next_page)
    yield scrapy.Request(next_page, callback=self.parse)
```

**After (response.follow() 방식)**
```python
for a in response.css("ul.pager a"):
    yield response.follow(a, callback=self.parse)
```

### 📈 개선 효과
- **코드 감소**: 4줄 → 2줄 (50% 감소)
- **복잡도 감소**: 수동 처리 → 자동 처리
- **에러 감소**: 자동 예외 처리
- **유지보수성 향상**: 더 읽기 쉬운 코드

## 🎯 크롤링 대상

**메인 사이트**: [http://quotes.toscrape.com](http://quotes.toscrape.com)

### 수집 데이터
- 📝 **명언**: 텍스트, 작가, 태그
- 👤 **작가 정보**: 이름, 생년월일, 출생지, 전기
- 🔗 **링크 관계**: 명언 ↔ 작가 연결

## 📚 학습 자료

프로젝트의 `tutorial_explanations/` 폴더에서 상세한 학습 자료를 확인할 수 있습니다:

- **follow_explanation.py**: response.follow() 동작 원리
- **comparison_demo.py**: 기존 방식과 새로운 방식 비교
- **README.md**: 학습 가이드

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 🙏 감사의 말

- [Scrapy](https://scrapy.org/) - 훌륭한 웹 크롤링 프레임워크
- [Quotes to Scrape](http://quotes.toscrape.com/) - 실습용 웹사이트 제공

---

<div align="center">

**⭐ 이 프로젝트가 도움이 되었다면 스타를 눌러주세요! ⭐**

Made with ❤️ by [junexi0828](https://github.com/junexi0828)

</div>