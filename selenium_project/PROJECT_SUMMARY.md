# 📊 Selenium 프로젝트 실습 결과 요약

## 🎯 프로젝트 개요

이 프로젝트는 **Selenium을 사용한 동적 웹 스크래핑** 실습으로, Scrapy로는 수집하기 어려운 JavaScript로 렌더링되는 콘텐츠를 스크래핑하는 방법을 학습했습니다.

---

## 🚀 실습 내용

### 1. 환경 설정
```bash
# 가상환경 활성화
source /Users/juns/bigdata/scrapy_env/bin/activate

# Selenium 설치
pip install selenium==4.15.2 webdriver-manager==4.0.1
```

**설치된 패키지:**
- ✅ selenium v4.15.2
- ✅ webdriver-manager v4.0.1

### 2. Naver Finance 환율 정보 스크래핑

**타겟 URL:** https://finance.naver.com/marketindex/

**도전 과제:**
- 환율고시 테이블이 iframe 내부에 위치
- JavaScript로 동적 로딩
- Scrapy Shell로는 데이터가 비어있음

**해결 방법:**
- ✅ Selenium WebDriver 사용
- ✅ iframe 전환 (`switch_to.frame()`)
- ✅ 동적 콘텐츠 로딩 후 스크래핑

---

## 📊 스크래핑 결과

### 실행 명령어
```bash
cd selenium_project
source /Users/juns/bigdata/scrapy_env/bin/activate
python naver_finance/n_exchange.py
```

### 수집 결과
- **수집 날짜:** 2025.10.20 13:21
- **수집 항목:** 58개 국가/통화 환율 정보
- **출력 파일:** `outputs/json/exchange_rates.json`

### 주요 환율 데이터 (예시)
```json
{
  "date": "2025.10.20 13:21",
  "미국 USD": "1,418.90",
  "유럽연합 EUR": "1,655.50",
  "일본 JPY (100엔)": "941.73",
  "중국 CNY": "199.15",
  "홍콩 HKD": "182.67",
  ...
}
```

---

## 💻 프로젝트 구조

```
selenium_project/
├── README.md                       # 프로젝트 소개 및 가이드
├── QUICK_START.md                  # 빠른 시작 가이드
├── PROJECT_SUMMARY.md              # 이 파일 (실습 결과 요약)
├── requirements_selenium.txt       # Python 패키지 목록
├── simple_test.py                  # 간단한 Selenium 테스트
├── test_installation.py            # 설치 확인 테스트
│
├── selenium_basics/                # Selenium 기초 학습
│   ├── __init__.py
│   ├── webdriver_config.py        # WebDriver 설정 방법
│   └── iframe_handling.py         # iframe 처리 예제
│
├── naver_finance/                 # Naver Finance 스크래핑
│   ├── __init__.py
│   ├── basic_example.py           # Selenium 기본 사용법
│   ├── n_exchange.py              # ⭐ 메인: 환율 정보 스크래핑
│   └── with_middleware.py         # Scrapy + Selenium 통합
│
└── outputs/                       # 출력 파일 저장
    ├── json/
    │   └── exchange_rates.json    # 수집된 환율 데이터
    └── csv/
```

---

## 🎓 학습한 주요 내용

### 1. Selenium WebDriver 설정
```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

# ChromeDriver 경로 지정
service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service)
```

### 2. iframe 처리
```python
# iframe 찾기
iframe = driver.find_element(By.ID, "frame_ex1")

# iframe으로 전환
driver.switch_to.frame(iframe)

# iframe 내부 데이터 스크래핑
rows = driver.find_elements(By.XPATH, "//table/tbody/tr")

# 메인 콘텐츠로 복귀
driver.switch_to.default_content()
```

### 3. 요소 찾기 및 데이터 추출
```python
# 날짜 정보 추출
date = driver.find_element(By.XPATH, "//div[@class='exchange_info']/span[1]").text

# 테이블 행 순회
for row in rows:
    title = row.find_element(By.XPATH, ".//td[@class='tit']/a").text
    rate = row.find_element(By.XPATH, ".//td[@class='sale']").text
```

### 4. 데이터 저장
```python
import json

with open('exchange_rates.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
```

---

## 🆚 Scrapy vs Selenium 비교

| 항목 | Scrapy | Selenium |
|------|--------|----------|
| **속도** | ⚡ 매우 빠름 | 🐢 느림 (브라우저 실행) |
| **동적 콘텐츠** | ❌ 제한적 | ✅ 완벽 지원 |
| **JavaScript** | ❌ 실행 안됨 | ✅ 실행됨 |
| **리소스 사용** | 💚 낮음 | 🔴 높음 (메모리/CPU) |
| **대량 스크래핑** | ✅ 적합 | ⚠️ 제한적 |
| **iframe 처리** | ❌ 어려움 | ✅ 쉬움 |
| **사용 사례** | 정적 페이지, API | 동적 페이지, SPA |

