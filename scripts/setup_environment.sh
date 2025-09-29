#!/bin/bash

# 🚀 Scrapy 고급 기능 프로젝트 환경 설정 스크립트
# 이 스크립트는 프로젝트 환경을 자동으로 설정합니다.

echo "🕷️ Scrapy 고급 기능 프로젝트 환경 설정을 시작합니다..."

# 현재 디렉토리 확인
PROJECT_ROOT=$(pwd)
echo "📂 프로젝트 루트: $PROJECT_ROOT"

# 가상환경 활성화 확인
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ 가상환경이 이미 활성화되어 있습니다: $VIRTUAL_ENV"
else
    echo "⚠️ 가상환경이 활성화되지 않았습니다."

    # scrapy_env 디렉토리가 있는지 확인
    if [ -d "scrapy_env" ]; then
        echo "🔄 기존 가상환경을 활성화합니다..."
        source scrapy_env/bin/activate
        echo "✅ 가상환경 활성화 완료!"
    else
        echo "❌ scrapy_env 가상환경을 찾을 수 없습니다."
        echo "💡 다음 명령어로 가상환경을 생성하세요:"
        echo "   python3 -m venv scrapy_env"
        echo "   source scrapy_env/bin/activate"
        echo "   pip install -r requirements/requirements.txt"
        exit 1
    fi
fi

# Scrapy 설치 확인
echo "🔍 Scrapy 설치 상태를 확인합니다..."
if command -v scrapy &> /dev/null; then
    SCRAPY_VERSION=$(scrapy version)
    echo "✅ Scrapy가 설치되어 있습니다: $SCRAPY_VERSION"
else
    echo "❌ Scrapy가 설치되지 않았습니다."
    echo "📦 의존성을 설치합니다..."
    pip install -r requirements/requirements.txt
fi

# 프로젝트 구조 확인
echo "📁 프로젝트 구조를 확인합니다..."

REQUIRED_DIRS=("scrapy_project" "demos" "docs" "requirements" "scripts")
for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "✅ $dir 디렉토리 존재"
    else
        echo "❌ $dir 디렉토리가 없습니다."
        mkdir -p "$dir"
        echo "📁 $dir 디렉토리를 생성했습니다."
    fi
done

# Scrapy 프로젝트 설정 확인
echo "🕷️ Scrapy 프로젝트 설정을 확인합니다..."
cd scrapy_project

if [ -f "scrapy.cfg" ]; then
    echo "✅ scrapy.cfg 파일 존재"
else
    echo "❌ scrapy.cfg 파일이 없습니다."
    exit 1
fi

# 스파이더 목록 확인
echo "🔍 사용 가능한 스파이더를 확인합니다..."
SPIDERS=$(scrapy list 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "✅ 사용 가능한 스파이더들:"
    echo "$SPIDERS" | sed 's/^/   • /'
else
    echo "❌ 스파이더 목록을 가져올 수 없습니다."
fi

# 출력 디렉토리 생성
echo "📊 출력 디렉토리를 확인합니다..."
OUTPUT_DIRS=("outputs/json" "outputs/csv" "outputs/databases")
for dir in "${OUTPUT_DIRS[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        echo "📁 $dir 디렉토리를 생성했습니다."
    else
        echo "✅ $dir 디렉토리 존재"
    fi
done

# 환경 변수 설정
export SCRAPY_SETTINGS_MODULE=tutorial.settings
echo "⚙️ 환경 변수 설정 완료: SCRAPY_SETTINGS_MODULE=$SCRAPY_SETTINGS_MODULE"

# 설정 완료 메시지
echo ""
echo "🎉 환경 설정이 완료되었습니다!"
echo ""
echo "🚀 다음 명령어들을 사용할 수 있습니다:"
echo ""
echo "   📋 기본 크롤링:"
echo "   scrapy crawl quotes_spider -o outputs/json/basic_quotes.json"
echo ""
echo "   🔄 ItemLoader 사용:"
echo "   scrapy crawl complex_quotes -o outputs/json/complex_quotes.json"
echo ""
echo "   🕵️ User-Agent 회전:"
echo "   scrapy crawl useragent_spider -o outputs/json/useragent_test.json"
echo ""
echo "   🛡️ 윤리적 크롤링:"
echo "   scrapy crawl ethical_spider -o outputs/json/ethical_crawling.json"
echo ""
echo "   🎮 데모 실행:"
echo "   python ../demos/advanced_features/useragent_demo.py"
echo ""
echo "Happy Scraping! 🕷️✨"

cd "$PROJECT_ROOT"
