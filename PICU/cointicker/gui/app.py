"""
엔터프라이즈급 GUI 애플리케이션
모든 모듈을 통합하는 메인 애플리케이션

⚠️ 주의: 삭제 및 수정 금지 ⚠️

이 파일은 백엔드/프론트엔드 포트 동기화의 핵심입니다:
- _auto_start_essential_services(): GUI 시작 시 백엔드/프론트엔드 자동 시작
- _reinitialize_tier2_monitor(): 백엔드 시작 후 포트 파일 읽어 Tier2 모니터 재초기화
- refresh_all(): 새로고침 시 포트 파일 확인 및 Tier2 모니터 업데이트
- refresh_tier2(): Tier2 새로고침 시 포트 변경 감지

연동된 컴포넌트:
- backend/run_server.sh: 백엔드 포트 파일 생성 (config/.backend_port)
- frontend/run_dev.sh: 백엔드 포트 파일 읽기 및 VITE_API_BASE_URL 설정
- gui/modules/pipeline_orchestrator.py: 백엔드/프론트엔드 프로세스 시작
- gui/tier2_monitor.py: 포트 파일 읽어 백엔드 URL 결정

이 파일의 포트 동기화 로직을 수정하면 GUI의 백엔드 포트 자동 감지가 작동하지 않습니다.
특히 _auto_start_essential_services(), _reinitialize_tier2_monitor(), refresh_all() 메서드는 중요합니다.
"""

import sys
import threading
import time
from pathlib import Path

# PyQt5 사용 시도, 없으면 tkinter 사용
try:
    from PyQt5.QtWidgets import (
        QApplication,
        QMainWindow,
        QWidget,
        QVBoxLayout,
        QHBoxLayout,
        QTabWidget,
        QLabel,
        QPushButton,
        QTableWidget,
        QTableWidgetItem,
        QTextEdit,
        QComboBox,
        QLineEdit,
        QMessageBox,
        QStatusBar,
        QMenuBar,
        QMenu,
        QAction,
        QSystemTrayIcon,
        QMenu as QMenuType,
        QCheckBox,
        QSpinBox,
        QGroupBox,
        QScrollArea,
        QFormLayout,
    )
    from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject, QMetaObject
    from PyQt5.QtGui import QIcon, QFont

    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False

# tkinter fallback도 확인
try:
    import tkinter as tk
    from tkinter import ttk, messagebox, scrolledtext

    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False

