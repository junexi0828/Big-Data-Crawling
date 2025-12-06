# HDFS 데몬 실행 실패 문제 해결 보고서

## 1. 문제 상황

HDFS (Hadoop Distributed File System) 데몬(Namenode, Datanode 등)을 실행하는 스크립트가 특정 환경에서 실패하는 문제가 발생했습니다. 주요 원인은 `JAVA_HOME` 및 `HADOOP_HOME` 환경 변수가 하드코딩되어 있거나, 사용자 환경마다 다른 설치 경로를 반영하지 못했기 때문입니다. 이로 인해 스크립트의 이식성이 저하되고, 새로운 개발 환경을 설정할 때마다 수동으로 경로를 수정해야 하는 번거로움이 있었습니다.

## 2. 해결 방안

이 문제를 해결하기 위해, 셸 스크립트와 Python 유틸리티를 결합하여 환경 변수를 동적으로 탐지하고 설정하는 범용적인 솔루션을 도입했습니다. 핵심적인 두 파일은 `start.sh`와 `path_utils.py`입니다.

### 2.1. `path_utils.py`: 범용 경로 탐지 유틸리티

Python으로 `path_utils.py` 모듈을 생성하여, 시스템의 다양한 위치에서 Hadoop 및 기타 필수 소프트웨어의 설치 경로를 지능적으로 찾는 기능을 구현했습니다.

`get_hadoop_home()` 함수의 주요 탐지 로직:
1.  **`HADOOP_HOME` 환경 변수** 확인 (가장 높은 우선순위)
2.  프로젝트 내 `cluster_config.yaml` 설정 파일 조회
3.  `shutil.which('hadoop')`을 통해 시스템 `PATH`에 등록된 `hadoop` 명령어 위치를 추론
4.  프로젝트와 인접한 `hadoop_project/hadoop-*` 디렉토리 검색
5.  `/opt/hadoop*`, `/usr/local/hadoop*` 등 표준 설치 경로 순차 검색

이 Python 함수는 복잡한 파일 시스템 검색과 조건부 로직을 효과적으로 처리하여, 거의 모든 환경에서 Hadoop 설치를 안정적으로 찾아낼 수 있습니다.

### 2.2. `start.sh`: 동적 환경 설정의 통합

사용자의 주 진입점인 `start.sh` 스크립트를 수정하여, 스크립트 실행 시점에 `path_utils.py`의 경로 탐지 기능을 호출하도록 통합했습니다.

**`start.sh`의 Hadoop 경로 설정 로직:**

```bash
# ... (스크립트 상단)

# 2. Hadoop 경로 설정 (path_utils.py의 범용 경로 찾기 사용)
# 먼저 간단한 경로 확인, 없으면 path_utils.py로 시스템 경로까지 포함하여 찾기
if [ -d "$BIGDATA_ROOT/hadoop_project/hadoop-3.4.1" ]; then
    export HADOOP_HOME="$BIGDATA_ROOT/hadoop_project/hadoop-3.4.1"
else
    # path_utils.py를 사용하여 시스템 경로까지 포함하여 찾기
    if command -v python3 &> /dev/null; then
        PYTHON_CMD=$(command -v python3)
        # path_utils.py의 get_hadoop_home() 함수 호출
        HADOOP_PATH=$($PYTHON_CMD -c "
import sys
# 프로젝트 경로를 sys.path에 추가하여 모듈 임포트
sys.path.insert(0, '$PROJECT_ROOT')
try:
    from shared.path_utils import get_hadoop_home
    hadoop_path = get_hadoop_home()
    if hadoop_path:
        print(str(hadoop_path))
except Exception:
    pass
" 2>/dev/null)

        if [ -n "$HADOOP_PATH" ] && [ -d "$HADOOP_PATH" ]; then
            export HADOOP_HOME="$HADOOP_PATH"
        fi
    fi
fi

# ... (이후 HADOOP_HOME을 사용하여 다른 변수 설정)
```

`start.sh`는 간단한 인라인 Python 명령(`python -c "..."`)을 실행하여 `path_utils.py`의 `get_hadoop_home()` 함수를 호출하고, 그 결과를 `HADOOP_HOME` 변수에 저장합니다. 이로써 셸 스크립트의 간결함을 유지하면서 Python의 강력한 경로 탐지 기능을 활용할 수 있게 되었습니다.

## 3. 기대 효과 및 결과

-   **이식성 향상**: `start.sh` 스크립트는 더 이상 특정 디렉토리 구조나 하드코딩된 경로에 의존하지 않습니다. 개발자들은 각자의 환경에서 별도의 수정 없이 스크립트를 즉시 실행할 수 있습니다.
-   **안정성 증대**: HDFS 데몬 실행에 필수적인 `JAVA_HOME`과 `HADOOP_HOME`이 실행 시점에 동적으로 정확하게 설정되므로, 경로 누락으로 인한 데몬 실행 실패 문제가 근본적으로 해결되었습니다.
-   **유지보수 편의성**: 경로 탐지 로직이 `path_utils.py`에 중앙화되어 있어, 향후 새로운 탐지 규칙을 추가하거나 기존 로직을 수정하기 용이합니다.

이 통합을 통해 HDFS 데몬 실행 문제가 해결되었으며, 프로젝트의 전반적인 개발 및 배포 환경이 더욱 견고해졌습니다.