#!/bin/bash
# 코인티커 프로젝트 통합 테스트 스크립트
# 모든 테스트를 단계별로 실행하고 결과를 리포트로 생성

set -e  # 오류 발생 시 중단 (옵션에 따라 변경 가능)

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

# 테스트 결과 디렉토리
TEST_RESULTS_DIR="$PROJECT_ROOT/tests/results"
TEST_RESULT_FILE="$TEST_RESULTS_DIR/test_results.txt"
TEST_LOG_FILE="$TEST_RESULTS_DIR/test_log.txt"
mkdir -p "$TEST_RESULTS_DIR"

# 카운터 초기화
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
SKIPPED_TESTS=0

# 옵션 파싱
QUICK_MODE=false
SKIP_ENV_SETUP=false
SKIP_UNIT_TESTS=false
SKIP_INTEGRATION=false
SKIP_PROCESS_FLOW=false
VERBOSE=false

show_help() {
    cat << EOF
코인티커 프로젝트 통합 테스트 스크립트

사용법: $0 [옵션]

옵션:
  -q, --quick           빠른 테스트 모드 (환경 설정 스킵, 기본 테스트만)
  -e, --skip-env        환경 설정 스킵 (가상환경, 의존성)
  -u, --skip-unit      Unit 테스트 스킵
  -i, --skip-integration 통합 테스트 스킵
  -p, --skip-process    프로세스 흐름 테스트 스킵
  -v, --verbose         상세 출력
  -h, --help            도움말 표시

예제:
  $0                    # 전체 테스트 실행
  $0 -q                 # 빠른 테스트
  $0 -u -p              # Unit 및 프로세스 테스트 스킵
EOF
}

# 옵션 파싱
while [[ $# -gt 0 ]]; do
    case $1 in
        -q|--quick)
            QUICK_MODE=true
            SKIP_ENV_SETUP=true
            SKIP_UNIT_TESTS=true
            SKIP_INTEGRATION=true
            SKIP_PROCESS_FLOW=true
            shift
            ;;
        -e|--skip-env)
            SKIP_ENV_SETUP=true
            shift
            ;;
        -u|--skip-unit)
            SKIP_UNIT_TESTS=true
            shift
            ;;
        -i|--skip-integration)
            SKIP_INTEGRATION=true
            shift
            ;;
        -p|--skip-process)
            SKIP_PROCESS_FLOW=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}알 수 없는 옵션: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# 로그 함수
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$TEST_LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$TEST_LOG_FILE"
    ((PASSED_TESTS++))
    ((TOTAL_TESTS++))
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$TEST_LOG_FILE"
    ((FAILED_TESTS++))
    ((TOTAL_TESTS++))
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$TEST_LOG_FILE"
}

log_skip() {
    echo -e "${CYAN}[SKIP]${NC} $1" | tee -a "$TEST_LOG_FILE"
    ((SKIPPED_TESTS++))
}

