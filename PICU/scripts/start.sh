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
# bigdata 루트 (PICU의 부모 디렉토리, hadoop_project가 있는 위치)
BIGDATA_ROOT="$(cd "$PROJECT_ROOT/.." && pwd)"
cd "$PROJECT_ROOT"

# ==================================================
# HDFS/Java/Hadoop 환경 변수 동적 설정
# ==================================================
# 1. Java 경로 설정 (macOS 동적 감지, 실패 시 하드코딩 경로 사용)
if [ -x "/usr/libexec/java_home" ]; then
    export JAVA_HOME=$(/usr/libexec/java_home)
else
    echo -e "\033[1;33m⚠️  /usr/libexec/java_home 를 찾을 수 없습니다. 하드코딩된 Java 경로를 사용합니다.\033[0m"
    export JAVA_HOME="/opt/homebrew/Cellar/openjdk@17/17.0.16/libexec/openjdk.jdk/Contents/Home"
fi

# 2. Hadoop 경로 설정 (path_utils.py의 범용 경로 찾기 사용)
# 먼저 간단한 경로 확인, 없으면 path_utils.py로 시스템 경로까지 포함하여 찾기
if [ -d "$BIGDATA_ROOT/hadoop_project/hadoop-3.4.1" ]; then
    export HADOOP_HOME="$BIGDATA_ROOT/hadoop_project/hadoop-3.4.1"
    echo -e "\033[0;36m   - HADOOP_HOME (프로젝트 경로): $HADOOP_HOME\033[0m"
elif [ -d "$PROJECT_ROOT/hadoop_project/hadoop-3.4.1" ]; then
    export HADOOP_HOME="$PROJECT_ROOT/hadoop_project/hadoop-3.4.1"
    echo -e "\033[0;36m   - HADOOP_HOME (프로젝트 경로): $HADOOP_HOME\033[0m"
