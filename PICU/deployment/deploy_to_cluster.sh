#!/bin/bash

# CoinTicker Cluster Deployment Script
# Usage: ./deploy_to_cluster.sh [node_ip]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR/../cointicker"
# Hadoop 경로 확인 (상대 경로 또는 환경 변수)
HADOOP_ROOT="${HADOOP_ROOT:-$(cd "$SCRIPT_DIR/../../hadoop_project/hadoop-3.4.1" 2>/dev/null && pwd)}"

# 색상 코드
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 노드 IP 배열
MASTER="192.168.0.100"
WORKERS=("192.168.0.101" "192.168.0.102" "192.168.0.103")
ALL_NODES=("$MASTER" "${WORKERS[@]}")

# 함수: 배너 출력
print_banner() {
    echo -e "${GREEN}"
    echo "======================================"
    echo "  CoinTicker Cluster Deployment"
    echo "======================================"
    echo -e "${NC}"
}

# 함수: 노드 연결 확인
check_node() {
    local node=$1
    echo -e "${YELLOW}Checking connection to $node...${NC}"
    if ssh -o ConnectTimeout=5 -o BatchMode=yes ubuntu@$node "echo 2>&1" >/dev/null 2>&1; then
        echo -e "${GREEN}✓ Connected to $node${NC}"
        return 0
    else
        echo -e "${RED}✗ Failed to connect to $node${NC}"
        return 1
    fi
}

# 함수: 프로젝트 배포
deploy_project() {
    local node=$1
    local is_master=false

    # Master 노드인지 확인
    if [ "$node" == "$MASTER" ]; then
        is_master=true
    fi

    echo -e "${YELLOW}Deploying project to $node...${NC}"

    # 프로젝트 디렉토리 전송
    rsync -avz --delete \
        --exclude='.git' \
        --exclude='*.pyc' \
        --exclude='__pycache__' \
        --exclude='venv' \
        --exclude='*.log' \
        --exclude='.pytest_cache' \
        --exclude='node_modules' \
        "$PROJECT_ROOT/" \
        ubuntu@$node:/home/ubuntu/cointicker/

    # requirements 파일 전송 (base.txt와 master.txt 또는 worker.txt)
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PICU_ROOT="$SCRIPT_DIR/.."

    if [ "$is_master" = true ]; then
        # Master Node: base.txt와 master.txt 전송
        rsync -avz \
            "$PICU_ROOT/requirements/base.txt" \
            "$PICU_ROOT/requirements/master.txt" \
            ubuntu@$node:/home/ubuntu/cointicker/
        echo -e "${GREEN}✓ Requirements files (base.txt, master.txt) deployed${NC}"
    else
        # Worker Node: base.txt와 worker.txt 전송
        rsync -avz \
            "$PICU_ROOT/requirements/base.txt" \
            "$PICU_ROOT/requirements/worker.txt" \
            ubuntu@$node:/home/ubuntu/cointicker/
        echo -e "${GREEN}✓ Requirements files (base.txt, worker.txt) deployed${NC}"
    fi

    echo -e "${GREEN}✓ Project deployed to $node${NC}"
}

# 함수: 가상환경 설정
setup_venv() {
    local node=$1
    local is_master=false

    # Master 노드인지 확인
    if [ "$node" == "$MASTER" ]; then
        is_master=true
    fi

    echo -e "${YELLOW}Setting up virtual environment on $node...${NC}"

    if [ "$is_master" = true ]; then
        ssh ubuntu@$node << 'EOF'
cd /home/ubuntu/cointicker

# 가상환경 생성
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# 의존성 설치 (Master용)
source venv/bin/activate
pip install --upgrade pip setuptools wheel
if [ -f "master.txt" ]; then
    pip install -r master.txt
    echo "✓ Master dependencies installed"
else
    echo "✗ master.txt not found"
    exit 1
fi
EOF
    else
        ssh ubuntu@$node << 'EOF'
cd /home/ubuntu/cointicker

# 가상환경 생성
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# 의존성 설치 (Worker용)
source venv/bin/activate
pip install --upgrade pip setuptools wheel
if [ -f "worker.txt" ]; then
    pip install -r worker.txt
    echo "✓ Worker dependencies installed"
else
    echo "✗ worker.txt not found"
    exit 1
fi
EOF
    fi

    echo -e "${GREEN}✓ Virtual environment ready on $node${NC}"
}

