# CoinTicker 자동화 설정 가이드

**작성일**: 2025-12-02
**버전**: 1.0.0

---

## 📋 목차

1. [개요](#개요)
2. [GUI 자동 시작 설정](#gui-자동-시작-설정)
3. [Systemd 서비스 관리](#systemd-서비스-관리)
4. [충돌 방지 시스템](#충돌-방지-시스템)
5. [설정 파일 구조](#설정-파일-구조)
6. [사용 예시](#사용-예시)
7. [문제 해결](#문제-해결)

---

## 개요

CoinTicker 프로젝트는 두 가지 자동화 방식을 지원합니다:

### 1️⃣ GUI 자동 시작

- **목적**: GUI 실행 시 필요한 프로세스를 자동으로 시작
- **범위**: GUI가 실행되는 동안만 작동
- **설정**: `config/gui_config.yaml` 파일

### 2️⃣ Systemd 서비스

- **목적**: 시스템 부팅 시 자동 시작, GUI 없이 백그라운드 실행
- **범위**: 시스템 전체, GUI와 독립적
- **설정**: systemd 서비스 파일 + GUI Config 탭

### 자동화 방식 비교

| 특징                | GUI 자동 시작                | Systemd 서비스          |
| ------------------- | ---------------------------- | ----------------------- |
| GUI 필요 여부       | ✅ 필요                      | ❌ 불필요               |
| 부팅 시 자동 시작   | ❌ 불가능                    | ✅ 가능                 |
| 장애 시 자동 재시작 | ❌ 없음                      | ✅ 자동 재시작          |
| 설정 위치           | gui_config.yaml              | systemd 서비스          |
| 제어 방법           | GUI 버튼                     | systemctl 명령어 + GUI  |
| 적용 대상           | Backend, Frontend, Spider 등 | Tier 1/2 오케스트레이터 |

---

## GUI 자동 시작 설정

### 설정 파일 위치

```
PICU/cointicker/config/gui_config.yaml
```

### 기본 설정 구조

```yaml
gui:
  auto_start:
    enabled: true # GUI 시작 시 자동 시작 활성화
    processes:
      - backend # 백엔드 서버
      - frontend # 프론트엔드 서버
```

### 자동 시작 가능한 프로세스

| 프로세스 이름 | 설명                  | 기본값      |
| ------------- | --------------------- | ----------- |
| `backend`     | 백엔드 API 서버       | ✅ 활성화   |
| `frontend`    | 프론트엔드 웹 서버    | ✅ 활성화   |
| `spider`      | 웹 크롤러 (Scrapy)    | ❌ 비활성화 |
| `kafka`       | Kafka 메시지 큐       | ❌ 비활성화 |
| `mapreduce`   | MapReduce 데이터 처리 | ❌ 비활성화 |

### GUI에서 설정하기

1. **CoinTicker GUI 실행**

   ```bash
   cd /Users/juns/code/personal/notion/pknu_workspace/bigdata/PICU/cointicker
   python gui/main.py
   ```

2. **Config 탭 선택**

   - 상단 탭에서 "Config" 클릭

3. **자동 시작 설정 섹션 찾기**

   - 스크롤하여 "자동 시작 설정" 그룹 박스 찾기

4. **원하는 프로세스 선택**

   ```
   ☑ GUI 시작 시 자동으로 프로세스 시작

   자동 시작할 프로세스:
   ☑ Backend (백엔드 서버)
   ☑ Frontend (프론트엔드 서버)
   ☐ Spider (웹 크롤러)
   ☐ Kafka (메시지 큐)
   ☐ MapReduce (데이터 처리)
   ```

5. **설정 저장**
   - 하단의 "GUI 설정 저장" 버튼 클릭

### 수동으로 설정 파일 편집

```yaml
# config/gui_config.yaml
gui:
  auto_start:
    enabled: true
    processes:
      - backend
      - frontend
      - spider # Spider도 자동 시작
      - kafka # Kafka도 자동 시작
```

저장 후 GUI를 재시작하면 설정이 적용됩니다.

### 자동 시작 비활성화

**방법 1: GUI에서**

- Config 탭 → "GUI 시작 시 자동으로 프로세스 시작" 체크박스 해제

**방법 2: 설정 파일에서**

```yaml
auto_start:
  enabled: false # 자동 시작 완전 비활성화
```

---

## Systemd 서비스 관리

### 지원하는 서비스

#### 1. Tier 1 오케스트레이터

- **설명**: 라즈베리파이 클러스터에서 크롤링 → MapReduce → HDFS 저장 전체 관리
- **대상**: Master 노드 (raspberry-master)
- **스크립트**: `deployment/create_orchestrator_service.sh`
- **서비스 이름**: `cointicker-orchestrator`

#### 2. Tier 2 파이프라인 스케줄러

- **설명**: HDFS → DB 적재 + 감성분석 + 인사이트 생성 자동화
- **대상**: Tier 2 서버 (외부 서버 또는 로컬)
- **스크립트**: `deployment/create_tier2_scheduler_service.sh`
- **서비스 이름**: `cointicker-tier2-scheduler`

### Tier 1 오케스트레이터 설치

#### 방법 1: GUI에서 설치 (권장)

1. **Config 탭 → Systemd 서비스 설정**
2. **"Tier 1 오케스트레이터 서비스 활성화" 체크**
3. **"서비스 설치" 버튼 클릭**
4. **sudo 비밀번호 입력**
5. **"부팅 시 자동 시작" 체크 (선택사항)**
6. **"GUI 설정 저장" 클릭**

#### 방법 2: 명령줄에서 설치

```bash
# Master 노드에 SSH 접속
ssh ubuntu@raspberry-master

# 스크립트 실행
cd /home/ubuntu/cointicker/deployment
bash create_orchestrator_service.sh
```

#### 서비스 제어 명령어

```bash
# 서비스 시작
sudo systemctl start cointicker-orchestrator

# 서비스 중지
sudo systemctl stop cointicker-orchestrator

# 서비스 재시작
sudo systemctl restart cointicker-orchestrator

# 서비스 상태 확인
sudo systemctl status cointicker-orchestrator

# 로그 확인 (실시간)
sudo journalctl -u cointicker-orchestrator -f

# 부팅 시 자동 시작 활성화
sudo systemctl enable cointicker-orchestrator

# 부팅 시 자동 시작 비활성화
sudo systemctl disable cointicker-orchestrator
```

### Tier 2 스케줄러 설치

#### 로컬 설치 (Tier 2 서버가 현재 머신)

```bash
cd /Users/juns/code/personal/notion/pknu_workspace/bigdata/PICU/deployment
bash create_tier2_scheduler_service.sh
```

#### 원격 서버에 설치

```bash
# 환경 변수 설정
export TIER2_USER=ubuntu
export TIER2_HOST=192.168.1.100
export PROJECT_DIR=/home/ubuntu/cointicker

# 스크립트 실행 (SSH를 통해 원격 서버에 자동 설치)
bash create_tier2_scheduler_service.sh
```

**환경 변수 설명:**

- `TIER2_USER`: Tier 2 서버의 사용자 이름 (기본값: ubuntu)
- `TIER2_HOST`: Tier 2 서버 IP 또는 호스트명 (기본값: localhost)
- `PROJECT_DIR`: 프로젝트 경로 (기본값: /home/ubuntu/cointicker)

#### GUI에서 제어

1. **Config 탭 → Systemd 서비스 설정**
2. **Tier 2 파이프라인 스케줄러 섹션**
3. **버튼 사용:**
   - "서비스 설치" - 서비스 설치 (로컬만)
   - "서비스 시작" - 서비스 시작
   - "서비스 중지" - 서비스 중지
   - "상태 확인" - 현재 상태 확인

### Systemd 서비스 파일 구조

#### Tier 1 오케스트레이터

```ini
[Unit]
Description=CoinTicker Pipeline Orchestrator
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/cointicker
Environment="PATH=/home/ubuntu/cointicker/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/home/ubuntu/cointicker/venv/bin/python /home/ubuntu/cointicker/master-node/orchestrator.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

#### Tier 2 스케줄러

```ini
[Unit]
Description=CoinTicker Tier 2 Pipeline Scheduler
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/cointicker
Environment="PATH=/home/ubuntu/cointicker/venv/bin:/usr/local/bin:/usr/bin:/bin"
Environment="PYTHONPATH=/home/ubuntu/cointicker:/home/ubuntu/cointicker/shared"
ExecStart=/home/ubuntu/cointicker/venv/bin/python /home/ubuntu/cointicker/scripts/run_pipeline_scheduler.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**주요 설정 설명:**

- `Restart=always`: 프로세스 종료 시 자동 재시작
- `RestartSec=10`: 재시작 대기 시간 (10초)
- `StandardOutput=journal`: 로그를 systemd journal에 기록
- `WantedBy=multi-user.target`: 부팅 시 자동 시작 대상

---

## 충돌 방지 시스템

### 충돌 발생 시나리오

GUI 수동 제어와 systemd 서비스가 동시에 실행되면 다음 문제가 발생할 수 있습니다:

1. **포트 충돌**: 같은 포트를 두 프로세스가 사용
2. **리소스 중복**: CPU/메모리 낭비
3. **데이터 불일치**: 같은 작업을 두 번 실행

### SystemdManager 모듈

**위치**: `gui/modules/systemd_manager.py`

**주요 기능:**

```python
from gui.modules.systemd_manager import SystemdManager

# 서비스 실행 여부 확인
is_running = SystemdManager.is_service_running("tier1_orchestrator")

# 부팅 시 자동 시작 활성화 여부 확인
is_enabled = SystemdManager.is_service_enabled("tier2_scheduler")

# 전체 상태 확인
status = SystemdManager.get_service_status("tier1_orchestrator")
# {"running": True, "enabled": True, "exists": True}

# GUI 제어와 충돌 확인
conflict_msg = SystemdManager.check_conflict_with_gui("tier1_orchestrator")
if conflict_msg:
    print(conflict_msg)  # 경고 메시지
```

### 충돌 방지 로직

#### GUI에서 프로세스 시작 시

```python
# app.py의 start_process 메서드에서 (예시)
def start_process(self, process_name):
    # systemd 서비스와 충돌 확인
    if process_name in ["orchestrator", "tier2_scheduler"]:
        service_name = "tier1_orchestrator" if process_name == "orchestrator" else "tier2_scheduler"
        conflict = SystemdManager.check_conflict_with_gui(service_name)

        if conflict:
            # 경고 메시지 표시
            QMessageBox.warning(self, "경고", conflict)
            return

    # 충돌 없으면 프로세스 시작
    self.pipeline_orchestrator.start_process(process_name)
```

#### 경고 메시지 예시

**systemd 서비스가 실행 중인 경우:**

```
tier1_orchestrator systemd 서비스가 이미 실행 중입니다.

GUI에서 수동으로 제어하려면 먼저 systemd 서비스를 중지하세요:
sudo systemctl stop cointicker-orchestrator

또는 Config 탭에서 서비스를 중지할 수 있습니다.
```

**부팅 시 자동 시작이 활성화된 경우:**

```
tier1_orchestrator systemd 서비스가 부팅 시 자동 시작으로 설정되어 있습니다.

GUI에서 수동 제어 시 시스템 재부팅 후 서비스가 자동으로 시작될 수 있습니다.
systemd 자동 시작을 비활성화하려면:
sudo systemctl disable cointicker-orchestrator
```

### 충돌 해결 방법

#### 옵션 1: systemd 서비스 중지

```bash
# Tier 1
sudo systemctl stop cointicker-orchestrator
sudo systemctl disable cointicker-orchestrator

# Tier 2
sudo systemctl stop cointicker-tier2-scheduler
sudo systemctl disable cointicker-tier2-scheduler
```

#### 옵션 2: GUI에서 중지

1. **Config 탭 → Systemd 서비스 설정**
2. **"서비스 중지" 버튼 클릭**
3. **"부팅 시 자동 시작" 체크 해제**
4. **"GUI 설정 저장"**

#### 옵션 3: GUI 자동 시작 비활성화

GUI를 사용하지 않고 systemd만 사용하려면:

```yaml
# config/gui_config.yaml
auto_start:
  enabled: false # GUI 자동 시작 비활성화
```

---

## 설정 파일 구조

### gui_config.yaml 전체 구조

```yaml
gui:
  # 윈도우 설정
  window:
    width: 1400
    height: 900
    theme: default

  # 새로고침 설정
  refresh:
    auto_refresh: false
    interval: 30

  # Tier2 서버 설정
  tier2:
    base_url: http://localhost:5000
    timeout: 5

  # 클러스터 연결 설정
  cluster:
    ssh_timeout: 10
    retry_count: 3

  # GUI 자동 시작 설정
  auto_start:
    enabled: true # GUI 시작 시 자동 시작 활성화
    processes: # 자동 시작할 프로세스 목록
      - backend
      - frontend

  # Systemd 서비스 설정
  systemd:
    enabled: false # systemd 사용 여부
    services:
      tier1_orchestrator:
        enabled: false # Tier 1 서비스 활성화
        auto_start_on_boot: false # 부팅 시 자동 시작
      tier2_scheduler:
        enabled: false # Tier 2 서비스 활성화
        auto_start_on_boot: false # 부팅 시 자동 시작

  # 타이밍 설정
  timing:
    auto_start_delay: 1000 # 자동 시작 지연 시간 (ms)
    process_status_update_delay: 2000
    initial_refresh_delay: 5000
    stats_update_interval: 2000
    tier2_reconnect_delay: 3000
    tier2_refresh_delay: 5000
    dialog_wait_delay: 0.2
    config_refresh_delay: 500
    user_confirm_timeout: 30

  # 재시도 설정
  retry:
    default_max_retries: 3
    default_delay: 1.0
    backoff_factor: 1.5
```

### 설정 파일 위치

```
PICU/
├── cointicker/
│   └── config/
│       ├── gui_config.yaml           # GUI 설정 (자동 생성)
│       ├── cluster_config.yaml       # 클러스터 설정
│       ├── database_config.yaml      # 데이터베이스 설정
│       └── spider_config.yaml        # Spider 설정
└── deployment/
    ├── create_orchestrator_service.sh      # Tier 1 서비스 설치
    └── create_tier2_scheduler_service.sh   # Tier 2 서비스 설치
```

---

## 사용 예시

### 시나리오 1: 개발 환경 (GUI 사용)

**목표**: GUI에서 수동으로 제어하며 개발

**설정:**

```yaml
# gui_config.yaml
auto_start:
  enabled: true
  processes:
    - backend
    - frontend
    # Spider는 필요할 때만 수동으로 시작

systemd:
  enabled: false # systemd 사용 안 함
```

**워크플로우:**

1. GUI 실행 → Backend + Frontend 자동 시작
2. 필요 시 Control 탭에서 Spider 수동 시작
3. 개발 완료 후 GUI 종료 → 모든 프로세스 자동 종료

### 시나리오 2: 프로덕션 환경 (systemd 사용)

**목표**: 서버 부팅 시 자동으로 모든 서비스 시작, GUI 없이 운영

**설정:**

**1. Tier 1 (라즈베리파이 클러스터)**

```bash
# Master 노드에서
ssh ubuntu@raspberry-master
cd /home/ubuntu/cointicker/deployment
bash create_orchestrator_service.sh

# 부팅 시 자동 시작 활성화
sudo systemctl enable cointicker-orchestrator
```

**2. Tier 2 (외부 서버)**

```bash
# 외부 서버에서
ssh ubuntu@tier2-server
cd /home/ubuntu/cointicker/deployment
bash create_tier2_scheduler_service.sh

# 부팅 시 자동 시작 활성화
sudo systemctl enable cointicker-tier2-scheduler
```

**3. GUI 설정 (모니터링용)**

```yaml
# gui_config.yaml
auto_start:
  enabled: false # GUI 자동 시작 비활성화 (systemd가 담당)

systemd:
  enabled: true
  services:
    tier1_orchestrator:
      enabled: true
      auto_start_on_boot: true
    tier2_scheduler:
      enabled: true
      auto_start_on_boot: true
```

**워크플로우:**

1. 서버 부팅 → systemd가 자동으로 모든 서비스 시작
2. 필요 시 GUI 실행 (모니터링만)
3. GUI 종료해도 서비스는 계속 실행

### 시나리오 3: 하이브리드 (GUI + systemd 혼용)

**목표**: Tier 2는 systemd로 자동화, GUI는 모니터링 및 Tier 1 수동 제어

**설정:**

```yaml
# gui_config.yaml
auto_start:
  enabled: true
  processes:
    - backend
    - frontend
    # Tier 1 프로세스는 GUI에서 수동 제어

systemd:
  enabled: true
  services:
    tier1_orchestrator:
      enabled: false # Tier 1은 GUI에서 제어
      auto_start_on_boot: false
    tier2_scheduler:
      enabled: true # Tier 2는 systemd로 자동화
      auto_start_on_boot: true
```

**Tier 2 서비스 설치:**

```bash
bash create_tier2_scheduler_service.sh
sudo systemctl enable cointicker-tier2-scheduler
```

**워크플로우:**

1. Tier 2 서버 부팅 → 파이프라인 스케줄러 자동 시작
2. GUI 실행 → Backend + Frontend 자동 시작
3. 필요 시 Control 탭에서 Tier 1 작업 수동 실행
4. GUI 종료해도 Tier 2는 백그라운드에서 계속 실행

---

## 문제 해결

### 1. GUI 자동 시작이 작동하지 않음

**증상**: GUI 실행해도 프로세스가 자동으로 시작되지 않음

**해결 방법:**

1. **설정 파일 확인**

   ```bash
   cat config/gui_config.yaml
   ```

   `auto_start.enabled`가 `true`인지 확인

2. **로그 확인**

   ```bash
   # GUI 로그 확인
   tail -f logs/gui.log
   ```

   자동 시작 관련 오류 메시지 확인

3. **Config 탭에서 재설정**

   - Config 탭 → 자동 시작 설정 확인
   - 원하는 프로세스 체크
   - "GUI 설정 저장" 클릭

4. **GUI 재시작**
   ```bash
   python gui/main.py
   ```

### 2. Systemd 서비스 설치 실패

**증상**: `create_*_service.sh` 실행 시 권한 오류

**해결 방법:**

1. **sudo 권한 확인**

   ```bash
   sudo -v
   ```

2. **스크립트 실행 권한 확인**

   ```bash
   chmod +x deployment/create_orchestrator_service.sh
   chmod +x deployment/create_tier2_scheduler_service.sh
   ```

3. **수동으로 서비스 파일 생성**

   ```bash
   sudo nano /etc/systemd/system/cointicker-orchestrator.service
   # 위의 "Systemd 서비스 파일 구조" 참고하여 내용 입력

   sudo systemctl daemon-reload
   sudo systemctl enable cointicker-orchestrator
   ```

### 3. Systemd 서비스가 시작되지 않음

**증상**: `systemctl start` 실행해도 서비스가 시작되지 않음

**해결 방법:**

1. **상태 확인**

   ```bash
   sudo systemctl status cointicker-orchestrator
   ```

2. **로그 확인**

   ```bash
   sudo journalctl -u cointicker-orchestrator -n 50
   ```

3. **일반적인 원인**

   **a. Python 가상환경 경로 오류**

   ```bash
   # 가상환경 존재 확인
   ls /home/ubuntu/cointicker/venv/bin/python

   # 없으면 생성
   python3 -m venv /home/ubuntu/cointicker/venv
   pip install -r requirements.txt
   ```

   **b. 프로젝트 경로 오류**

   ```bash
   # 프로젝트 경로 확인
   ls /home/ubuntu/cointicker/master-node/orchestrator.py
   ls /home/ubuntu/cointicker/scripts/run_pipeline_scheduler.py
   ```

   **c. 권한 문제**

   ```bash
   # 소유권 확인
   sudo chown -R ubuntu:ubuntu /home/ubuntu/cointicker
   ```

4. **서비스 파일 수정**

   ```bash
   sudo nano /etc/systemd/system/cointicker-orchestrator.service
   # WorkingDirectory와 ExecStart 경로 확인

   sudo systemctl daemon-reload
   sudo systemctl restart cointicker-orchestrator
   ```

### 4. GUI와 Systemd 충돌

**증상**:

- "서비스가 이미 실행 중입니다" 경고
- 포트 충돌 오류
- 프로세스 중복 실행

**해결 방법:**

**옵션 A: GUI만 사용**

```bash
# systemd 서비스 중지
sudo systemctl stop cointicker-orchestrator
sudo systemctl disable cointicker-orchestrator

# GUI에서 수동 제어
```

**옵션 B: Systemd만 사용**

```yaml
# gui_config.yaml 수정
auto_start:
  enabled: false
```

**옵션 C: 역할 분리**

- Tier 1 오케스트레이터 → systemd
- GUI → 모니터링 + Tier 2 제어

```yaml
auto_start:
  enabled: true
  processes:
    - backend
    - frontend
    # orchestrator는 systemd가 담당
```

### 5. 원격 서버 설치 실패

**증상**: `TIER2_HOST` 설정 후 설치 스크립트가 원격 서버에 연결되지 않음

**해결 방법:**

1. **SSH 연결 확인**

   ```bash
   ssh ubuntu@192.168.1.100
   ```

2. **SSH 키 인증 설정**

   ```bash
   # 로컬에서
   ssh-copy-id ubuntu@192.168.1.100
   ```

3. **환경 변수 확인**

   ```bash
   echo $TIER2_USER   # ubuntu
   echo $TIER2_HOST   # 192.168.1.100
   echo $PROJECT_DIR  # /home/ubuntu/cointicker
   ```

4. **수동 설치**

   ```bash
   # 원격 서버에 직접 접속
   ssh ubuntu@192.168.1.100

   # 스크립트 복사 후 실행
   cd /home/ubuntu/cointicker/deployment
   bash create_tier2_scheduler_service.sh
   ```

### 6. 설정이 저장되지 않음

**증상**: Config 탭에서 설정 변경 후 저장했지만 GUI 재시작 시 원래대로 돌아감

**해결 방법:**

1. **설정 파일 권한 확인**

   ```bash
   ls -l config/gui_config.yaml
   # 쓰기 권한이 있는지 확인

   chmod 644 config/gui_config.yaml
   ```

2. **설정 파일 백업**

   ```bash
   cp config/gui_config.yaml config/gui_config.yaml.backup
   ```

3. **수동으로 설정 파일 편집**

   ```bash
   nano config/gui_config.yaml
   ```

4. **GUI 재시작**
   ```bash
   python gui/main.py
   ```

### 7. 로그 확인 방법

**GUI 로그:**

```bash
tail -f logs/gui.log
```

**Systemd 서비스 로그:**

```bash
# 전체 로그
sudo journalctl -u cointicker-orchestrator

# 최근 50줄
sudo journalctl -u cointicker-orchestrator -n 50

# 실시간 로그
sudo journalctl -u cointicker-orchestrator -f

# 특정 시간 이후 로그
sudo journalctl -u cointicker-orchestrator --since "1 hour ago"
```

---

## 추가 자료

### 관련 문서

- [배포 가이드](DEPLOYMENT_GUIDE.md)
- [GUI 가이드](GUI_GUIDE.md)
- [클러스터 설정 체크리스트](../analysis/CLUSTER_SETUP_CHECKLIST.md)

### 참고 파일

- `gui/app.py` - GUI 자동 시작 로직 (line 881-935)
- `gui/core/config_manager.py` - 설정 관리 (line 228-266)
- `gui/ui/config_tab.py` - Config 탭 UI (line 157-287)
- `gui/modules/systemd_manager.py` - Systemd 충돌 방지
- `deployment/create_orchestrator_service.sh` - Tier 1 서비스 설치
- `deployment/create_tier2_scheduler_service.sh` - Tier 2 서비스 설치

### 도움이 필요하신가요?

문제가 해결되지 않으면:

1. 로그 파일 확인
2. GitHub Issues에 문의
3. 관련 문서 참고

---

**문서 작성**: Juns mcp
**최종 업데이트**: 2025-12-02
