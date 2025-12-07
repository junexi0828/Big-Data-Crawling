#!/bin/bash
# PICU GUI 애플리케이션 실행 스크립트

set -e

# 프로젝트 루트 (스크립트 디렉토리에서 상위로)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

# 통합 환경 설정 (PostgreSQL 기본값 포함)
if [ -f "$PROJECT_ROOT/scripts/setup_env.sh" ]; then
    source "$PROJECT_ROOT/scripts/setup_env.sh"
fi

# 가상환경 활성화 (PICU 루트 venv)
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "경고: 가상환경이 없습니다. 'bash scripts/start.sh'를 실행하여 설치하세요."
    exit 1
fi

# GUI를 백그라운드에서 실행
python cointicker/gui/main.py &
GUI_PID=$!

# 서비스가 시작되고 포트 파일을 생성할 때까지 대기 (약 15초)
echo "서비스 시작 중... 잠시 후 최종 접속 주소를 표시합니다."
sleep 15

# --- 최종 접속 주소 안내 ---
echo ""
echo -e "\033[1m\033[0;36m╔═════════════════════════════════════════════════════╗\033[0m"
echo -e "\033[1m\033[0;36m║   모든 서비스가 시작되었습니다. 아래 주소로 접속하세요.          ║\033[0m"
echo -e "\033[1m\033[0;36m╚═════════════════════════════════════════════════════╝\033[0m"
echo ""

# --- Backend ---
BACKEND_PORT_FILE="$PROJECT_ROOT/cointicker/config/.backend_port"
if [ -f "$BACKEND_PORT_FILE" ]; then
    BACKEND_PORT=$(cat "$BACKEND_PORT_FILE")
    echo -e "  - \033[1mBackend API:\033[0m http://localhost:$BACKEND_PORT"
    echo -e "  - \033[1mBackend Docs:\033[0m http://localhost:$BACKEND_PORT/docs"
else
    echo -e "  - \033[1mBackend API:\033[0m http://localhost:5000 (기본값, 실제 포트는 다를 수 있음)"
    echo -e "  - \033[1mBackend Docs:\033[0m http://localhost:5000/docs"
fi

# --- Frontend ---
# run_dev.sh 스크립트가 VITE_PORT 또는 PORT 환경 변수를 사용하거나 3000을 기본값으로 사용합니다.
# 사용자의 로그에서 3001 포트가 사용된 것을 확인했으므로, 해당 포트도 함께 안내합니다.
echo -e "  - \033[1mFrontend:\033[0m http://localhost:3000 또는 http://localhost:3001"

# --- Hadoop ---
if [ -n "$HADOOP_HOME" ]; then
    HDFS_PORT=$(python3 -c "
import xml.etree.ElementTree as ET; from pathlib import Path;
config_file=Path('${HADOOP_HOME}/etc/hadoop/hdfs-site.xml');
prop_name='dfs.namenode.http-address'; default='9870'; port=default;
if config_file.is_file():
    try:
        for p in ET.parse(config_file).getroot().findall('property'):
            if p.find('name') is not None and p.find('name').text == prop_name:
                val_tag = p.find('value');
                if val_tag is not None and val_tag.text:
                    val = val_tag.text;
                    port=val.split(':')[-1] if ':' in val else val;
                    break;
    except: pass;
print(port)" 2>/dev/null || echo "9870")

    YARN_PORT=$(python3 -c "
import xml.etree.ElementTree as ET; from pathlib import Path;
config_file=Path('${HADOOP_HOME}/etc/hadoop/yarn-site.xml');
prop_name='yarn.resourcemanager.webapp.address'; default='8088'; port=default;
if config_file.is_file():
    try:
        for p in ET.parse(config_file).getroot().findall('property'):
            if p.find('name') is not None and p.find('name').text == prop_name:
                val_tag = p.find('value');
                if val_tag is not None and val_tag.text:
                    val = val_tag.text;
                    port=val.split(':')[-1] if ':' in val else val;
                    break;
    except: pass;
print(port)" 2>/dev/null || echo "8088")

    echo -e "  - \033[1mHadoop NameNode:\033[0m http://localhost:$HDFS_PORT"
    echo -e "  - \033[1mHadoop ResourceManager:\033[0m http://localhost:$YARN_PORT"
else
    echo -e "  - \033[1mHadoop NameNode:\033[0m http://localhost:9870 (기본값)"
    echo -e "  - \033[1mHadoop ResourceManager:\033[0m http://localhost:8088 (기본값)"
fi
echo ""
echo -e "\033[0;33m참고: GUI가 종료되면 이 터미널도 함께 종료됩니다.\033[0m"
echo ""

# GUI 프로세스가 종료될 때까지 대기
wait $GUI_PID

