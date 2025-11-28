#!/bin/bash
# CoinTicker GUI 실행 스크립트

set -e

# 프로젝트 루트 확인
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

# 가상환경 활성화
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "경고: 가상환경이 없습니다. 'bash gui/scripts/install.sh'를 실행하여 설치하세요."
fi

# GUI 실행
python gui/main.py

