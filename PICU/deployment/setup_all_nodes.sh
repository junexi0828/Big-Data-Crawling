#!/bin/bash
# 모든 노드 배포 스크립트

set -e

# 색상 정의
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "=========================================="
echo "모든 노드 배포"
echo "=========================================="
echo ""

# Master Node 배포
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}Master Node 배포${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
bash "$PROJECT_ROOT/deployment/setup_master.sh"

# Worker Nodes 배포
for i in 1 2 3; do
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}Worker Node #$i 배포${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    bash "$PROJECT_ROOT/deployment/setup_worker.sh" "raspberry-worker$i" "192.168.0.10$i"
done

echo ""
echo "=========================================="
echo -e "${GREEN}✅ 모든 노드 배포 완료!${NC}"
echo "=========================================="
echo ""

