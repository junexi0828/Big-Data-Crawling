# 동적 콘텐츠 처리 및 로그인 처리 가이드

## 📋 목차

1. [동적 콘텐츠 처리](#동적-콘텐츠-처리)
2. [복잡한 HTTP 요청](#복잡한-http-요청)
3. [로그인 처리](#로그인-처리)
4. [실습 예제](#실습-예제)
5. [문제 해결](#문제-해결)

---

## 🌐 동적 콘텐츠 처리

### 개요

현대 웹사이트는 JavaScript를 통해 콘텐츠를 동적으로 로드합니다. Scrapy는 기본적으로 JavaScript를 실행하지 않으므로, 다른 접근 방법이 필요합니다.

### 전략 1: 브라우저 개발자 도구 활용

#### Network 도구 사용법

1. **브라우저 개발자 도구 열기** (F12)
2. **Network 탭 선택**
3. **Preserve log 옵션 활성화** - 이전 방문 로그 유지
4. **페이지 스크롤/상호작용** - 동적 로딩 트리거
5. **XHR/Fetch 필터** - API 요청 확인

#### 주요 발견 사항

```javascript
// 예: 무한 스크롤 웹사이트의 실제 API 엔드포인트
http://quotes.toscrape.com/api/quotes?page=1
// 응답: JSON 형식
{
  "has_next": true,
  "page": 1,
  "quotes": [...]
}
```

### 전략 2: JSON API 활용

#### ScrollableSpider 예제

```python
import scrapy
import json

class ScrollableSpider(scrapy.Spider):
    name = "scrollable_spider"
    allowed_domains = ["quotes.toscrape.com"]
    page = 1
    start_urls = ["http://quotes.toscrape.com/api/quotes?page=1"]

    def parse(self, response):
        # JSON 응답을 파이썬 딕셔너리로 변환
        data = json.loads(response.text)

        # quotes 데이터에서 각 quote 추출
        for quote in data["quotes"]:
            yield {
                "quote": quote["text"],
                "author": quote["author"]["name"],
                "tags": quote["tags"],
            }

        # 다음 페이지가 있는지 확인
        if data["has_next"]:
            self.page += 1
            next_page = f"http://quotes.toscrape.com/api/quotes?page={self.page}"
            yield scrapy.Request(url=next_page, callback=self.parse)
```

#### 실행

```bash
scrapy crawl scrollable_spider -O dynamicquote.jl
```

#### 결과

- ✅ 100개 quotes 수집
- ✅ 자동 페이지네이션
- ✅ HTML 파싱 불필요

---

## 🔄 복잡한 HTTP 요청

### cURL to Scrapy Request 변환

많은 웹사이트는 복잡한 헤더나 쿠키를 요구합니다. cURL 명령어를 Scrapy Request로 변환할 수 있습니다.

### 방법 1: Request.from_curl()

```python
import scrapy

class ComplexRequestSpider(scrapy.Spider):
    name = "complex_request_spider"

    def start_requests(self):
        curl_command = """
        curl 'http://quotes.toscrape.com/api/quotes?page=1' \
        -H 'User-Agent: Mozilla/5.0' \
        -H 'Accept: application/json' \
        -H 'Referer: http://quotes.toscrape.com/scroll'
        """

        request = scrapy.Request.from_curl(
            curl_command.strip(),
            callback=self.parse
        )
        yield request

    def parse(self, response):
        import json
        data = json.loads(response.text)
        # 데이터 처리...
```

### 방법 2: curl_to_request_kwargs()

```python
from scrapy.utils.curl import curl_to_request_kwargs

curl_kwargs = curl_to_request_kwargs(
    curl_command.strip(),
    ignore_unknown_options=True
)
yield scrapy.Request(**curl_kwargs, callback=self.parse)
```

### 실행 결과

```bash
scrapy crawl complex_request_spider -O complex_requests_output.jl
```

- ✅ 복잡한 헤더 자동 처리
- ✅ cURL 명령어 재사용 가능

---

## 🔐 로그인 처리

### CSRF (Cross-Site Request Forgery) 이해

#### CSRF 공격이란?

- 공격자가 피해자로 하여금 의도하지 않은 행동을 하게 만드는 공격
- 로그인된 세션을 악용하여 악의적인 요청 전송

#### CSRF 방어 메커니즘

1. **CSRF 토큰**: 각 폼에 고유한 토큰 포함
2. **Referer/Origin 체크**: 요청 출처 확인
3. **SameSite 쿠키**: 쿠키 전송 제한
4. **CAPTCHA**: 봇 방지

### 로그인 처리 방법

#### 1-Pass 로그인 (간단한 방법)

**사용 시기**: Hidden 데이터가 복잡하지 않은 경우

```python
import scrapy
from scrapy.http import FormRequest

class SimpleLoginSpider(scrapy.Spider):
    name = "simple_login"
    login_url = "http://quotes.toscrape.com/login"

    custom_settings = {
        "DUPEFILTER_CLASS": "scrapy.dupefilters.BaseDupeFilter",
        "COOKIES_ENABLED": True,  # 중요!
    }

    def start_requests(self):
        # 직접 로그인 폼 데이터 제출
        return [
            FormRequest(
                self.login_url,
                formdata={
                    "username": "user",
                    "password": "secret"
                },
                callback=self.parse,
            )
        ]

    def parse(self, response):
        # 로그인 성공 확인
        if "Logout" in response.text:
            self.logger.info("✅ 로그인 성공!")
            # 데이터 수집...
```

#### 2-Pass 로그인 (복잡한 방법)

**사용 시기**: CSRF 토큰 등 Hidden 데이터가 있는 경우

```python
import scrapy
from scrapy.http import Request, FormRequest

class ComplexLoginSpider(scrapy.Spider):
    name = "complex_login"
    login_url = "http://quotes.toscrape.com/login"

    custom_settings = {
        "DUPEFILTER_CLASS": "scrapy.dupefilters.BaseDupeFilter",
        "COOKIES_ENABLED": True,
    }

    def start_requests(self):
        # 1단계: 로그인 페이지 요청
        return [Request(self.login_url, callback=self.process_login)]

    def process_login(self, response):
        # 2단계: CSRF 토큰 추출
        csrf_token = response.xpath(
            '//input[@name="csrf_token"]/@value'
        ).extract_first()

        self.logger.info(f"🔑 CSRF 토큰: {csrf_token}")

        # FormRequest.from_response로 로그인 폼 제출
        yield FormRequest.from_response(
            response,
            formdata={
                "csrf_token": csrf_token,
                "username": "user",
                "password": "secret",
            },
            callback=self.parse,
        )

    def parse(self, response):
        # 로그인 성공 확인
        if "Logout" in response.text:
            self.logger.info("✅ 로그인 성공!")
            # 데이터 수집...
```

### 실행 및 결과

```bash
# 간단한 로그인
scrapy crawl simple_login -O simple_login_output.jl

# 복잡한 로그인
scrapy crawl complex_login -O complex_login_output.jl
```

**결과 비교**

| 방식   | 요청 수 | 장점           | 단점                |
| ------ | ------- | -------------- | ------------------- |
| 1-Pass | 3       | 빠름, 단순     | CSRF 토큰 처리 불가 |
| 2-Pass | 4       | CSRF 토큰 처리 | 추가 요청 필요      |

---

## 🎯 실습 예제

### ItemLoader와 함께 사용하기

```python
from scrapy.loader import ItemLoader
from tutorial.items import QuotesItem

class LoginQuotesSpider(scrapy.Spider):
    name = "login_quotes"

    def parse(self, response):
        for q in response.css("div.quote"):
            loader = ItemLoader(item=QuotesItem(), selector=q)
            loader.add_css("quote_content", "span.text::text")
            loader.add_css("author_name", "small.author::text")
            loader.add_css("tags", "div.tags a.tag::text")

            yield loader.load_item()

        # 다음 페이지
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
```

---

## 🔧 문제 해결

### 1. 로그인이 실패하는 경우

#### 문제: "Logout" 링크가 보이지 않음

**해결 방법**:

```python
# 쿠키 활성화 확인
custom_settings = {
    "COOKIES_ENABLED": True,  # 반드시 True!
}

# 로그인 응답 디버깅
def after_login(self, response):
    self.logger.info(f"응답 URL: {response.url}")
    self.logger.info(f"응답 텍스트 일부: {response.text[:200]}")
```

#### 문제: CSRF 토큰 오류

**해결 방법**:

```python
# XPath 선택자 확인
csrf_token = response.xpath('//input[@name="csrf_token"]/@value').get()

# 또는 CSS 선택자 사용
csrf_token = response.css('form input[name="csrf_token"]::attr(value)').get()

# 토큰 출력하여 확인
self.logger.info(f"CSRF 토큰: {csrf_token}")
```

### 2. 동적 콘텐츠가 보이지 않는 경우

#### 문제: JavaScript로 로드되는 콘텐츠

**해결 방법 1: API 엔드포인트 찾기**

```bash
# 브라우저 개발자 도구 > Network 탭
# XHR/Fetch 필터 적용
# 실제 API 엔드포인트 확인
```

**해결 방법 2: Scrapy-Splash 사용**

```python
# JavaScript 렌더링이 필요한 경우
# Scrapy-Splash 또는 Selenium 고려
```

### 3. XPath 표현식 최적화

#### ❌ 나쁜 예: 절대 경로

```python
response.xpath('/html/body/div/div[2]/div[1]/div[1]/span[1]/text()')
```

#### ✅ 좋은 예: 상대 경로 + 속성

```python
response.xpath('//span[has-class("text")]/text()')
# 또는
response.css('span.text::text')
```

### 4. 중복 필터 문제

#### 문제: 같은 URL 재방문 불가

**해결 방법**:

```python
# 전역 설정 (settings.py)
DUPEFILTER_CLASS = 'scrapy.dupefilters.BaseDupeFilter'

# 또는 스파이더별 설정
custom_settings = {
    'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
}

# 또는 개별 요청에 dont_filter 사용
yield scrapy.Request(url, callback=self.parse, dont_filter=True)
```

---

## 📊 실습 결과 요약

### 구현된 스파이더

1. **ScrollableSpider** (`scrollablespider.py`)

   - 100개 quotes 수집
   - JSON API 활용
   - 자동 페이지네이션

2. **ComplexRequestSpider** (`complex_request_spider.py`)

   - cURL 명령어 변환
   - 복잡한 헤더 처리

3. **SimpleLoginSpider** (`simple_login_spider.py`)

   - 1-pass 로그인
   - 5개 quotes 수집
   - 빠른 처리

4. **ComplexLoginSpider** (`complex_login_spider.py`)
   - 2-pass 로그인
   - CSRF 토큰 처리
   - 5개 quotes 수집

### 성능 통계

| 스파이더             | 요청 수 | 수집 아이템 | 처리 시간 | 성공률 |
| -------------------- | ------- | ----------- | --------- | ------ |
| ScrollableSpider     | 11      | 100         | ~34초     | 100%   |
| ComplexRequestSpider | 2       | 3           | ~4초      | 100%   |
| SimpleLoginSpider    | 3       | 5           | ~9초      | 100%   |
| ComplexLoginSpider   | 4       | 5           | ~13초     | 100%   |

---

## 🎓 핵심 학습 내용

### 동적 콘텐츠 처리

- ✅ 브라우저 개발자 도구 활용법
- ✅ Network 탭으로 API 엔드포인트 발견
- ✅ JSON 응답 파싱
- ✅ XPath 표현식 최적화

### 보안 및 인증

- ✅ CSRF 공격 이해
- ✅ CSRF 토큰 추출 및 활용
- ✅ 쿠키 관리
- ✅ 세션 유지

### 실무 스킬

- ✅ cURL 명령어 재사용
- ✅ 복잡한 HTTP 요청 처리
- ✅ 로그인 시스템 우회
- ✅ 에러 핸들링 및 디버깅

---

## 📚 추가 리소스

### 공식 문서

- [Scrapy FormRequest](https://docs.scrapy.org/en/latest/topics/request-response.html#formrequest-objects)
- [Scrapy Request.from_curl()](https://docs.scrapy.org/en/latest/topics/request-response.html#request-from-curl)
- [CSRF 보안](https://portswigger.net/web-security/csrf)

### 관련 도구

- [curl2scrapy](https://michael-shub.github.io/curl2scrapy/) - cURL to Scrapy 변환기
- [Scrapy-Splash](https://github.com/scrapy-plugins/scrapy-splash) - JavaScript 렌더링
- [Selenium](https://www.selenium.dev/) - 브라우저 자동화

### 모범 사례

1. **윤리적 크롤링**: robots.txt 준수
2. **지연 시간 설정**: 서버 부하 최소화
3. **User-Agent 설정**: 적절한 식별
4. **에러 처리**: 견고한 예외 처리
5. **로그 레벨 조정**: 디버깅 정보 수집

---

## 🔗 관련 문서

- [설치 가이드](INSTALLATION.md)
- [프로젝트 구조](PROJECT_STRUCTURE.md)
- [배포 가이드](DEPLOYMENT_GUIDE.md)
- [정규화 데이터베이스 가이드](NORMALIZED_DB_GUIDE.md)

---

**작성일**: 2025-10-13
**버전**: 1.0
**작성자**: Big Data Scrapy Tutorial
