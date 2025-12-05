#!/bin/bash
# ==============================================================================
# 스파이더 테스트 스크립트 (스크래피 독립 모드)
# ==============================================================================
# 개별 스파이더를 실행하고 데이터 수집 결과를 확인합니다.
#
# 📌 스크래피 독립 테스트 모드:
#   - Kafka/HDFS 연결 실패는 정상 동작으로 처리 (에러로 카운트하지 않음)
#   - 스크래피 자체의 데이터 수집 성공 여부만 확인
#   - 로컬 임시 파일(data/temp/)에서도 데이터 수집 확인
#
# 사용법:
#   bash scripts/run_spider_test.sh [spider_name] [options]
#
# 예제:
#   bash scripts/run_spider_test.sh upbit_trends
#   bash scripts/run_spider_test.sh upbit_trends --timeout 60
#   bash scripts/run_spider_test.sh all  # 모든 스파이더 실행
#
# 옵션:
#   --timeout N    타임아웃 시간 (초, 기본값: 30)
#   --log-level    로그 레벨 (INFO, DEBUG, WARNING, 기본값: INFO)
#   --output-dir   출력 디렉토리 (기본값: tests/results/spider_test)
# ==============================================================================

set -e

# 색상 정의
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# 프로젝트 루트 디렉토리
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

# 기본값 설정
SPIDER_NAME=""
TIMEOUT=30
LOG_LEVEL="INFO"
OUTPUT_DIR="$PROJECT_ROOT/tests/results/spider_test"
RUN_ALL=false

# 사용 가능한 스파이더 목록
AVAILABLE_SPIDERS=("upbit_trends" "coinness" "saveticker" "perplexity" "cnn_fear_greed")

# 옵션 파싱
while [[ $# -gt 0 ]]; do
    case $1 in
        --timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        --log-level)
            LOG_LEVEL="$2"
            shift 2
            ;;
        --output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        all|ALL)
            RUN_ALL=true
            SPIDER_NAME="all"
            shift
            ;;
        -*)
            echo -e "${RED}알 수 없는 옵션: $1${NC}"
            exit 1
            ;;
        *)
            SPIDER_NAME="$1"
            shift
            ;;
    esac
done

# 스파이더 이름이 없으면 사용법 출력
if [ -z "$SPIDER_NAME" ]; then
    echo -e "${BOLD}스파이더 테스트 스크립트${NC}"
    echo ""
    echo "사용법: $0 [spider_name] [options]"
    echo ""
    echo "사용 가능한 스파이더:"
    for spider in "${AVAILABLE_SPIDERS[@]}"; do
        echo "  - $spider"
    done
    echo "  - all (모든 스파이더 실행)"
    echo ""
    echo "옵션:"
    echo "  --timeout N      타임아웃 시간 (초, 기본값: 30)"
    echo "  --log-level LVL  로그 레벨 (INFO, DEBUG, WARNING, 기본값: INFO)"
    echo "  --output-dir DIR 출력 디렉토리 (기본값: tests/results/spider_test)"
    echo ""
    echo "예제:"
    echo "  $0 upbit_trends"
    echo "  $0 upbit_trends --timeout 60 --log-level DEBUG"
    echo "  $0 all"
    exit 1
fi

# 출력 디렉토리 생성
mkdir -p "$OUTPUT_DIR"

# 가상환경 확인 및 활성화
if [ -d "venv" ]; then
    source venv/bin/activate
    echo -e "${GREEN}✅ 가상환경 활성화${NC}"
elif [ -d "../venv" ]; then
    source ../venv/bin/activate
    echo -e "${GREEN}✅ 가상환경 활성화${NC}"
else
    echo -e "${YELLOW}⚠️  가상환경을 찾을 수 없습니다. 시스템 Python을 사용합니다.${NC}"
fi

