# PICU 클러스터 구성 점검 보고서

**작성 일시**: 2025-12-01
**목적**: 클러스터 연결 전 전체 구성 점검 및 미구현/누락 사항 확인

---

## 📋 점검 항목 요약

| 항목                     | 상태         | 우선순위 | 비고                       |
| ------------------------ | ------------ | -------- | -------------------------- |
| IP 주소 일관성           | ⚠️ 주의 필요 | 높음     | 설정 파일 간 불일치        |
| 배포 스크립트            | ✅ 완료      | -        | 모든 노드 배포 가능        |
| 오케스트레이터 자동 시작 | ❌ 미구현    | 높음     | systemd 서비스 필요        |
| Tier 2 파이프라인 자동화 | ❌ 미구현    | 높음     | 스케줄러 필요              |
| Scrapyd 설정             | ❌ 미구현    | 중간     | 배포 스크립트에 없음       |
| HDFS 클라이언트 설정     | ⚠️ 개선 필요 | 중간     | cluster_config.yaml 미사용 |
| 데이터베이스 초기화      | ✅ 완료      | -        | init_db.py 존재            |
| GUI 통합 관리            | ✅ 완료      | -        | 모든 모듈 통합됨           |

---

## 🔍 상세 점검 결과

### 1. IP 주소 일관성 문제 ⚠️

**문제점**:

- `cluster_config.yaml.example`: `192.168.1.100-103` 사용
- 실제 `cluster_config.yaml`: `192.168.0.100-103` 사용
- 대부분의 배포 스크립트: `192.168.0.100-103` 사용

**영향**:

- 설정 파일과 실제 네트워크 환경이 다를 수 있음
- 문서와 실제 설정 간 혼란 가능

**권장 조치**:

1. `cluster_config.yaml.example`을 실제 사용하는 IP 대역(`192.168.0.x`)으로 수정
2. 또는 모든 문서와 스크립트를 `192.168.1.x`로 통일

**위치**:

- `PICU/cointicker/config/cluster_config.yaml.example` (라인 10, 17, 21, 25)

---

### 2. 오케스트레이터 자동 시작 미구현 ❌

**현재 상태**:

- `master-node/orchestrator.py`는 구현되어 있음
- 배포 스크립트에서 systemd 서비스 설정이 주석 처리됨
- 수동 실행만 가능

**문제점**:

- 라즈베리파이 재부팅 시 오케스트레이터가 자동으로 시작되지 않음
- 크롤링 작업이 자동으로 실행되지 않음

**필요한 작업**:

1. systemd 서비스 파일 생성 (`/etc/systemd/system/cointicker-orchestrator.service`)
2. 배포 스크립트에서 서비스 활성화
3. Scrapyd 서비스도 함께 설정 (scheduler.py 사용 시)

**참고 위치**:

- `PICU/deployment/setup_master.sh` (라인 213-215, 주석 처리됨)
- `PICU/cointicker/master-node/orchestrator.py`

**예시 systemd 서비스 파일**:

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

[Install]
WantedBy=multi-user.target
```

---

### 3. Tier 2 파이프라인 자동화 미구현 ❌

**현재 상태**:

- `scripts/run_pipeline.py`는 구현되어 있음
- HDFS에서 데이터를 가져와 DB에 적재하는 로직 존재
- 자동 실행 스케줄러가 없음

**문제점**:

- Tier 1에서 HDFS에 저장된 데이터가 Tier 2 DB로 자동 전송되지 않음
- 수동으로만 `run_pipeline.py` 실행 가능

**필요한 작업**:

1. Tier 2 서버에서 주기적으로 실행하는 스케줄러 구현
   - cron job 또는 systemd timer
   - 또는 Python 스케줄러 (schedule 라이브러리 사용)
2. 실행 주기 결정 (예: 30분마다 또는 1시간마다)

**참고 위치**:

- `PICU/cointicker/scripts/run_pipeline.py`
- `PICU/cointicker/backend/services/data_loader.py`

**권장 구현**:

```python
# scripts/run_pipeline_scheduler.py (새로 생성)
import schedule
import time
from scripts.run_pipeline import run_full_pipeline

