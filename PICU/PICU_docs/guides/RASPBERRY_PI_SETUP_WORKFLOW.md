# 라즈베리 파이 클러스터 설정 워크플로우

**작성 일시**: 2025-11-30
**대상**: 라즈베리 파이 4대 클러스터 초기 설정 단계별 가이드
**버전**: 1.0

---

## 📋 전체 프로세스 요약

### 단계별 작업 흐름

```
1. 하나의 라즈베리 파이에 Ubuntu 설치
   ↓
2. 기본 설정 (사용자, SSH 등)
   ↓
3. SD 카드를 4개로 복제
   ↓
4. 각 라즈베리 파이에 복제된 SD 카드 삽입
   ↓
5. 각 노드별 고유 설정 (호스트명, IP 등)
```

---

## ✅ 답변: 처음부터 호스트명 설정할 필요 없음

**결론**: 처음 설치 시 호스트명을 설정할 필요 없습니다. 복제 후에 각각 변경하는 것이 더 효율적입니다.

**이유:**

- 복제 후에 한 번만 설정하면 되므로 더 빠름
- 처음부터 설정해도 복제 시 덮어씌워질 수 있음
- 각 노드마다 다른 호스트명이 필요하므로 복제 후 설정이 필수

---

## 📝 상세 단계별 가이드

### 1단계: 하나의 라즈베리 파이에 Ubuntu 설치

#### 1-1. Ubuntu Server 이미지 다운로드 및 설치

**라즈베리 파이 3 권장: Ubuntu Server 20.04 LTS (64-bit)**

**Raspberry Pi Imager 사용 (권장):**

1. Raspberry Pi Imager 다운로드 및 실행
2. "Choose OS" → "Other general-purpose OS" → "Ubuntu" → "Ubuntu Server 20.04 LTS"
3. SD 카드 선택
4. 설정 (⚙️ 아이콘 클릭):
   - **SSH 활성화**: ✅ 체크
   - **사용자 이름**: `ubuntu` (또는 원하는 이름)
   - **비밀번호**: 안전한 비밀번호 설정
   - **호스트명**: 설정하지 않아도 됨 (복제 후 변경 예정)
5. Write 클릭

#### 1-2. 라즈베리 파이 부팅 및 기본 확인

SD 카드를 라즈베리 파이에 삽입하고 부팅:

```bash
# 라즈베리 파이에 모니터/키보드 연결 후
# 또는 네트워크에서 IP 확인 후 SSH 접속

# IP 확인
hostname -I

# 기본 업데이트 (선택적, 시간이 걸릴 수 있음)
sudo apt update
sudo apt upgrade -y
```

---

### 2단계: SSH 키 복사 (개발 PC에서)

**개발 PC에서 실행:**

```bash
# 라즈베리 파이 IP 확인 (예: 192.168.0.60)
# SSH 키 복사
ssh-copy-id -i ~/.ssh/id_rsa.pub ubuntu@192.168.0.60

# 패스워드 없이 접속되는지 확인
ssh ubuntu@192.168.0.60
```

**이 단계까지 완료하면 기본 설정이 끝납니다!**

---

### 3단계: SD 카드 복제

#### 3-1. 이미지 생성 (macOS)

```bash
# 1. SD 카드가 마운트되어 있는지 확인
diskutil list

# 2. SD 카드 언마운트 (예: /dev/disk2)
diskutil unmountDisk /dev/disk2

# 3. 이미지 생성
sudo dd if=/dev/rdisk2 of=~/raspberry-pi-base.img bs=1m status=progress
```

#### 3-2. 다른 SD 카드에 복제 (3개)

```bash
# 각 SD 카드를 연결하고 diskutil list로 확인 후
sudo dd if=~/raspberry-pi-base.img of=/dev/rdisk3 bs=1m status=progress
sudo dd if=~/raspberry-pi-base.img of=/dev/rdisk4 bs=1m status=progress
sudo dd if=~/raspberry-pi-base.img of=/dev/rdisk5 bs=1m status=progress
```

**또는 Raspberry Pi Imager 사용:**

- "Use custom image" 선택
- 생성한 이미지 선택
- 각 SD 카드에 순차적으로 복제

---

### 4단계: 각 라즈베리 파이에 복제된 SD 카드 삽입 및 부팅

각 라즈베리 파이에 복제된 SD 카드를 삽입하고 부팅합니다.

**중요**: 이 시점에서는 아직 모든 노드가 동일한 설정입니다.

---

