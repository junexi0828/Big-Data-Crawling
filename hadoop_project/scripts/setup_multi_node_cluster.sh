#!/bin/bash

# Hadoop Multi-Node Cluster Mode Setup Script
# 강의 슬라이드 Page 15-23 기반
# NameNode: bigpie1, DataNode: bigpie2, bigpie3, bigpie4

set -e  # 오류 발생 시 스크립트 중단

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 변수 설정 (사용자 환경에 맞게 수정 필요)
HADOOP_VERSION="3.4.1"
HADOOP_DIR="hadoop-${HADOOP_VERSION}"
HADOOP_TAR="${HADOOP_DIR}.tar.gz"
HADOOP_URL="https://dlcdn.apache.org/hadoop/common/hadoop-${HADOOP_VERSION}/${HADOOP_TAR}"
HADOOP_INSTALL_DIR="/opt/hadoop"
HADOOP_TMP_DIR="/opt/hadoop_tmp"

# 노드 설정 (사용자 환경에 맞게 수정 필요)
NAMENODE="bigpie1"
DATANODES=("bigpie2" "bigpie3" "bigpie4")

# IP 주소 설정 (사용자 환경에 맞게 수정 필요)
declare -A NODE_IPS=(
    ["bigpie1"]="192.168.0.40"
    ["bigpie2"]="192.168.0.41"
    ["bigpie3"]="192.168.0.42"
    ["bigpie4"]="192.168.0.43"
)

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Hadoop Multi-Node Cluster Mode Setup${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "${YELLOW}NameNode: ${NAMENODE}${NC}"
echo -e "${YELLOW}DataNodes: ${DATANODES[*]}${NC}"

# 현재 호스트 확인
CURRENT_HOST=$(hostname)
if [ "$CURRENT_HOST" != "$NAMENODE" ]; then
    echo -e "${RED}이 스크립트는 NameNode (${NAMENODE})에서 실행해야 합니다.${NC}"
    echo -e "${RED}현재 호스트: ${CURRENT_HOST}${NC}"
    exit 1
fi

# 클러스터 관리 함수
function others {
    grep "bigpie" /etc/hosts | awk '{print $2}' | grep -v $(hostname)
}

function cluster_run {
    for x in $(others); do
        echo -e "${YELLOW}Executing on ${x}: $@${NC}"
        ssh $x "$@" || true
    done
    echo -e "${YELLOW}Executing on localhost: $@${NC}"
    $@
}

function cluster_scp {
    for x in $(others); do
        echo -e "${YELLOW}Copying to ${x}: $1${NC}"
        cat $1 | ssh $x "sudo tee $1" > /dev/null 2>&1 || true
    done
}

# 1. 사전 준비사항 확인
echo -e "\n${YELLOW}[Step 1] 사전 준비사항 확인${NC}"
echo -e "${YELLOW}Java, ssh, pdsh 설치 확인 중...${NC}"

if ! command -v java &> /dev/null; then
    echo -e "${RED}Java가 설치되어 있지 않습니다.${NC}"
    exit 1
fi

if ! command -v ssh &> /dev/null; then
    echo -e "${YELLOW}ssh 설치 중...${NC}"
    sudo apt install -y ssh
fi

if ! command -v pdsh &> /dev/null; then
    echo -e "${YELLOW}pdsh 설치 중...${NC}"
    sudo apt install -y pdsh
fi

echo -e "${GREEN}사전 준비사항 확인 완료${NC}"

# 2. /etc/hosts 파일 편집 안내
echo -e "\n${YELLOW}[Step 2] /etc/hosts 파일 편집${NC}"
echo -e "${YELLOW}각 노드에서 /etc/hosts 파일을 편집해야 합니다.${NC}"
echo -e "${YELLOW}다음 내용을 추가하세요:${NC}"
echo ""
for node in "${!NODE_IPS[@]}"; do
    echo "${NODE_IPS[$node]} $node"
done
echo ""
read -p "계속하시겠습니까? [y/N]: " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

# 3. SSH 설정
echo -e "\n${YELLOW}[Step 3] SSH 설정${NC}"

# SSH config 파일 생성
if [ ! -f ~/.ssh/config ]; then
    echo -e "${YELLOW}SSH config 파일 생성 중...${NC}"
    mkdir -p ~/.ssh
    for node in "${!NODE_IPS[@]}"; do
        cat >> ~/.ssh/config << EOF
Host $node
    User $(whoami)
    Hostname ${NODE_IPS[$node]}

EOF
    done
    chmod 600 ~/.ssh/config
    echo -e "${GREEN}SSH config 파일 생성 완료${NC}"
fi

# SSH 키 생성 (없는 경우)
if [ ! -f ~/.ssh/id_rsa ]; then
    echo -e "${YELLOW}SSH 키 생성 중...${NC}"
    ssh-keygen -t rsa -P "" -f ~/.ssh/id_rsa
fi

# authorized_keys에 추가
if [ ! -f ~/.ssh/authorized_keys ] || ! grep -q "$(cat ~/.ssh/id_rsa.pub)" ~/.ssh/authorized_keys 2>/dev/null; then
    cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
    chmod 0600 ~/.ssh/authorized_keys
fi

# 다른 노드로 SSH config 복사
echo -e "${YELLOW}다른 노드로 SSH config 복사 중...${NC}"
for node in "${DATANODES[@]}"; do
    scp ~/.ssh/config $node:~/.ssh/config 2>/dev/null || echo -e "${YELLOW}${node}로 복사 실패 (계속 진행)${NC}"
done

# 4. 클러스터 관리 함수 추가
echo -e "\n${YELLOW}[Step 4] 클러스터 관리 함수 추가${NC}"
if ! grep -q "function others" ~/.bashrc 2>/dev/null; then
    cat >> ~/.bashrc << 'EOF'

# Hadoop Cluster Management Functions
function others {
    grep "bigpie" /etc/hosts | awk '{print $2}' | grep -v $(hostname)
}

function cluster_run {
    for x in $(others); do ssh $x "$@"; done
    $@
}

function cluster_reboot {
    cluster_run sudo shutdown -r now
}

function cluster_shutdown {
    cluster_run sudo shutdown now
}

function cluster_scp {
    for x in $(others); do
        cat $1 | ssh $x "sudo tee $1" > /dev/null 2>&1
    done
}
EOF
    echo -e "${GREEN}클러스터 관리 함수 추가 완료${NC}"
    source ~/.bashrc
else
    echo -e "${GREEN}클러스터 관리 함수가 이미 존재합니다.${NC}"
fi

# 5. Hadoop 다운로드 및 설치
echo -e "\n${YELLOW}[Step 5] Hadoop 다운로드 및 설치${NC}"
if [ ! -f "$HADOOP_TAR" ]; then
    echo -e "${YELLOW}Hadoop 다운로드 중...${NC}"
    wget "$HADOOP_URL" || {
        echo -e "${RED}Hadoop 다운로드 실패${NC}"
        exit 1
    }
fi

if [ ! -d "$HADOOP_DIR" ]; then
    tar -zxvf "$HADOOP_TAR"
fi

echo -e "${YELLOW}Hadoop을 ${HADOOP_INSTALL_DIR}에 설치 중...${NC}"
sudo mkdir -p "$HADOOP_INSTALL_DIR"
sudo tar -zxvf "$HADOOP_TAR" -C /opt/
sudo mv "/opt/${HADOOP_DIR}" "$HADOOP_INSTALL_DIR"
sudo chown -R $(whoami):$(whoami) "$HADOOP_INSTALL_DIR"
echo -e "${GREEN}Hadoop 설치 완료${NC}"

# 6. 환경 변수 설정
echo -e "\n${YELLOW}[Step 6] 환경 변수 설정${NC}"
if ! grep -q "HADOOP_HOME" ~/.bashrc 2>/dev/null; then
    cat >> ~/.bashrc << EOF

# Hadoop Environment Variables
export PDSH_RCMD_TYPE=ssh
export HADOOP_HOME=${HADOOP_INSTALL_DIR}
export PATH=\$PATH:\$HADOOP_HOME/bin:\$HADOOP_HOME/sbin
EOF
    source ~/.bashrc
    echo -e "${GREEN}환경 변수 설정 완료${NC}"
else
    echo -e "${GREEN}환경 변수가 이미 설정되어 있습니다.${NC}"
fi

# 7. JAVA_HOME 설정
echo -e "\n${YELLOW}[Step 7] JAVA_HOME 설정${NC}"
if [ -z "$JAVA_HOME" ]; then
    JAVA_HOME=$(readlink -f /usr/bin/java | sed "s:bin/java::")
fi

HADOOP_ENV_FILE="${HADOOP_INSTALL_DIR}/etc/hadoop/hadoop-env.sh"
if grep -q "^export JAVA_HOME=" "$HADOOP_ENV_FILE"; then
    sudo sed -i.bak "s|^export JAVA_HOME=.*|export JAVA_HOME=${JAVA_HOME}|" "$HADOOP_ENV_FILE"
else
    echo "export JAVA_HOME=${JAVA_HOME}" | sudo tee -a "$HADOOP_ENV_FILE" > /dev/null
fi
echo -e "${GREEN}JAVA_HOME 설정 완료: ${JAVA_HOME}${NC}"

# 8. Hadoop 파일 복사
echo -e "\n${YELLOW}[Step 8] Hadoop 파일을 다른 노드로 복사${NC}"
echo -e "${YELLOW}임시 디렉토리 생성 중...${NC}"
cluster_run sudo mkdir -p "${HADOOP_TMP_DIR}/hdfs"
cluster_run sudo chown -R $(whoami):$(whoami) "${HADOOP_TMP_DIR}"
cluster_run sudo mkdir -p "${HADOOP_INSTALL_DIR}"
cluster_run sudo chown -R $(whoami):$(whoami) "${HADOOP_INSTALL_DIR}"

echo -e "${YELLOW}Hadoop 파일 복사 중...${NC}"
for node in "${DATANODES[@]}"; do
    echo -e "${YELLOW}${node}로 복사 중...${NC}"
    rsync -avxP "${HADOOP_INSTALL_DIR}" $node:/opt/ || echo -e "${YELLOW}${node}로 복사 실패${NC}"
done

# .bashrc 복사
cluster_scp ~/.bashrc

echo -e "${GREEN}파일 복사 완료${NC}"

# 9. 설정 파일 생성 안내
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}기본 설정 완료!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "\n${YELLOW}다음 단계:${NC}"
echo -e "${YELLOW}1. 설정 파일 템플릿을 사용하여 다음 파일들을 편집하세요:${NC}"
echo "   - ${HADOOP_INSTALL_DIR}/etc/hadoop/core-site.xml"
echo "   - ${HADOOP_INSTALL_DIR}/etc/hadoop/hdfs-site.xml"
echo "   - ${HADOOP_INSTALL_DIR}/etc/hadoop/mapred-site.xml"
echo "   - ${HADOOP_INSTALL_DIR}/etc/hadoop/yarn-site.xml"
echo ""
echo -e "${YELLOW}2. 설정 파일을 다른 노드로 복사:${NC}"
echo "   cluster_scp ${HADOOP_INSTALL_DIR}/etc/hadoop/core-site.xml"
echo "   cluster_scp ${HADOOP_INSTALL_DIR}/etc/hadoop/hdfs-site.xml"
echo "   cluster_scp ${HADOOP_INSTALL_DIR}/etc/hadoop/mapred-site.xml"
echo "   cluster_scp ${HADOOP_INSTALL_DIR}/etc/hadoop/yarn-site.xml"
echo ""
echo -e "${YELLOW}3. master 및 workers 파일 생성:${NC}"
echo "   echo '${NAMENODE}' | sudo tee ${HADOOP_INSTALL_DIR}/etc/hadoop/master"
echo "   echo -e '${DATANODES[0]}\n${DATANODES[1]}\n${DATANODES[2]}' | sudo tee ${HADOOP_INSTALL_DIR}/etc/hadoop/workers"
echo ""
echo -e "${YELLOW}4. NameNode 포맷 및 시작:${NC}"
echo "   hdfs namenode -format -force"
echo "   start-dfs.sh && start-yarn.sh"
echo ""
echo -e "${YELLOW}5. 데몬 확인:${NC}"
echo "   jps"
echo "   cluster_run jps"