if PYQT5_AVAILABLE:
    from gui.core.module_manager import ModuleManager
    from gui.core.config_manager import ConfigManager
    from gui.core.timing_config import TimingConfig
    from gui.core.retry_utils import execute_with_retry
    from gui.monitors import ClusterMonitor, Tier2Monitor
    from gui.ui import (
        DashboardTab,
        ClusterTab,
        Tier2Tab,
        ModulesTab,
        ControlTab,
        ConfigTab,
    )
    from shared.logger import setup_logger

    logger = setup_logger(__name__)

    class MainApplication(QMainWindow):
        """메인 애플리케이션"""

        def __init__(self):
            super().__init__()

            # 핵심 컴포넌트 초기화
            self.module_manager = ModuleManager()
            self.config_manager = ConfigManager()
            self.cluster_monitor = None
            self.tier2_monitor = None
            self.pipeline_orchestrator = None

            # 자동 새로고침
            self.auto_refresh_timer = QTimer()
            self.auto_refresh_timer.timeout.connect(self.refresh_all)
            self.auto_refresh_enabled = False

            # 통계 업데이트 타이머
            self.stats_timer = QTimer()
            self.stats_timer.timeout.connect(self._update_all_stats)
            stats_interval = TimingConfig.get("gui.stats_update_interval", 2000)
            self.stats_timer.start(stats_interval)

            # UI 초기화
            self._init_ui()
            self._load_config()
            self._load_modules()

            # 백엔드와 프론트엔드 자동 시작 (GUI 진입 시, 먼저 실행)
            auto_start_delay = TimingConfig.get("gui.auto_start_delay", 1000)
            QTimer.singleShot(auto_start_delay, self._auto_start_essential_services)

            # 프로세스 상태 테이블 초기 업데이트 (자동 시작 후)
            process_status_delay = TimingConfig.get(
                "gui.process_status_update_delay", 2000
            )
            QTimer.singleShot(process_status_delay, self._update_process_status_table)

            # 초기 데이터 로드 (백엔드 시작 후)
            initial_refresh_delay = TimingConfig.get("gui.initial_refresh_delay", 5000)
            QTimer.singleShot(initial_refresh_delay, self.refresh_all)

        def _init_ui(self):
            """UI 초기화"""
            self.setWindowTitle("CoinTicker 통합 관리 시스템")
            self.setGeometry(100, 100, 1600, 1000)

            # 중앙 위젯
            central_widget = QWidget()
            self.setCentralWidget(central_widget)

            # 메뉴바
            self._create_menu_bar()

            # 탭 위젯
            self.tabs = QTabWidget()
            central_layout = QVBoxLayout()
            central_layout.addWidget(self.tabs)
            central_widget.setLayout(central_layout)

            # 탭 생성 (분리된 탭 클래스 사용)
            self.dashboard_tab = DashboardTab(self)
            self.tabs.addTab(self.dashboard_tab, "대시보드")

            self.cluster_tab = ClusterTab(self)
            self.tabs.addTab(self.cluster_tab, "클러스터")

            self.tier2_tab = Tier2Tab(self)
            self.tabs.addTab(self.tier2_tab, "Tier2 서버")

            self.modules_tab = ModulesTab(self)
            self.tabs.addTab(self.modules_tab, "모듈 관리")

            self.control_tab = ControlTab(self)
            self.tabs.addTab(self.control_tab, "제어")

            self.config_tab = ConfigTab(self)
            self.tabs.addTab(self.config_tab, "설정")

            # 상태바
            self.statusBar().showMessage("준비됨")

        def _create_menu_bar(self):
            """메뉴바 생성"""
            menubar = self.menuBar()

            # 파일 메뉴
            file_menu = menubar.addMenu("파일")

            refresh_action = QAction("새로고침", self)
            refresh_action.setShortcut("F5")
            refresh_action.triggered.connect(self.refresh_all)
            file_menu.addAction(refresh_action)

            file_menu.addSeparator()

            exit_action = QAction("종료", self)
            exit_action.setShortcut("Ctrl+Q")
            exit_action.triggered.connect(self.close)
            file_menu.addAction(exit_action)

            # 보기 메뉴
            view_menu = menubar.addMenu("보기")

            auto_refresh_action = QAction("자동 새로고침", self, checkable=True)
            auto_refresh_action.triggered.connect(self.toggle_auto_refresh)
            view_menu.addAction(auto_refresh_action)

            # 도구 메뉴
            tools_menu = menubar.addMenu("도구")

            installer_action = QAction("설치 마법사", self)
            installer_action.triggered.connect(self.run_installer)
            tools_menu.addAction(installer_action)

            # 도움말 메뉴
            help_menu = menubar.addMenu("도움말")

            about_action = QAction("정보", self)
            about_action.triggered.connect(self.show_about)
            help_menu.addAction(about_action)

        def _load_config(self):
            """설정 로드"""
            self.config_manager.create_default_configs()

            # 클러스터 모니터 초기화
            cluster_config = self.config_manager.load_config("cluster")
            if cluster_config:
                self.cluster_monitor = ClusterMonitor()

            # Tier2 모니터 초기화
            gui_config = self.config_manager.load_config("gui")
            if gui_config:
                # 백엔드 포트 파일에서 우선 읽기
                from gui.monitors import get_default_backend_url

                default_url = get_default_backend_url()

                tier2_url = self.config_manager.get_config(
                    "gui", "tier2.base_url", default_url
                )
                self.tier2_monitor = Tier2Monitor(base_url=tier2_url)
                if hasattr(self, "config_tab") and hasattr(
                    self.config_tab, "tier2_url_edit"
                ):
                    self.config_tab.tier2_url_edit.setText(tier2_url)

                # GUI 설정 값 로드
                if hasattr(self, "config_tab"):
                    if hasattr(self.config_tab, "window_width_spin"):
                        self.config_tab.window_width_spin.setValue(
                            self.config_manager.get_config("gui", "window.width", 1400)
                        )
                        self.config_tab.window_height_spin.setValue(
                            self.config_manager.get_config("gui", "window.height", 900)
                        )
                        theme = self.config_manager.get_config(
                            "gui", "window.theme", "default"
                        )
                        index = self.config_tab.window_theme_combo.findText(theme)
                        if index >= 0:
                            self.config_tab.window_theme_combo.setCurrentIndex(index)

                        self.config_tab.auto_refresh_check.setChecked(
                            self.config_manager.get_config(
                                "gui", "refresh.auto_refresh", False
                            )
                        )
                        self.config_tab.refresh_interval_spin.setValue(
                            self.config_manager.get_config(
                                "gui", "refresh.interval", 30
                            )
                        )

                        self.config_tab.tier2_timeout_spin.setValue(
                            self.config_manager.get_config("gui", "tier2.timeout", 5)
                        )

                        self.config_tab.cluster_ssh_timeout_spin.setValue(
                            self.config_manager.get_config(
                                "gui", "cluster.ssh_timeout", 10
                            )
                        )
                        self.config_tab.cluster_retry_spin.setValue(
                            self.config_manager.get_config(
                                "gui", "cluster.retry_count", 3
                            )
                        )

            # 설정 표시 초기화
            config_refresh_delay = TimingConfig.get("gui.config_refresh_delay", 500)
            QTimer.singleShot(
                config_refresh_delay, lambda: self.refresh_config_display()
            )

        def _load_modules(self):
            """모듈 로드"""
            # 프로젝트 루트 기준으로 경로 해결
            # gui/app.py -> cointicker/gui/config/module_mapping.json
            project_root = Path(__file__).parent.parent
            mapping_file = project_root / "gui" / "config" / "module_mapping.json"

            logger.info(f"모듈 매핑 파일 경로: {mapping_file}")

            if mapping_file.exists():
                self.module_manager.load_module_mapping(str(mapping_file))

                # 모듈 초기화 및 자동 시작
                logger.info(
                    f"모듈 초기화 시작. 등록된 모듈: {list(self.module_manager.modules.keys())}"
                )
                for module_name in self.module_manager.modules:
                    config = self.config_manager.get_config("gui", default={})
                    success = self.module_manager.initialize_module(module_name, config)
                    if success:
                        logger.info(f"모듈 초기화 완료: {module_name}")
                    else:
                        logger.warning(f"모듈 초기화 실패: {module_name}")

                    # 모듈 자동 시작 (SpiderModule, KafkaModule 등은 명령어 실행 시 자동 시작되지만,
                    # 초기 로드 시에도 시작해두면 좋음)
                    if module_name in ["SpiderModule", "KafkaModule", "PipelineModule"]:
                        try:
                            if self.module_manager.start_module(module_name):
                                logger.info(f"모듈 자동 시작 완료: {module_name}")
                            else:
                                logger.warning(f"모듈 자동 시작 실패: {module_name}")
                        except Exception as e:
                            logger.warning(f"모듈 자동 시작 오류 {module_name}: {e}")
            else:
                logger.warning(f"모듈 매핑 파일을 찾을 수 없습니다: {mapping_file}")

            # 파이프라인 오케스트레이터 초기화
            from gui.modules.pipeline_orchestrator import PipelineOrchestrator

            # 사용자 확인 콜백 함수 정의 (스레드 안전)
            def user_confirm_callback(title: str, message: str) -> bool:
                """사용자 확인 다이얼로그 표시 (메인 스레드에서 실행)"""
                import threading

                # 결과를 저장할 변수
                result_container = {"value": False}
                event = threading.Event()

                # 메인 스레드에서 실행할 함수
                def show_dialog():
                    try:
                        # 이벤트 루프 처리하여 다이얼로그가 확실히 표시되도록
                        app = QApplication.instance()
                        if app:
                            app.processEvents()

                        reply = QMessageBox.question(
                            self,
                            title,
                            message,
                            QMessageBox.Yes | QMessageBox.No,
                            QMessageBox.Yes,
                        )
                        result_container["value"] = reply == QMessageBox.Yes
                        logger.info(
                            f"사용자 확인 결과: {'예 (단일 노드 모드로 진행)' if result_container['value'] else '아니오 (멀티노드 모드 유지)'}"
                        )
                    except Exception as e:
                        logger.error(f"사용자 확인 다이얼로그 표시 중 오류: {e}")
                        result_container["value"] = True  # 오류 시 기본값: 예
                    finally:
                        event.set()  # 대기 중인 스레드에 신호 전송

                # 메인 스레드에서 실행 (QTimer 사용)
                QTimer.singleShot(0, show_dialog)

                # 다이얼로그가 표시될 시간을 주기 위해 짧은 대기
                import time

                dialog_wait_delay = TimingConfig.get("gui.dialog_wait_delay", 0.2)
                time.sleep(dialog_wait_delay)

                # 다이얼로그가 닫힐 때까지 대기
                user_confirm_timeout = TimingConfig.get("gui.user_confirm_timeout", 300)
                if not event.wait(timeout=user_confirm_timeout):
                    # 타임아웃 발생 시 기본값 반환
                    logger.warning(
                        "사용자 확인 다이얼로그 타임아웃 (5분). 기본값(예)을 사용합니다."
                    )
                    return True  # 타임아웃 시 기본값: 예

                return result_container["value"]

            self.pipeline_orchestrator = PipelineOrchestrator(
                user_confirm_callback=user_confirm_callback
            )
            self.pipeline_orchestrator.initialize({})

            # 모듈 연결
            if "BackendModule" in self.module_manager.modules:
                self.pipeline_orchestrator.set_module(
                    "backend", self.module_manager.modules["BackendModule"]
                )
            if "KafkaModule" in self.module_manager.modules:
                self.pipeline_orchestrator.set_module(
                    "kafka_consumer", self.module_manager.modules["KafkaModule"]
                )
            if "SpiderModule" in self.module_manager.modules:
                self.pipeline_orchestrator.set_module(
                    "spider", self.module_manager.modules["SpiderModule"]
                )

        def refresh_all(self):
            """모든 데이터 새로고침"""
            # Tier2 모니터가 포트 파일을 다시 읽도록 보장
            try:
                from gui.monitors import get_default_backend_url

                current_url = get_default_backend_url()
                logger.debug(f"refresh_all: 현재 백엔드 URL 확인 = {current_url}")

                # Tier2 모니터가 없거나 포트가 변경되었으면 재초기화
                if not self.tier2_monitor or self.tier2_monitor.base_url != current_url:
                    if self.tier2_monitor:
                        logger.info(
                            f"백엔드 포트 변경 감지: {self.tier2_monitor.base_url} -> {current_url}"
                        )
                    else:
                        logger.debug(f"Tier2 모니터 초기화 (URL: {current_url})")
                    self.tier2_monitor = Tier2Monitor(base_url=current_url)
                    if hasattr(self, "config_tab") and hasattr(
                        self.config_tab, "tier2_url_edit"
                    ):
                        self.config_tab.tier2_url_edit.setText(current_url)
            except Exception as e:
                logger.error(f"refresh_all: Tier2 모니터 포트 업데이트 실패: {e}")

            self.refresh_cluster()
            self.refresh_tier2()
            self.refresh_modules()
            self.update_summary()

        def refresh_cluster(self):
            """클러스터 상태 새로고침"""
            if hasattr(self, "cluster_tab"):
                self.cluster_tab.refresh_cluster()

        def refresh_tier2(self):
            """Tier2 서버 상태 새로고침"""
            # 백엔드 포트가 변경되었을 수 있으므로 항상 재확인
            from gui.tier2_monitor import get_default_backend_url

            current_url = get_default_backend_url()
            logger.debug(f"refresh_tier2: 현재 백엔드 URL 확인 = {current_url}")

            # Tier2 모니터가 없거나 포트가 변경되었으면 재초기화
            if not self.tier2_monitor or self.tier2_monitor.base_url != current_url:
                if self.tier2_monitor:
                    logger.info(
                        f"백엔드 포트 변경 감지: {self.tier2_monitor.base_url} -> {current_url}"
                    )
                else:
                    logger.debug(f"Tier2 모니터 초기화 (URL: {current_url})")
                self.tier2_monitor = Tier2Monitor(base_url=current_url)
                if hasattr(self, "tier2_url_edit"):
                    self.tier2_url_edit.setText(current_url)

            if not self.tier2_monitor:
                logger.error("refresh_tier2: Tier2 모니터가 초기화되지 않았습니다")
                return

            self.statusBar().showMessage("Tier2 서버 상태 확인 중...")

            try:
                logger.debug(
                    f"refresh_tier2: 헬스 체크 요청 URL = {self.tier2_monitor.base_url}"
                )
                status = self.tier2_monitor.get_server_status()
                summary = self.tier2_monitor.get_dashboard_summary()

                import json

                status_text = json.dumps(status, indent=2, ensure_ascii=False)
                if summary and summary.get("success"):
                    status_text += "\n\n=== 대시보드 요약 ===\n"
                    status_text += json.dumps(
                        summary.get("data", {}), indent=2, ensure_ascii=False
                    )

                if hasattr(self, "tier2_tab"):
                    self.tier2_tab.tier2_status_text.setPlainText(status_text)
                self.statusBar().showMessage("Tier2 서버 상태 업데이트 완료", 3000)
            except Exception as e:
                logger.error(f"Tier2 새로고침 실패: {e}")
                self.statusBar().showMessage(f"오류: {str(e)}", 5000)

        def refresh_modules(self):
            """모듈 상태 새로고침"""
            if hasattr(self, "modules_tab"):
                self.modules_tab.refresh_modules()

        def update_summary(self):
            """요약 정보 업데이트"""
            summary = "=== 시스템 요약 ===\n\n"

            # 모듈 상태
            modules = self.module_manager.get_all_modules_status()
            summary += f"등록된 모듈: {len(modules)}\n"
            running = sum(1 for m in modules if m.get("status") == "running")
            summary += f"실행 중인 모듈: {running}\n\n"

            # 클러스터 상태
            if self.cluster_monitor:
                try:
                    nodes = self.cluster_monitor.get_all_nodes_status()
                    online = sum(1 for n in nodes if n.get("online"))
                    summary += f"클러스터 노드: {len(nodes)}개 (온라인: {online}개)\n"
                except:
                    summary += "클러스터 상태 확인 실패\n"

            # Tier2 서버 상태
            if self.tier2_monitor:
                try:
                    health = self.tier2_monitor.check_health()
                    summary += f"Tier2 서버: {'온라인' if health.get('online') else '오프라인'}\n"
                except:
                    summary += "Tier2 서버 상태 확인 실패\n"

            if hasattr(self, "dashboard_tab"):
                self.dashboard_tab.update_summary(summary)

        def start_spider(self):
            """Spider 시작"""
            host = self.host_combo.currentText()
            spider = self.spider_combo.currentText()

            if not spider:
                QMessageBox.warning(self, "경고", "Spider를 선택하세요.")
                return

            # 로그 콜백 설정
            def log_callback(process_id, log_entry):
                timestamp = log_entry.get("timestamp", "")[:19]  # 초까지만
                message = log_entry.get("message", "")
                log_type = log_entry.get("type", "stdout")

                # GUI 스레드에서 실행
                if hasattr(self, "control_tab"):
                    self.control_tab.control_log.append(
                        f"[{timestamp}] [{log_type.upper()}] {message}"
                    )

                # 통계 업데이트
                self._update_spider_stats(spider)

            result = self.module_manager.execute_command(
                "SpiderModule",
                "start_spider",
                {
                    "spider_name": spider,
                    "host": host if host else None,
                    "log_callback": log_callback,
                },
            )

            if result.get("success"):
                if hasattr(self, "control_tab"):
                    self.control_tab.control_log.append(
                        f"✅ Spider 시작: {spider} @ {host or '로컬'} (PID: {result.get('pid')})"
                    )
                # 실시간 통계 업데이트 시작
                self._start_stats_refresh()
            else:
                if hasattr(self, "control_tab"):
                    self.control_tab.control_log.append(
                        f"❌ Spider 시작 실패: {result.get('error', '알 수 없는 오류')}"
                    )

        def stop_spider(self):
            """Spider 중지"""
            host = self.host_combo.currentText()
            spider = self.spider_combo.currentText()

            if not spider:
                QMessageBox.warning(self, "경고", "Spider를 선택하세요.")
                return

            result = self.module_manager.execute_command(
                "SpiderModule",
                "stop_spider",
                {"spider_name": spider, "host": host if host else None},
            )

            if hasattr(self, "control_tab"):
                self.control_tab.control_log.append(
                    f"Spider 중지: {spider} @ {host or '로컬'}"
                )
                self.control_tab.control_log.append(str(result))

        def restart_pipeline(self):
            """파이프라인 재시작"""
            host = self.host_combo.currentText()

            result = self.module_manager.execute_command(
                "PipelineModule", "run_full_pipeline", {"host": host if host else None}
            )

            if hasattr(self, "control_tab"):
                self.control_tab.control_log.append(
                    f"파이프라인 재시작: {host or '로컬'}"
                )
                self.control_tab.control_log.append(str(result))

        def show_hdfs_status(self):
            """HDFS 상태 표시"""
            if hasattr(self, "cluster_tab"):
                self.cluster_tab.show_hdfs_status()

        def generate_insights(self):
            """인사이트 생성"""
            if hasattr(self, "tier2_tab"):
                self.tier2_tab.generate_insights()

        def refresh_config_display(self, config_name: str = None):
            """설정 표시 새로고침"""
            if hasattr(self, "config_tab"):
                self.config_tab.refresh_config_display(config_name)

        def save_gui_config(self):
            """GUI 설정 저장"""
            if hasattr(self, "config_tab"):
                self.config_tab.save_gui_config()

        def update_tier2_url(self):
            """Tier2 URL 업데이트 (하위 호환성)"""
            self.save_gui_config()

        def toggle_auto_refresh(self, enabled: bool):
            """자동 새로고침 토글"""
            self.auto_refresh_enabled = enabled
            if enabled:
                interval = self.config_manager.get_config("gui", "refresh.interval", 30)
                self.auto_refresh_timer.start(interval * 1000)
            else:
                self.auto_refresh_timer.stop()

        def load_modules(self):
            """모듈 로드"""
            self._load_modules()
            self.refresh_modules()
            QMessageBox.information(self, "완료", "모듈이 로드되었습니다.")

        def run_installer(self):
            """설치 마법사 실행"""
            from gui.installer.installer_gui import run_installer

            run_installer()

        def show_about(self):
            """정보 표시"""
            QMessageBox.about(
                self,
                "정보",
                "CoinTicker 통합 관리 시스템\n\n"
                "버전: 2.0.0\n"
                "엔터프라이즈급 통합 GUI 애플리케이션",
            )

        def _start_stats_refresh(self):
            """통계 업데이트 시작"""
            if not self.stats_timer.isActive():
                self.stats_timer.start(2000)

        def _update_all_stats(self):
            """모든 통계 업데이트"""
            self._update_spider_stats()
            self._update_kafka_stats()
            self._update_backend_stats()
            # 프로세스 상태 테이블도 업데이트
            if self.pipeline_orchestrator:
                self._update_process_status_table()

        def _update_spider_stats(self, spider_name: str = None):
            """Spider 통계 업데이트"""
            try:
                if spider_name:
                    result = self.module_manager.execute_command(
                        "SpiderModule",
                        "get_spider_status",
                        {"spider_name": spider_name},
                    )
                    if result.get("success"):
                        status = result.get("status", {})
                        stats = status.get("stats", {})
                        items = stats.get("items_processed", 0)
                        errors = stats.get("errors", 0)
                        if hasattr(self, "control_tab"):
                            self.control_tab.update_stats(
                                spider_stats=f"Spider ({spider_name}): 아이템 {items}개, 에러 {errors}개"
                            )
                else:
                    # 모든 Spider 통계
                    result = self.module_manager.execute_command(
                        "SpiderModule", "get_spider_status", {}
                    )
                    if result.get("success"):
                        spiders = result.get("spiders", {})
                        total_items = sum(
                            s.get("stats", {}).get("items_processed", 0)
                            for s in spiders.values()
                        )
                        running = sum(
                            1 for s in spiders.values() if s.get("status") == "running"
                        )
                        if hasattr(self, "control_tab"):
                            self.control_tab.update_stats(
                                spider_stats=f"Spider: 실행 중 {running}개, 총 아이템 {total_items}개"
                            )
            except Exception as e:
                logger.error(f"Spider 통계 업데이트 오류: {e}")

        def _update_kafka_stats(self):
            """Kafka 통계 업데이트"""
            try:
                result = self.module_manager.execute_command(
                    "KafkaModule", "get_stats", {}
                )
                if result.get("success"):
                    processed = result.get("processed_count", 0)
                    errors = result.get("error_count", 0)
                    status = result.get("status", "stopped")
                    status_text = "실행 중" if status == "running" else "중지됨"
                    if hasattr(self, "control_tab"):
                        self.control_tab.update_stats(
                            kafka_stats=f"Kafka: {status_text}, 처리 {processed}개, 에러 {errors}개"
                        )
            except Exception as e:
                logger.error(f"Kafka 통계 업데이트 오류: {e}")

        def _update_backend_stats(self):
            """Backend 통계 업데이트"""
            try:
                result = self.module_manager.execute_command(
                    "BackendModule", "check_health", {}
                )
                if result.get("success") and result.get("online"):
                    db_status = result.get("database", "unknown")
                    if hasattr(self, "control_tab"):
                        self.control_tab.update_stats(
                            backend_stats=f"Backend: 온라인, DB {db_status}"
                        )
                else:
                    if hasattr(self, "control_tab"):
                        self.control_tab.update_stats(backend_stats="Backend: 오프라인")
            except Exception as e:
                logger.error(f"Backend 통계 업데이트 오류: {e}")

        def _auto_start_essential_services(self):
            """필수 서비스 자동 시작 (백엔드, 프론트엔드)"""
            if not self.pipeline_orchestrator:
                logger.warning(
                    "파이프라인 오케스트레이터가 초기화되지 않아 자동 시작을 건너뜁니다."
                )
                return

            logger.info("필수 서비스 자동 시작 중... (백엔드, 프론트엔드)")

            def run_auto_start():
                # 백엔드와 프론트엔드만 자동 시작
                essential_processes = ["backend", "frontend"]
                started_count = 0

                for process_name in essential_processes:
                    try:
                        result = self.pipeline_orchestrator.start_process(
                            process_name, wait=False
                        )
                        if result.get("success"):
                            started_count += 1
                            logger.info(f"✅ {process_name} 자동 시작 완료")
                        else:
                            logger.warning(
                                f"⚠️ {process_name} 자동 시작 실패: {result.get('error')}"
                            )
                    except Exception as e:
                        logger.error(f"❌ {process_name} 자동 시작 중 오류: {e}")

                # UI 업데이트 (메인 스레드에서)
                def update_ui():
                    if started_count > 0:
                        logger.info(
                            f"필수 서비스 {started_count}/{len(essential_processes)}개 자동 시작 완료"
                        )
                        # 포트 파일이 생성되었을 수 있으므로 Tier2 모니터 재초기화
                        if started_count > 0:
                            # 백엔드가 시작되고 포트 파일이 생성될 시간을 주기 위해 재초기화
                            tier2_reconnect_delay = TimingConfig.get(
                                "gui.tier2_reconnect_delay", 3000
                            )
                            QTimer.singleShot(
                                tier2_reconnect_delay, self._reinitialize_tier2_monitor
                            )
                            # 재초기화 후 새로고침
                            tier2_refresh_delay = TimingConfig.get(
                                "gui.tier2_refresh_delay", 5000
                            )
                            QTimer.singleShot(tier2_refresh_delay, self.refresh_all)
                    self._update_process_status_table()

                QTimer.singleShot(0, update_ui)

            threading.Thread(target=run_auto_start, daemon=True).start()

        def _reinitialize_tier2_monitor(self):
            """Tier2 모니터 재초기화 (포트 파일 생성 후)"""
            try:
                from gui.monitors import get_default_backend_url
                from pathlib import Path

                # 포트 파일이 생성되었는지 확인
                # 경로 계산: gui/app.py -> gui -> cointicker -> cointicker/config
                current_file = Path(__file__)
                config_dir = current_file.parent.parent / "config"
                port_file = config_dir / ".backend_port"

                if not port_file.exists():
                    logger.warning(
                        "포트 파일이 아직 생성되지 않았습니다. 2초 후 다시 시도합니다."
                    )
                    # 2초 후 다시 시도
                    tier2_reconnect_delay = TimingConfig.get(
                        "gui.tier2_reconnect_delay", 3000
                    )
                    QTimer.singleShot(
                        tier2_reconnect_delay, self._reinitialize_tier2_monitor
                    )
                    return

                port_str = port_file.read_text().strip()
                logger.info(f"포트 파일 발견: {port_str}")

                current_url = get_default_backend_url()
                logger.info(f"Tier2 모니터 재초기화: 현재 URL = {current_url}")

                if self.tier2_monitor:
                    if self.tier2_monitor.base_url != current_url:
                        logger.info(
                            f"Tier2 모니터 포트 업데이트: {self.tier2_monitor.base_url} -> {current_url}"
                        )
                    else:
                        logger.info(
                            f"Tier2 모니터 포트가 이미 올바릅니다: {current_url}"
                        )

                self.tier2_monitor = Tier2Monitor(base_url=current_url)
                if hasattr(self, "tier2_url_edit"):
                    self.tier2_url_edit.setText(current_url)

                logger.info(f"Tier2 모니터 재초기화 완료: {current_url}")
            except Exception as e:
                logger.error(f"Tier2 모니터 재초기화 실패: {e}")

        def start_all_processes(self):
            """전체 프로세스 시작"""
            if not self.pipeline_orchestrator:
                QMessageBox.warning(
                    self, "경고", "파이프라인 오케스트레이터가 초기화되지 않았습니다."
                )
                return

            if hasattr(self, "control_tab"):
                self.control_tab.control_log.append("🚀 전체 프로세스 시작 중...")
                self.control_tab.start_all_btn.setEnabled(False)

            def run_start():
                result = self.pipeline_orchestrator.start_all()

                # 메인 스레드에서 UI 업데이트
                def update_ui():
                    if hasattr(self, "control_tab"):
                        self.control_tab.start_all_btn.setEnabled(True)

                    if result.get("success"):
                        if hasattr(self, "control_tab"):
                            self.control_tab.control_log.append(
                                f"✅ 전체 프로세스 시작 완료 ({result.get('started')}/{result.get('total')}개)"
                            )
                        QMessageBox.information(
                            self,
                            "성공",
                            f"전체 프로세스 시작 완료!\n\n시작된 프로세스: {result.get('started')}/{result.get('total')}개",
                        )
                    else:
                        if hasattr(self, "control_tab"):
                            self.control_tab.control_log.append(
                                f"❌ 일부 프로세스 시작 실패"
                            )
                        QMessageBox.warning(
                            self,
                            "경고",
                            "일부 프로세스 시작에 실패했습니다.\n로그를 확인하세요.",
                        )

                    # 프로세스 상태 테이블 업데이트
                    self._update_process_status_table()

                # 메인 스레드에서 실행
                QTimer.singleShot(0, update_ui)

            threading.Thread(target=run_start, daemon=True).start()

        def stop_all_processes(self):
            """전체 프로세스 중지"""
            if not self.pipeline_orchestrator or self.pipeline_orchestrator is None:
                QMessageBox.warning(
                    self, "경고", "파이프라인 오케스트레이터가 초기화되지 않았습니다."
                )
                return

            reply = QMessageBox.question(
                self,
                "확인",
                "모든 프로세스를 중지하시겠습니까?",
                QMessageBox.Yes | QMessageBox.No,
            )

            if reply == QMessageBox.No:
                return

            if hasattr(self, "control_tab"):
                self.control_tab.control_log.append("⏹️ 전체 프로세스 중지 중...")
                self.control_tab.stop_all_btn.setEnabled(False)

            def run_stop():
                result = self.pipeline_orchestrator.stop_all()

                # 메인 스레드에서 UI 업데이트
                def update_ui():
                    if hasattr(self, "control_tab"):
                        self.control_tab.stop_all_btn.setEnabled(True)

                    if result.get("success"):
                        if hasattr(self, "control_tab"):
                            self.control_tab.control_log.append(
                                f"✅ 전체 프로세스 중지 완료 ({result.get('stopped')}/{result.get('total')}개)"
                            )
                        QMessageBox.information(
                            self, "성공", "전체 프로세스 중지 완료!"
                        )
                    else:
                        if hasattr(self, "control_tab"):
                            self.control_tab.control_log.append(
                                f"❌ 일부 프로세스 중지 실패"
                            )
                        QMessageBox.warning(
                            self, "경고", "일부 프로세스 중지에 실패했습니다."
                        )

                    # 프로세스 상태 테이블 업데이트
                    self._update_process_status_table()

                # 메인 스레드에서 실행
                QTimer.singleShot(0, update_ui)

            threading.Thread(target=run_stop, daemon=True).start()

        def restart_all_processes(self):
            """전체 프로세스 재시작"""
            if not self.pipeline_orchestrator or self.pipeline_orchestrator is None:
                QMessageBox.warning(
                    self, "경고", "파이프라인 오케스트레이터가 초기화되지 않았습니다."
                )
                return

            if hasattr(self, "control_tab"):
                self.control_tab.control_log.append("🔄 전체 프로세스 재시작 중...")
                self.control_tab.restart_all_btn.setEnabled(False)

            def run_restart():
                # 먼저 중지
                stop_result = self.pipeline_orchestrator.stop_all()
                time.sleep(2)
                # 그 다음 시작
                start_result = self.pipeline_orchestrator.start_all()

                # 메인 스레드에서 UI 업데이트
                def update_ui():
                    if hasattr(self, "control_tab"):
                        self.control_tab.restart_all_btn.setEnabled(True)

                    if start_result.get("success"):
                        if hasattr(self, "control_tab"):
                            self.control_tab.control_log.append(
                                f"✅ 전체 프로세스 재시작 완료"
                            )
                        QMessageBox.information(
                            self, "성공", "전체 프로세스 재시작 완료!"
                        )
                    else:
                        if hasattr(self, "control_tab"):
                            self.control_tab.control_log.append(
                                f"❌ 재시작 중 일부 프로세스 실패"
                            )
                        QMessageBox.warning(
                            self, "경고", "재시작 중 일부 프로세스에 실패했습니다."
                        )

                    # 프로세스 상태 테이블 업데이트
                    self._update_process_status_table()

                # 메인 스레드에서 실행
                QTimer.singleShot(0, update_ui)

            threading.Thread(target=run_restart, daemon=True).start()

        def _update_process_status_table(self):
            """프로세스 상태 테이블 업데이트"""
            if not self.pipeline_orchestrator or self.pipeline_orchestrator is None:
                return

            try:
                status = self.pipeline_orchestrator.get_status()
                if status is None:
                    return

                if not isinstance(status, dict):
                    logger.warning(
                        f"프로세스 상태가 딕셔너리가 아닙니다: {type(status)}"
                    )
                    return

                process_table = (
                    self.control_tab.process_status_table
                    if hasattr(self, "control_tab")
                    else None
                )
                if not process_table:
                    return
                process_table.setRowCount(len(status))

                for i, (process_name, info) in enumerate(status.items()):
                    # info가 딕셔너리가 아니면 건너뛰기
                    if not isinstance(info, dict):
                        logger.warning(
                            f"프로세스 정보가 딕셔너리가 아닙니다: {process_name}, {type(info)}"
                        )
                        continue

                    # 프로세스 이름
                    process_table.setItem(i, 0, QTableWidgetItem(str(process_name)))

                    # 상태
                    status_text = info.get("status", "stopped")
                    # ProcessStatus Enum인 경우 value 추출
                    if hasattr(status_text, "value"):
                        status_text = status_text.value
                    elif not isinstance(status_text, str):
                        status_text = str(status_text)

                    # 상태 표시 텍스트 변환
                    display_text = {
                        "running": "실행 중",
                        "starting": "시작 중",
                        "stopping": "중지 중",
                        "stopped": "중지됨",
                        "error": "오류",
                    }.get(status_text, status_text)

                    status_item = QTableWidgetItem(display_text)
                    if status_text == "running":
                        status_item.setForeground(Qt.green)
                    elif status_text == "starting":
                        status_item.setForeground(Qt.blue)  # 시작 중은 파란색
                    elif status_text == "error":
                        status_item.setForeground(Qt.red)
                    else:
                        status_item.setForeground(Qt.gray)
                    process_table.setItem(i, 1, status_item)

                    # 시작 시간
                    start_time = info.get("start_time")
                    if start_time and isinstance(start_time, str) and start_time != "-":
                        start_time_str = (
                            start_time[:19] if len(start_time) > 19 else start_time
                        )
                    else:
                        start_time_str = "-"
                    process_table.setItem(
                        i,
                        2,
                        QTableWidgetItem(start_time_str),
                    )

                    # 동작 버튼
                    action_widget = QWidget()
                    action_layout = QHBoxLayout()
                    action_layout.setContentsMargins(2, 2, 2, 2)

                    if status_text == "running":
                        stop_btn = QPushButton("중지")
                        stop_btn.setMaximumWidth(60)
                        stop_btn.clicked.connect(
                            lambda checked, pn=process_name: self._stop_single_process(
                                pn
                            )
                        )
                        action_layout.addWidget(stop_btn)
                    elif status_text == "starting":
                        # 시작 중일 때는 버튼 비활성화
                        wait_label = QLabel("대기 중...")
                        wait_label.setStyleSheet("color: blue;")
                        action_layout.addWidget(wait_label)
                    else:
                        start_btn = QPushButton("시작")
                        start_btn.setMaximumWidth(60)
                        start_btn.clicked.connect(
                            lambda checked, pn=process_name: self._start_single_process(
                                pn
                            )
                        )
                        action_layout.addWidget(start_btn)

                    action_widget.setLayout(action_layout)
                    process_table.setCellWidget(i, 3, action_widget)

                process_table.resizeColumnsToContents()
            except Exception as e:
                logger.error(f"프로세스 상태 테이블 업데이트 오류: {e}")

        def _start_single_process(self, process_name: str):
            """개별 프로세스 시작"""
            if not self.pipeline_orchestrator or self.pipeline_orchestrator is None:
                return

            if hasattr(self, "control_tab"):
                self.control_tab.control_log.append(f"▶️ {process_name} 시작 중...")
            result = self.pipeline_orchestrator.start_process(process_name, wait=True)

            if result.get("success"):
                if hasattr(self, "control_tab"):
                    self.control_tab.control_log.append(f"✅ {process_name} 시작 완료")
            else:
                if hasattr(self, "control_tab"):
                    self.control_tab.control_log.append(
                        f"❌ {process_name} 시작 실패: {result.get('error')}"
                    )

            self._update_process_status_table()

        def _stop_single_process(self, process_name: str):
            """개별 프로세스 중지"""
            if not self.pipeline_orchestrator or self.pipeline_orchestrator is None:
                return

            if hasattr(self, "control_tab"):
                self.control_tab.control_log.append(f"⏹️ {process_name} 중지 중...")
            result = self.pipeline_orchestrator.stop_process(process_name)

            if result.get("success"):
                if hasattr(self, "control_tab"):
                    self.control_tab.control_log.append(f"✅ {process_name} 중지 완료")
            else:
                if hasattr(self, "control_tab"):
                    self.control_tab.control_log.append(
                        f"❌ {process_name} 중지 실패: {result.get('error')}"
                    )

            self._update_process_status_table()

        def closeEvent(self, event):
            """종료 이벤트"""
            if self.cluster_monitor:
                self.cluster_monitor.close()
            event.accept()

    def main():
        """메인 함수"""
        app = QApplication(sys.argv)
        app.setApplicationName("CoinTicker")

        window = MainApplication()
        window.show()

        sys.exit(app.exec_())