### 5단계: 각 노드별 고유 설정

**각 라즈베리 파이마다 다음을 설정해야 합니다:**

#### 5-1. 호스트명 변경

**Node 1 (Master):**

```bash
sudo hostnamectl set-hostname raspberry-master
```

**Node 2 (Worker 1):**

```bash
sudo hostnamectl set-hostname raspberry-worker1
```

**Node 3 (Worker 2):**

```bash
sudo hostnamectl set-hostname raspberry-worker2
```

**Node 4 (Worker 3):**

```bash
sudo hostnamectl set-hostname raspberry-worker3
```

#### 5-2. 고정 IP 설정

**Node 1 (Master) - `/etc/netplan/50-cloud-init.yaml` 또는 유사한 파일:**

```bash
sudo nano /etc/netplan/50-cloud-init.yaml
```

```yaml
network:
  version: 2
  ethernets:
    eth0:
      dhcp4: no
      addresses:
        - 192.168.0.100/24
      gateway4: 192.168.0.1
      nameservers:
        addresses:
          - 8.8.8.8
          - 8.8.4.4
```

**적용:**

```bash
sudo netplan apply
```

**Node 2-4 (Workers):**

- Node 2: `192.168.0.101`
- Node 3: `192.168.0.102`
- Node 4: `192.168.0.103`

#### 5-3. /etc/hosts 파일 수정 (모든 노드에서 동일)

```bash
sudo nano /etc/hosts
```

다음 내용 추가:

```
192.168.0.100 raspberry-master
192.168.0.101 raspberry-worker1
192.168.0.102 raspberry-worker2
192.168.0.103 raspberry-worker3
```

#### 5-4. 재부팅

```bash
sudo reboot
```

---

### 6단계: SSH 키 복사 (각 노드에)

**개발 PC에서 각 노드에 SSH 키 복사:**

```bash
# 사용자 이름: ubuntu (모든 노드 동일)
# 각 노드의 IP가 설정된 후
ssh-copy-id -i ~/.ssh/id_rsa.pub ubuntu@192.168.0.100  # Master
ssh-copy-id -i ~/.ssh/id_rsa.pub ubuntu@192.168.0.101  # Worker 1
ssh-copy-id -i ~/.ssh/id_rsa.pub ubuntu@192.168.0.102  # Worker 2
ssh-copy-id -i ~/.ssh/id_rsa.pub ubuntu@192.168.0.103  # Worker 3

# 또는 호스트명으로 접속 (호스트명은 각각 다름)
ssh-copy-id -i ~/.ssh/id_rsa.pub ubuntu@raspberry-master
ssh-copy-id -i ~/.ssh/id_rsa.pub ubuntu@raspberry-worker1
ssh-copy-id -i ~/.ssh/id_rsa.pub ubuntu@raspberry-worker2
ssh-copy-id -i ~/.ssh/id_rsa.pub ubuntu@raspberry-worker3
```

---

## ✅ 체크리스트

### 1단계: 기본 설치

- [ ] Ubuntu Server 20.04 LTS 설치
- [ ] 사용자 이름 설정 (예: `juns`)
- [ ] 비밀번호 설정
- [ ] SSH 활성화
- [ ] 기본 업데이트 (선택적)

### 2단계: SSH 키 설정

- [ ] 개발 PC에서 SSH 키 복사
- [ ] 패스워드 없이 접속 확인

### 3단계: SD 카드 복제

- [ ] 원본 SD 카드에서 이미지 생성
- [ ] 3개 SD 카드에 복제

### 4단계: 각 노드 설정

- [ ] Node 1: 호스트명 → `raspberry-master`, IP → `192.168.0.100`
- [ ] Node 2: 호스트명 → `raspberry-worker1`, IP → `192.168.0.101`
- [ ] Node 3: 호스트명 → `raspberry-worker2`, IP → `192.168.0.102`
- [ ] Node 4: 호스트명 → `raspberry-worker3`, IP → `192.168.0.103`
- [ ] 모든 노드에 `/etc/hosts` 파일 수정
- [ ] 모든 노드 재부팅

### 5단계: 최종 확인

- [ ] 각 노드에 SSH 키 복사
- [ ] 패스워드 없이 모든 노드 접속 확인
- [ ] 네트워크 연결 확인 (`ping` 테스트)

---

## 🎯 핵심 정리

### 처음 설치 시 설정할 것:

