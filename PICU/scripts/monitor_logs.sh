#!/bin/bash
# 24/7 서비스 로그 모니터링 스크립트
# GUI 종료 후에도 터미널에서 실시간 로그 확인 가능

# 색상 정의
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 프로젝트 루트 찾기
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
COINTICKER_ROOT="$PROJECT_ROOT/cointicker"
LOGS_DIR="$COINTICKER_ROOT/logs"

# 로그 파일 경로
ORCHESTRATOR_LOG="$LOGS_DIR/orchestrator.log"
SCHEDULER_LOG="$LOGS_DIR/scheduler.log"
SCRAPYD_LOG="$LOGS_DIR/com.cointicker.scrapyd.out.log"
ORCHESTRATOR_SERVICE_LOG="$LOGS_DIR/com.cointicker.orchestrator.out.log"

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

# 메뉴 표시 함수
show_menu() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}24/7 서비스 로그 모니터링${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    echo "로그 디렉토리: $LOGS_DIR"
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}모니터링할 로그를 선택하세요${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "  1) Orchestrator 로그 (파이프라인 전체)"
    echo "  2) Scrapyd Scheduler 로그 (크롤링 스케줄링)"
    echo "  3) Scrapyd 서버 로그"
    echo "  4) Orchestrator 서비스 로그 (launchctl)"
    echo "  5) 모든 로그 동시 모니터링"
    echo "  6) 로그 파일 위치 확인"
    echo ""
    echo -e "${YELLOW}💡 'x'를 입력하면 메인 메뉴로 돌아갑니다${NC}"
    echo ""
}

