# 설치 스크립트 수정 보고서

**수정 일시**: 2025-12-03
**목적**: 통합 설치 마법사의 가상환경 연동 오류 수정

---

## 🔴 문제 상황

### 증상
```
[83%] ✅ Python 의존성 설치 완료
[83%] 설치 확인 중...
[100%] ✅ 설치 확인 완료

❌ 설치 중 오류가 발생했습니다:
  - Python 의존성 설치 실패
```

### 근본 원인

#### 1. **Externally-Managed-Environment 오류**
macOS Homebrew Python은 PEP 668에 따라 시스템 보호를 위해 가상환경 없이 pip 설치를 막습니다:

```
error: externally-managed-environment

× This environment is externally managed
╰─> To install Python packages system-wide, try brew install
    xyz, where xyz is the package you are trying to
    install.

    If you wish to install a Python library that isn't in Homebrew,
    use a virtual environment:

    python3 -m venv path/to/venv
    source path/to/venv/bin/activate
    python3 -m pip install xyz
```

#### 2. **installer.py의 로직 오류**
`cointicker/gui/installer/installer.py`의 `install_python_dependencies()` 메서드가:
- 가상환경을 생성했음에도 불구하고
- **시스템 Python (`sys.executable`)**을 사용하여 pip 설치 시도
- 결과적으로 externally-managed-environment 오류 발생

---

## ✅ 수정 내용

### 1. `install_python_dependencies()` 메서드 수정

**위치**: `cointicker/gui/installer/installer.py:185-260`

#### 변경 전:
```python
def install_python_dependencies(
    self, use_venv: bool = True
) -> Tuple[bool, List[str]]:
    """Python 의존성 설치"""
    logs = []

    try:
        # pip 업그레이드 (시스템 Python 사용)
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
            check=True,
            capture_output=True,
            timeout=300,
        )

        # requirements.txt 설치 (시스템 Python 사용)
        result = subprocess.run(
            [
                sys.executable,  # ❌ 문제: 시스템 Python 사용
                "-m",
                "pip",
                "install",
                "-r",
                str(self.requirements_file),
            ],
            capture_output=True,
            text=True,
            timeout=1800,
        )
```

#### 변경 후:
```python
def install_python_dependencies(
    self, use_venv: bool = True
) -> Tuple[bool, List[str]]:
    """Python 의존성 설치"""
    logs = []

    try:
        # ✅ 가상환경 사용 시 가상환경의 Python 사용
        if use_venv:
            venv_dir = self.project_root / "venv"
            if self.system == "Windows":
                python_executable = venv_dir / "Scripts" / "python.exe"
            else:
                python_executable = venv_dir / "bin" / "python"

            if not python_executable.exists():
                logs.append(f"가상환경 Python을 찾을 수 없습니다: {python_executable}")
                logs.append("가상환경이 제대로 생성되지 않았을 수 있습니다.")
                return False, logs

            pip_executable = str(python_executable)
        else:
            pip_executable = sys.executable

        # pip 업그레이드 (가상환경 Python 사용)
        subprocess.run(
            [pip_executable, "-m", "pip", "install", "--upgrade", "pip"],
            check=True,
            capture_output=True,
            timeout=300,
        )

        # requirements.txt 설치 (가상환경 Python 사용)
        result = subprocess.run(
            [
                pip_executable,  # ✅ 수정: 가상환경 Python 사용
                "-m",
                "pip",
                "install",
                "-r",
                str(self.requirements_file),
            ],
            capture_output=True,
            text=True,
            timeout=1800,
        )
```

---

### 2. `verify_installation()` 메서드 수정

**위치**: `cointicker/gui/installer/installer.py:294-353`

#### 변경 전:
```python
def verify_installation(self) -> Tuple[bool, List[str]]:
    """설치 확인"""
    logs = []

    for package_name, import_name in required_packages.items():
        try:
            result = subprocess.run(
                [sys.executable, "-c", f"import {import_name}; print('OK')"],
                # ❌ 문제: 시스템 Python으로 import 확인
                capture_output=True,
                text=True,
                timeout=10,
            )
```

#### 변경 후:
```python
def verify_installation(self, use_venv: bool = True) -> Tuple[bool, List[str]]:
    """설치 확인"""
    logs = []

    # ✅ 가상환경 사용 시 가상환경의 Python 사용
    if use_venv:
        venv_dir = self.project_root / "venv"
        if self.system == "Windows":
            python_executable = str(venv_dir / "Scripts" / "python.exe")
        else:
            python_executable = str(venv_dir / "bin" / "python")

        if not Path(python_executable).exists():
            logs.append(f"가상환경 Python을 찾을 수 없습니다: {python_executable}")
            logs.append("시스템 Python으로 확인합니다.")
            python_executable = sys.executable
    else:
        python_executable = sys.executable

    for package_name, import_name in required_packages.items():
        try:
            result = subprocess.run(
                [python_executable, "-c", f"import {import_name}; print('OK')"],
                # ✅ 수정: 가상환경 Python으로 import 확인
                capture_output=True,
                text=True,
                timeout=10,
            )
```

---

### 3. `run_full_installation()` 메서드 수정

