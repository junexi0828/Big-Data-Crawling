# Selenium WebDriver 데모

슬라이드 "Selenium Fast-Track"의 실습 예제 구현

## 📋 데모 목록

### 1. **testChrome.py** - Selenium 기본 사용법
```bash
python selenium_demos/testChrome.py
```

**학습 내용:**
- WebDriver 초기화
- 요소 찾기 (By.NAME, By.XPATH, By.ID 등)
- 텍스트 입력 (`send_keys`)
- 조건부 대기 (`WebDriverWait`)
- 다양한 폼 요소 처리:
  - Text input
  - Password
  - Textarea  
  - Select (드롭다운)
  - Checkbox
  - Radio 버튼
- 폼 제출 (`click`)

---

### 2. **testGoogle.py** - Google 검색 (navigator.webdriver 우회)
```bash
python selenium_demos/testGoogle.py
```

**학습 내용:**
- Google의 Selenium 감지 우회
- CDP (Chrome DevTool Protocol) 사용
- `navigator.webdriver`를 undefined로 설정
- 검색 자동화

**핵심 코드:**
```python
# CDP를 사용하여 navigator.webdriver 비활성화
driver.execute_cdp_cmd(
    "Page.addScriptToEvaluateOnNewDocument",
    {
        "source": """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        """
    }
)
```

---

### 3. **testNaver.py** - Naver Finance 스크래핑 ⭐
```bash
python selenium_demos/testNaver.py
```

**학습 내용:**
- 페이지 소스 확인 (`driver.page_source`)
- iframe 전환 (`switch_to.frame`)
- 동적 콘텐츠 스크래핑
- 메인 윈도우 복귀 (`switch_to.default_content`)
- 탭 클릭 및 테이블 추출

**실행 결과:**
```
환율 정보 (처음 10개):
1. 미국 USD: 1418.5
2. 유럽연합 EUR: 1655.6
3. 일본 JPY (100엔): 941.87
...
```

---

### 4. **testHeadless.py** - WebDriver Configuration
```bash
python selenium_demos/testHeadless.py
```

**학습 내용:**
- 헤드리스 브라우징 (브라우저 UI 없이)
- User-Agent 변경
- 다양한 Chrome 옵션:
  - `--headless`
  - `--disable-gpu`
  - `--lang=ko_KR`
  - `user-agent=...`

**장점:**
- ✅ 서버 환경에서 실행 가능
- ✅ 리소스 절약
- ✅ 빠른 실행 속도

---

## 🚀 실행 방법

### 환경 준비
```bash
# 가상환경 활성화
source /Users/juns/bigdata/scrapy_env/bin/activate

# selenium_project 디렉토리로 이동
cd selenium_project
```

### 개별 실행
```bash
# 1. 기본 Selenium 사용법
python selenium_demos/testChrome.py

# 2. Google 검색 (navigator.webdriver 우회)
python selenium_demos/testGoogle.py

# 3. Naver Finance 스크래핑 (추천!)
python selenium_demos/testNaver.py

# 4. 헤드리스 모드 & User-Agent
python selenium_demos/testHeadless.py
```

---

## 📊 스크립트 비교

| 스크립트 | 난이도 | 학습 내용 | 실행 시간 |
|---------|-------|----------|---------|
| testChrome.py | ⭐ 기초 | 기본 사용법 | ~30초 |
| testGoogle.py | ⭐⭐ 중급 | 감지 우회 | ~20초 |
| testNaver.py | ⭐⭐⭐ 고급 | iframe, 실전 | ~15초 |
| testHeadless.py | ⭐⭐ 중급 | 설정 최적화 | ~10초 |

---

## 🎓 학습 순서 추천

```
1. testChrome.py      → Selenium 기본 익히기
2. testNaver.py        → iframe 처리 및 실전 적용
3. testGoogle.py       → 감지 우회 기법
4. testHeadless.py     → 최적화 및 서버 환경 준비
```

---

## 💡 핵심 개념

### 1. WebDriver 초기화
```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

chromedriver_path = "~/.wdm/drivers/chromedriver/..."
service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service)
```

### 2. 요소 찾기
```python
# By.NAME
element = driver.find_element(By.NAME, "my-text")

# By.XPATH
element = driver.find_element(By.XPATH, "//div[@class='exchange_info']")

# By.ID
element = driver.find_element(By.ID, "frame_ex1")

# By.CSS_SELECTOR
element = driver.find_element(By.CSS_SELECTOR, "td.tit")
```

### 3. iframe 처리
```python
# iframe으로 전환
driver.switch_to.frame('frame_ex1')

# iframe 내부 작업
rows = driver.find_elements(By.XPATH, "//table/tbody/tr")

# 메인 윈도우로 복귀
driver.switch_to.default_content()
```

### 4. 조건부 대기
```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 요소가 나타날 때까지 대기
element = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.TAG_NAME, "form"))
)
```

---

## 🐛 문제 해결

### 문제 1: ChromeDriver 권한 오류
```bash
# 실행 권한 부여
chmod +x ~/.wdm/drivers/chromedriver/mac64/.../chromedriver
```

### 문제 2: 요소를 찾을 수 없음
```python
# 대기 시간 추가
time.sleep(2)

# 또는 명시적 대기 사용
WebDriverWait(driver, 10).until(...)
```

### 문제 3: iframe 내부 요소 접근 불가
```python
# iframe으로 전환 필수!
driver.switch_to.frame('frame_id')
```

---

## 📚 추가 학습 자료

- [Selenium 공식 문서](https://www.selenium.dev/documentation/)
- [Selenium Python](https://selenium-python.readthedocs.io/)
- [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)

---

**작성일:** 2025-10-20  
**버전:** 1.0  
**슬라이드 출처:** Big Data 처리론 - Selenium Fast-Track

