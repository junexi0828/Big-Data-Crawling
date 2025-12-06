# CoinTicker GUI 통합 가이드

> **엔터프라이즈급 통합 관리 및 모니터링 시스템**

## 📋 목차

1. [개요](#개요)
2. [빠른 시작](#빠른-시작)
3. [설치](#설치)
4. [실행](#실행)
5. [주요 기능](#주요-기능)
6. [모듈 시스템](#모듈-시스템)
7. [설정 관리](#설정-관리)
8. [문제 해결](#문제-해결)

---

## 개요

CoinTicker GUI는 라즈베리파이 클러스터와 Tier2 서버를 통합 관리하는 엔터프라이즈급 애플리케이션입니다.

### 핵심 특징

- **모듈 통합 관리**: 모든 시스템 모듈을 중앙에서 관리
- **실시간 모니터링**: 클러스터 및 서버 상태 실시간 추적
- **원격 제어**: SSH를 통한 라즈베리파이 노드 제어
- **설치 마법사**: 자동 의존성 설치 및 설정
- **크로스 플랫폼**: PyQt5/tkinter fallback 지원

---

## 빠른 시작

### PICU 루트에서 실행 (권장)

```bash
# 1. 통합 가상환경 설정
bash setup_venv.sh

# 2. 가상환경 활성화
source venv/bin/activate

# 3. GUI 실행
bash run_gui.sh
```

### 설치 마법사 실행

```bash
# CLI 버전 (GUI 불필요)
bash run_installer.sh

# 또는 직접 실행
source venv/bin/activate
python cointicker/gui/installer/installer_cli.py
```

---

## 설치

### 방법 1: 통합 가상환경 설정 (권장)

PICU 루트에서 모든 의존성을 한 번에 설치:

```bash
# PICU 루트에서 실행
bash setup_venv.sh
```

이 스크립트는:

- Python 버전 확인
- 가상환경 생성 (`venv/`)
- 모든 의존성 자동 설치 (`requirements.txt`)
- PyQt5 포함 모든 패키지 설치

### 방법 2: CLI 설치 마법사

```bash
# PICU 루트에서
bash run_installer.sh

# 또는 cointicker에서
cd cointicker
python gui/installer/installer_cli.py
```

### 방법 3: 수동 설치

```bash
# 가상환경 생성
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install --upgrade pip
pip install -r requirements.txt
```

### PyQt5 설치 (GUI 사용 시)

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

---

## 실행

### GUI 애플리케이션

#### PICU 루트에서 (권장)

```bash
# 가상환경 활성화 후
source venv/bin/activate
bash run_gui.sh

# 또는 직접 실행
python cointicker/gui/main.py
```

#### cointicker 디렉토리에서

```bash
cd cointicker
source venv/bin/activate  # cointicker/venv 사용 시
python gui/main.py
```

### 설치 마법사

```bash
# PICU 루트에서
bash run_installer.sh

# 또는
source venv/bin/activate
python cointicker/gui/installer/installer_cli.py
```

---

## 주요 기능

### 1. 대시보드 탭

- 시스템 전체 요약 정보
- 모듈 상태 요약
- 클러스터 및 Tier2 서버 상태

### 2. 클러스터 모니터링 탭

- **노드 상태 테이블**: 모든 라즈베리파이 노드 상태
- **리소스 모니터링**: CPU, 메모리, 디스크 사용률
- **Hadoop/HDFS 상태**: HDFS 파일 시스템 상태 확인
- **Scrapy 프로세스**: 실행 중인 Spider 프로세스 확인

### 3. Tier2 서버 탭

- **서버 헬스 체크**: FastAPI 백엔드 서버 상태
- **대시보드 요약**: 실시간 데이터 요약
- **감성 분석 추이**: 시간별 감성 분석 데이터
- **최신 뉴스 및 인사이트**: 수집된 데이터 조회
- **인사이트 생성**: 수동 인사이트 생성 트리거

### 4. 모듈 관리 탭

- **모듈 목록**: 등록된 모든 모듈 표시
- **모듈 상태**: 각 모듈의 실행 상태
- **모듈 로드**: 동적 모듈 로드
- **모듈 설정**: 모듈별 설정 확인

### 5. 제어 탭

- **Spider 제어**: Spider 시작/중지
- **파이프라인 제어**: 전체 파이프라인 재시작
- **실행 로그**: 명령어 실행 결과 표시
- **호스트 선택**: 원격/로컬 실행 선택

### 6. 설정 탭

- **Tier2 서버 URL**: 백엔드 서버 주소 설정
- **설정 파일 보기**: 모든 설정 파일 내용 확인
- **설정 수정**: 설정 값 변경 및 저장

---

## 모듈 시스템

### 지원 모듈

1. **SpiderModule**: Scrapy Spider 관리

   - Spider 시작/중지
   - Spider 상태 확인
   - Spider 목록 조회

2. **MapReduceModule**: MapReduce 작업 관리

   - 정제 작업 실행
   - 작업 상태 확인

3. **HDFSModule**: HDFS 파일 시스템 관리

   - 파일 업로드/다운로드
   - 디렉토리 목록 조회
   - HDFS 상태 확인

4. **BackendModule**: FastAPI 백엔드 관리

   - 서버 시작/중지
   - API 호출
   - 헬스 체크

5. **PipelineModule**: 파이프라인 관리
   - 오케스트레이터 제어
   - 스케줄러 제어
   - 전체 파이프라인 실행

### 모듈 매핑

모듈은 `cointicker/gui/module_mapping.json`에 정의됩니다:

```json
{
  "modules": [
    {
      "name": "SpiderModule",
      "path": "gui.modules.spider_module",
      "class": "SpiderModule",
      "config": {
        "worker_nodes_path": "worker-nodes"
      }
    }
  ]
}
```

### 새 모듈 추가하기

1. **모듈 클래스 생성** (`gui/modules/my_module.py`):

```python
from gui.core.module_manager import ModuleInterface

class MyModule(ModuleInterface):
    def initialize(self, config: dict) -> bool:
        # 초기화 로직
        return True

    def start(self) -> bool:
        # 시작 로직
        return True

    def stop(self) -> bool:
        # 중지 로직
        return True

    def execute(self, command: str, params: dict = None) -> dict:
        # 명령어 실행
        return {"success": True}
```

2. **모듈 매핑에 등록** (`gui/module_mapping.json`):

```json
{
  "name": "MyModule",
  "path": "gui.modules.my_module",
  "class": "MyModule",
  "config": {}
}
```

3. **모듈 사용**:

```python
result = module_manager.execute_command(
    "MyModule",
    "my_command",
    {"param": "value"}
)
```

---

## 설정 관리

### 설정 파일 위치

- `cointicker/config/cluster_config.yaml` - 클러스터 설정
- `cointicker/config/database_config.yaml` - 데이터베이스 설정
- `cointicker/config/spider_config.yaml` - Spider 설정
- `cointicker/config/gui_config.yaml` - GUI 설정 (자동 생성)

### 설정 예시

```yaml
# config/gui_config.yaml
gui:
  window:
    width: 1400
    height: 900
    theme: "default"
  refresh:
    auto_refresh: false
    interval: 30
  tier2:
    base_url: "http://localhost:5000"
    timeout: 5
  cluster:
    ssh_timeout: 10
    retry_count: 3
```

### 설정 사용

```python
from gui.core.config_manager import ConfigManager

config = ConfigManager()
value = config.get_config("gui", "tier2.base_url")
config.set_config("gui", "tier2.base_url", "http://new-url:5000")
```

---

## 문제 해결

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

### tkinter 오류 (macOS Python 3.14)

Python 3.14에서 tkinter가 기본 포함되지 않을 수 있습니다.

**해결 방법:**

1. CLI 설치 마법사 사용 (권장)
2. PyQt5 설치 후 사용
3. 또는 Python-tk 설치:
   ```bash
   brew install python-tk
   ```

### SSH 연결 실패

1. **SSH 키 설정 확인**:

   ```bash
   ssh-keygen -t rsa -b 4096
   ssh-copy-id ubuntu@192.168.1.100
   ```

2. **방화벽 설정 확인**
3. **네트워크 연결 확인**

### 모듈 로드 실패

1. `module_mapping.json` 파일 확인
2. 모듈 경로 확인
3. 모듈 클래스 이름 확인
4. 의존성 설치 확인

### 가상환경 문제

PICU 루트의 통합 가상환경을 사용하세요:

```bash
# PICU 루트에서
bash setup_venv.sh
source venv/bin/activate
```

---

## 사용자 인터페이스

### 탭 구성

1. **대시보드**: 시스템 전체 요약
2. **클러스터**: 라즈베리파이 노드 모니터링
3. **Tier2 서버**: 백엔드 서버 상태
4. **모듈 관리**: 등록된 모듈 관리
5. **제어**: Spider 및 파이프라인 제어
6. **설정**: 애플리케이션 설정

### 단축키

- `F5`: 모든 데이터 새로고침
- `Ctrl+Q`: 애플리케이션 종료

### 자동 새로고침

- "보기" 메뉴 → "자동 새로고침" 체크
- 기본 30초 간격 (설정에서 변경 가능)

---

## 아키텍처

```
PICU/
├── venv/                    # 통합 가상환경 (PICU 루트)
├── requirements.txt         # 통합 의존성
├── setup_venv.sh           # 가상환경 설정 스크립트
├── run_gui.sh              # GUI 실행 스크립트
├── run_installer.sh        # 설치 마법사 실행 스크립트
│
└── cointicker/
    └── gui/
        ├── core/                    # 핵심 모듈
        │   ├── module_manager.py    # 모듈 매니저
        │   └── config_manager.py    # 설정 관리자
        ├── modules/                 # 기능 모듈
        │   ├── spider_module.py
        │   ├── mapreduce_module.py
        │   ├── hdfs_module.py
        │   ├── backend_module.py
        │   └── pipeline_module.py
        ├── installer/               # 설치 마법사
        │   ├── installer.py         # 설치 로직
        │   ├── installer_cli.py     # CLI 버전
        │   └── installer_gui.py    # GUI 버전
        ├── app.py                   # 메인 애플리케이션 (PyQt5)
        ├── dashboard.py             # 대시보드 (tkinter fallback)
        ├── cluster_monitor.py       # 클러스터 모니터링
        ├── tier2_monitor.py         # Tier2 서버 모니터링
        ├── main.py                  # 진입점
        └── module_mapping.json      # 모듈 매핑 설정
```

---

## 보안 고려사항

1. **SSH 키 관리**: SSH 키는 안전하게 보관하세요
2. **설정 파일 보안**: 민감한 정보는 환경 변수 사용
3. **CORS 설정**: 프로덕션 환경에서는 특정 도메인만 허용
4. **네트워크 보안**: 방화벽 설정 확인

---

## 추가 리소스

- [프로젝트 README](../cointicker/README.md)
- [빠른 시작 가이드](../cointicker/docs/QUICKSTART.md)
- [테스트 가이드](../cointicker/tests/README.md)
- [개발 현황](../cointicker/DEVELOPMENT_STATUS.md)

---

## 라이선스

MIT License
