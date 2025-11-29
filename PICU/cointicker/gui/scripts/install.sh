#!/bin/bash
# CoinTicker GUI 설치 스크립트

set -e

echo "=========================================="
echo "CoinTicker GUI 설치 스크립트"
echo "=========================================="
echo ""

# 색상 정의
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 프로젝트 루트 확인
# gui/scripts/install.sh -> gui/ -> cointicker/ -> PICU/
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${YELLOW}[1/5] Python 버전 확인${NC}"
PYTHON_VERSION=$(python3 --version 2>&1)
echo "  $PYTHON_VERSION"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo -e "${RED}❌ Python 3.8 이상이 필요합니다.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python 버전 확인 완료${NC}"
echo ""

echo -e "${YELLOW}[2/5] 가상환경 확인${NC}"
if [ ! -d "venv" ]; then
    echo "  가상환경 생성 중..."
    python3 -m venv venv
    echo -e "${GREEN}✅ 가상환경 생성 완료${NC}"
else
    echo "  가상환경이 이미 존재합니다."
fi
echo ""

echo -e "${YELLOW}[3/5] 가상환경 활성화${NC}"
source venv/bin/activate
echo -e "${GREEN}✅ 가상환경 활성화 완료${NC}"
echo ""

echo -e "${YELLOW}[4/5] pip 업그레이드${NC}"
pip install --upgrade pip > /dev/null 2>&1
echo -e "${GREEN}✅ pip 업그레이드 완료${NC}"
echo ""

echo -e "${YELLOW}[5/5] 의존성 설치${NC}"
REQUIREMENTS_FILE="$PROJECT_ROOT/requirements.txt"
if [ -f "$REQUIREMENTS_FILE" ]; then
    pip install -r "$REQUIREMENTS_FILE"
    echo -e "${GREEN}✅ 의존성 설치 완료${NC}"
else
    echo -e "${RED}❌ requirements.txt 파일을 찾을 수 없습니다: $REQUIREMENTS_FILE${NC}"
    exit 1
fi
echo ""

echo "=========================================="
echo -e "${GREEN}설치가 완료되었습니다!${NC}"
echo "=========================================="
echo ""
echo "다음 명령어로 GUI를 실행하세요:"
echo "  python cointicker/gui/main.py"
echo "  또는: bash scripts/start.sh"
echo ""
echo "또는 설치 마법사를 실행하세요:"
echo "  python gui/installer/installer_cli.py  # CLI 버전 (권장)"
echo "  python gui/installer/installer_gui.py  # GUI 버전 (PyQt5 필요)"
echo ""

