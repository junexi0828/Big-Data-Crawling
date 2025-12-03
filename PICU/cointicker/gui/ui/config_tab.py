"""
설정 탭
애플리케이션 설정을 관리하는 탭
"""

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTabWidget,
    QScrollArea,
    QGroupBox,
    QFormLayout,
    QLabel,
    QTextEdit,
    QLineEdit,
    QSpinBox,
    QComboBox,
    QCheckBox,
    QMessageBox,
)
import yaml


class ConfigTab(QWidget):
    """설정 탭 클래스"""

    def __init__(self, parent=None):
        """
        초기화

        Args:
            parent: 부모 위젯 (MainApplication)
        """
        super().__init__(parent)
        self.parent_app = parent
        self._init_ui()

    def _init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout()

        # 설정 카테고리 탭
        config_tabs = QTabWidget()

        # GUI 설정 탭
        gui_tab = self._create_gui_config_tab()
        config_tabs.addTab(gui_tab, "GUI 설정")

        # 클러스터 설정 탭
        cluster_tab = self._create_cluster_config_tab()
        config_tabs.addTab(cluster_tab, "클러스터 설정")

        # 데이터베이스 설정 탭
        db_tab = self._create_database_config_tab()
        config_tabs.addTab(db_tab, "데이터베이스 설정")

        # Spider 설정 탭
        spider_tab = self._create_spider_config_tab()
        config_tabs.addTab(spider_tab, "Spider 설정")

        layout.addWidget(config_tabs)

        # 새로고침 버튼
        refresh_btn = QPushButton("설정 새로고침")
        refresh_btn.clicked.connect(self.refresh_config_display)
        layout.addWidget(refresh_btn)

        self.setLayout(layout)

    def _create_gui_config_tab(self):
        """GUI 설정 탭 생성"""
        tab = QWidget()
        layout = QVBoxLayout()
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()

        # Window 설정
        window_group = QGroupBox("윈도우 설정")
        window_layout = QFormLayout()

        self.window_width_spin = QSpinBox()
        self.window_width_spin.setRange(800, 4000)
        self.window_width_spin.setValue(1400)
        window_layout.addRow("너비:", self.window_width_spin)

        self.window_height_spin = QSpinBox()
        self.window_height_spin.setRange(600, 3000)
        self.window_height_spin.setValue(900)
        window_layout.addRow("높이:", self.window_height_spin)

        self.window_theme_combo = QComboBox()
        self.window_theme_combo.addItems(["default", "dark", "light"])
        window_layout.addRow("테마:", self.window_theme_combo)

        window_group.setLayout(window_layout)
        scroll_layout.addWidget(window_group)

        # Refresh 설정
        refresh_group = QGroupBox("새로고침 설정")
        refresh_layout = QFormLayout()

        self.auto_refresh_check = QCheckBox()
        refresh_layout.addRow("자동 새로고침:", self.auto_refresh_check)
        if self.parent_app and hasattr(self.parent_app, "toggle_auto_refresh"):
            self.auto_refresh_check.toggled.connect(self.parent_app.toggle_auto_refresh)

        self.refresh_interval_spin = QSpinBox()
        self.refresh_interval_spin.setRange(5, 3600)
        self.refresh_interval_spin.setSuffix(" 초")
        self.refresh_interval_spin.setValue(30)
        refresh_layout.addRow("새로고침 간격:", self.refresh_interval_spin)

        refresh_group.setLayout(refresh_layout)
        scroll_layout.addWidget(refresh_group)

        # Tier2 설정
        tier2_group = QGroupBox("Tier2 서버 설정")
        tier2_layout = QFormLayout()

        # 백엔드 포트 파일에서 우선 읽기
        from gui.monitors import get_default_backend_url

        default_url = get_default_backend_url()
        self.tier2_url_edit = QLineEdit(default_url)
        tier2_layout.addRow("서버 URL:", self.tier2_url_edit)

        self.tier2_timeout_spin = QSpinBox()
        self.tier2_timeout_spin.setRange(1, 60)
        self.tier2_timeout_spin.setSuffix(" 초")
        self.tier2_timeout_spin.setValue(5)
        tier2_layout.addRow("타임아웃:", self.tier2_timeout_spin)

        tier2_group.setLayout(tier2_layout)
        scroll_layout.addWidget(tier2_group)

        # Cluster 설정
        cluster_group = QGroupBox("클러스터 연결 설정")
        cluster_layout = QFormLayout()

        self.cluster_ssh_timeout_spin = QSpinBox()
        self.cluster_ssh_timeout_spin.setRange(1, 60)
        self.cluster_ssh_timeout_spin.setSuffix(" 초")
        self.cluster_ssh_timeout_spin.setValue(10)
        cluster_layout.addRow("SSH 타임아웃:", self.cluster_ssh_timeout_spin)

        self.cluster_retry_spin = QSpinBox()
        self.cluster_retry_spin.setRange(1, 10)
        self.cluster_retry_spin.setValue(3)
        cluster_layout.addRow("재시도 횟수:", self.cluster_retry_spin)

        cluster_group.setLayout(cluster_layout)
        scroll_layout.addWidget(cluster_group)

        # 자동 시작 설정
        auto_start_group = QGroupBox("자동 시작 설정")
        auto_start_layout = QVBoxLayout()

        self.auto_start_enabled_check = QCheckBox("GUI 시작 시 자동으로 프로세스 시작")
        self.auto_start_enabled_check.setChecked(True)
        auto_start_layout.addWidget(self.auto_start_enabled_check)

        # 자동 시작할 프로세스 선택
        processes_label = QLabel("자동 시작할 프로세스:")
        auto_start_layout.addWidget(processes_label)

        self.auto_start_backend_check = QCheckBox("Backend (백엔드 서버)")
        self.auto_start_backend_check.setChecked(True)
        auto_start_layout.addWidget(self.auto_start_backend_check)

        self.auto_start_frontend_check = QCheckBox("Frontend (프론트엔드 서버)")
        self.auto_start_frontend_check.setChecked(True)
        auto_start_layout.addWidget(self.auto_start_frontend_check)

        self.auto_start_spider_check = QCheckBox("Spider (웹 크롤러)")
        self.auto_start_spider_check.setChecked(False)
        auto_start_layout.addWidget(self.auto_start_spider_check)

        self.auto_start_kafka_check = QCheckBox("Kafka (메시지 큐)")
        self.auto_start_kafka_check.setChecked(False)
        auto_start_layout.addWidget(self.auto_start_kafka_check)

        self.auto_start_mapreduce_check = QCheckBox("MapReduce (데이터 처리)")
        self.auto_start_mapreduce_check.setChecked(False)
        auto_start_layout.addWidget(self.auto_start_mapreduce_check)

        auto_start_group.setLayout(auto_start_layout)
        scroll_layout.addWidget(auto_start_group)

        # systemd 서비스 설정
        systemd_group = QGroupBox("Systemd 서비스 설정 (백그라운드 실행)")
        systemd_layout = QVBoxLayout()

        systemd_info = QLabel(
            "systemd 서비스를 활성화하면 시스템 부팅 시 자동으로 프로세스가 시작됩니다.\n"
            "GUI 없이 백그라운드에서 실행되며, 장애 발생 시 자동으로 재시작됩니다."
        )
        systemd_info.setWordWrap(True)
        systemd_info.setStyleSheet("color: #666; font-size: 11px; padding: 5px;")
        systemd_layout.addWidget(systemd_info)

        # Tier 1 Orchestrator 서비스
        self.systemd_tier1_enabled_check = QCheckBox("Tier 1 오케스트레이터 서비스 활성화")
        self.systemd_tier1_enabled_check.setChecked(False)
        systemd_layout.addWidget(self.systemd_tier1_enabled_check)

        self.systemd_tier1_autostart_check = QCheckBox("  └─ 부팅 시 자동 시작")
        self.systemd_tier1_autostart_check.setChecked(False)
        self.systemd_tier1_autostart_check.setEnabled(False)
        self.systemd_tier1_enabled_check.toggled.connect(
            self.systemd_tier1_autostart_check.setEnabled
        )
        systemd_layout.addWidget(self.systemd_tier1_autostart_check)

        tier1_btn_layout = QHBoxLayout()
        self.tier1_install_btn = QPushButton("서비스 설치")
        self.tier1_install_btn.clicked.connect(
            lambda: self.install_systemd_service("tier1_orchestrator")
        )
        tier1_btn_layout.addWidget(self.tier1_install_btn)

        self.tier1_start_btn = QPushButton("서비스 시작")
        self.tier1_start_btn.clicked.connect(
            lambda: self.control_systemd_service("tier1_orchestrator", "start")
        )
        tier1_btn_layout.addWidget(self.tier1_start_btn)

        self.tier1_stop_btn = QPushButton("서비스 중지")
        self.tier1_stop_btn.clicked.connect(
            lambda: self.control_systemd_service("tier1_orchestrator", "stop")
        )
        tier1_btn_layout.addWidget(self.tier1_stop_btn)

        self.tier1_status_btn = QPushButton("상태 확인")
        self.tier1_status_btn.clicked.connect(
            lambda: self.check_systemd_service_status("tier1_orchestrator")
        )
        tier1_btn_layout.addWidget(self.tier1_status_btn)

        tier1_btn_layout.addStretch()
        systemd_layout.addLayout(tier1_btn_layout)

        # Tier 2 Scheduler 서비스
        self.systemd_tier2_enabled_check = QCheckBox("Tier 2 파이프라인 스케줄러 서비스 활성화")
        self.systemd_tier2_enabled_check.setChecked(False)
        systemd_layout.addWidget(self.systemd_tier2_enabled_check)

        self.systemd_tier2_autostart_check = QCheckBox("  └─ 부팅 시 자동 시작")
        self.systemd_tier2_autostart_check.setChecked(False)
        self.systemd_tier2_autostart_check.setEnabled(False)
        self.systemd_tier2_enabled_check.toggled.connect(
            self.systemd_tier2_autostart_check.setEnabled
        )
        systemd_layout.addWidget(self.systemd_tier2_autostart_check)

        tier2_btn_layout = QHBoxLayout()
        self.tier2_install_btn = QPushButton("서비스 설치")
        self.tier2_install_btn.clicked.connect(
            lambda: self.install_systemd_service("tier2_scheduler")
        )
        tier2_btn_layout.addWidget(self.tier2_install_btn)

        self.tier2_start_btn = QPushButton("서비스 시작")
        self.tier2_start_btn.clicked.connect(
            lambda: self.control_systemd_service("tier2_scheduler", "start")
        )
        tier2_btn_layout.addWidget(self.tier2_start_btn)

        self.tier2_stop_btn = QPushButton("서비스 중지")
        self.tier2_stop_btn.clicked.connect(
            lambda: self.control_systemd_service("tier2_scheduler", "stop")
        )
        tier2_btn_layout.addWidget(self.tier2_stop_btn)

        self.tier2_status_btn = QPushButton("상태 확인")
        self.tier2_status_btn.clicked.connect(
            lambda: self.check_systemd_service_status("tier2_scheduler")
        )
        tier2_btn_layout.addWidget(self.tier2_status_btn)

        tier2_btn_layout.addStretch()
        systemd_layout.addLayout(tier2_btn_layout)

        systemd_group.setLayout(systemd_layout)
        scroll_layout.addWidget(systemd_group)

        scroll_layout.addStretch()
        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)

        # 저장 버튼
        save_btn = QPushButton("GUI 설정 저장")
        save_btn.clicked.connect(self.save_gui_config)
        layout.addWidget(scroll)
        layout.addWidget(save_btn)

        tab.setLayout(layout)
        return tab

    def _create_cluster_config_tab(self):
        """클러스터 설정 탭 생성"""
        tab = QWidget()
        layout = QVBoxLayout()
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()

        # 설정 텍스트 (읽기 전용)
        config_label = QLabel("클러스터 설정 파일 내용:")
        scroll_layout.addWidget(config_label)

        self.cluster_config_text = QTextEdit()
        self.cluster_config_text.setReadOnly(True)
        scroll_layout.addWidget(self.cluster_config_text)

        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)

        # 새로고침 버튼
        refresh_btn = QPushButton("설정 새로고침")
        refresh_btn.clicked.connect(lambda: self.refresh_config_display("cluster"))
        layout.addWidget(scroll)
        layout.addWidget(refresh_btn)

        tab.setLayout(layout)
        return tab

    def _create_database_config_tab(self):
        """데이터베이스 설정 탭 생성"""
        tab = QWidget()
        layout = QVBoxLayout()
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()

        # 설정 텍스트 (읽기 전용)
        config_label = QLabel("데이터베이스 설정 파일 내용:")
        scroll_layout.addWidget(config_label)

        self.database_config_text = QTextEdit()
        self.database_config_text.setReadOnly(True)
        scroll_layout.addWidget(self.database_config_text)

        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)

        # 새로고침 버튼
        refresh_btn = QPushButton("설정 새로고침")
        refresh_btn.clicked.connect(lambda: self.refresh_config_display("database"))
        layout.addWidget(scroll)
        layout.addWidget(refresh_btn)

        tab.setLayout(layout)
        return tab

    def _create_spider_config_tab(self):
        """Spider 설정 탭 생성"""
        tab = QWidget()
        layout = QVBoxLayout()
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()

        # 설정 텍스트 (읽기 전용)
        config_label = QLabel("Spider 설정 파일 내용:")
        scroll_layout.addWidget(config_label)

        self.spider_config_text = QTextEdit()
        self.spider_config_text.setReadOnly(True)
        scroll_layout.addWidget(self.spider_config_text)

        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)

        # 새로고침 버튼
        refresh_btn = QPushButton("설정 새로고침")
        refresh_btn.clicked.connect(lambda: self.refresh_config_display("spider"))
        layout.addWidget(scroll)
        layout.addWidget(refresh_btn)

        tab.setLayout(layout)
        return tab

    def refresh_config_display(self, config_name: str = None):
        """설정 표시 새로고침"""
        if not self.parent_app or not self.parent_app.config_manager:
            return

        # GUI 설정 로드
        gui_config = self.parent_app.config_manager.get_config("gui")
        if gui_config:
            try:
                # 자동 시작 설정
                auto_start_config = gui_config.get("auto_start", {})
                self.auto_start_enabled_check.setChecked(
                    auto_start_config.get("enabled", True)
                )

                # 자동 시작할 프로세스 목록
                auto_start_processes = auto_start_config.get("processes", [])
                self.auto_start_backend_check.setChecked("backend" in auto_start_processes)
                self.auto_start_frontend_check.setChecked(
                    "frontend" in auto_start_processes
                )
                self.auto_start_spider_check.setChecked("spider" in auto_start_processes)
                self.auto_start_kafka_check.setChecked("kafka" in auto_start_processes)
                self.auto_start_mapreduce_check.setChecked(
                    "mapreduce" in auto_start_processes
                )

                # systemd 설정
                systemd_config = gui_config.get("systemd", {}).get("services", {})
                tier1_config = systemd_config.get("tier1_orchestrator", {})
                tier2_config = systemd_config.get("tier2_scheduler", {})

                self.systemd_tier1_enabled_check.setChecked(
                    tier1_config.get("enabled", False)
                )
                self.systemd_tier1_autostart_check.setChecked(
                    tier1_config.get("auto_start_on_boot", False)
                )
                self.systemd_tier2_enabled_check.setChecked(
                    tier2_config.get("enabled", False)
                )
                self.systemd_tier2_autostart_check.setChecked(
                    tier2_config.get("auto_start_on_boot", False)
                )

            except Exception as e:
                from shared.logger import setup_logger

                logger = setup_logger(__name__)
                logger.error(f"GUI 설정 표시 오류: {e}")

        configs_to_refresh = (
            [config_name] if config_name else ["cluster", "database", "spider"]
        )

        for cfg_name in configs_to_refresh:
            config = self.parent_app.config_manager.load_config(cfg_name)
            if config:
                try:
                    config_text = yaml.dump(
                        config, default_flow_style=False, allow_unicode=True
                    )
                    if cfg_name == "cluster":
                        self.cluster_config_text.setPlainText(config_text)
                    elif cfg_name == "database":
                        self.database_config_text.setPlainText(config_text)
                    elif cfg_name == "spider":
                        self.spider_config_text.setPlainText(config_text)
                except Exception as e:
                    from shared.logger import setup_logger

                    logger = setup_logger(__name__)
                    logger.error(f"설정 표시 오류 ({cfg_name}): {e}")

    def save_gui_config(self):
        """GUI 설정 저장"""
        if not self.parent_app or not self.parent_app.config_manager:
            return

        try:
            # URL 유효성 검사
            if not hasattr(self, "tier2_url_edit") or not self.tier2_url_edit:
                return
            url = self.tier2_url_edit.text().strip()
            if not url:
                QMessageBox.warning(self, "경고", "Tier2 서버 URL을 입력하세요.")
                return
            if not (url.startswith("http://") or url.startswith("https://")):
                QMessageBox.warning(
                    self,
                    "경고",
                    "올바른 URL 형식이 아닙니다. (http:// 또는 https://로 시작해야 합니다)",
                )
                return

            # Window 설정
            self.parent_app.config_manager.set_config(
                "gui", "window.width", self.window_width_spin.value()
            )
            self.parent_app.config_manager.set_config(
                "gui", "window.height", self.window_height_spin.value()
            )
            self.parent_app.config_manager.set_config(
                "gui", "window.theme", self.window_theme_combo.currentText()
            )

            # Refresh 설정
            auto_refresh = self.auto_refresh_check.isChecked()
            self.parent_app.config_manager.set_config(
                "gui", "refresh.auto_refresh", auto_refresh
            )
            self.parent_app.config_manager.set_config(
                "gui", "refresh.interval", self.refresh_interval_spin.value()
            )

            # Tier2 설정
            self.parent_app.config_manager.set_config("gui", "tier2.base_url", url)
            self.parent_app.config_manager.set_config(
                "gui", "tier2.timeout", self.tier2_timeout_spin.value()
            )
            if self.parent_app.tier2_monitor:
                from gui.monitors import Tier2Monitor

                self.parent_app.tier2_monitor = Tier2Monitor(base_url=url)

            # Cluster 설정
            self.parent_app.config_manager.set_config(
                "gui", "cluster.ssh_timeout", self.cluster_ssh_timeout_spin.value()
            )
            self.parent_app.config_manager.set_config(
                "gui", "cluster.retry_count", self.cluster_retry_spin.value()
            )

            # 자동 시작 설정
            self.parent_app.config_manager.set_config(
                "gui", "auto_start.enabled", self.auto_start_enabled_check.isChecked()
            )

            # 자동 시작할 프로세스 목록 생성
            auto_start_processes = []
            if self.auto_start_backend_check.isChecked():
                auto_start_processes.append("backend")
            if self.auto_start_frontend_check.isChecked():
                auto_start_processes.append("frontend")
            if self.auto_start_spider_check.isChecked():
                auto_start_processes.append("spider")
            if self.auto_start_kafka_check.isChecked():
                auto_start_processes.append("kafka")
            if self.auto_start_mapreduce_check.isChecked():
                auto_start_processes.append("mapreduce")

            self.parent_app.config_manager.set_config(
                "gui", "auto_start.processes", auto_start_processes
            )

            # systemd 설정
            self.parent_app.config_manager.set_config(
                "gui",
                "systemd.services.tier1_orchestrator.enabled",
                self.systemd_tier1_enabled_check.isChecked(),
            )
            self.parent_app.config_manager.set_config(
                "gui",
                "systemd.services.tier1_orchestrator.auto_start_on_boot",
                self.systemd_tier1_autostart_check.isChecked(),
            )
            self.parent_app.config_manager.set_config(
                "gui",
                "systemd.services.tier2_scheduler.enabled",
                self.systemd_tier2_enabled_check.isChecked(),
            )
            self.parent_app.config_manager.set_config(
                "gui",
                "systemd.services.tier2_scheduler.auto_start_on_boot",
                self.systemd_tier2_autostart_check.isChecked(),
            )

            # 자동 새로고침 업데이트
            if auto_refresh:
                interval = self.refresh_interval_spin.value()
                self.parent_app.auto_refresh_timer.stop()
                self.parent_app.auto_refresh_timer.start(interval * 1000)
            else:
                self.parent_app.auto_refresh_timer.stop()

            # 윈도우 크기 적용
            if self.parent_app:
                self.parent_app.resize(
                    self.window_width_spin.value(), self.window_height_spin.value()
                )

            QMessageBox.information(self, "완료", "GUI 설정이 저장되었습니다.")
        except Exception as e:
            from shared.logger import setup_logger

            logger = setup_logger(__name__)
            logger.error(f"GUI 설정 저장 오류: {e}")
            QMessageBox.warning(self, "오류", f"설정 저장 실패: {str(e)}")

    def install_systemd_service(self, service_name):
        """systemd 서비스 설치"""
        try:
            import subprocess
            from pathlib import Path

            # 스크립트 경로
            project_root = Path(__file__).parent.parent.parent
            deployment_dir = project_root / "deployment"

            if service_name == "tier1_orchestrator":
                script_path = deployment_dir / "create_orchestrator_service.sh"
                service_file = "cointicker-orchestrator.service"
            elif service_name == "tier2_scheduler":
                script_path = deployment_dir / "create_tier2_scheduler_service.sh"
                service_file = "cointicker-tier2-scheduler.service"
            else:
                QMessageBox.warning(self, "오류", f"알 수 없는 서비스: {service_name}")
                return

            # 스크립트 실행 확인
            reply = QMessageBox.question(
                self,
                "확인",
                f"{service_name} systemd 서비스를 설치하시겠습니까?\n\n"
                f"sudo 권한이 필요합니다.",
                QMessageBox.Yes | QMessageBox.No,
            )

            if reply == QMessageBox.Yes:
                # 스크립트 실행
                result = subprocess.run(
                    ["bash", str(script_path)],
                    capture_output=True,
                    text=True,
                    timeout=60,
                )

                if result.returncode == 0:
                    QMessageBox.information(
                        self,
                        "완료",
                        f"{service_name} 서비스가 설치되었습니다.\n\n{result.stdout}",
                    )
                else:
                    QMessageBox.warning(
                        self,
                        "오류",
                        f"서비스 설치 실패:\n{result.stderr}",
                    )

        except Exception as e:
            QMessageBox.warning(self, "오류", f"서비스 설치 중 오류 발생:\n{str(e)}")

    def control_systemd_service(self, service_name, action):
        """systemd 서비스 제어 (start/stop/restart)"""
        try:
            import subprocess

            if service_name == "tier1_orchestrator":
                service_file = "cointicker-orchestrator"
            elif service_name == "tier2_scheduler":
                service_file = "cointicker-tier2-scheduler"
            else:
                QMessageBox.warning(self, "오류", f"알 수 없는 서비스: {service_name}")
                return

            # systemctl 명령 실행
            cmd = ["sudo", "systemctl", action, service_file]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                QMessageBox.information(
                    self, "완료", f"{service_name} 서비스를 {action} 했습니다."
                )
            else:
                QMessageBox.warning(
                    self, "오류", f"서비스 {action} 실패:\n{result.stderr}"
                )

        except Exception as e:
            QMessageBox.warning(self, "오류", f"서비스 제어 중 오류 발생:\n{str(e)}")

    def check_systemd_service_status(self, service_name):
        """systemd 서비스 상태 확인"""
        try:
            import subprocess

            if service_name == "tier1_orchestrator":
                service_file = "cointicker-orchestrator"
            elif service_name == "tier2_scheduler":
                service_file = "cointicker-tier2-scheduler"
            else:
                QMessageBox.warning(self, "오류", f"알 수 없는 서비스: {service_name}")
                return

            # systemctl status 실행
            cmd = ["systemctl", "status", service_file, "--no-pager"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

            # 상태 표시
            status_text = result.stdout if result.stdout else result.stderr
            QMessageBox.information(
                self, f"{service_name} 상태", f"```\n{status_text}\n```"
            )

        except Exception as e:
            QMessageBox.warning(self, "오류", f"상태 확인 중 오류 발생:\n{str(e)}")