# 메인 루프
while true; do
    show_menu

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
        echo ""
        continue
    fi

    # 숫자가 아닌 경우 처리
    if ! [[ "$choice" =~ ^[0-9]+$ ]]; then
        echo ""
        echo -e "${RED}❌ 잘못된 선택입니다. (1-6 또는 x: 뒤로가기)${NC}"
        echo ""
        continue
    fi

    # 숫자 범위 확인
    if [ "$choice" -lt 1 ] || [ "$choice" -gt 6 ]; then
        echo ""
        echo -e "${RED}❌ 잘못된 선택입니다. (1-6 또는 x: 뒤로가기)${NC}"
        echo ""
        continue
    fi

    case $choice in
        1)
            echo ""
            echo -e "${GREEN}Orchestrator 로그 모니터링 시작...${NC}"
            echo -e "${YELLOW}종료: Ctrl+C (메뉴로 돌아가기)${NC}"
            echo ""
            if [ -f "$ORCHESTRATOR_LOG" ]; then
                # Ctrl+C를 처리하여 메뉴로 돌아가도록 함
                (trap 'exit 0' INT; tail -f "$ORCHESTRATOR_LOG" 2>/dev/null) || true
                echo ""
                echo -e "${YELLOW}모니터링을 종료했습니다.${NC}"
                echo ""
            else
                echo -e "${RED}❌ 로그 파일이 없습니다: $ORCHESTRATOR_LOG${NC}"
                echo "Orchestrator가 실행 중인지 확인하세요."
                echo ""
                # 입력 버퍼 비우기
                while read -t 0.1 dummy 2>/dev/null; do :; done || true
                echo -n "계속하려면 Enter를 누르세요... "
                read dummy
            fi
            ;;
        2)
            echo ""
            echo -e "${GREEN}Scrapyd Scheduler 로그 모니터링 시작...${NC}"
            echo -e "${YELLOW}종료: Ctrl+C (메뉴로 돌아가기)${NC}"
            echo ""
            if [ -f "$SCHEDULER_LOG" ]; then
                # Ctrl+C를 처리하여 메뉴로 돌아가도록 함
                (trap 'exit 0' INT; tail -f "$SCHEDULER_LOG" 2>/dev/null) || true
                echo ""
                echo -e "${YELLOW}모니터링을 종료했습니다.${NC}"
                echo ""
            else
                echo -e "${RED}❌ 로그 파일이 없습니다: $SCHEDULER_LOG${NC}"
                echo "Scheduler가 실행 중인지 확인하세요."
                echo ""
                # 입력 버퍼 비우기
                while read -t 0.1 dummy 2>/dev/null; do :; done || true
                echo -n "계속하려면 Enter를 누르세요... "
                read dummy
            fi
            ;;
        3)
            echo ""
            echo -e "${GREEN}Scrapyd 서버 로그 모니터링 시작...${NC}"
            echo -e "${YELLOW}종료: Ctrl+C (메뉴로 돌아가기)${NC}"
            echo ""
            if [ -f "$SCRAPYD_LOG" ]; then
                # Ctrl+C를 처리하여 메뉴로 돌아가도록 함
                (trap 'exit 0' INT; tail -f "$SCRAPYD_LOG" 2>/dev/null) || true
                echo ""
                echo -e "${YELLOW}모니터링을 종료했습니다.${NC}"
                echo ""
            else
                echo -e "${YELLOW}⚠️ 서비스 로그 파일이 없습니다: $SCRAPYD_LOG${NC}"
                echo "일반 로그 확인 중..."
                if [ -f "$LOGS_DIR/scrapyd.log" ]; then
                    (trap 'exit 0' INT; tail -f "$LOGS_DIR/scrapyd.log" 2>/dev/null) || true
                    echo ""
                    echo -e "${YELLOW}모니터링을 종료했습니다.${NC}"
                    echo ""
                else
                    echo -e "${RED}❌ Scrapyd 로그 파일을 찾을 수 없습니다.${NC}"
                    echo ""
                    # 입력 버퍼 비우기
                    while read -t 0.1 dummy 2>/dev/null; do :; done || true
                    echo -n "계속하려면 Enter를 누르세요... "
                    read dummy
                fi
            fi
            ;;
        4)
            echo ""
            echo -e "${GREEN}Orchestrator 서비스 로그 모니터링 시작...${NC}"
            echo -e "${YELLOW}종료: Ctrl+C (메뉴로 돌아가기)${NC}"
            echo ""
            if [ -f "$ORCHESTRATOR_SERVICE_LOG" ]; then
                # Ctrl+C를 처리하여 메뉴로 돌아가도록 함
                (trap 'exit 0' INT; tail -f "$ORCHESTRATOR_SERVICE_LOG" 2>/dev/null) || true
                echo ""
                echo -e "${YELLOW}모니터링을 종료했습니다.${NC}"
                echo ""
            else
                echo -e "${YELLOW}⚠️ 서비스 로그 파일이 없습니다: $ORCHESTRATOR_SERVICE_LOG${NC}"
                echo "일반 로그 확인 중..."
                if [ -f "$ORCHESTRATOR_LOG" ]; then
                    (trap 'exit 0' INT; tail -f "$ORCHESTRATOR_LOG" 2>/dev/null) || true
                    echo ""
                    echo -e "${YELLOW}모니터링을 종료했습니다.${NC}"
                    echo ""
                else
                    echo -e "${RED}❌ Orchestrator 로그 파일을 찾을 수 없습니다.${NC}"
                    echo ""
                    # 입력 버퍼 비우기
                    while read -t 0.1 dummy 2>/dev/null; do :; done || true
                    echo -n "계속하려면 Enter를 누르세요... "
                    read dummy
                fi
            fi
            ;;
        5)
            echo ""
            echo -e "${GREEN}모든 로그 동시 모니터링 시작...${NC}"
            echo -e "${YELLOW}종료: Ctrl+C (메뉴로 돌아가기)${NC}"
            echo ""
            echo -e "${BLUE}=== Orchestrator ===${NC}"
            echo -e "${BLUE}=== Scheduler ===${NC}"
            echo -e "${BLUE}=== Scrapyd ===${NC}"
            echo ""

            # 여러 로그 파일을 동시에 tail
            if [ -f "$ORCHESTRATOR_LOG" ] && [ -f "$SCHEDULER_LOG" ]; then
                # Ctrl+C를 처리하여 메뉴로 돌아가도록 함
                (trap 'pkill -P $$ tail 2>/dev/null || true; exit 0' INT; tail -f "$ORCHESTRATOR_LOG" "$SCHEDULER_LOG" 2>/dev/null | \
                    awk '/^==> / {gsub(/^==> /, ""); file=$0; next} {print "[" file "] " $0}') || true
                echo ""
                echo -e "${YELLOW}모니터링을 종료했습니다.${NC}"
                echo ""
            else
                echo -e "${RED}❌ 일부 로그 파일이 없습니다.${NC}"
                [ -f "$ORCHESTRATOR_LOG" ] && tail -f "$ORCHESTRATOR_LOG" &
                [ -f "$SCHEDULER_LOG" ] && tail -f "$SCHEDULER_LOG" &
                (trap 'pkill -P $$ tail 2>/dev/null || true; exit 0' INT; wait) || true
                echo ""
                echo -e "${YELLOW}모니터링을 종료했습니다.${NC}"
                echo ""
            fi
            ;;
        6)
            echo ""
            echo -e "${BLUE}로그 파일 위치:${NC}"
            echo ""
            echo "Orchestrator:"
            echo "  - 일반: $ORCHESTRATOR_LOG"
            echo "  - 서비스: $ORCHESTRATOR_SERVICE_LOG"
            echo ""
            echo "Scheduler:"
            echo "  - 일반: $SCHEDULER_LOG"
            echo ""
            echo "Scrapyd:"
            echo "  - 서비스: $SCRAPYD_LOG"
            echo ""
            echo -e "${YELLOW}로그 파일 존재 여부:${NC}"
            [ -f "$ORCHESTRATOR_LOG" ] && echo -e "${GREEN}✓${NC} Orchestrator 로그" || echo -e "${RED}✗${NC} Orchestrator 로그 없음"
            [ -f "$SCHEDULER_LOG" ] && echo -e "${GREEN}✓${NC} Scheduler 로그" || echo -e "${RED}✗${NC} Scheduler 로그 없음"
            [ -f "$ORCHESTRATOR_SERVICE_LOG" ] && echo -e "${GREEN}✓${NC} Orchestrator 서비스 로그" || echo -e "${YELLOW}⚠${NC} Orchestrator 서비스 로그 없음"
            [ -f "$SCRAPYD_LOG" ] && echo -e "${GREEN}✓${NC} Scrapyd 서비스 로그" || echo -e "${YELLOW}⚠${NC} Scrapyd 서비스 로그 없음"
            echo ""
            echo -e "${YELLOW}빠른 모니터링 명령어:${NC}"
            echo "  Orchestrator: tail -f $ORCHESTRATOR_LOG"
            echo "  Scheduler: tail -f $SCHEDULER_LOG"
            echo "  모든 로그: tail -f $LOGS_DIR/*.log"
            echo ""
            # 입력 버퍼 비우기
            while read -t 0.1 dummy 2>/dev/null; do :; done || true
            echo -n "계속하려면 Enter를 누르세요... "
            read dummy
            ;;
        *)
            echo ""
            echo -e "${RED}❌ 잘못된 선택입니다. (1-6 또는 x: 뒤로가기)${NC}"
            echo ""
            continue
            ;;
    esac
done

