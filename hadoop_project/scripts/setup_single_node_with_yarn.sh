#!/bin/bash

# Hadoop Single-Node Cluster Mode Setup (with YARN) Script
# 강의 슬라이드 Page 13-14 기반

set -e  # 오류 발생 시 스크립트 중단

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 변수 설정
HADOOP_VERSION="3.4.1"
HADOOP_DIR="hadoop-${HADOOP_VERSION}"
HADOOP_TAR="${HADOOP_DIR}.tar.gz"
HADOOP_URL="https://dlcdn.apache.org/hadoop/common/hadoop-${HADOOP_VERSION}/${HADOOP_TAR}"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Hadoop Single-Node Cluster Mode Setup${NC}"
echo -e "${GREEN}(with YARN)${NC}"
echo -e "${GREEN}========================================${NC}"

# 1. Java 확인
echo -e "\n${YELLOW}[Step 1] Java 확인${NC}"
if ! command -v java &> /dev/null; then
    echo -e "${RED}Java가 설치되어 있지 않습니다.${NC}"
    echo -e "${YELLOW}JDK v8 또는 v11을 설치해주세요.${NC}"
    echo -e "${YELLOW}예시: sudo apt install openjdk-8-jdk${NC}"
    exit 1
fi

JAVA_VERSION=$(java -version 2>&1 | head -n 1)
echo -e "${GREEN}Java 버전: ${JAVA_VERSION}${NC}"

# 2. JAVA_HOME 확인 및 설정
echo -e "\n${YELLOW}[Step 2] JAVA_HOME 확인${NC}"
if [ -z "$JAVA_HOME" ]; then
    if [[ "$OSTYPE" == "darwin"* ]]; then
        JAVA_HOME=$(/usr/libexec/java_home 2>/dev/null || echo "")
    else
        JAVA_HOME=$(readlink -f /usr/bin/java | sed "s:bin/java::")
    fi

    if [ -z "$JAVA_HOME" ]; then
        echo -e "${RED}JAVA_HOME을 수동으로 설정해주세요.${NC}"
        echo -e "${YELLOW}예시: export JAVA_HOME=/usr/lib/jvm/bellsoft-java8-aarch64${NC}"
        exit 1
    fi
fi
echo -e "${GREEN}JAVA_HOME: ${JAVA_HOME}${NC}"

# 3. Hadoop 다운로드 및 압축 해제
echo -e "\n${YELLOW}[Step 3] Hadoop 다운로드 및 압축 해제${NC}"
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

cd "$HADOOP_DIR"

# 4. JAVA_HOME 설정
echo -e "\n${YELLOW}[Step 4] hadoop-env.sh에 JAVA_HOME 설정${NC}"
HADOOP_ENV_FILE="./etc/hadoop/hadoop-env.sh"

if grep -q "^export JAVA_HOME=" "$HADOOP_ENV_FILE"; then
    sed -i.bak "s|^export JAVA_HOME=.*|export JAVA_HOME=${JAVA_HOME}|" "$HADOOP_ENV_FILE"
else
    echo "export JAVA_HOME=${JAVA_HOME}" >> "$HADOOP_ENV_FILE"
fi
echo -e "${GREEN}JAVA_HOME 설정 완료${NC}"

# 5. core-site.xml 설정
echo -e "\n${YELLOW}[Step 5] core-site.xml 설정${NC}"
CORE_SITE="./etc/hadoop/core-site.xml"

cat > "$CORE_SITE" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
    <property>
        <name>fs.defaultFS</name>
        <value>hdfs://localhost:9000</value>
    </property>
</configuration>
EOF

echo -e "${GREEN}core-site.xml 설정 완료${NC}"

# 6. hdfs-site.xml 설정
echo -e "\n${YELLOW}[Step 6] hdfs-site.xml 설정${NC}"
HDFS_SITE="./etc/hadoop/hdfs-site.xml"

cat > "$HDFS_SITE" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
    <property>
        <name>dfs.replication</name>
        <value>1</value>
    </property>
</configuration>
EOF

echo -e "${GREEN}hdfs-site.xml 설정 완료${NC}"

