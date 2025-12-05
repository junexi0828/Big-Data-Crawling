# 시스템 자원 모니터링 기능 구현 검토 보고서 1차

## 1. 개요

본 문서는 'CoinTicker 통합 관리 시스템' GUI에 추가된 **시스템 자원(CPU, 메모리) 실시간 모니터링 기능**의 구현 내용을 검토하고 평가하기 위해 작성되었습니다. 이 기능은 단일 노드 환경에서 발생할 수 있는 자원 부족 문제를 진단하기 위해 추가되었습니다.

## 2. 검토 파일

- **`gui/app.py`**: 메인 애플리케이션 (Controller 역할)
- **`gui/ui/dashboard_tab.py`**: 대시보드 UI (View 역할)
- **`gui/modules/managers/system_monitor.py`**: 자원 수집 로직 (Model 역할)

## 3. 구현 구조 분석

이번 기능은 **Model-View-Controller(MVC)와 유사한 패턴**으로 매우 체계적으로 구현되었습니다. 각 파일의 역할이 명확하게 분리되어 있어 코드의 유지보수성과 확장성이 뛰어납니다.

- **`system_monitor.py` (Model)**

  - `psutil` 라이브러리를 사용하여 실제 시스템 자원 데이터를 수집하는 역할을 담당합니다.
  - `psutil`이 없어도 프로그램이 비정상 종료되지 않도록 예외 처리가 되어 있으며, 기능이 비활성화됨을 명확히 로깅합니다.
  - `get_system_stats()` 메서드를 통해 CPU, 메모리, 디스크 사용량 등 정제된 데이터를 제공하는 깔끔한 인터페이스를 가집니다.

- **`dashboard_tab.py` (View)**

  - 수집된 자원 데이터를 사용자에게 시각적으로 보여주는 UI 컴포넌트(`QProgressBar`)를 담당합니다.
  - `update_resource_display()` 라는 공개 메서드를 통해 외부에서 데이터를 받아 UI를 갱신하는 역할을 명확히 합니다.
  - 자원 사용량에 따라 프로그레스 바의 색상을 변경하는 로직이 포함되어 사용자에게 직관적인 피드백을 제공합니다.

- **`app.py` (Controller)**
  - `SystemMonitor`와 `DashboardTab` 인스턴스를 생성하고 관리합니다.
  - `QTimer`를 사용하여 3초마다 `system_monitor`로부터 데이터를 가져와 `dashboard_tab`의 UI를 업데이트하도록 조율하는 **핵심적인 역할**을 수행합니다.
  - 자원 모니터링 위젯을 메인 윈도우의 **상태 표시줄(Status Bar)**과 **대시보드 탭** 두 곳에 모두 표시하여 사용자가 어느 화면에서든 시스템 상태를 쉽게 인지할 수 있도록 구현한 점이 돋보입니다.

## 4. 코드 검토 결과

### 4.1. 장점

- **관심사의 분리 (SoC)**: 앞서 언급했듯, 데이터 수집, UI 표시, 전체 흐름 제어의 역할이 세 개의 파일에 명확하게 분리되어 있어 이상적인 구조입니다.
- **안정성**: `psutil` 라이브러리의 존재 여부를 확인하고, 없을 경우 관련 기능을 비활성화하는 방식으로 구현되어 특정 라이브러리 부재로 인한 전체 프로그램의 비정상 종료를 방지했습니다.
- **우수한 사용자 경험(UX)**:
  - 자원 사용량을 단순히 텍스트가 아닌 **프로그레스 바**로 시각화하여 직관성을 높였습니다.
  - 사용량이 75%, 90%를 초과할 경우 **색상(초록 -> 주황 -> 빨강)을 변경**하여 사용자에게 위험 수준을 즉시 알립니다.
  - 메모리 프로그레스 바에 마우스를 올리면 **툴팁(Tool-tip)**으로 전체 용량 대비 실제 사용량(GB)을 보여주는 세심함이 돋보입니다.
- **효율적인 연동**: `QTimer`를 사용하여 주기적으로, 그리고 비동기적으로 UI를 업데이트함으로써 GUI의 반응성을 해치지 않으면서도 실시간에 가까운 모니터링을 구현했습니다.

### 4.2. 개선 제안 (선택 사항)

현재 구현은 매우 훌륭하여 추가적인 개선이 반드시 필요하지는 않지만, 향후 고도화를 위해 다음 사항을 고려해볼 수 있습니다.

- **업데이트 주기 설정**: 현재 3초로 하드코딩된 업데이트 주기를 `timing_config.py`와 같은 설정 파일로 옮기면, 사용자가 시스템 부하에 따라 유연하게 조절할 수 있게 됩니다.
- **CPU 측정 방식**: `psutil.cpu_percent(interval=1)`은 1초간 블로킹(blocking)됩니다. 현재 3초 주기로는 전혀 문제없지만, 만약 더 빠른 UI 반응성이 요구된다면 별도 스레드에서 `psutil.cpu_percent(interval=None)`을 주기적으로 호출하는 논블로킹(non-blocking) 방식으로 변경을 고려할 수 있습니다.

## 5. 결론

**성공적으로 구현되었습니다.**

새로 추가된 시스템 자원 모니터링 기능은 매우 체계적이고 안정적으로 구현되었습니다. 명확한 역할 분담, 뛰어난 사용자 경험, 안정성을 고려한 예외 처리 등 모든 면에서 높은 완성도를 보여줍니다.

이 기능은 향후 복잡한 파이프라인 운영 중 발생할 수 있는 **성능 문제를 진단하고, 시스템 장애의 원인이 자원 부족인지 아닌지를 신속하게 파악하는 데 결정적인 역할**을 할 것입니다.

