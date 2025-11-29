#!/bin/bash
# Backend 서버 실행 스크립트
#
# ⚠️ 주의: 삭제 및 수정 금지 ⚠️
#
# 이 스크립트는 GUI와 연동되어 있습니다:
# - 포트 충돌 감지 및 자동 포트 변경 (5000 -> 5001)
# - 포트 정보를 config/.backend_port 파일에 저장
# - GUI의 tier2_monitor가 이 파일을 읽어 백엔드 포트를 동기화
#
# 연동된 컴포넌트:
# - gui/modules/pipeline_orchestrator.py: 백엔드 시작 시 이 스크립트 사용
# - gui/modules/backend_module.py: 백엔드 모듈 시작 시 이 스크립트 사용
# - gui/monitors/tier2_monitor.py: get_backend_port_from_file()로 포트 읽기
# - gui/app.py: _reinitialize_tier2_monitor()로 포트 동기화
#
# 이 스크립트를 수정하거나 삭제하면 GUI의 백엔드 포트 자동 감지 기능이 작동하지 않습니다.

set -e

# 색상 정의
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 프로젝트 루트 확인
# subprocess.Popen에서 cwd가 설정되어 있어도 스크립트 경로는 정확히 계산됨
# backend/scripts/run_server.sh -> backend/ -> cointicker/ -> PICU/
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

echo "=========================================="
echo "Backend 서버 시작"
echo "=========================================="
echo ""

# 가상환경 활성화 (PICU 루트 venv 우선, 그 다음 cointicker venv)
if [ -d "$PROJECT_ROOT/venv" ]; then
    source "$PROJECT_ROOT/venv/bin/activate"
    echo -e "${GREEN}✅ 가상환경 활성화: $VIRTUAL_ENV${NC}"
elif [ -d "$SCRIPT_DIR/../venv" ]; then
    source "$SCRIPT_DIR/../venv/bin/activate"
    echo -e "${GREEN}✅ 가상환경 활성화: $VIRTUAL_ENV${NC}"
else
    echo -e "${RED}❌ 가상환경을 찾을 수 없습니다.${NC}"
    echo -e "${YELLOW}먼저 'bash scripts/start.sh'를 실행하여 설치하세요.${NC}"
    exit 1
fi

# SQLite 사용 (데이터베이스 미설정 시)
export USE_SQLITE=true

# Python 경로 설정 (cointicker 디렉토리를 경로에 추가)
export PYTHONPATH="$PROJECT_ROOT/cointicker:$PYTHONPATH"

# Backend 디렉토리로 이동
# subprocess.Popen에서 cwd가 이미 backend 디렉토리로 설정되어 있으므로
# 현재 디렉토리가 backend가 아닌 경우에만 이동
if [ "$(basename "$(pwd)")" != "backend" ]; then
    cd "$PROJECT_ROOT/cointicker/backend" || cd "$SCRIPT_DIR"
fi

# 현재 디렉토리를 Python 경로에 추가 (상대 import 지원)
export PYTHONPATH="$(pwd):$PYTHONPATH"

# 포트 설정 (기본값: 5000)
BACKEND_PORT=${BACKEND_PORT:-5000}

# 포트가 사용 중인지 확인 (백엔드 서버만)
# GUI에서 실행 시 비대화형 모드 지원 (AUTO_PORT_SWITCH 환경 변수)
AUTO_PORT_SWITCH=${AUTO_PORT_SWITCH:-false}

if lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    PORT_PID=$(lsof -ti :$BACKEND_PORT)
    PORT_CMD=$(ps -p $PORT_PID -o comm= 2>/dev/null || echo "unknown")
    if [[ "$PORT_CMD" == *"uvicorn"* ]] || [[ "$PORT_CMD" == *"python"* ]]; then
        if [[ "$AUTO_PORT_SWITCH" == "true" ]]; then
            # GUI에서 실행 시 자동으로 다른 포트 사용
            echo -e "${YELLOW}⚠️  포트 $BACKEND_PORT이 이미 사용 중입니다. 자동으로 다른 포트를 사용합니다 (5001)...${NC}"
            BACKEND_PORT=5001
        else
            # 대화형 모드 (터미널에서 직접 실행 시)
            echo -e "${YELLOW}⚠️  포트 $BACKEND_PORT이 이미 사용 중입니다 (PID: $PORT_PID).${NC}"
            echo -e "${YELLOW}기존 백엔드 서버를 종료하시겠습니까? (y/n)${NC}"
            read -r response
            if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
                echo -e "${YELLOW}기존 프로세스 종료 중...${NC}"
                kill -9 $PORT_PID 2>/dev/null || true
                sleep 1
            else
                echo -e "${YELLOW}다른 포트를 사용합니다 (5001)...${NC}"
                BACKEND_PORT=5001
            fi
        fi
    else
        echo -e "${YELLOW}⚠️  포트 $BACKEND_PORT이 사용 중이지만 백엔드 서버가 아닙니다.${NC}"
        echo -e "${YELLOW}다른 포트를 사용합니다 (5001)...${NC}"
        BACKEND_PORT=5001
    fi
fi

# 백엔드 포트를 파일에 저장 (프론트엔드가 읽을 수 있도록)
BACKEND_PORT_FILE="$PROJECT_ROOT/cointicker/config/.backend_port"
# 디렉토리가 없으면 생성
mkdir -p "$(dirname "$BACKEND_PORT_FILE")"
echo "$BACKEND_PORT" > "$BACKEND_PORT_FILE"
echo -e "${GREEN}✅ 백엔드 포트 파일 생성: $BACKEND_PORT_FILE (포트: $BACKEND_PORT)${NC}"

echo -e "${BLUE}Backend 서버 시작 중...${NC}"
echo ""
echo -e "${GREEN}접속 주소:${NC}"
echo "  - API: http://localhost:$BACKEND_PORT"
echo "  - API 문서: http://localhost:$BACKEND_PORT/docs"
echo "  - 헬스 체크: http://localhost:$BACKEND_PORT/health"
echo ""
echo -e "${YELLOW}💡 프론트엔드 실행 시 이 포트($BACKEND_PORT)를 사용합니다.${NC}"
echo ""

uvicorn app:app --host 0.0.0.0 --port $BACKEND_PORT --reload

