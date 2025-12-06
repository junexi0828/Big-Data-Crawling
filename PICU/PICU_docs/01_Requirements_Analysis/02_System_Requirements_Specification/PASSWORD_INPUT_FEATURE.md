# GUI 비밀번호 입력 기능

**작성 일시**: 2025-12-02
**목적**: HDFS 시작 시 sudo 비밀번호를 GUI에서 안전하게 입력받는 기능

---

## 🔐 기능 개요

HDFS 시작 시 관리자 권한이 필요한 경우, GUI에서 비밀번호 입력 다이얼로그를 표시하여 사용자로부터 비밀번호를 입력받습니다.

---

## ✅ 보안 고려사항

### 비밀번호 저장 및 처리

1. **메모리에만 저장**

   - 비밀번호는 서버나 파일에 저장되지 않음
   - 메모리에만 임시로 저장됨

2. **즉시 삭제**

   - 사용 후 즉시 메모리에서 삭제됨
   - `del password` 명령으로 명시적 삭제

3. **서버 저장 없음**

   - 설정 파일에 저장되지 않음
   - 데이터베이스에 저장되지 않음
   - 로그에 기록되지 않음

4. **취소 가능**
   - 사용자가 취소하면 `None` 반환
   - HDFS 시작이 중단됨

---

## 🎯 구현 세부사항

### 1. GUI 비밀번호 입력 다이얼로그

**파일**: `PICU/cointicker/gui/app.py`

```python
def user_password_callback(title: str, message: str) -> Optional[str]:
    """
    사용자 비밀번호 입력 다이얼로그 표시

    보안 고려사항:
    - 비밀번호는 메모리에만 저장됨
    - 사용 후 즉시 삭제됨
    - 서버나 파일에 저장되지 않음
    """
    # QInputDialog.getText() 사용
    # QLineEdit.Password로 마스킹
```

### 2. HDFSManager 연동

**파일**: `PICU/cointicker/gui/modules/managers/hdfs_manager.py`

- `user_password_callback` 파라미터 추가
- HDFS 시작 시 비밀번호 필요 시 콜백 호출
- 비밀번호를 stdin으로 전달 후 즉시 삭제

### 3. PipelineOrchestrator 연동

**파일**: `PICU/cointicker/gui/modules/pipeline_orchestrator.py`

- `user_password_callback` 파라미터 추가
- HDFSManager에 콜백 전달

---

## 📋 사용 흐름

1. **HDFS 시작 요청**

   - 사용자가 GUI에서 HDFS 시작 버튼 클릭

2. **비밀번호 필요 확인**

   - HDFSManager가 sudo 권한 필요 여부 확인

3. **비밀번호 입력 다이얼로그 표시**

   - GUI에서 비밀번호 입력 다이얼로그 표시
   - 사용자가 비밀번호 입력 (마스킹됨)

4. **비밀번호 전달**

   - 비밀번호를 stdin으로 전달
   - 즉시 메모리에서 삭제

5. **HDFS 시작**
   - 비밀번호가 정상적으로 전달되면 HDFS 시작

---

## ⚠️ 주의사항

1. **타임아웃**

   - 기본 타임아웃: 60초
   - 타임아웃 시 취소로 처리

2. **취소 처리**

   - 사용자가 취소하면 HDFS 시작이 중단됨
   - 에러 메시지 표시

3. **보안**
   - 비밀번호는 절대 로그에 기록되지 않음
   - 파일이나 데이터베이스에 저장되지 않음
   - 메모리에만 임시 저장

---

## 🔧 설정

**타임아웃 설정**:

```python
# gui_config.yaml
gui:
  user_password_timeout: 60  # 초 단위
```

---

## ✅ 테스트

1. **정상 동작 테스트**

   - GUI에서 HDFS 시작
   - 비밀번호 입력 다이얼로그 표시 확인
   - 비밀번호 입력 후 HDFS 시작 확인

2. **취소 테스트**

   - 비밀번호 입력 다이얼로그에서 취소
   - HDFS 시작이 중단되는지 확인

3. **타임아웃 테스트**
   - 60초 동안 입력하지 않음
   - 자동 취소되는지 확인

---

**작성자**: Juns Claude Code
**최종 업데이트**: 2025-12-02
