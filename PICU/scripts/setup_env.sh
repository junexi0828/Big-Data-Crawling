#!/bin/bash
# PICU 프로젝트 통합 환경 설정 스크립트
# 모든 Shell 스크립트에서 source하여 사용

# 스크립트 위치에서 PICU 루트 찾기
export PICU_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export COINTICKER_ROOT="$PICU_ROOT/cointicker"

# PYTHONPATH 설정 (중복 제거)
# 기존 PYTHONPATH에서 중복 제거
PYTHONPATH_CLEANED=""
if [ -n "$PYTHONPATH" ]; then
    # 기존 PYTHONPATH를 배열로 분리
    IFS=':' read -ra PATHS <<< "$PYTHONPATH"
    for path in "${PATHS[@]}"; do
        # PICU 관련 경로가 아닌 것만 유지
        if [[ ! "$path" =~ "$PICU_ROOT" ]]; then
            if [ -z "$PYTHONPATH_CLEANED" ]; then
                PYTHONPATH_CLEANED="$path"
            else
                PYTHONPATH_CLEANED="$PYTHONPATH_CLEANED:$path"
            fi
        fi
    done
fi

# PICU 관련 경로 추가
if [ -z "$PYTHONPATH_CLEANED" ]; then
    export PYTHONPATH="$COINTICKER_ROOT:$COINTICKER_ROOT/shared"
else
    export PYTHONPATH="$COINTICKER_ROOT:$COINTICKER_ROOT/shared:$PYTHONPATH_CLEANED"
fi

# 가상환경 활성화 (있으면)
if [ -f "$PICU_ROOT/venv/bin/activate" ]; then
    source "$PICU_ROOT/venv/bin/activate"
fi

# 환경 변수 출력 (디버깅용, 필요시 주석 처리)
if [ "${PICU_ENV_VERBOSE:-0}" = "1" ]; then
    echo "✅ PICU 환경 설정 완료"
    echo "   PICU_ROOT: $PICU_ROOT"
    echo "   COINTICKER_ROOT: $COINTICKER_ROOT"
    echo "   PYTHONPATH: $PYTHONPATH"
    if [ -n "$VIRTUAL_ENV" ]; then
        echo "   가상환경: $VIRTUAL_ENV"
    fi
fi
