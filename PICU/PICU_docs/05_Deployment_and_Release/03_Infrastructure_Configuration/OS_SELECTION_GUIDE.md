# 라즈베리 파이 OS 선택 가이드

**작성 일시**: 2025-11-30
**대상**: 라즈베리 파이 4대 클러스터 OS 선택
**버전**: 1.0

---

## 📋 목차

1. [OS 옵션 비교](#os-옵션-비교)
2. [권장 사항](#권장-사항)
3. [설정 방법](#설정-방법)

---

## OS 옵션 비교

### 옵션 1: 전부 Ubuntu Server (권장) ⭐

**장점:**

- ✅ **일관성**: 모든 노드가 동일한 OS 환경
- ✅ **최신 패키지**: 최신 소프트웨어 패키지 사용 가능
- ✅ **문서화**: Ubuntu 관련 문서와 커뮤니티 지원이 풍부
- ✅ **클러스터 관리 용이**: 동일한 OS로 설정 스크립트 통일 가능
- ✅ **Hadoop 호환성**: Hadoop 공식 문서에서 Ubuntu/Debian 환경을 많이 다룸
- ✅ **Docker 지원**: Docker 설치 및 사용이 간편
- ✅ **업데이트**: 장기 지원(LTS) 버전으로 안정적

**단점:**

- ❌ 리소스 사용량이 Raspberry Pi OS보다 약간 높을 수 있음
- ❌ 일부 Raspberry Pi 전용 하드웨어 기능이 제한될 수 있음

**권장 버전:**

- Ubuntu Server 22.04 LTS (권장)
- Ubuntu Server 20.04 LTS (안정적)

---

### 옵션 2: 전부 Raspberry Pi OS

**장점:**

- ✅ **라즈베리 파이 최적화**: 하드웨어에 최적화됨
- ✅ **경량**: 리소스 사용량이 적음
- ✅ **하드웨어 지원**: GPIO, 카메라 등 하드웨어 기능 완벽 지원
- ✅ **공식 OS**: 라즈베리 파이 재단 공식 지원

**단점:**

- ❌ 패키지 버전이 상대적으로 오래될 수 있음
- ❌ 클러스터 환경에서의 문서가 상대적으로 적음
- ❌ 일부 최신 소프트웨어 설치 시 문제 발생 가능

---

### 옵션 3: Ubuntu + Raspberry Pi OS 혼합

**장점:**

- ✅ 역할에 따라 최적화 가능

**단점:**

- ❌ **관리 복잡도 증가**: 두 가지 OS 환경 관리 필요
- ❌ **설정 불일치**: 각 OS마다 다른 설정 방법
- ❌ **패키지 버전 차이**: 동일한 소프트웨어라도 버전이 다를 수 있음
- ❌ **디버깅 어려움**: 문제 발생 시 OS별로 다른 원인 확인 필요
- ❌ **문서화 복잡**: 두 가지 OS에 대한 문서 유지 필요

**권장하지 않음** ❌

---

## 권장 사항

### 🏆 최종 권장: 전부 Ubuntu Server 22.04 LTS

**이유:**

1. **클러스터 환경의 일관성**

   - 모든 노드가 동일한 환경 → 설정 스크립트 통일
   - 문제 발생 시 동일한 해결 방법 적용 가능
   - 배포 자동화 스크립트 작성이 간편

2. **프로젝트 요구사항 충족**

   - Hadoop, Kafka, Scrapy 모두 Ubuntu/Debian 환경에서 잘 작동
   - Python, Java 등 필수 소프트웨어 설치가 간편

3. **유지보수 용이성**

   - 동일한 OS로 문제 해결 시간 단축
   - 문서화 및 가이드 작성이 단순화

4. **확장성**
   - 향후 노드 추가 시 동일한 환경 구성 가능
   - Docker 등 컨테이너 기술 사용 시 호환성 우수

---

## 설정 방법

### Ubuntu Server 22.04 LTS 설치

#### 1. 이미지 다운로드

```bash
# Raspberry Pi Imager 사용 (권장)
# 또는 직접 다운로드
wget https://cdimage.ubuntu.com/releases/22.04.3/release/ubuntu-22.04.3-preinstalled-server-arm64+raspi.img.xz
```

#### 2. SD 카드에 설치

**Raspberry Pi Imager 사용:**

1. Raspberry Pi Imager 다운로드
2. "Choose OS" → "Other general-purpose OS" → "Ubuntu" → "Ubuntu Server 22.04 LTS"
3. SD 카드 선택
4. 설정 (SSH 활성화, 사용자 이름/비밀번호 설정)
5. Write

**또는 수동 설치:**

```bash
# macOS에서
unxz ubuntu-22.04.3-preinstalled-server-arm64+raspi.img.xz
diskutil unmountDisk /dev/diskX
sudo dd if=ubuntu-22.04.3-preinstalled-server-arm64+raspi.img of=/dev/rdiskX bs=1m
```

#### 3. 초기 설정

각 라즈베리 파이에 SD 카드를 삽입하고 부팅 후:

```bash
# 1. 업데이트
sudo apt update && sudo apt upgrade -y

# 2. 필수 패키지 설치
sudo apt install -y openssh-server python3 python3-pip git

# 3. Java 설치 (Hadoop, Kafka용)
sudo apt install -y openjdk-11-jdk

# 4. 호스트명 설정 (각 노드마다 다르게)
sudo hostnamectl set-hostname raspberry-master  # Node 1
# 또는
sudo hostnamectl set-hostname raspberry-worker1  # Node 2
# 등등
```

---

## 네트워크 설정 (Ubuntu Server)

### 고정 IP 설정 (netplan)

각 노드에서 `/etc/netplan/` 디렉토리의 설정 파일 수정:

**Node 1 (Master):**

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

**Node 2-4 (Workers):**
동일한 형식으로 각각 101, 102, 103으로 설정

**적용:**

```bash
sudo netplan apply
```

---

## 체크리스트

### Ubuntu Server 선택 시

- [ ] Ubuntu Server 22.04 LTS 이미지 다운로드
- [ ] 4개 SD 카드에 설치
- [ ] 각 노드 초기 설정 (업데이트, 필수 패키지)
- [ ] 호스트명 설정 (raspberry-master, raspberry-worker1-3)
- [ ] 고정 IP 설정
- [ ] SSH 키 복사 (패스워드 없이 접속)
- [ ] Java 설치 확인
- [ ] Python 3 설치 확인

---

## 성능 비교

| 항목          | Ubuntu Server 22.04 | Raspberry Pi OS |
| ------------- | ------------------- | --------------- |
| 부팅 시간     | 약간 느림           | 빠름            |
| 메모리 사용   | 약간 높음           | 낮음            |
| 패키지 최신도 | 최신                | 안정적          |
| 클러스터 관리 | ⭐⭐⭐⭐⭐          | ⭐⭐⭐          |
| 문서화        | ⭐⭐⭐⭐⭐          | ⭐⭐⭐⭐        |
| 하드웨어 지원 | ⭐⭐⭐⭐            | ⭐⭐⭐⭐⭐      |

**결론**: 클러스터 환경에서는 Ubuntu Server가 더 적합합니다.

---

## 다음 단계

OS 선택 후:

1. [RASPBERRY_PI_INITIAL_SETUP.md](./RASPBERRY_PI_INITIAL_SETUP.md) - 초기 설정 및 SSH 키 설정
2. [RASPBERRY_PI_SD_CLONE_GUIDE.md](./RASPBERRY_PI_SD_CLONE_GUIDE.md) - SD 카드 복제 및 클러스터 설정
3. [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) - 전체 배포 가이드

---

## 참고

- **프로젝트 문서**: "Raspberry Pi OS (Debian 기반) 또는 Ubuntu Server" 모두 지원
- **실제 사용**: 클러스터 환경에서는 Ubuntu Server 권장
- **하드웨어**: GPIO, 카메라 등 특수 하드웨어를 사용하지 않는다면 Ubuntu Server가 더 적합

---

**작성자**: PICU 프로젝트 팀
**최종 수정**: 2025-11-30