# PYTHONPATH 설정 (shared 디렉토리 포함)
export PYTHONPATH="$PROJECT_ROOT/worker-nodes:$PROJECT_ROOT/shared:$PROJECT_ROOT:$PYTHONPATH"

# Scrapy 프로젝트 디렉토리
SPIDER_DIR="$PROJECT_ROOT/worker-nodes/cointicker"

if [ ! -d "$SPIDER_DIR" ]; then
    echo -e "${RED}❌ Scrapy 프로젝트 디렉토리를 찾을 수 없습니다: $SPIDER_DIR${NC}"
    exit 1
fi

# timeout 명령어 확인
if command -v gtimeout &> /dev/null; then
    TIMEOUT_CMD="gtimeout"
elif command -v timeout &> /dev/null; then
    TIMEOUT_CMD="timeout"
else
    TIMEOUT_CMD=""
fi

# 스파이더 실행 함수
# 반환값: 0=성공, 1=실패
# 전역 변수: ITEMS_COUNT (아이템 수)
run_spider() {
    local spider=$1
    local output_file="$OUTPUT_DIR/${spider}_$(date +%Y%m%d_%H%M%S).log"

    # 전역 변수 초기화
    ITEMS_COUNT=0

    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}스파이더 실행: ${BOLD}$spider${NC}${CYAN}${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""

    cd "$SPIDER_DIR"

    # logs 디렉토리 생성
    mkdir -p logs

    # 스파이더 실행
    echo -e "${YELLOW}스파이더 실행 중... (타임아웃: ${TIMEOUT}초)${NC}"

    if [ -n "$TIMEOUT_CMD" ]; then
        $TIMEOUT_CMD "$TIMEOUT" scrapy crawl "$spider" -L "$LOG_LEVEL" 2>&1 | tee "$output_file" || SPIDER_EXIT_CODE=$?
    else
        scrapy crawl "$spider" -L "$LOG_LEVEL" 2>&1 | head -200 | tee "$output_file" || SPIDER_EXIT_CODE=$?
    fi

    # 결과 분석
    if [ -f "$output_file" ]; then
        # ============================================
        # 스크래피 독립 테스트: Kafka/HDFS 연결 실패는 정상 동작으로 처리
        # ============================================

        # Kafka/HDFS 연결 실패 확인 (정보로만 표시)
        KAFKA_ERRORS=$(grep -c "Failed to connect Kafka Producer\|kafka.*ERROR\|ERROR.*kafka\|Producer.*ERROR" "$output_file" 2>/dev/null | tr -d '\n' || echo "0")
        HDFS_ERRORS=$(grep -c "Failed to save to HDFS\|HDFS.*ERROR\|ERROR.*HDFS" "$output_file" 2>/dev/null | tr -d '\n' || echo "0")

        # 숫자 검증 (개행 문자 제거 후 검증)
        if ! [[ "$KAFKA_ERRORS" =~ ^[0-9]+$ ]]; then
            KAFKA_ERRORS=0
        fi
        if ! [[ "$HDFS_ERRORS" =~ ^[0-9]+$ ]]; then
            HDFS_ERRORS=0
        fi

        if [ "$KAFKA_ERRORS" -gt 0 ]; then
            echo -e "${YELLOW}💡 Kafka 미실행, 스크래피 독립 모드로 동작 중입니다.${NC}"
        fi
        if [ "$HDFS_ERRORS" -gt 0 ]; then
            echo -e "${YELLOW}💡 HDFS 미실행, 로컬 임시 파일에 저장됩니다.${NC}"
        fi

        # 아이템 수집 확인 (개선된 방법)
        # Scrapy 통계에서 item_scraped_count 추출 (다양한 형식 지원)
        ITEMS_COUNT=$(grep -oE "'item_scraped_count'[:\s]*[0-9]+" "$output_file" 2>/dev/null | grep -oE "[0-9]+" | head -1 || \
                      grep -oE '"item_scraped_count"[:\s]*[0-9]+' "$output_file" 2>/dev/null | grep -oE "[0-9]+" | head -1 || \
                      grep -oE "item_scraped_count[:\s]*[0-9]+" "$output_file" 2>/dev/null | grep -oE "[0-9]+" | head -1 || \
                      echo "0")

        # 숫자 검증 (먼저 수행하여 빈 문자열 방지)
        if ! [[ "$ITEMS_COUNT" =~ ^[0-9]+$ ]]; then
            ITEMS_COUNT=0
        fi

        # 통계를 찾지 못한 경우 로컬 파일 확인
        if [ "$ITEMS_COUNT" -eq 0 ] || [ -z "$ITEMS_COUNT" ]; then
            TEMP_DIR="$SPIDER_DIR/data/temp"
            if [ -d "$TEMP_DIR" ]; then
                # 날짜별 디렉토리에서 최근 파일 찾기
                TODAY=$(date +%Y%m%d)
                DATE_DIR="$TEMP_DIR/$TODAY"

                # 스파이더 이름 매칭 패턴 (예: upbit_trends -> upbit_*.json)
                if [[ "$spider" == "upbit_trends" ]]; then
                    FILE_PATTERN="upbit_*.json"
                elif [[ "$spider" == "cnn_fear_greed" ]]; then
                    FILE_PATTERN="fear_greed_*.json"
                elif [[ "$spider" == "perplexity" ]]; then
                    FILE_PATTERN="perplexity_*.json"
                else
                    FILE_PATTERN="${spider}_*.json"
                fi

                # 최근 5분 이내 파일 찾기
                if [ -d "$DATE_DIR" ]; then
                    RECENT_FILE=$(find "$DATE_DIR" -name "$FILE_PATTERN" -type f -mmin -5 2>/dev/null | sort -r | head -1)
                else
                    RECENT_FILE=$(find "$TEMP_DIR" -name "$FILE_PATTERN" -type f -mmin -5 2>/dev/null | sort -r | head -1)
                fi

                if [ -n "$RECENT_FILE" ] && [ -f "$RECENT_FILE" ]; then
                    FILE_ITEMS=$(python3 -c "
import json
import sys
try:
    with open('$RECENT_FILE', 'r') as f:
        data = json.load(f)
        if isinstance(data, list):
            print(len(data))
        elif isinstance(data, dict):
            print(1)
        else:
            print(0)
except Exception as e:
    print(0)
" 2>/dev/null || echo "0")

                    # 숫자 검증
                    if [[ "$FILE_ITEMS" =~ ^[0-9]+$ ]] && [ "$FILE_ITEMS" -gt 0 ]; then
                        ITEMS_COUNT="$FILE_ITEMS"
                        echo -e "${GREEN}✅ 로컬 파일에서 아이템 수 확인: $ITEMS_COUNT개${NC}"
                        echo -e "${BLUE}   파일 위치: $RECENT_FILE${NC}"
                    fi
                fi
            fi
        fi

        # 에러 확인 (Kafka/HDFS 연결 실패는 제외)
        ERRORS_COUNT=$(grep "ERROR" "$output_file" 2>/dev/null | grep -v "kafka\|HDFS\|Producer\|Failed to connect\|Failed to save" | wc -l | tr -d ' ' || echo "0")
        WARNINGS_COUNT=$(grep -c "WARNING" "$output_file" 2>/dev/null || echo "0")

        # 숫자 검증
        if ! [[ "$ERRORS_COUNT" =~ ^[0-9]+$ ]]; then
            ERRORS_COUNT=0
        fi
        if ! [[ "$WARNINGS_COUNT" =~ ^[0-9]+$ ]]; then
            WARNINGS_COUNT=0
        fi

        # 결과 출력
        echo ""
        echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${BOLD}스파이더 실행 결과: $spider${NC}"
        echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""

        # 종료 코드 확인
        if [ "${SPIDER_EXIT_CODE:-0}" -ne 0 ]; then
            echo -e "${RED}❌ 스파이더 실행 실패 (종료 코드: ${SPIDER_EXIT_CODE})${NC}"
        elif grep -q "no active project\|crawl command is not available" "$output_file" 2>/dev/null; then
            echo -e "${RED}❌ Scrapy 프로젝트가 활성화되지 않았습니다${NC}"
        elif [ "$ERRORS_COUNT" -gt 0 ]; then
            echo -e "${RED}❌ 스파이더 실행 중 오류 발생 (스크래피 독립 모드)${NC}"
            echo -e "   아이템 수집: ${YELLOW}$ITEMS_COUNT${NC}"
            echo -e "   에러 수: ${RED}$ERRORS_COUNT${NC}"
            echo -e "   경고 수: ${YELLOW}$WARNINGS_COUNT${NC}"
            if [ "$KAFKA_ERRORS" -gt 0 ] || [ "$HDFS_ERRORS" -gt 0 ]; then
                echo ""
                echo -e "${YELLOW}💡 참고:${NC}"
                if [ "$KAFKA_ERRORS" -gt 0 ]; then
                    echo -e "   - Kafka 미실행 (스크래피 독립 모드에서는 정상, 에러로 카운트하지 않음)${NC}"
                fi
                if [ "$HDFS_ERRORS" -gt 0 ]; then
                    echo -e "   - HDFS 미실행 (로컬 임시 파일에 저장됨, 에러로 카운트하지 않음)${NC}"
                fi
            fi
        elif [ "$ITEMS_COUNT" -gt 0 ]; then
            echo -e "${GREEN}✅ 스파이더 실행 완료 (스크래피 독립 모드)${NC}"
            echo -e "   아이템 수집: ${GREEN}$ITEMS_COUNT${NC}"
            echo -e "   에러 수: ${GREEN}$ERRORS_COUNT${NC}"
            echo -e "   경고 수: ${YELLOW}$WARNINGS_COUNT${NC}"
            if [ "$KAFKA_ERRORS" -gt 0 ] || [ "$HDFS_ERRORS" -gt 0 ]; then
                echo ""
                echo -e "${YELLOW}💡 참고:${NC}"
                if [ "$KAFKA_ERRORS" -gt 0 ]; then
                    echo -e "   - Kafka 미실행 (스크래피 독립 모드에서는 정상)${NC}"
                fi
                if [ "$HDFS_ERRORS" -gt 0 ]; then
                    echo -e "   - HDFS 미실행 (로컬 임시 파일에 저장됨)${NC}"
                fi
            fi
        else
            echo -e "${RED}❌ 스파이더 실행 완료했으나 아이템이 수집되지 않았습니다 (스크래피 독립 모드)${NC}"
            echo -e "   아이템 수집: ${RED}0${NC}"
            echo -e "   에러 수: ${YELLOW}$ERRORS_COUNT${NC}"
            echo -e "   경고 수: ${YELLOW}$WARNINGS_COUNT${NC}"
            echo ""
            echo -e "${YELLOW}💡 가능한 원인:${NC}"
            echo -e "   1. 웹사이트 구조 변경"
            echo -e "   2. 네트워크 연결 문제"
            echo -e "   3. 스파이더 파싱 로직 오류"
            echo -e "   4. robots.txt 또는 접근 제한"
            if [ "$KAFKA_ERRORS" -gt 0 ] || [ "$HDFS_ERRORS" -gt 0 ]; then
                echo ""
                echo -e "${YELLOW}💡 참고:${NC}"
                echo -e "   - Kafka/HDFS 연결 실패는 스크래피 독립 모드에서는 정상입니다 (에러로 카운트하지 않음)${NC}"
                echo -e "   - 로컬 임시 파일(data/temp/)에서 데이터를 확인하세요${NC}"
            fi
        fi

        echo ""
        echo -e "출력 파일: ${BLUE}$output_file${NC}"
        echo ""

        # 최근 에러 로그 출력 (있는 경우)
        if [ "$ERRORS_COUNT" -gt 0 ]; then
            echo -e "${RED}최근 에러 로그:${NC}"
            grep "ERROR" "$output_file" | tail -5 | sed 's/^/   /'
            echo ""
        fi

        return ${SPIDER_EXIT_CODE:-0}
    else
        echo -e "${RED}❌ 출력 파일이 생성되지 않았습니다${NC}"
        return 1
    fi
}

# 메인 실행
cd "$PROJECT_ROOT"

TOTAL_SPIDERS=0
SUCCESS_COUNT=0
FAIL_COUNT=0
ITEMS_COUNT=0  # 전역 변수 초기화

if [ "$RUN_ALL" = true ]; then
    # 모든 스파이더 실행
    echo -e "${BOLD}모든 스파이더 실행 모드 (스크래피 독립 모드)${NC}"
    echo ""
    echo -e "${YELLOW}📌 스크래피 독립 테스트 모드:${NC}"
    echo -e "${YELLOW}   - Kafka/HDFS 연결 실패는 정상 동작으로 처리됩니다${NC}"
    echo -e "${YELLOW}   - 스크래피 자체의 데이터 수집 성공 여부만 확인합니다${NC}"
    echo -e "${YELLOW}   - 로컬 임시 파일(data/temp/)에서도 데이터 수집을 확인합니다${NC}"
    echo ""

    for spider in "${AVAILABLE_SPIDERS[@]}"; do
        TOTAL_SPIDERS=$((TOTAL_SPIDERS + 1))
        if run_spider "$spider"; then
            if [ "$ITEMS_COUNT" -gt 0 ]; then
                SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
            else
                FAIL_COUNT=$((FAIL_COUNT + 1))
            fi
        else
            FAIL_COUNT=$((FAIL_COUNT + 1))
        fi
        sleep 2  # 스파이더 간 간격
    done
else
    # 단일 스파이더 실행
    # 스파이더 이름 검증
    if [[ ! " ${AVAILABLE_SPIDERS[@]} " =~ " ${SPIDER_NAME} " ]]; then
        echo -e "${RED}❌ 알 수 없는 스파이더: $SPIDER_NAME${NC}"
        echo ""
        echo "사용 가능한 스파이더:"
        for spider in "${AVAILABLE_SPIDERS[@]}"; do
            echo "  - $spider"
        done
        exit 1
    fi

    TOTAL_SPIDERS=1
    if run_spider "$SPIDER_NAME"; then
        if [ "$ITEMS_COUNT" -gt 0 ]; then
            SUCCESS_COUNT=1
        else
            FAIL_COUNT=1
        fi
    else
        FAIL_COUNT=1
    fi
fi

# 최종 요약
echo ""
echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}테스트 결과 요약 (스크래피 독립 모드)${NC}"
echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "총 스파이더: $TOTAL_SPIDERS"
echo -e "${GREEN}성공 (데이터 수집): $SUCCESS_COUNT${NC}"
echo -e "${RED}실패 (데이터 미수집): $FAIL_COUNT${NC}"
echo ""
echo -e "${YELLOW}💡 참고:${NC}"
echo -e "${YELLOW}   - Kafka/HDFS 연결 실패는 에러로 카운트하지 않았습니다${NC}"
echo -e "${YELLOW}   - 스크래피 자체의 데이터 수집 성공 여부만 평가했습니다${NC}"
echo -e "${YELLOW}   - 로컬 임시 파일(data/temp/)에서도 데이터 수집을 확인했습니다${NC}"
echo ""
echo -e "출력 디렉토리: ${BLUE}$OUTPUT_DIR${NC}"
echo ""

if [ $FAIL_COUNT -eq 0 ]; then
    exit 0
else
    exit 1
fi

