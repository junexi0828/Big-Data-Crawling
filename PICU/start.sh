#!/bin/bash
# PICU 프로젝트 통합 설치 및 실행 스크립트
# 사용자가 처음 접속했을 때 실행하는 메인 스크립트

set -e

# 색상 정의
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# 프로젝트 루트
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_ROOT"

echo ""
echo -e "${BOLD}${CYAN}╔════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${CYAN}║   PICU 프로젝트 통합 설치 마법사       ║${NC}"
echo -e "${BOLD}${CYAN}╚════════════════════════════════════════╝${NC}"
echo ""

# 가상환경 확인
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  가상환경이 없습니다.${NC}"
    echo -e "${BLUE}통합 설치 마법사를 실행합니다...${NC}"
    echo ""

    # Python 경로 확인
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        echo -e "${RED}❌ Python을 찾을 수 없습니다.${NC}"
        exit 1
    fi

    # 통합 설치 마법사 실행
    INSTALLER_SCRIPT="$PROJECT_ROOT/cointicker/gui/installer/unified_installer.py"

    if [ -f "$INSTALLER_SCRIPT" ]; then
        $PYTHON_CMD "$INSTALLER_SCRIPT"
    else
        echo -e "${RED}❌ 통합 설치 마법사를 찾을 수 없습니다.${NC}"
        echo -e "${YELLOW}대신 기본 설치를 진행합니다...${NC}"
        # 기본 설치 (가상환경 생성 및 의존성 설치)
        python3 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
        echo -e "${GREEN}✅ 기본 설치 완료!${NC}"
    fi
else
    # 가상환경이 있으면 바로 GUI 실행 옵션 제공
    source venv/bin/activate

    echo -e "${GREEN}✅ 가상환경이 이미 설정되어 있습니다.${NC}"
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}실행 옵션을 선택하세요${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "  1) 🖥️  GUI 애플리케이션 실행"
    echo "  2) 🔧 통합 설치 마법사 실행 (재설치)"
    echo "  3) 🧪 전체 시스템 테스트"
    echo "  4) 🎯 서비스 실행 가이드"
    echo "  5) 📋 프로젝트 정보 보기"
    echo "  6) ❌ 종료"
    echo ""
    read -p "선택 (1-6): " choice

    case $choice in
        1)
            echo ""
            echo -e "${GREEN}GUI 애플리케이션을 실행합니다...${NC}"
            echo ""
            bash "$PROJECT_ROOT/scripts/run_gui.sh"
            ;;
        2)
            echo ""
            echo -e "${GREEN}통합 설치 마법사를 실행합니다...${NC}"
            echo ""
            python "$PROJECT_ROOT/cointicker/gui/installer/unified_installer.py"
            ;;
        3)
            echo ""
            echo -e "${GREEN}전체 시스템 테스트를 시작합니다...${NC}"
            echo ""
            bash "$PROJECT_ROOT/scripts/test_user_flow.sh"
            ;;
        4)
            echo ""
            echo -e "${GREEN}서비스 실행 가이드를 표시합니다...${NC}"
            echo ""
            bash "$PROJECT_ROOT/scripts/run_all_services.sh"
            ;;
        5)
            echo ""
            echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo -e "${CYAN}프로젝트 정보${NC}"
            echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo ""
            echo -e "${BOLD}PICU 프로젝트${NC}"
            echo "  - Personal Investment & Cryptocurrency Understanding"
            echo ""
            echo -e "${BOLD}주요 구성 요소:${NC}"
            echo "  • CoinTicker - 암호화폐 시장 동향 분석 시스템"
            echo "  • GUI - 통합 관리 대시보드"
            echo "  • Backend API - FastAPI 기반 REST API"
            echo "  • Frontend - React 기반 웹 대시보드"
            echo ""
            echo -e "${BOLD}문서:${NC}"
            echo "  • README.md - 프로젝트 메인 문서"
            echo "  • SCRIPTS_README.md - 스크립트 가이드"
            echo "  • PICU_docs/ - 프로젝트 문서"
            echo ""
            echo -e "${BOLD}빠른 시작:${NC}"
            echo "  bash start.sh"
            echo ""
            ;;
        6)
            echo ""
            echo -e "${YELLOW}종료합니다.${NC}"
            echo ""
            exit 0
            ;;
        *)
            echo ""
            echo -e "${RED}❌ 잘못된 선택입니다.${NC}"
            echo ""
            exit 1
            ;;
    esac
fi