- ✅ **사용자 이름** (예: `juns` 또는 `pi`) - **필수!**
  - **SSH 접속에 사용**: `ssh juns@192.168.0.XX`
  - **배포 스크립트에서 사용**: `MASTER_USER="juns"` 또는 환경 변수로 설정
  - **파일 경로에 사용**: `/home/juns/cointicker` 또는 `/home/pi/cointicker`
  - **없으면 SSH 접속 불가능!**
- ✅ **비밀번호**
- ✅ **SSH 활성화**

### 처음 설치 시 설정하지 않아도 되는 것:

- ❌ **호스트명** (복제 후 각각 변경)
- ❌ **고정 IP** (복제 후 각각 설정)

### 사용자 이름이 사용되는 곳:

1. **SSH 접속** (필수)

   ```bash
   ssh juns@192.168.0.100  # 사용자 이름 없으면 접속 불가
   ```

2. **배포 스크립트** (`setup_master.sh`, `setup_worker.sh`)

   ```bash
   # 기본값: pi (스크립트에서)
   MASTER_USER="${MASTER_USER:-pi}"

   # 환경 변수로 변경 가능:
   MASTER_USER=juns ./setup_master.sh
   ```

3. **파일 경로**

   ```bash
   PROJECT_DIR="/home/pi/cointicker"  # 또는 /home/juns/cointicker
   ```

4. **rsync, scp 등 파일 전송**
   ```bash
   rsync ... juns@raspberry-master:/home/juns/cointicker
   ```

**결론**: 사용자 이름은 **반드시 필요**합니다. Ubuntu Server 설치 시 기본 사용자를 생성해야 합니다.

### 복제 후 반드시 설정할 것:

- ✅ **호스트명** (각 노드마다 다르게)
  - `raspberry-master`, `raspberry-worker1`, `raspberry-worker2`, `raspberry-worker3`
  - ⚠️ **사용자 이름이 아님!** 사용자 이름은 그대로 `ubuntu`
- ✅ **고정 IP** (각 노드마다 다르게)
- ✅ **/etc/hosts** (모든 노드에 동일하게)

### 사용자 이름 vs 호스트명 정리:

| 항목              | 사용자 이름 (User)         | 호스트명 (Hostname)                      |
| ----------------- | -------------------------- | ---------------------------------------- |
| **Ubuntu 기본값** | `ubuntu`                   | `ubuntu`                                 |
| **복제 후 변경**  | ❌ 변경 불필요             | ✅ 각 노드마다 변경                      |
| **SSH 접속 예시** | `ssh ubuntu@192.168.0.100` | `ssh ubuntu@raspberry-master`            |
| **설정 위치**     | 설치 시 설정               | `/etc/hostname`                          |
| **모든 노드**     | 동일 (`ubuntu`)            | 다름 (master, worker1, worker2, worker3) |

---

## 💡 팁

### 자동화 스크립트 (선택적)

각 노드에서 실행할 수 있는 설정 스크립트:

```bash
#!/bin/bash
# setup_node.sh

NODE_NUMBER=$1  # 0=master, 1-3=workers
NODE_IP="192.168.0.10${NODE_NUMBER}"

if [ $NODE_NUMBER -eq 0 ]; then
    HOSTNAME="raspberry-master"
else
    HOSTNAME="raspberry-worker${NODE_NUMBER}"
fi

# 호스트명 설정
sudo hostnamectl set-hostname $HOSTNAME

# /etc/hosts 수정
echo "192.168.0.100 raspberry-master" | sudo tee -a /etc/hosts
echo "192.168.0.101 raspberry-worker1" | sudo tee -a /etc/hosts
echo "192.168.0.102 raspberry-worker2" | sudo tee -a /etc/hosts
echo "192.168.0.103 raspberry-worker3" | sudo tee -a /etc/hosts

echo "✅ Node 설정 완료: $HOSTNAME ($NODE_IP)"
echo "재부팅이 필요합니다: sudo reboot"
```

**사용법:**

```bash
# Master 노드에서
chmod +x setup_node.sh
./setup_node.sh 0

# Worker 1에서
./setup_node.sh 1

# Worker 2에서
./setup_node.sh 2

# Worker 3에서
./setup_node.sh 3
```

---

## 다음 단계

설정이 완료되면:

1. [RASPBERRY_PI_SD_CLONE_GUIDE.md](./RASPBERRY_PI_SD_CLONE_GUIDE.md) - 상세 설정 가이드
2. [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) - 전체 배포 가이드

---

**작성자**: PICU 프로젝트 팀
**최종 수정**: 2025-11-30
