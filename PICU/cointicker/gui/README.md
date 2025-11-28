# GUI 애플리케이션

> **참고**: 상세한 가이드는 [PICU 루트의 GUI_GUIDE.md](../../../PICU_docs/GUI_GUIDE.md)를 참고하세요.

CoinTicker 프로젝트의 통합 관리 및 모니터링 시스템입니다.

## 🎯 주요 기능

### 1. 모듈 통합 관리

- **모듈 매니저**: 모든 시스템 모듈을 중앙에서 관리
- **플러그인 시스템**: 모듈을 동적으로 로드 및 실행
- **모듈 매핑**: JSON 기반 모듈 설정 및 매핑

### 2. 클러스터 모니터링

- 라즈베리파이 노드 상태 실시간 모니터링
- CPU, 메모리, 디스크 사용률 추적
- Hadoop/HDFS 상태 확인
- Scrapy 프로세스 모니터링

### 3. Tier2 서버 관리

- FastAPI 백엔드 서버 헬스 체크
- 대시보드 데이터 조회
- 인사이트 생성 및 관리

### 4. 파이프라인 제어

- Spider 시작/중지
- MapReduce 작업 실행
- 파이프라인 오케스트레이터 제어
- 스케줄러 관리

### 5. 설정 관리

- 중앙 집중식 설정 관리
- YAML/JSON 설정 파일 지원
- 설정 유효성 검사

### 6. 설치 마법사

- 의존성 자동 설치
- 가상환경 자동 생성
- 시스템 의존성 확인 및 설치

## 📦 설치

### PICU 루트에서 통합 설치 (권장)

```bash
# PICU 루트에서
bash setup_venv.sh
source venv/bin/activate
```

### cointicker 디렉토리에서 설치

```bash
# 가상환경 생성
python3 -m venv venv
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

## 🚀 실행

### PICU 루트에서 실행 (권장)

```bash
# 가상환경 활성화 후
source venv/bin/activate
bash run_gui.sh
```

### cointicker에서 실행

```bash
python gui/main.py
```

## 🧪 테스트

### GUI 테스트 실행

```bash
# 리팩토링 테스트
python gui/tests/test_refactoring.py

# 통합 테스트
python gui/tests/test_integration.py
```

### 설치 마법사

```bash
# PICU 루트에서
bash run_installer.sh

# 또는
python cointicker/gui/installer/installer_cli.py
```

## 🏗️ 아키텍처

```
gui/
├── core/                    # 핵심 모듈
│   ├── module_manager.py    # 모듈 매니저
│   ├── config_manager.py    # 설정 관리자
│   ├── cache_manager.py     # 캐시 관리자
│   ├── retry_utils.py       # 재시도 유틸리티
│   └── timing_config.py     # 타이밍 설정
├── modules/                 # 기능 모듈
│   ├── spider_module.py     # Spider 관리
│   ├── mapreduce_module.py # MapReduce 관리
│   ├── hdfs_module.py       # HDFS 관리
│   ├── backend_module.py   # Backend 관리
│   ├── pipeline_module.py  # 파이프라인 관리
│   ├── pipeline_orchestrator.py # 파이프라인 오케스트레이터
│   ├── process_monitor.py   # 프로세스 모니터
│   └── managers/            # 서비스 매니저
│       ├── hdfs_manager.py  # HDFS 매니저
│       ├── kafka_manager.py # Kafka 매니저
│       └── ssh_manager.py   # SSH 매니저
├── ui/                      # UI 탭 컴포넌트
│   ├── dashboard_tab.py     # 대시보드 탭
│   ├── cluster_tab.py       # 클러스터 탭
│   ├── tier2_tab.py         # Tier2 서버 탭
│   ├── modules_tab.py      # 모듈 관리 탭
│   ├── control_tab.py      # 제어 탭
│   └── config_tab.py        # 설정 탭
├── installer/               # 설치 마법사
│   ├── installer.py         # 설치 로직
│   ├── installer_cli.py     # CLI 설치
│   ├── installer_gui.py    # GUI 설치
│   └── unified_installer.py # 통합 설치
├── monitors/                # 모니터링 모듈
│   ├── cluster_monitor.py   # 클러스터 모니터링
│   └── tier2_monitor.py     # Tier2 서버 모니터링
├── tests/                   # GUI 테스트
│   ├── test_refactoring.py  # 리팩토링 테스트
│   ├── test_integration.py  # 통합 테스트
│   ├── test_tier2_monitor.py # Tier2Monitor 테스트
│   ├── test_config_manager.py # ConfigManager 테스트
│   └── test_module_manager.py # ModuleManager 테스트
├── app.py                   # 메인 애플리케이션 (PyQt5)
├── dashboard.py             # 대시보드 (tkinter fallback)
├── main.py                  # 진입점
├── config/                  # 설정 파일
│   └── module_mapping.json  # 모듈 매핑 설정
├── scripts/                 # 스크립트
│   ├── run.sh               # 실행 스크립트
│   └── install.sh           # 설치 스크립트
├── docs/                    # 문서
│   └── QUICK_START.md       # 빠른 시작 가이드
└── README.md                # 이 파일
```

## 📋 모듈 시스템

### 모듈 인터페이스

모든 모듈은 `ModuleInterface`를 구현해야 합니다:

```python
from gui.core.module_manager import ModuleInterface

