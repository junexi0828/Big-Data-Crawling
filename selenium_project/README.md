# Selenium 프로젝트 - Naver Finance 환율 정보 스크래핑

## 📋 프로젝트 개요

이 프로젝트는 Selenium을 사용하여 Naver Finance의 동적 콘텐츠(환율 정보)를 스크래핑하는 실습입니다.

**주요 학습 목표:**
1. **동적 콘텐츠 스크래핑**: JavaScript로 로드되는 데이터 수집
2. **Selenium WebDriver**: 브라우저 자동화 기초
3. **iframe 처리**: iframe 내부 콘텐츠 접근 방법
4. **실전 적용**: Naver Finance 환율 정보 스크래핑

---

## 📁 프로젝트 구조

```
selenium_project/
├── README.md                       # 이 파일
├── QUICK_START.md                  # 빠른 시작 가이드
├── PROJECT_SUMMARY.md              # 실습 결과 요약
├── requirements_selenium.txt       # Python 패키지 목록
│
├── selenium_demos/                 # ⭐ 메인 실습 (슬라이드 기반)
│   ├── README.md                  # 실습 가이드
│   ├── testChrome.py              # 기본 Selenium 사용법
│   ├── testGoogle.py              # Google 검색 (감지 우회)
│   ├── testNaver.py               # Naver Finance 스크래핑
│   └── testHeadless.py            # 헤드리스 모드 & User-Agent
│
├── selenium_basics/                # 기초 학습
│   ├── webdriver_config.py        # WebDriver 설정
│   └── iframe_handling.py         # iframe 처리 예제
│
├── naver_finance/                 # 실전 프로젝트
│   ├── n_exchange.py              # 환율 정보 스크래핑 (완성판)
│   └── with_middleware.py         # Scrapy + Selenium 통합
│
├── utils/                         # 공통 유틸리티
│   └── webdriver_utils.py         # WebDriver 유틸 (권한 자동 설정)
│
└── outputs/                       # 출력 파일 저장
    ├── json/                      # JSON 형식 출력
    └── csv/                       # CSV 형식 출력
```

---

## 🚀 설치 방법

### 1. 가상 환경 활성화

```bash
# 프로젝트 루트로 이동
cd /Users/juns/bigdata

# 가상 환경 활성화
source scrapy_env/bin/activate
```

### 2. 필요한 패키지 확인

이미 설치되어 있습니다:
- `selenium==4.15.2`
- `webdriver-manager==4.0.1`

### 3. ChromeDriver 권한 설정 (자동)

```bash
cd selenium_project
python utils/webdriver_utils.py
```

이 명령은 모든 ChromeDriver에 실행 권한을 자동으로 부여합니다.

---

## 🎓 실습 가이드

### 📚 학습 순서

```
1. selenium_demos/testChrome.py     → Selenium 기본 사용법
2. selenium_demos/testNaver.py      → iframe 처리 & 실전 스크래핑
3. selenium_demos/testGoogle.py     → Google 감지 우회
4. selenium_demos/testHeadless.py   → 헤드리스 모드 & 최적화
```

### 실습 1: Selenium 기본 사용법

```bash
python selenium_demos/testChrome.py
```

**학습 내용:**
- 웹 페이지 열기
- 요소 찾기 (By.NAME, By.XPATH 등)
- 텍스트 입력
- 폼 제출

### 실습 2: Naver Finance 스크래핑 ⭐

```bash
python selenium_demos/testNaver.py
```

**학습 내용:**
- iframe으로 전환
- 동적 콘텐츠 스크래핑
- 58개 국가/통화 환율 정보 수집

**출력 예시:**
```
환율 정보 (처음 10개):
1. 미국 USD: 1418.5
2. 유럽연합 EUR: 1655.6
3. 일본 JPY (100엔): 941.87
...
```

### 실습 3: Google 검색 (감지 우회)

```bash
python selenium_demos/testGoogle.py
```

**학습 내용:**
- navigator.webdriver 비활성화
- CDP (Chrome DevTool Protocol) 사용

### 실습 4: 헤드리스 모드

```bash
python selenium_demos/testHeadless.py
```

**학습 내용:**
- 헤드리스 브라우징 (브라우저 UI 없이)
- User-Agent 변경