else
    # path_utils.py를 사용하여 시스템 경로까지 포함하여 찾기
    if command -v python3 &> /dev/null || command -v python &> /dev/null; then
        PYTHON_CMD=$(command -v python3 2>/dev/null || command -v python 2>/dev/null)
        # path_utils.py의 get_hadoop_home() 함수 호출
        HADOOP_PATH=$($PYTHON_CMD -c "
import sys
sys.path.insert(0, '$PROJECT_ROOT')
try:
    from shared.path_utils import get_hadoop_home
    hadoop_path = get_hadoop_home()
    if hadoop_path:
        print(str(hadoop_path))
except Exception:
    pass
" 2>/dev/null)

        if [ -n "$HADOOP_PATH" ] && [ -d "$HADOOP_PATH" ]; then
            export HADOOP_HOME="$HADOOP_PATH"
            echo -e "\033[0;32m✅ HADOOP_HOME 자동 감지 (path_utils): $HADOOP_HOME\033[0m"
        else
            echo -e "\033[1;33m⚠️  Hadoop 경로를 찾을 수 없습니다. path_utils.py가 Python 실행 시 자동으로 찾을 것입니다.\033[0m"
            unset HADOOP_HOME
        fi
    else
        echo -e "\033[1;33m⚠️  Python을 찾을 수 없어 Hadoop 경로를 자동으로 찾을 수 없습니다.\033[0m"
        echo -e "\033[0;36m   Python 실행 시 path_utils.py가 자동으로 찾을 것입니다.\033[0m"
        unset HADOOP_HOME
    fi
fi

# 3. Hadoop Classpath 설정
if [ -n "$HADOOP_HOME" ] && [ -x "$HADOOP_HOME/bin/hadoop" ]; then
    export CLASSPATH=$($HADOOP_HOME/bin/hadoop classpath --glob)
    echo -e "\033[0;32m✅ Hadoop Classpath 설정 완료\033[0m"
elif [ -n "$HADOOP_HOME" ]; then
    echo -e "\033[1;33m⚠️  Hadoop 실행 파일을 찾을 수 없습니다: $HADOOP_HOME/bin/hadoop\033[0m"
    echo -e "\033[0;36m   path_utils.py가 자동으로 찾을 것입니다.\033[0m"
fi

# 4. Native Library 경로 설정 (libjvm.dylib, libhdfs.dylib)
# PyArrow가 libhdfs.dylib를 직접 찾도록 경로를 지정 (가장 확실한 방법)
if [ -n "$HADOOP_HOME" ] && [ -d "$HADOOP_HOME/lib/native" ]; then
    export ARROW_LIBHDFS_DIR="$HADOOP_HOME/lib/native"
    # macOS에서는 DYLD_LIBRARY_PATH도 설정
    if [[ "$OSTYPE" == "darwin"* ]]; then
        current_dyld="${DYLD_LIBRARY_PATH:-}"
        if [[ "$current_dyld" != *"$ARROW_LIBHDFS_DIR"* ]]; then
            export DYLD_LIBRARY_PATH="$JAVA_HOME/lib/server:$ARROW_LIBHDFS_DIR${current_dyld:+:$current_dyld}"
        fi
    fi
    echo -e "\033[0;32m✅ Java, Hadoop 환경 변수 설정 완료.\033[0m"
    if [ -n "$HADOOP_HOME" ]; then
        echo -e "\033[0;36m   - HADOOP_HOME: $HADOOP_HOME\033[0m"
    fi
    echo -e "\033[0;36m   - ARROW_LIBHDFS_DIR: $ARROW_LIBHDFS_DIR\033[0m"
elif [ -n "$HADOOP_HOME" ]; then
    echo -e "\033[1;33m⚠️  Hadoop native library 디렉토리를 찾을 수 없습니다: $HADOOP_HOME/lib/native\033[0m"
    echo -e "\033[0;32m✅ Java, Hadoop 환경 변수 설정 완료 (ARROW_LIBHDFS_DIR 제외).\033[0m"
    echo -e "\033[0;36m   - HADOOP_HOME: $HADOOP_HOME\033[0m"
    echo -e "\033[0;36m   - path_utils.py가 자동으로 ARROW_LIBHDFS_DIR을 설정할 것입니다.\033[0m"
else
    echo -e "\033[0;32m✅ Java 환경 변수 설정 완료.\033[0m"
    echo -e "\033[0;36m   - HADOOP_HOME은 path_utils.py가 자동으로 찾을 것입니다.\033[0m"
fi
# ==================================================

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
    # 통합 환경 설정 (PostgreSQL 기본값 포함)
    if [ -f "$PROJECT_ROOT/scripts/setup_env.sh" ]; then
        source "$PROJECT_ROOT/scripts/setup_env.sh"
    fi

    source venv/bin/activate

    # 메뉴 표시 함수
    show_menu() {
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
        echo "  7) 🗄️  DB 테스트 (데이터베이스 적재 상태 확인)"
        echo "  8) 🔄 파이프라인 검증 테스트 (Pipeline Verification)"
        echo "  9) 🎯 서비스 실행 가이드"
        echo " 10) 📋 기업소개 및 프로젝트 정보 보기"
        echo " 11) 📊 24/7 서비스 로그 모니터링 (GUI 종료 후 터미널 모니터링)"
        echo " 12) ❌ 종료"
        echo ""
        echo -e "${YELLOW}💡 'x'를 입력하면 종료됩니다${NC}"
    }

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

    # 메인 루프
    while true; do
        show_menu

        # 사용자 입력 받기
        choice=$(get_user_choice "> ")

        # 빈 입력 처리 (Enter만 누른 경우)
        if [ -z "$choice" ]; then
            echo ""
            echo -e "${YELLOW}⚠️  선택을 입력해주세요.${NC}"
            echo ""
            continue
        fi

        # 'x' 키 처리 (종료)
        if [ "$choice" = "BACK" ] || [ "$choice" = "x" ] || [ "$choice" = "X" ]; then
            echo ""
            echo -e "${YELLOW}프로그램을 종료합니다...${NC}"
            echo ""
            exit 0
        fi

        # 숫자가 아닌 경우 처리
        if ! [[ "$choice" =~ ^[0-9]+$ ]]; then
            echo ""
            echo -e "${RED}❌ 잘못된 선택입니다. (1-12 또는 x: 종료)${NC}"
            echo ""
            # 입력 버퍼 비우기
            while read -t 0.1 dummy 2>/dev/null; do :; done || true
            echo -n "계속하려면 Enter를 누르세요... "
            read dummy
            continue
        fi

        # 숫자 범위 확인
        if [ "$choice" -lt 1 ] || [ "$choice" -gt 12 ]; then
            echo ""
            echo -e "${RED}❌ 잘못된 선택입니다. (1-12 또는 x: 종료)${NC}"
            echo ""
            # 입력 버퍼 비우기
            while read -t 0.1 dummy 2>/dev/null; do :; done || true
            echo -n "계속하려면 Enter를 누르세요... "
            read dummy
            continue
        fi

        case $choice in
            1)
                echo ""
                echo -e "${GREEN}GUI 애플리케이션을 실행합니다...${NC}"
                echo ""
                bash "$PROJECT_ROOT/scripts/run_gui.sh"
                echo ""
                # 입력 버퍼 비우기
                while read -t 0.1 dummy 2>/dev/null; do :; done || true
                echo -n "계속하려면 Enter를 누르세요... "
                read dummy
                ;;
            2)
                echo ""
                echo -e "${GREEN}통합 설치 마법사를 실행합니다...${NC}"
                echo ""
                # PYTHONPATH 설정 (unified_installer.py의 의존성 import를 위해)
                COINTICKER_ROOT="$PROJECT_ROOT/cointicker"
                export PYTHONPATH="$COINTICKER_ROOT:$COINTICKER_ROOT/shared:$COINTICKER_ROOT/worker-nodes:$COINTICKER_ROOT/backend${PYTHONPATH:+:$PYTHONPATH}"
                python "$PROJECT_ROOT/cointicker/gui/installer/unified_installer.py"
                echo ""
                # 입력 버퍼 비우기
                while read -t 0.1 dummy 2>/dev/null; do :; done || true
                echo -n "계속하려면 Enter를 누르세요... "
                read dummy
                ;;
            3)
                echo ""
                echo -e "${GREEN}사용자 흐름 테스트 (User Flow Test)를 시작합니다...${NC}"
                echo ""
                if [ -f "$PROJECT_ROOT/scripts/test_user_flow.sh" ]; then
                    bash "$PROJECT_ROOT/scripts/test_user_flow.sh"
                else
                    echo -e "${RED}❌ 사용자 흐름 테스트 스크립트를 찾을 수 없습니다.${NC}"
                fi
                echo ""
                # 입력 버퍼 비우기
                while read -t 0.1 dummy 2>/dev/null; do :; done || true
                echo -n "계속하려면 Enter를 누르세요... "
                read dummy
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
                echo ""
                # 입력 버퍼 비우기
                while read -t 0.1 dummy 2>/dev/null; do :; done || true
                echo -n "계속하려면 Enter를 누르세요... "
                read dummy
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
                echo ""
                # 입력 버퍼 비우기
                while read -t 0.1 dummy 2>/dev/null; do :; done || true
                echo -n "계속하려면 Enter를 누르세요... "
                read dummy
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
                echo ""
                # 입력 버퍼 비우기
                while read -t 0.1 dummy 2>/dev/null; do :; done || true
                echo -n "계속하려면 Enter를 누르세요... "
                read dummy
                ;;
            7)
                echo ""
                echo -e "${GREEN}DB 테스트 (데이터베이스 적재 상태 확인)를 시작합니다...${NC}"
                echo ""
                if [ -f "$PROJECT_ROOT/scripts/check_db_status.py" ]; then
                    python "$PROJECT_ROOT/scripts/check_db_status.py"
                else
                    echo -e "${RED}❌ DB 테스트 스크립트를 찾을 수 없습니다.${NC}"
                fi
                echo ""
                # 입력 버퍼 비우기
                while read -t 0.1 dummy 2>/dev/null; do :; done || true
                echo -n "계속하려면 Enter를 누르세요... "
                read dummy
                ;;
            8)
                echo ""
                echo -e "${GREEN}파이프라인 검증 테스트를 시작합니다...${NC}"
                echo ""
                if [ -f "$PROJECT_ROOT/scripts/verify_pipeline.py" ]; then
                    python "$PROJECT_ROOT/scripts/verify_pipeline.py"
                else
                    echo -e "${RED}❌ 파이프라인 검증 테스트 스크립트를 찾을 수 없습니다.${NC}"
                fi
                echo ""
                # 입력 버퍼 비우기
                while read -t 0.1 dummy 2>/dev/null; do :; done || true
                echo -n "계속하려면 Enter를 누르세요... "
                read dummy
                ;;
            9)
                echo ""
                echo -e "${GREEN}서비스 실행 가이드를 표시합니다...${NC}"
                echo ""
                bash "$PROJECT_ROOT/scripts/run_all_services.sh"
                echo ""
                # 입력 버퍼 비우기
                while read -t 0.1 dummy 2>/dev/null; do :; done || true
                echo -n "계속하려면 Enter를 누르세요... "
                read dummy
                ;;
            10)
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
                # 입력 버퍼 비우기
                while read -t 0.1 dummy 2>/dev/null; do :; done || true
                echo -n "계속하려면 Enter를 누르세요... "
                read dummy
                ;;
            11)
                echo ""
                echo -e "${GREEN}24/7 서비스 로그 모니터링을 시작합니다...${NC}"
                echo ""
                bash "$PROJECT_ROOT/scripts/monitor_logs.sh"
                echo ""
                # 입력 버퍼 비우기
                while read -t 0.1 dummy 2>/dev/null; do :; done || true
                echo -n "계속하려면 Enter를 누르세요... "
                read dummy
                ;;
            12)
                echo ""
                echo -e "${YELLOW}종료합니다.${NC}"
                echo ""
                exit 0
                ;;
            *)
                echo ""
                echo -e "${RED}❌ 잘못된 선택입니다. (1-12 또는 x: 종료)${NC}"
                echo ""
                # 입력 버퍼 비우기
                while read -t 0.1 dummy 2>/dev/null; do :; done || true
                echo -n "계속하려면 Enter를 누르세요... "
                read dummy
                ;;
        esac
    done
fi

