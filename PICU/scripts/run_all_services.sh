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

# 통합 환경 설정 (PostgreSQL 기본값 포함)
if [ -f "$PROJECT_ROOT/scripts/setup_env.sh" ]; then
    source "$PROJECT_ROOT/scripts/setup_env.sh"
fi

# 가상환경 확인
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ 가상환경이 없습니다.${NC}"
    echo -e "${YELLOW}먼저 'bash scripts/start.sh'를 실행하여 설치하세요.${NC}"
    exit 1
fi

# 가상환경 활성화
source venv/bin/activate

echo ""
echo -e "${CYAN}╔════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║   CoinTicker 서비스 실행 가이드       ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════╝${NC}"
echo ""

# 입력 받기 함수 (간단하고 안정적인 버전, 'x'로 뒤로가기)
get_user_choice() {
    local prompt_text="$1"
    local raw_input=""
    local choice=""

    # 터미널이 아닌 경우 기본 read 사용
    if [ ! -t 0 ]; then
        read -p "$prompt_text" raw_input
        # 'x' 또는 'X' 체크
        raw_input=$(echo "$raw_input" | tr '[:upper:]' '[:lower:]' | tr -d '[:space:]')
        if [ "$raw_input" = "x" ]; then
            echo "BACK"
            return
        fi
        # 숫자만 추출
        choice=$(echo "$raw_input" | grep -oE '^[0-9]+' | head -1)
        echo "$choice"
        return
    fi

    # 입력 버퍼 비우기
    while read -t 0.1 dummy 2>/dev/null; do :; done || true

    # 기본 read 사용
    read -p "$prompt_text" raw_input

    # 앞뒤 공백 제거 및 소문자 변환
    raw_input=$(echo "$raw_input" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | tr '[:upper:]' '[:lower:]')

    # 'x' 또는 'X' 체크 (뒤로가기)
    if [ "$raw_input" = "x" ]; then
        echo "BACK"
        return
    fi

    # 숫자만 추출 (앞에서부터 연속된 숫자만)
    if [[ "$raw_input" =~ ^[0-9]+ ]]; then
        choice="${BASH_REMATCH[0]}"
    elif [ -z "$raw_input" ]; then
        # 빈 입력
        choice=""
    else
        # 숫자가 아닌 다른 문자
        choice="$raw_input"
    fi

    echo "$choice"
}

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}서비스 실행 옵션${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "  1) 🖥️  GUI 실행"
echo "  2) 🔧 Backend 서버 실행"
echo "  3) 🌐 Frontend 개발 서버 실행"
echo "  4) 🔗 HDFS 연결 테스트"
echo "  5) 📊 MapReduce 실행 (클러스터 모드)"
echo "  6) 📖 실행 가이드 보기 (모든 서비스)"
echo ""
echo -e "${YELLOW}💡 'x'를 입력하면 메인 메뉴로 돌아갑니다${NC}"
echo ""
choice=$(get_user_choice "> ")

# 'x' 키 처리 (뒤로가기)
if [ "$choice" = "BACK" ] || [ "$choice" = "x" ] || [ "$choice" = "X" ]; then
    echo ""
    echo -e "${YELLOW}메인 메뉴로 돌아갑니다...${NC}"
    echo ""
    exit 0
fi

# 빈 입력 처리
if [ -z "$choice" ]; then
    echo ""
    echo -e "${RED}❌ 선택을 입력해주세요.${NC}"
    exit 1
fi

# 숫자가 아닌 경우 처리
if ! [[ "$choice" =~ ^[0-9]+$ ]]; then
    echo ""
    echo -e "${RED}❌ 잘못된 선택입니다. (1-6 또는 x: 뒤로가기)${NC}"
    exit 1
fi

# 숫자 범위 확인
if [ "$choice" -lt 1 ] || [ "$choice" -gt 6 ]; then
    echo ""
    echo -e "${RED}❌ 잘못된 선택입니다. (1-6 또는 x: 뒤로가기)${NC}"
    exit 1
fi

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
        echo -e "${GREEN}HDFS 연결 테스트 실행 중...${NC}"
        if [ -f "$PROJECT_ROOT/cointicker/tests/test_hdfs_connection.py" ]; then
            python "$PROJECT_ROOT/cointicker/tests/test_hdfs_connection.py"
        else
            echo -e "${RED}❌ HDFS 연결 테스트 스크립트를 찾을 수 없습니다.${NC}"
        fi
        ;;
    5)
        echo -e "${GREEN}MapReduce 실행 중...${NC}"
        echo -e "${YELLOW}💡 'x'를 입력하면 뒤로가기${NC}"
        input_path=$(get_user_choice "> 입력 경로 (기본: /user/cointicker/raw, x: 뒤로가기): ")
        if [ "$input_path" = "BACK" ] || [ "$input_path" = "x" ] || [ "$input_path" = "X" ]; then
            echo ""
            echo -e "${YELLOW}뒤로가기...${NC}"
            exit 0
        fi
        input_path=${input_path:-/user/cointicker/raw}

        output_path=$(get_user_choice "> 출력 경로 (기본: /user/cointicker/cleaned, x: 뒤로가기): ")
        if [ "$output_path" = "BACK" ] || [ "$output_path" = "x" ] || [ "$output_path" = "X" ]; then
            echo ""
            echo -e "${YELLOW}뒤로가기...${NC}"
            exit 0
        fi
        output_path=${output_path:-/user/cointicker/cleaned}

        if [ -f "$PROJECT_ROOT/cointicker/scripts/run_mapreduce.sh" ]; then
            bash "$PROJECT_ROOT/cointicker/scripts/run_mapreduce.sh" "$input_path" "$output_path"
        else
            echo -e "${RED}❌ MapReduce 스크립트를 찾을 수 없습니다.${NC}"
        fi
        ;;
    6)
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

        # --- Backend ---
        BACKEND_PORT_FILE="$PROJECT_ROOT/cointicker/config/.backend_port"
        if [ -f "$BACKEND_PORT_FILE" ]; then
            BACKEND_PORT=$(cat "$BACKEND_PORT_FILE")
            echo "  - Backend API: http://localhost:$BACKEND_PORT"
            echo "  - Backend Docs: http://localhost:$BACKEND_PORT/docs"
        else
            echo "  - Backend API: http://localhost:5000 (기본값, 실제 포트는 다를 수 있음)"
            echo "  - Backend Docs: http://localhost:5000/docs"
        fi

        # --- Frontend ---
        # Frontend 포트는 run_dev.sh 스크립트에서 결정됩니다. 기본값은 3000입니다.
        # 스크립트 실행 시 출력되는 주소를 확인하세요.
        FRONTEND_PORT="3000"
        echo "  - Frontend: http://localhost:$FRONTEND_PORT (기본값, 실제 포트는 다를 수 있음)"

        # --- Hadoop ---
        echo "  - Hadoop NameNode: http://localhost:9870 (기본값)"
        echo "  - Hadoop ResourceManager: http://localhost:8088 (기본값)"
        echo ""
        echo -e "${YELLOW}참고:${NC}"
        echo "  - Hadoop 포트는 실제 설정(hdfs-site.xml, yarn-site.xml)에 따라 다를 수 있습니다."
        echo "  - Kafka, Scrapy, Selenium은 이 프로젝트에서 별도의 독립 웹 UI를 제공하지 않습니다."
        echo "  - Scrapy 작업은 GUI의 '제어' 탭 또는 Backend API를 통해 모니터링할 수 있습니다."
        echo ""
        echo -e "${CYAN}추가 테스트 및 도구:${NC}"
        echo "  - HDFS 연결 테스트: python cointicker/tests/test_hdfs_connection.py"
        echo "  - MapReduce (클러스터): bash cointicker/scripts/run_mapreduce.sh [INPUT] [OUTPUT]"
        echo "  - MapReduce (로컬): bash cointicker/worker-nodes/mapreduce/run_cleaner.sh"
        echo "  - 전체 테스트: bash cointicker/tests/run_all_tests.sh"
        echo "  - 통합 테스트: bash cointicker/tests/run_integration_tests.sh"
        echo ""
        echo -e "${YELLOW}각 터미널에서 위 명령어를 실행하세요.${NC}"
        ;;
    *)
        echo -e "${RED}❌ 잘못된 선택입니다. (1-6 또는 x: 뒤로가기)${NC}"
        exit 1
        ;;
esac

