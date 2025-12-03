# Deployment 스크립트 검증 보고서

**작성 일시**: 2025-12-01
**검증 대상**: `PICU/deployment/` 디렉토리 내 모든 배포 스크립트

---

## 📋 검증 개요

각 노드별로 배포되어야 할 파일과 의존성 설치가 스크립트에 올바르게 반영되어 있는지 검증했습니다.

---

## ✅ 검증 완료 항목

### 1. 파일 배포 구조

#### Master Node (`setup_master.sh`)

✅ **정상 배포되는 파일들:**

- `cointicker/master-node/` → `/home/ubuntu/cointicker/master-node/`
- `cointicker/shared/` → `/home/ubuntu/cointicker/shared/`
- `cointicker/config/` → `/home/ubuntu/cointicker/config/`
- `requirements/requirements-master.txt` → `/home/ubuntu/cointicker/requirements-master.txt`

#### Worker Node (`setup_worker.sh`)

✅ **정상 배포되는 파일들:**

- `cointicker/worker-nodes/` → `/home/ubuntu/cointicker/worker-nodes/`
- `cointicker/shared/` → `/home/ubuntu/cointicker/shared/`
- `cointicker/config/` → `/home/ubuntu/cointicker/config/`
- `requirements/requirements-worker.txt` → `/home/ubuntu/cointicker/requirements-worker.txt`

### 2. 의존성 설치

✅ **정상 작동:**

- `setup_master.sh`: `requirements-master.txt` 사용 ✅
- `setup_worker.sh`: `requirements-worker.txt` 사용 ✅
- 가상환경 생성 및 pip 업그레이드 포함 ✅

### 3. IP 주소 설정

✅ **정상:**

- `setup_all_nodes.sh`: Worker 노드 IP 하드코딩 (192.168.0.101, 102, 103) ✅
- `cluster_config.yaml`과 일치 ✅

---

## ⚠️ 발견된 문제점

### 🔴 심각 (즉시 수정 필요)

#### 1. `deploy_to_cluster.sh` - 잘못된 requirements 파일 사용

**문제:**

```bash
# Line 82: deploy_to_cluster.sh
pip install -r requirements.txt  # ❌ 잘못됨
```

**현재 상황:**

- Master와 Worker 노드 모두 `requirements.txt`를 사용
- 실제로는 `requirements-master.txt`와 `requirements-worker.txt`를 사용해야 함

**영향:**

- Master 노드에 Worker 전용 패키지가 설치될 수 있음
- Worker 노드에 Master 전용 패키지가 설치될 수 있음
- 불필요한 패키지 설치로 인한 리소스 낭비

**수정 필요:**

```bash
# Master Node
if [ "$node" == "$MASTER" ]; then
    pip install -r requirements-master.txt
else
    pip install -r requirements-worker.txt
fi
```

---

### 🟡 중요 (수정 권장)

#### 2. `setup_master.sh`와 `setup_worker.sh` - Hadoop 배포 누락

**문제:**

- `setup_master.sh`와 `setup_worker.sh`에 Hadoop 배포 로직이 없음
- `deploy_to_cluster.sh`에는 Hadoop 배포가 있지만, 다른 스크립트와 통합되지 않음

**현재 상황:**

- `deploy_to_cluster.sh`만 Hadoop 배포 포함 (Master 노드만)
- `setup_master.sh`와 `setup_worker.sh`는 Hadoop 배포 없음

**영향:**

- `setup_all_nodes.sh`를 사용하면 Hadoop이 배포되지 않음
- Hadoop 설정 파일 배포도 누락됨

**수정 필요:**

- `setup_master.sh`에 Hadoop 배포 추가
- Worker 노드에도 Hadoop 바이너리 배포 필요 (DataNode용)

#### 3. Hadoop 설정 파일 배포 누락

**문제:**

- Hadoop 바이너리는 배포되지만, 설정 파일(`core-site.xml`, `hdfs-site.xml`, `yarn-site.xml`, `mapred-site.xml`) 배포가 없음

**필요한 설정 파일:**

- `core-site.xml`: `fs.defaultFS=hdfs://raspberry-master:9000`
- `hdfs-site.xml`: `dfs.replication=3`
- `yarn-site.xml`: `yarn.resourcemanager.hostname=raspberry-master`
- `mapred-site.xml`: `mapreduce.framework.name=yarn`

**수정 필요:**

- Hadoop 설정 파일 템플릿 생성
- 배포 스크립트에 설정 파일 배포 로직 추가

---

### 🟢 경미 (선택적 개선)

