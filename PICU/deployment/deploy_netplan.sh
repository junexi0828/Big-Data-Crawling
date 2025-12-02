#!/bin/bash

# Netplan 설정 배포 스크립트
# CoinTicker Hadoop Cluster - Network Configuration Deployment

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 노드 정보
MASTER="192.168.0.100"
WORKERS=("192.168.0.101" "192.168.0.102" "192.168.0.103")

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  CoinTicker Cluster - Netplan Deployment${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 함수: 노드에 netplan 배포
deploy_netplan() {
    local node=$1
    local config_file=$2
    local node_name=$3

    echo -e "${YELLOW}📦 Deploying netplan to $node_name ($node)...${NC}"

    # 설정 파일 존재 확인
    if [ ! -f "$config_file" ]; then
        echo -e "${RED}✗ Configuration file not found: $config_file${NC}"
        return 1
    fi

    # 노드 연결 확인
    if ! ping -c 1 -W 2 $node > /dev/null 2>&1; then
        echo -e "${RED}✗ Cannot reach $node_name ($node)${NC}"
        return 1
    fi

    # 설정 파일 업로드
    scp "$config_file" ubuntu@$node:/tmp/netplan-config.yaml || {
        echo -e "${RED}✗ Failed to upload config to $node_name${NC}"
        return 1
    }

    # 설정 파일 적용
    ssh ubuntu@$node "sudo mv /tmp/netplan-config.yaml /etc/netplan/99-static-ip.yaml && \
                       sudo chmod 600 /etc/netplan/99-static-ip.yaml && \
                       sudo netplan apply" || {
        echo -e "${RED}✗ Failed to apply netplan on $node_name${NC}"
        return 1
    }

    echo -e "${GREEN}✓ Successfully deployed to $node_name${NC}"
    echo ""
    return 0
}

# 메인 메뉴
echo "Select deployment option:"
echo ""
echo "  ${GREEN}1)${NC} Deploy to Master Node only"
echo "  ${GREEN}2)${NC} Deploy to Worker Node 1"
echo "  ${GREEN}3)${NC} Deploy to Worker Node 2"
echo "  ${GREEN}4)${NC} Deploy to Worker Node 3"
echo "  ${GREEN}5)${NC} Deploy to All Nodes"
echo "  ${RED}0)${NC} Exit"
echo ""
read -p "$(echo -e ${YELLOW}Select option \(0-5\): ${NC})" choice

case $choice in
    1)
        deploy_netplan "$MASTER" "$SCRIPT_DIR/netplan-master.yaml" "Master"
        ;;
    2)
        deploy_netplan "${WORKERS[0]}" "$SCRIPT_DIR/netplan-worker1.yaml" "Worker1"
        ;;
    3)
        deploy_netplan "${WORKERS[1]}" "$SCRIPT_DIR/netplan-worker2.yaml" "Worker2"
        ;;
    4)
        deploy_netplan "${WORKERS[2]}" "$SCRIPT_DIR/netplan-worker3.yaml" "Worker3"
        ;;
    5)
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${YELLOW}Deploying to all nodes...${NC}"
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""

        deploy_netplan "$MASTER" "$SCRIPT_DIR/netplan-master.yaml" "Master"
        deploy_netplan "${WORKERS[0]}" "$SCRIPT_DIR/netplan-worker1.yaml" "Worker1"
        deploy_netplan "${WORKERS[1]}" "$SCRIPT_DIR/netplan-worker2.yaml" "Worker2"
        deploy_netplan "${WORKERS[2]}" "$SCRIPT_DIR/netplan-worker3.yaml" "Worker3"

        echo -e "${GREEN}╔════════════════════════════════════════════════╗${NC}"
        echo -e "${GREEN}║  ✓ All nodes configured successfully!         ║${NC}"
        echo -e "${GREEN}╚════════════════════════════════════════════════╝${NC}"
        ;;
    0)
        echo -e "${GREEN}Exiting...${NC}"
        exit 0
        ;;
    *)
        echo -e "${RED}✗ Invalid option${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Network configuration deployment complete!    ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Test connectivity: ping 192.168.0.100"
echo "  2. SSH test: ssh ubuntu@raspberry-master"
echo "  3. Check WiFi status: ssh ubuntu@raspberry-master 'ip addr show wlan0'"
echo ""
