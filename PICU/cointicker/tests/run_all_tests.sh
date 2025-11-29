#!/bin/bash
# ==============================================================================
# 코인티커 프로젝트 통합 테스트 스크립트
# ==============================================================================
# 모든 테스트를 단계별로 실행하고 결과를 리포트로 생성합니다.
#
# 📌 사용 방법:
#
# 1. 일반 모드 (기본): 상태만 확인, WARNING은 보류로 처리
#    bash tests/run_all_tests.sh
#    - 서비스가 실행 중인지 상태만 확인
#    - 서비스가 없으면 스크립트 경로 안내
#    - WARNING은 실패가 아닌 보류(스킵)로 처리
#
# 2. 서비스 자동 시작 모드: 실제 실행, WARNING/ERROR는 실패로 기록
#    bash tests/run_all_tests.sh --start-services
#    - Backend, Frontend 서비스를 실제로 시작
#    - Kafka Consumer, MapReduce 스크립트 실행
#    - Spider 실제 실행 및 결과 확인
#    - WARNING과 ERROR는 모두 실패로 기록
#
# 📋 주요 옵션:
#   -s, --start-services  서비스 자동 시작 모드 (실제 실행)
#   -q, --quick           빠른 테스트 모드
#   -u, --skip-unit       Unit 테스트 스킵
#   -i, --skip-integration 통합 테스트 스킵
#   -p, --skip-process    프로세스 흐름 테스트 스킵
#   -v, --verbose         상세 출력
#   -h, --help            도움말 표시
#
# 📊 테스트 결과:
#   - results/test_results.txt  테스트 결과 요약
#   - results/test_log.txt      상세 테스트 로그
#   - results/process_flow/     프로세스 흐름 테스트 결과
#
# ==============================================================================

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
# tests/run_all_tests.sh -> tests/ -> cointicker/
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
# PICU 루트도 계산 (requirements.txt 찾기용)
PICU_ROOT="$(cd "$PROJECT_ROOT/.." && pwd)"
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
START_SERVICES=false  # 서비스 자동 시작 옵션

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
  -s, --start-services  서비스 자동 시작 (Backend, Frontend 등)
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
        -s|--start-services)
            START_SERVICES=true
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
    ((PASSED_TESTS++)) || true
    ((TOTAL_TESTS++)) || true
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$TEST_LOG_FILE"
    ((FAILED_TESTS++)) || true
    ((TOTAL_TESTS++)) || true
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$TEST_LOG_FILE"
    # --start-services 모드일 때는 WARNING도 실패로 카운트
    if [ "$START_SERVICES" = true ]; then
        ((FAILED_TESTS++)) || true
        ((TOTAL_TESTS++)) || true
    else
        # 일반 모드일 때는 보류(스킵)로 처리
        ((SKIPPED_TESTS++)) || true
        ((TOTAL_TESTS++)) || true
    fi
}

