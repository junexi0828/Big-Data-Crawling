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
from PyQt5.QtCore import QTimer
import yaml
import subprocess
import platform
import os
from pathlib import Path
from typing import Optional
from gui.core.timing_config import TimingConfig


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

        # 타이밍 설정
        timing_group = QGroupBox("타이밍 설정")
        timing_layout = QFormLayout()

        # GUI 타이밍
        gui_timing_label = QLabel("<b>GUI 타이밍</b>")
        timing_layout.addRow(gui_timing_label)

        self.stats_update_interval_spin = QSpinBox()
        self.stats_update_interval_spin.setRange(1000, 60000)
        self.stats_update_interval_spin.setSuffix(" ms")
        self.stats_update_interval_spin.setValue(3000)
        timing_layout.addRow("통계 업데이트 간격:", self.stats_update_interval_spin)

        self.resource_update_interval_spin = QSpinBox()
        self.resource_update_interval_spin.setRange(1000, 60000)
        self.resource_update_interval_spin.setSuffix(" ms")
        self.resource_update_interval_spin.setValue(3000)
        timing_layout.addRow(
            "시스템 자원 업데이트 간격:", self.resource_update_interval_spin
        )

        self.user_confirm_timeout_spin = QSpinBox()
        self.user_confirm_timeout_spin.setRange(5, 300)
        self.user_confirm_timeout_spin.setSuffix(" 초")
        self.user_confirm_timeout_spin.setValue(30)
        timing_layout.addRow("사용자 확인 대기 시간:", self.user_confirm_timeout_spin)

        # HDFS 타이밍
        hdfs_timing_label = QLabel("<b>HDFS 타이밍</b>")
        timing_layout.addRow(hdfs_timing_label)

        self.hdfs_script_timeout_spin = QSpinBox()
        self.hdfs_script_timeout_spin.setRange(5, 300)
        self.hdfs_script_timeout_spin.setSuffix(" 초")
        self.hdfs_script_timeout_spin.setValue(30)
        timing_layout.addRow("HDFS 스크립트 타임아웃:", self.hdfs_script_timeout_spin)

        self.hdfs_daemon_stop_timeout_spin = QSpinBox()
        self.hdfs_daemon_stop_timeout_spin.setRange(5, 300)
        self.hdfs_daemon_stop_timeout_spin.setSuffix(" 초")
        self.hdfs_daemon_stop_timeout_spin.setValue(10)
        timing_layout.addRow(
            "HDFS 데몬 중지 타임아웃:", self.hdfs_daemon_stop_timeout_spin
        )

        self.hdfs_format_timeout_spin = QSpinBox()
        self.hdfs_format_timeout_spin.setRange(5, 300)
        self.hdfs_format_timeout_spin.setSuffix(" 초")
        self.hdfs_format_timeout_spin.setValue(30)
        timing_layout.addRow("HDFS 포맷 타임아웃:", self.hdfs_format_timeout_spin)

        # SSH 타이밍
        ssh_timing_label = QLabel("<b>SSH 타이밍</b>")
        timing_layout.addRow(ssh_timing_label)

        self.ssh_connection_test_timeout_spin = QSpinBox()
        self.ssh_connection_test_timeout_spin.setRange(1, 60)
        self.ssh_connection_test_timeout_spin.setSuffix(" 초")
        self.ssh_connection_test_timeout_spin.setValue(5)
        timing_layout.addRow(
            "SSH 연결 테스트 타임아웃:", self.ssh_connection_test_timeout_spin
        )

        self.ssh_command_timeout_spin = QSpinBox()
        self.ssh_command_timeout_spin.setRange(5, 300)
        self.ssh_command_timeout_spin.setSuffix(" 초")
        self.ssh_command_timeout_spin.setValue(10)
        timing_layout.addRow("SSH 명령어 실행 타임아웃:", self.ssh_command_timeout_spin)

        # Pipeline 타이밍
        pipeline_timing_label = QLabel("<b>Pipeline 타이밍</b>")
        timing_layout.addRow(pipeline_timing_label)

        self.pipeline_process_wait_timeout_spin = QSpinBox()
        self.pipeline_process_wait_timeout_spin.setRange(1, 60)
        self.pipeline_process_wait_timeout_spin.setSuffix(" 초")
        self.pipeline_process_wait_timeout_spin.setValue(5)
        timing_layout.addRow(
            "프로세스 종료 대기 타임아웃:", self.pipeline_process_wait_timeout_spin
        )

        timing_group.setLayout(timing_layout)
        scroll_layout.addWidget(timing_group)

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
        systemd_main_layout = QHBoxLayout()  # 메인 레이아웃 (수평)
        systemd_layout = QVBoxLayout()  # 왼쪽 컨텐츠 레이아웃

        systemd_info = QLabel(
            "systemd 서비스를 활성화하면 시스템 부팅 시 자동으로 프로세스가 시작됩니다.\n"
            "GUI 없이 백그라운드에서 실행되며, 장애 발생 시 자동으로 재시작됩니다."
        )
        systemd_info.setWordWrap(True)
        systemd_info.setStyleSheet("color: #666; font-size: 11px; padding: 5px;")
        systemd_layout.addWidget(systemd_info)

        # Tier 1 Orchestrator 서비스
        self.systemd_tier1_enabled_check = QCheckBox(
            "Tier 1 오케스트레이터 서비스 활성화"
        )
        self.systemd_tier1_enabled_check.setChecked(False)
        systemd_layout.addWidget(self.systemd_tier1_enabled_check)

        self.systemd_tier1_autostart_check = QCheckBox("  └─ 부팅 시 자동 시작")
        self.systemd_tier1_autostart_check.setChecked(False)
        self.systemd_tier1_autostart_check.setEnabled(False)
        self.systemd_tier1_enabled_check.toggled.connect(
            self.systemd_tier1_autostart_check.setEnabled
        )
        # 체크박스 변경 시 plist 파일 업데이트
        self.systemd_tier1_autostart_check.toggled.connect(
            lambda checked: self._update_plist_autostart("tier1_orchestrator", checked)
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

        # Scrapyd 서버 서비스
        self.systemd_scrapyd_enabled_check = QCheckBox(
            "Scrapyd 서버 서비스 활성화 (크롤링 작업 스케줄링)"
        )
        self.systemd_scrapyd_enabled_check.setChecked(False)
        systemd_layout.addWidget(self.systemd_scrapyd_enabled_check)

        self.systemd_scrapyd_autostart_check = QCheckBox("  └─ 부팅 시 자동 시작")
        self.systemd_scrapyd_autostart_check.setChecked(False)
        self.systemd_scrapyd_autostart_check.setEnabled(False)
        self.systemd_scrapyd_enabled_check.toggled.connect(
            self.systemd_scrapyd_autostart_check.setEnabled
        )
        # 체크박스 변경 시 plist 파일 업데이트
        self.systemd_scrapyd_autostart_check.toggled.connect(
            lambda checked: self._update_plist_autostart("scrapyd", checked)
        )
        systemd_layout.addWidget(self.systemd_scrapyd_autostart_check)

        scrapyd_btn_layout = QHBoxLayout()
        self.scrapyd_install_btn = QPushButton("서비스 설치")
        self.scrapyd_install_btn.clicked.connect(
            lambda: self.install_systemd_service("scrapyd")
        )
        scrapyd_btn_layout.addWidget(self.scrapyd_install_btn)

        self.scrapyd_start_btn = QPushButton("서비스 시작")
        self.scrapyd_start_btn.clicked.connect(
            lambda: self.control_systemd_service("scrapyd", "start")
        )
        scrapyd_btn_layout.addWidget(self.scrapyd_start_btn)

        self.scrapyd_stop_btn = QPushButton("서비스 중지")
        self.scrapyd_stop_btn.clicked.connect(
            lambda: self.control_systemd_service("scrapyd", "stop")
        )
        scrapyd_btn_layout.addWidget(self.scrapyd_stop_btn)

        self.scrapyd_status_btn = QPushButton("상태 확인")
        self.scrapyd_status_btn.clicked.connect(
            lambda: self.check_systemd_service_status("scrapyd")
        )
        scrapyd_btn_layout.addWidget(self.scrapyd_status_btn)

        scrapyd_btn_layout.addStretch()
        systemd_layout.addLayout(scrapyd_btn_layout)

        # Tier 2 Scheduler 서비스
        self.systemd_tier2_enabled_check = QCheckBox(
            "Tier 2 파이프라인 서비스 활성화 (HDFS → DB 적재 → frontend 서버)"
        )
        self.systemd_tier2_enabled_check.setChecked(False)
        systemd_layout.addWidget(self.systemd_tier2_enabled_check)

        self.systemd_tier2_autostart_check = QCheckBox("  └─ 부팅 시 자동 시작")
        self.systemd_tier2_autostart_check.setChecked(False)
        self.systemd_tier2_autostart_check.setEnabled(False)
        self.systemd_tier2_enabled_check.toggled.connect(
            self.systemd_tier2_autostart_check.setEnabled
        )
        # 체크박스 변경 시 plist 파일 업데이트
        self.systemd_tier2_autostart_check.toggled.connect(
            lambda checked: self._update_plist_autostart("tier2_scheduler", checked)
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

        # 왼쪽 컨텐츠를 메인 레이아웃에 추가
        systemd_main_layout.addLayout(systemd_layout)

        # 오른쪽 설명 박스
        info_box = QGroupBox("서비스 상세 정보")
        info_box.setStyleSheet(
            """
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """
        )
        info_layout = QVBoxLayout()
        info_layout.setSpacing(15)

        # Tier 1 설명
        tier1_info = QLabel(
            "<b>Tier 1 오케스트레이터 서비스:</b><br>"
            "• <b>실행:</b> master-node/orchestrator.py<br>"
            "• <b>기능:</b> 크롤링 → MapReduce → HDFS 저장 전체 관리<br>"
            "• <b>스케줄:</b> 5분마다 크롤링, 30분마다 전체 파이프라인,<br>"
            "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;매일 자정 공포·탐욕 지수"
        )
        tier1_info.setWordWrap(True)
        tier1_info.setStyleSheet(
            """
            QLabel {
                color: #ddd;
                font-size: 11px;
                padding: 10px;
                background-color: #2a2a2a;
                border-radius: 5px;
            }
        """
        )
        info_layout.addWidget(tier1_info)

        # Tier 2 설명
        tier2_info = QLabel(
            "<b>Tier 2 파이프라인 24/7 데몬 서비스:</b><br>"
            "• <b>실행:</b> scripts/run_pipeline_scheduler.py<br>"
            "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(master-node/scheduler.py가 아님)<br>"
            "• <b>기능:</b> HDFS → DB 적재 + 감성분석 + 인사이트 생성 자동화<br>"
            "• <b>스케줄:</b> n 분마다 전체 파이프라인 실행<br>"
        )
        tier2_info.setWordWrap(True)
        tier2_info.setStyleSheet(
            """
            QLabel {
                color: #ddd;
                font-size: 11px;
                padding: 10px;
                background-color: #2a2a2a;
                border-radius: 5px;
            }
        """
        )
        info_layout.addWidget(tier2_info)

        info_layout.addStretch()
        info_box.setLayout(info_layout)

        # 설명 박스를 메인 레이아웃에 추가 (최소 너비 설정)
        info_box.setMinimumWidth(350)
        info_box.setMaximumWidth(400)
        systemd_main_layout.addWidget(info_box)

        systemd_group.setLayout(systemd_main_layout)
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

        # 버튼 레이아웃
        button_layout = QHBoxLayout()

        # 새로고침 버튼
        refresh_btn = QPushButton("설정 새로고침")
        refresh_btn.clicked.connect(lambda: self.refresh_config_display("cluster"))
        button_layout.addWidget(refresh_btn)

        # 설정 파일 열기 버튼
        open_file_btn = QPushButton("설정 파일 열기")
        open_file_btn.clicked.connect(lambda: self.open_config_file("cluster"))
        button_layout.addWidget(open_file_btn)

        layout.addWidget(scroll)
        layout.addLayout(button_layout)

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

        # 버튼 레이아웃
        button_layout = QHBoxLayout()

        # 새로고침 버튼
        refresh_btn = QPushButton("설정 새로고침")
        refresh_btn.clicked.connect(lambda: self.refresh_config_display("database"))
        button_layout.addWidget(refresh_btn)

        # 설정 파일 열기 버튼
        open_file_btn = QPushButton("설정 파일 열기")
        open_file_btn.clicked.connect(lambda: self.open_config_file("database"))
        button_layout.addWidget(open_file_btn)

        layout.addWidget(scroll)
        layout.addLayout(button_layout)

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

        # 버튼 레이아웃
        button_layout = QHBoxLayout()

        # 새로고침 버튼
        refresh_btn = QPushButton("설정 새로고침")
        refresh_btn.clicked.connect(lambda: self.refresh_config_display("spider"))
        button_layout.addWidget(refresh_btn)

        # 설정 파일 열기 버튼
        open_file_btn = QPushButton("설정 파일 열기")
        open_file_btn.clicked.connect(lambda: self.open_config_file("spider"))
        button_layout.addWidget(open_file_btn)

        layout.addWidget(scroll)
        layout.addLayout(button_layout)

        tab.setLayout(layout)
        return tab

    def refresh_config_display(self, config_name: Optional[str] = None):
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
                self.auto_start_backend_check.setChecked(
                    "backend" in auto_start_processes
                )
                self.auto_start_frontend_check.setChecked(
                    "frontend" in auto_start_processes
                )
                self.auto_start_spider_check.setChecked(
                    "spider" in auto_start_processes
                )
                self.auto_start_kafka_check.setChecked("kafka" in auto_start_processes)
                self.auto_start_mapreduce_check.setChecked(
                    "mapreduce" in auto_start_processes
                )

                # systemd 설정
                systemd_config = gui_config.get("systemd", {}).get("services", {})
                tier1_config = systemd_config.get("tier1_orchestrator", {})
                scrapyd_config = systemd_config.get("scrapyd", {})
                tier2_config = systemd_config.get("tier2_scheduler", {})

                self.systemd_tier1_enabled_check.setChecked(
                    tier1_config.get("enabled", False)
                )
                self.systemd_tier1_autostart_check.setChecked(
                    tier1_config.get("auto_start_on_boot", False)
                )
                self.systemd_scrapyd_enabled_check.setChecked(
                    scrapyd_config.get("enabled", False)
                )
                self.systemd_scrapyd_autostart_check.setChecked(
                    scrapyd_config.get("auto_start_on_boot", False)
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
                "systemd.services.scrapyd.enabled",
                self.systemd_scrapyd_enabled_check.isChecked(),
            )
            self.parent_app.config_manager.set_config(
                "gui",
                "systemd.services.scrapyd.auto_start_on_boot",
                self.systemd_scrapyd_autostart_check.isChecked(),
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

            # 타이밍 설정 저장
            if hasattr(self, "stats_update_interval_spin"):
                TimingConfig.set(
                    "gui.stats_update_interval", self.stats_update_interval_spin.value()
                )
                TimingConfig.set(
                    "gui.resource_update_interval",
                    self.resource_update_interval_spin.value(),
                )
                TimingConfig.set(
                    "gui.user_confirm_timeout", self.user_confirm_timeout_spin.value()
                )
                TimingConfig.set(
                    "hdfs.script_timeout", self.hdfs_script_timeout_spin.value()
                )
                TimingConfig.set(
                    "hdfs.daemon_stop_timeout",
                    self.hdfs_daemon_stop_timeout_spin.value(),
                )
                TimingConfig.set(
                    "hdfs.format_timeout", self.hdfs_format_timeout_spin.value()
                )
                TimingConfig.set(
                    "ssh.connection_test_timeout",
                    self.ssh_connection_test_timeout_spin.value(),
                )
                TimingConfig.set(
                    "ssh.command_timeout", self.ssh_command_timeout_spin.value()
                )
                TimingConfig.set(
                    "pipeline.process_wait_timeout",
                    self.pipeline_process_wait_timeout_spin.value(),
                )

                # 타이머 즉시 업데이트
                if self.parent_app and hasattr(self.parent_app, "stats_timer"):
                    stats_interval = TimingConfig.get("gui.stats_update_interval", 5000)
                    if self.parent_app.stats_timer.isActive():
                        self.parent_app.stats_timer.stop()
                        self.parent_app.stats_timer.start(stats_interval)

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
        """systemd 서비스 설치 (sudo 비밀번호 입력 지원)"""
        try:
            import subprocess
            import threading
            from pathlib import Path
            from shared.logger import setup_logger

            logger = setup_logger(__name__)

            # 스크립트 경로
            from shared.path_utils import get_project_root

            project_root = get_project_root()
            deployment_dir = project_root / "deployment"

            if service_name == "tier1_orchestrator":
                script_path = deployment_dir / "create_orchestrator_service.sh"
                service_file = "cointicker-orchestrator.service"
            elif service_name == "scrapyd":
                script_path = deployment_dir / "create_scrapyd_service.sh"
                service_file = "cointicker-scrapyd.service"
            elif service_name == "tier2_scheduler":
                script_path = deployment_dir / "create_tier2_scheduler_service.sh"
                service_file = "cointicker-tier2-scheduler.service"
            else:
                QMessageBox.warning(self, "오류", f"알 수 없는 서비스: {service_name}")
                return

            if not script_path.exists():
                QMessageBox.warning(
                    self, "오류", f"스크립트를 찾을 수 없습니다: {script_path}"
                )
                return

            # 스크립트 실행 확인
            reply = QMessageBox.question(
                self,
                "확인",
                f"{service_name} systemd 서비스를 설치하시겠습니까?\n\n"
                f"sudo 권한이 필요합니다.",
                QMessageBox.Yes | QMessageBox.No,
            )

            if reply == QMessageBox.No:
                return

            # 비밀번호 입력 받기
            if not self.parent_app or not hasattr(
                self.parent_app, "pipeline_orchestrator"
            ):
                QMessageBox.warning(
                    self, "오류", "비밀번호 입력 기능을 사용할 수 없습니다."
                )
                return

            user_password_callback = (
                self.parent_app.pipeline_orchestrator.user_password_callback
                if self.parent_app.pipeline_orchestrator
                else None
            )

            if not user_password_callback:
                QMessageBox.warning(
                    self, "오류", "비밀번호 입력 콜백을 사용할 수 없습니다."
                )
                return

            # 비밀번호 입력 다이얼로그 표시
            password = user_password_callback(
                f"{service_name} 서비스 설치 - 관리자 권한 필요",
                f"{service_name} systemd 서비스를 설치하려면 관리자 비밀번호가 필요합니다.\n\n"
                f"비밀번호를 입력하세요:",
            )

            if not password:
                logger.warning("비밀번호 입력이 취소되었습니다.")
                QMessageBox.warning(
                    self,
                    "취소",
                    "비밀번호 입력이 취소되었습니다. 서비스를 설치할 수 없습니다.",
                )
                return

            # 별도 스레드에서 실행 (타임아웃 방지)
            def run_installation(pwd: str):
                try:
                    # 비밀번호 검증 (sudo -S로 테스트)
                    logger.info("비밀번호 검증 중...")
                    test_process = subprocess.Popen(
                        ["sudo", "-S", "echo", "test"],
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )

                    try:
                        password_bytes = (pwd + "\n").encode()
                        if test_process.stdin:
                            test_process.stdin.write(password_bytes)
                            test_process.stdin.flush()
                        stdout, stderr = test_process.communicate(timeout=5)

                        if test_process.returncode != 0:
                            error_msg = stderr.decode("utf-8", errors="ignore")

                            def show_password_error():
                                QMessageBox.warning(
                                    self,
                                    "오류",
                                    f"비밀번호가 올바르지 않습니다.\n\n{error_msg}",
                                )

                            QTimer.singleShot(0, show_password_error)
                            return
                    except subprocess.TimeoutExpired:
                        test_process.kill()

                        def show_timeout_error():
                            QMessageBox.warning(self, "오류", "비밀번호 검증 시간 초과")

                        QTimer.singleShot(0, show_timeout_error)
                        return

                    logger.info("✅ 비밀번호 검증 성공")

                    # OS 확인
                    import platform

                    system = platform.system()

                    if system == "Darwin":  # macOS
                        # macOS: launchctl plist 파일 생성
                        logger.info(
                            f"{service_name} launchctl 서비스 설치 시작 (macOS)..."
                        )

                        from shared.path_utils import get_cointicker_root

                        cointicker_root = get_cointicker_root()
                        home = Path.home()
                        launch_agents_dir = home / "Library" / "LaunchAgents"
                        launch_agents_dir.mkdir(parents=True, exist_ok=True)

                        # 서비스별 설정
                        if service_name == "tier1_orchestrator":
                            plist_name = "com.cointicker.orchestrator"
                            script_path_py = (
                                cointicker_root / "master-node" / "orchestrator.py"
                            )
                        elif service_name == "scrapyd":
                            plist_name = "com.cointicker.scrapyd"
                            # scrapyd는 Python 스크립트가 아닌 데몬이므로 venv의 scrapyd 명령어 사용
                            script_path_py = None  # scrapyd는 별도 처리
                        elif service_name == "tier2_scheduler":
                            plist_name = "com.cointicker.tier2-scheduler"
                            script_path_py = (
                                cointicker_root
                                / "scripts"
                                / "run_pipeline_scheduler.py"
                            )
                        else:
                            raise ValueError(f"알 수 없는 서비스: {service_name}")

                        plist_path = launch_agents_dir / f"{plist_name}.plist"

                        # venv Python 경로 찾기
                        venv_python = (
                            cointicker_root.parent / "venv" / "bin" / "python3"
                        )
                        if not venv_python.exists():
                            # 대체 경로 시도
                            venv_python = (
                                cointicker_root.parent / "venv" / "bin" / "python"
                            )

                        if not venv_python.exists():

                            def show_error():
                                QMessageBox.warning(
                                    self,
                                    "오류",
                                    f"가상환경 Python을 찾을 수 없습니다: {venv_python}",
                                )

                            QTimer.singleShot(0, show_error)
                            return

                        # "부팅 시 자동 시작" 체크박스 상태 확인
                        autostart_enabled = False
                        if service_name == "tier1_orchestrator":
                            autostart_enabled = (
                                self.systemd_tier1_autostart_check.isChecked()
                            )
                        elif service_name == "scrapyd":
                            autostart_enabled = (
                                self.systemd_scrapyd_autostart_check.isChecked()
                            )
                        elif service_name == "tier2_scheduler":
                            autostart_enabled = (
                                self.systemd_tier2_autostart_check.isChecked()
                            )

                        # scrapyd는 Python 스크립트가 아닌 데몬이므로 별도 처리
                        if service_name == "scrapyd":
                            # scrapyd 명령어 찾기
                            import shutil

                            scrapyd_cmd = shutil.which("scrapyd")
                            if not scrapyd_cmd:
                                # venv의 scrapyd 확인 (여러 경로 시도)
                                project_root = cointicker_root.parent  # PICU/
                                bigdata_root = project_root.parent  # bigdata/

                                venv_scrapyd_paths = [
                                    venv_python.parent / "scrapyd",  # 현재 venv
                                    project_root
                                    / "venv"
                                    / "bin"
                                    / "scrapyd",  # PICU/venv
                                    cointicker_root
                                    / "venv"
                                    / "bin"
                                    / "scrapyd",  # cointicker/venv
                                    bigdata_root
                                    / "venv"
                                    / "bin"
                                    / "scrapyd",  # bigdata/venv
                                ]

                                for scrapyd_path in venv_scrapyd_paths:
                                    if scrapyd_path.exists():
                                        scrapyd_cmd = str(scrapyd_path)
                                        logger.info(
                                            f"Scrapyd 명령어 발견: {scrapyd_cmd}"
                                        )
                                        break

                            if not scrapyd_cmd or not Path(scrapyd_cmd).exists():

                                def show_error():
                                    QMessageBox.warning(
                                        self,
                                        "오류",
                                        f"scrapyd 명령어를 찾을 수 없습니다.\n\n"
                                        f"설치하세요: pip install scrapyd\n"
                                        f"또는 venv에 scrapyd가 설치되어 있는지 확인하세요.",
                                    )

                                QTimer.singleShot(0, show_error)
                                return

                            # plist 파일 내용 생성 (scrapyd 데몬)
                            plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{plist_name}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{scrapyd_cmd}</string>
    </array>
    <key>WorkingDirectory</key>
    <string>{cointicker_root.parent}</string>
    <key>RunAtLoad</key>
    <{str(autostart_enabled).lower()}/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>{cointicker_root / "logs" / f"{plist_name}.out.log"}</string>
    <key>StandardErrorPath</key>
    <string>{cointicker_root / "logs" / f"{plist_name}.err.log"}</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>{Path(scrapyd_cmd).parent}:{os.environ.get('PATH', '')}</string>
    </dict>
</dict>
</plist>"""
                        else:
                            # plist 파일 내용 생성 (Python 스크립트)
                            plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{plist_name}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{venv_python}</string>
        <string>{script_path_py}</string>
    </array>
    <key>WorkingDirectory</key>
    <string>{cointicker_root}</string>
    <key>RunAtLoad</key>
    <{str(autostart_enabled).lower()}/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>{cointicker_root / "logs" / f"{plist_name}.out.log"}</string>
    <key>StandardErrorPath</key>
    <string>{cointicker_root / "logs" / f"{plist_name}.err.log"}</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>{venv_python.parent}:{os.environ.get('PATH', '')}</string>
        <key>PYTHONPATH</key>
        <string>{cointicker_root}:{cointicker_root / "shared"}</string>
    </dict>
</dict>
</plist>"""

                        # plist 파일 생성 (비밀번호 불필요, 사용자 디렉토리)
                        try:
                            with open(plist_path, "w", encoding="utf-8") as f:
                                f.write(plist_content)

                            logger.info(f"✅ plist 파일 생성 완료: {plist_path}")

                            # launchctl 로드 (비밀번호 불필요)
                            result = subprocess.run(
                                ["launchctl", "load", str(plist_path)],
                                capture_output=True,
                                text=True,
                                timeout=10,
                            )

                            if result.returncode == 0:

                                def show_success():
                                    QMessageBox.information(
                                        self,
                                        "완료",
                                        f"{service_name} launchctl 서비스가 설치되었습니다.\n\n"
                                        f"plist 파일: {plist_path}\n"
                                        f"서비스 이름: {plist_name}",
                                    )

                                QTimer.singleShot(0, show_success)
                            else:

                                def show_error():
                                    QMessageBox.warning(
                                        self,
                                        "오류",
                                        f"서비스 로드 실패:\n{result.stderr}",
                                    )

                                QTimer.singleShot(0, show_error)
                        except Exception as e:
                            logger.error(f"plist 파일 생성 실패: {e}")

                            def show_error():
                                QMessageBox.warning(
                                    self,
                                    "오류",
                                    f"plist 파일 생성 실패:\n{str(e)}",
                                )

                            QTimer.singleShot(0, show_error)

                    elif system == "Linux":
                        # Linux: systemd 서비스 설치 (기존 스크립트 사용)
                        logger.info(
                            f"{service_name} systemd 서비스 설치 시작 (Linux)..."
                        )
                        install_process = subprocess.Popen(
                            ["sudo", "-S", "bash", str(script_path)],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                        )

                        try:
                            # 검증된 비밀번호 재사용
                            password_bytes = (pwd + "\n").encode()
                            if install_process.stdin:
                                install_process.stdin.write(password_bytes)
                                install_process.stdin.flush()

                            # 출력 읽기
                            stdout, stderr = install_process.communicate(timeout=300)

                            stdout_text = stdout.decode("utf-8", errors="ignore")
                            stderr_text = stderr.decode("utf-8", errors="ignore")

                            if install_process.returncode == 0:

                                def show_success():
                                    QMessageBox.information(
                                        self,
                                        "완료",
                                        f"{service_name} 서비스가 설치되었습니다.\n\n{stdout_text}",
                                    )

                                QTimer.singleShot(0, show_success)
                            else:

                                def show_error():
                                    QMessageBox.warning(
                                        self,
                                        "오류",
                                        f"서비스 설치 실패:\n{stderr_text}",
                                    )

                                QTimer.singleShot(0, show_error)
                        except subprocess.TimeoutExpired:
                            install_process.kill()

                            def show_timeout():
                                QMessageBox.warning(
                                    self, "오류", "서비스 설치 시간 초과 (5분)"
                                )

                            QTimer.singleShot(0, show_timeout)
                        finally:
                            # 비밀번호 즉시 삭제
                            pwd = ""
                    else:

                        def show_error():
                            QMessageBox.warning(
                                self,
                                "오류",
                                f"지원하지 않는 OS: {system}\n\n"
                                f"Linux 또는 macOS만 지원됩니다.",
                            )

                        QTimer.singleShot(0, show_error)
                        # 비밀번호 즉시 삭제
                        pwd = ""

                except Exception as e:
                    logger.error(f"서비스 설치 중 오류: {e}")

                    def show_error():
                        QMessageBox.warning(
                            self, "오류", f"서비스 설치 중 오류 발생:\n{str(e)}"
                        )

                    QTimer.singleShot(0, show_error)

            # 별도 스레드에서 실행 (비밀번호를 인자로 전달)
            thread = threading.Thread(
                target=run_installation, args=(password,), daemon=True
            )
            thread.start()

            # 메인 스레드에서 비밀번호 즉시 삭제
            del password

        except Exception as e:
            from shared.logger import setup_logger

            logger = setup_logger(__name__)
            logger.error(f"서비스 설치 중 오류: {e}")
            QMessageBox.warning(self, "오류", f"서비스 설치 중 오류 발생:\n{str(e)}")

    def control_systemd_service(self, service_name, action):
        """systemd/launchctl 서비스 제어 (start/stop/restart)"""
        try:
            import subprocess
            import platform
            from gui.modules.systemd_manager import SystemdManager

            system = platform.system()

            if system == "Darwin":  # macOS
                # macOS: launchctl 사용
                plist_name = SystemdManager.MACOS_PLIST_NAMES.get(service_name)
                if not plist_name:
                    QMessageBox.warning(
                        self, "오류", f"알 수 없는 서비스: {service_name}"
                    )
                    return

                from pathlib import Path

                home = Path.home()
                plist_path = home / "Library" / "LaunchAgents" / f"{plist_name}.plist"

                if not plist_path.exists():
                    QMessageBox.warning(
                        self,
                        "오류",
                        f"서비스가 설치되지 않았습니다.\n\nplist 파일을 찾을 수 없습니다: {plist_path}",
                    )
                    return

                if action == "start":
                    result = subprocess.run(
                        ["launchctl", "load", str(plist_path)],
                        capture_output=True,
                        text=True,
                        timeout=30,
                    )
                elif action == "stop":
                    result = subprocess.run(
                        ["launchctl", "unload", str(plist_path)],
                        capture_output=True,
                        text=True,
                        timeout=30,
                    )
                elif action == "restart":
                    # unload 후 load
                    subprocess.run(
                        ["launchctl", "unload", str(plist_path)],
                        capture_output=True,
                        text=True,
                        timeout=30,
                    )
                    result = subprocess.run(
                        ["launchctl", "load", str(plist_path)],
                        capture_output=True,
                        text=True,
                        timeout=30,
                    )
                else:
                    QMessageBox.warning(self, "오류", f"지원하지 않는 동작: {action}")
                    return

                if result.returncode == 0:
                    QMessageBox.information(
                        self, "완료", f"{service_name} 서비스를 {action} 했습니다."
                    )
                    # Control 탭 상태 업데이트
                    self._sync_to_control_tab(service_name, action)
                else:
                    QMessageBox.warning(
                        self, "오류", f"서비스 {action} 실패:\n{result.stderr}"
                    )

            elif system == "Linux":  # Linux
                # Linux: systemctl 사용
                if service_name == "tier1_orchestrator":
                    service_file = "cointicker-orchestrator"
                elif service_name == "scrapyd":
                    service_file = "cointicker-scrapyd"
                elif service_name == "tier2_scheduler":
                    service_file = "cointicker-tier2-scheduler"
                else:
                    QMessageBox.warning(
                        self, "오류", f"알 수 없는 서비스: {service_name}"
                    )
                    return

                # systemctl 명령 실행
                cmd = ["sudo", "systemctl", action, service_file]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

                if result.returncode == 0:
                    QMessageBox.information(
                        self, "완료", f"{service_name} 서비스를 {action} 했습니다."
                    )
                    # Control 탭 상태 업데이트
                    self._sync_to_control_tab(service_name, action)
                else:
                    QMessageBox.warning(
                        self, "오류", f"서비스 {action} 실패:\n{result.stderr}"
                    )
            else:
                QMessageBox.warning(self, "오류", f"지원하지 않는 OS: {system}")

        except Exception as e:
            QMessageBox.warning(self, "오류", f"서비스 제어 중 오류 발생:\n{str(e)}")

    def check_systemd_service_status(self, service_name):
        """systemd/launchctl 서비스 상태 확인"""
        try:
            import subprocess
            import platform
            from gui.modules.systemd_manager import SystemdManager

            # SystemdManager를 사용하여 상태 확인
            status = SystemdManager.get_service_status(service_name)

            system = platform.system()

            if system == "Darwin":  # macOS
                # macOS: launchctl 사용
                plist_name = SystemdManager.MACOS_PLIST_NAMES.get(service_name)
                if not plist_name:
                    QMessageBox.warning(
                        self, "오류", f"알 수 없는 서비스: {service_name}"
                    )
                    return

                from pathlib import Path

                home = Path.home()
                plist_path = home / "Library" / "LaunchAgents" / f"{plist_name}.plist"

                # 상태 정보 구성
                status_lines = []
                status_lines.append(f"서비스: {service_name}")
                status_lines.append(f"plist 파일: {plist_path}")
                status_lines.append(
                    f"파일 존재: {'예' if status.get('exists') else '아니오'}"
                )
                status_lines.append(
                    f"실행 상태: {'실행 중' if status.get('running') else '중지됨'}"
                )
                status_lines.append(
                    f"자동 시작: {'활성화' if status.get('enabled') else '비활성화'}"
                )

                if status.get("running"):
                    # PID 정보 가져오기
                    list_result = subprocess.run(
                        ["launchctl", "list", plist_name],
                        capture_output=True,
                        text=True,
                        timeout=10,
                    )
                    if list_result.returncode == 0:
                        status_lines.append(f"\n상세 정보:\n{list_result.stdout}")

                status_text = "\n".join(status_lines)
                QMessageBox.information(self, f"{service_name} 상태", status_text)

            elif system == "Linux":  # Linux
                # Linux: systemctl 사용
                if service_name == "tier1_orchestrator":
                    service_file = "cointicker-orchestrator"
                elif service_name == "scrapyd":
                    service_file = "cointicker-scrapyd"
                elif service_name == "tier2_scheduler":
                    service_file = "cointicker-tier2-scheduler"
                else:
                    QMessageBox.warning(
                        self, "오류", f"알 수 없는 서비스: {service_name}"
                    )
                    return

                # systemctl status 실행
                cmd = ["systemctl", "status", service_file, "--no-pager"]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

                # 상태 표시
                status_text = result.stdout if result.stdout else result.stderr
                QMessageBox.information(
                    self, f"{service_name} 상태", f"```\n{status_text}\n```"
                )
            else:
                QMessageBox.warning(self, "오류", f"지원하지 않는 OS: {system}")

        except Exception as e:
            QMessageBox.warning(self, "오류", f"상태 확인 중 오류 발생:\n{str(e)}")

    def _update_plist_autostart(self, service_name: str, enabled: bool):
        """plist 파일의 RunAtLoad 값 업데이트"""
        try:
            import platform
            from gui.modules.systemd_manager import SystemdManager

            system = platform.system()
            if system != "Darwin":
                return  # macOS만 지원

            plist_name = SystemdManager.MACOS_PLIST_NAMES.get(service_name)
            if not plist_name:
                return

            from pathlib import Path
            import plistlib

            home = Path.home()
            plist_path = home / "Library" / "LaunchAgents" / f"{plist_name}.plist"

            if not plist_path.exists():
                return  # plist 파일이 없으면 업데이트 불가

            # plist 파일 읽기
            with open(plist_path, "rb") as f:
                plist_data = plistlib.load(f)

            # RunAtLoad 값 업데이트
            plist_data["RunAtLoad"] = enabled

            # plist 파일 쓰기
            with open(plist_path, "wb") as f:
                plistlib.dump(plist_data, f)

            from shared.logger import setup_logger

            logger = setup_logger(__name__)
            logger.info(
                f"{service_name} plist 파일의 RunAtLoad를 {enabled}로 업데이트했습니다."
            )

        except Exception as e:
            from shared.logger import setup_logger

            logger = setup_logger(__name__)
            logger.error(f"plist 파일 업데이트 실패: {e}")

    def _sync_to_control_tab(self, service_name: str, action: str):
        """Control 탭과 상태 동기화"""
        try:
            if not self.parent_app or not hasattr(self.parent_app, "control_tab"):
                return

            control_tab = self.parent_app.control_tab

            if service_name == "tier1_orchestrator":
                if action == "start":
                    control_tab.orchestrator_status_label.setText(" 상태: ✅ 실행 중")
                    control_tab.orchestrator_status_label.setStyleSheet(
                        "color: green; font-weight: bold; font-size: 14pt;"
                    )
                elif action == "stop":
                    control_tab.orchestrator_status_label.setText(" 상태: ⏹️ 중지됨")
                    control_tab.orchestrator_status_label.setStyleSheet(
                        "color: gray; font-size: 14pt;"
                    )
            elif service_name == "scrapyd":
                # Scrapyd 서버는 Control 탭에 별도 UI가 없으므로 로그만 출력
                # 필요시 Control 탭에 Scrapyd 서버 상태 표시 추가 가능
                pass
            elif service_name == "tier2_scheduler":
                if action == "start":
                    control_tab.scheduler_status_label.setText(" 상태: ✅ 실행 중")
                    control_tab.scheduler_status_label.setStyleSheet(
                        "color: green; font-weight: bold; font-size: 14pt;"
                    )
                elif action == "stop":
                    control_tab.scheduler_status_label.setText(" 상태: ⏹️ 중지됨")
                    control_tab.scheduler_status_label.setStyleSheet(
                        "color: gray; font-size: 14pt;"
                    )
        except Exception as e:
            from shared.logger import setup_logger

            logger = setup_logger(__name__)
            logger.debug(f"Control 탭 동기화 실패: {e}")

    def refresh_service_status(self):
        """서비스 상태를 확인하고 UI 업데이트"""
        try:
            from gui.modules.systemd_manager import SystemdManager

            # Tier 1 Orchestrator 상태 확인
            tier1_status = SystemdManager.get_service_status("tier1_orchestrator")
            if tier1_status.get("exists"):
                self.systemd_tier1_enabled_check.setChecked(True)
                self.systemd_tier1_autostart_check.setEnabled(True)
                # plist 파일에서 RunAtLoad 값 읽기
                self._load_plist_autostart("tier1_orchestrator")

            # Tier 2 Scheduler 상태 확인
            tier2_status = SystemdManager.get_service_status("tier2_scheduler")
            if tier2_status.get("exists"):
                self.systemd_tier2_enabled_check.setChecked(True)
                self.systemd_tier2_autostart_check.setEnabled(True)
                # plist 파일에서 RunAtLoad 값 읽기
                self._load_plist_autostart("tier2_scheduler")

        except Exception as e:
            from shared.logger import setup_logger

            logger = setup_logger(__name__)
            logger.debug(f"서비스 상태 새로고침 실패: {e}")

    def _load_plist_autostart(self, service_name: str):
        """plist 파일에서 RunAtLoad 값 읽어서 체크박스에 반영"""
        try:
            import platform
            from gui.modules.systemd_manager import SystemdManager

            system = platform.system()
            if system != "Darwin":
                return  # macOS만 지원

            plist_name = SystemdManager.MACOS_PLIST_NAMES.get(service_name)
            if not plist_name:
                return

            from pathlib import Path
            import plistlib

            home = Path.home()
            plist_path = home / "Library" / "LaunchAgents" / f"{plist_name}.plist"

            if not plist_path.exists():
                return  # plist 파일이 없으면 읽기 불가

            # plist 파일 읽기
            with open(plist_path, "rb") as f:
                plist_data = plistlib.load(f)

            # RunAtLoad 값 읽기
            run_at_load = plist_data.get("RunAtLoad", False)

            # 체크박스에 반영
            if service_name == "tier1_orchestrator":
                self.systemd_tier1_autostart_check.setChecked(run_at_load)
            elif service_name == "scrapyd":
                self.systemd_scrapyd_autostart_check.setChecked(run_at_load)
            elif service_name == "tier2_scheduler":
                self.systemd_tier2_autostart_check.setChecked(run_at_load)

        except Exception as e:
            from shared.logger import setup_logger

            logger = setup_logger(__name__)
            logger.debug(f"plist 파일 읽기 실패: {e}")

    def open_config_file(self, config_name: str):
        """설정 파일을 기본 에디터로 열기"""
        if not self.parent_app or not self.parent_app.config_manager:
            return

        try:
            config_file = (
                self.parent_app.config_manager.config_dir
                / self.parent_app.config_manager.config_files.get(config_name)
            )

            if not config_file.exists():
                QMessageBox.warning(
                    self,
                    "경고",
                    f"설정 파일을 찾을 수 없습니다:\n{config_file}",
                )
                return

            # 운영체제별 파일 열기
            system = platform.system()
            if system == "Darwin":  # macOS
                subprocess.run(["open", str(config_file)])
            elif system == "Windows":
                subprocess.run(["notepad", str(config_file)])
            else:  # Linux
                # 기본 에디터 찾기
                editor = os.environ.get("EDITOR", "nano")
                subprocess.run([editor, str(config_file)])

        except Exception as e:
            from shared.logger import setup_logger

            logger = setup_logger(__name__)
            logger.error(f"설정 파일 열기 오류: {e}")
            QMessageBox.warning(self, "오류", f"설정 파일 열기 실패: {str(e)}")