---

## 💻 완성된 프로젝트

### 환율 정보 스크래핑 (JSON 저장)

```bash
python naver_finance/n_exchange.py
```

**출력:**
- `outputs/json/exchange_rates.json`
- 58개 국가/통화 환율 정보

### Scrapy + Selenium 통합

```bash
python naver_finance/with_middleware.py
```

**특징:**
- Scrapy의 효율적인 크롤링
- Selenium의 동적 콘텐츠 처리
- Downloader Middleware 통합

---

## 🛠️ 유틸리티

### WebDriver 유틸리티

```python
from utils import create_chrome_driver, setup_navigator_webdriver_false

# WebDriver 생성 (권한 자동 설정)
driver = create_chrome_driver(headless=False)

# navigator.webdriver 비활성화
setup_navigator_webdriver_false(driver)

# 페이지 접속
driver.get("https://www.google.com")
```

**주요 기능:**
- ✅ ChromeDriver 권한 자동 설정
- ✅ 다양한 옵션 설정 (헤드리스, User-Agent 등)
- ✅ 재사용 가능한 유틸리티 함수

---

## 🆚 Scrapy vs Selenium 비교

| 특징 | Scrapy | Selenium |
|------|--------|----------|
| 속도 | ⚡ 매우 빠름 | 🐢 느림 (브라우저 실행) |
| 동적 콘텐츠 | ❌ 제한적 | ✅ 완벽 지원 |
| JavaScript | ❌ 실행 안됨 | ✅ 실행됨 |
| 리소스 사용 | 💚 낮음 | 🔴 높음 |
| iframe 처리 | ❌ 어려움 | ✅ 쉬움 |
| 사용 시나리오 | 정적 페이지, 대량 데이터 | 동적 페이지, JavaScript 필수 |

---

## 📊 출력 예시

### JSON 파일 확인

```bash
cat outputs/json/exchange_rates.json
```

```json
{
  "date": "2025.10.20 14:03",
  "미국 USD": "1,418.50",
  "유럽연합 EUR": "1,655.60",
  "일본 JPY (100엔)": "941.87",
  "중국 CNY": "199.10",
  ...
}
```

---

## 🐛 문제 해결

### 문제 1: ChromeDriver 권한 오류

```bash
# 자동 해결
python utils/webdriver_utils.py
```

### 문제 2: 요소를 찾을 수 없음

```python
# 대기 시간 추가
time.sleep(2)

# 또는 명시적 대기
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

element = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "element_id"))
)
```

### 문제 3: iframe 내부 요소 접근 불가

```python
# iframe으로 전환 필수!
iframe = driver.find_element(By.ID, "frame_ex1")
driver.switch_to.frame(iframe)

# 작업 후 반드시 복귀
driver.switch_to.default_content()
```

---

## ⚠️ 주의사항

1. **윤리적 크롤링**: robots.txt 확인 및 준수
2. **요청 간격**: 서버 부하를 고려하여 적절한 지연 시간 설정
3. **User-Agent**: 적절한 식별 정보 제공
4. **저작권**: 수집한 데이터의 사용 목적 및 범위 준수

---

## 📚 추가 리소스

### 공식 문서
- [Selenium 공식 문서](https://www.selenium.dev/documentation/)
- [Selenium Python 가이드](https://selenium-python.readthedocs.io/)
- [webdriver-manager](https://github.com/SergeyPirogov/webdriver_manager)

### 관련 가이드
- [QUICK_START.md](QUICK_START.md) - 빠른 시작 가이드
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - 실습 결과 요약
- [selenium_demos/README.md](selenium_demos/README.md) - 데모별 상세 가이드

---

## 🎯 다음 단계

1. ✅ 기본 Selenium 실습 완료
2. ✅ Naver Finance 스크래핑 완료
3. ⬜ 헤드리스 모드로 서버 배포
4. ⬜ 데이터베이스 연동 (SQLite, PostgreSQL)
5. ⬜ 스케줄링 (매일 자동 실행)
6. ⬜ 다른 웹사이트 스크래핑 도전

---

**작성일**: 2025-10-20  
**버전**: 2.0 (정리 완료)  
**슬라이드 출처**: Big Data 처리론 - Selenium Fast-Track
