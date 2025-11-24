#!/bin/bash

# DataNode 배포 스크립트
# NameNode에서 실행하여 모든 DataNode에 Hadoop 배포

set -e

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 변수 설정 (사용자 환경에 맞게 수정)
NAMENODE="bigpie1"
DATANODES=("bigpie2" "bigpie3" "bigpie4")
HADOOP_INSTALL_DIR="/opt/hadoop"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}DataNode 배포 스크립트${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "${YELLOW}NameNode: ${NAMENODE}${NC}"
echo -e "${YELLOW}DataNodes: ${DATANODES[*]}${NC}"

# 현재 호스트 확인
CURRENT_HOST=$(hostname)
if [ "$CURRENT_HOST" != "$NAMENODE" ]; then
    echo -e "${RED}이 스크립트는 NameNode (${NAMENODE})에서 실행해야 합니다.${NC}"
    exit 1
fi

# 클러스터 관리 함수
function others {
    grep "bigpie" /etc/hosts | awk '{print $2}' | grep -v $(hostname)
}

# 1. NameNode에 Hadoop이 설치되어 있는지 확인
echo -e "\n${YELLOW}[1/4] NameNode Hadoop 설치 확인${NC}"
if [ ! -d "$HADOOP_INSTALL_DIR" ]; then
    echo -e "${RED}NameNode에 Hadoop이 설치되어 있지 않습니다.${NC}"
    echo -e "${YELLOW}먼저 deploy_namenode.sh를 실행하세요.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Hadoop 설치 확인: ${HADOOP_INSTALL_DIR}${NC}"

# 2. DataNode 디렉토리 생성
echo -e "\n${YELLOW}[2/4] DataNode 디렉토리 생성${NC}"
for node in "${DATANODES[@]}"; do
    echo -e "${YELLOW}${node}에 디렉토리 생성 중...${NC}"
    ssh $node "sudo mkdir -p /opt/hadoop_tmp/hdfs/datanode && sudo mkdir -p $HADOOP_INSTALL_DIR && sudo chown -R $(whoami):$(whoami) /opt/hadoop_tmp && sudo chown -R $(whoami):$(whoami) $HADOOP_INSTALL_DIR" || {
        echo -e "${RED}${node} 디렉토리 생성 실패${NC}"
    }
done

# 3. Hadoop 파일 복사
echo -e "\n${YELLOW}[3/4] Hadoop 파일 복사${NC}"
for node in "${DATANODES[@]}"; do
    echo -e "${YELLOW}${node}로 복사 중... (시간이 걸릴 수 있습니다)${NC}"
    rsync -avxP --exclude='logs' --exclude='*.log' "$HADOOP_INSTALL_DIR" $node:/opt/ || {
        echo -e "${RED}${node}로 복사 실패${NC}"
    }
done

# 4. 설정 파일 배포
echo -e "\n${YELLOW}[4/4] 설정 파일 배포${NC}"
for node in "${DATANODES[@]}"; do
    echo -e "${YELLOW}${node}에 설정 파일 복사 중...${NC}"
    scp "$HADOOP_INSTALL_DIR/etc/hadoop/core-site.xml" $node:"$HADOOP_INSTALL_DIR/etc/hadoop/" || true
    scp "$HADOOP_INSTALL_DIR/etc/hadoop/hdfs-site.xml" $node:"$HADOOP_INSTALL_DIR/etc/hadoop/" || true
    scp "$HADOOP_INSTALL_DIR/etc/hadoop/mapred-site.xml" $node:"$HADOOP_INSTALL_DIR/etc/hadoop/" || true
    scp "$HADOOP_INSTALL_DIR/etc/hadoop/yarn-site.xml" $node:"$HADOOP_INSTALL_DIR/etc/hadoop/" || true
done

# 5. 환경 변수 배포
echo -e "\n${YELLOW}[5/5] 환경 변수 배포${NC}"
if [ -f ~/.bashrc ] && grep -q "HADOOP_HOME" ~/.bashrc; then
    for node in "${DATANODES[@]}"; do
        echo -e "${YELLOW}${node}에 환경 변수 복사 중...${NC}"
        scp ~/.bashrc $node:~/.bashrc || true
    done
fi

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}DataNode 배포 완료!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}배포된 노드:${NC}"
for node in "${DATANODES[@]}"; do
    echo "   - $node: $HADOOP_INSTALL_DIR"
done
echo ""
echo -e "${YELLOW}다음 단계:${NC}"
echo "1. 모든 노드에서 Hadoop 버전 확인:"
echo "   ssh bigpie2 'hadoop version'"
echo "2. NameNode 포맷: hdfs namenode -format -force"
echo "3. 클러스터 시작: start-dfs.sh && start-yarn.sh"

