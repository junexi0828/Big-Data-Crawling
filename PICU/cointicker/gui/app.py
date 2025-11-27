"""
엔터프라이즈급 GUI 애플리케이션
모든 모듈을 통합하는 메인 애플리케이션
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
    )
    from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject
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
    from gui.cluster_monitor import ClusterMonitor
    from gui.tier2_monitor import Tier2Monitor
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
            self.stats_timer.start(2000)  # 2초마다 업데이트

            # UI 초기화
            self._init_ui()
            self._load_config()
            self._load_modules()

            # 초기 데이터 로드
            QTimer.singleShot(1000, self.refresh_all)

            # 프로세스 상태 테이블 초기 업데이트
            QTimer.singleShot(2000, self._update_process_status_table)

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

            # 탭 생성
            self._create_dashboard_tab()
            self._create_cluster_tab()
            self._create_tier2_tab()
            self._create_modules_tab()
            self._create_control_tab()
            self._create_config_tab()

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

        def _create_dashboard_tab(self):
            """대시보드 탭 생성"""
            tab = QWidget()
            layout = QVBoxLayout()

            # 요약 정보
            summary_label = QLabel("시스템 요약")
            summary_label.setFont(QFont("Arial", 12, QFont.Bold))
            layout.addWidget(summary_label)

            self.summary_text = QTextEdit()
            self.summary_text.setReadOnly(True)
            layout.addWidget(self.summary_text)

            tab.setLayout(layout)
            self.tabs.addTab(tab, "대시보드")

        def _create_cluster_tab(self):
            """클러스터 모니터링 탭 생성"""
            tab = QWidget()
            layout = QVBoxLayout()

            # 버튼
            button_layout = QHBoxLayout()
            refresh_btn = QPushButton("새로고침")
            refresh_btn.clicked.connect(self.refresh_cluster)
            button_layout.addWidget(refresh_btn)

            hdfs_btn = QPushButton("HDFS 상태")
            hdfs_btn.clicked.connect(self.show_hdfs_status)
            button_layout.addWidget(hdfs_btn)

            button_layout.addStretch()
            layout.addLayout(button_layout)

            # 노드 테이블
            self.cluster_table = QTableWidget()
            self.cluster_table.setColumnCount(7)
            self.cluster_table.setHorizontalHeaderLabels(
                ["호스트", "상태", "CPU", "메모리", "디스크", "Hadoop", "Scrapy"]
            )
            layout.addWidget(self.cluster_table)

            tab.setLayout(layout)
            self.tabs.addTab(tab, "클러스터")

        def _create_tier2_tab(self):
            """Tier2 서버 탭 생성"""
            tab = QWidget()
            layout = QVBoxLayout()

            # 버튼
            button_layout = QHBoxLayout()
            refresh_btn = QPushButton("새로고침")
            refresh_btn.clicked.connect(self.refresh_tier2)
            button_layout.addWidget(refresh_btn)

            insights_btn = QPushButton("인사이트 생성")
            insights_btn.clicked.connect(self.generate_insights)
            button_layout.addWidget(insights_btn)

            button_layout.addStretch()
            layout.addLayout(button_layout)

            # 상태 텍스트
            self.tier2_status_text = QTextEdit()
            self.tier2_status_text.setReadOnly(True)
            layout.addWidget(self.tier2_status_text)

            tab.setLayout(layout)
            self.tabs.addTab(tab, "Tier2 서버")

        def _create_modules_tab(self):
            """모듈 관리 탭 생성"""
            tab = QWidget()
            layout = QVBoxLayout()

            # 버튼
            button_layout = QHBoxLayout()
            load_btn = QPushButton("모듈 로드")
            load_btn.clicked.connect(self.load_modules)
            button_layout.addWidget(load_btn)

            refresh_btn = QPushButton("상태 새로고침")
            refresh_btn.clicked.connect(self.refresh_modules)
            button_layout.addWidget(refresh_btn)

            button_layout.addStretch()
            layout.addLayout(button_layout)

            # 모듈 테이블
            self.modules_table = QTableWidget()
            self.modules_table.setColumnCount(3)
            self.modules_table.setHorizontalHeaderLabels(["모듈 이름", "상태", "설정"])
            layout.addWidget(self.modules_table)

            tab.setLayout(layout)
            self.tabs.addTab(tab, "모듈 관리")

        def _create_control_tab(self):
            """제어 탭 생성"""
            tab = QWidget()
            layout = QVBoxLayout()

            # 통합 제어 섹션
            integrated_group = QWidget()
            integrated_layout = QVBoxLayout()

            integrated_label = QLabel("🚀 통합 파이프라인 제어")
            integrated_label.setFont(QFont("Arial", 12, QFont.Bold))
            integrated_layout.addWidget(integrated_label)

            integrated_btn_layout = QHBoxLayout()
            self.start_all_btn = QPushButton("▶️ 전체 시작")
            self.start_all_btn.setStyleSheet(
                "background-color: #4CAF50; color: white; font-weight: bold; padding: 10px;"
            )
            self.start_all_btn.clicked.connect(self.start_all_processes)
            integrated_btn_layout.addWidget(self.start_all_btn)

            self.stop_all_btn = QPushButton("⏹️ 전체 중지")
            self.stop_all_btn.setStyleSheet(
                "background-color: #f44336; color: white; font-weight: bold; padding: 10px;"
            )
            self.stop_all_btn.clicked.connect(self.stop_all_processes)
            integrated_btn_layout.addWidget(self.stop_all_btn)

            self.restart_all_btn = QPushButton("🔄 전체 재시작")
            self.restart_all_btn.setStyleSheet(
                "background-color: #2196F3; color: white; font-weight: bold; padding: 10px;"
            )
            self.restart_all_btn.clicked.connect(self.restart_all_processes)
            integrated_btn_layout.addWidget(self.restart_all_btn)

            integrated_btn_layout.addStretch()
            integrated_layout.addLayout(integrated_btn_layout)

            # 프로세스 상태 표시
            self.process_status_table = QTableWidget()
            self.process_status_table.setColumnCount(4)
            self.process_status_table.setHorizontalHeaderLabels(
                ["프로세스", "상태", "시작 시간", "동작"]
            )
            self.process_status_table.setMaximumHeight(200)
            integrated_layout.addWidget(self.process_status_table)

            integrated_group.setLayout(integrated_layout)
            layout.addWidget(integrated_group)

            # 구분선
            line = QWidget()
            line.setFixedHeight(2)
            line.setStyleSheet("background-color: #ccc;")
            layout.addWidget(line)

            # 개별 제어 섹션
            individual_label = QLabel("개별 프로세스 제어")
            individual_label.setFont(QFont("Arial", 10, QFont.Bold))
            layout.addWidget(individual_label)

            # Spider 제어
            spider_group = QWidget()
            spider_layout = QVBoxLayout()

            host_layout = QHBoxLayout()
            host_layout.addWidget(QLabel("호스트:"))
            self.host_combo = QComboBox()
            host_layout.addWidget(self.host_combo)
            spider_layout.addLayout(host_layout)

            spider_layout2 = QHBoxLayout()
            spider_layout2.addWidget(QLabel("Spider:"))
            self.spider_combo = QComboBox()
            self.spider_combo.addItems(
                [
                    "upbit_trends",
                    "coinness",
                    "saveticker",
                    "perplexity",
                    "cnn_fear_greed",
                ]
            )
            spider_layout2.addWidget(self.spider_combo)
            spider_layout.addLayout(spider_layout2)

            button_layout = QHBoxLayout()
            start_btn = QPushButton("Spider 시작")
            start_btn.clicked.connect(self.start_spider)
            button_layout.addWidget(start_btn)

            stop_btn = QPushButton("Spider 중지")
            stop_btn.clicked.connect(self.stop_spider)
            button_layout.addWidget(stop_btn)

            pipeline_btn = QPushButton("파이프라인 재시작")
            pipeline_btn.clicked.connect(self.restart_pipeline)
            button_layout.addWidget(pipeline_btn)

            spider_layout.addLayout(button_layout)
            spider_group.setLayout(spider_layout)
            layout.addWidget(spider_group)

            # 실시간 모니터링 섹션
            monitor_label = QLabel("실시간 모니터링")
            monitor_label.setFont(QFont("Arial", 10, QFont.Bold))
            layout.addWidget(monitor_label)

            # 통계 표시
            stats_layout = QHBoxLayout()
            self.spider_stats_label = QLabel("Spider: 대기 중")
            self.kafka_stats_label = QLabel("Kafka: 대기 중")
            self.backend_stats_label = QLabel("Backend: 대기 중")
            stats_layout.addWidget(self.spider_stats_label)
            stats_layout.addWidget(self.kafka_stats_label)
            stats_layout.addWidget(self.backend_stats_label)
            stats_layout.addStretch()
            layout.addLayout(stats_layout)

            # 로그
            log_label = QLabel("실시간 로그")
            log_label.setFont(QFont("Arial", 10, QFont.Bold))
            layout.addWidget(log_label)

            self.control_log = QTextEdit()
            self.control_log.setReadOnly(True)
            self.control_log.setStyleSheet(
                "background-color: #1e1e1e; color: #d4d4d4; font-family: 'Courier New', monospace;"
            )
            layout.addWidget(self.control_log)

            tab.setLayout(layout)
            self.tabs.addTab(tab, "제어")

        def _create_config_tab(self):
            """설정 탭 생성"""
            tab = QWidget()
            layout = QVBoxLayout()

            # Tier2 URL 설정
            url_layout = QHBoxLayout()
            url_layout.addWidget(QLabel("Tier2 서버 URL:"))
            self.tier2_url_edit = QLineEdit("http://localhost:5000")
            url_layout.addWidget(self.tier2_url_edit)

            url_apply_btn = QPushButton("적용")
            url_apply_btn.clicked.connect(self.update_tier2_url)
            url_layout.addWidget(url_apply_btn)

            layout.addLayout(url_layout)

            # 설정 텍스트
            self.config_text = QTextEdit()
            self.config_text.setReadOnly(True)
            layout.addWidget(self.config_text)

            tab.setLayout(layout)
            self.tabs.addTab(tab, "설정")

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
                tier2_url = self.config_manager.get_config(
                    "gui", "tier2.base_url", "http://localhost:5000"
                )
                self.tier2_monitor = Tier2Monitor(base_url=tier2_url)
                self.tier2_url_edit.setText(tier2_url)

        def _load_modules(self):
            """모듈 로드"""
            mapping_file = Path("gui/module_mapping.json")
            if mapping_file.exists():
                self.module_manager.load_module_mapping(str(mapping_file))

                # 모듈 초기화
                for module_name in self.module_manager.modules:
                    config = self.config_manager.get_config("gui", default={})
                    self.module_manager.initialize_module(module_name, config)

            # 파이프라인 오케스트레이터 초기화
            from gui.modules.pipeline_orchestrator import PipelineOrchestrator

            self.pipeline_orchestrator = PipelineOrchestrator()
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
            self.refresh_cluster()
            self.refresh_tier2()
            self.refresh_modules()
            self.update_summary()

        def refresh_cluster(self):
            """클러스터 상태 새로고침"""
            if not self.cluster_monitor:
                return

            self.statusBar().showMessage("클러스터 상태 확인 중...")

            try:
                nodes = self.cluster_monitor.get_all_nodes_status()

                self.cluster_table.setRowCount(len(nodes))
                for i, node in enumerate(nodes):
                    self.cluster_table.setItem(
                        i, 0, QTableWidgetItem(node.get("host", "N/A"))
                    )
                    self.cluster_table.setItem(
                        i,
                        1,
                        QTableWidgetItem(
                            "온라인" if node.get("online") else "오프라인"
                        ),
                    )
                    self.cluster_table.setItem(
                        i,
                        2,
                        QTableWidgetItem(
                            f"{node.get('cpu_usage', 0):.1f}%"
                            if node.get("cpu_usage")
                            else "N/A"
                        ),
                    )
                    self.cluster_table.setItem(
                        i,
                        3,
                        QTableWidgetItem(
                            f"{node.get('memory_usage', 0):.1f}%"
                            if node.get("memory_usage")
                            else "N/A"
                        ),
                    )
                    self.cluster_table.setItem(
                        i,
                        4,
                        QTableWidgetItem(
                            f"{node.get('disk_usage', 0):.1f}%"
                            if node.get("disk_usage")
                            else "N/A"
                        ),
                    )
                    self.cluster_table.setItem(
                        i, 5, QTableWidgetItem(str(node.get("hadoop_status", "N/A")))
                    )
                    self.cluster_table.setItem(
                        i, 6, QTableWidgetItem(str(node.get("scrapy_status", "N/A")))
                    )

                self.statusBar().showMessage("클러스터 상태 업데이트 완료", 3000)
            except Exception as e:
                logger.error(f"클러스터 새로고침 실패: {e}")
                self.statusBar().showMessage(f"오류: {str(e)}", 5000)

        def refresh_tier2(self):
            """Tier2 서버 상태 새로고침"""
            if not self.tier2_monitor:
                return

            self.statusBar().showMessage("Tier2 서버 상태 확인 중...")

            try:
                status = self.tier2_monitor.get_server_status()
                summary = self.tier2_monitor.get_dashboard_summary()

                import json

                status_text = json.dumps(status, indent=2, ensure_ascii=False)
                if summary and summary.get("success"):
                    status_text += "\n\n=== 대시보드 요약 ===\n"
                    status_text += json.dumps(
                        summary.get("data", {}), indent=2, ensure_ascii=False
                    )

                self.tier2_status_text.setPlainText(status_text)
                self.statusBar().showMessage("Tier2 서버 상태 업데이트 완료", 3000)
            except Exception as e:
                logger.error(f"Tier2 새로고침 실패: {e}")
                self.statusBar().showMessage(f"오류: {str(e)}", 5000)

        def refresh_modules(self):
            """모듈 상태 새로고침"""
            modules = self.module_manager.get_all_modules_status()

            self.modules_table.setRowCount(len(modules))
            for i, module in enumerate(modules):
                self.modules_table.setItem(
                    i, 0, QTableWidgetItem(module.get("name", "N/A"))
                )
                self.modules_table.setItem(
                    i, 1, QTableWidgetItem(module.get("status", "N/A"))
                )
                self.modules_table.setItem(
                    i, 2, QTableWidgetItem(str(len(module.get("config", {}))))
                )

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

            self.summary_text.setPlainText(summary)

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
                self.control_log.append(f"[{timestamp}] [{log_type.upper()}] {message}")

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
                self.control_log.append(
                    f"✅ Spider 시작: {spider} @ {host or '로컬'} (PID: {result.get('pid')})"
                )
                # 실시간 통계 업데이트 시작
                self._start_stats_refresh()
            else:
                self.control_log.append(
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

            self.control_log.append(f"Spider 중지: {spider} @ {host or '로컬'}")
            self.control_log.append(str(result))

        def restart_pipeline(self):
            """파이프라인 재시작"""
            host = self.host_combo.currentText()

            result = self.module_manager.execute_command(
                "PipelineModule", "run_full_pipeline", {"host": host if host else None}
            )

            self.control_log.append(f"파이프라인 재시작: {host or '로컬'}")
            self.control_log.append(str(result))

        def show_hdfs_status(self):
            """HDFS 상태 표시"""
            if not self.cluster_monitor:
                return

            status = self.cluster_monitor.get_hdfs_status()
            QMessageBox.information(
                self, "HDFS 상태", status.get("report", "상태를 가져올 수 없습니다.")
            )

        def generate_insights(self):
            """인사이트 생성"""
            if not self.tier2_monitor:
                return

            result = self.tier2_monitor.generate_insights()
            if result.get("success"):
                QMessageBox.information(self, "성공", "인사이트 생성이 완료되었습니다.")
            else:
                QMessageBox.warning(
                    self,
                    "실패",
                    f"인사이트 생성 실패: {result.get('error', '알 수 없는 오류')}",
                )

        def update_tier2_url(self):
            """Tier2 URL 업데이트"""
            url = self.tier2_url_edit.text()
            self.tier2_monitor = Tier2Monitor(base_url=url)
            self.config_manager.set_config("gui", "tier2.base_url", url)
            QMessageBox.information(
                self, "완료", f"Tier2 서버 URL이 업데이트되었습니다: {url}"
            )

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
                        self.spider_stats_label.setText(
                            f"Spider ({spider_name}): 아이템 {items}개, 에러 {errors}개"
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
                        self.spider_stats_label.setText(
                            f"Spider: 실행 중 {running}개, 총 아이템 {total_items}개"
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
                    self.kafka_stats_label.setText(
                        f"Kafka: {status_text}, 처리 {processed}개, 에러 {errors}개"
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
                    self.backend_stats_label.setText(f"Backend: 온라인, DB {db_status}")
                else:
                    self.backend_stats_label.setText("Backend: 오프라인")
            except Exception as e:
                logger.error(f"Backend 통계 업데이트 오류: {e}")

        def start_all_processes(self):
            """전체 프로세스 시작"""
            if not self.pipeline_orchestrator:
                QMessageBox.warning(
                    self, "경고", "파이프라인 오케스트레이터가 초기화되지 않았습니다."
                )
                return

            self.control_log.append("🚀 전체 프로세스 시작 중...")
            self.start_all_btn.setEnabled(False)

            def run_start():
                result = self.pipeline_orchestrator.start_all()
                self.start_all_btn.setEnabled(True)

                if result.get("success"):
                    self.control_log.append(
                        f"✅ 전체 프로세스 시작 완료 ({result.get('started')}/{result.get('total')}개)"
                    )
                    QMessageBox.information(
                        self,
                        "성공",
                        f"전체 프로세스 시작 완료!\n\n시작된 프로세스: {result.get('started')}/{result.get('total')}개",
                    )
                else:
                    self.control_log.append(f"❌ 일부 프로세스 시작 실패")
                    QMessageBox.warning(
                        self,
                        "경고",
                        "일부 프로세스 시작에 실패했습니다.\n로그를 확인하세요.",
                    )

                # 프로세스 상태 테이블 업데이트
                self._update_process_status_table()

            threading.Thread(target=run_start, daemon=True).start()

        def stop_all_processes(self):
            """전체 프로세스 중지"""
            if not self.pipeline_orchestrator:
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

            self.control_log.append("⏹️ 전체 프로세스 중지 중...")
            self.stop_all_btn.setEnabled(False)

            def run_stop():
                result = self.pipeline_orchestrator.stop_all()
                self.stop_all_btn.setEnabled(True)

                if result.get("success"):
                    self.control_log.append(
                        f"✅ 전체 프로세스 중지 완료 ({result.get('stopped')}/{result.get('total')}개)"
                    )
                    QMessageBox.information(self, "성공", "전체 프로세스 중지 완료!")
                else:
                    self.control_log.append(f"❌ 일부 프로세스 중지 실패")
                    QMessageBox.warning(
                        self, "경고", "일부 프로세스 중지에 실패했습니다."
                    )

                # 프로세스 상태 테이블 업데이트
                self._update_process_status_table()

            threading.Thread(target=run_stop, daemon=True).start()

        def restart_all_processes(self):
            """전체 프로세스 재시작"""
            if not self.pipeline_orchestrator:
                QMessageBox.warning(
                    self, "경고", "파이프라인 오케스트레이터가 초기화되지 않았습니다."
                )
                return

            self.control_log.append("🔄 전체 프로세스 재시작 중...")
            self.restart_all_btn.setEnabled(False)

            def run_restart():
                # 먼저 중지
                stop_result = self.pipeline_orchestrator.stop_all()
                time.sleep(2)
                # 그 다음 시작
                start_result = self.pipeline_orchestrator.start_all()
                self.restart_all_btn.setEnabled(True)

                if start_result.get("success"):
                    self.control_log.append(f"✅ 전체 프로세스 재시작 완료")
                    QMessageBox.information(self, "성공", "전체 프로세스 재시작 완료!")
                else:
                    self.control_log.append(f"❌ 재시작 중 일부 프로세스 실패")
                    QMessageBox.warning(
                        self, "경고", "재시작 중 일부 프로세스에 실패했습니다."
                    )

                # 프로세스 상태 테이블 업데이트
                self._update_process_status_table()

            threading.Thread(target=run_restart, daemon=True).start()

        def _update_process_status_table(self):
            """프로세스 상태 테이블 업데이트"""
            if not self.pipeline_orchestrator:
                return

            try:
                status = self.pipeline_orchestrator.get_status()
                self.process_status_table.setRowCount(len(status))

                for i, (process_name, info) in enumerate(status.items()):
                    # 프로세스 이름
                    self.process_status_table.setItem(
                        i, 0, QTableWidgetItem(process_name)
                    )

                    # 상태
                    status_text = info.get("status", "stopped")
                    status_item = QTableWidgetItem(status_text)
                    if status_text == "running":
                        status_item.setForeground(Qt.green)
                    elif status_text == "error":
                        status_item.setForeground(Qt.red)
                    else:
                        status_item.setForeground(Qt.gray)
                    self.process_status_table.setItem(i, 1, status_item)

                    # 시작 시간
                    start_time = info.get("start_time", "-")
                    self.process_status_table.setItem(
                        i,
                        2,
                        QTableWidgetItem(start_time[:19] if start_time != "-" else "-"),
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
                    self.process_status_table.setCellWidget(i, 3, action_widget)

                self.process_status_table.resizeColumnsToContents()
            except Exception as e:
                logger.error(f"프로세스 상태 테이블 업데이트 오류: {e}")

        def _start_single_process(self, process_name: str):
            """개별 프로세스 시작"""
            if not self.pipeline_orchestrator:
                return

            self.control_log.append(f"▶️ {process_name} 시작 중...")
            result = self.pipeline_orchestrator.start_process(process_name, wait=True)

            if result.get("success"):
                self.control_log.append(f"✅ {process_name} 시작 완료")
            else:
                self.control_log.append(
                    f"❌ {process_name} 시작 실패: {result.get('error')}"
                )

            self._update_process_status_table()

        def _stop_single_process(self, process_name: str):
            """개별 프로세스 중지"""
            if not self.pipeline_orchestrator:
                return

            self.control_log.append(f"⏹️ {process_name} 중지 중...")
            result = self.pipeline_orchestrator.stop_process(process_name)

            if result.get("success"):
                self.control_log.append(f"✅ {process_name} 중지 완료")
            else:
                self.control_log.append(
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
        print("     bash gui/install.sh")
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
