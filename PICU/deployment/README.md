# PICU 배포 스크립트 가이드

**작성 일시**: 2025-12-01
**버전**: 2.0

---

## 📋 개요

이 디렉토리는 라즈베리파이 클러스터에 PICU 프로젝트를 배포하기 위한 스크립트를 포함합니다.

**중요**: 모든 스크립트는 **개발 PC에서 실행**하며, 스크립트가 자동으로 SSH로 각 노드에 연결하여 배포합니다.

---

## 🚀 빠른 시작

### 1. 사전 준비

#### 네트워크 설정 (Static IP)

각 노드에 고정 IP 주소를 설정해야 합니다.

**IP 할당**:

| 노드     | 호스트명          | IP 주소       | 용도                      |
| -------- | ----------------- | ------------- | ------------------------- |
| Master   | raspberry-master  | 192.168.0.100 | NameNode, ResourceManager |
| Worker 1 | raspberry-worker1 | 192.168.0.101 | DataNode, NodeManager     |
| Worker 2 | raspberry-worker2 | 192.168.0.102 | DataNode, NodeManager     |
| Worker 3 | raspberry-worker3 | 192.168.0.103 | DataNode, NodeManager     |

**네트워크 설정 파일 종류**:

이 디렉토리에는 두 가지 종류의 네트워크 설정 파일이 있습니다:

1. **`network-config-*` 파일들** (SD 카드 초기 설정용)

   - **용도**: SD 카드의 `/Volumes/system-boot/` 파티션에 복사
   - **사용 시점**: 새 SD 카드를 굽고 **첫 부팅 전**
   - **동작**: cloud-init이 첫 부팅 시 자동으로 네트워크 설정 적용
   - **파일**: `network-config-master`, `network-config-worker1`, `network-config-worker2`, `network-config-worker3`

2. **`netplan-*.yaml` 파일들** (운영 중인 시스템 배포용)
   - **용도**: 이미 부팅된 라즈베리파이의 `/etc/netplan/` 디렉토리에 배포
   - **사용 시점**: 이미 운영 중인 시스템의 네트워크 설정을 변경할 때
   - **동작**: SSH로 접속하여 수동으로 배포 후 `netplan apply`
   - **파일**: `netplan-master.yaml`, `netplan-worker1.yaml`, `netplan-worker2.yaml`, `netplan-worker3.yaml`

**시나리오별 사용 방법**:

**시나리오 A: SD 카드 초기 설정 (새로 설치하는 경우) ⭐**

```bash
# SD 카드를 Mac에 연결
# /Volumes/system-boot/ 파티션이 마운트됨

# Master Node SD 카드
cp network-config-master /Volumes/system-boot/network-config

# Worker Node 1 SD 카드
cp network-config-worker1 /Volumes/system-boot/network-config

# Worker Node 2, 3도 동일하게...
# SD 카드를 라즈베리파이에 삽입 후 첫 부팅 시 자동 설정됨
```

> 💡 **팁**: `prepare_sd_cards.sh` 스크립트를 사용하면 더 편리합니다.

**시나리오 B: 운영 중인 시스템 네트워크 변경**

```bash
cd /Users/juns/code/personal/notion/pknu_workspace/bigdata/PICU/deployment

# 방법 1: 자동 배포 스크립트 사용 (권장)
./deploy_netplan.sh
# 옵션 5 선택 → 모든 노드에 자동 배포

# 방법 2: 수동 배포
scp netplan-master.yaml ubuntu@192.168.0.100:/tmp/
ssh ubuntu@192.168.0.100 "sudo mv /tmp/netplan-master.yaml /etc/netplan/99-static-ip.yaml && \
                          sudo chmod 600 /etc/netplan/99-static-ip.yaml && \
                          sudo netplan apply"
```

**네트워크 설정 특징**:

- **유선 우선**: `eth0` (metric 100) - 1순위
- **무선 백업**: `wlan0` (metric 200) - 2순위
- **자동 전환**: 유선 끊김 시 자동으로 무선 전환
- **WiFi SSID**: `iptime` (2.4GHz)

