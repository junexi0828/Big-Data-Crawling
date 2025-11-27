#!/bin/bash
# PICU 통합 가상환경 설정 스크립트

set -e

# 색상 정의
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 프로젝트 루트 확인
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_ROOT"

echo "=========================================="
echo "PICU 통합 가상환경 설정"
echo "=========================================="
echo ""

echo -e "${BLUE}[1/4] Python 버전 확인${NC}"
PYTHON_VERSION=$(python3 --version 2>&1)
echo "  $PYTHON_VERSION"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo -e "${RED}❌ Python 3.8 이상이 필요합니다.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python 버전 확인 완료${NC}"
echo ""

echo -e "${BLUE}[2/4] 가상환경 생성${NC}"
if [ ! -d "venv" ]; then
    echo "  가상환경 생성 중..."
    python3 -m venv venv
    echo -e "${GREEN}✅ 가상환경 생성 완료${NC}"
else
    echo "  가상환경이 이미 존재합니다."
fi
echo ""

echo -e "${BLUE}[3/4] 가상환경 활성화${NC}"
source venv/bin/activate
echo -e "${GREEN}✅ 가상환경 활성화 완료: $VIRTUAL_ENV${NC}"
echo ""

echo -e "${BLUE}[4/4] 의존성 설치${NC}"
if [ -f "requirements.txt" ]; then
    echo "  pip 업그레이드 중..."
    pip install --upgrade pip > /dev/null 2>&1

    echo "  requirements.txt 의존성 설치 중..."
    pip install -r requirements.txt
    echo -e "${GREEN}✅ 의존성 설치 완료${NC}"
else
    echo -e "${RED}❌ requirements.txt 파일을 찾을 수 없습니다.${NC}"
    exit 1
fi
echo ""

echo "=========================================="
echo -e "${GREEN}설정이 완료되었습니다!${NC}"
echo "=========================================="
echo ""
echo "가상환경 활성화:"
echo "  source venv/bin/activate"
echo ""
echo "설치 마법사 실행:"
echo "  python cointicker/gui/installer/installer_cli.py"
echo ""
echo "GUI 애플리케이션 실행:"
echo "  python cointicker/gui/main.py"
echo ""