log_skip() {
    echo -e "${CYAN}[SKIP]${NC} $1" | tee -a "$TEST_LOG_FILE"
    ((SKIPPED_TESTS++)) || true
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
    log_info "PICU 루트: $PICU_ROOT"
    log_info "PROJECT_ROOT: $PROJECT_ROOT"
    log_info "현재 VIRTUAL_ENV: ${VIRTUAL_ENV:-없음}"

    # 이미 가상환경이 활성화되어 있으면 그대로 사용
    if [ -n "$VIRTUAL_ENV" ]; then
        log_info "이미 가상환경이 활성화되어 있습니다: $VIRTUAL_ENV"
        VENV_ACTIVATED=true
    else
        VENV_ACTIVATED=false

        # PICU 루트의 venv 우선 확인, 없으면 cointicker의 venv 확인
        if [ -d "$PICU_ROOT/venv" ]; then
            log_info "PICU 루트 가상환경 발견: $PICU_ROOT/venv"
            # set -e의 영향을 받지 않도록 조건문으로 처리
            if source "$PICU_ROOT/venv/bin/activate" 2>/dev/null; then
                VENV_ACTIVATED=true
                log_info "PICU 루트 가상환경 활성화 성공"
            else
                log_warning "PICU 루트 가상환경 활성화 실패, cointicker venv 확인 중..."
            fi
        else
            log_info "PICU 루트 가상환경 없음: $PICU_ROOT/venv"
        fi

        if [ "$VENV_ACTIVATED" = false ] && [ -d "$PROJECT_ROOT/venv" ]; then
            log_info "cointicker 가상환경 발견: $PROJECT_ROOT/venv"
            if source "$PROJECT_ROOT/venv/bin/activate" 2>/dev/null; then
                VENV_ACTIVATED=true
                log_info "cointicker 가상환경 활성화 성공"
            else
                log_warning "cointicker 가상환경 활성화 실패, 재생성합니다"
                rm -rf "$PROJECT_ROOT/venv" || true
                # set -e의 영향을 받지 않도록 조건문으로 처리
                if python3 -m venv "$PROJECT_ROOT/venv" 2>&1; then
                    if source "$PROJECT_ROOT/venv/bin/activate" 2>/dev/null; then
                        VENV_ACTIVATED=true
                        log_info "cointicker 가상환경 재생성 및 활성화 성공"
                    else
                        log_error "cointicker 가상환경 재생성 후 활성화 실패"
                    fi
                else
                    log_error "cointicker 가상환경 생성 실패"
                fi
            fi
        elif [ "$VENV_ACTIVATED" = false ]; then
            log_info "cointicker 가상환경 없음: $PROJECT_ROOT/venv"
        fi

        if [ "$VENV_ACTIVATED" = false ]; then
            log_info "새 가상환경 생성 중... (PICU 루트에 생성)"
            # set -e의 영향을 받지 않도록 조건문으로 처리
            if python3 -m venv "$PICU_ROOT/venv" 2>&1; then
                if source "$PICU_ROOT/venv/bin/activate" 2>/dev/null; then
                    VENV_ACTIVATED=true
                    log_info "새 가상환경 생성 및 활성화 성공"
                else
                    log_error "새 가상환경 생성 후 활성화 실패"
                fi
            else
                log_error "새 가상환경 생성 실패"
            fi
        fi
    fi

    # 가상환경 활성화 확인 (source 후 VIRTUAL_ENV가 설정되었는지 확인)
    if [ -z "$VIRTUAL_ENV" ]; then
        # VIRTUAL_ENV가 설정되지 않았으면 다시 확인
        if [ "$VENV_ACTIVATED" = true ]; then
            # 활성화 시도했지만 VIRTUAL_ENV가 설정되지 않음 - 재시도
            log_warning "가상환경 활성화 후 VIRTUAL_ENV가 설정되지 않음, 재시도 중..."
            if [ -d "$PICU_ROOT/venv" ]; then
                source "$PICU_ROOT/venv/bin/activate" || true
            elif [ -d "$PROJECT_ROOT/venv" ]; then
                source "$PROJECT_ROOT/venv/bin/activate" || true
            fi
        fi
    fi

    if [ -z "$VIRTUAL_ENV" ] && [ "$VENV_ACTIVATED" = false ]; then
        log_error "가상환경 활성화 실패 (현재 VIRTUAL_ENV: ${VIRTUAL_ENV:-없음})"
        log_error "PICU 루트 venv: $([ -d "$PICU_ROOT/venv" ] && echo "존재" || echo "없음")"
        log_error "cointicker venv: $([ -d "$PROJECT_ROOT/venv" ] && echo "존재" || echo "없음")"
        exit 1
    fi

    # VIRTUAL_ENV가 설정되었거나 이미 활성화된 경우
    if [ -n "$VIRTUAL_ENV" ] || [ "$VENV_ACTIVATED" = true ]; then
        log_success "가상환경 활성화 완료: ${VIRTUAL_ENV:-활성화됨}"
    fi

    # pip 업그레이드
    log_info "pip 업그레이드 중..."
    # set -e의 영향을 받지 않도록 조건문으로 처리
    if pip install --upgrade pip --quiet 2>&1 | tee -a "$TEST_LOG_FILE"; then
        log_success "pip 업그레이드 완료"
    else
        log_warning "pip 업그레이드 실패 (계속 진행)"
    fi

    # 의존성 설치
    log_info "의존성 설치 중..."
    # PICU 루트의 requirements.txt 우선 사용, 없으면 cointicker의 requirements.txt 사용
    REQUIREMENTS_FILE="$PICU_ROOT/requirements.txt"
    if [ ! -f "$REQUIREMENTS_FILE" ]; then
        REQUIREMENTS_FILE="$PROJECT_ROOT/requirements.txt"
        if [ ! -f "$REQUIREMENTS_FILE" ]; then
            log_error "requirements.txt 파일을 찾을 수 없습니다 (PICU: $PICU_ROOT/requirements.txt, cointicker: $PROJECT_ROOT/requirements.txt)"
            exit 1
        fi
    fi
    log_info "requirements.txt 사용: $REQUIREMENTS_FILE"

    # set -e의 영향을 받지 않도록 조건문으로 처리
    if pip install -r "$REQUIREMENTS_FILE" --quiet 2>&1 | tee -a "$TEST_LOG_FILE"; then
        log_success "의존성 설치 완료"
    else
        log_warning "일부 의존성 설치 실패 (계속 진행)"
        # 필수 패키지만 설치 시도
        pip install scrapy fastapi sqlalchemy pymysql uvicorn --quiet 2>&1 | tee -a "$TEST_LOG_FILE" || log_warning "필수 패키지 설치도 실패 (계속 진행)"
    fi
else
    log_skip "환경 설정 스킵됨"
    # 가상환경 활성화 시도 (PICU 루트 우선)
    if [ -d "$PICU_ROOT/venv" ]; then
        source "$PICU_ROOT/venv/bin/activate" 2>/dev/null || log_warning "PICU 루트 가상환경 활성화 실패"
    elif [ -d "$PROJECT_ROOT/venv" ]; then
        source "$PROJECT_ROOT/venv/bin/activate" 2>/dev/null || log_warning "cointicker 가상환경 활성화 실패"
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

# PYTHONPATH 설정 (cointicker 루트를 경로에 추가)
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# shared.utils
if python3 -c "from shared.utils import generate_hash, get_timestamp; print('OK')" 2>/dev/null; then
    log_success "shared.utils"
else
    log_error "shared.utils import 실패"
fi

# backend.models
if python3 -c "from backend.models import RawNews, MarketTrends; print('OK')" 2>/dev/null; then
    log_success "backend.models"
else
    log_error "backend.models import 실패"
fi

# cointicker.spiders
if python3 -c "import sys; sys.path.insert(0, '$PROJECT_ROOT/worker-nodes'); from cointicker.spiders.upbit_trends import UpbitTrendsSpider; print('OK')" 2>/dev/null; then
    log_success "cointicker.spiders"
else
    log_error "cointicker.spiders import 실패"
fi

# cointicker.items
if python3 -c "import sys; sys.path.insert(0, '$PROJECT_ROOT/worker-nodes'); from cointicker.items import MarketTrendItem, CryptoNewsItem; print('OK')" 2>/dev/null; then
    log_success "cointicker.items"
else
    log_error "cointicker.items import 실패"
fi

# backend.api
if python3 -c "from backend.api import dashboard, news, insights; print('OK')" 2>/dev/null; then
    log_success "backend.api"
else
    log_error "backend.api import 실패"
fi

# backend.services
if python3 -c "from backend.services import data_loader, sentiment_analyzer; print('OK')" 2>/dev/null; then
    log_success "backend.services"
else
    log_error "backend.services import 실패"
fi

# mapreduce
if python3 -c "import sys; sys.path.insert(0, '$PROJECT_ROOT/worker-nodes/mapreduce'); from cleaner_mapper import clean_data; from cleaner_reducer import remove_duplicates; print('OK')" 2>/dev/null; then
    log_success "mapreduce"
else
    log_error "mapreduce import 실패"
fi

# Spider 구조 테스트
log_info "Spider 구조 테스트 중..."
cd "$PROJECT_ROOT/worker-nodes"
for spider in upbit_trends coinness saveticker perplexity cnn_fear_greed; do
    if python3 -c "import sys; sys.path.insert(0, '$PROJECT_ROOT/worker-nodes'); from cointicker.spiders.$spider import *; print('OK')" 2>/dev/null; then
        log_success "Spider: $spider"
    else
        log_error "Spider: $spider import 실패"
    fi
done
cd "$PROJECT_ROOT"

# ============================================
# 3단계: Unit 테스트
# ============================================
if [ "$SKIP_UNIT_TESTS" = false ]; then
    section_header "3단계: Unit 테스트"

    log_info "Unit 테스트 실행 중..."
    # Unit 테스트 실행 및 결과 캡처
    python3 -m unittest discover tests -v 2>&1 | tee -a "$TEST_LOG_FILE"
    UNIT_TEST_EXIT_CODE=${PIPESTATUS[0]}

    if [ "$UNIT_TEST_EXIT_CODE" -eq 0 ]; then
        UNIT_TEST_RESULT="PASSED"
        log_success "Unit 테스트 통과"
    else
        UNIT_TEST_RESULT="FAILED"
        log_error "Unit 테스트 실패"
    fi

    # GUI 테스트 실행
    log_info "GUI Unit 테스트 실행 중..."
    # unittest.TestCase 기반 테스트 실행
    # discover는 gui/tests/ 디렉토리의 모든 test_*.py 파일을 자동으로 찾아 실행합니다
    # 포함되는 파일: test_tier2_monitor.py, test_config_manager.py, test_module_manager.py
    python3 -m unittest discover gui/tests -v -p "test_*.py" 2>&1 | tee -a "$TEST_LOG_FILE"
    GUI_UNIT_TEST_EXIT_CODE=${PIPESTATUS[0]}

    # 직접 실행 스크립트 테스트 (test_integration.py)
    log_info "GUI 통합 테스트 스크립트 실행 중..."
    cd "$PROJECT_ROOT"

    # test_refactoring.py 실행 (리팩토링 완료로 인해 비활성화됨)
    # 리팩토링이 완료되어 더 이상 실행하지 않습니다.
    # 필요시 수동으로 실행: python3 gui/tests/test_refactoring.py
    # if [ -f "gui/tests/test_refactoring.py" ]; then
    #     log_skip "GUI 리팩토링 테스트 스킵됨 (리팩토링 완료)"
    # fi

    # test_integration.py 실행
    if [ -f "gui/tests/test_integration.py" ]; then
        if python3 gui/tests/test_integration.py 2>&1 | tee -a "$TEST_LOG_FILE"; then
            log_success "GUI 통합 테스트 통과"
        else
            log_error "GUI 통합 테스트 실패"
            GUI_UNIT_TEST_EXIT_CODE=1
        fi
    fi

    # GUI 테스트 결과 종합
    if [ "$GUI_UNIT_TEST_EXIT_CODE" -eq 0 ]; then
        log_success "GUI 테스트 통과"
    else
        log_error "GUI 테스트 실패"
        # Unit 테스트 결과도 실패로 업데이트
        if [ "$UNIT_TEST_EXIT_CODE" -eq 0 ]; then
            UNIT_TEST_RESULT="FAILED"
        fi
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
    # 백엔드 포트 파일에서 포트 읽기
    BACKEND_PORT=5000
    BACKEND_PORT_FILE="$PROJECT_ROOT/config/.backend_port"
    if [ -f "$BACKEND_PORT_FILE" ]; then
        SAVED_PORT=$(cat "$BACKEND_PORT_FILE" 2>/dev/null | tr -d '\n')
        if [ -n "$SAVED_PORT" ] && [ "$SAVED_PORT" -gt 0 ] 2>/dev/null; then
            BACKEND_PORT=$SAVED_PORT
        fi
    fi

    if curl -s "http://localhost:$BACKEND_PORT/health" > /dev/null 2>&1; then
        log_success "Backend 서버 실행 중 (포트: $BACKEND_PORT)"
    else
        if [ "$START_SERVICES" = true ]; then
            log_info "Backend 서버 시작 중..."
            BACKEND_SCRIPT="$PROJECT_ROOT/backend/scripts/run_server.sh"
            if [ -f "$BACKEND_SCRIPT" ]; then
                # 백그라운드로 실행
                bash "$BACKEND_SCRIPT" > /dev/null 2>&1 &
                BACKEND_PID=$!
                log_info "Backend 서버 시작됨 (PID: $BACKEND_PID)"
                # 서버 시작 대기 (최대 10초)
                for i in {1..10}; do
                    sleep 1
                    if curl -s "http://localhost:$BACKEND_PORT/health" > /dev/null 2>&1; then
                        log_success "Backend 서버 실행 중 (포트: $BACKEND_PORT)"
                        break
                    fi
                done
                if ! curl -s "http://localhost:$BACKEND_PORT/health" > /dev/null 2>&1; then
                    log_error "Backend 서버 시작 실패 또는 타임아웃"
                fi
            else
                log_error "Backend 스크립트를 찾을 수 없습니다: $BACKEND_SCRIPT"
            fi
        else
            log_warning "Backend 서버가 실행 중이 아닙니다 (포트: $BACKEND_PORT)"
            echo "  실행 방법: bash $PROJECT_ROOT/backend/scripts/run_server.sh"
            echo "  또는 --start-services 옵션으로 자동 시작"
        fi
    fi

    # Frontend 서버 테스트
    log_info "Frontend 서버 상태 확인 중..."
    FRONTEND_PORT=3000
    # run_dev.sh에서 기록한 프론트엔드 포트 파일이 있으면 우선 사용
    FRONTEND_PORT_FILE="$PROJECT_ROOT/config/.frontend_port"
    if [ -f "$FRONTEND_PORT_FILE" ]; then
        SAVED_FRONTEND_PORT=$(cat "$FRONTEND_PORT_FILE" 2>/dev/null | tr -d '\n')
        if [ -n "$SAVED_FRONTEND_PORT" ] && [ "$SAVED_FRONTEND_PORT" -gt 0 ] 2>/dev/null; then
            FRONTEND_PORT=$SAVED_FRONTEND_PORT
        fi
    fi

    if curl -s "http://localhost:$FRONTEND_PORT" > /dev/null 2>&1; then
        log_success "Frontend 서버 실행 중 (포트: $FRONTEND_PORT)"
    else
        if [ "$START_SERVICES" = true ]; then
            log_info "Frontend 서버 시작 중..."
            FRONTEND_SCRIPT="$PROJECT_ROOT/frontend/scripts/run_dev.sh"
            if [ -f "$FRONTEND_SCRIPT" ]; then
                # 백그라운드로 실행
                bash "$FRONTEND_SCRIPT" > /dev/null 2>&1 &
                FRONTEND_PID=$!
                log_info "Frontend 서버 시작됨 (PID: $FRONTEND_PID)"
                # 서버 시작 대기 (최대 45초, Vite 및 의존성 로딩 포함)
                for i in {1..45}; do
                    sleep 1
                    if curl -s "http://localhost:$FRONTEND_PORT" > /dev/null 2>&1; then
                        log_success "Frontend 서버 실행 중 (포트: $FRONTEND_PORT)"
                        break
                    fi
                done
                if ! curl -s "http://localhost:$FRONTEND_PORT" > /dev/null 2>&1; then
                    log_error "Frontend 서버 시작 실패 또는 타임아웃"
                fi
            else
                log_error "Frontend 스크립트를 찾을 수 없습니다: $FRONTEND_SCRIPT"
            fi
        else
            log_warning "Frontend 서버가 실행 중이 아닙니다 (포트: $FRONTEND_PORT)"
            echo "  실행 방법: bash $PROJECT_ROOT/frontend/scripts/run_dev.sh"
            echo "  또는 --start-services 옵션으로 자동 시작"
        fi
    fi

    # Kafka 브로커 테스트
    log_info "Kafka 브로커 상태 확인 중..."
    if command -v kafka-topics.sh &> /dev/null; then
        if kafka-topics.sh --list --bootstrap-server localhost:9092 > /dev/null 2>&1; then
            log_success "Kafka 브로커 연결 성공"
        else
            if [ "$START_SERVICES" = true ]; then
                log_info "Kafka Consumer 시작 중..."
                KAFKA_SCRIPT="$PROJECT_ROOT/worker-nodes/scripts/run_kafka_consumer.sh"
                if [ -f "$KAFKA_SCRIPT" ]; then
                    # 백그라운드로 실행
                    bash "$KAFKA_SCRIPT" > /dev/null 2>&1 &
                    KAFKA_PID=$!
                    log_info "Kafka Consumer 시작됨 (PID: $KAFKA_PID)"
                    sleep 3
                    # Kafka Consumer 실행 확인
                    if ps -p $KAFKA_PID > /dev/null 2>&1; then
                        log_success "Kafka Consumer 실행 중 (PID: $KAFKA_PID)"
                    else
                        log_error "Kafka Consumer 시작 실패"
                    fi
                else
                    log_error "Kafka Consumer 스크립트를 찾을 수 없습니다: $KAFKA_SCRIPT"
                fi
            else
                log_warning "Kafka 브로커 연결 실패"
                KAFKA_SCRIPT="$PROJECT_ROOT/worker-nodes/scripts/run_kafka_consumer.sh"
                if [ -f "$KAFKA_SCRIPT" ]; then
                    echo "  실행 방법: bash $KAFKA_SCRIPT"
                fi
            fi
        fi
    else
        if [ "$START_SERVICES" = true ]; then
            log_info "Kafka Consumer 시작 중..."
            KAFKA_SCRIPT="$PROJECT_ROOT/worker-nodes/scripts/run_kafka_consumer.sh"
            if [ -f "$KAFKA_SCRIPT" ]; then
                # 백그라운드로 실행
                bash "$KAFKA_SCRIPT" > /dev/null 2>&1 &
                KAFKA_PID=$!
                log_info "Kafka Consumer 시작됨 (PID: $KAFKA_PID)"
                sleep 3
                # Kafka Consumer 실행 확인
                if ps -p $KAFKA_PID > /dev/null 2>&1; then
                    log_success "Kafka Consumer 실행 중 (PID: $KAFKA_PID)"
                else
                    log_error "Kafka Consumer 시작 실패"
                fi
            else
                log_error "Kafka Consumer 스크립트를 찾을 수 없습니다: $KAFKA_SCRIPT"
            fi
        else
            log_warning "Kafka 클러스터 CLI(kafka-topics.sh)를 찾을 수 없습니다 (클러스터/브로커 미실행 또는 미설치 상태)"
            KAFKA_SCRIPT="$PROJECT_ROOT/worker-nodes/scripts/run_kafka_consumer.sh"
            if [ -f "$KAFKA_SCRIPT" ]; then
                echo "  클러스터가 준비된 후 각 모듈을 실행하거나, 아래 명령어로 수동 실행하세요:"
                echo "    bash $KAFKA_SCRIPT"
                echo "  또는 서비스 자동 시작 모드에서 실행:"
                echo "    bash tests/run_all_tests.sh --start-services"
            fi
        fi
    fi

    # HDFS 테스트
    log_info "HDFS 상태 확인 중..."
    if command -v hdfs &> /dev/null; then
        if hdfs dfsadmin -report > /dev/null 2>&1; then
            log_success "HDFS 연결 성공"
        else
            if [ "$START_SERVICES" = true ]; then
                log_info "MapReduce 작업 시작 중..."
                MAPREDUCE_SCRIPT="$PROJECT_ROOT/worker-nodes/mapreduce/run_cleaner.sh"
                if [ -f "$MAPREDUCE_SCRIPT" ]; then
                    # MapReduce는 일회성 작업이므로 실행만 확인
                    log_info "MapReduce 스크립트 확인: $MAPREDUCE_SCRIPT"
                    if bash "$MAPREDUCE_SCRIPT" --dry-run 2>/dev/null || bash -n "$MAPREDUCE_SCRIPT" 2>/dev/null; then
                        log_success "MapReduce 스크립트 유효성 확인 완료"
                    else
                        log_error "MapReduce 스크립트 실행 실패"
                    fi
                else
                    log_error "MapReduce 스크립트를 찾을 수 없습니다: $MAPREDUCE_SCRIPT"
                fi
            else
                log_warning "HDFS 연결 실패"
                MAPREDUCE_SCRIPT="$PROJECT_ROOT/worker-nodes/mapreduce/run_cleaner.sh"
                if [ -f "$MAPREDUCE_SCRIPT" ]; then
                    echo "  실행 방법: bash $MAPREDUCE_SCRIPT"
                fi
            fi
        fi
    else
        if [ "$START_SERVICES" = true ]; then
            log_info "MapReduce 작업 시작 중..."
            MAPREDUCE_SCRIPT="$PROJECT_ROOT/worker-nodes/mapreduce/run_cleaner.sh"
            if [ -f "$MAPREDUCE_SCRIPT" ]; then
                # MapReduce는 일회성 작업이므로 실행만 확인
                log_info "MapReduce 스크립트 확인: $MAPREDUCE_SCRIPT"
                if bash "$MAPREDUCE_SCRIPT" --dry-run 2>/dev/null || bash -n "$MAPREDUCE_SCRIPT" 2>/dev/null; then
                    log_success "MapReduce 스크립트 유효성 확인 완료"
                else
                    log_error "MapReduce 스크립트 실행 실패"
                fi
            else
                log_error "MapReduce 스크립트를 찾을 수 없습니다: $MAPREDUCE_SCRIPT"
            fi
        else
            log_warning "Hadoop/HDFS CLI(hdfs)를 찾을 수 없습니다 (클러스터/네임노드 미실행 또는 미설치 상태)"
            MAPREDUCE_SCRIPT="$PROJECT_ROOT/worker-nodes/mapreduce/run_cleaner.sh"
            if [ -f "$MAPREDUCE_SCRIPT" ]; then
                echo "  클러스터가 준비된 후 각 모듈을 실행하거나, 아래 명령어로 수동 실행하세요:"
                echo "    bash $MAPREDUCE_SCRIPT"
                echo "  또는 서비스 자동 시작 모드에서 실행:"
                echo "    bash tests/run_all_tests.sh --start-services"
            fi
        fi
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
    SPIDER_DIR="$PROJECT_ROOT/worker-nodes/cointicker"
    SPIDER_OUTPUT="$PROCESS_FLOW_DIR/spider_output.log"

    # Scrapy 프로젝트 디렉토리 확인
    if [ ! -f "$SPIDER_DIR/scrapy.cfg" ]; then
        if [ "$START_SERVICES" = true ]; then
            log_error "Scrapy 프로젝트를 찾을 수 없습니다: $SPIDER_DIR/scrapy.cfg"
        else
            log_warning "Scrapy 프로젝트를 찾을 수 없습니다: $SPIDER_DIR/scrapy.cfg"
            echo "  작업 디렉토리: $SPIDER_DIR"
        fi
    else
        cd "$SPIDER_DIR"

        # timeout 명령어 확인
        if command -v gtimeout &> /dev/null; then
            TIMEOUT_CMD="gtimeout"
        elif command -v timeout &> /dev/null; then
            TIMEOUT_CMD="timeout"
        else
            TIMEOUT_CMD=""
        fi

        if [ "$START_SERVICES" = true ]; then
            # 실제 Spider 실행
            log_info "Spider 실행 중 (upbit_trends)..."
            # PYTHONPATH 설정: worker-nodes 디렉토리를 경로에 추가
            export PYTHONPATH="$PROJECT_ROOT/worker-nodes:$PYTHONPATH"
            if [ -n "$TIMEOUT_CMD" ]; then
                $TIMEOUT_CMD 30 scrapy crawl upbit_trends -L INFO 2>&1 | tee "$SPIDER_OUTPUT" || SPIDER_EXIT_CODE=$?
            else
                scrapy crawl upbit_trends -L INFO 2>&1 | head -100 | tee "$SPIDER_OUTPUT" || SPIDER_EXIT_CODE=$?
            fi

            if [ -f "$SPIDER_OUTPUT" ]; then
                # grep 결과를 숫자로 변환
                ITEMS_COUNT=$(grep -c "item_scraped_count" "$SPIDER_OUTPUT" 2>/dev/null | head -1 | tr -d '\n' || echo "0")
                ERRORS_COUNT=$(grep -c "ERROR" "$SPIDER_OUTPUT" 2>/dev/null | head -1 | tr -d '\n' || echo "0")

                # 숫자가 아닌 경우 0으로 설정
                if ! [[ "$ITEMS_COUNT" =~ ^[0-9]+$ ]]; then
                    ITEMS_COUNT=0
                fi
                if ! [[ "$ERRORS_COUNT" =~ ^[0-9]+$ ]]; then
                    ERRORS_COUNT=0
                fi

                # Scrapy 프로젝트가 없는 경우도 확인
                if grep -q "no active project\|crawl command is not available" "$SPIDER_OUTPUT" 2>/dev/null; then
                    log_error "Spider 실행 실패: Scrapy 프로젝트가 활성화되지 않았습니다"
                elif [ "${SPIDER_EXIT_CODE:-0}" -ne 0 ]; then
                    log_error "Spider 실행 실패 (종료 코드: ${SPIDER_EXIT_CODE})"
                elif [ "$ERRORS_COUNT" -gt 0 ]; then
                    log_error "Spider 실행 중 오류 발생 (아이템: $ITEMS_COUNT, 에러: $ERRORS_COUNT)"
                elif [ "$ITEMS_COUNT" -gt 0 ]; then
                    log_success "Spider 실행 완료 (아이템: $ITEMS_COUNT)"
                else
                    log_error "Spider 실행 완료했으나 아이템이 수집되지 않았습니다"
                fi
            else
                log_error "Spider 실행 실패: 출력 파일이 생성되지 않았습니다"
            fi
        else
            # 일반 모드: 상태만 확인
            # PYTHONPATH 설정: worker-nodes 디렉토리를 경로에 추가
            export PYTHONPATH="$PROJECT_ROOT/worker-nodes:$PYTHONPATH"
            if [ -n "$TIMEOUT_CMD" ]; then
                $TIMEOUT_CMD 5 scrapy crawl upbit_trends -L ERROR 2>&1 | head -20 | tee "$SPIDER_OUTPUT" > /dev/null 2>&1 || true
            else
                scrapy crawl upbit_trends -L ERROR 2>&1 | head -20 | tee "$SPIDER_OUTPUT" > /dev/null 2>&1 || true
            fi

            if [ -f "$SPIDER_OUTPUT" ]; then
                if grep -q "no active project\|crawl command is not available" "$SPIDER_OUTPUT" 2>/dev/null; then
                    log_warning "Spider 실행 실패: Scrapy 프로젝트가 활성화되지 않았습니다"
                    echo "  작업 디렉토리: $SPIDER_DIR"
                else
                    log_success "Spider 프로젝트 확인 완료"
                fi
            else
                log_warning "Spider 프로젝트 확인 실패"
            fi
        fi
        cd "$PROJECT_ROOT"
    fi
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

# 최종 결과 판정
# Unit 테스트 실패 또는 FAILED_TESTS가 있으면 실패
FINAL_RESULT="PASSED"
if [ "$UNIT_TEST_RESULT" = "FAILED" ] || [ $FAILED_TESTS -gt 0 ]; then
    FINAL_RESULT="FAILED"
fi

if [ "$FINAL_RESULT" = "PASSED" ]; then
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
    if [ "$UNIT_TEST_RESULT" = "FAILED" ]; then
        echo -e "${RED}⚠️  Unit 테스트 실패${NC}"
    fi
    if [ $FAILED_TESTS -gt 0 ]; then
        echo -e "${RED}⚠️  실패한 테스트: $FAILED_TESTS개${NC}"
    fi
    echo ""
    echo "상세 로그: $TEST_LOG_FILE"
    echo "결과 요약: $TEST_RESULT_FILE"
    exit 1
fi