**네트워크 설정 확인**:

```bash
# 각 노드에서 IP 확인
ssh ubuntu@raspberry-master "ip addr show | grep 'inet '"
ssh ubuntu@raspberry-worker1 "ip addr show | grep 'inet '"

# 라우팅 테이블 확인
ssh ubuntu@raspberry-master "ip route show"
```

> 📖 **상세 가이드**: [NETWORK_SETUP_README.md](./NETWORK_SETUP_README.md) 참고

#### SSH 키 설정

```bash
# 개발 PC에서 각 노드에 SSH 키 복사
ssh-copy-id ubuntu@raspberry-master      # 192.168.0.100
ssh-copy-id ubuntu@raspberry-worker1     # 192.168.0.101
ssh-copy-id ubuntu@raspberry-worker2     # 192.168.0.102
ssh-copy-id ubuntu@raspberry-worker3     # 192.168.0.103
```

#### 연결 확인

```bash
# 패스워드 없이 접속되는지 확인
ssh ubuntu@raspberry-master "echo 'OK'"
ssh ubuntu@raspberry-worker1 "echo 'OK'"
ssh ubuntu@raspberry-worker2 "echo 'OK'"
ssh ubuntu@raspberry-worker3 "echo 'OK'"
```

### 2. 배포 실행

#### 방법 1: 모든 노드 한 번에 배포 (권장) ⭐

```bash
# 개발 PC에서
cd /Users/juns/code/personal/notion/pknu_workspace/bigdata/PICU/deployment

# 한 번만 실행하면 모든 노드에 자동 배포
./setup_all_nodes.sh
```

**이 스크립트가 하는 일**:

1. Master Node 배포 (`setup_master.sh` 호출)
2. Worker Node 1 배포 (`setup_worker.sh` 호출)
3. Worker Node 2 배포 (`setup_worker.sh` 호출)
4. Worker Node 3 배포 (`setup_worker.sh` 호출)

#### 방법 2: 개별 노드 배포

```bash
# 개발 PC에서
cd PICU/deployment

# Master Node 배포
./setup_master.sh

# Worker Nodes 개별 배포
./setup_worker.sh raspberry-worker1 192.168.0.101
./setup_worker.sh raspberry-worker2 192.168.0.102
./setup_worker.sh raspberry-worker3 192.168.0.103
```

---

## 📁 스크립트 설명

### `setup_all_nodes.sh` ⭐ **권장**

**모든 노드를 한 번에 배포하는 통합 스크립트**

**사용법**:

```bash
./setup_all_nodes.sh
```

**기능**:

- Master Node 1개 자동 배포
- Worker Node 3개 자동 배포 (순차 실행)

**실행 위치**: 개발 PC

---

### `setup_master.sh`

