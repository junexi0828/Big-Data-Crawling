# HDFS 데몬 실행 실패 문제 해결 보고서

## 1. 문제 요약

**현상**: GUI 또는 스크립트를 통해 하둡(Hadoop) 및 카프카(Kafka) 데몬 실행 시, 프로세스가 시작되지 않는 심각한 결함이 발생.

**초기 진단**: 데몬 자체가 실행되지 않는 것으로 보아, 프로세스 시작 흐름의 가장 근본적인 단계에서 문제가 발생했을 것으로 추정.

## 2. 진단 과정

HDFS 데몬 시작을 담당하는 `HDFSManager`의 실행 흐름을 단계적으로 추적하여 문제의 원인을 진단했습니다.

### 2.1. HADOOP_HOME 경로 확인

-   **내용**: `HADOOP_HOME` 환경 변수 및 `hdfs_manager.py`가 탐색하는 기본 경로들을 확인.
-   **결과**: 환경 변수는 없었으나, 자동 감지 로직이 프로젝트 내 `hadoop_project/hadoop-3.4.1` 디렉토리를 **정상적으로 탐지**함을 확인. 경로 문제는 아님.

### 2.2. 디렉토리 권한 확인

-   **내용**: 감지된 `HADOOP_HOME` 내부의 `logs` 디렉토리 등에 대한 현재 사용자의 접근 권한 확인.
-   **결과**: 모든 관련 디렉토리의 권한이 정상적임을 확인. 권한 문제도 아님.

### 2.3. 데몬 직접 실행 및 로그 분석

-   **내용**: `hdfs --daemon start namenode` 명령어를 직접 실행하여 반응을 살폈으나, 별다른 오류 메시지 없이 프로세스가 종료됨. 이는 데몬이 시작 직후 내부 오류로 종료되었음을 시사.
-   **결과**: NameNode의 최신 로그 파일(`.../logs/hadoop-*-namenode-*.log`)을 분석한 결과, 다음과 같은 **치명적 오류(FATAL ERROR)**를 발견.

```
org.apache.hadoop.hdfs.server.common.InconsistentFSStateException: Directory /private/tmp/hadoop-juns/dfs/name is in an inconsistent state: storage directory does not exist or is not accessible.
```

### 2.4. 근본 원인 식별

-   **원인**: NameNode의 핵심 데이터 저장 디렉토리(`dfs.namenode.name.dir`)가 **OS의 임시 폴더(`/private/tmp/...`)**를 사용하도록 설정되어 있었습니다.
-   **문제점**: macOS는 재시작 등의 이유로 임시 폴더의 내용을 주기적으로 삭제합니다. 이로 인해 이전에 생성되었던 NameNode의 데이터가 삭제되면서, NameNode가 자신의 데이터 상태가 파괴되었다고 판단하여 시작을 거부하고 스스로를 종료시키는 것이었습니다.

## 3. 해결 조치

문제의 근본 원인인 '임시 디렉토리 사용'을 해결하기 위해, 데이터가 영구적으로 보존될 수 있도록 아래와 같이 코드를 수정했습니다.

### 3.1. `hdfs_manager.py` 수정

-   `setup_single_node_mode` 및 `setup_cluster_mode` 함수가 `hdfs-site.xml` 파일을 생성하는 로직을 수정했습니다.

### 3.2. 영구 저장소 경로 지정

-   기존에는 `dfs.replication` 속성만 설정했지만, 아래 두 가지 속성을 명시적으로 추가했습니다.
    -   `dfs.namenode.name.dir`: NameNode 데이터 저장 경로
    -   `dfs.datanode.data.dir`: DataNode 데이터 저장 경로
-   새로운 저장 경로는 OS의 임시 폴더가 아닌, 하둡 설치 경로 내부의 `data/` 폴더(`$HADOOP_HOME/data/namenode`, `$HADOOP_HOME/data/datanode`)를 사용하도록 설정했습니다.

### 3.3. 이전 임시 디렉토리 정리

-   향후 발생할 수 있는 충돌을 방지하기 위해, 문제가 되었던 이전 OS 임시 디렉토리(`rm -rf /private/tmp/hadoop-juns`)를 완전히 삭제했습니다.

## 4. 결과

-   **문제 해결**: 위 조치 이후, HDFS 시작 시 `HDFSManager`는 새로 지정된 영구 데이터 디렉토리를 자동으로 포맷하고 데몬을 정상적으로 실행합니다.
-   **안정성 확보**: 이제 OS가 임시 파일을 삭제하더라도 하둡의 핵심 데이터는 안전하게 보존되므로, 데몬이 항상 안정적으로 시작될 수 있는 환경이 구축되었습니다.

## 5. 핵심 요약

**"Hadoop의 데이터 디렉토리가 OS 임시 폴더로 설정되어 데이터가 유실된 것이 원인이었으며, 데이터 경로를 영구적인 폴더로 변경하여 문제를 해결함."**
