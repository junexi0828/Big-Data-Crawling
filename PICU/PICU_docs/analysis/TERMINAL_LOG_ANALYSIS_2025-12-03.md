# 터미널 로그 분석 보고서

**날짜**: 2025-12-03
**분석 범위**: GUI 실행 로그 (라인 1-1033)

## 📋 요약

터미널 로그 분석 결과, 두 가지 주요 문제가 발견되었습니다:

1. **스파이더 상태 체크 로직 오류**: 종료 코드 0(성공)을 실패로 잘못 판단
2. **백엔드 서버 포트 충돌**: 포트 5000/5001이 이미 사용 중이어서 서버 시작 실패

## 🔍 상세 분석

### 1. 스파이더 문제

#### 문제 현상

```
라인 409: Spider upbit_trends 시작 실패 (프로세스 종료, 종료 코드: 0)
```

#### 원인 분석

- 스파이더는 **일회성 작업**으로 정상적으로 실행되고 종료됨
- 종료 코드 **0은 성공**을 의미하지만, GUI는 이를 **실패**로 판단
- `spider_module.py`의 `check_process_status()` 함수가 프로세스 종료를 무조건 "error"로 처리

#### 해결 방법

✅ **수정 완료**: 종료 코드를 확인하여 0이면 "completed"로, 0이 아니면 "error"로 설정

**수정 내용**:

```python
if returncode == 0:
    # 종료 코드 0 = 정상 종료 (스파이더는 일회성 작업)
    self.spiders[spider_name]["status"] = "completed"
    logger.info(f"Spider {spider_name} 실행 완료 (종료 코드: 0)")
else:
    # 종료 코드가 0이 아니면 실패
    self.spiders[spider_name]["status"] = "error"
    logger.error(f"Spider {spider_name} 실행 실패 (종료 코드: {returncode})")
```

### 2. 백엔드 서버 문제

#### 문제 현상

```
라인 117: ERROR: [Errno 48] Address already in use
라인 153-412: Connection refused 에러 반복 발생
```

#### 원인 분석

1. **포트 5000**: ControlCenter 프로세스가 사용 중 (백엔드 서버 아님)
2. **포트 5001**: 스크립트가 5001로 변경 시도했지만 여전히 충돌 발생
3. **포트 충돌 처리 부족**: 현재 스크립트는 5001만 시도하고, 그것도 실패하면 종료

#### 해결 방법

✅ **수정 완료**: 여러 포트를 순차적으로 시도하도록 개선

**수정 내용**:

- `find_available_port()` 함수 추가: 5001부터 5010까지 순차적으로 사용 가능한 포트 찾기
- 포트 충돌 시 자동으로 다음 포트 시도
- 사용 가능한 포트를 찾지 못하면 명확한 에러 메시지 출력

**수정된 로직**:

```bash
find_available_port() {
    local start_port=$1
    local max_port=$((start_port + 10))
    local port=$start_port

    while [ $port -le $max_port ]; do
        if ! lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            echo $port
            return 0
        fi
        port=$((port + 1))
    done

    return 1
}
```

## 📊 로그 패턴 분석

### 정상 동작

- ✅ 스파이더 시작: 라인 138-152에서 모든 스파이더가 정상적으로 시작됨
- ✅ Kafka Consumer: 라인 73-75에서 정상 시작
- ✅ Frontend: 라인 77-79에서 정상 시작

### 문제 발생

- ❌ 백엔드 서버: 라인 117에서 포트 충돌로 시작 실패
- ❌ 스파이더 상태: 라인 409에서 종료 코드 0을 실패로 잘못 판단
- ❌ 헬스 체크: 라인 153-412에서 백엔드 서버 연결 실패로 반복 에러

## 🔧 수정 사항 요약

### 1. `spider_module.py`

- **위치**: `PICU/cointicker/gui/modules/spider_module.py`
- **변경**: `check_process_status()` 함수에서 종료 코드 확인 로직 추가
- **효과**: 스파이더 정상 종료를 성공으로 올바르게 인식

### 2. `run_server.sh`

- **위치**: `PICU/cointicker/backend/scripts/run_server.sh`
- **변경**: `find_available_port()` 함수 추가 및 포트 충돌 처리 개선
- **효과**: 포트 충돌 시 자동으로 사용 가능한 포트 찾기

## 🎯 다음 단계

1. **테스트 필요**:

   - 스파이더 실행 후 상태가 "completed"로 표시되는지 확인
   - 백엔드 서버가 포트 충돌 시 자동으로 다른 포트를 사용하는지 확인

2. **추가 개선 사항**:
   - 백엔드 서버 시작 실패 시 재시도 로직 추가
   - 포트 충돌 감지 시 기존 프로세스 자동 종료 옵션 추가

## 📝 참고 사항

- 스파이더는 일회성 작업이므로 정상 종료(exit code 0)는 성공으로 처리해야 함
- 백엔드 서버는 포트 충돌 시 여러 포트를 시도하여 안정성 향상
- GUI의 헬스 체크는 백엔드 서버가 정상 시작된 후에만 성공할 수 있음
