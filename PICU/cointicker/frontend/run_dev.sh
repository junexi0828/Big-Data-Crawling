#!/bin/bash
# Frontend 개발 서버 실행 스크립트

set -e

# 색상 정의
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 스크립트 디렉토리
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# 프로젝트 루트
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "=========================================="
echo "Frontend 개발 서버 시작"
echo "=========================================="
echo ""

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
    # 의존성 업데이트 확인 (선택적)
    echo -e "${YELLOW}의존성 업데이트 확인 중...${NC}"
    npm install --dry-run 2>&1 | grep -q "up to date" && echo -e "${GREEN}의존성이 최신 상태입니다.${NC}" || echo -e "${YELLOW}의존성 업데이트가 필요할 수 있습니다.${NC}"
fi

echo ""
echo -e "${BLUE}Frontend 개발 서버 시작 중...${NC}"
echo -e "${GREEN}접속 주소: http://localhost:3000${NC}"
echo ""

npm run dev