# 7. mapred-site.xml 설정
echo -e "\n${YELLOW}[Step 7] mapred-site.xml 설정${NC}"
MAPRED_SITE="./etc/hadoop/mapred-site.xml"
HADOOP_HOME_FULL=$(pwd)

cat > "$MAPRED_SITE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
    <property>
        <name>mapreduce.framework.name</name>
        <value>yarn</value>
    </property>
    <property>
        <name>mapreduce.application.classpath</name>
        <value>${HADOOP_HOME_FULL}/share/hadoop/mapreduce/*</value>
    </property>
</configuration>
EOF

echo -e "${GREEN}mapred-site.xml 설정 완료${NC}"

# 8. yarn-site.xml 설정
echo -e "\n${YELLOW}[Step 8] yarn-site.xml 설정${NC}"
YARN_SITE="./etc/hadoop/yarn-site.xml"

cat > "$YARN_SITE" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
    <property>
        <name>yarn.nodemanager.aux-services</name>
        <value>mapreduce_shuffle</value>
    </property>
    <property>
        <name>yarn.nodemanager.aux-services.mapreduce.shuffle.class</name>
        <value>org.apache.hadoop.mapred.ShuffleHandler</value>
    </property>
    <property>
        <name>yarn.resourcemanager.hostname</name>
        <value>localhost</value>
    </property>
</configuration>
EOF

echo -e "${GREEN}yarn-site.xml 설정 완료${NC}"

# 9. SSH 설정
echo -e "\n${YELLOW}[Step 9] 패스워드 없는 SSH 로그인 설정${NC}"

if [ ! -f ~/.ssh/id_rsa ]; then
    echo -e "${YELLOW}SSH 키 생성 중...${NC}"
    ssh-keygen -t rsa -P "" -f ~/.ssh/id_rsa
fi

if [ ! -f ~/.ssh/authorized_keys ] || ! grep -q "$(cat ~/.ssh/id_rsa.pub)" ~/.ssh/authorized_keys 2>/dev/null; then
    cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
    chmod 0600 ~/.ssh/authorized_keys
    echo -e "${GREEN}SSH 키 설정 완료${NC}"
else
    echo -e "${GREEN}SSH 키가 이미 설정되어 있습니다.${NC}"
fi

# 10. NameNode 포맷
echo -e "\n${YELLOW}[Step 10] NameNode 포맷${NC}"
read -p "NameNode를 포맷하시겠습니까? (기존 데이터가 삭제됩니다) [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    bin/hdfs namenode -format -force
    echo -e "${GREEN}NameNode 포맷 완료${NC}"
else
    echo -e "${YELLOW}NameNode 포맷 건너뜀${NC}"
fi

# 11. 완료 메시지
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}설정 완료!${NC}"
echo -e "${GREEN}========================================${NC}"

echo -e "\n${YELLOW}다음 단계:${NC}"
echo -e "${GREEN}# HDFS 데몬 시작${NC}"
echo "sbin/start-dfs.sh"
echo ""
echo -e "${GREEN}# YARN 데몬 시작${NC}"
echo "sbin/start-yarn.sh"
echo ""
echo -e "${GREEN}# 웹 인터페이스${NC}"
echo "NameNode: http://localhost:9870/"
echo "ResourceManager: http://localhost:8088/"
echo ""
echo -e "${GREEN}# 프로세스 확인${NC}"
echo "jps"
echo ""
echo -e "${GREEN}# HDFS 디렉토리 생성 및 파일 업로드${NC}"
echo "bin/hdfs dfs -mkdir -p /user/\$(whoami)/input"
echo "bin/hdfs dfs -put *.txt input"
echo ""
echo -e "${GREEN}# Wordcount 실행${NC}"
echo "bin/hdfs dfs -rm -r output  # 기존 output 삭제"
echo "bin/hadoop jar share/hadoop/mapreduce/hadoop-mapreduce-examples-${HADOOP_VERSION}.jar wordcount input output"
echo ""
echo -e "${GREEN}# 결과 확인${NC}"
echo "bin/hdfs dfs -cat output/*"
echo ""
echo -e "${GREEN}# 데몬 중지${NC}"
echo "sbin/stop-yarn.sh && sbin/stop-dfs.sh"

