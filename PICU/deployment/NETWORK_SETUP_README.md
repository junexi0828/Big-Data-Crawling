# 라즈베리파이 네트워크 설정 가이드

## 📁 파일 구조

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
├── deploy_netplan.sh            # 자동 배포 스크립트
└── NETWORK_SETUP_README.md      # 이 파일
```

### 파일 용도 구분

이 디렉토리에는 **두 가지 종류**의 네트워크 설정 파일이 있습니다:

| 파일 종류          | 용도                       | 사용 시점          | 배포 위치                             | 설명                              |
| ------------------ | -------------------------- | ------------------ | ------------------------------------- | --------------------------------- |
| `network-config-*` | SD 카드 초기 설정          | **첫 부팅 전**     | `/Volumes/system-boot/network-config` | cloud-init이 첫 부팅 시 자동 설정 |
| `netplan-*.yaml`   | 운영 중인 시스템 설정 변경 | **시스템 운영 중** | `/etc/netplan/99-static-ip.yaml`      | SSH로 접속하여 수동 배포          |

**중요**:

- ✅ 두 파일의 내용은 거의 동일하지만 **용도가 다릅니다**
- ✅ **SD 카드 초기 설정 시**: `network-config-*` 파일 사용
- ✅ **운영 중인 시스템 변경 시**: `netplan-*.yaml` 파일 사용

---

## 🚀 빠른 시작

### **시나리오 A: SD 카드 초기 설정 (새로 설치하는 경우) ⭐**

SD 카드를 처음 굽고 첫 부팅 전에 네트워크를 설정하는 경우:

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

### **시나리오 B: 운영 중인 시스템 네트워크 변경**

이미 부팅되어 운영 중인 라즈베리파이의 네트워크 설정을 변경하는 경우:

#### **방법 1: 자동 배포 스크립트 사용 (권장)**

```bash
cd /Users/juns/code/personal/notion/pknu_workspace/bigdata/PICU/deployment

# 전체 노드에 배포
./deploy_netplan.sh
# 옵션 5 선택 → 모든 노드에 자동 배포

# 특정 노드에만 배포
./deploy_netplan.sh
# 옵션 1-4 선택 → 개별 노드 배포
```

#### **방법 2: 수동 배포**

```bash
# Master Node
scp netplan-master.yaml ubuntu@192.168.0.100:/tmp/
ssh ubuntu@192.168.0.100 "sudo mv /tmp/netplan-master.yaml /etc/netplan/99-static-ip.yaml && \
                          sudo chmod 600 /etc/netplan/99-static-ip.yaml && \
                          sudo netplan apply"

# Worker Node 1
scp netplan-worker1.yaml ubuntu@192.168.0.101:/tmp/
ssh ubuntu@192.168.0.101 "sudo mv /tmp/netplan-worker1.yaml /etc/netplan/99-static-ip.yaml && \
                           sudo chmod 600 /etc/netplan/99-static-ip.yaml && \
                           sudo netplan apply"

# Worker Node 2, 3도 동일하게...
```

---

## 📋 네트워크 설정 내용

### **IP 할당**

| 노드     | 호스트명          | 유선 IP       | 무선 IP       | 우선순위  |
| -------- | ----------------- | ------------- | ------------- | --------- |
| Master   | raspberry-master  | 192.168.0.100 | 192.168.0.100 | 유선 우선 |
| Worker 1 | raspberry-worker1 | 192.168.0.101 | 192.168.0.101 | 유선 우선 |
| Worker 2 | raspberry-worker2 | 192.168.0.102 | 192.168.0.102 | 유선 우선 |
| Worker 3 | raspberry-worker3 | 192.168.0.103 | 192.168.0.103 | 유선 우선 |

### **WiFi 설정**

- **SSID**: `iptime` (2.4GHz)
- **비밀번호**: 설정 완료
- **자동 전환**: 유선 끊김 시 자동으로 무선 전환

### **라우팅 우선순위**

```
eth0 (유선):  metric 100  ← 1순위 (우선 사용)
wlan0 (무선): metric 200  ← 2순위 (백업)
```

---

## 🔧 네트워크 제어 명령어

### **인터페이스 상태 확인**

```bash
# Master 노드 접속
ssh ubuntu@raspberry-master

