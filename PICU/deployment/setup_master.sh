#!/bin/bash
# Master Node (라즈베리파이 #1) 배포 스크립트

set -e

# 색상 정의
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 설정
MASTER_HOST="${MASTER_HOST:-raspberry-master}"
MASTER_USER="${MASTER_USER:-pi}"
MASTER_IP="${MASTER_IP:-192.168.1.100}"
PROJECT_DIR="/home/pi/cointicker"

echo "=========================================="
echo "Master Node 배포"
echo "=========================================="
echo ""
echo "대상: $MASTER_USER@$MASTER_IP"
echo ""

# 프로젝트 루트 확인
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

# 1. 코드 배포
echo -e "${BLUE}[1/3] 코드 배포 중...${NC}"
rsync -avz --exclude 'venv' --exclude '__pycache__' --exclude '*.pyc' \
    "$PROJECT_ROOT/cointicker/master-node/" \
    "$MASTER_USER@$MASTER_IP:$PROJECT_DIR/master-node/"

rsync -avz --exclude 'venv' --exclude '__pycache__' --exclude '*.pyc' \
    "$PROJECT_ROOT/cointicker/shared/" \
    "$MASTER_USER@$MASTER_IP:$PROJECT_DIR/shared/"

rsync -avz --exclude 'venv' --exclude '__pycache__' --exclude '*.pyc' \
    "$PROJECT_ROOT/cointicker/config/" \
    "$MASTER_USER@$MASTER_IP:$PROJECT_DIR/config/"

echo -e "${GREEN}✅ 코드 배포 완료${NC}"
echo ""

# 2. 가상환경 설정
echo -e "${BLUE}[2/3] 가상환경 설정 중...${NC}"
ssh "$MASTER_USER@$MASTER_IP" << EOF
    cd $PROJECT_DIR

    # 가상환경 생성
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi

    # 가상환경 활성화 및 의존성 설치
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r $PROJECT_ROOT/requirements/requirements-master.txt
EOF

echo -e "${GREEN}✅ 가상환경 설정 완료${NC}"
echo ""

# 3. 서비스 설정
echo -e "${BLUE}[3/3] 서비스 설정 중...${NC}"
ssh "$MASTER_USER@$MASTER_IP" << EOF
    cd $PROJECT_DIR

    # systemd 서비스 파일 생성 (선택적)
    # sudo systemctl enable cointicker-master
    # sudo systemctl start cointicker-master
EOF

echo -e "${GREEN}✅ Master Node 배포 완료!${NC}"
echo ""