---

## 📈 성능 통계

### 실행 통계
- **처리 시간:** ~10초
- **요청 수:** 2회 (메인 페이지 + iframe)
- **수집 항목:** 58개
- **성공률:** 100%

### 리소스 사용
- **메모리:** 브라우저 실행으로 인한 높은 메모리 사용
- **CPU:** 중간~높음
- **네트워크:** 낮음 (2개 페이지만 로드)

---

## 🎯 실습 성과

### ✅ 완료한 실습
1. ✅ Selenium 설치 및 환경 설정
2. ✅ WebDriver 기본 사용법 학습
3. ✅ iframe 처리 방법 학습
4. ✅ Naver Finance 환율 정보 스크래핑 (58개 항목)
5. ✅ JSON 파일로 데이터 저장

### 📝 작성한 스크립트
1. `selenium_basics/webdriver_config.py` - WebDriver 설정
2. `selenium_basics/iframe_handling.py` - iframe 처리 데모
3. `naver_finance/basic_example.py` - Selenium 기초
4. `naver_finance/n_exchange.py` - 환율 스크래핑 (메인)
5. `naver_finance/with_middleware.py` - Scrapy 통합

---

## 💡 주요 학습 포인트

### 1. iframe 처리의 중요성
- 많은 웹사이트가 보안/성능을 위해 iframe 사용
- `switch_to.frame()` 필수
- 작업 후 `switch_to.default_content()` 복귀

### 2. 대기 전략
```python
# 암묵적 대기 (Implicit Wait)
driver.implicitly_wait(10)

# 명시적 대기 (Explicit Wait)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

element = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "element_id"))
)
```

### 3. 선택자 활용
```python
# By.ID
driver.find_element(By.ID, "frame_ex1")

# By.XPATH
driver.find_element(By.XPATH, "//td[@class='tit']")

# By.CSS_SELECTOR
driver.find_element(By.CSS_SELECTOR, "td.tit")

# By.CLASS_NAME
driver.find_element(By.CLASS_NAME, "exchange_info")
```

---

## 🚧 해결한 문제들

### 문제 1: webdriver-manager 경로 오류
**증상:**
```
OSError: [Errno 8] Exec format error: '...THIRD_PARTY_NOTICES.chromedriver'
```

**해결:**
```python
# ChromeDriver 경로 직접 지정
chromedriver_path = os.path.expanduser(
    "~/.wdm/drivers/chromedriver/mac64/.../chromedriver"
)
service = Service(chromedriver_path)
```

### 문제 2: iframe 내부 요소를 찾을 수 없음
**증상:**
```
NoSuchElementException: Unable to locate element
```

**해결:**
```python
# iframe으로 전환 필수!
iframe = driver.find_element(By.ID, "frame_ex1")
driver.switch_to.frame(iframe)
```

---

## 🔄 Scrapy와 Selenium 통합

### Selenium Downloader Middleware
슬라이드에서 제시된 방식대로 Selenium을 Scrapy의 Downloader Middleware로 통합하는 예제도 구현했습니다.

**장점:**
- ✅ Scrapy의 효율적인 요청 관리
- ✅ Selenium의 JavaScript 실행 능력
- ✅ 대규모 크롤링에 적합

**파일:** `naver_finance/with_middleware.py`

---

## 📚 추가 학습 자료

### 공식 문서
- [Selenium 공식 문서](https://www.selenium.dev/documentation/)
- [Selenium Python 가이드](https://selenium-python.readthedocs.io/)

### 참고 자료
- Naver Finance: https://finance.naver.com/
- XPath 튜토리얼: https://www.w3schools.com/xml/xpath_intro.asp

---

## 🎉 결론

이번 실습을 통해 다음을 성공적으로 학습했습니다:

1. ✅ **Selenium 기초**: WebDriver 설정 및 사용법
2. ✅ **동적 콘텐츠 스크래핑**: JavaScript로 렌더링되는 페이지 처리
3. ✅ **iframe 처리**: 중첩된 프레임 내부 데이터 추출
4. ✅ **실전 적용**: Naver Finance 실제 데이터 수집 (58개 환율)
5. ✅ **데이터 저장**: JSON 형식으로 구조화된 데이터 저장

### 다음 단계
- ⬜ 헤드리스 모드로 실행하여 속도 향상
- ⬜ 스케줄링을 통한 자동화 (cron, APScheduler)
- ⬜ 데이터베이스 연동 (SQLite, PostgreSQL)
- ⬜ 다른 동적 웹사이트 스크래핑 도전
- ⬜ Scrapy + Selenium 대규모 프로젝트

---

**작성일:** 2025-10-20
**프로젝트 상태:** ✅ 완료
**성공률:** 100%

