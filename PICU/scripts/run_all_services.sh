#!/bin/bash
# 모든 서비스 실행 가이드 스크립트
# CLI 버전 가이드 스크립트입니다.
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
echo "CoinTicker 서비스 실행 가이드"
echo "=========================================="
echo ""

# 가상환경 확인
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ 가상환경이 없습니다.${NC}"
    echo -e "${YELLOW}먼저 'bash scripts/start.sh'를 실행하여 설치하세요.${NC}"
    exit 1
fi

# 가상환경 활성화
source venv/bin/activate

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}서비스 실행 옵션${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "1. GUI 실행"
echo "2. Backend 서버 실행"
echo "3. Frontend 개발 서버 실행"
echo "4. HDFS 연결 테스트"
echo "5. MapReduce 실행 (클러스터 모드)"
echo "6. 실행 가이드 보기 (모든 서비스)"
echo ""
read -p "선택하세요 (1-6): " choice

case $choice in
    1)
        echo -e "${GREEN}GUI 실행 중...${NC}"
        bash "$PROJECT_ROOT/scripts/run_gui.sh"
        ;;
    2)
        echo -e "${GREEN}Backend 서버 실행 중...${NC}"
        bash "$PROJECT_ROOT/cointicker/backend/scripts/run_server.sh"
        ;;
    3)
        echo -e "${GREEN}Frontend 개발 서버 실행 중...${NC}"
        bash "$PROJECT_ROOT/cointicker/frontend/scripts/run_dev.sh"
        ;;
    4)
        echo -e "${GREEN}HDFS 연결 테스트 실행 중...${NC}"
        if [ -f "$PROJECT_ROOT/cointicker/tests/test_hdfs_connection.py" ]; then
            python "$PROJECT_ROOT/cointicker/tests/test_hdfs_connection.py"
        else
            echo -e "${RED}❌ HDFS 연결 테스트 스크립트를 찾을 수 없습니다.${NC}"
        fi
        ;;
    5)
        echo -e "${GREEN}MapReduce 실행 중...${NC}"
        read -p "입력 경로 (기본: /user/cointicker/raw): " input_path
        read -p "출력 경로 (기본: /user/cointicker/cleaned): " output_path
        input_path=${input_path:-/user/cointicker/raw}
        output_path=${output_path:-/user/cointicker/cleaned}
        if [ -f "$PROJECT_ROOT/cointicker/scripts/run_mapreduce.sh" ]; then
            bash "$PROJECT_ROOT/cointicker/scripts/run_mapreduce.sh" "$input_path" "$output_path"
        else
            echo -e "${RED}❌ MapReduce 스크립트를 찾을 수 없습니다.${NC}"
        fi
        ;;
    6)
        echo ""
        echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${CYAN}모든 서비스 실행 가이드${NC}"
        echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        echo -e "${YELLOW}3개의 터미널이 필요합니다.${NC}"
        echo ""
        echo -e "${CYAN}터미널 1 - GUI:${NC}"
        echo "  cd \"$PROJECT_ROOT\""
        echo "  source venv/bin/activate"
        echo "  bash scripts/run_gui.sh"
        echo ""
        echo -e "${CYAN}터미널 2 - Backend:${NC}"
        echo "  cd \"$PROJECT_ROOT\""
        echo "  source venv/bin/activate"
        echo "  bash cointicker/backend/scripts/run_server.sh"
        echo ""
        echo -e "${CYAN}터미널 3 - Frontend:${NC}"
        echo "  cd \"$PROJECT_ROOT\""
        echo "  bash cointicker/frontend/scripts/run_dev.sh"
        echo ""
        echo -e "${GREEN}접속 주소:${NC}"
        echo "  - GUI: 로컬 실행"
        echo "  - Backend API: http://localhost:5000"
        echo "  - Backend Docs: http://localhost:5000/docs"
        echo "  - Frontend: http://localhost:3000"
        echo ""
        echo -e "${CYAN}추가 테스트 및 도구:${NC}"
        echo "  - HDFS 연결 테스트: python cointicker/tests/test_hdfs_connection.py"
        echo "  - MapReduce (클러스터): bash cointicker/scripts/run_mapreduce.sh [INPUT] [OUTPUT]"
        echo "  - MapReduce (로컬): bash cointicker/worker-nodes/mapreduce/run_cleaner.sh"
        echo "  - 전체 테스트: bash cointicker/tests/run_all_tests.sh"
        echo "  - 통합 테스트: bash cointicker/tests/run_integration_tests.sh"
        echo ""
        echo -e "${YELLOW}각 터미널에서 위 명령어를 실행하세요.${NC}"
        ;;
    *)
        echo -e "${RED}잘못된 선택입니다.${NC}"
        exit 1
        ;;
esac

