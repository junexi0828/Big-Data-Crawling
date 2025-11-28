#!/bin/bash
# Worker Node (라즈베리파이 #2,3,4) 배포 스크립트

set -e

# 색상 정의
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 설정
WORKER_HOST="${1:-raspberry-worker1}"
WORKER_USER="${WORKER_USER:-pi}"
WORKER_IP="${2:-192.168.1.101}"
PROJECT_DIR="/home/pi/cointicker"

echo "=========================================="
echo "Worker Node 배포: $WORKER_HOST"
echo "=========================================="
echo ""
echo "대상: $WORKER_USER@$WORKER_IP"
echo ""

# 프로젝트 루트 확인
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

# 1. 코드 배포
echo -e "${BLUE}[1/3] 코드 배포 중...${NC}"
rsync -avz --exclude 'venv' --exclude '__pycache__' --exclude '*.pyc' \
    "$PROJECT_ROOT/cointicker/worker-nodes/" \
    "$WORKER_USER@$WORKER_IP:$PROJECT_DIR/worker-nodes/"

rsync -avz --exclude 'venv' --exclude '__pycache__' --exclude '*.pyc' \
    "$PROJECT_ROOT/cointicker/shared/" \
    "$WORKER_USER@$WORKER_IP:$PROJECT_DIR/shared/"

rsync -avz --exclude 'venv' --exclude '__pycache__' --exclude '*.pyc' \
    "$PROJECT_ROOT/cointicker/config/" \
    "$WORKER_USER@$WORKER_IP:$PROJECT_DIR/config/"

echo -e "${GREEN}✅ 코드 배포 완료${NC}"
echo ""

# 2. 가상환경 설정
echo -e "${BLUE}[2/3] 가상환경 설정 중...${NC}"
ssh "$WORKER_USER@$WORKER_IP" << EOF
    cd $PROJECT_DIR

    # 가상환경 생성
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi

    # 가상환경 활성화 및 의존성 설치
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r $PROJECT_ROOT/requirements/requirements-worker.txt
EOF

echo -e "${GREEN}✅ 가상환경 설정 완료${NC}"
echo ""

# 3. 서비스 설정
echo -e "${BLUE}[3/3] 서비스 설정 중...${NC}"
ssh "$WORKER_USER@$WORKER_IP" << EOF
    cd $PROJECT_DIR

    # systemd 서비스 파일 생성 (선택적)
    # sudo systemctl enable cointicker-worker
    # sudo systemctl start cointicker-worker
EOF

echo -e "${GREEN}✅ Worker Node 배포 완료!${NC}"
echo ""

