# 단일 노드 모드 문제 해결 가이드

**작성 일시**: 2025-12-02
**목적**: 단일 노드 모드에서 발생하는 문제 진단 및 해결

---

## 🔍 발견된 문제

### 1. Spider 실행 실패 ❌

**증상**:
- 모든 Spider가 시작 후 즉시 종료됨
- 로그: "Spider {name} 시작 실패 (프로세스 종료)"

**원인**:
- `spider_module.py`에서 `scrapy crawl` 명령 실행 시 venv를 활성화하지 않음
- 시스템 Python을 사용하여 scrapy 모듈을 찾을 수 없음

**해결 방법**:
- Spider 실행 시 venv의 Python을 사용하도록 수정 필요

---

### 2. HDFS 시작 시 Password 프롬프트 ⚠️

**증상**:
- HDFS 시작 시 "Password:" 프롬프트가 나타남
- 단일 노드 모드로 전환했지만 여전히 문제 발생

**원인**:
- HDFS 데몬 시작 시 sudo 권한이 필요할 수 있음
- 또는 SSH 연결 시도 중 비밀번호 요청

**해결 방법**:
- sudo 없이 실행 가능하도록 권한 설정
- 또는 sudo 비밀번호 없이 실행 가능하도록 설정

---

### 3. Backend 포트 충돌 ⚠️

**증상**:
- "Address already in use" 오류
- 포트 5000이 이미 사용 중

**원인**:
- 이전에 실행된 백엔드 프로세스가 종료되지 않음

**해결 방법**:
- 기존 프로세스 종료 후 재시작

---

## ✅ 해결 방법

### Spider 문제 해결

**수정 필요 파일**: `PICU/cointicker/gui/modules/spider_module.py`

**현재 코드** (라인 164):
```python
cmd = f"cd {cointicker_abs} && scrapy crawl {spider_name}"
```

**수정 후**:
```python
# venv Python 경로 찾기
project_root = Path(__file__).parent.parent.parent.parent
venv_python = project_root / "venv" / "bin" / "python"
if venv_python.exists():
    cmd = f"cd {cointicker_abs} && {venv_python} -m scrapy crawl {spider_name}"
else:
    # venv가 없으면 시스템 scrapy 사용 (fallback)
    cmd = f"cd {cointicker_abs} && scrapy crawl {spider_name}"
```

---

### HDFS 문제 해결

**옵션 1: sudo 없이 실행 가능하도록 설정** (권장)

```bash
# Hadoop 디렉토리 권한 확인
ls -la /opt/hadoop
# 필요시 권한 변경
sudo chown -R $USER:$USER /opt/hadoop
```

**옵션 2: sudo 비밀번호 없이 실행**

```bash
# sudoers 파일에 추가 (주의: 보안 위험)
echo "$USER ALL=(ALL) NOPASSWD: /opt/hadoop/bin/hdfs" | sudo tee /etc/sudoers.d/hadoop
```

---

### Backend 포트 충돌 해결

```bash
# 기존 백엔드 프로세스 종료
pkill -f "uvicorn app:app"
# 또는 특정 포트 사용 프로세스 종료
lsof -ti:5000 | xargs kill -9
lsof -ti:5001 | xargs kill -9
```

---

## 📝 단일 노드 모드 동작 확인

**단일 노드 모드에서도 정상 동작해야 합니다.**

- ✅ Spider는 로컬에서 실행 가능해야 함
- ✅ HDFS는 단일 노드 모드로 실행 가능해야 함
- ✅ Backend/Frontend는 로컬에서 실행 가능해야 함

**클러스터 연결은 선택 사항입니다.**

---

**작성자**: Claude Code
**최종 업데이트**: 2025-12-02

