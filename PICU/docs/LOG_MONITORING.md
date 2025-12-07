# 24/7 서비스 로그 모니터링 가이드

GUI를 종료한 후에도 터미널에서 실시간으로 서비스 로그를 모니터링할 수 있습니다.

## 빠른 시작

### 방법 1: 모니터링 스크립트 사용 (권장)

```bash
cd PICU
bash scripts/monitor_logs.sh
```

또는 `start.sh`에서 옵션 9 선택:

```bash
bash scripts/start.sh
# 옵션 9 선택
```

### 방법 2: 직접 tail 명령어 사용

```bash
# Orchestrator 로그
tail -f PICU/cointicker/logs/orchestrator.log

# Scrapyd Scheduler 로그
tail -f PICU/cointicker/logs/scheduler.log

# 모든 로그 동시 모니터링
tail -f PICU/cointicker/logs/*.log
```

## 로그 파일 위치

### 주요 로그 파일

| 서비스              | 로그 파일 경로                                             | 설명                                                |
| ------------------- | ---------------------------------------------------------- | --------------------------------------------------- |
| Orchestrator        | `PICU/cointicker/logs/orchestrator.log`                    | 파이프라인 전체 로그 (크롤링 → MapReduce → DB 적재) |
| Scrapyd Scheduler   | `PICU/cointicker/logs/scheduler.log`                       | 크롤링 작업 스케줄링 로그                           |
| Scrapyd 서버        | `PICU/cointicker/logs/com.cointicker.scrapyd.out.log`      | Scrapyd 서버 로그 (launchctl)                       |
| Orchestrator 서비스 | `PICU/cointicker/logs/com.cointicker.orchestrator.out.log` | Orchestrator 서비스 로그 (launchctl)                |

### 로그 파일 확인

```bash
# 로그 디렉토리 확인
ls -lh PICU/cointicker/logs/

# 최근 로그 확인 (마지막 50줄)
tail -50 PICU/cointicker/logs/orchestrator.log
tail -50 PICU/cointicker/logs/scheduler.log
```

## 실시간 모니터링 명령어

### 단일 로그 모니터링

```bash
# Orchestrator만 모니터링
tail -f PICU/cointicker/logs/orchestrator.log

# Scheduler만 모니터링
tail -f PICU/cointicker/logs/scheduler.log
```

### 여러 로그 동시 모니터링

```bash
# 모든 로그 파일 동시 모니터링
tail -f PICU/cointicker/logs/*.log

# 특정 로그만 선택
tail -f PICU/cointicker/logs/orchestrator.log \
        PICU/cointicker/logs/scheduler.log
```

### 로그 필터링

```bash
# ERROR만 필터링
tail -f PICU/cointicker/logs/orchestrator.log | grep ERROR

# 특정 Spider만 필터링
tail -f PICU/cointicker/logs/scheduler.log | grep "upbit_trends"

# 시간대별 필터링
tail -f PICU/cointicker/logs/orchestrator.log | grep "2025-12-08 07:"
```

## 모니터링 스크립트 옵션

`monitor_logs.sh` 스크립트는 다음 옵션을 제공합니다:

1. **Orchestrator 로그** - 파이프라인 전체 로그
2. **Scrapyd Scheduler 로그** - 크롤링 스케줄링 로그
3. **Scrapyd 서버 로그** - Scrapyd 서버 실행 로그
4. **Orchestrator 서비스 로그** - launchctl 서비스 로그
5. **모든 로그 동시 모니터링** - 모든 로그를 한 화면에 표시
6. **로그 파일 위치 확인** - 로그 파일 경로 및 존재 여부 확인

## 로그 레벨 및 형식

모든 로그는 다음 형식을 따릅니다:

```
YYYY-MM-DD HH:MM:SS - 모듈명 - 레벨 - 메시지
```

예시:

```
2025-12-08 07:33:52 - __main__ - INFO - ✅ 프로젝트 'cointicker' 배포 완료
2025-12-08 07:33:52 - __main__ - INFO - 📋 스케줄링 대상 Spider (5개):
```

## 문제 해결

### 로그 파일이 없을 때

```bash
# 로그 디렉토리 생성
mkdir -p PICU/cointicker/logs

# 서비스 상태 확인
launchctl list | grep cointicker
ps aux | grep -E "(orchestrator|scheduler)"
```

### 로그가 업데이트되지 않을 때

1. 서비스가 실행 중인지 확인:

   ```bash
   launchctl list | grep cointicker
   ```

2. 서비스를 재시작:

   ```bash
   # Config 탭에서 서비스 재시작
   # 또는
   launchctl unload ~/Library/LaunchAgents/com.cointicker.orchestrator.plist
   launchctl load ~/Library/LaunchAgents/com.cointicker.orchestrator.plist
   ```

3. 로그 파일 권한 확인:
   ```bash
   ls -l PICU/cointicker/logs/
   ```

## 고급 사용법

### 로그를 파일로 저장하면서 모니터링

```bash
tail -f PICU/cointicker/logs/orchestrator.log | tee monitor.log
```

### 특정 시간 이후 로그만 확인

```bash
# 07:00 이후 로그만
tail -f PICU/cointicker/logs/orchestrator.log | grep "2025-12-08 07:"
```

### 로그 통계 확인

```bash
# ERROR 개수 확인
grep -c ERROR PICU/cointicker/logs/orchestrator.log

# 최근 1시간 로그 라인 수
tail -n 1000 PICU/cointicker/logs/orchestrator.log | wc -l
```

## 참고

- 로그 파일은 자동으로 회전되지 않으므로, 주기적으로 정리하는 것을 권장합니다.
- 로그 파일 크기가 너무 커지면 디스크 공간을 확인하세요.
- GUI를 종료해도 launchctl 서비스는 계속 실행되므로 로그가 계속 업데이트됩니다.
