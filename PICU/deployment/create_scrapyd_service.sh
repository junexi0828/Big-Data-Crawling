#!/bin/bash
# Scrapyd 서버 systemd/launchctl 서비스 생성 스크립트

set -e

# 색상 정의
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 설정
MASTER_USER="${MASTER_USER:-ubuntu}"
MASTER_IP="${MASTER_IP:-localhost}"
PROJECT_DIR="${PROJECT_DIR:-/home/ubuntu/cointicker}"

# macOS인지 확인
if [[ "$OSTYPE" == "darwin"* ]]; then
    IS_MACOS=true
    PROJECT_DIR="${PROJECT_DIR:-$HOME/code/personal/notion/pknu_workspace/bigdata/PICU/cointicker}"
else
    IS_MACOS=false
fi

echo "=========================================="
echo "Scrapyd 서버 systemd/launchctl 서비스 생성"
echo "=========================================="
echo ""
echo "대상: $MASTER_USER@$MASTER_IP"
echo "프로젝트 경로: $PROJECT_DIR"
echo ""

if [ "$IS_MACOS" = true ]; then
    # macOS: launchctl 사용
    echo -e "${BLUE}macOS: launchctl 서비스 생성 중...${NC}"

    PLIST_NAME="com.cointicker.scrapyd"
    PLIST_FILE="$HOME/Library/LaunchAgents/${PLIST_NAME}.plist"

    # venv Python 경로 찾기
    if [ -f "$PROJECT_DIR/../venv/bin/python" ]; then
        PYTHON_CMD="$PROJECT_DIR/../venv/bin/python"
    elif [ -f "$PROJECT_DIR/venv/bin/python" ]; then
        PYTHON_CMD="$PROJECT_DIR/venv/bin/python"
    else
        PYTHON_CMD=$(which python3)
    fi

    # scrapyd 명령어 찾기
    if [ -f "$PROJECT_DIR/../venv/bin/scrapyd" ]; then
        SCRAPYD_CMD="$PROJECT_DIR/../venv/bin/scrapyd"
    elif [ -f "$PROJECT_DIR/venv/bin/scrapyd" ]; then
        SCRAPYD_CMD="$PROJECT_DIR/venv/bin/scrapyd"
    else
        SCRAPYD_CMD=$(which scrapyd)
    fi

    # 프로젝트 루트 찾기
    if [ -d "$PROJECT_DIR/../.." ]; then
        PROJECT_ROOT="$(cd "$PROJECT_DIR/../.." && pwd)"
    else
        PROJECT_ROOT="$(cd "$PROJECT_DIR/.." && pwd)"
    fi

    # plist 파일 생성
    cat > "$PLIST_FILE" << PLIST_EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>${PLIST_NAME}</string>
    <key>ProgramArguments</key>
    <array>
        <string>${SCRAPYD_CMD}</string>
    </array>
    <key>WorkingDirectory</key>
    <string>${PROJECT_ROOT}</string>
    <key>RunAtLoad</key>
    <false/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>${PROJECT_ROOT}/logs/scrapyd.log</string>
    <key>StandardErrorPath</key>
    <string>${PROJECT_ROOT}/logs/scrapyd.error.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>$(dirname "$SCRAPYD_CMD"):/usr/local/bin:/usr/bin:/bin</string>
    </dict>
</dict>
</plist>
PLIST_EOF

    echo "✓ plist 파일 생성 완료: $PLIST_FILE"

    # launchctl 로드
    launchctl load "$PLIST_FILE" 2>/dev/null || launchctl unload "$PLIST_FILE" 2>/dev/null && launchctl load "$PLIST_FILE"
    echo "✓ launchctl 서비스 로드 완료"

    echo ""
    echo -e "${GREEN}✅ Scrapyd 서비스 설정 완료!${NC}"
    echo ""
    echo "서비스 제어 명령어:"
    echo "  시작: launchctl load $PLIST_FILE"
    echo "  중지: launchctl unload $PLIST_FILE"
    echo "  상태: launchctl list | grep $PLIST_NAME"
    echo "  로그: tail -f $PROJECT_ROOT/logs/scrapyd.log"
    echo ""
    echo "부팅 시 자동 시작 활성화:"
    echo "  plutil -replace RunAtLoad -bool true $PLIST_FILE"
    echo "  launchctl unload $PLIST_FILE && launchctl load $PLIST_FILE"

else
    # Linux: systemd 사용
    if [ "$MASTER_IP" == "localhost" ] || [ "$MASTER_IP" == "127.0.0.1" ]; then
        # 로컬 실행
        echo -e "${BLUE}로컬에서 서비스 파일 생성 중...${NC}"

        sudo tee /etc/systemd/system/cointicker-scrapyd.service > /dev/null << SERVICE_EOF
[Unit]
Description=CoinTicker Scrapyd Server
After=network.target

[Service]
Type=simple
User=$MASTER_USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=$PROJECT_DIR/venv/bin/scrapyd
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
        sudo systemctl enable cointicker-scrapyd
        echo "✓ 서비스 활성화 완료"

        # 서비스 상태 확인
        echo ""
        echo "서비스 상태:"
        sudo systemctl status cointicker-scrapyd --no-pager -l || true

    else
        # 원격 실행
        echo -e "${BLUE}원격 서버에서 서비스 파일 생성 중...${NC}"
        ssh "$MASTER_USER@$MASTER_IP" << EOF
            sudo tee /etc/systemd/system/cointicker-scrapyd.service > /dev/null << 'SERVICE_EOF'
[Unit]
Description=CoinTicker Scrapyd Server
After=network.target

[Service]
Type=simple
User=$MASTER_USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=$PROJECT_DIR/venv/bin/scrapyd
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
            sudo systemctl enable cointicker-scrapyd
            echo "✓ 서비스 활성화 완료"

            # 서비스 상태 확인
            echo ""
            echo "서비스 상태:"
            sudo systemctl status cointicker-scrapyd --no-pager -l || true
EOF
    fi

    echo ""
    echo -e "${GREEN}✅ Scrapyd 서비스 설정 완료!${NC}"
    echo ""
    echo "서비스 제어 명령어:"
    echo "  시작: sudo systemctl start cointicker-scrapyd"
    echo "  중지: sudo systemctl stop cointicker-scrapyd"
    echo "  상태: sudo systemctl status cointicker-scrapyd"
    echo "  로그: sudo journalctl -u cointicker-scrapyd -f"
    echo ""
fi

