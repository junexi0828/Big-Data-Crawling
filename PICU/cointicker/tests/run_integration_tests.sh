#!/bin/bash
# 코인티커 프로젝트 통합 테스트 스크립트
# 가상환경 생성, 의존성 설치, 모든 테스트 실행

set -e  # 오류 발생 시 중단

# 색상 정의
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 프로젝트 루트 디렉토리
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

# 테스트 결과 디렉토리
TEST_RESULTS_DIR="$PROJECT_ROOT/tests/results"
mkdir -p "$TEST_RESULTS_DIR"

# 테스트 결과 파일 (run_all_tests.sh와 구분되도록 다른 이름 사용)
TEST_RESULT_FILE="$TEST_RESULTS_DIR/integration_test_results.txt"
TEST_LOG_FILE="$TEST_RESULTS_DIR/integration_test_log.txt"

# 카운터 초기화
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

echo "=========================================="
echo "코인티커 프로젝트 통합 테스트"
echo "=========================================="
echo ""

# 1. Python 버전 확인
echo -e "${BLUE}[1/7] Python 버전 확인${NC}"
PYTHON_VERSION=$(python3 --version 2>&1)
echo "  $PYTHON_VERSION"
if ! python3 --version | grep -q "Python 3"; then
    echo -e "${RED}❌ Python 3이 필요합니다${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python 버전 확인 완료${NC}"
echo ""

# 2. 가상환경 확인 및 생성
echo -e "${BLUE}[2/7] 가상환경 설정${NC}"
if [ -d "venv" ]; then
    echo "  기존 가상환경 발견"
    source venv/bin/activate 2>/dev/null || {
        echo -e "${YELLOW}⚠️  가상환경 활성화 실패, 재생성합니다${NC}"
        rm -rf venv
        python3 -m venv venv
        source venv/bin/activate
    }
else
    echo "  새 가상환경 생성 중..."
    python3 -m venv venv
    source venv/bin/activate
fi

if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${RED}❌ 가상환경 활성화 실패${NC}"
    exit 1
fi
echo -e "${GREEN}✅ 가상환경 활성화 완료: $VIRTUAL_ENV${NC}"
echo ""

# 3. pip 업그레이드
echo -e "${BLUE}[3/7] pip 업그레이드${NC}"
pip install --upgrade pip --quiet
echo -e "${GREEN}✅ pip 업그레이드 완료${NC}"
echo ""

# 4. 의존성 설치
echo -e "${BLUE}[4/7] 의존성 설치${NC}"
# PICU 루트의 requirements.txt 사용
REQUIREMENTS_FILE="$PROJECT_ROOT/../requirements.txt"
if [ ! -f "$REQUIREMENTS_FILE" ]; then
    echo -e "${RED}❌ requirements.txt 파일을 찾을 수 없습니다: $REQUIREMENTS_FILE${NC}"
    exit 1
fi

echo "  의존성 설치 중... (시간이 걸릴 수 있습니다)"
# 일부 패키지 설치 실패해도 계속 진행
pip install -r "$REQUIREMENTS_FILE" 2>&1 | tee -a "$TEST_LOG_FILE" || {
    echo -e "${YELLOW}⚠️  일부 의존성 설치 실패 (계속 진행)${NC}"
    # 핵심 의존성만 개별 설치 시도
    echo "  핵심 의존성 개별 설치 시도..."
    pip install scrapy fastapi sqlalchemy pymysql uvicorn --quiet 2>&1 | tee -a "$TEST_LOG_FILE" || true
}
echo -e "${GREEN}✅ 의존성 설치 완료 (일부 실패 가능)${NC}"
echo ""

# 5. Python 문법 검사
echo -e "${BLUE}[5/7] Python 문법 검사${NC}"
SYNTAX_ERRORS=0
while IFS= read -r -d '' file; do
    if ! python3 -m py_compile "$file" 2>/dev/null; then
        echo -e "  ${RED}❌${NC} $(basename $file)"
        ((SYNTAX_ERRORS++))
        ((FAILED_TESTS++))
    else
        echo -e "  ${GREEN}✅${NC} $(basename $file)"
        ((PASSED_TESTS++))
    fi
    ((TOTAL_TESTS++))
done < <(find . -name "*.py" -type f ! -path "*/venv/*" ! -path "*/__pycache__/*" ! -path "*/.git/*" -print0)

