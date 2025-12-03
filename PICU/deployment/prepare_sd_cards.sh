#!/bin/bash

# SD 카드 준비 헬퍼 스크립트
# CoinTicker Hadoop Cluster - SD 카드별 user-data 설정
#
# 사용법:
#   1. Ubuntu 이미지를 SD 카드에 굽기
#   2. SD 카드를 Mac에 연결
#   3. 이 스크립트 실행: ./prepare_sd_cards.sh
#   4. 메뉴에서 노드 선택
#   5. SD 카드를 꺼내서 라즈베리파이에 삽입

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# SD 카드 마운트 경로 (자동 감지)
BOOT_MOUNT=""

# 함수: SD 카드 마운트 경로 찾기
find_boot_mount() {
    if [ -d "/Volumes/bootfs" ]; then
        BOOT_MOUNT="/Volumes/bootfs"
    elif [ -d "/Volumes/system-boot" ]; then
        BOOT_MOUNT="/Volumes/system-boot"
    else
        return 1
    fi
    return 0
}

# 함수: SD 카드가 마운트되었는지 확인
check_mount() {
    if ! find_boot_mount; then
        echo -e "${RED}✗ SD 카드가 마운트되지 않았습니다${NC}"
        echo ""
        echo "다음을 확인하세요:"
        echo "  1. SD 카드가 Mac에 연결되어 있는지"
        echo "  2. /Volumes/bootfs 또는 /Volumes/system-boot가 마운트되었는지"
        echo ""
        return 1
    fi
    echo -e "${GREEN}✓ SD 카드 감지됨: $BOOT_MOUNT${NC}"
    return 0
}

# 함수: 현재 hostname 확인
check_current_hostname() {
    if [ -f "$BOOT_MOUNT/user-data" ]; then
        local current_hostname=$(grep "^hostname:" "$BOOT_MOUNT/user-data" | awk '{print $2}')
        echo -e "${CYAN}📌 현재 설정된 hostname: ${YELLOW}$current_hostname${NC}"
    else
        echo -e "${RED}✗ user-data 파일을 찾을 수 없습니다${NC}"
    fi
}

# 함수: user-data 파일 교체
replace_user_data() {
    local node_type=$1
    local source_file=""
    local node_name=""

    case $node_type in
        "master")
            node_name="raspberry-master"
            # worker1을 master로 변환
            if [ -f "$BOOT_MOUNT/worker-configs/user-data-worker1" ]; then
                sed 's/hostname: raspberry-worker1/hostname: raspberry-master/' \
                    "$BOOT_MOUNT/worker-configs/user-data-worker1" > "$BOOT_MOUNT/user-data"
            else
                echo -e "${RED}✗ worker-configs/user-data-worker1을 찾을 수 없습니다${NC}"
                return 1
            fi
            ;;
        "worker1")
            node_name="raspberry-worker1"
            source_file="$BOOT_MOUNT/worker-configs/user-data-worker1"
            ;;
        "worker2")
            node_name="raspberry-worker2"
            source_file="$BOOT_MOUNT/worker-configs/user-data-worker2"
            ;;
        "worker3")
            node_name="raspberry-worker3"
            source_file="$BOOT_MOUNT/worker-configs/user-data-worker3"
            ;;
        *)
            echo -e "${RED}✗ 잘못된 노드 타입입니다${NC}"
            return 1
            ;;
    esac

    # 워커 노드는 파일 복사
    if [ -n "$source_file" ]; then
        if [ -f "$source_file" ]; then
            cp "$source_file" "$BOOT_MOUNT/user-data"
        else
            echo -e "${RED}✗ $source_file을 찾을 수 없습니다${NC}"
            return 1
        fi
    fi

    echo -e "${GREEN}✓ ${node_name}로 설정 완료${NC}"
    return 0
}

# 배너 출력
clear
echo -e "${CYAN}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                                                    ║${NC}"
echo -e "${CYAN}║       CoinTicker Hadoop Cluster                    ║${NC}"
echo -e "${CYAN}║       SD 카드 준비 도구                            ║${NC}"
echo -e "${CYAN}║                                                    ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════╝${NC}"
echo ""

