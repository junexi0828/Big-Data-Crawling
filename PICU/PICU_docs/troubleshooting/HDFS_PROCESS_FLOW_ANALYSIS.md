# HDFS 프로세스 흐름 분석 및 문제점

## 현재 흐름도

```
_check_and_start_hdfs()
  ↓
1. HDFS 실행 여부 확인 (_check_hdfs_running)
   ├─ 실행 중 → return 성공
   └─ 실행 안 됨 → 계속
  ↓
2. 클러스터 설정 확인 (_get_cluster_config)
  ↓
3. HADOOP_HOME 자동 감지
  ↓
4. 멀티노드/단일 노드 모드 결정
   ├─ has_cluster_config == True
   │   ├─ _setup_cluster_mode() 성공
   │   │   └─ ssh_available = _test_ssh_connection("localhost")  # [수정] localhost SSH 확인 추가
   │   └─ _setup_cluster_mode() 실패
   │       ├─ 사용자 확인 → 단일 노드 모드
   │       │   ├─ _setup_single_node_mode()
   │       │   └─ ssh_available = _test_ssh_connection("localhost")
   │       └─ 사용자 거부 → return 실패
   └─ has_cluster_config == False
       ├─ _setup_single_node_mode()
       └─ ssh_available = _test_ssh_connection("localhost")
  ↓
5. SSH 실패 시 로컬 SSH 설정 시도 (모든 경우에 실행)
   ├─ _setup_local_ssh() 성공 → ssh_available 재테스트
   └─ _setup_local_ssh() 실패 → ssh_available = False
  ↓
6. HDFS 시작
   ├─ ssh_available == False
   │   └─ _start_hdfs_daemons_direct() → return (여기서 종료되어야 함)
   └─ ssh_available == True
       ├─ subprocess.Popen(start-dfs.sh) → process 변수 생성
       └─ 포트 확인 로직 실행 (else 블록 안에서 process 변수 사용)  # [수정 완료]
```

## 발견된 문제점

### 🔴 치명적 버그 1: process 변수 스코프 오류

**위치**: 645-702줄

**문제**:

```python
if not ssh_available:
    return self._start_hdfs_daemons_direct(...)  # 여기서 return
else:
    process = subprocess.Popen(...)  # process 변수 생성

# [문제] 들여쓰기가 잘못되어 if-else 블록 밖에 있음
for attempt in range(max_retries):
    if process.poll() is not None:  # ❌ process가 정의되지 않을 수 있음!
```

**영향**:

- `_start_hdfs_daemons_direct()`가 호출되면 `return`으로 함수가 종료되어야 하는데, 만약 `return`이 제대로 작동하지 않거나 코드가 수정되면 `process` 변수가 정의되지 않은 상태에서 `process.poll()`이 실행되어 `NameError` 발생

### 🔴 치명적 버그 2: 중복된 포트 확인 로직

**위치**:

- `_check_and_start_hdfs()`: 661-702줄
- `_start_hdfs_daemons_direct()`: 949-952줄

**문제**:

- `_start_hdfs_daemons_direct()`는 이미 내부에서 포트 확인을 하고 결과를 반환함
- 그런데 `_check_and_start_hdfs()`에서도 포트 확인 로직이 있음
- 하지만 `return`으로 인해 실행되지 않아야 하는데, 코드 구조상 혼란스러움

### 🟡 로직 문제 3: 들여쓰기 오류

**위치**: 661줄 이후

**문제**:

- 포트 확인 로직(661-702줄)이 `if-else` 블록 밖에 있어서 항상 실행되는 것처럼 보임
- 하지만 실제로는 `if not ssh_available:` 블록에서 `return`되므로 실행되지 않음
- 코드 가독성과 유지보수성 저하

### 🟡 로직 문제 4: \_wait_for_hdfs_ports 호출 방식 불일치

**위치**: 693-695줄

**문제**:

```python
port_check_result = self._wait_for_hdfs_ports(
    namenode_ports, max_retries=1, retry_interval=0
)
```

- `max_retries=1, retry_interval=0`으로 호출하면 실제로는 포트 확인이 1번만 이루어짐
- 하지만 위의 `for attempt in range(max_retries):` 루프에서 이미 재시도하고 있음
- 중복된 재시도 로직

## 수정 방안

### 수정 1: 들여쓰기 수정 및 process 변수 스코프 보장

```python
if not ssh_available:
    # SSH 없이 데몬 직접 시작 (단일 노드 모드)
    logger.info("SSH 없이 HDFS 데몬을 직접 시작합니다...")
    return self._start_hdfs_daemons_direct(
        hadoop_home, hdfs_env, namenode_ports
    )
else:
    # SSH를 통한 일반 시작 (클러스터 모드)
    logger.info("HDFS 시작 중...")
    process = subprocess.Popen(
        ["bash", str(start_dfs_script)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
        env=hdfs_env,
    )

    # HDFS 시작 대기 및 포트 확인 (재시도 로직)
    import time
    max_retries = 15
    retry_interval = 2

    for attempt in range(max_retries):
        time.sleep(retry_interval)

        # 프로세스가 종료되었는지 확인
        if process.poll() is not None:
            # ... 에러 처리 ...
            break

        # 포트 확인
        port_check_result = self._wait_for_hdfs_ports(
            namenode_ports, max_retries=1, retry_interval=0
        )
        if port_check_result.get("success"):
            return port_check_result

    return {
        "success": False,
        "error": f"HDFS 시작 후 포트 확인 실패 (최대 {max_retries * retry_interval}초 대기)",
    }
```

### 수정 2: \_wait_for_hdfs_ports 호출 방식 개선

`_wait_for_hdfs_ports`를 호출할 때 `max_retries=1`이 아니라 실제 재시도 로직을 제거하고 직접 포트 확인만 하도록 수정하거나, 아니면 `_wait_for_hdfs_ports`를 사용하지 않고 직접 포트 확인 로직을 작성
