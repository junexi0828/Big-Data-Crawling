# ⚡ 빠른 시작 가이드

## 1️⃣ 환경 설정 (5분)

### 필요한 것들

- Python 3.8 이상
- Chrome 브라우저 (최신 버전 권장)

### 설치

```bash
# 프로젝트 디렉토리로 이동
cd selenium_project

# 필요한 패키지 설치
pip install -r requirements_selenium.txt
```

**설치되는 패키지:**
- `selenium`: 브라우저 자동화
- `webdriver-manager`: ChromeDriver 자동 관리
- `pandas`: 데이터 처리 (선택사항)

---

## 2️⃣ 첫 번째 실습: Selenium 기본 (10분)

### 실습 1: WebDriver 설정 테스트

```bash
python selenium_basics/webdriver_config.py
```

**결과:**
- Chrome 브라우저가 자동으로 열림
- Google 페이지 방문
- WebDriver 정보 출력
- 자동으로 브라우저 종료

### 실습 2: Selenium 기본 사용법

```bash
python naver_finance/basic_example.py
```

**학습 내용:**
- 웹 페이지 열기
- 요소 찾기
- 텍스트 입력
- 명시적 대기

---

## 3️⃣ 두 번째 실습: iframe 처리 (15분)

### 실습 3: iframe 처리

```bash
python selenium_basics/iframe_handling.py
```

**학습 내용:**
- iframe이란?
- iframe으로 전환하는 방법
- Naver Finance의 실제 iframe 처리
- 메인 콘텐츠로 복귀

**중요 개념:**
```python
# iframe으로 전환
driver.switch_to.frame(iframe_element)

# iframe 내부 요소 접근
element = driver.find_element(By.XPATH, "...")

# 메인 콘텐츠로 복귀
driver.switch_to.default_content()
```

---

## 4️⃣ 세 번째 실습: Naver Finance 스크래핑 (20분)

### 실습 4: 환율 정보 스크래핑 ⭐

```bash
python naver_finance/n_exchange.py
```

**무엇을 하나요?**
1. Naver Finance 시장지표 페이지 접속
2. 환율고시 날짜 추출
3. iframe 내부의 환율 테이블 스크래핑
4. JSON 파일로 저장

**출력 파일:**
- `outputs/json/exchange_rates_YYYYMMDD_HHMMSS.json`

**출력 예시:**
```json
{
  "date": "2021.05.26 09:34",
  "미국 USD": "1,122.50",
  "유럽연합 EUR": "1,375.12",
  "일본 JPY(100엔)": "1,034.39",
  "중국 CNY": "175.25",
  ...
}
```

---

## 5️⃣ 네 번째 실습: Scrapy + Selenium 통합 (30분)

### 실습 5: Selenium Middleware

```bash
python naver_finance/with_middleware.py
```

**무엇이 다른가요?**
- Scrapy의 강력한 크롤링 기능
- Selenium의 동적 콘텐츠 처리 능력
- 두 가지를 결합!

**장점:**
- ✅ Scrapy의 효율적인 요청 관리
- ✅ Selenium의 JavaScript 실행
- ✅ 대규모 크롤링에 적합

---

## 🎯 실습 순서 요약

```
1. webdriver_config.py     → Selenium 설정 확인
2. basic_example.py         → Selenium 기본 사용법
3. iframe_handling.py       → iframe 처리 방법
4. n_exchange.py            → ⭐ 메인 실습: Naver Finance 스크래핑
5. with_middleware.py       → Scrapy + Selenium 통합
```

---

## 🐛 자주 발생하는 문제

### 문제 1: ChromeDriver 오류

**증상:**
```
selenium.common.exceptions.SessionNotCreatedException
```

**해결:**
```bash
# webdriver-manager가 자동으로 해결해줍니다.
# 하지만 수동으로 설치하려면:
# 1. Chrome 버전 확인: chrome://version/
# 2. 해당 버전의 ChromeDriver 다운로드
```

### 문제 2: 요소를 찾을 수 없음

**증상:**
```
selenium.common.exceptions.NoSuchElementException
```

**해결:**
```python
# 대기 시간 추가
time.sleep(2)

# 또는 명시적 대기
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

wait = WebDriverWait(driver, 10)
element = wait.until(
    EC.presence_of_element_located((By.ID, "element_id"))
)
```

### 문제 3: iframe 내부 요소에 접근 불가

**증상:**
```
selenium.common.exceptions.NoSuchElementException
(iframe 내부의 요소임에도 불구하고)
```

**해결:**
```python
# iframe으로 전환했는지 확인!
iframe = driver.find_element(By.ID, "frame_ex1")
driver.switch_to.frame(iframe)

# 작업 후 반드시 복귀
driver.switch_to.default_content()
```

---

## 📊 결과 확인

### JSON 파일 확인

```bash
# 출력 디렉토리 확인
ls -la outputs/json/

# JSON 파일 내용 확인 (macOS/Linux)
cat outputs/json/exchange_rates.json

# JSON 파일 내용 확인 (Windows)
type outputs\json\exchange_rates.json
```

### Python으로 JSON 읽기

```python
import json

with open('outputs/json/exchange_rates.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    print(json.dumps(data, ensure_ascii=False, indent=2))
```

---

## 🎓 다음 단계

1. ✅ 기본 실습 완료
2. ⬜ 헤드리스 모드로 실행 (`headless=True`)
3. ⬜ 다른 웹사이트 스크래핑 시도
4. ⬜ 데이터를 CSV로 저장
5. ⬜ 데이터베이스에 저장
6. ⬜ 스케줄링 (매일 자동 실행)

---

## 💡 팁

### 빠르게 테스트하기

```bash
# 헤드리스 모드로 실행 (브라우저 UI 없이)
# n_exchange.py 파일에서 headless=True로 변경
```

### 윤리적 크롤링

```python
# 요청 간격 추가
import time
time.sleep(2)  # 2초 대기

# User-Agent 설정
chrome_options.add_argument('user-agent=...')
```

### 디버깅

```python
# 스크린샷 저장
driver.save_screenshot('debug.png')

# 페이지 소스 확인
print(driver.page_source)

# 현재 URL 확인
print(driver.current_url)
```

---

## 📚 추가 리소스

- [Selenium 공식 문서](https://www.selenium.dev/documentation/)
- [Selenium Python 가이드](https://selenium-python.readthedocs.io/)
- [XPath 튜토리얼](https://www.w3schools.com/xml/xpath_intro.asp)

---

**준비되셨나요? 실습 1번부터 시작하세요! 🚀**

```bash
python selenium_basics/webdriver_config.py
```

