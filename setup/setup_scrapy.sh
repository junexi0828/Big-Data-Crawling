#!/bin/bash

# 🕷️ Scrapy 프로젝트 설치 스크립트

set -e

PROJECT_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$PROJECT_ROOT"

echo "🕷️ Scrapy 프로젝트 설치를 시작합니다..."

# 가상환경 확인 및 생성
if [ ! -d "scrapy_env" ]; then
    echo "📦 가상환경 생성 중..."
    python3 -m venv scrapy_env
fi

# 가상환경 활성화
source scrapy_env/bin/activate

# pip 업그레이드 (가상환경 내 pip 사용)
if [ -f "scrapy_env/bin/pip" ]; then
    scrapy_env/bin/pip install --upgrade pip --quiet
else
    echo "⚠️  pip을 찾을 수 없습니다. 가상환경을 재생성합니다..."
    rm -rf scrapy_env
    python3 -m venv scrapy_env
    source scrapy_env/bin/activate
    scrapy_env/bin/pip install --upgrade pip --quiet
fi

# Scrapy 의존성 설치
if [ -f "setup/requirements.txt" ]; then
    echo "📦 Scrapy 의존성 설치 중..."
    scrapy_env/bin/pip install -r setup/requirements.txt --quiet
    echo "✅ Scrapy 의존성 설치 완료"

    # Scrapy 버전 확인
    if [ -f "scrapy_env/bin/scrapy" ]; then
        SCRAPY_VERSION=$(scrapy_env/bin/scrapy version)
        echo "✅ Scrapy 버전: $SCRAPY_VERSION"
    fi
else
    echo "❌ setup/requirements.txt 파일을 찾을 수 없습니다."
    exit 1
fi

# 출력 디렉토리 생성
mkdir -p scrapy_project/outputs/{json,csv,databases}

echo ""
echo "🎉 Scrapy 프로젝트 설치 완료!"
echo ""
echo "다음 명령어로 테스트하세요:"
echo "  cd scrapy_project && scrapy list"

