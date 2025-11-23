#!/bin/bash

# 🚀 Big Data 프로젝트 통합 설치 스크립트
# Kafka, Scrapy, Selenium 프로젝트의 모든 의존성을 설치합니다.

# set -e 제거: 일부 패키지 설치 실패 시에도 계속 진행

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

# ==============================================================================
# 호환 버전 자동 찾기 함수들
# ==============================================================================

# Python 버전 정보 추출
get_python_version() {
    python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null
}

# pip를 사용하여 호환되는 최신 버전 찾기
find_compatible_version() {
    local package_name=$1
    local min_version=$2

    # pip index를 사용하여 호환되는 최신 버전 찾기
    local compatible_version=$(scrapy_env/bin/pip index versions "$package_name" 2>/dev/null | \
        grep -E "^\s+[0-9]+\.[0-9]+\.[0-9]+" | \
        head -1 | \
        sed 's/^[[:space:]]*//' | \
        cut -d' ' -f1)

    if [ -z "$compatible_version" ]; then
        # pip index가 실패하면 최신 버전 시도
        compatible_version=$(scrapy_env/bin/pip install "${package_name}==999.0.0" --dry-run 2>&1 | \
            grep -oE "from versions: .*" | \
            sed 's/from versions: //' | \
            tr ',' '\n' | \
            sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | \
            grep -E "^[0-9]+\.[0-9]+\.[0-9]+" | \
            sort -V -r | \
            head -1)
    fi

    echo "$compatible_version"
}

