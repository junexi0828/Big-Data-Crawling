#!/bin/bash

# 전체 클러스터 배포 스크립트
# NameNode와 DataNode를 순차적으로 배포

set -e

# 색상 정의
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Hadoop 클러스터 전체 배포${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 1. NameNode 배포
echo -e "${YELLOW}[1/2] NameNode 배포${NC}"
bash "$PROJECT_ROOT/deployment/deploy_namenode.sh"

echo ""
read -p "NameNode 배포가 완료되었습니다. DataNode 배포를 계속하시겠습니까? [y/N]: " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # 2. DataNode 배포
    echo -e "\n${YELLOW}[2/2] DataNode 배포${NC}"
    bash "$PROJECT_ROOT/deployment/deploy_datanodes.sh"

    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN}전체 클러스터 배포 완료!${NC}"
    echo -e "${GREEN}========================================${NC}"
else
    echo -e "${YELLOW}DataNode 배포를 건너뜁니다.${NC}"
    echo -e "${YELLOW}나중에 deploy_datanodes.sh를 실행하세요.${NC}"
fi