**위치**: `cointicker/gui/installer/installer.py:440-447`

#### 변경 전:
```python
# 6. 설치 확인
update_progress("설치 확인 중...", 0)
success, logs = self.verify_installation()  # ❌ use_venv 인자 없음
```

#### 변경 후:
```python
# 6. 설치 확인
update_progress("설치 확인 중...", 0)
success, logs = self.verify_installation(use_venv=create_venv)  # ✅ 인자 전달
```

---

## 📋 수정된 파일 목록

### 1. `cointicker/gui/installer/installer.py`
- **수정 라인**: 185-260, 294-353, 440-447
- **수정 내용**:
  - `install_python_dependencies()`: 가상환경 Python 경로 감지 및 사용
  - `verify_installation()`: 가상환경 Python으로 패키지 확인
  - `run_full_installation()`: verify_installation 호출 시 use_venv 인자 전달

---

## 🧪 검증 방법

### 1. 기존 가상환경 삭제 (선택)
```bash
cd /Users/juns/code/personal/notion/pknu_workspace/bigdata/PICU
rm -rf venv
```

### 2. 통합 설치 마법사 실행
```bash
bash scripts/start.sh
# 메뉴에서 "2) 통합 설치 마법사 실행 (재설치)" 선택
```

### 3. 또는 직접 실행
```bash
python3 cointicker/gui/installer/unified_installer.py
```

### 4. 예상 결과
```
[0%] Python 버전 확인 중...
[16%] ✅ Python 버전 확인 완료
[16%] pip 확인 중...
[33%] ✅ pip 확인 완료
[33%] 가상환경 생성 중...
[50%] ✅ 가상환경 생성 완료
[50%] 시스템 의존성 설치 중...
[66%] ✅ 시스템 의존성 설치 완료
[66%] Python 의존성 설치 중... (시간이 걸릴 수 있습니다)
[83%] ✅ Python 의존성 설치 완료
[83%] 설치 확인 중...
✓ scrapy 설치 확인
✓ fastapi 설치 확인
✓ sqlalchemy 설치 확인
✓ pandas 설치 확인
✓ transformers 설치 확인
✓ paramiko 설치 확인
✓ pyyaml 설치 확인
✓ PyQt5 설치 확인
[100%] ✅ 설치 확인 완료

✅ 설치가 성공적으로 완료되었습니다!
```

---

## 📝 다른 설치 스크립트 상태

### ✅ Shell 스크립트들 (정상)

다음 Shell 스크립트들은 이미 가상환경 활성화를 올바르게 수행하고 있어 수정 불필요:

1. **`cointicker/gui/scripts/install.sh`**
   ```bash
   # Line 45
   source venv/bin/activate  # ✅ 가상환경 활성화

   # Line 68
   pip install -r "$REQUIREMENTS_FILE"  # ✅ 활성화된 가상환경의 pip 사용
   ```

2. **`scripts/start.sh`**
   ```bash
   # Line 52-64
   python3 -m venv venv
   source venv/bin/activate

   if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
       pip install -r "$PROJECT_ROOT/requirements.txt"
   elif [ -f "$PROJECT_ROOT/requirements/dev.txt" ]; then
       pip install -r "$PROJECT_ROOT/requirements/dev.txt"
   fi
   ```

3. **`scripts/test_user_flow.sh`**
   ```bash
   # Line 40, 55
   source venv/bin/activate
   pip install -q -r "$PROJECT_ROOT/requirements.txt"
   ```

4. **`cointicker/tests/run_integration_tests.sh`**
   ```bash
   # Line 51, 98
   source venv/bin/activate
   pip install -r "$REQUIREMENTS_FILE"
   ```

---

## 🎯 핵심 교훈

### 1. macOS Homebrew Python 제약
- PEP 668: Externally-Managed-Environment
- 시스템 Python으로 직접 pip 설치 불가
- **반드시 가상환경 사용 필요**

### 2. Python 실행 파일 경로
- **시스템 Python**: `/usr/bin/python3` 또는 Homebrew 경로
- **가상환경 Python**:
  - macOS/Linux: `venv/bin/python`
  - Windows: `venv/Scripts/python.exe`

### 3. subprocess 모듈 사용 시 주의
- `sys.executable`은 **현재 스크립트를 실행한 Python**
- 가상환경 생성 후에도 `sys.executable`은 시스템 Python을 가리킴
- **가상환경의 Python을 명시적으로 지정 필요**

---

## ✅ 결론

### 수정 완료 사항:
1. ✅ `installer.py`의 가상환경 Python 경로 감지 로직 추가
2. ✅ `install_python_dependencies()`에서 가상환경 Python 사용
3. ✅ `verify_installation()`에서 가상환경 Python으로 패키지 확인
4. ✅ Shell 스크립트들은 이미 정상 작동 중

### 예상 효과:
- ✅ macOS Homebrew Python 환경에서 정상 설치 가능
- ✅ 가상환경 분리를 통한 시스템 보호
- ✅ 모든 의존성이 가상환경에 올바르게 설치됨

---

**수정 완료**: 2025-12-03
**다음 테스트 필요**: 통합 설치 마법사 재실행