# 패키지 설치 시도 (여러 버전 시도)
install_with_fallback() {
    local package_spec=$1
    # 패키지명 추출 (버전 제약 제거)
    local package_name=$(echo "$package_spec" | sed 's/[>=<].*$//' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    # Python import용 이름 (하이픈을 언더스코어로 변환)
    local import_name=$(echo "$package_name" | sed 's/-/_/g')
    local requested_version=$(echo "$package_spec" | grep -oE "[>=<]+[0-9.]+" | head -1 || echo "")

    echo "   📦 $package_spec 설치 시도 중..."

    # 먼저 요청된 버전으로 시도
    if scrapy_env/bin/pip install "$package_spec" --quiet 2>/dev/null; then
        # 설치 성공 확인
        if scrapy_env/bin/python3 -c "import $import_name" 2>/dev/null || scrapy_env/bin/python3 -c "import $package_name" 2>/dev/null; then
            local installed_version=$(scrapy_env/bin/python3 -c "import $import_name; print($import_name.__version__)" 2>/dev/null || \
                scrapy_env/bin/python3 -c "import $package_name; print($package_name.__version__)" 2>/dev/null || \
                echo "설치됨")
            echo "   ✅ $package_name 설치 완료 (버전: $installed_version)"
            return 0
        fi
    fi

    # 실패 시 버전 제약 없이 최신 버전 시도
    echo "   ⚠️  요청된 버전 설치 실패, 호환되는 최신 버전 찾는 중..."
    if scrapy_env/bin/pip install "$package_name" --quiet 2>/dev/null; then
        # 설치 성공 확인
        if scrapy_env/bin/python3 -c "import $import_name" 2>/dev/null || scrapy_env/bin/python3 -c "import $package_name" 2>/dev/null; then
            local installed_version=$(scrapy_env/bin/python3 -c "import $import_name; print($import_name.__version__)" 2>/dev/null || \
                scrapy_env/bin/python3 -c "import $package_name; print($package_name.__version__)" 2>/dev/null || \
                echo "설치됨")
            echo "   ✅ $package_name 설치 완료 (버전: $installed_version)"
            return 0
        fi
    fi

    # Python 버전별 호환 버전 목록 시도
    local python_version=$(get_python_version)
    echo "   🔍 Python $python_version과 호환되는 버전 찾는 중..."

    # Python 버전별 호환 버전 매핑
    case "$package_name" in
        pandas)
            # Python 3.14는 pandas 2.2.0 이상 필요
            if [[ "$python_version" == "3.14" ]] || [[ "$python_version" > "3.13" ]]; then
                for version in "2.2.2" "2.2.1" "2.2.0" "latest"; do
                    if [ "$version" = "latest" ]; then
                        if scrapy_env/bin/pip install "$package_name" --upgrade --quiet 2>/dev/null; then
                            if scrapy_env/bin/python3 -c "import pandas" 2>/dev/null; then
                                return 0
                            fi
                        fi
                    else
                        if scrapy_env/bin/pip install "${package_name}==${version}" --quiet 2>/dev/null; then
                            if scrapy_env/bin/python3 -c "import pandas" 2>/dev/null; then
                                return 0
                            fi
                        fi
                    fi
                done
            else
                # Python 3.13 이하는 기존 버전 시도
                for version in "2.1.4" "2.1.3" "2.1.2" "2.1.1" "2.1.0"; do
                    if scrapy_env/bin/pip install "${package_name}==${version}" --quiet 2>/dev/null; then
                        if scrapy_env/bin/python3 -c "import pandas" 2>/dev/null; then
                            return 0
                        fi
                    fi
                done
            fi
            ;;
        selenium)
            # Selenium은 일반적으로 호환성이 좋음
            for version in "latest" "4.16.0" "4.15.2" "4.15.1" "4.15.0"; do
                if [ "$version" = "latest" ]; then
                    if scrapy_env/bin/pip install "$package_name" --upgrade --quiet 2>/dev/null; then
                        if scrapy_env/bin/python3 -c "import selenium" 2>/dev/null; then
                            return 0
                        fi
                    fi
                else
                    if scrapy_env/bin/pip install "${package_name}==${version}" --quiet 2>/dev/null; then
                        if scrapy_env/bin/python3 -c "import selenium" 2>/dev/null; then
                            return 0
                        fi
                    fi
                fi
            done
            ;;
        webdriver-manager|webdriver_manager)
            for version in "latest" "4.0.2" "4.0.1" "4.0.0"; do
                if [ "$version" = "latest" ]; then
                    if scrapy_env/bin/pip install "$package_name" --upgrade --quiet 2>/dev/null; then
                        if scrapy_env/bin/python3 -c "import webdriver_manager" 2>/dev/null; then
                            return 0
                        fi
                    fi
                else
                    if scrapy_env/bin/pip install "${package_name}==${version}" --quiet 2>/dev/null; then
                        if scrapy_env/bin/python3 -c "import webdriver_manager" 2>/dev/null; then
                            return 0
                        fi
                    fi
                fi
            done
            ;;
        *)
            # 알 수 없는 패키지는 최신 버전 시도
            scrapy_env/bin/pip install "$package_name" --upgrade --quiet 2>/dev/null && return 0
            ;;
    esac

    return 1
}

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Big Data 프로젝트 통합 설치${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# ==============================================================================
# 운영체제 감지 및 선택
# ==============================================================================

detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Ubuntu/Debian 감지
        if [ -f /etc/os-release ]; then
            . /etc/os-release
            if [[ "$ID" == "ubuntu" ]] || [[ "$ID" == "debian" ]]; then
                echo "ubuntu"
            else
                echo "linux"
            fi
        else
            echo "linux"
        fi
    else
        echo "unknown"
    fi
}

OS_TYPE=$(detect_os)

if [ "$OS_TYPE" == "unknown" ]; then
    echo -e "${YELLOW}운영체제를 자동으로 감지할 수 없습니다.${NC}"
    echo ""
    echo "운영체제를 선택하세요:"
    echo "  1) macOS"
    echo "  2) Ubuntu/Debian"
    echo "  3) 기타 Linux"
    echo ""
    read -p "선택 (1-3): " OS_CHOICE

    case $OS_CHOICE in
        1) OS_TYPE="macos" ;;
        2) OS_TYPE="ubuntu" ;;
        3) OS_TYPE="linux" ;;
        *)
            echo -e "${RED}잘못된 선택입니다.${NC}"
            exit 1
            ;;
    esac
fi