# 메인 메뉴
while true; do
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}어느 노드용 SD 카드를 준비하시겠습니까?${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "  ${GREEN}1)${NC} Master Node       (raspberry-master)   ${CYAN}192.168.0.100${NC}"
    echo "  ${GREEN}2)${NC} Worker Node 1     (raspberry-worker1)  ${CYAN}192.168.0.101${NC}"
    echo "  ${GREEN}3)${NC} Worker Node 2     (raspberry-worker2)  ${CYAN}192.168.0.102${NC}"
    echo "  ${GREEN}4)${NC} Worker Node 3     (raspberry-worker3)  ${CYAN}192.168.0.103${NC}"
    echo ""
    echo "  ${YELLOW}5)${NC} 현재 설정 확인"
    echo "  ${RED}0)${NC} 종료"
    echo ""
    read -p "$(echo -e ${YELLOW}선택 \(0-5\): ${NC})" choice

    case $choice in
        1)
            echo ""
            echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo -e "${YELLOW}📦 Master Node 설정 중...${NC}"
            echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

            if check_mount; then
                if replace_user_data "master"; then
                    echo ""
                    check_current_hostname
                    echo ""
                    echo -e "${GREEN}╔════════════════════════════════════════════════╗${NC}"
                    echo -e "${GREEN}║  ✓ Master Node SD 카드 준비 완료!             ║${NC}"
                    echo -e "${GREEN}╚════════════════════════════════════════════════╝${NC}"
                    echo ""
                    echo -e "${YELLOW}다음 단계:${NC}"
                    echo "  1. SD 카드를 안전하게 제거"
                    echo "  2. 라즈베리파이 #1 (Master)에 삽입"
                    echo "  3. 전원 켜기"
                    echo ""
                fi
            fi
            ;;
        2)
            echo ""
            echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo -e "${YELLOW}📦 Worker Node 1 설정 중...${NC}"
            echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

            if check_mount; then
                if replace_user_data "worker1"; then
                    echo ""
                    check_current_hostname
                    echo ""
                    echo -e "${GREEN}╔════════════════════════════════════════════════╗${NC}"
                    echo -e "${GREEN}║  ✓ Worker Node 1 SD 카드 준비 완료!           ║${NC}"
                    echo -e "${GREEN}╚════════════════════════════════════════════════╝${NC}"
                    echo ""
                    echo -e "${YELLOW}다음 단계:${NC}"
                    echo "  1. SD 카드를 안전하게 제거"
                    echo "  2. 라즈베리파이 #2 (Worker 1)에 삽입"
                    echo "  3. 전원 켜기"
                    echo ""
                fi
            fi
            ;;
        3)
            echo ""
            echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo -e "${YELLOW}📦 Worker Node 2 설정 중...${NC}"
            echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

            if check_mount; then
                if replace_user_data "worker2"; then
                    echo ""
                    check_current_hostname
                    echo ""
                    echo -e "${GREEN}╔════════════════════════════════════════════════╗${NC}"
                    echo -e "${GREEN}║  ✓ Worker Node 2 SD 카드 준비 완료!           ║${NC}"
                    echo -e "${GREEN}╚════════════════════════════════════════════════╝${NC}"
                    echo ""
                    echo -e "${YELLOW}다음 단계:${NC}"
                    echo "  1. SD 카드를 안전하게 제거"
                    echo "  2. 라즈베리파이 #3 (Worker 2)에 삽입"
                    echo "  3. 전원 켜기"
                    echo ""
                fi
            fi
            ;;
        4)
            echo ""
            echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo -e "${YELLOW}📦 Worker Node 3 설정 중...${NC}"
            echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

            if check_mount; then
                if replace_user_data "worker3"; then
                    echo ""
                    check_current_hostname
                    echo ""
                    echo -e "${GREEN}╔════════════════════════════════════════════════╗${NC}"
                    echo -e "${GREEN}║  ✓ Worker Node 3 SD 카드 준비 완료!           ║${NC}"
                    echo -e "${GREEN}╚════════════════════════════════════════════════╝${NC}"
                    echo ""
                    echo -e "${YELLOW}다음 단계:${NC}"
                    echo "  1. SD 카드를 안전하게 제거"
                    echo "  2. 라즈베리파이 #4 (Worker 3)에 삽입"
                    echo "  3. 전원 켜기"
                    echo ""
                fi
            fi
            ;;
        5)
            echo ""
            echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo -e "${YELLOW}🔍 현재 SD 카드 설정 확인${NC}"
            echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo ""
            if check_mount; then
                check_current_hostname
                echo ""
                if [ -d "$BOOT_MOUNT/worker-configs" ]; then
                    echo -e "${GREEN}✓ worker-configs 디렉토리 존재${NC}"
                    echo ""
                    echo "사용 가능한 설정 파일:"
                    ls -1 "$BOOT_MOUNT/worker-configs/" | grep "user-data" | while read file; do
                        echo "  - $file"
                    done
                else
                    echo -e "${RED}✗ worker-configs 디렉토리를 찾을 수 없습니다${NC}"
                fi
            fi
            ;;
        0)
            echo ""
            echo -e "${GREEN}╔════════════════════════════════════════════════╗${NC}"
            echo -e "${GREEN}║  SD 카드 준비 도구를 종료합니다                ║${NC}"
            echo -e "${GREEN}╚════════════════════════════════════════════════╝${NC}"
            echo ""
            exit 0
            ;;
        *)
            echo ""
            echo -e "${RED}✗ 잘못된 선택입니다. 0-5 사이의 숫자를 입력하세요.${NC}"
            ;;
    esac

    # 계속 진행할지 묻기
    echo ""
    read -p "$(echo -e ${YELLOW}다른 SD 카드를 준비하시겠습니까? \(y/n\): ${NC})" continue_choice
    if [[ ! $continue_choice =~ ^[Yy]$ ]]; then
        echo ""
        echo -e "${GREEN}╔════════════════════════════════════════════════╗${NC}"
        echo -e "${GREEN}║  SD 카드 준비 완료!                           ║${NC}"
        echo -e "${GREEN}╚════════════════════════════════════════════════╝${NC}"
        echo ""
        exit 0
    fi
    clear
    echo -e "${CYAN}╔════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║       CoinTicker Hadoop Cluster                    ║${NC}"
    echo -e "${CYAN}║       SD 카드 준비 도구                            ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════╝${NC}"
done