if [ $SYNTAX_ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ 모든 Python 파일 문법 정상 ($TOTAL_TESTS개)${NC}"
else
    echo -e "${RED}❌ 문법 오류 발견: $SYNTAX_ERRORS개${NC}"
fi
echo ""

# 6. 모듈 Import 테스트
echo -e "${BLUE}[6/7] 모듈 Import 테스트${NC}"

# Utils 테스트
if python3 -c "import sys; sys.path.insert(0, 'shared'); from shared.utils import generate_hash, get_timestamp; print('OK')" 2>/dev/null; then
    echo -e "  ${GREEN}✅${NC} shared.utils"
    ((PASSED_TESTS++))
else
    echo -e "  ${RED}❌${NC} shared.utils"
    ((FAILED_TESTS++))
fi
((TOTAL_TESTS++))

# Models 테스트
if python3 -c "import sys; sys.path.insert(0, 'backend'); from backend.models import RawNews, MarketTrends; print('OK')" 2>/dev/null; then
    echo -e "  ${GREEN}✅${NC} backend.models"
    ((PASSED_TESTS++))
else
    echo -e "  ${RED}❌${NC} backend.models"
    ((FAILED_TESTS++))
fi
((TOTAL_TESTS++))

# Spiders 테스트
if python3 -c "import sys; sys.path.insert(0, 'worker-nodes'); from cointicker.spiders.upbit_trends import UpbitTrendsSpider; print('OK')" 2>/dev/null; then
    echo -e "  ${GREEN}✅${NC} cointicker.spiders"
    ((PASSED_TESTS++))
else
    echo -e "  ${RED}❌${NC} cointicker.spiders"
    ((FAILED_TESTS++))
fi
((TOTAL_TESTS++))

# Items 테스트
if python3 -c "import sys; sys.path.insert(0, 'worker-nodes'); from cointicker.items import MarketTrendItem, CryptoNewsItem; print('OK')" 2>/dev/null; then
    echo -e "  ${GREEN}✅${NC} cointicker.items"
    ((PASSED_TESTS++))
else
    echo -e "  ${RED}❌${NC} cointicker.items"
    ((FAILED_TESTS++))
fi
((TOTAL_TESTS++))

# Backend API 테스트
if python3 -c "import sys; sys.path.insert(0, 'backend'); from backend.api import dashboard, news, insights; print('OK')" 2>/dev/null; then
    echo -e "  ${GREEN}✅${NC} backend.api"
    ((PASSED_TESTS++))
else
    echo -e "  ${RED}❌${NC} backend.api"
    ((FAILED_TESTS++))
fi
((TOTAL_TESTS++))

# Services 테스트
if python3 -c "import sys; sys.path.insert(0, 'backend'); from backend.services import data_loader, sentiment_analyzer; print('OK')" 2>/dev/null; then
    echo -e "  ${GREEN}✅${NC} backend.services"
    ((PASSED_TESTS++))
else
    echo -e "  ${RED}❌${NC} backend.services"
    ((FAILED_TESTS++))
fi
((TOTAL_TESTS++))

# MapReduce 테스트
if python3 -c "import sys; sys.path.insert(0, 'worker-nodes/mapreduce'); from cleaner_mapper import clean_data; from cleaner_reducer import remove_duplicates; print('OK')" 2>/dev/null; then
    echo -e "  ${GREEN}✅${NC} mapreduce"
    ((PASSED_TESTS++))
else
    echo -e "  ${RED}❌${NC} mapreduce"
    ((FAILED_TESTS++))
fi
((TOTAL_TESTS++))

echo ""

# 7. Unit 테스트 실행
echo -e "${BLUE}[7/7] Unit 테스트 실행${NC}"

# 테스트 디렉토리로 이동
cd "$PROJECT_ROOT"

# unittest 실행
if python3 -m unittest discover tests -v 2>&1 | tee -a "$TEST_LOG_FILE"; then
    UNIT_TEST_RESULT="PASSED"
    echo -e "${GREEN}✅ Unit 테스트 통과${NC}"
else
    UNIT_TEST_RESULT="FAILED"
    echo -e "${RED}❌ Unit 테스트 실패${NC}"
    ((FAILED_TESTS++))
fi
((TOTAL_TESTS++))

echo ""

# 결과 요약
echo "=========================================="
echo "테스트 결과 요약"
echo "=========================================="
echo "총 테스트: $TOTAL_TESTS"
echo -e "${GREEN}통과: $PASSED_TESTS${NC}"
echo -e "${RED}실패: $FAILED_TESTS${NC}"
echo ""

# 통과율 계산
if [ $TOTAL_TESTS -gt 0 ]; then
    PASS_RATE=$(echo "scale=2; $PASSED_TESTS * 100 / $TOTAL_TESTS" | bc)
    echo "통과율: ${PASS_RATE}%"
fi

# 결과 파일 저장
cat > "$TEST_RESULT_FILE" << EOF
코인티커 프로젝트 테스트 결과
테스트 일자: $(date '+%Y-%m-%d %H:%M:%S')
Python 버전: $PYTHON_VERSION
가상환경: $VIRTUAL_ENV

총 테스트: $TOTAL_TESTS
통과: $PASSED_TESTS
실패: $FAILED_TESTS
통과율: ${PASS_RATE}%

Unit 테스트: $UNIT_TEST_RESULT
EOF

if [ $FAILED_TESTS -eq 0 ]; then
    echo ""
    echo -e "${GREEN}=========================================="
    echo -e "✅ 모든 테스트 통과!${NC}"
    echo -e "${GREEN}==========================================${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}=========================================="
    echo -e "❌ 일부 테스트 실패${NC}"
    echo -e "${RED}==========================================${NC}"
    echo "상세 로그: $TEST_LOG_FILE"
    echo "결과 요약: $TEST_RESULT_FILE"
    exit 1
fi

