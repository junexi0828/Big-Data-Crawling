#!/bin/bash
# Master Node (라즈베리파이 #1) 배포 스크립트

set -e

# 색상 정의
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 설정
MASTER_HOST="${MASTER_HOST:-raspberry-master}"
MASTER_USER="${MASTER_USER:-ubuntu}"
MASTER_IP="${MASTER_IP:-192.168.0.100}"
PROJECT_DIR="/home/ubuntu/cointicker"
HADOOP_INSTALL_DIR="/opt/hadoop"

# Hadoop 경로 확인 (상대 경로 또는 환경 변수)
HADOOP_ROOT="${HADOOP_ROOT:-$(cd "$(dirname "$0")/../../hadoop_project/hadoop-3.4.1" 2>/dev/null && pwd)}"

echo "=========================================="
echo "Master Node 배포"
echo "=========================================="
echo ""
echo "대상: $MASTER_USER@$MASTER_IP"
echo ""

# 프로젝트 루트 확인
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

# 1. 코드 배포
echo -e "${BLUE}[1/3] 코드 배포 중...${NC}"
rsync -avz --exclude 'venv' --exclude '__pycache__' --exclude '*.pyc' \
    "$PROJECT_ROOT/cointicker/master-node/" \
    "$MASTER_USER@$MASTER_IP:$PROJECT_DIR/master-node/"

rsync -avz --exclude 'venv' --exclude '__pycache__' --exclude '*.pyc' \
    "$PROJECT_ROOT/cointicker/shared/" \
    "$MASTER_USER@$MASTER_IP:$PROJECT_DIR/shared/"

rsync -avz --exclude 'venv' --exclude '__pycache__' --exclude '*.pyc' \
    "$PROJECT_ROOT/cointicker/config/" \
    "$MASTER_USER@$MASTER_IP:$PROJECT_DIR/config/"

# requirements 파일 전송 (base.txt와 master.txt)
rsync -avz \
    "$PROJECT_ROOT/requirements/base.txt" \
    "$PROJECT_ROOT/requirements/master.txt" \
    "$MASTER_USER@$MASTER_IP:$PROJECT_DIR/"

echo -e "${GREEN}✅ 코드 배포 완료${NC}"
echo ""

# 2. 가상환경 설정
echo -e "${BLUE}[2/3] 가상환경 설정 중...${NC}"
ssh "$MASTER_USER@$MASTER_IP" << EOF
    cd $PROJECT_DIR

    # 가상환경 생성
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi

    # 가상환경 활성화 및 의존성 설치
    source venv/bin/activate
    pip install --upgrade pip

    # requirements 파일 설치
    if [ -f "$PROJECT_DIR/master.txt" ]; then
        pip install -r $PROJECT_DIR/master.txt
        echo "✓ Installed from master.txt"
    else
        echo "✗ master.txt not found in $PROJECT_DIR"
        exit 1
    fi
EOF

echo -e "${GREEN}✅ 가상환경 설정 완료${NC}"
echo ""

# 3. Hadoop 배포 (NameNode용)
echo -e "${BLUE}[3/4] Hadoop 배포 중...${NC}"
if [ -d "$HADOOP_ROOT" ]; then
    # Hadoop 바이너리 전송
    rsync -avz --delete \
        --exclude='logs' \
        --exclude='*.log' \
        "$HADOOP_ROOT/" \
        "$MASTER_USER@$MASTER_IP:$HADOOP_INSTALL_DIR/"

    echo -e "${GREEN}✅ Hadoop 바이너리 배포 완료${NC}"

    # Hadoop 설정 파일 생성
    ssh "$MASTER_USER@$MASTER_IP" << EOF
        mkdir -p $HADOOP_INSTALL_DIR/etc/hadoop

        # core-site.xml
        cat > $HADOOP_INSTALL_DIR/etc/hadoop/core-site.xml << 'CORE_EOF'
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

        # hdfs-site.xml
        cat > $HADOOP_INSTALL_DIR/etc/hadoop/hdfs-site.xml << 'HDFS_EOF'
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

        # yarn-site.xml
        cat > $HADOOP_INSTALL_DIR/etc/hadoop/yarn-site.xml << 'YARN_EOF'
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
        cat > $HADOOP_INSTALL_DIR/etc/hadoop/mapred-site.xml << 'MAPRED_EOF'
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

        # 환경 변수 설정
        if ! grep -q "HADOOP_HOME" ~/.bashrc; then
            cat >> ~/.bashrc << 'BASHRC_EOF'

# Hadoop Environment
export HADOOP_HOME=/opt/hadoop
export HADOOP_CONF_DIR=\$HADOOP_HOME/etc/hadoop
export YARN_CONF_DIR=\$HADOOP_HOME/etc/hadoop
export PATH=\$PATH:\$HADOOP_HOME/bin:\$HADOOP_HOME/sbin
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-arm64
BASHRC_EOF
        fi

        # 권한 설정
        sudo chown -R ubuntu:ubuntu $HADOOP_INSTALL_DIR
        chmod +x $HADOOP_INSTALL_DIR/bin/*
        chmod +x $HADOOP_INSTALL_DIR/sbin/*

        # 디렉토리 생성
        sudo mkdir -p /opt/hadoop_tmp/hdfs/namenode
        sudo chown -R ubuntu:ubuntu /opt/hadoop_tmp

        echo "✓ Hadoop 설정 완료"
EOF

    echo -e "${GREEN}✅ Hadoop 설정 파일 배포 완료${NC}"
else
    echo -e "${YELLOW}⚠️  Hadoop 경로를 찾을 수 없습니다: $HADOOP_ROOT${NC}"
    echo -e "${YELLOW}   환경 변수 HADOOP_ROOT를 설정하거나 hadoop_project/hadoop-3.4.1 경로를 확인하세요${NC}"
fi
echo ""

# 4. 서비스 설정
echo -e "${BLUE}[4/4] 서비스 설정 중...${NC}"
ssh "$MASTER_USER@$MASTER_IP" << EOF
    cd $PROJECT_DIR

    # systemd 서비스 파일 생성 (선택적)
    # sudo systemctl enable cointicker-master
    # sudo systemctl start cointicker-master
EOF

echo -e "${GREEN}✅ Master Node 배포 완료!${NC}"
echo ""