# 30분마다 실행
schedule.every(30).minutes.do(run_full_pipeline)

while True:
    schedule.run_pending()
    time.sleep(60)
```

---

### 4. Scrapyd 설정 미구현 ❌

**현재 상태**:

- `master-node/scheduler.py`는 Scrapyd를 사용하도록 구현됨
- `requirements-master.txt`에 `scrapyd>=1.3.0` 포함됨
- 배포 스크립트에서 Scrapyd 설치/설정이 없음

**문제점**:

- Scrapyd 서버가 설치/실행되지 않으면 scheduler.py가 동작하지 않음
- Scrapyd 설정 파일(`scrapyd.conf`)이 없음

**필요한 작업**:

1. Scrapyd 설치 확인 (requirements-master.txt에 포함되어 있음)
2. Scrapyd 설정 파일 생성 (`~/.scrapyd/scrapyd.conf`)
3. Scrapyd 서비스 자동 시작 설정 (systemd)
4. 배포 스크립트에 Scrapyd 설정 추가

**참고 위치**:

- `PICU/cointicker/master-node/scheduler.py`
- `PICU/requirements/requirements-master.txt` (라인 6)

**예시 Scrapyd 설정**:

```ini
# ~/.scrapyd/scrapyd.conf
[scrapyd]
bind_address = 0.0.0.0
http_port = 6800
eggs_dir = eggs
logs_dir = logs
items_dir = items
jobs_to_keep = 5
dbs_dir = dbs
max_proc = 0
max_proc_per_cpu = 4
finished_to_keep = 100
poll_interval = 5.0
```

---

### 5. HDFS 클라이언트 설정 개선 필요 ⚠️

**현재 상태**:

- `shared/hdfs_client.py`는 기본값으로 `localhost:9000` 사용
- `cluster_config.yaml`의 설정을 읽어오지 않음

**문제점**:

- Tier 2에서 HDFS에 접속할 때 cluster_config.yaml의 설정을 사용하지 않음
- 하드코딩된 namenode 주소 사용

**개선 방안**:

1. HDFSClient 초기화 시 cluster_config.yaml 읽기
2. 또는 환경 변수로 namenode 주소 설정

**참고 위치**:

- `PICU/cointicker/shared/hdfs_client.py` (라인 33)
- `PICU/cointicker/config/cluster_config.yaml` (라인 34)

**개선 예시**:

```python
# shared/hdfs_client.py 수정
def __init__(self, namenode: str = None, use_java: bool = True):
    if namenode is None:
        # cluster_config.yaml에서 읽기
        config_path = get_cointicker_root() / "config" / "cluster_config.yaml"
        if config_path.exists():
            with open(config_path) as f:
                config = yaml.safe_load(f)
                namenode = config.get("hadoop", {}).get("hdfs", {}).get("namenode", "hdfs://localhost:9000")
        else:
            namenode = "hdfs://localhost:9000"
    # ...
