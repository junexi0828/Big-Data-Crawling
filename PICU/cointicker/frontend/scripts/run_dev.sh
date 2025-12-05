#!/bin/bash
# Frontend 개발 서버 실행 스크립트
#
# ⚠️ 주의: 삭제 및 수정 금지 ⚠️
#
# 이 스크립트는 GUI와 연동되어 있습니다:
# - 포트 충돌 감지 및 자동 포트 변경 (3000 -> 3001)
# - 백엔드 포트를 config/.backend_port 파일에서 읽어 VITE_API_BASE_URL 설정
# - 프론트엔드와 백엔드 포트 동기화
#
# 연동된 컴포넌트:
# - gui/modules/pipeline_orchestrator.py: 프론트엔드 시작 시 이 스크립트 사용
# - vite.config.ts: VITE_API_BASE_URL 환경 변수 사용
# - frontend/services/api.ts: 백엔드 API URL 동적 설정
#
# 이 스크립트를 수정하거나 삭제하면 GUI의 프론트엔드 포트 자동 감지 기능이 작동하지 않습니다.

set -e

# 색상 정의
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 스크립트 디렉토리
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# 프로젝트 루트
# frontend/scripts/run_dev.sh -> frontend/ -> cointicker/ -> PICU/
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Frontend 디렉토리로 이동
# subprocess.Popen에서 cwd가 이미 frontend 디렉토리로 설정되어 있으므로
# 현재 디렉토리가 frontend가 아닌 경우에만 이동
if [ "$(basename "$(pwd)")" != "frontend" ]; then
    cd "$SCRIPT_DIR" || cd "$PROJECT_ROOT/cointicker/frontend"
fi

# Figma 프로젝트 디렉토리로 이동
FIGMA_PROJECT_DIR="Cryptocurrency Analytics Dashboard"
if [ -d "$FIGMA_PROJECT_DIR" ]; then
    cd "$FIGMA_PROJECT_DIR" || {
        echo -e "${RED}❌ Figma 프로젝트 디렉토리로 이동할 수 없습니다: $FIGMA_PROJECT_DIR${NC}"
        exit 1
    }
else
    echo -e "${RED}❌ Figma 프로젝트 디렉토리를 찾을 수 없습니다: $FIGMA_PROJECT_DIR${NC}"
    exit 1
fi

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

# 포트 설정 (기본값: 3000)
FRONTEND_PORT=${FRONTEND_PORT:-3000}

# 포트가 사용 중인지 확인
if lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    PORT_PID=$(lsof -ti :$FRONTEND_PORT)
    PORT_CMD=$(ps -p $PORT_PID -o comm= 2>/dev/null || echo "unknown")
    if [[ "$PORT_CMD" == *"vite"* ]] || [[ "$PORT_CMD" == *"node"* ]] || [[ "$PORT_CMD" == *"npm"* ]]; then
        echo -e "${YELLOW}⚠️  포트 $FRONTEND_PORT이 이미 사용 중입니다 (PID: $PORT_PID).${NC}"
        # 대화형 터미널에서만 사용자에게 물어봄 (테스트/GUI에서는 자동으로 다른 포트 사용)
        if [ -t 0 ]; then
            echo -e "${YELLOW}기존 프론트엔드 서버를 종료하시겠습니까? (y/n)${NC}"
            read -r response
            if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
                echo -e "${YELLOW}기존 프로세스 종료 중...${NC}"
                kill -9 $PORT_PID 2>/dev/null || true
                sleep 1
            else
                echo -e "${YELLOW}다른 포트를 사용합니다 (3001)...${NC}"
                FRONTEND_PORT=3001
                # vite.config.js에서 포트 변경 (임시)
                export VITE_PORT=$FRONTEND_PORT
            fi
        else
            echo -e "${YELLOW}비대화형 환경이므로 기존 프로세스를 유지하고 다른 포트(3001)를 사용합니다.${NC}"
            FRONTEND_PORT=3001
            export VITE_PORT=$FRONTEND_PORT
        fi
    else
        echo -e "${YELLOW}⚠️  포트 $FRONTEND_PORT이 사용 중이지만 프론트엔드 서버가 아닙니다.${NC}"
        echo -e "${YELLOW}다른 포트를 사용합니다 (3001)...${NC}"
        FRONTEND_PORT=3001
        export VITE_PORT=$FRONTEND_PORT
    fi
fi

# 최종 프론트엔드 포트를 파일에 기록 (테스트 스크립트 및 GUI에서 사용)
FRONTEND_PORT_FILE="$PROJECT_ROOT/cointicker/config/.frontend_port"
mkdir -p "$(dirname "$FRONTEND_PORT_FILE")"
echo "$FRONTEND_PORT" > "$FRONTEND_PORT_FILE" 2>/dev/null || true

echo ""
echo -e "${BLUE}Frontend 개발 서버 시작 중...${NC}"
echo -e "${GREEN}접속 주소: http://localhost:$FRONTEND_PORT${NC}"
echo ""

# 백엔드 포트 확인 (백엔드가 저장한 포트 파일에서 읽기)
BACKEND_PORT=${BACKEND_PORT:-5000}

# 백엔드 포트 파일 확인
BACKEND_PORT_FILE="$PROJECT_ROOT/cointicker/config/.backend_port"
if [ -f "$BACKEND_PORT_FILE" ]; then
    SAVED_PORT=$(cat "$BACKEND_PORT_FILE" 2>/dev/null | tr -d '\n')
    if [ -n "$SAVED_PORT" ] && [ "$SAVED_PORT" -gt 0 ] 2>/dev/null; then
        BACKEND_PORT=$SAVED_PORT
        echo -e "${GREEN}✅ 백엔드 포트를 설정 파일에서 읽었습니다: $BACKEND_PORT${NC}"
    fi
fi

# GUI 설정에서도 확인 (fallback)
if [ "$BACKEND_PORT" = "5000" ] && [ -f "$PROJECT_ROOT/cointicker/config/gui_config.yaml" ]; then
    TIER2_URL=$(grep -E "base_url:" "$PROJECT_ROOT/cointicker/config/gui_config.yaml" 2>/dev/null | head -1 | awk '{print $2}' | sed 's|http://localhost:||' | sed 's|http://127.0.0.1:||')
    if [ -n "$TIER2_URL" ] && [ "$TIER2_URL" -gt 0 ] 2>/dev/null; then
        BACKEND_PORT=$TIER2_URL
        echo -e "${GREEN}✅ 백엔드 포트를 GUI 설정에서 읽었습니다: $BACKEND_PORT${NC}"
    fi
fi

# 포트를 환경변수로 전달 (vite.config.js에서 읽을 수 있도록)
export PORT=$FRONTEND_PORT
export VITE_PORT=$FRONTEND_PORT
export BACKEND_PORT=$BACKEND_PORT
export VITE_API_BASE_URL="http://localhost:$BACKEND_PORT"

echo -e "${BLUE}백엔드 API 주소: http://localhost:$BACKEND_PORT${NC}"
echo ""

npm run dev

