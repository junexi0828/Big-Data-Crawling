# 변경 이력

## [2.0.0] - 2025-10-20

### 추가
- ✨ `utils/webdriver_utils.py` - ChromeDriver 권한 자동 설정 유틸리티
- ✨ `selenium_demos/` - 슬라이드 기반 실습 예제
  - testChrome.py
  - testGoogle.py
  - testNaver.py
  - testHeadless.py

### 변경
- 📝 README.md 전면 개편 (정리된 구조 반영)
- 🎨 프로젝트 구조 재구성

### 삭제
- 🗑️ simple_test.py (임시 테스트 파일)
- 🗑️ test_installation.py (utils로 대체)
- 🗑️ naver_finance/basic_example.py (중복)
- 🗑️ naver_finance/naver_finance_demo.py (중복)

### 개선
- 🔧 ChromeDriver 권한 문제 자동 해결
- 📦 모듈화된 유틸리티 함수
- 📚 더 나은 문서화

## [1.0.0] - 2025-10-20

### 추가
- 🎉 Selenium 프로젝트 초기 버전
- Naver Finance 환율 스크래핑 기능
- Scrapy + Selenium 통합 예제
