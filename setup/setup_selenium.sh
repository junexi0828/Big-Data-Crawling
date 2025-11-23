#!/bin/bash

# 🤖 Selenium 프로젝트 설치 스크립트

set -e

PROJECT_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$PROJECT_ROOT"

echo "🤖 Selenium 프로젝트 설치를 시작합니다..."

# 가상환경 확인
if [ ! -d "scrapy_env" ]; then
    echo "❌ 가상환경이 없습니다. 먼저 setup_all.sh 또는 setup_scrapy.sh를 실행하세요."
    exit 1
fi

# 가상환경 활성화
source scrapy_env/bin/activate

# Selenium 의존성 설치
if [ -f "selenium_project/requirements_selenium.txt" ]; then
    echo "📦 Selenium 의존성 설치 중..."
    scrapy_env/bin/pip install -r selenium_project/requirements_selenium.txt --quiet
    echo "✅ Selenium 의존성 설치 완료"

    # Selenium 버전 확인
    scrapy_env/bin/python3 -c "import selenium; print(f'✅ Selenium 버전: {selenium.__version__}')" 2>/dev/null || echo "⚠️  Selenium 설치 확인 필요"
else
    echo "❌ selenium_project/requirements_selenium.txt 파일을 찾을 수 없습니다."
    exit 1
fi

# 출력 디렉토리 생성
mkdir -p selenium_project/outputs/{json,csv}

echo ""
echo "🎉 Selenium 프로젝트 설치 완료!"
echo ""
echo "다음 명령어로 테스트하세요:"
echo "  cd selenium_project && python selenium_basics/webdriver_config.py"