echo -e "${CYAN}감지된 운영체제: $OS_TYPE${NC}"
echo ""

# ==============================================================================
# 1. 시스템 요구사항 확인 및 자동 설치
# ==============================================================================

echo -e "${YELLOW}[1/7] 시스템 요구사항 확인 및 설치 중...${NC}"

# Python 확인
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "${GREEN}✅ Python: $PYTHON_VERSION${NC}"
else
    echo -e "${RED}❌ Python 3가 설치되지 않았습니다.${NC}"
    echo "   자동 설치를 시도합니다..."

    case $OS_TYPE in
        macos)
            if command -v brew &> /dev/null; then
                echo "   Homebrew를 사용하여 Python 설치 중..."
                brew install python3
            else
                echo -e "${RED}   Homebrew가 설치되지 않았습니다.${NC}"
                echo "   https://brew.sh 에서 Homebrew를 먼저 설치하세요."
                exit 1
            fi
            ;;
        ubuntu)
            echo "   apt를 사용하여 Python 설치 중..."
            sudo apt update
            sudo apt install -y python3 python3-venv python3-pip
            ;;
        *)
            echo -e "${RED}   자동 설치를 지원하지 않는 운영체제입니다.${NC}"
            echo "   Python 3를 수동으로 설치하세요: https://www.python.org/downloads/"
            exit 1
            ;;
    esac
fi

# Java 확인 및 설치
JAVA_INSTALLED=true
if command -v java &> /dev/null; then
    JAVA_VERSION=$(java -version 2>&1 | head -n 1 | cut -d'"' -f2)
    echo -e "${GREEN}✅ Java: $JAVA_VERSION${NC}"
else
    echo -e "${YELLOW}⚠️  Java가 설치되지 않았습니다. (Kafka 프로젝트에 필요)${NC}"
    echo "   자동 설치를 시도합니다..."

    case $OS_TYPE in
        macos)
            if command -v brew &> /dev/null; then
                echo "   Homebrew를 사용하여 Java 설치 중..."
                brew install openjdk@17 || brew install openjdk@8
                echo "   JAVA_HOME 설정이 필요할 수 있습니다."
            else
                echo -e "${YELLOW}   Homebrew가 없어 Java를 자동 설치할 수 없습니다.${NC}"
                JAVA_INSTALLED=false
            fi
            ;;
        ubuntu)
            echo "   apt를 사용하여 Java 설치 중..."
            sudo apt update
            sudo apt install -y default-jdk
            ;;
        *)
            echo -e "${YELLOW}   자동 설치를 지원하지 않는 운영체제입니다.${NC}"
            JAVA_INSTALLED=false
            ;;
    esac

    if [ "$JAVA_INSTALLED" = true ]; then
        echo -e "${GREEN}✅ Java 설치 완료${NC}"
    fi
fi

# Maven 확인 및 설치
MVN_INSTALLED=true
if command -v mvn &> /dev/null; then
    MVN_VERSION=$(mvn -version | head -n 1 | cut -d' ' -f3)
    echo -e "${GREEN}✅ Maven: $MVN_VERSION${NC}"
else
    echo -e "${YELLOW}⚠️  Maven이 설치되지 않았습니다. (Kafka 프로젝트에 필요)${NC}"
    echo "   자동 설치를 시도합니다..."

    case $OS_TYPE in
        macos)
            if command -v brew &> /dev/null; then
                echo "   Homebrew를 사용하여 Maven 설치 중..."
                brew install maven
            else
                echo -e "${YELLOW}   Homebrew가 없어 Maven을 자동 설치할 수 없습니다.${NC}"
                MVN_INSTALLED=false
            fi
            ;;
        ubuntu)
            echo "   apt를 사용하여 Maven 설치 중..."
            sudo apt update
            sudo apt install -y maven
            ;;
        *)
            echo -e "${YELLOW}   자동 설치를 지원하지 않는 운영체제입니다.${NC}"
            MVN_INSTALLED=false
            ;;
    esac

    if [ "$MVN_INSTALLED" = true ]; then
        echo -e "${GREEN}✅ Maven 설치 완료${NC}"
    fi
