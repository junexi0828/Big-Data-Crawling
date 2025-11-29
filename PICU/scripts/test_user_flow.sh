#!/bin/bash
# 실사용자 흐름 테스트: 설치 → GUI → 프론트엔드

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
echo "실사용자 흐름 테스트"
echo "=========================================="
echo ""

# ============================================
# 1단계: 처음 설치
# ============================================
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}1단계: 처음 설치${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo -e "${YELLOW}가상환경 설정 중...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✅ 가상환경 생성 완료${NC}"
else
    echo -e "${GREEN}✅ 가상환경이 이미 존재합니다${NC}"
fi

source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -q -r "$PROJECT_ROOT/requirements.txt"
echo -e "${GREEN}✅ 의존성 설치 완료${NC}"

echo ""
echo -e "${YELLOW}가상환경 활성화 중...${NC}"
source venv/bin/activate

# ============================================
# 2단계: GUI 열기
# ============================================
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}2단계: GUI 열기${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo -e "${YELLOW}GUI 모듈 테스트 중...${NC}"
cd cointicker

# GUI 모듈이 정상적으로 로드되는지 테스트
if python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from gui.main import main
    from gui.core.module_manager import ModuleManager
    from gui.modules.kafka_module import KafkaModule
    print('✅ GUI 모듈 로드 성공')
except Exception as e:
    print(f'❌ GUI 모듈 로드 실패: {e}')
    sys.exit(1)
"; then
    echo -e "${GREEN}✅ GUI 모듈 정상${NC}"
else
    echo -e "${RED}❌ GUI 모듈 오류${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}GUI 실행 방법:${NC}"
echo -e "${GREEN}  cd \"$PROJECT_ROOT\"${NC}"
echo -e "${GREEN}  source venv/bin/activate${NC}"
echo -e "${GREEN}  bash scripts/run_gui.sh${NC}"
echo ""
echo -e "${YELLOW}또는:${NC}"
echo -e "${GREEN}  cd \"$PROJECT_ROOT\"${NC}"
echo -e "${GREEN}  python cointicker/gui/main.py${NC}"

cd ..

# ============================================
# 3단계: 프론트엔드
# ============================================
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}3단계: 프론트엔드${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

cd cointicker/frontend

# package.json 확인
if [ ! -f "package.json" ]; then
    echo -e "${RED}❌ package.json 파일을 찾을 수 없습니다.${NC}"
    exit 1
fi

# node_modules 확인 및 설치
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}프론트엔드 의존성 설치 중...${NC}"
    if npm install; then
        echo -e "${GREEN}✅ 프론트엔드 의존성 설치 완료${NC}"
    else
        echo -e "${RED}❌ 프론트엔드 의존성 설치 실패${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ 프론트엔드 의존성이 이미 설치되어 있습니다.${NC}"
fi

# 빌드 테스트
echo ""
echo -e "${YELLOW}프론트엔드 빌드 테스트 중...${NC}"
if npm run build 2>&1 | tail -10; then
    echo -e "${GREEN}✅ 프론트엔드 빌드 성공${NC}"
else
    echo -e "${RED}❌ 프론트엔드 빌드 실패${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}프론트엔드 실행 방법:${NC}"
echo -e "${GREEN}  cd \"$PROJECT_ROOT/cointicker/frontend\"${NC}"
echo -e "${GREEN}  npm run dev${NC}"
echo ""
echo -e "${YELLOW}접속: http://localhost:3000${NC}"

cd ../..

# ============================================
# 4단계: Backend 서버 (선택적)
# ============================================
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}4단계: Backend 서버 (선택적)${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

cd cointicker/backend

echo -e "${YELLOW}Backend 모듈 테스트 중...${NC}"
if python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from app import app
    from models import Base
    print('✅ Backend 모듈 로드 성공')
except Exception as e:
    print(f'❌ Backend 모듈 로드 실패: {e}')
    sys.exit(1)
"; then
    echo -e "${GREEN}✅ Backend 모듈 정상${NC}"
else
    echo -e "${YELLOW}⚠️ Backend 모듈 오류 (데이터베이스 미설정일 수 있음)${NC}"
fi

echo ""
echo -e "${YELLOW}Backend 서버 실행 방법:${NC}"
echo -e "${GREEN}  cd \"$PROJECT_ROOT\"${NC}"
echo -e "${GREEN}  source venv/bin/activate${NC}"
echo -e "${GREEN}  bash cointicker/backend/scripts/run_server.sh${NC}"
echo ""
echo -e "${YELLOW}또는:${NC}"
echo -e "${GREEN}  cd \"$PROJECT_ROOT/cointicker/backend\"${NC}"
echo -e "${GREEN}  uvicorn app:app --host 0.0.0.0 --port 5000${NC}"
echo ""
echo -e "${YELLOW}접속: http://localhost:5000${NC}"

cd ../..

# ============================================
# 최종 요약
# ============================================
echo ""
echo "=========================================="
echo -e "${GREEN}✅ 실사용자 흐름 테스트 완료!${NC}"
echo "=========================================="
echo ""
echo -e "${CYAN}실행 순서:${NC}"
echo ""
echo -e "${YELLOW}1. GUI 실행 (터미널 1):${NC}"
echo "   cd \"$PROJECT_ROOT\""
echo "   source venv/bin/activate"
echo "   bash scripts/run_gui.sh"
echo ""
echo -e "${YELLOW}2. Backend 서버 실행 (터미널 2):${NC}"
echo "   cd \"$PROJECT_ROOT\""
echo "   source venv/bin/activate"
echo "   bash cointicker/backend/scripts/run_server.sh"
echo ""
echo -e "${YELLOW}3. Frontend 개발 서버 실행 (터미널 3):${NC}"
echo "   cd \"$PROJECT_ROOT\""
echo "   bash cointicker/frontend/scripts/run_dev.sh"
echo ""
echo -e "${CYAN}접속 주소:${NC}"
echo "   - GUI: 로컬 실행"
echo "   - Backend API: http://localhost:5000"
echo "   - Frontend: http://localhost:3000"
echo ""