elif TKINTER_AVAILABLE:
    # PyQt5가 없을 때는 기존 tkinter 버전 사용
    def main():
        """메인 함수 (tkinter fallback)"""
        from gui.dashboard import main as tkinter_main

        tkinter_main()

else:
    # GUI가 모두 없을 때는 CLI 모드로 실행
    def main():
        """메인 함수 (CLI 모드)"""
        print("=" * 60)
        print("CoinTicker 통합 관리 시스템")
        print("=" * 60)
        print("\nGUI 라이브러리가 설치되지 않았습니다.")
        print("\n설치 방법:")
        print("  1. PyQt5 설치 (권장):")
        print("     pip install PyQt5")
        print("\n  2. 또는 tkinter 설치 (macOS):")
        print("     brew install python-tk")
        print("\n  3. 또는 CLI 설치 마법사 사용:")
        print("     python gui/installer/installer_cli.py")
        print("\n  4. 또는 자동 설치 스크립트 사용:")
        print("     bash gui/scripts/install.sh")
        print("\n" + "=" * 60)

        # CLI 설치 마법사 실행 제안
        try:
            response = (
                input("\nCLI 설치 마법사를 실행하시겠습니까? [Y/n]: ").strip().lower()
            )
            if not response or response in ["y", "yes", "예", "ㅇ"]:
                from gui.installer.installer_cli import main as cli_main

                cli_main()
        except KeyboardInterrupt:
            print("\n취소되었습니다.")
        except Exception as e:
            print(f"\n오류: {e}")


if __name__ == "__main__":
    main()
