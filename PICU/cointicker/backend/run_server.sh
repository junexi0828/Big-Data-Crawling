#!/bin/bash
# Backend 서버 실행 스크립트

set -e

# 색상 정의
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 프로젝트 루트 확인
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

echo "=========================================="
echo "Backend 서버 시작"
echo "=========================================="
echo ""

# 프로젝트 루트 찾기
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# 가상환경 활성화 (PICU 루트 venv 우선)
if [ -d "$PROJECT_ROOT/venv" ]; then
    source "$PROJECT_ROOT/venv/bin/activate"
    echo -e "${GREEN}✅ 가상환경 활성화: $VIRTUAL_ENV${NC}"
elif [ -d "$SCRIPT_DIR/../venv" ]; then
    source "$SCRIPT_DIR/../venv/bin/activate"
    echo -e "${GREEN}✅ 가상환경 활성화: $VIRTUAL_ENV${NC}"
else
    echo -e "${RED}❌ 가상환경을 찾을 수 없습니다.${NC}"
    echo -e "${YELLOW}먼저 'bash start.sh'를 실행하여 설치하세요.${NC}"
    exit 1
fi

# SQLite 사용 (데이터베이스 미설정 시)
export USE_SQLITE=true

# Backend 서버 실행
cd cointicker/backend

echo -e "${BLUE}Backend 서버 시작 중...${NC}"
echo ""
echo -e "${GREEN}접속 주소:${NC}"
echo "  - API: http://localhost:5000"
echo "  - API 문서: http://localhost:5000/docs"
echo "  - 헬스 체크: http://localhost:5000/health"
echo ""

uvicorn app:app --host 0.0.0.0 --port 5000 --reload

