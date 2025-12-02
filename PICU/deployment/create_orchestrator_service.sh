#!/bin/bash
# 오케스트레이터 systemd 서비스 생성 스크립트

set -e

# 색상 정의
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 설정
MASTER_USER="${MASTER_USER:-ubuntu}"
MASTER_IP="${MASTER_IP:-192.168.0.100}"
PROJECT_DIR="/home/ubuntu/cointicker"

echo "=========================================="
echo "오케스트레이터 systemd 서비스 생성"
echo "=========================================="
echo ""
echo "대상: $MASTER_USER@$MASTER_IP"
echo ""

# 서비스 파일 생성
echo -e "${BLUE}서비스 파일 생성 중...${NC}"
ssh "$MASTER_USER@$MASTER_IP" << 'EOF'
    sudo tee /etc/systemd/system/cointicker-orchestrator.service > /dev/null << 'SERVICE_EOF'
[Unit]
Description=CoinTicker Pipeline Orchestrator
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/cointicker
Environment="PATH=/home/ubuntu/cointicker/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/home/ubuntu/cointicker/venv/bin/python /home/ubuntu/cointicker/master-node/orchestrator.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SERVICE_EOF

    echo "✓ 서비스 파일 생성 완료"

    # systemd 재로드
    sudo systemctl daemon-reload
    echo "✓ systemd 재로드 완료"

    # 서비스 활성화
    sudo systemctl enable cointicker-orchestrator
    echo "✓ 서비스 활성화 완료"

    # 서비스 상태 확인
    echo ""
    echo "서비스 상태:"
    sudo systemctl status cointicker-orchestrator --no-pager -l || true
EOF

echo ""
echo -e "${GREEN}✅ 오케스트레이터 서비스 설정 완료!${NC}"
echo ""
echo "서비스 제어 명령어:"
echo "  시작: ssh $MASTER_USER@$MASTER_IP 'sudo systemctl start cointicker-orchestrator'"
echo "  중지: ssh $MASTER_USER@$MASTER_IP 'sudo systemctl stop cointicker-orchestrator'"
echo "  상태: ssh $MASTER_USER@$MASTER_IP 'sudo systemctl status cointicker-orchestrator'"
echo "  로그: ssh $MASTER_USER@$MASTER_IP 'sudo journalctl -u cointicker-orchestrator -f'"
echo ""