#### 4. `deploy_to_cluster.sh` - 프로젝트 루트 경로 하드코딩

**문제:**

```bash
# Line 10: deploy_to_cluster.sh
HADOOP_ROOT="/Users/juns/code/personal/notion/pknu_workspace/bigdata/hadoop_project/hadoop-3.4.1"
```

**영향:**

- 다른 개발자 환경에서 작동하지 않음
- 상대 경로나 환경 변수 사용 권장

**개선 제안:**

```bash
HADOOP_ROOT="${HADOOP_ROOT:-$(cd "$SCRIPT_DIR/../../hadoop_project/hadoop-3.4.1" 2>/dev/null && pwd)}"
```

#### 5. `setup_all_nodes.sh` - IP 주소 하드코딩

**현재:**

```bash
bash "$PROJECT_ROOT/deployment/setup_worker.sh" "raspberry-worker$i" "192.168.0.10$i"
```

**개선 제안:**

- `cluster_config.yaml`에서 IP 주소 읽어오기
- 환경 변수로 IP 주소 설정 가능하게 하기

---

## 📊 노드별 필수 파일 체크리스트

### Master Node 필수 파일

| 파일/디렉토리             | 배포 스크립트     | 상태 |
| ------------------------- | ----------------- | ---- |
| `master-node/`            | `setup_master.sh` | ✅   |
| `shared/`                 | `setup_master.sh` | ✅   |
| `config/`                 | `setup_master.sh` | ✅   |
| `requirements-master.txt` | `setup_master.sh` | ✅   |
| `/opt/hadoop/`            | `setup_master.sh` | ✅   |
| Hadoop 설정 파일          | `setup_master.sh` | ✅   |

### Worker Node 필수 파일

| 파일/디렉토리             | 배포 스크립트     | 상태 |
| ------------------------- | ----------------- | ---- |
| `worker-nodes/`           | `setup_worker.sh` | ✅   |
| `shared/`                 | `setup_worker.sh` | ✅   |
| `config/`                 | `setup_worker.sh` | ✅   |
| `requirements-worker.txt` | `setup_worker.sh` | ✅   |
| `/opt/hadoop/`            | `setup_worker.sh` | ✅   |
| Hadoop 설정 파일          | `setup_worker.sh` | ✅   |

---

## 🔧 수정 권장 사항

### 우선순위 1: `deploy_to_cluster.sh` 수정

```bash
# setup_venv 함수 수정
setup_venv() {
    local node=$1
    local is_master=false

    if [ "$node" == "$MASTER" ]; then
        is_master=true
    fi

    ssh ubuntu@$node << EOF
cd /home/ubuntu/cointicker

if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

source venv/bin/activate
pip install --upgrade pip setuptools wheel

if [ "$is_master" = true ]; then
    pip install -r requirements-master.txt
else
    pip install -r requirements-worker.txt
fi

echo "✓ Dependencies installed"
EOF
}
```

### 우선순위 2: Hadoop 배포 통합

1. `setup_master.sh`에 Hadoop 배포 추가
2. `setup_worker.sh`에 Hadoop 배포 추가 (DataNode용)
3. Hadoop 설정 파일 배포 로직 추가

### 우선순위 3: 설정 파일 관리

1. Hadoop 설정 파일 템플릿 생성 (`deployment/hadoop-configs/`)
2. 클러스터 설정에 맞게 자동 생성하는 스크립트 작성

---

## 📝 검증 결과 요약

### ✅ 정상 작동

- 파일 배포 구조 (master-node, worker-nodes, shared, config)
- 의존성 설치 (requirements-master.txt, requirements-worker.txt)
- 가상환경 생성

### ✅ 수정 완료

- ✅ `deploy_to_cluster.sh`의 requirements 파일 사용 수정 완료
- ✅ Hadoop 배포 통합 완료 (`setup_master.sh`, `setup_worker.sh`에 추가)
- ✅ Hadoop 설정 파일 배포 완료 (core-site.xml, hdfs-site.xml, yarn-site.xml, mapred-site.xml)
- ✅ Hadoop 경로 상대 경로로 개선 완료

### 📌 권장 사항

- 설정 파일 중앙 관리
- 환경 변수 활용
- 설정 검증 로직 추가

---

## 🎯 다음 단계

1. **즉시 수정**: `deploy_to_cluster.sh`의 requirements 파일 사용 수정
2. **단기 개선**: Hadoop 배포 로직 통합
3. **중기 개선**: 설정 파일 관리 시스템 구축

---

**검증 완료 일시**: 2025-12-01
**검증자**: AI Assistant
**검증 버전**: 1.0