# 섹션 헤더
section_header() {
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}${CYAN}$1${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

# 테스트 시작
echo ""
echo -e "${BOLD}${CYAN}╔════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${CYAN}║   코인티커 프로젝트 통합 테스트        ║${NC}"
echo -e "${BOLD}${CYAN}╚════════════════════════════════════════╝${NC}"
echo ""
echo "테스트 시작 시간: $(date '+%Y-%m-%d %H:%M:%S')"
echo "프로젝트 루트: $PROJECT_ROOT"
echo "결과 디렉토리: $TEST_RESULTS_DIR"
echo ""

# ============================================
# 1단계: 환경 설정
# ============================================
if [ "$SKIP_ENV_SETUP" = false ]; then
    section_header "1단계: 환경 설정"

    # Python 버전 확인
    log_info "Python 버전 확인 중..."
    PYTHON_VERSION=$(python3 --version 2>&1)
    if python3 --version | grep -q "Python 3"; then
        log_success "Python 버전 확인: $PYTHON_VERSION"
    else
        log_error "Python 3이 필요합니다"
        exit 1
    fi

    # 가상환경 확인 및 생성
    log_info "가상환경 설정 중..."
    if [ -d "venv" ]; then
        source venv/bin/activate 2>/dev/null || {
            log_warning "가상환경 활성화 실패, 재생성합니다"
            rm -rf venv
            python3 -m venv venv
            source venv/bin/activate
        }
    else
        log_info "새 가상환경 생성 중..."
        python3 -m venv venv
        source venv/bin/activate
    fi

    if [ -z "$VIRTUAL_ENV" ]; then
        log_error "가상환경 활성화 실패"
        exit 1
    fi
    log_success "가상환경 활성화 완료: $VIRTUAL_ENV"

    # pip 업그레이드
    log_info "pip 업그레이드 중..."
    pip install --upgrade pip --quiet 2>&1 | tee -a "$TEST_LOG_FILE" || true
    log_success "pip 업그레이드 완료"

    # 의존성 설치
    log_info "의존성 설치 중..."
    if [ ! -f "requirements.txt" ]; then
        log_error "requirements.txt 파일을 찾을 수 없습니다"
        exit 1
    fi

    if pip install -r requirements.txt --quiet 2>&1 | tee -a "$TEST_LOG_FILE"; then
        log_success "의존성 설치 완료"
    else
        log_warning "일부 의존성 설치 실패 (계속 진행)"
        pip install scrapy fastapi sqlalchemy pymysql uvicorn --quiet 2>&1 | tee -a "$TEST_LOG_FILE" || true
    fi
else
    log_skip "환경 설정 스킵됨"
    if [ -d "venv" ]; then
        source venv/bin/activate 2>/dev/null || log_warning "가상환경 활성화 실패"
    fi
fi

# ============================================
# 2단계: 코드 품질 검사
# ============================================
section_header "2단계: 코드 품질 검사"

# Python 문법 검사
log_info "Python 문법 검사 중..."
SYNTAX_ERRORS=0
PYTHON_FILES=0

while IFS= read -r -d '' file; do
    ((PYTHON_FILES++))
    if python3 -m py_compile "$file" 2>/dev/null; then
        if [ "$VERBOSE" = true ]; then
            log_info "  ✅ $(basename "$file")"
        fi
    else
        log_error "문법 오류: $(basename "$file")"
        ((SYNTAX_ERRORS++))
    fi
done < <(find . -name "*.py" -type f ! -path "*/venv/*" ! -path "*/__pycache__/*" ! -path "*/.git/*" -print0)

if [ $SYNTAX_ERRORS -eq 0 ]; then
    log_success "모든 Python 파일 문법 정상 ($PYTHON_FILES개)"
else
    log_error "문법 오류 발견: $SYNTAX_ERRORS개"
fi

# 모듈 Import 테스트
log_info "모듈 Import 테스트 중..."

# shared.utils
if python3 -c "import sys; sys.path.insert(0, 'shared'); from shared.utils import generate_hash, get_timestamp; print('OK')" 2>/dev/null; then
    log_success "shared.utils"
else
    log_error "shared.utils import 실패"
fi

# backend.models
if python3 -c "import sys; sys.path.insert(0, 'backend'); from backend.models import RawNews, MarketTrends; print('OK')" 2>/dev/null; then
    log_success "backend.models"
else
    log_error "backend.models import 실패"
fi

# cointicker.spiders
if python3 -c "import sys; sys.path.insert(0, 'worker-nodes'); from cointicker.spiders.upbit_trends import UpbitTrendsSpider; print('OK')" 2>/dev/null; then
    log_success "cointicker.spiders"
else
    log_error "cointicker.spiders import 실패"
fi

# cointicker.items
if python3 -c "import sys; sys.path.insert(0, 'worker-nodes'); from cointicker.items import MarketTrendItem, CryptoNewsItem; print('OK')" 2>/dev/null; then
    log_success "cointicker.items"
else
    log_error "cointicker.items import 실패"
fi

# backend.api
if python3 -c "import sys; sys.path.insert(0, 'backend'); from backend.api import dashboard, news, insights; print('OK')" 2>/dev/null; then
    log_success "backend.api"
else
    log_error "backend.api import 실패"
fi

# backend.services
if python3 -c "import sys; sys.path.insert(0, 'backend'); from backend.services import data_loader, sentiment_analyzer; print('OK')" 2>/dev/null; then
    log_success "backend.services"
else
    log_error "backend.services import 실패"
fi

# mapreduce
if python3 -c "import sys; sys.path.insert(0, 'worker-nodes/mapreduce'); from cleaner_mapper import clean_data; from cleaner_reducer import remove_duplicates; print('OK')" 2>/dev/null; then
    log_success "mapreduce"
else
    log_error "mapreduce import 실패"
fi

# Spider 구조 테스트
log_info "Spider 구조 테스트 중..."
cd worker-nodes
for spider in upbit_trends coinness saveticker perplexity cnn_fear_greed; do
    if python3 -c "import sys; sys.path.insert(0, '.'); from cointicker.spiders.$spider import *; print('OK')" 2>/dev/null; then
        log_success "Spider: $spider"
    else
        log_error "Spider: $spider import 실패"
    fi
done
cd ..

# ============================================
# 3단계: Unit 테스트
# ============================================
if [ "$SKIP_UNIT_TESTS" = false ]; then
    section_header "3단계: Unit 테스트"

    log_info "Unit 테스트 실행 중..."
    if python3 -m unittest discover tests -v 2>&1 | tee -a "$TEST_LOG_FILE"; then
        UNIT_TEST_RESULT="PASSED"
        log_success "Unit 테스트 통과"
    else
        UNIT_TEST_RESULT="FAILED"
        log_error "Unit 테스트 실패"
    fi
else
    log_skip "Unit 테스트 스킵됨"
    UNIT_TEST_RESULT="SKIPPED"
fi

# ============================================
# 4단계: 통합 테스트 (서비스 상태 확인)
# ============================================
if [ "$SKIP_INTEGRATION" = false ]; then
    section_header "4단계: 통합 테스트 (서비스 상태 확인)"

    # Backend API 테스트
    log_info "Backend API 상태 확인 중..."
    if curl -s http://localhost:5000/health > /dev/null 2>&1; then
        log_success "Backend 서버 실행 중"
    else
        log_warning "Backend 서버가 실행 중이 아닙니다"
        echo "  실행 방법: bash backend/run_server.sh"
    fi

    # Frontend 서버 테스트
    log_info "Frontend 서버 상태 확인 중..."
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        log_success "Frontend 서버 실행 중"
    else
        log_warning "Frontend 서버가 실행 중이 아닙니다"
        echo "  실행 방법: bash frontend/run_dev.sh"
    fi

    # Kafka 브로커 테스트
    log_info "Kafka 브로커 상태 확인 중..."
    if command -v kafka-topics.sh &> /dev/null; then
        if kafka-topics.sh --list --bootstrap-server localhost:9092 > /dev/null 2>&1; then
            log_success "Kafka 브로커 연결 성공"
        else
            log_warning "Kafka 브로커 연결 실패"
        fi
    else
        log_warning "Kafka 명령어를 찾을 수 없습니다"
    fi

    # HDFS 테스트
    log_info "HDFS 상태 확인 중..."
    if command -v hdfs &> /dev/null; then
        if hdfs dfsadmin -report > /dev/null 2>&1; then
            log_success "HDFS 연결 성공"
        else
            log_warning "HDFS 연결 실패"
        fi
    else
        log_warning "HDFS 명령어를 찾을 수 없습니다"
    fi
else
    log_skip "통합 테스트 스킵됨"
fi

# ============================================
# 5단계: 프로세스 흐름 테스트
# ============================================
if [ "$SKIP_PROCESS_FLOW" = false ]; then
    section_header "5단계: 프로세스 흐름 테스트"

    PROCESS_FLOW_DIR="$TEST_RESULTS_DIR/process_flow"
    mkdir -p "$PROCESS_FLOW_DIR"

    # Spider 실행 테스트
    log_info "Spider 실행 테스트 중..."
    cd worker-nodes
    SPIDER_OUTPUT="$PROCESS_FLOW_DIR/spider_output.log"

    # timeout 명령어 확인
    if command -v gtimeout &> /dev/null; then
        TIMEOUT_CMD="gtimeout"
    elif command -v timeout &> /dev/null; then
        TIMEOUT_CMD="timeout"
    else
        TIMEOUT_CMD=""
    fi

    if [ -n "$TIMEOUT_CMD" ]; then
        $TIMEOUT_CMD 30 scrapy crawl upbit_trends -L INFO 2>&1 | tee "$SPIDER_OUTPUT" || true
    else
        scrapy crawl upbit_trends -L INFO 2>&1 | head -100 | tee "$SPIDER_OUTPUT" || true
    fi

    if [ -f "$SPIDER_OUTPUT" ]; then
        ITEMS_COUNT=$(grep -c "item_scraped_count" "$SPIDER_OUTPUT" 2>/dev/null || echo "0")
        ERRORS_COUNT=$(grep -c "ERROR" "$SPIDER_OUTPUT" 2>/dev/null || echo "0")
        if [ "$ERRORS_COUNT" -eq 0 ] && [ "$ITEMS_COUNT" -gt 0 ]; then
            log_success "Spider 실행 완료 (아이템: $ITEMS_COUNT)"
        else
            log_warning "Spider 실행 완료 (아이템: $ITEMS_COUNT, 에러: $ERRORS_COUNT)"
        fi
    else
        log_error "Spider 실행 실패"
    fi
    cd ..
else
    log_skip "프로세스 흐름 테스트 스킵됨"
fi

# ============================================
# 결과 요약
# ============================================
section_header "테스트 결과 요약"

# 통과율 계산
if [ $TOTAL_TESTS -gt 0 ]; then
    PASS_RATE=$(echo "scale=2; $PASSED_TESTS * 100 / $TOTAL_TESTS" | bc 2>/dev/null || echo "0")
else
    PASS_RATE=0
fi

echo "총 테스트: $TOTAL_TESTS"
echo -e "${GREEN}통과: $PASSED_TESTS${NC}"
echo -e "${RED}실패: $FAILED_TESTS${NC}"
echo -e "${CYAN}스킵: $SKIPPED_TESTS${NC}"
echo "통과율: ${PASS_RATE}%"
echo ""

# 결과 파일 저장
cat > "$TEST_RESULT_FILE" << EOF
코인티커 프로젝트 테스트 결과
테스트 일자: $(date '+%Y-%m-%d %H:%M:%S')
Python 버전: $PYTHON_VERSION
가상환경: ${VIRTUAL_ENV:-N/A}

총 테스트: $TOTAL_TESTS
통과: $PASSED_TESTS
실패: $FAILED_TESTS
스킵: $SKIPPED_TESTS
통과율: ${PASS_RATE}%

Unit 테스트: ${UNIT_TEST_RESULT:-N/A}

테스트 옵션:
- 빠른 모드: $QUICK_MODE
- 환경 설정 스킵: $SKIP_ENV_SETUP
- Unit 테스트 스킵: $SKIP_UNIT_TESTS
- 통합 테스트 스킵: $SKIP_INTEGRATION
- 프로세스 흐름 테스트 스킵: $SKIP_PROCESS_FLOW
EOF

# 최종 결과
if [ $FAILED_TESTS -eq 0 ]; then
    echo ""
    echo -e "${GREEN}=========================================="
    echo -e "✅ 모든 테스트 통과!${NC}"
    echo -e "${GREEN}==========================================${NC}"
    echo ""
    echo "상세 로그: $TEST_LOG_FILE"
    echo "결과 요약: $TEST_RESULT_FILE"
    exit 0
else
    echo ""
    echo -e "${RED}=========================================="
    echo -e "❌ 일부 테스트 실패${NC}"
    echo -e "${RED}==========================================${NC}"
    echo ""
    echo "상세 로그: $TEST_LOG_FILE"
    echo "결과 요약: $TEST_RESULT_FILE"
    exit 1
fi

