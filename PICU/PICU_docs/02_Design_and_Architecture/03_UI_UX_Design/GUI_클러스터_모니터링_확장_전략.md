# GUI 클러스터 모니터링 확장 전략

**작성일**: 2025-12-07
**상태**: 📋 계획 단계

---

## 📋 목표

1. **대시보드**: 마스터/워커 노드 구분 모니터링 섹션 추가
2. **클러스터 탭**: 노드별 개별 제어 버튼 구현

---

## 🎯 구현 전략

### 1. 대시보드 - 노드 모니터링 섹션 추가

**위치**: `gui/ui/dashboard_tab.py`

**새 섹션**: "클러스터 노드 모니터링"

**구조**:

```
┌─────────────────────────────────────┐
│ 클러스터 노드 모니터링              │
├─────────────────────────────────────┤
│ 마스터 노드 (1개)                   │
│  ├─ Orchestrator: 실행 중/중지     │
│  └─ Scheduler: 실행 중/중지         │
│                                     │
│ 워커 노드 (4개)                     │
│  ├─ Node 1: 온라인/오프라인        │
│  ├─ Node 2: 온라인/오프라인        │
│  ├─ Node 3: 온라인/오프라인        │
│  └─ Node 4: 온라인/오프라인        │
└─────────────────────────────────────┘
```

**데이터 소스**:

- 마스터 노드: `PipelineModule` 상태 확인
- 워커 노드: `ClusterMonitor` 기존 기능 활용

---

### 2. 클러스터 탭 - 노드별 개별 제어

**위치**: `gui/ui/cluster_tab.py`

**구현 내용**:

- 각 노드별 카드/섹션 생성
- 노드별 시작/중지/재시작 버튼
- 노드별 프로세스 상태 표시

**UI 구조**:

```
┌─────────────────────────────────────┐
│ 마스터 노드                         │
│ [Orchestrator 시작] [중지] [재시작] │
│ [Scheduler 시작] [중지] [재시작]    │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ 워커 노드 1 (hostname/IP)           │
│ 상태: 온라인                        │
│ [전체 시작] [전체 중지] [재시작]     │
│ [Spider 시작] [Kafka 시작] [HDFS 시작] │
└─────────────────────────────────────┘
```

**기능**:

- SSH를 통한 원격 노드 제어
- `PipelineModule.execute()` 활용
- `SSHManager` 기존 기능 활용

---

## 🔧 기술 구현

### 1. 노드 상태 모니터링

**데이터 수집**:

```python
# 마스터 노드
orchestrator_status = pipeline_module.execute("get_orchestrator_status")
scheduler_status = pipeline_module.execute("get_scheduler_status")

# 워커 노드
worker_nodes = cluster_monitor.get_worker_nodes()
for node in worker_nodes:
    node_status = cluster_monitor.check_node_status(node)
```

**업데이트 주기**: 기존 시스템 자원 모니터링과 동일 (5초)

### 2. 노드 제어 기능

**마스터 노드**:

```python
# Orchestrator
pipeline_module.execute("start_orchestrator")
pipeline_module.execute("stop_orchestrator")

# Scheduler
pipeline_module.execute("start_scheduler")
pipeline_module.execute("stop_scheduler")
```

**워커 노드**:

```python
# SSH를 통한 원격 제어
ssh_manager.execute_command(host, "start_spider")
ssh_manager.execute_command(host, "start_kafka_consumer")
ssh_manager.execute_command(host, "start_hdfs")
```

---

## 📊 데이터 흐름

```
Dashboard Tab
  ↓
ClusterMonitor (기존)
  ↓
PipelineModule (마스터 노드)
SSHManager (워커 노드)
  ↓
노드 상태 표시
```

---

## ✅ 구현 단계

### Phase 1: 대시보드 섹션 추가

- [ ] `dashboard_tab.py`에 노드 모니터링 섹션 추가
- [ ] 마스터/워커 노드 상태 표시
- [ ] 기존 모니터링 타이머에 통합

### Phase 2: 클러스터 탭 제어 기능

- [ ] 노드별 카드 UI 생성
- [ ] 마스터 노드 제어 버튼 연결
- [ ] 워커 노드 제어 버튼 연결
- [ ] SSH 원격 제어 구현

### Phase 3: 상태 동기화

- [ ] 노드 상태 실시간 업데이트
- [ ] 제어 후 상태 반영
- [ ] 에러 처리 및 알림

---

## 🔗 관련 모듈

- `gui/ui/dashboard_tab.py`: 대시보드 UI
- `gui/ui/cluster_tab.py`: 클러스터 탭 UI
- `gui/modules/pipeline_module.py`: 마스터 노드 제어
- `gui/modules/managers/ssh_manager.py`: 워커 노드 SSH 제어
- `gui/monitors/cluster_monitor.py`: 클러스터 모니터링

---

## ⚠️ 주의사항

1. **SSH 인증**: 워커 노드 제어 시 SSH 키 인증 필요
2. **권한 관리**: 마스터 노드 제어는 systemd 서비스와 충돌 방지
3. **네트워크 지연**: 원격 노드 제어 시 타임아웃 설정
4. **상태 동기화**: 제어 후 상태 업데이트 지연 고려

---

**작성자**: Juns AI Assistant
**최종 업데이트**: 2025-12-07
