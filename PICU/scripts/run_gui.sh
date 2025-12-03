#!/bin/bash
# PICU GUI 애플리케이션 실행 스크립트

set -e

# 프로젝트 루트 (스크립트 디렉토리에서 상위로)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

# 가상환경 활성화 (PICU 루트 venv)
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "경고: 가상환경이 없습니다. 'bash scripts/start.sh'를 실행하여 설치하세요."
    exit 1
fi

# GUI 실행
python cointicker/gui/main.py