fi

echo ""

# ==============================================================================
# 2. Python 가상환경 설정
# ==============================================================================

echo -e "${YELLOW}[2/7] Python 가상환경 설정 중...${NC}"

# 가상환경 유효성 검사 함수
check_venv_validity() {
    if [ ! -d "scrapy_env" ]; then
        return 1
    fi

    # Python 인터프리터 경로 확인
    if [ -f "scrapy_env/bin/python3" ]; then
        # Python 인터프리터가 실제로 존재하는지 확인
        if ! scrapy_env/bin/python3 --version &> /dev/null; then
            return 1
        fi
    else
        return 1
    fi

    # pip이 존재하고 작동하는지 확인
    if [ -f "scrapy_env/bin/pip" ]; then
        if ! scrapy_env/bin/pip --version &> /dev/null; then
            return 1
        fi
    else
        return 1
    fi

    return 0
}

# 가상환경 유효성 검사
if check_venv_validity; then
    echo -e "${GREEN}✅ 기존 가상환경 발견 및 유효성 확인 완료${NC}"
else
    if [ -d "scrapy_env" ]; then
        echo -e "${YELLOW}⚠️  기존 가상환경이 손상되었거나 잘못된 경로를 참조합니다.${NC}"
        echo "📦 가상환경을 재생성합니다..."
        rm -rf scrapy_env
    else
        echo "📦 가상환경 생성 중..."
    fi

    python3 -m venv scrapy_env
    echo -e "${GREEN}✅ 가상환경 생성 완료${NC}"
fi

# 가상환경 활성화
source scrapy_env/bin/activate
echo -e "${GREEN}✅ 가상환경 활성화 완료${NC}"

# pip 확인 및 업그레이드 (가상환경 내 pip 사용)
echo "📦 pip 업그레이드 중..."
if scrapy_env/bin/pip install --upgrade pip --quiet 2>/dev/null; then
    echo -e "${GREEN}✅ pip 업그레이드 완료${NC}"
else
    echo -e "${YELLOW}⚠️  pip 업그레이드 실패. 가상환경을 재생성합니다...${NC}"
    rm -rf scrapy_env
    python3 -m venv scrapy_env
    source scrapy_env/bin/activate
    scrapy_env/bin/pip install --upgrade pip --quiet
    echo -e "${GREEN}✅ 가상환경 재생성 및 pip 업그레이드 완료${NC}"
fi

echo ""

# ==============================================================================
# 3. Scrapy 프로젝트 의존성 설치
# ==============================================================================

echo -e "${YELLOW}[3/7] Scrapy 프로젝트 의존성 설치 중...${NC}"