# 시스템 자원 모니터링 기능 구현 검토 보고서 2차 (개선사항)

## 1. 개요

본 문서는 'CoinTicker 통합 관리 시스템' GUI에 추가된 **시스템 자원(CPU, 메모리) 실시간 모니터링 기능**의 구현 내용을 검토하고, 코드 전반의 하드코딩된 타이머 값에 대한 리팩토링을 제안하기 위해 작성되었습니다.

## 2. 검토 파일

- **`gui/app.py`**: 메인 애플리케이션 (Controller 역할)
- **`gui/ui/dashboard_tab.py`**: 대시보드 UI (View 역할)
- **`gui/modules/managers/system_monitor.py`**: 자원 수집 로직 (Model 역할)
- **`gui/modules/managers/hdfs_manager.py`**: HDFS 관리 로직

## 3. 자원 모니터링 기능 구현 구조 분석

이번 기능은 **Model-View-Controller(MVC)와 유사한 패턴**으로 매우 체계적으로 구현되었습니다. 각 파일의 역할이 명확하게 분리되어 있어 코드의 유지보수성과 확장성이 뛰어납니다.

- **`system_monitor.py` (Model)**: `psutil`을 사용하여 시스템 자원 데이터를 수집하고, 깔끔한 인터페이스를 제공합니다.
- **`dashboard_tab.py` (View)**: 수집된 데이터를 `QProgressBar`를 통해 시각적으로 표현하며, 값에 따라 색상을 변경하여 직관적인 피드백을 제공합니다.
- **`app.py` (Controller)**: `QTimer`를 사용하여 주기적으로 `SystemMonitor`와 `DashboardTab`을 연결하고, UI 업데이트를 조율하는 핵심 역할을 수행합니다.

### 4. 코드 검토 결과

- **관심사의 분리 (SoC)**: 데이터 수집, UI 표시, 흐름 제어의 역할이 명확하게 분리되어 이상적인 구조입니다.
- **안정성**: `psutil` 라이브러리가 없을 경우에도 프로그램이 비정상 종료되지 않도록 안정적으로 처리되었습니다.
- **우수한 사용자 경험(UX)**: 프로그레스 바, 동적 색상 변경, 상세 정보를 담은 툴팁 등을 통해 사용자 경험을 크게 향상했습니다.

---

## 5. 하드코딩된 타이머 값 리팩토링 권장 사항

코드 전반을 검토한 결과, 여러 곳에 타이머 간격 및 타임아웃 값이 하드코딩되어 있는 것을 확인했습니다. 유지보수성과 유연성을 높이기 위해, 이 값들을 **`gui/core/timing_config.py`** 로 중앙화하여 관리하는 것을 강력히 권장합니다.

### 5.1. 발견된 하드코딩 값 및 개선 제안

| 파일 경로                              | 라인 (근사치) | 현재 코드                                             | 개선 제안                                                                                                    |
| -------------------------------------- | ------------- | ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| `gui/app.py`                           | 125           | `self.resource_timer.start(3000)`                     | `interval = TimingConfig.get("gui.resource_update_interval", 3000)`<br>`self.resource_timer.start(interval)` |
| `gui/app.py`                           | 480           | `event.wait(timeout=30)`                              | `timeout = TimingConfig.get("gui.user_confirm_timeout", 30)`<br>`event.wait(timeout=timeout)`                |
| `gui/app.py`                           | 900           | `process.wait(timeout=5)`                             | `timeout = TimingConfig.get("pipeline.process_wait_timeout", 5)`<br>`process.wait(timeout=timeout)`          |
| `gui/modules/managers/hdfs_manager.py` | 120           | `stop_result.stderr.decode("utf-8", errors="ignore")` | `timeout=30` -> `timeout=TimingConfig.get("hdfs.script_timeout", 30)`                                        |
| `gui/modules/managers/hdfs_manager.py` | 145           | `stop_result = subprocess.run(..., timeout=10)`       | `timeout=10` -> `timeout=TimingConfig.get("hdfs.daemon_stop_timeout", 10)`                                   |
| `gui/modules/managers/hdfs_manager.py` | 500           | `format_result = subprocess.run(..., timeout=30)`     | `timeout=30` -> `timeout=TimingConfig.get("hdfs.format_timeout", 30)`                                        |

### 5.2. 리팩토링 방법

1.  **`timing_config.py`에 키 추가**:
    `DEFAULTS` 딕셔너리에 `"gui.resource_update_interval": 3000` 와 같이 새로운 키와 기본값을 추가합니다.

2.  **코드 수정**:
    하드코딩된 숫자(예: `3000`)를 `TimingConfig.get("gui.resource_update_interval", 3000)`으로 교체합니다.

### 5.3. 기대 효과

- **중앙 관리**: 모든 시간 관련 설정이 한 파일에 모여 있어 관리가 용이해집니다.
- **유연성**: 코드 수정 및 재배포 없이 설정 파일(`config.yaml`) 변경만으로 애플리케이션의 동작을 미세 조정할 수 있습니다.
- **가독성**: `3000`이라는 숫자 대신 `resource_update_interval`과 같은 의미 있는 이름으로 코드를 읽을 수 있어 가독성이 향상됩니다.

## 6. 최종 결론

자원 모니터링 기능은 매우 훌륭하게 구현되었습니다. 여기에 더해, 위에 제안된 **타이머 값 리팩토링**을 진행한다면 코드의 품질과 유지보수성이 한 단계 더 향상될 것입니다.
