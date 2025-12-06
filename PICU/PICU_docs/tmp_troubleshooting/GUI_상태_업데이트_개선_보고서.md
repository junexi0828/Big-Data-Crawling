# GUI 상태 업데이트 개선 보고서

**작성일**: 2025-12-06
**작업 내용**: 프로세스 상태 테이블과 대시보드 상태 업데이트 문제 해결
**상태**: ✅ **완료**

---

## 📋 문제 분석

### 발견된 문제

1. **프로세스 상태 테이블이 업데이트되지 않음**

   - 개별 제어 버튼 클릭 후에도 상태가 변경되지 않음
   - 프로세스 상태 테이블에 "실행 중"으로 표시되어도 대시보드에는 "중지됨"으로 표시됨

2. **대시보드와 프로세스 상태 테이블의 상태 불일치**

   - 프로세스 상태 테이블: `PipelineOrchestrator.get_status()` 사용
   - 대시보드: `ModuleManager` 직접 호출
   - 두 소스가 서로 다른 상태를 반환

3. **`PipelineOrchestrator.get_status()`가 실제 프로세스 상태를 확인하지 않음**
   - 내부 상태(`self.processes`)만 반환
   - 실제 프로세스가 실행 중인지 확인하지 않음

---

## ✅ 해결 방법

### 1. `PipelineOrchestrator.get_status()` 개선

**변경 전**:

```python
def get_status(self) -> Dict:
    """전체 프로세스 상태 조회"""
    status = {}
    for name, info in self.processes.items():
        status[name] = {
            "status": info["status"].value,
            "start_time": info["start_time"],
            "running": info["status"] == ProcessStatus.RUNNING,
        }
    return status
```

**변경 후**:

- 각 프로세스의 **실제 실행 상태를 확인**
- 모듈이 있으면 모듈의 상태 확인
- 모듈이 없으면 프로세스 직접 확인 (포트, 프로세스 poll 등)
- 실제 상태와 내부 상태가 다르면 내부 상태 업데이트

**확인 방법**:

- **Kafka Consumer**: `KafkaModule.execute("get_status")` 사용
- **HDFS**: `HDFSManager.check_running()` 사용
- **Spider**: `SpiderModule.execute("get_spider_status")` 사용
- **Backend/Frontend**: 포트 연결 확인

**효과**:

- 실제 프로세스 상태를 정확히 반영
- 내부 상태와 실제 상태 자동 동기화

---

### 2. `_update_pipeline_monitoring()` 개선

**변경 전**:

- `ModuleManager`를 직접 호출하여 상태 조회
- `PipelineOrchestrator` 상태와 별도로 관리

**변경 후**:

- `PipelineOrchestrator.get_status()`를 우선 사용
- 상세 정보는 `ModuleManager`에서 조회하되, 기본 상태는 `PipelineOrchestrator` 사용

**효과**:

- 프로세스 상태 테이블과 대시보드의 상태 일치
- 단일 소스(`PipelineOrchestrator`)에서 상태 관리

---

## 📊 변경 사항

### 수정된 파일

1. **`PICU/cointicker/gui/modules/pipeline_orchestrator.py`**

   - `get_status()` 메서드 개선
   - 실제 프로세스 상태 확인 로직 추가
   - 내부 상태 자동 동기화

2. **`PICU/cointicker/gui/app.py`**
   - `_update_pipeline_monitoring()` 개선
   - Kafka/HDFS 상태 수집 시 `PipelineOrchestrator` 상태 우선 사용

---

## 🔄 상태 업데이트 흐름

### 이전 흐름

```
개별 제어 버튼 클릭
  ↓
PipelineOrchestrator.start_process() / stop_process()
  ↓
내부 상태만 업데이트 (self.processes)
  ↓
get_status() → 내부 상태만 반환
  ↓
프로세스 상태 테이블: 내부 상태 표시
대시보드: ModuleManager 직접 호출 → 다른 상태 표시
```

### 개선된 흐름

```
개별 제어 버튼 클릭
  ↓
PipelineOrchestrator.start_process() / stop_process()
  ↓
내부 상태 업데이트 (self.processes)
  ↓
get_status() → 실제 프로세스 상태 확인
  ↓
실제 상태와 내부 상태 비교
  ↓
불일치 시 내부 상태 자동 업데이트
  ↓
프로세스 상태 테이블: 실제 상태 표시
대시보드: PipelineOrchestrator 상태 우선 사용 → 동일한 상태 표시
```

---

## ✅ 검증 사항

- [x] `PipelineOrchestrator.get_status()`가 실제 프로세스 상태를 확인함
- [x] Kafka Consumer 상태가 정확히 반영됨
- [x] HDFS 상태가 정확히 반영됨
- [x] 프로세스 상태 테이블과 대시보드 상태가 일치함
- [x] 개별 제어 후 상태가 즉시 업데이트됨
- [x] 주기적 업데이트(3초마다)가 정상 작동함

---

## 🎯 사용 방법

### 상태 확인

1. **프로세스 상태 테이블**:

   - 통합 파이프라인 제어 섹션의 테이블에서 확인
   - 실제 프로세스 상태를 정확히 표시

2. **대시보드**:

   - 대시보드 탭의 파이프라인 모니터링 섹션에서 확인
   - 프로세스 상태 테이블과 동일한 상태 표시

3. **개별 제어 후**:
   - 버튼 클릭 후 약 3초 이내에 상태 업데이트
   - 프로세스 상태 테이블과 대시보드 모두 자동 업데이트

---

## 🔗 관련 파일

- `PICU/cointicker/gui/modules/pipeline_orchestrator.py` - PipelineOrchestrator 상태 조회
- `PICU/cointicker/gui/app.py` - GUI 메인 애플리케이션, 상태 업데이트
- `PICU/cointicker/gui/ui/dashboard_tab.py` - 대시보드 탭
- `PICU/cointicker/gui/ui/control_tab.py` - 제어 탭

---

**보고서 작성자**: Juns AI Assistant
**최종 업데이트**: 2025-12-06
