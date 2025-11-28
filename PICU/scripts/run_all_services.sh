#!/bin/bash
# 모든 서비스 실행 가이드 스크립트
# CLI 버전 가이드 스크립트입니다.
set -e

# 색상 정의
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# 프로젝트 루트 (스크립트 디렉토리에서 상위로)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "=========================================="
echo "CoinTicker 서비스 실행 가이드"
echo "=========================================="
echo ""

# 가상환경 확인
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ 가상환경이 없습니다.${NC}"
    echo -e "${YELLOW}먼저 'bash scripts/start.sh'를 실행하여 설치하세요.${NC}"
    exit 1
fi

# 가상환경 활성화
source venv/bin/activate

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}서비스 실행 옵션${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "1. GUI 실행"
echo "2. Backend 서버 실행"
echo "3. Frontend 개발 서버 실행"
echo "4. 실행 가이드 보기 (모든 서비스)"
echo ""
read -p "선택하세요 (1-4): " choice

case $choice in
    1)
        echo -e "${GREEN}GUI 실행 중...${NC}"
        bash "$PROJECT_ROOT/scripts/run_gui.sh"
        ;;
    2)
        echo -e "${GREEN}Backend 서버 실행 중...${NC}"
        bash "$PROJECT_ROOT/cointicker/backend/scripts/run_server.sh"
        ;;
    3)
        echo -e "${GREEN}Frontend 개발 서버 실행 중...${NC}"
        bash "$PROJECT_ROOT/cointicker/frontend/scripts/run_dev.sh"
        ;;
    4)
        echo ""
        echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${CYAN}모든 서비스 실행 가이드${NC}"
        echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        echo -e "${YELLOW}3개의 터미널이 필요합니다.${NC}"
        echo ""
        echo -e "${CYAN}터미널 1 - GUI:${NC}"
        echo "  cd \"$PROJECT_ROOT\""
        echo "  source venv/bin/activate"
        echo "  bash scripts/run_gui.sh"
        echo ""
        echo -e "${CYAN}터미널 2 - Backend:${NC}"
        echo "  cd \"$PROJECT_ROOT\""
        echo "  source venv/bin/activate"
        echo "  bash cointicker/backend/scripts/run_server.sh"
        echo ""
        echo -e "${CYAN}터미널 3 - Frontend:${NC}"
        echo "  cd \"$PROJECT_ROOT\""
        echo "  bash cointicker/frontend/scripts/run_dev.sh"
        echo ""
        echo -e "${GREEN}접속 주소:${NC}"
        echo "  - GUI: 로컬 실행"
        echo "  - Backend API: http://localhost:5000"
        echo "  - Backend Docs: http://localhost:5000/docs"
        echo "  - Frontend: http://localhost:3000"
        echo ""
        echo -e "${YELLOW}각 터미널에서 위 명령어를 실행하세요.${NC}"
        ;;
    *)
        echo -e "${RED}잘못된 선택입니다.${NC}"
        exit 1
        ;;
esac