# 함수: Hadoop 배포 (Master와 Worker 모두)
deploy_hadoop() {
    local node=$1
    local is_master=false

    if [ "$node" == "$MASTER" ]; then
        is_master=true
        echo -e "${YELLOW}Deploying Hadoop to master node $node (NameNode)...${NC}"
    else
        echo -e "${YELLOW}Deploying Hadoop to worker node $node (DataNode)...${NC}"
    fi

    if [ ! -d "$HADOOP_ROOT" ]; then
        echo -e "${RED}✗ Hadoop 경로를 찾을 수 없습니다: $HADOOP_ROOT${NC}"
        echo -e "${YELLOW}   환경 변수 HADOOP_ROOT를 설정하거나 hadoop_project/hadoop-3.4.1 경로를 확인하세요${NC}"
        return 1
    fi

    # Hadoop 바이너리 전송
    rsync -avz --delete \
        --exclude='logs' \
        --exclude='*.log' \
        "$HADOOP_ROOT/" \
        ubuntu@$node:/opt/hadoop/

    # Hadoop 설정 파일 생성
    if [ "$is_master" = true ]; then
        # Master Node (NameNode) 설정
        ssh ubuntu@$node << 'EOF'
mkdir -p /opt/hadoop/etc/hadoop

# core-site.xml
cat > /opt/hadoop/etc/hadoop/core-site.xml << 'CORE_EOF'
<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
    <property>
        <name>fs.defaultFS</name>
        <value>hdfs://raspberry-master:9000</value>
        <description>기본 파일시스템 URI</description>
    </property>
</configuration>
CORE_EOF

# hdfs-site.xml (NameNode 포함)
cat > /opt/hadoop/etc/hadoop/hdfs-site.xml << 'HDFS_EOF'
<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
    <property>
        <name>dfs.replication</name>
        <value>3</value>
        <description>데이터 블록 복제 팩터</description>
    </property>
    <property>
        <name>dfs.datanode.data.dir</name>
        <value>/opt/hadoop_tmp/hdfs/datanode</value>
        <description>DataNode 데이터 디렉토리</description>
    </property>
    <property>
        <name>dfs.namenode.name.dir</name>
        <value>/opt/hadoop_tmp/hdfs/namenode</value>
        <description>NameNode 메타데이터 디렉토리</description>
    </property>
</configuration>
HDFS_EOF
EOF
    else
        # Worker Node (DataNode) 설정
        ssh ubuntu@$node << 'EOF'
mkdir -p /opt/hadoop/etc/hadoop

# core-site.xml
cat > /opt/hadoop/etc/hadoop/core-site.xml << 'CORE_EOF'
<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
    <property>
        <name>fs.defaultFS</name>
        <value>hdfs://raspberry-master:9000</value>
        <description>기본 파일시스템 URI</description>
    </property>
</configuration>
CORE_EOF

# hdfs-site.xml (DataNode만)
cat > /opt/hadoop/etc/hadoop/hdfs-site.xml << 'HDFS_EOF'
<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
    <property>
        <name>dfs.replication</name>
        <value>3</value>
        <description>데이터 블록 복제 팩터</description>
    </property>
    <property>
        <name>dfs.datanode.data.dir</name>
        <value>/opt/hadoop_tmp/hdfs/datanode</value>
        <description>DataNode 데이터 디렉토리</description>
    </property>
</configuration>
HDFS_EOF
EOF
    fi

    # yarn-site.xml과 mapred-site.xml (공통)
    ssh ubuntu@$node << 'EOF'
# yarn-site.xml
cat > /opt/hadoop/etc/hadoop/yarn-site.xml << 'YARN_EOF'
<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
    <property>
        <name>yarn.nodemanager.aux-services</name>
        <value>mapreduce_shuffle</value>
        <description>NodeManager 보조 서비스</description>
    </property>
    <property>
        <name>yarn.nodemanager.aux-services.mapreduce.shuffle.class</name>
        <value>org.apache.hadoop.mapred.ShuffleHandler</value>
        <description>Shuffle 핸들러 클래스</description>
    </property>
    <property>
        <name>yarn.resourcemanager.hostname</name>
        <value>raspberry-master</value>
        <description>ResourceManager 호스트명</description>
    </property>
</configuration>
YARN_EOF

# mapred-site.xml
cat > /opt/hadoop/etc/hadoop/mapred-site.xml << 'MAPRED_EOF'
<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
    <property>
        <name>mapreduce.framework.name</name>
        <value>yarn</value>
        <description>MapReduce 프레임워크 이름 (yarn 사용)</description>
    </property>
    <property>
        <name>mapreduce.application.classpath</name>
        <value>/opt/hadoop/share/hadoop/mapreduce/*:/opt/hadoop/share/hadoop/mapreduce/lib/*</value>
        <description>MapReduce 애플리케이션 클래스패스</description>
    </property>
</configuration>
MAPRED_EOF
EOF

    # 환경 변수 및 권한 설정
    if [ "$is_master" = true ]; then
        # Master Node: NameNode 디렉토리도 생성
        ssh ubuntu@$node << 'EOF'
# .bashrc에 Hadoop 환경 변수 추가
if ! grep -q "HADOOP_HOME" ~/.bashrc; then
    cat >> ~/.bashrc << 'BASHRC_EOF'

# Hadoop Environment
export HADOOP_HOME=/opt/hadoop
export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
export YARN_CONF_DIR=$HADOOP_HOME/etc/hadoop
export PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-arm64
BASHRC_EOF
    echo "✓ Hadoop environment variables added"
fi

# 권한 설정
sudo chown -R ubuntu:ubuntu /opt/hadoop
chmod +x /opt/hadoop/bin/*
chmod +x /opt/hadoop/sbin/*

# 디렉토리 생성 (NameNode + DataNode)
sudo mkdir -p /opt/hadoop_tmp/hdfs/namenode
sudo mkdir -p /opt/hadoop_tmp/hdfs/datanode
sudo chown -R ubuntu:ubuntu /opt/hadoop_tmp

echo "✓ Hadoop permissions and directories set"
EOF
    else
        # Worker Node: DataNode 디렉토리만 생성
        ssh ubuntu@$node << 'EOF'
# .bashrc에 Hadoop 환경 변수 추가
if ! grep -q "HADOOP_HOME" ~/.bashrc; then
    cat >> ~/.bashrc << 'BASHRC_EOF'

# Hadoop Environment
export HADOOP_HOME=/opt/hadoop
export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
export YARN_CONF_DIR=$HADOOP_HOME/etc/hadoop
export PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-arm64
BASHRC_EOF
    echo "✓ Hadoop environment variables added"
fi

# 권한 설정
sudo chown -R ubuntu:ubuntu /opt/hadoop
chmod +x /opt/hadoop/bin/*
chmod +x /opt/hadoop/sbin/*

# 디렉토리 생성 (DataNode만)
sudo mkdir -p /opt/hadoop_tmp/hdfs/datanode
sudo chown -R ubuntu:ubuntu /opt/hadoop_tmp

echo "✓ Hadoop permissions and directories set"
EOF
    fi

    echo -e "${GREEN}✓ Hadoop deployed to $node${NC}"
}

# 함수: 전체 클러스터 배포
deploy_all() {
    echo -e "${YELLOW}Deploying to all cluster nodes...${NC}"

    # 마스터 노드
    echo -e "\n${GREEN}=== Master Node ($MASTER) ===${NC}"
    check_node $MASTER || exit 1
    deploy_project $MASTER
    setup_venv $MASTER
    deploy_hadoop $MASTER

    # 워커 노드들
    for worker in "${WORKERS[@]}"; do
        echo -e "\n${GREEN}=== Worker Node ($worker) ===${NC}"
        if check_node $worker; then
            deploy_project $worker
            setup_venv $worker
            deploy_hadoop $worker
        else
            echo -e "${RED}Skipping $worker (not reachable)${NC}"
        fi
    done

    echo -e "\n${GREEN}✓ Cluster deployment completed!${NC}"
}

# 함수: 단일 노드 배포
deploy_single() {
    local node=$1
    echo -e "${YELLOW}Deploying to single node $node...${NC}"

    check_node $node || exit 1
    deploy_project $node
    setup_venv $node
    deploy_hadoop $node

    echo -e "${GREEN}✓ Deployment to $node completed!${NC}"
}

# 메인 스크립트
print_banner

if [ $# -eq 0 ]; then
    # 인자 없으면 전체 클러스터 배포
    echo "No node specified. Deploying to all nodes..."
    deploy_all
else
    # 특정 노드만 배포
    deploy_single $1
fi

echo -e "\n${GREEN}Deployment finished!${NC}"
echo -e "Next steps:"
echo -e "  1. SSH to node: ${YELLOW}ssh ubuntu@$MASTER${NC}"
echo -e "  2. Activate venv: ${YELLOW}source /home/ubuntu/cointicker/venv/bin/activate${NC}"
echo -e "  3. Run project: ${YELLOW}python main.py${NC}"
