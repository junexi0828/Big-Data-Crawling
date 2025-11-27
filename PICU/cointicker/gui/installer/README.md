# 설치 마법사

> **참고**: 상세한 가이드는 [PICU 루트의 GUI_GUIDE.md](../../../GUI_GUIDE.md)를 참고하세요.

CoinTicker 프로젝트의 자동 설치 도구입니다.

## 설치 방법

### PICU 루트에서 통합 설치 (권장)

```bash
# PICU 루트에서
bash setup_venv.sh
```

### CLI 설치 마법사

```bash
# PICU 루트에서
bash run_installer.sh

# 또는 cointicker에서
python gui/installer/installer_cli.py
```

### GUI 설치 마법사 (PyQt5 필요)

```bash
# PyQt5 설치 후
pip install PyQt5

# 설치 마법사 실행
python gui/installer/installer_gui.py
```

## 설치 과정

1. **Python 버전 확인**: Python 3.8 이상 필요
2. **pip 확인**: pip 설치 여부 확인
3. **가상환경 생성** (선택): 자동 가상환경 생성
4. **시스템 의존성 설치**: OS별 시스템 패키지 설치
5. **Python 의존성 설치**: requirements.txt 자동 설치
6. **설치 확인**: 필수 패키지 설치 확인

## 문제 해결

### macOS에서 tkinter 오류

Python 3.14에서 tkinter가 기본 포함되지 않을 수 있습니다.

**해결 방법:**

1. CLI 설치 마법사 사용 (권장)
2. 또는 Python-tk 설치:
   ```bash
   brew install python-tk
   ```

### PyQt5 설치 실패

**macOS:**

```bash
brew install pyqt5
pip install PyQt5
```

**Linux:**

```bash
sudo apt-get install python3-pyqt5
```

**Windows:**

```bash
pip install PyQt5
```

## 수동 설치

GUI 없이 수동으로 설치하려면:

```bash
# 가상환경 생성
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install --upgrade pip
pip install -r requirements.txt
```
