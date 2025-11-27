#!/bin/bash
# 전체 테스트 실행 스크립트

echo "=========================================="
echo "코인티커 프로젝트 테스트 시작"
echo "=========================================="

cd "$(dirname "$0")/.."

# 색상 정의
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 테스트 카운터
PASSED=0
FAILED=0

# 1. Python 문법 검사
echo -e "\n${YELLOW}[1/6] Python 문법 검사${NC}"
find . -name "*.py" -type f ! -path "*/__pycache__/*" ! -path "*/venv/*" | while read f; do
    if python3 -m py_compile "$f" 2>/dev/null; then
        echo -e "  ${GREEN}✅${NC} $(basename $f)"
        ((PASSED++))
    else
        echo -e "  ${RED}❌${NC} $(basename $f)"
        ((FAILED++))
    fi
done

# 2. Import 테스트
echo -e "\n${YELLOW}[2/6] Import 테스트${NC}"

# Utils import
if python3 -c "import sys; sys.path.insert(0, 'shared'); from shared.utils import generate_hash; print('✅ Utils')" 2>/dev/null; then
    echo -e "  ${GREEN}✅${NC} shared.utils"
    ((PASSED++))
else
    echo -e "  ${RED}❌${NC} shared.utils"
    ((FAILED++))
fi

# Models import
if python3 -c "import sys; sys.path.insert(0, 'backend'); from backend.models import RawNews; print('✅ Models')" 2>/dev/null; then
    echo -e "  ${GREEN}✅${NC} backend.models"
    ((PASSED++))
else
    echo -e "  ${RED}❌${NC} backend.models"
    ((FAILED++))
fi

# Spiders import
if python3 -c "import sys; sys.path.insert(0, 'worker-nodes'); from cointicker.spiders.upbit_trends import UpbitTrendsSpider; print('✅ Spiders')" 2>/dev/null; then
    echo -e "  ${GREEN}✅${NC} Spiders"
    ((PASSED++))
else
    echo -e "  ${RED}❌${NC} Spiders"
    ((FAILED++))
fi

# 3. Spider 구조 테스트
echo -e "\n${YELLOW}[3/6] Spider 구조 테스트${NC}"
cd worker-nodes
for spider in upbit_trends coinness saveticker perplexity cnn_fear_greed; do
    if python3 -c "import sys; sys.path.insert(0, '.'); from cointicker.spiders.$spider import *; print('✅ $spider')" 2>/dev/null; then
        echo -e "  ${GREEN}✅${NC} $spider"
        ((PASSED++))
    else
        echo -e "  ${RED}❌${NC} $spider"
        ((FAILED++))
    fi
done
cd ..

# 4. Items 테스트
echo -e "\n${YELLOW}[4/6] Items 테스트${NC}"
if python3 -c "import sys; sys.path.insert(0, 'worker-nodes'); from cointicker.items import MarketTrendItem, CryptoNewsItem; print('✅ Items')" 2>/dev/null; then
    echo -e "  ${GREEN}✅${NC} Items"
    ((PASSED++))
else
    echo -e "  ${RED}❌${NC} Items"
    ((FAILED++))
fi

# 5. Backend 구조 테스트
echo -e "\n${YELLOW}[5/6] Backend 구조 테스트${NC}"
if python3 -c "import sys; sys.path.insert(0, 'backend'); from backend.app import app; print('✅ FastAPI app')" 2>/dev/null; then
    echo -e "  ${GREEN}✅${NC} FastAPI app"
    ((PASSED++))
else
    echo -e "  ${RED}❌${NC} FastAPI app"
    ((FAILED++))
fi

# 6. MapReduce 테스트
echo -e "\n${YELLOW}[6/6] MapReduce 테스트${NC}"
cd worker-nodes/mapreduce
if python3 -c "from cleaner_mapper import clean_data; print('✅ Mapper')" 2>/dev/null; then
    echo -e "  ${GREEN}✅${NC} Mapper"
    ((PASSED++))
else
    echo -e "  ${RED}❌${NC} Mapper"
    ((FAILED++))
fi

if python3 -c "from cleaner_reducer import remove_duplicates; print('✅ Reducer')" 2>/dev/null; then
    echo -e "  ${GREEN}✅${NC} Reducer"
    ((PASSED++))
else
    echo -e "  ${RED}❌${NC} Reducer"
    ((FAILED++))
fi
cd ../..

# 결과 요약
echo -e "\n=========================================="
echo -e "테스트 결과"
echo -e "=========================================="
echo -e "${GREEN}통과: ${PASSED}${NC}"
echo -e "${RED}실패: ${FAILED}${NC}"
echo -e "=========================================="

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ 모든 테스트 통과!${NC}"
    exit 0
else
    echo -e "${RED}❌ 일부 테스트 실패${NC}"
    exit 1
fi

