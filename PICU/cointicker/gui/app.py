"""
엔터프라이즈급 GUI 애플리케이션
모든 모듈을 통합하는 메인 애플리케이션
"""

import sys
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

            # 자동 새로고침
            self.auto_refresh_timer = QTimer()
            self.auto_refresh_timer.timeout.connect(self.refresh_all)
            self.auto_refresh_enabled = False

            # UI 초기화
            self._init_ui()
            self._load_config()
            self._load_modules()

            # 초기 데이터 로드
            QTimer.singleShot(1000, self.refresh_all)

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

            # 로그
            self.control_log = QTextEdit()
            self.control_log.setReadOnly(True)
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

            result = self.module_manager.execute_command(
                "SpiderModule",
                "start_spider",
                {"spider_name": spider, "host": host if host else None},
            )

            self.control_log.append(f"Spider 시작: {spider} @ {host or '로컬'}")
            self.control_log.append(str(result))

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
