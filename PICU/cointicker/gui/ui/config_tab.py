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
