# 📦 설치 가이드

이 가이드는 Scrapy 고급 기능 프로젝트를 설치하고 설정하는 방법을 안내합니다.

## 🚀 **빠른 설치**

### 1. 저장소 클론
```bash
git clone https://github.com/junexi0828/Big-Data-Crawling.git
cd Big-Data-Crawling
```

### 2. 브랜치 선택
```bash
# 최적화된 구조 브랜치 사용 (권장)
git checkout optimized-structure

# 또는 전체 개발 과정이 포함된 메인 브랜치
git checkout main
```

### 3. 가상환경 활성화
```bash
source scrapy_env/bin/activate
```

### 4. 의존성 확인
```bash
pip list | grep scrapy
```

## 🛠️ **수동 설치 (가상환경이 없는 경우)**

### 1. Python 가상환경 생성
```bash
python3 -m venv scrapy_env
source scrapy_env/bin/activate
```

### 2. 의존성 설치
```bash
pip install -r setup/requirements.txt
```

### 3. 주요 패키지 버전 확인
```bash
scrapy version
```

**필요한 주요 패키지들:**
- `scrapy>=2.13.3`
- `requests>=2.32.5`
- `lxml>=6.0.1`
- `itemloaders>=1.3.2`

## 🧪 **설치 테스트**

### 1. Scrapy 명령어 테스트
```bash
cd scrapy_project
scrapy --help
```

### 2. 기본 스파이더 테스트
```bash
scrapy list
```

예상 출력:
```
complex_quotes
ethical_spider
quotes_spider
useragent_spider
```

### 3. 샘플 크롤링 테스트
```bash
scrapy crawl quotes_spider -o test_output.json -s DOWNLOAD_DELAY=1
```

## 🔧 **개발 환경 설정**

### IDE 설정 (VS Code)
1. Python 인터프리터를 가상환경으로 설정
2. 확장 프로그램 설치: Python, Scrapy

### 환경 변수 설정
```bash
export SCRAPY_SETTINGS_MODULE=tutorial.settings
```

## 🚨 **문제 해결**

### 일반적인 오류들

**1. ImportError: No module named 'scrapy'**
```bash
# 가상환경이 활성화되었는지 확인
source scrapy_env/bin/activate
pip install scrapy
```

**2. SSL 인증서 오류**
```bash
pip install --trusted-host pypi.org --trusted-host pypi.python.org scrapy
```

**3. lxml 설치 오류 (macOS)**
```bash
# Xcode Command Line Tools 설치
xcode-select --install
pip install lxml
```

**4. Permission denied 오류**
```bash
# 권한 확인
chmod +x scrapy_env/bin/activate
```

### 디버깅 팁

1. **로그 레벨 증가**
```bash
scrapy crawl spider_name -L DEBUG
```

2. **Scrapy Shell 사용**
```bash
scrapy shell "http://quotes.toscrape.com"
```

3. **설정 확인**
```bash
scrapy settings
```

## 📱 **플랫폼별 설치**

### macOS
```bash
# Homebrew 사용
brew install python3
python3 -m venv scrapy_env
```

### Ubuntu/Debian
```bash
sudo apt update
sudo apt install python3-venv python3-dev libxml2-dev libxslt1-dev
python3 -m venv scrapy_env
```

### Windows
```bash
# Anaconda 권장
conda create -n scrapy_env python=3.9
conda activate scrapy_env
conda install scrapy
```

## ✅ **설치 완료 확인**

모든 설치가 완료되면 다음 명령어가 성공적으로 실행되어야 합니다:

```bash
cd scrapy_project
scrapy crawl quotes_spider -o test.json
ls outputs/json/
```

**설치가 완료되었습니다! 🎉**

다음 단계: [프로젝트 사용법](../README.md)으로 이동하세요.