**Master Node (라즈베리파이 #1) 배포 스크립트**

**사용법**:

```bash
./setup_master.sh
```

**기능**:

1. 코드 배포: `master-node/`, `shared/`, `config/`
2. 가상환경 생성 및 의존성 설치 (`requirements-master.txt`)
3. Hadoop 배포 (`/opt/hadoop`) + NameNode 설정
4. 환경 변수 설정

**배포 대상**: `ubuntu@192.168.0.100` (raspberry-master)

**실행 위치**: 개발 PC

---

### `setup_worker.sh`

**Worker Node (라즈베리파이 #2,3,4) 배포 스크립트**

**사용법**:

```bash
./setup_worker.sh <hostname> <ip_address>

# 예시
./setup_worker.sh raspberry-worker1 192.168.0.101
./setup_worker.sh raspberry-worker2 192.168.0.102
./setup_worker.sh raspberry-worker3 192.168.0.103
```

**기능**:

1. 코드 배포: `worker-nodes/`, `shared/`, `config/`
2. 가상환경 생성 및 의존성 설치 (`requirements-worker.txt`)
3. Hadoop 배포 (`/opt/hadoop`) + DataNode 설정
4. 환경 변수 설정

**실행 위치**: 개발 PC

---

### `deploy_to_cluster.sh`

**대체 배포 스크립트 (전체 프로젝트 배포)**

**사용법**:

```bash
# 모든 노드 배포
./deploy_to_cluster.sh

# 특정 노드만 배포
./deploy_to_cluster.sh 192.168.0.100
```

**기능**:

- 전체 프로젝트 디렉토리 배포
- 가상환경 설정
- Hadoop 배포 (Master/Worker 구분)

**실행 위치**: 개발 PC

---

## 🔍 배포 프로세스 상세

### 스크립트 동작 원리

1. **개발 PC에서 스크립트 실행**

   ```bash
   ./setup_all_nodes.sh
   ```

2. **스크립트가 자동으로 수행**:

   - `rsync`로 파일 전송
   - `ssh ubuntu@<IP> "명령어"`로 원격 명령 실행
   - 각 노드에 순차적으로 배포

3. **각 노드에서 자동 실행**:
   - 파일 수신 및 배치
   - 가상환경 생성
   - 의존성 설치
   - Hadoop 설정

### 배포되는 파일

#### Master Node

- `cointicker/master-node/` → `/home/ubuntu/cointicker/master-node/`
- `cointicker/shared/` → `/home/ubuntu/cointicker/shared/`
- `cointicker/config/` → `/home/ubuntu/cointicker/config/`
- `requirements/requirements-master.txt` → `/home/ubuntu/cointicker/`
- `hadoop_project/hadoop-3.4.1/` → `/opt/hadoop/`

#### Worker Node

- `cointicker/worker-nodes/` → `/home/ubuntu/cointicker/worker-nodes/`
- `cointicker/shared/` → `/home/ubuntu/cointicker/shared/`
- `cointicker/config/` → `/home/ubuntu/cointicker/config/`
- `requirements/requirements-worker.txt` → `/home/ubuntu/cointicker/`
- `hadoop_project/hadoop-3.4.1/` → `/opt/hadoop/`

---

## ⚙️ 환경 변수

### Hadoop 경로 설정

기본값: `../../hadoop_project/hadoop-3.4.1`

다른 경로 사용 시:

```bash
export HADOOP_ROOT="/path/to/hadoop-3.4.1"
./setup_all_nodes.sh
```

### 노드 IP 주소 변경

기본값:

- Master: `192.168.0.100`
- Worker 1: `192.168.0.101`
- Worker 2: `192.168.0.102`
- Worker 3: `192.168.0.103`

변경 시:

```bash
# Master Node
MASTER_IP=192.168.1.100 ./setup_master.sh

# Worker Node
./setup_worker.sh raspberry-worker1 192.168.1.101
```

---

## ✅ 배포 확인

### 각 노드에 접속하여 확인

```bash
# Master Node
ssh ubuntu@raspberry-master
cd /home/ubuntu/cointicker
ls -la                    # 파일 확인
source venv/bin/activate  # 가상환경 활성화
hadoop version            # Hadoop 확인

# Worker Node
ssh ubuntu@raspberry-worker1
cd /home/ubuntu/cointicker
ls -la
source venv/bin/activate
hadoop version
```

### 배포 상태 확인

```bash
# 각 노드에서
cd /home/ubuntu/cointicker
ls -la                    # 파일 확인
test -d venv && echo "가상환경 존재" || echo "가상환경 없음"
test -d /opt/hadoop && echo "Hadoop 설치됨" || echo "Hadoop 없음"
```

---

## 🐛 문제 해결

### SSH 연결 실패

```bash
# SSH 키 확인
ls -la ~/.ssh/id_ed25519.pub

# 키 재복사
ssh-copy-id ubuntu@raspberry-master
```

### Hadoop 경로 오류

```bash
# Hadoop 경로 확인
ls -la ../../hadoop_project/hadoop-3.4.1

# 환경 변수 설정
export HADOOP_ROOT="/정확한/경로/hadoop-3.4.1"
```

### rsync 오류

```bash
# 네트워크 연결 확인
ping 192.168.0.100
ping 192.168.0.101

# SSH 연결 확인
ssh ubuntu@raspberry-master "echo 'OK'"
```

### 네트워크 설정 오류

```bash
# 네트워크 인터페이스 확인
ssh ubuntu@raspberry-master "ip addr show"

# netplan 설정 확인
ssh ubuntu@raspberry-master "sudo cat /etc/netplan/99-static-ip.yaml"

# netplan 재적용
ssh ubuntu@raspberry-master "sudo netplan apply"

# WiFi 연결 확인
ssh ubuntu@raspberry-master "ip link show wlan0"
```

---

## 🌐 네트워크 설정 상세

### 각 노드별 네트워크 구성

| 노드     | 호스트명          | 유선 IP       | 무선 IP       | 우선순위  |
| -------- | ----------------- | ------------- | ------------- | --------- |
| Master   | raspberry-master  | 192.168.0.100 | 192.168.0.100 | 유선 우선 |
| Worker 1 | raspberry-worker1 | 192.168.0.101 | 192.168.0.101 | 유선 우선 |
| Worker 2 | raspberry-worker2 | 192.168.0.102 | 192.168.0.102 | 유선 우선 |
| Worker 3 | raspberry-worker3 | 192.168.0.103 | 192.168.0.103 | 유선 우선 |

### 네트워크 파일 구조

```
deployment/
├── network-config-master      # SD 카드 초기 설정용 (Master)
├── network-config-worker1     # SD 카드 초기 설정용 (Worker 1)
├── network-config-worker2     # SD 카드 초기 설정용 (Worker 2)
├── network-config-worker3     # SD 카드 초기 설정용 (Worker 3)
├── netplan-config.yaml.example  # 템플릿 (WiFi 정보 입력 필요)
├── netplan-master.yaml          # 운영 중인 시스템 배포용 (Master)
├── netplan-worker1.yaml         # 운영 중인 시스템 배포용 (Worker 1)
├── netplan-worker2.yaml         # 운영 중인 시스템 배포용 (Worker 2)
├── netplan-worker3.yaml         # 운영 중인 시스템 배포용 (Worker 3)
└── deploy_netplan.sh            # 자동 배포 스크립트
```

### 파일 용도 구분

| 파일 종류          | 용도                       | 사용 시점      | 배포 위치                             |
| ------------------ | -------------------------- | -------------- | ------------------------------------- |
| `network-config-*` | SD 카드 초기 설정          | 첫 부팅 전     | `/Volumes/system-boot/network-config` |
| `netplan-*.yaml`   | 운영 중인 시스템 설정 변경 | 시스템 운영 중 | `/etc/netplan/99-static-ip.yaml`      |

**중요**:

- ✅ **SD 카드 초기 설정 시**: `network-config-*` 파일 사용
- ✅ **운영 중인 시스템 변경 시**: `netplan-*.yaml` 파일 사용
- ⚠️ 두 파일은 용도가 다르며, 내용은 거의 동일하지만 사용 시점과 방법이 다릅니다

### 네트워크 제어 명령어

```bash
# 네트워크 인터페이스 확인
ssh ubuntu@raspberry-master "ip addr show"

# 라우팅 테이블 확인
ssh ubuntu@raspberry-master "ip route show"

# WiFi 상태 확인
ssh ubuntu@raspberry-master "ip link show wlan0"

# 유선/무선 전환
ssh ubuntu@raspberry-master "sudo ip link set eth0 up"  # 유선 활성화
ssh ubuntu@raspberry-master "sudo ip link set wlan0 up" # 무선 활성화
```

> 📖 **상세 가이드**: [NETWORK_SETUP_README.md](./NETWORK_SETUP_README.md) 참고

---

## 📚 관련 문서

- [DEPLOYMENT_GUIDE.md](../../PICU_docs/guides/DEPLOYMENT_GUIDE.md) - 전체 배포 가이드
- [DEPLOYMENT_VALIDATION_REPORT.md](./DEPLOYMENT_VALIDATION_REPORT.md) - 배포 스크립트 검증 보고서
- [NETWORK_SETUP_README.md](./NETWORK_SETUP_README.md) - 네트워크 설정 상세 가이드

---

**마지막 업데이트**: 2025-12-01