class MyModule(ModuleInterface):
    def initialize(self, config: dict) -> bool:
        # 초기화 로직
        pass

    def start(self) -> bool:
        # 시작 로직
        pass

    def stop(self) -> bool:
        # 중지 로직
        pass

    def execute(self, command: str, params: dict = None) -> dict:
        # 명령어 실행
        pass
```

### 모듈 등록

`config/module_mapping.json`에 모듈을 등록:

```json
{
  "modules": [
    {
      "name": "MyModule",
      "path": "gui.modules.my_module",
      "class": "MyModule",
      "config": {
        "key": "value"
      }
    }
  ]
}
```

## ⚙️ 설정

### 설정 파일 위치

- `config/cluster_config.yaml` - 클러스터 설정
- `config/database_config.yaml` - 데이터베이스 설정
- `config/spider_config.yaml` - Spider 설정
- `config/gui_config.yaml` - GUI 설정

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
```

## 🔧 문제 해결

### PyQt5 설치 실패

macOS:

```bash
brew install pyqt5
pip install PyQt5
```

Linux:

```bash
sudo apt-get install python3-pyqt5
```

Windows:

```bash
pip install PyQt5
```

### tkinter 사용 (PyQt5 대체)

PyQt5가 설치되지 않은 경우 자동으로 tkinter 버전을 사용합니다.

### SSH 연결 실패

1. SSH 키 설정 확인
2. 방화벽 설정 확인
3. 네트워크 연결 확인

## 📚 API 사용 예시

### 모듈 실행

```python
from gui.core.module_manager import ModuleManager

manager = ModuleManager()
manager.load_module_mapping("gui/config/module_mapping.json")

# Spider 시작
result = manager.execute_command(
    "SpiderModule",
    "start_spider",
    {"spider_name": "upbit_trends", "host": None}
)
```

### 설정 관리

```python
from gui.core.config_manager import ConfigManager

config = ConfigManager()
value = config.get_config("gui", "tier2.base_url")
config.set_config("gui", "tier2.base_url", "http://new-url:5000")
```

## 🎨 사용자 인터페이스

### 탭 구성

1. **대시보드**: 시스템 전체 요약
2. **클러스터**: 라즈베리파이 노드 모니터링
3. **Tier2 서버**: 백엔드 서버 상태
4. **모듈 관리**: 등록된 모듈 관리
5. **제어**: Spider 및 파이프라인 제어
6. **설정**: 애플리케이션 설정

### 단축키

- `F5`: 새로고침
- `Ctrl+Q`: 종료

## 🔐 보안 고려사항

1. SSH 키는 안전하게 보관하세요
2. 설정 파일에 민감한 정보가 포함되지 않도록 주의하세요
3. 프로덕션 환경에서는 CORS 설정을 제한하세요

## 📝 라이선스

MIT License