if [ -f "setup/requirements.txt" ]; then
    echo "📦 Scrapy 의존성 설치 중..."

    # Python 버전 확인
    PYTHON_VERSION=$(get_python_version)
    echo "   Python 버전: $PYTHON_VERSION"

    # requirements 파일의 각 패키지를 개별적으로 설치 시도
    INSTALLED_PACKAGES=()
    FAILED_PACKAGES=()

    while IFS= read -r line || [ -n "$line" ]; do
        # 빈 줄과 주석 제외
        [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue

        # 패키지명과 버전 추출
        package_spec=$(echo "$line" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')

        if install_with_fallback "$package_spec"; then
            INSTALLED_PACKAGES+=("$package_spec")
        else
            FAILED_PACKAGES+=("$package_spec")
            echo -e "${YELLOW}   ⚠️  $package_spec 설치 실패${NC}"
        fi
    done < setup/requirements.txt

    echo ""

    # 설치 결과 요약
    if [ ${#INSTALLED_PACKAGES[@]} -gt 0 ]; then
        echo -e "${GREEN}✅ Scrapy 의존성 설치 완료${NC}"

        # Scrapy 버전 확인
        if [ -f "scrapy_env/bin/scrapy" ]; then
            SCRAPY_VERSION=$(scrapy_env/bin/scrapy version)
            echo -e "${GREEN}   Scrapy 버전: $SCRAPY_VERSION${NC}"
        fi
    fi

    if [ ${#FAILED_PACKAGES[@]} -gt 0 ]; then
        echo -e "${YELLOW}⚠️  일부 패키지 설치 실패:${NC}"
        for pkg in "${FAILED_PACKAGES[@]}"; do
            echo -e "${YELLOW}   • $pkg${NC}"
        done
    fi
else
    echo -e "${RED}❌ setup/requirements.txt 파일을 찾을 수 없습니다.${NC}"
fi

echo ""

# ==============================================================================
# 4. Selenium 프로젝트 의존성 설치
# ==============================================================================

echo -e "${YELLOW}[4/7] Selenium 프로젝트 의존성 설치 중...${NC}"

if [ -f "selenium_project/requirements_selenium.txt" ]; then
    echo "📦 Selenium 의존성 설치 중..."

    # Python 버전 확인
    PYTHON_VERSION=$(get_python_version)
    echo "   Python 버전: $PYTHON_VERSION"

    # requirements 파일의 각 패키지를 개별적으로 설치 시도
    INSTALLED_PACKAGES=()
    FAILED_PACKAGES=()

    while IFS= read -r line || [ -n "$line" ]; do
        # 빈 줄과 주석 제외
        [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue

        # 패키지명과 버전 추출
        package_spec=$(echo "$line" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')

        if install_with_fallback "$package_spec"; then
            INSTALLED_PACKAGES+=("$package_spec")
        else
            FAILED_PACKAGES+=("$package_spec")
            echo -e "${YELLOW}   ⚠️  $package_spec 설치 실패${NC}"
        fi
    done < selenium_project/requirements_selenium.txt

    echo ""

    # 설치 결과 요약
    if [ ${#INSTALLED_PACKAGES[@]} -gt 0 ]; then
        echo -e "${GREEN}✅ 설치 완료된 패키지:${NC}"
        for pkg in "${INSTALLED_PACKAGES[@]}"; do
            package_name=$(echo "$pkg" | sed 's/[>=<].*$//' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
            import_name=$(echo "$package_name" | sed 's/-/_/g')

            # import 시도 (하이픈과 언더스코어 모두 시도)
            if scrapy_env/bin/python3 -c "import $import_name" 2>/dev/null || \
               scrapy_env/bin/python3 -c "import $package_name" 2>/dev/null; then
                version=$(scrapy_env/bin/python3 -c "import $import_name; print($import_name.__version__)" 2>/dev/null || \
                    scrapy_env/bin/python3 -c "import $package_name; print($package_name.__version__)" 2>/dev/null || \
                    echo "설치됨")
                echo -e "${GREEN}   • $package_name: $version${NC}"
            else
                echo -e "${GREEN}   • $pkg${NC}"
            fi
        done
    fi

    if [ ${#FAILED_PACKAGES[@]} -gt 0 ]; then
        echo -e "${YELLOW}⚠️  설치 실패한 패키지:${NC}"
        for pkg in "${FAILED_PACKAGES[@]}"; do
            echo -e "${YELLOW}   • $pkg${NC}"
        done
        echo -e "${YELLOW}   이 패키지들은 선택적 의존성이므로 계속 진행합니다.${NC}"
    fi

    # 최종 확인
    if scrapy_env/bin/python3 -c "import selenium" 2>/dev/null; then
        SELENIUM_VERSION=$(scrapy_env/bin/python3 -c "import selenium; print(selenium.__version__)" 2>/dev/null)
        echo -e "${GREEN}✅ Selenium 사용 가능 (버전: $SELENIUM_VERSION)${NC}"
    else
        echo -e "${RED}❌ Selenium 설치 실패 - 필수 패키지입니다.${NC}"
    fi
else
    echo -e "${RED}❌ selenium_project/requirements_selenium.txt 파일을 찾을 수 없습니다.${NC}"
fi

echo ""

# ==============================================================================
# 5. Kafka 프로젝트 빌드
# ==============================================================================

echo -e "${YELLOW}[5/7] Kafka 프로젝트 빌드 중...${NC}"

if [ "$JAVA_INSTALLED" = false ] || [ "$MVN_INSTALLED" = false ]; then
    echo -e "${YELLOW}⚠️  Java 또는 Maven이 없어 Kafka 프로젝트를 빌드할 수 없습니다.${NC}"
    echo "   Java와 Maven을 설치한 후 다음 명령어를 실행하세요:"
    echo "   cd kafka_project/kafka_demo && mvn clean install"
    echo "   cd kafka_project/kafka_streams && mvn clean install"
else
    # Java/Maven 재확인 (설치 후)
    if command -v java &> /dev/null && command -v mvn &> /dev/null; then
        # Kafka Demo 빌드
        if [ -f "kafka_project/kafka_demo/pom.xml" ]; then
            echo "📦 Kafka Demo 빌드 중..."
            cd kafka_project/kafka_demo
            mvn clean install -DskipTests --quiet
            echo -e "${GREEN}✅ Kafka Demo 빌드 완료${NC}"
            cd "$PROJECT_ROOT"
        fi

        # Kafka Streams 빌드
        if [ -f "kafka_project/kafka_streams/pom.xml" ]; then
            echo "📦 Kafka Streams 빌드 중..."
            cd kafka_project/kafka_streams
            mvn clean install -DskipTests --quiet
            echo -e "${GREEN}✅ Kafka Streams 빌드 완료${NC}"
            cd "$PROJECT_ROOT"
        fi
    else
        echo -e "${YELLOW}⚠️  Java 또는 Maven을 찾을 수 없습니다.${NC}"
    fi
fi

echo ""

# ==============================================================================
# 6. 프로젝트 구조 확인 및 디렉토리 생성
# ==============================================================================

echo -e "${YELLOW}[6/7] 프로젝트 구조 확인 중...${NC}"

# 필요한 디렉토리 생성
REQUIRED_DIRS=(
    "scrapy_project/outputs/json"
    "scrapy_project/outputs/csv"
    "scrapy_project/outputs/databases"
    "selenium_project/outputs/json"
    "selenium_project/outputs/csv"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        echo -e "${GREEN}📁 $dir 디렉토리 생성${NC}"
    fi
done

echo ""

# ==============================================================================
# 7. Hadoop 설치 (선택사항)
# ==============================================================================

echo -e "${YELLOW}[7/8] Hadoop 설치 안내...${NC}"

if [ ! -d "hadoop_project/hadoop-3.4.1" ]; then
    echo -e "${YELLOW}⚠️  Hadoop이 설치되지 않았습니다.${NC}"
    echo ""
    echo "Hadoop을 설치하시겠습니까? (y/n)"
    read -p "선택: " INSTALL_HADOOP

    if [ "$INSTALL_HADOOP" = "y" ] || [ "$INSTALL_HADOOP" = "Y" ]; then
        if [ -f "setup/setup_hadoop.sh" ]; then
            echo "   Hadoop 설치 스크립트 실행 중..."
            bash setup/setup_hadoop.sh
            echo -e "${GREEN}✅ Hadoop 설치 완료${NC}"
        else
            echo -e "${YELLOW}   setup_hadoop.sh 파일을 찾을 수 없습니다.${NC}"
        fi
    fi
else
    echo -e "${GREEN}✅ Hadoop이 이미 설치되어 있습니다.${NC}"
fi

echo ""

# ==============================================================================
# 8. Kafka 서버 설치 안내 (선택사항)
# ==============================================================================

echo -e "${YELLOW}[8/8] Kafka 서버 설치 안내...${NC}"

if ! command -v kafka-server-start &> /dev/null && ! command -v kafka-server-start.sh &> /dev/null; then
    echo -e "${YELLOW}⚠️  Kafka 서버가 설치되지 않았습니다.${NC}"
    echo ""
    echo "Kafka 서버를 설치하시겠습니까? (y/n)"
    read -p "선택: " INSTALL_KAFKA

    if [ "$INSTALL_KAFKA" = "y" ] || [ "$INSTALL_KAFKA" = "Y" ]; then
        case $OS_TYPE in
            macos)
                if command -v brew &> /dev/null; then
                    echo "   Homebrew를 사용하여 Kafka 설치 중..."
                    brew install kafka
                    echo -e "${GREEN}✅ Kafka 설치 완료${NC}"
                    echo ""
                    echo "Kafka 서버를 시작하시겠습니까? (y/n)"
                    read -p "선택: " START_KAFKA
                    if [ "$START_KAFKA" = "y" ] || [ "$START_KAFKA" = "Y" ]; then
                        brew services start kafka
                        echo -e "${GREEN}✅ Kafka 서버 시작 완료${NC}"
                    fi
                else
                    echo -e "${YELLOW}   Homebrew가 없어 Kafka를 자동 설치할 수 없습니다.${NC}"
                fi
                ;;
            ubuntu)
                echo "   Kafka는 수동 설치가 필요합니다."
                echo "   kafka_project/docs/cluster_setup_guide.md 참조"
                ;;
            *)
                echo "   Kafka는 수동 설치가 필요합니다."
                ;;
        esac
    fi
else
    echo -e "${GREEN}✅ Kafka 서버가 설치되어 있습니다.${NC}"
fi

echo ""

# ==============================================================================
# 설치 완료 및 요약
# ==============================================================================

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✅ 설치 완료!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

echo -e "${YELLOW}📋 설치 요약:${NC}"
echo ""

# Python 패키지 확인
echo -e "${BLUE}Python 패키지:${NC}"
scrapy_env/bin/pip list | grep -E "scrapy|selenium|kafka-python|pandas" | sed 's/^/   /' || echo "   (설치된 패키지 없음)"

echo ""

# Java/Maven 확인
if command -v java &> /dev/null && command -v mvn &> /dev/null; then
    echo -e "${BLUE}Java/Maven:${NC}"
    echo "   Java: $(java -version 2>&1 | head -n 1 | cut -d'"' -f2)"
    echo "   Maven: $(mvn -version | head -n 1 | cut -d' ' -f3)"
    echo ""
fi

# 다음 단계 안내
echo -e "${YELLOW}🚀 다음 단계:${NC}"
echo ""
echo "1. 가상환경 활성화:"
echo "   ${GREEN}source scrapy_env/bin/activate${NC}"
echo ""
echo "2. Scrapy 프로젝트 테스트:"
echo "   ${GREEN}cd scrapy_project && scrapy list${NC}"
echo ""
echo "3. Selenium 프로젝트 테스트:"
echo "   ${GREEN}cd selenium_project && python selenium_basics/webdriver_config.py${NC}"
echo ""
echo "4. Kafka 프로젝트 테스트:"
echo "   ${GREEN}cd kafka_project && ./scripts/test_kafka.sh${NC}"
echo ""
echo "5. Hadoop 프로젝트 테스트:"
echo "   ${GREEN}cd hadoop_project/hadoop-3.4.1 && ./bin/hadoop version${NC}"
echo ""

# Kafka 서버 안내
echo -e "${YELLOW}📝 참고사항:${NC}"
echo ""
echo "- Kafka 서버는 별도로 설치 및 시작해야 합니다:"
echo "  ${GREEN}macOS: brew install kafka && brew services start kafka${NC}"
echo "  ${GREEN}Linux: kafka_project/docs/cluster_setup_guide.md 참조${NC}"
echo ""
echo "- Hadoop Cluster Mode 설정:"
echo "  ${GREEN}hadoop_project/scripts/setup_single_node_wo_yarn.sh${NC}"
echo "  ${GREEN}hadoop_project/docs/SETUP_GUIDE.md 참조${NC}"
echo ""
echo "- 자세한 설치 가이드는 ${GREEN}setup/REQUIREMENTS.md${NC}를 참조하세요."
echo ""

echo -e "${GREEN}Happy Coding! 🎉${NC}"