# 네트워크 인터페이스 확인
ip addr show

# 라우팅 테이블 확인
ip route show

# WiFi 상태 확인
ip link show wlan0
```

### **유선/무선 전환**

```bash
# 유선만 사용
sudo ip link set eth0 up
sudo ip link set wlan0 down

# 무선만 사용
sudo ip link set wlan0 up
sudo ip link set eth0 down

# 둘 다 활성화 (자동 우선순위)
sudo ip link set eth0 up
sudo ip link set wlan0 up
```

### **WiFi 테스트**

```bash
# WiFi 인터페이스로 핑 테스트
ping -c 3 -I wlan0 8.8.8.8

# WiFi 연결 확인
ip addr show wlan0 | grep "inet "
```

---

## 🛠️ 트러블슈팅

### **WiFi 연결 안 될 때**

```bash
# WiFi 인터페이스 재시작
sudo ip link set wlan0 down
sudo ip link set wlan0 up

# netplan 재적용
sudo netplan apply

# 로그 확인
sudo journalctl -u systemd-networkd -f
```

### **유선과 무선 충돌 문제**

```bash
# 라우팅 테이블 확인
ip route show

# 출력 예시:
# default via 192.168.0.1 dev eth0 proto static metric 100  ← 우선
# default via 192.168.0.1 dev wlan0 proto static metric 200 ← 백업
```

metric 값이 다르면 정상입니다.

### **SSH 연결 끊김**

유선 케이블 뽑으면 잠시 끊길 수 있지만, 무선으로 자동 전환됩니다 (약 5-10초).

---

## 📝 새 노드 추가 시

### **SD 카드 초기 설정용 (network-config)**

```bash
# 1. 기존 파일 복사
cp network-config-worker1 network-config-worker4

# 2. IP 주소 수정
# network-config-worker4 파일에서 192.168.0.101 → 192.168.0.104로 변경

# 3. SD 카드에 복사
cp network-config-worker4 /Volumes/system-boot/network-config
```

### **운영 중인 시스템 배포용 (netplan)**

```bash
# 1. 템플릿 복사
cp netplan-config.yaml.example netplan-worker4.yaml

# 2. IP 주소 수정
# netplan-worker4.yaml 파일에서 192.168.0.101 → 192.168.0.104로 변경

# 3. 배포
scp netplan-worker4.yaml ubuntu@192.168.0.104:/tmp/
ssh ubuntu@192.168.0.104 "sudo mv /tmp/netplan-worker4.yaml /etc/netplan/99-static-ip.yaml && \
                           sudo chmod 600 /etc/netplan/99-static-ip.yaml && \
                           sudo netplan apply"
```

---

## ⚠️ 주의사항

1. **파일 권한**: netplan 설정 파일은 반드시 `600` 권한

   ```bash
   sudo chmod 600 /etc/netplan/99-static-ip.yaml
   ```

2. **WiFi 비밀번호 보안**: Git에 커밋하지 말 것

   ```bash
   # .gitignore에 추가
   netplan-*.yaml
   network-config-*
   !netplan-config.yaml.example
   ```

   > ⚠️ **주의**: `network-config-*`와 `netplan-*.yaml` 파일에는 WiFi 비밀번호가 포함되어 있습니다!

3. **IP 중복 방지**: 각 노드는 고유한 IP 사용

4. **netplan apply 후**:
   - SSH 연결이 잠시 끊길 수 있음
   - 약 5-10초 후 재연결 시도

---

## 📚 참고 문서

- [RASPBERRY_PI_INITIAL_SETUP.md](../PICU_docs/guides/RASPBERRY_PI_INITIAL_SETUP.md) - SSH 키 설정
- [DEPLOYMENT_GUIDE.md](../PICU_docs/guides/DEPLOYMENT_GUIDE.md) - 전체 배포 가이드

---

**작성자**: PICU 프로젝트 팀
**최종 수정**: 2025-12-02
