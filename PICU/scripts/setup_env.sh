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

# PICU 관련 경로 추가 (기존 하드코딩된 모든 경로 포함)
NEW_PATHS="$COINTICKER_ROOT:$COINTICKER_ROOT/shared:$COINTICKER_ROOT/worker-nodes:$COINTICKER_ROOT/backend:$COINTICKER_ROOT/worker-nodes/mapreduce"

if [ -z "$PYTHONPATH_CLEANED" ]; then
    export PYTHONPATH="$NEW_PATHS"
else
    export PYTHONPATH="$NEW_PATHS:$PYTHONPATH_CLEANED"
fi

# Hadoop 환경 설정 (자동 감지)
if [ -z "$HADOOP_HOME" ]; then
    # 1. cluster_config.yaml에서 hadoop.home 확인
    if [ -f "$COINTICKER_ROOT/config/cluster_config.yaml" ]; then
        # yaml 파싱 (간단한 grep 방식) - 'home:' 또는 'hadoop_home:' 찾기
        HADOOP_FROM_CONFIG=$(grep -A 3 "^hadoop:" "$COINTICKER_ROOT/config/cluster_config.yaml" | grep -E "(home:|hadoop_home:)" | head -1 | awk '{print $2}' | tr -d '"' | tr -d "'")
        if [ -n "$HADOOP_FROM_CONFIG" ] && [ -d "$HADOOP_FROM_CONFIG" ]; then
            export HADOOP_HOME="$HADOOP_FROM_CONFIG"
        fi
    fi

    # 2. hadoop 명령어가 PATH에 있으면 그 위치에서 HADOOP_HOME 추론
    if [ -z "$HADOOP_HOME" ] && command -v hadoop &> /dev/null; then
        HADOOP_BIN_PATH=$(command -v hadoop)
        HADOOP_DETECTED="$(cd "$(dirname "$HADOOP_BIN_PATH")/.." && pwd)"
        if [ -f "$HADOOP_DETECTED/bin/hadoop" ]; then
            export HADOOP_HOME="$HADOOP_DETECTED"
        fi
    fi

    # 3. 프로젝트 인접 경로 확인 (hadoop_project/hadoop-*)
    if [ -z "$HADOOP_HOME" ] && [ -d "$PICU_ROOT/../hadoop_project" ]; then
        # 최신 버전 찾기 (역순 정렬)
        for HADOOP_DIR in $(ls -1dr "$PICU_ROOT/../hadoop_project"/hadoop-* 2>/dev/null); do
            if [ -f "$HADOOP_DIR/bin/hadoop" ]; then
                export HADOOP_HOME="$(cd "$HADOOP_DIR" && pwd)"
                break
            fi
        done
    fi

    # 4. 표준 설치 경로들 확인
    if [ -z "$HADOOP_HOME" ]; then
        STANDARD_PATHS=(
            "/opt/hadoop"
            /opt/hadoop-*
            "/usr/local/hadoop"
            /usr/local/hadoop-*
            ~/hadoop-*
        )

        for HADOOP_PATH in "${STANDARD_PATHS[@]}"; do
            # glob 확장 후 역순 정렬
            for EXPANDED_PATH in $(eval echo $HADOOP_PATH 2>/dev/null | tr ' ' '\n' | sort -r); do
                if [ -f "$EXPANDED_PATH/bin/hadoop" ]; then
                    export HADOOP_HOME="$(cd "$EXPANDED_PATH" && pwd)"
                    break 2
                fi
            done
        done
    fi
fi

# HADOOP_HOME이 설정되었으면 PATH에 추가
if [ -n "$HADOOP_HOME" ]; then
    # Hadoop bin 경로 추가 (중복 확인)
    if [ -d "$HADOOP_HOME/bin" ] && [[ ":$PATH:" != *":$HADOOP_HOME/bin:"* ]]; then
        export PATH="$HADOOP_HOME/bin:$PATH"
    fi

    # Hadoop sbin 경로 추가 (중복 확인)
    if [ -d "$HADOOP_HOME/sbin" ] && [[ ":$PATH:" != *":$HADOOP_HOME/sbin:"* ]]; then
        export PATH="$HADOOP_HOME/sbin:$PATH"
    fi
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
    if [ -n "$HADOOP_HOME" ]; then
        echo "   HADOOP_HOME: $HADOOP_HOME"
    fi
    if [ -n "$VIRTUAL_ENV" ]; then
        echo "   가상환경: $VIRTUAL_ENV"
    fi
fi
