#!/bin/bash

# NameNode 배포 스크립트
# 마스터 노드(bigpie1)에 Hadoop 설치 및 설정

set -e

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 변수 설정
HADOOP_VERSION="3.4.1"
HADOOP_TAR="hadoop-${HADOOP_VERSION}.tar.gz"
HADOOP_URL="https://dlcdn.apache.org/hadoop/common/hadoop-${HADOOP_VERSION}/${HADOOP_TAR}"
HADOOP_INSTALL_DIR="/opt/hadoop"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}NameNode 배포 스크립트${NC}"
echo -e "${GREEN}========================================${NC}"

# 1. Java 확인
if ! command -v java &> /dev/null; then
    echo -e "${RED}Java가 설치되어 있지 않습니다.${NC}"
    exit 1
fi

# 2. Hadoop 다운로드
echo -e "\n${YELLOW}[1/5] Hadoop 다운로드${NC}"
cd /tmp
if [ ! -f "$HADOOP_TAR" ]; then
    wget "$HADOOP_URL"
fi

# 3. Hadoop 설치
echo -e "\n${YELLOW}[2/5] Hadoop 설치${NC}"
sudo mkdir -p "$HADOOP_INSTALL_DIR"
sudo tar -zxvf "$HADOOP_TAR" -C /opt/
sudo mv "/opt/hadoop-${HADOOP_VERSION}" "$HADOOP_INSTALL_DIR"
sudo chown -R $(whoami):$(whoami) "$HADOOP_INSTALL_DIR"

# 4. 설정 파일 배포
echo -e "\n${YELLOW}[3/5] 설정 파일 배포${NC}"
if [ -d "$PROJECT_ROOT/config" ]; then
    # 설정 파일 템플릿 복사
    cp "$PROJECT_ROOT/config/core-site.xml.example" "$HADOOP_INSTALL_DIR/etc/hadoop/core-site.xml"
    cp "$PROJECT_ROOT/config/hdfs-site.xml.example" "$HADOOP_INSTALL_DIR/etc/hadoop/hdfs-site.xml"
    cp "$PROJECT_ROOT/config/mapred-site.xml.example" "$HADOOP_INSTALL_DIR/etc/hadoop/mapred-site.xml"
    cp "$PROJECT_ROOT/config/yarn-site.xml.example" "$HADOOP_INSTALL_DIR/etc/hadoop/yarn-site.xml"

    echo -e "${YELLOW}⚠️  설정 파일을 환경에 맞게 수정하세요:${NC}"
    echo "   - $HADOOP_INSTALL_DIR/etc/hadoop/core-site.xml"
    echo "   - $HADOOP_INSTALL_DIR/etc/hadoop/hdfs-site.xml"
    echo "   - $HADOOP_INSTALL_DIR/etc/hadoop/mapred-site.xml"
    echo "   - $HADOOP_INSTALL_DIR/etc/hadoop/yarn-site.xml"
fi

# 5. 환경 변수 설정
echo -e "\n${YELLOW}[4/5] 환경 변수 설정${NC}"
if ! grep -q "HADOOP_HOME" ~/.bashrc 2>/dev/null; then
    cat >> ~/.bashrc << EOF

# Hadoop Environment Variables
export PDSH_RCMD_TYPE=ssh
export HADOOP_HOME=${HADOOP_INSTALL_DIR}
export PATH=\$PATH:\$HADOOP_HOME/bin:\$HADOOP_HOME/sbin
EOF
    source ~/.bashrc
fi

# 6. JAVA_HOME 설정
echo -e "\n${YELLOW}[5/5] JAVA_HOME 설정${NC}"
if [ -z "$JAVA_HOME" ]; then
    JAVA_HOME=$(readlink -f /usr/bin/java | sed "s:bin/java::")
fi

HADOOP_ENV_FILE="$HADOOP_INSTALL_DIR/etc/hadoop/hadoop-env.sh"
if grep -q "^export JAVA_HOME=" "$HADOOP_ENV_FILE"; then
    sed -i.bak "s|^export JAVA_HOME=.*|export JAVA_HOME=${JAVA_HOME}|" "$HADOOP_ENV_FILE"
else
    echo "export JAVA_HOME=${JAVA_HOME}" >> "$HADOOP_ENV_FILE"
fi

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}NameNode 배포 완료!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}다음 단계:${NC}"
echo "1. 설정 파일 수정 (Multi-Node 모드에 맞게)"
echo "2. master 및 workers 파일 생성"
echo "3. NameNode 포맷: hdfs namenode -format -force"
echo "4. DataNode 배포: ./deployment/deploy_datanodes.sh"

