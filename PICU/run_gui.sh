#!/bin/bash
# PICU GUI 애플리케이션 실행 스크립트

set -e

# 프로젝트 루트 확인
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_ROOT"

# 가상환경 활성화
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "경고: 가상환경이 없습니다. 'bash setup_venv.sh'를 실행하여 설정하세요."
    exit 1
fi

# GUI 실행
python cointicker/gui/main.py

