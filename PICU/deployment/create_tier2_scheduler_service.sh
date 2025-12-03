#!/bin/bash
# Tier 2 파이프라인 스케줄러 systemd 서비스 생성 스크립트

set -e

# 색상 정의
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 설정
TIER2_USER="${TIER2_USER:-ubuntu}"
TIER2_HOST="${TIER2_HOST:-localhost}"
PROJECT_DIR="${PROJECT_DIR:-/home/ubuntu/cointicker}"

echo "=========================================="
echo "Tier 2 파이프라인 스케줄러 systemd 서비스 생성"
echo "=========================================="
echo ""
echo "대상: $TIER2_USER@$TIER2_HOST"
echo "프로젝트 경로: $PROJECT_DIR"
echo ""

if [ "$TIER2_HOST" == "localhost" ] || [ "$TIER2_HOST" == "127.0.0.1" ]; then
    # 로컬 실행
    echo -e "${BLUE}로컬에서 서비스 파일 생성 중...${NC}"

    sudo tee /etc/systemd/system/cointicker-tier2-scheduler.service > /dev/null << SERVICE_EOF
[Unit]
Description=CoinTicker Tier 2 Pipeline Scheduler
After=network.target

[Service]
Type=simple
User=$TIER2_USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin:/usr/local/bin:/usr/bin:/bin"
Environment="PYTHONPATH=$PROJECT_DIR:$PROJECT_DIR/shared"
ExecStart=$PROJECT_DIR/venv/bin/python $PROJECT_DIR/scripts/run_pipeline_scheduler.py
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
    sudo systemctl enable cointicker-tier2-scheduler
    echo "✓ 서비스 활성화 완료"

    # 서비스 상태 확인
    echo ""
    echo "서비스 상태:"
    sudo systemctl status cointicker-tier2-scheduler --no-pager -l || true

else
    # 원격 실행
    echo -e "${BLUE}원격 서버에서 서비스 파일 생성 중...${NC}"
    ssh "$TIER2_USER@$TIER2_HOST" << EOF
        sudo tee /etc/systemd/system/cointicker-tier2-scheduler.service > /dev/null << 'SERVICE_EOF'
[Unit]
Description=CoinTicker Tier 2 Pipeline Scheduler
After=network.target

[Service]
Type=simple
User=$TIER2_USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin:/usr/local/bin:/usr/bin:/bin"
Environment="PYTHONPATH=$PROJECT_DIR:$PROJECT_DIR/shared"
ExecStart=$PROJECT_DIR/venv/bin/python $PROJECT_DIR/scripts/run_pipeline_scheduler.py
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
        sudo systemctl enable cointicker-tier2-scheduler
        echo "✓ 서비스 활성화 완료"

        # 서비스 상태 확인
        echo ""
        echo "서비스 상태:"
        sudo systemctl status cointicker-tier2-scheduler --no-pager -l || true
EOF
fi

echo ""
echo -e "${GREEN}✅ Tier 2 스케줄러 서비스 설정 완료!${NC}"
echo ""
echo "서비스 제어 명령어:"
if [ "$TIER2_HOST" == "localhost" ] || [ "$TIER2_HOST" == "127.0.0.1" ]; then
    echo "  시작: sudo systemctl start cointicker-tier2-scheduler"
    echo "  중지: sudo systemctl stop cointicker-tier2-scheduler"
    echo "  재시작: sudo systemctl restart cointicker-tier2-scheduler"
    echo "  상태: sudo systemctl status cointicker-tier2-scheduler"
    echo "  로그: sudo journalctl -u cointicker-tier2-scheduler -f"
    echo "  부팅 시 자동 시작 활성화: sudo systemctl enable cointicker-tier2-scheduler"
    echo "  부팅 시 자동 시작 비활성화: sudo systemctl disable cointicker-tier2-scheduler"
else
    echo "  시작: ssh $TIER2_USER@$TIER2_HOST 'sudo systemctl start cointicker-tier2-scheduler'"
    echo "  중지: ssh $TIER2_USER@$TIER2_HOST 'sudo systemctl stop cointicker-tier2-scheduler'"
    echo "  재시작: ssh $TIER2_USER@$TIER2_HOST 'sudo systemctl restart cointicker-tier2-scheduler'"
    echo "  상태: ssh $TIER2_USER@$TIER2_HOST 'sudo systemctl status cointicker-tier2-scheduler'"
    echo "  로그: ssh $TIER2_USER@$TIER2_HOST 'sudo journalctl -u cointicker-tier2-scheduler -f'"
    echo "  부팅 시 자동 시작 활성화: ssh $TIER2_USER@$TIER2_HOST 'sudo systemctl enable cointicker-tier2-scheduler'"
    echo "  부팅 시 자동 시작 비활성화: ssh $TIER2_USER@$TIER2_HOST 'sudo systemctl disable cointicker-tier2-scheduler'"
fi
echo ""
