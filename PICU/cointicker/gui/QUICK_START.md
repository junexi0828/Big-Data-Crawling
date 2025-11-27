# GUI 빠른 시작 가이드

## 🚀 가장 빠른 방법

### PICU 루트에서 (권장)

```bash
# 1. 통합 가상환경 설정 (한 번만)
bash setup_venv.sh

# 2. 가상환경 활성화
source venv/bin/activate

# 3. GUI 실행
bash run_gui.sh
```

끝! 이제 GUI가 실행됩니다.

## 📋 단계별 설명

### 1단계: 가상환경 설정

PICU 루트에서 실행:

```bash
bash setup_venv.sh
```

이 스크립트는:
- Python 버전 확인
- 가상환경 생성 (`venv/`)
- 모든 의존성 자동 설치

### 2단계: 가상환경 활성화

```bash
source venv/bin/activate
```

### 3단계: GUI 실행

```bash
bash run_gui.sh
```

또는:

```bash
python cointicker/gui/main.py
```

## 🔧 문제 해결

### PyQt5가 없을 때

자동으로 CLI 모드로 전환되거나, 설치 마법사가 실행됩니다.

### tkinter 오류 (macOS)

Python 3.14에서는 tkinter가 없을 수 있습니다. PyQt5를 설치하세요:

```bash
pip install PyQt5
```

## 📚 더 자세한 정보

- [GUI 통합 가이드](../../GUI_GUIDE.md) - 전체 가이드
- [GUI README](README.md) - 상세 문서

