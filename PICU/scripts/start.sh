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

# 프로젝트 루트 (scripts/ 디렉토리에서 상위로)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
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

        # requirements 파일 찾기 (우선순위: requirements.txt > requirements/dev.txt)
        if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
            pip install -r "$PROJECT_ROOT/requirements.txt"
        elif [ -f "$PROJECT_ROOT/requirements/dev.txt" ]; then
            pip install -r "$PROJECT_ROOT/requirements/dev.txt"
        else
            echo -e "${RED}❌ requirements 파일을 찾을 수 없습니다.${NC}"
            exit 1
        fi
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
    echo "  3) 🧪 사용자 흐름 테스트 (User Flow Test)"
    echo "  4) 🧪 통합 테스트 (Integration Test)"
    echo "  5) 🧪 자동 테스트 (Automated Test)"
    echo "  6) 🔗 HDFS 클러스터 연결 테스트"
    echo "  7) 🎯 서비스 실행 가이드"
    echo "  8) 📋 기업소개 및 프로젝트 정보 보기"
    echo "  9) ❌ 종료"
    echo ""
    read -p "선택 (1-9): " choice

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
            echo -e "${GREEN}사용자 흐름 테스트 (User Flow Test)를 시작합니다...${NC}"
            echo ""
            bash "$PROJECT_ROOT/scripts/test_user_flow.sh"
            ;;
        4)
            echo ""
            echo -e "${GREEN}통합 테스트 (Integration Test)를 시작합니다...${NC}"
            echo ""
            if [ -f "$PROJECT_ROOT/cointicker/tests/run_integration_tests.sh" ]; then
                bash "$PROJECT_ROOT/cointicker/tests/run_integration_tests.sh"
            else
                echo -e "${RED}❌ 통합 테스트 스크립트를 찾을 수 없습니다.${NC}"
            fi
            ;;
        5)
            echo ""
            echo -e "${GREEN}자동 테스트 (Automated Test)를 시작합니다...${NC}"
            echo ""
            if [ -f "$PROJECT_ROOT/cointicker/tests/run_all_tests.sh" ]; then
                bash "$PROJECT_ROOT/cointicker/tests/run_all_tests.sh"
            else
                echo -e "${RED}❌ 자동 테스트 스크립트를 찾을 수 없습니다.${NC}"
            fi
            ;;
        6)
            echo ""
            echo -e "${GREEN}HDFS 클러스터 연결 테스트를 시작합니다...${NC}"
            echo ""
            if [ -f "$PROJECT_ROOT/cointicker/tests/test_hdfs_connection.py" ]; then
                python "$PROJECT_ROOT/cointicker/tests/test_hdfs_connection.py"
            else
                echo -e "${RED}❌ HDFS 클러스터 연결 테스트 스크립트를 찾을 수 없습니다.${NC}"
            fi
            ;;
        7)
            echo ""
            echo -e "${GREEN}서비스 실행 가이드를 표시합니다...${NC}"
            echo ""
            bash "$PROJECT_ROOT/scripts/run_all_services.sh"
            ;;
        8)
            echo ""
            echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo -e "${CYAN}기업소개 및 프로젝트 정보${NC}"
            echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo ""
            echo -e "${BOLD}CoinTicker - AI 기반 암호화폐 투자 인사이트 플랫폼${NC}"
            echo ""
            echo -e "${BOLD}주요 구성 요소:${NC}"
            echo "  • CoinTicker - 암호화폐 시장 동향 분석 시스템"
            echo "  • GUI - 통합 관리 대시보드"
            echo "  • Backend API - FastAPI 기반 REST API"
            echo "  • Frontend - React 기반 웹 대시보드"
            echo ""
            echo -e "${BOLD}프로젝트 정보:${NC}"
            echo "  • PICU - Personal Investment & Cryptocurrency Understanding"
            echo ""
            echo -e "${BOLD}문서:${NC}"
            echo "  • README.md - 프로젝트 메인 문서"
            echo "  • SCRIPTS_README.md - 스크립트 가이드"
            echo "  • PICU_docs/ - 프로젝트 문서"
            echo ""
            echo -e "${BOLD}기업소개 페이지:${NC}"
            echo "  https://eieconcierge.com/cointicker/"
            echo ""

            # 웹 브라우저로 기업소개 페이지 열기
            if command -v open &> /dev/null; then
                # macOS
                echo -e "${BLUE}기업소개 페이지를 브라우저에서 엽니다...${NC}"
                open "https://eieconcierge.com/cointicker/"
            elif command -v xdg-open &> /dev/null; then
                # Linux
                echo -e "${BLUE}기업소개 페이지를 브라우저에서 엽니다...${NC}"
                xdg-open "https://eieconcierge.com/cointicker/"
            elif command -v start &> /dev/null; then
                # Windows (Git Bash)
                echo -e "${BLUE}기업소개 페이지를 브라우저에서 엽니다...${NC}"
                start "https://eieconcierge.com/cointicker/"
            else
                echo -e "${YELLOW}⚠️  브라우저를 자동으로 열 수 없습니다.${NC}"
                echo -e "${YELLOW}   다음 URL을 직접 방문하세요:${NC}"
                echo -e "${CYAN}   https://eieconcierge.com/cointicker/${NC}"
            fi
            echo ""
            ;;
        9)
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