```

---

### 6. 배포 스크립트 점검 ✅

**상태**: 완료

**확인 사항**:

- ✅ `setup_all_nodes.sh`: 모든 노드 배포 가능
- ✅ `setup_master.sh`: Master Node 배포 완료
- ✅ `setup_worker.sh`: Worker Node 배포 완료
- ✅ requirements 파일 존재 (`requirements-master.txt`, `requirements-worker.txt`)
- ✅ Hadoop 설정 파일 자동 생성
- ⚠️ systemd 서비스 설정은 주석 처리됨 (위 2번 항목 참고)

---

### 7. 데이터베이스 초기화 ✅

**상태**: 완료

**확인 사항**:

- ✅ `backend/init_db.py` 존재
- ✅ DB 모델 정의 완료 (`backend/models.py`)
- ✅ DataLoader 구현 완료 (`backend/services/data_loader.py`)

---

### 8. GUI 통합 관리 ✅

**상태**: 완료

**확인 사항**:

- ✅ 모든 모듈 통합 관리 가능
- ✅ 클러스터 모니터링 기능
- ✅ Tier 2 서버 관리 기능
- ✅ 파이프라인 제어 기능
- ✅ 설정 중앙 관리

---

## 🎯 우선순위별 조치 사항

### 높은 우선순위 (테스트 전 필수)

1. **IP 주소 일관성 수정**

   - `cluster_config.yaml.example` 수정
   - 또는 실제 네트워크 환경 확인 후 cluster_config.yaml 업데이트

2. **오케스트레이터 자동 시작 설정**

   - systemd 서비스 파일 생성
   - 배포 스크립트에 서비스 활성화 추가

3. **Tier 2 파이프라인 자동화**
   - 스케줄러 스크립트 생성
   - systemd timer 또는 cron job 설정

### 중간 우선순위 (테스트 중 구현)

4. **Scrapyd 설정**

   - Scrapyd 설정 파일 생성
   - Scrapyd 서비스 자동 시작 설정

5. **HDFS 클라이언트 개선**
   - cluster_config.yaml 읽기 기능 추가

---

## 📝 테스트 전 체크리스트

### Tier 1 (라즈베리파이 클러스터)

- [ ] 모든 노드 네트워크 연결 확인
- [ ] SSH 키 복사 완료
- [ ] 배포 스크립트 실행 완료
- [ ] Hadoop NameNode/DataNode 시작 확인
- [ ] YARN ResourceManager/NodeManager 시작 확인
- [ ] 오케스트레이터 수동 실행 테스트
- [ ] Scrapy Spider 수동 실행 테스트
- [ ] HDFS 저장 확인 (`hdfs dfs -ls /raw/`)
- [ ] MapReduce 작업 수동 실행 테스트

### Tier 2 (외부 서버)

- [ ] 데이터베이스 초기화 완료
- [ ] 백엔드 서버 실행 확인
- [ ] 프론트엔드 서버 실행 확인
- [ ] HDFS 클라이언트 연결 테스트
- [ ] Tier 2 파이프라인 수동 실행 테스트
- [ ] GUI 실행 확인

### 통합 테스트

- [ ] Tier 1 → HDFS 데이터 저장 확인
- [ ] Tier 1 → Tier 2 데이터 전송 확인
- [ ] Tier 2 → DB 적재 확인
- [ ] GUI를 통한 클러스터 모니터링 확인
- [ ] GUI를 통한 파이프라인 제어 확인

---

## 🔧 빠른 수정 가이드

### 1. IP 주소 일관성 수정

```bash
# cluster_config.yaml.example 수정
cd PICU/cointicker/config
# 192.168.1.x → 192.168.0.x로 변경
```

### 2. 오케스트레이터 systemd 서비스 생성

```bash
# Master Node에 접속
ssh ubuntu@raspberry-master

# 서비스 파일 생성
sudo nano /etc/systemd/system/cointicker-orchestrator.service
# (위의 예시 내용 복사)

# 서비스 활성화
sudo systemctl daemon-reload
sudo systemctl enable cointicker-orchestrator
sudo systemctl start cointicker-orchestrator
```

### 3. Tier 2 파이프라인 스케줄러 생성

```bash
# scripts/run_pipeline_scheduler.py 생성
# (위의 예시 코드 사용)

# systemd timer 설정 또는 cron job 추가
```

---

## 📚 관련 문서

- [배포 가이드](../guides/DEPLOYMENT_GUIDE.md)
- [GUI 가이드](../guides/GUI_GUIDE.md)
- [프로젝트 구조](../reference/PROJECT_DOCUMENTATION.md)

---

**마지막 업데이트**: 2025-12-01
