#!/bin/bash

# Hadoop 설치 스크립트
# Hadoop 바이너리 다운로드 및 기본 설정

# 색상 코드
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 프로젝트 루트 디렉토리
PROJECT_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$PROJECT_ROOT"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Hadoop 설치${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# ==============================================================================
# 1. Java 확인
# ==============================================================================

echo -e "${YELLOW}[1/4] Java 확인 중...${NC}"

JAVA_INSTALLED=true
if command -v java &> /dev/null; then
    JAVA_VERSION=$(java -version 2>&1 | head -n 1 | cut -d'"' -f2)
    echo -e "${GREEN}✅ Java: $JAVA_VERSION${NC}"

    # Java 버전 확인 (v8 이상 필요)
    JAVA_MAJOR=$(echo "$JAVA_VERSION" | cut -d'.' -f1)
    if [ "$JAVA_MAJOR" -lt 8 ]; then
        echo -e "${RED}❌ Java 8 이상이 필요합니다. (현재: $JAVA_VERSION)${NC}"
        JAVA_INSTALLED=false
    fi
else
    echo -e "${RED}❌ Java가 설치되지 않았습니다.${NC}"
    echo "   Hadoop은 Java JDK v8 이상이 필요합니다."
    JAVA_INSTALLED=false
fi

if [ "$JAVA_INSTALLED" = false ]; then
    echo ""
    echo -e "${YELLOW}Java 설치 방법:${NC}"
    echo "   macOS: brew install openjdk@8"
    echo "   Ubuntu: sudo apt install openjdk-8-jdk"
    echo ""
    echo -e "${YELLOW}⚠️  Java를 설치한 후 다시 실행하세요.${NC}"
    exit 1
fi

# JAVA_HOME 확인
if [ -z "$JAVA_HOME" ]; then
    echo -e "${YELLOW}⚠️  JAVA_HOME이 설정되지 않았습니다.${NC}"

    # macOS에서 JAVA_HOME 찾기
    if [[ "$OSTYPE" == "darwin"* ]]; then
        JAVA_HOME=$(/usr/libexec/java_home 2>/dev/null || echo "")
        if [ -n "$JAVA_HOME" ]; then
            echo -e "${GREEN}✅ JAVA_HOME 자동 감지: $JAVA_HOME${NC}"
            export JAVA_HOME
        fi
    else
        # Linux에서 JAVA_HOME 찾기
        JAVA_HOME=$(readlink -f /usr/bin/java | sed "s:bin/java::")
        if [ -n "$JAVA_HOME" ]; then
            echo -e "${GREEN}✅ JAVA_HOME 자동 감지: $JAVA_HOME${NC}"
            export JAVA_HOME
        fi
    fi

    if [ -z "$JAVA_HOME" ]; then
        echo -e "${YELLOW}⚠️  JAVA_HOME을 수동으로 설정해야 할 수 있습니다.${NC}"
    fi
else
    echo -e "${GREEN}✅ JAVA_HOME: $JAVA_HOME${NC}"
fi

echo ""

# ==============================================================================
# 2. Hadoop 다운로드
# ==============================================================================

echo -e "${YELLOW}[2/4] Hadoop 다운로드 확인 중...${NC}"

HADOOP_VERSION="3.4.1"
HADOOP_DIR="hadoop-${HADOOP_VERSION}"
HADOOP_TAR="${HADOOP_DIR}.tar.gz"
HADOOP_URL="https://dlcdn.apache.org/hadoop/common/hadoop-${HADOOP_VERSION}/${HADOOP_TAR}"

# hadoop_project 디렉토리 확인
if [ ! -d "hadoop_project" ]; then
    echo -e "${YELLOW}⚠️  hadoop_project 디렉토리가 없습니다.${NC}"
    echo "   hadoop_project 디렉토리를 생성합니다..."
    mkdir -p hadoop_project
fi

cd hadoop_project

# 이미 다운로드되어 있는지 확인
if [ -d "$HADOOP_DIR" ]; then
    echo -e "${GREEN}✅ Hadoop이 이미 다운로드되어 있습니다: $HADOOP_DIR${NC}"
else
    if [ -f "$HADOOP_TAR" ]; then
        echo -e "${YELLOW}압축 파일이 있습니다. 압축 해제 중...${NC}"
        tar -zxvf "$HADOOP_TAR"
        echo -e "${GREEN}✅ 압축 해제 완료${NC}"
    else
        echo -e "${YELLOW}Hadoop 다운로드 중... (약 300MB)${NC}"
        if command -v wget &> /dev/null; then
            wget "$HADOOP_URL" || {
                echo -e "${RED}❌ Hadoop 다운로드 실패${NC}"
                echo "   수동으로 다운로드: $HADOOP_URL"
                exit 1
            }
        elif command -v curl &> /dev/null; then
            curl -L -o "$HADOOP_TAR" "$HADOOP_URL" || {
                echo -e "${RED}❌ Hadoop 다운로드 실패${NC}"
                echo "   수동으로 다운로드: $HADOOP_URL"
                exit 1
            }
        else
            echo -e "${RED}❌ wget 또는 curl이 필요합니다.${NC}"
            exit 1
        fi

        echo -e "${GREEN}✅ 다운로드 완료${NC}"
        echo -e "${YELLOW}압축 해제 중...${NC}"
        tar -zxvf "$HADOOP_TAR"
        echo -e "${GREEN}✅ 압축 해제 완료${NC}"
    fi
fi

echo ""

# ==============================================================================
# 3. 기본 설정 (Local Mode)
# ==============================================================================

echo -e "${YELLOW}[3/4] 기본 설정 중 (Local Mode)...${NC}"

cd "$HADOOP_DIR"

# hadoop-env.sh에 JAVA_HOME 설정
HADOOP_ENV_FILE="./etc/hadoop/hadoop-env.sh"

if [ -n "$JAVA_HOME" ]; then
    if grep -q "^export JAVA_HOME=" "$HADOOP_ENV_FILE" 2>/dev/null; then
        # 기존 JAVA_HOME 업데이트
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i.bak "s|^export JAVA_HOME=.*|export JAVA_HOME=${JAVA_HOME}|" "$HADOOP_ENV_FILE"
        else
            sed -i.bak "s|^export JAVA_HOME=.*|export JAVA_HOME=${JAVA_HOME}|" "$HADOOP_ENV_FILE"
        fi
        echo -e "${GREEN}✅ JAVA_HOME 업데이트 완료${NC}"
    else
        # JAVA_HOME 추가
        echo "export JAVA_HOME=${JAVA_HOME}" >> "$HADOOP_ENV_FILE"
        echo -e "${GREEN}✅ JAVA_HOME 추가 완료${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  JAVA_HOME이 설정되지 않아 hadoop-env.sh를 수동으로 편집해야 합니다.${NC}"
fi

# 버전 확인
echo -e "${YELLOW}Hadoop 버전 확인 중...${NC}"
if ./bin/hadoop version &> /dev/null; then
    HADOOP_VER=$(./bin/hadoop version 2>&1 | head -n 1)
    echo -e "${GREEN}✅ $HADOOP_VER${NC}"
else
    echo -e "${YELLOW}⚠️  Hadoop 버전 확인 실패${NC}"
fi

echo ""

# ==============================================================================
# 4. 설치 완료 및 안내
# ==============================================================================

echo -e "${YELLOW}[4/4] 설치 완료 확인 중...${NC}"

cd "$PROJECT_ROOT"

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✅ Hadoop 설치 완료!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

echo -e "${CYAN}📋 설치 요약:${NC}"
echo ""
echo "   • Hadoop 버전: $HADOOP_VERSION"
echo "   • 설치 위치: $(pwd)/hadoop_project/$HADOOP_DIR"
echo "   • Java 버전: $JAVA_VERSION"
if [ -n "$JAVA_HOME" ]; then
    echo "   • JAVA_HOME: $JAVA_HOME"
fi
echo ""

echo -e "${YELLOW}🚀 다음 단계:${NC}"
echo ""
echo "1. Local Mode 테스트:"
echo "   ${GREEN}cd hadoop_project/$HADOOP_DIR${NC}"
echo "   ${GREEN}mkdir input && echo 'Hello Hadoop' > input/test.txt${NC}"
echo "   ${GREEN}./bin/hadoop jar share/hadoop/mapreduce/hadoop-mapreduce-examples-${HADOOP_VERSION}.jar wordcount input output${NC}"
echo "   ${GREEN}cat output/part-r-00000${NC}"
echo ""
echo "2. Single-Node Cluster Mode 설정:"
echo "   ${GREEN}cd hadoop_project${NC}"
echo "   ${GREEN}./scripts/setup_single_node_wo_yarn.sh${NC}"
echo "   또는"
echo "   ${GREEN}./scripts/setup_single_node_with_yarn.sh${NC}"
echo ""
echo "3. 상세 설정 가이드:"
echo "   ${GREEN}cat hadoop_project/docs/SETUP_GUIDE.md${NC}"
echo ""

echo -e "${YELLOW}📝 참고사항:${NC}"
echo ""
echo "- Hadoop은 기본적으로 Local Mode로 설정됩니다."
echo "- Cluster Mode를 사용하려면 추가 설정이 필요합니다."
echo "- 자세한 내용은 ${GREEN}hadoop_project/docs/SETUP_GUIDE.md${NC}를 참조하세요."
echo ""

echo -e "${GREEN}Happy Hadoop! 🐘${NC}"

