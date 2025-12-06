"""
제어 탭
프로세스 제어 및 모니터링 탭
"""

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QComboBox,
    QTextEdit,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QScrollArea,
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class ControlTab(QWidget):
    """제어 탭 클래스"""

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
        # 스크롤 영역 생성
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # 스크롤 가능한 컨텐츠 위젯
        content_widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(12)  # 섹션 간 간격 조정 (20 → 12)
        layout.setContentsMargins(20, 20, 20, 20)  # 여백 유지

        # 통합 제어 섹션
        integrated_group = QWidget()
        integrated_group.setMinimumHeight(320)  # 최소 높이 증가 (테이블 + 버튼 + 여유)
        integrated_layout = QVBoxLayout()
        integrated_layout.setSpacing(10)

        integrated_label = QLabel("통합 파이프라인 제어기")
        integrated_label.setFont(QFont("Arial", 18, QFont.Bold))  # 16 → 18
        integrated_layout.addWidget(integrated_label)

        # 통합 제어 설명
        integrated_desc = QLabel(
            "※ 모든 프로세스를 의존성 순서대로 일괄 제어합니다\n"
            "   (Backend → Kafka → Spider → HDFS → Frontend)"
        )
        integrated_desc.setStyleSheet("color: #666; font-size: 13pt;")  # 12pt → 13pt
        integrated_layout.addWidget(integrated_desc)

        integrated_btn_layout = QHBoxLayout()
        self.start_all_btn = QPushButton("▶️ 전체 시작")
        self.start_all_btn.setStyleSheet(
            "background-color: #4CAF50; color: white; font-weight: bold; padding: 10px; font-size: 14pt;"
        )
        self.start_all_btn.clicked.connect(self.start_all_processes)
        integrated_btn_layout.addWidget(self.start_all_btn)

        self.stop_all_btn = QPushButton("⏹️ 전체 중지")
        self.stop_all_btn.setStyleSheet(
            "background-color: #f44336; color: white; font-weight: bold; padding: 10px; font-size: 14pt;"
        )
        self.stop_all_btn.clicked.connect(self.stop_all_processes)
        integrated_btn_layout.addWidget(self.stop_all_btn)

        self.restart_all_btn = QPushButton("🔄 전체 재시작")
        self.restart_all_btn.setStyleSheet(
            "background-color: #2196F3; color: white; font-weight: bold; padding: 10px; font-size: 14pt;"
        )
        self.restart_all_btn.clicked.connect(self.restart_all_processes)
        integrated_btn_layout.addWidget(self.restart_all_btn)

        integrated_btn_layout.addStretch()
        integrated_layout.addLayout(integrated_btn_layout)

        # 프로세스 상태 표시 (5개 행 기준으로 높이 설정)
        self.process_status_table = QTableWidget()
        self.process_status_table.setColumnCount(4)
        self.process_status_table.setHorizontalHeaderLabels(
            ["프로세스", "상태", "시작 시간", "동작"]
        )
        # 헤더 높이(약 35px) + 5개 행(각 약 35px) = 약 210px
        self.process_status_table.setMinimumHeight(230)
        self.process_status_table.setMaximumHeight(240)  # 스크롤 없이 5개 행 표시
        self.process_status_table.setVerticalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )  # 스크롤바 숨김
        self.process_status_table.verticalHeader().setDefaultSectionSize(
            40
        )  # 행 높이 설정
        self.process_status_table.setStyleSheet(
            "QTableWidget { font-size: 12pt; } "
            "QHeaderView::section { font-size: 12pt; font-weight: bold; }"
        )  # 테이블 폰트 크기 증가 (5개 스크롤없이 가능한 크기)
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
        individual_label.setFont(QFont("Arial", 16, QFont.Bold))  # 14 → 16
        layout.addWidget(individual_label)

        # 개별 제어 설명
        individual_desc = QLabel(
            "※ 특정 프로세스만 개별적으로 제어합니다 (PipelineOrchestrator 통일)"
        )
        individual_desc.setStyleSheet("color: #666; font-size: 13pt;")  # 12pt → 13pt
        layout.addWidget(individual_desc)

        # Spider 제어
        spider_group = QWidget()
        spider_group.setMinimumHeight(150)  # 최소 높이 증가
        spider_layout = QVBoxLayout()
        spider_layout.setSpacing(8)

        host_layout = QHBoxLayout()
        host_label = QLabel("호스트:")
        host_label.setStyleSheet("font-size: 14pt;")
        host_layout.addWidget(host_label)
        self.host_combo = QComboBox()
        self.host_combo.setStyleSheet("font-size: 14pt;")
        host_layout.addWidget(self.host_combo)
        spider_layout.addLayout(host_layout)

        spider_layout2 = QHBoxLayout()
        spider_label = QLabel("Spider:")
        spider_label.setStyleSheet("font-size: 14pt;")
        spider_layout2.addWidget(spider_label)
        self.spider_combo = QComboBox()
        self.spider_combo.setStyleSheet("font-size: 14pt;")
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
        start_btn.setStyleSheet("font-size: 14pt;")
        start_btn.clicked.connect(self.start_spider)
        button_layout.addWidget(start_btn)

        stop_btn = QPushButton("Spider 중지")
        stop_btn.setStyleSheet("font-size: 14pt;")
        stop_btn.clicked.connect(self.stop_spider)
        button_layout.addWidget(stop_btn)

        pipeline_btn = QPushButton("파이프라인 재시작")
        pipeline_btn.setStyleSheet("font-size: 14pt;")
        pipeline_btn.clicked.connect(self.restart_pipeline)
        button_layout.addWidget(pipeline_btn)

        spider_layout.addLayout(button_layout)
        spider_group.setLayout(spider_layout)
        layout.addWidget(spider_group)

        # Kafka 제어
        kafka_group = QWidget()
        kafka_group.setMinimumHeight(130)  # 최소 높이 증가
        kafka_layout = QVBoxLayout()
        kafka_layout.setSpacing(8)

        kafka_label = QLabel("Kafka Consumer 제어")
        kafka_label.setFont(QFont("Arial", 16, QFont.Bold))  # 14 → 16
        kafka_layout.addWidget(kafka_label)

        kafka_button_layout = QHBoxLayout()
        kafka_start_btn = QPushButton("Kafka 시작")
        kafka_start_btn.setStyleSheet(
            "background-color: #4CAF50; color: white; font-weight: bold; padding: 8px; font-size: 14pt;"
        )
        kafka_start_btn.clicked.connect(self.start_kafka)
        kafka_button_layout.addWidget(kafka_start_btn)

        kafka_stop_btn = QPushButton("Kafka 중지")
        kafka_stop_btn.setStyleSheet(
            "background-color: #f44336; color: white; font-weight: bold; padding: 8px; font-size: 14pt;"
        )
        kafka_stop_btn.clicked.connect(self.stop_kafka)
        kafka_button_layout.addWidget(kafka_stop_btn)

        kafka_restart_btn = QPushButton("Kafka 재시작")
        kafka_restart_btn.setStyleSheet(
            "background-color: #2196F3; color: white; font-weight: bold; padding: 8px; font-size: 14pt;"
        )
        kafka_restart_btn.clicked.connect(self.restart_kafka)
        kafka_button_layout.addWidget(kafka_restart_btn)

        kafka_button_layout.addStretch()
        kafka_layout.addLayout(kafka_button_layout)

        # Kafka 상태 표시
        self.kafka_status_info_label = QLabel("상태: 확인 중...")
        self.kafka_status_info_label.setStyleSheet("font-size: 14pt;")
        kafka_layout.addWidget(self.kafka_status_info_label)

        kafka_group.setLayout(kafka_layout)
        layout.addWidget(kafka_group)

        # HDFS 제어
        hdfs_group = QWidget()
        hdfs_group.setMinimumHeight(130)  # 최소 높이 증가
        hdfs_layout = QVBoxLayout()
        hdfs_layout.setSpacing(8)

        hdfs_label = QLabel("HDFS 제어")
        hdfs_label.setFont(QFont("Arial", 16, QFont.Bold))  # 14 → 16
        hdfs_layout.addWidget(hdfs_label)

        hdfs_button_layout = QHBoxLayout()
        hdfs_start_btn = QPushButton("HDFS 시작")
        hdfs_start_btn.setStyleSheet(
            "background-color: #4CAF50; color: white; font-weight: bold; padding: 8px; font-size: 14pt;"
        )
        hdfs_start_btn.clicked.connect(self.start_hdfs)
        hdfs_button_layout.addWidget(hdfs_start_btn)

        hdfs_stop_btn = QPushButton("HDFS 중지")
        hdfs_stop_btn.setStyleSheet(
            "background-color: #f44336; color: white; font-weight: bold; padding: 8px; font-size: 14pt;"
        )
        hdfs_stop_btn.clicked.connect(self.stop_hdfs)
        hdfs_button_layout.addWidget(hdfs_stop_btn)

        hdfs_restart_btn = QPushButton("HDFS 재시작")
        hdfs_restart_btn.setStyleSheet(
            "background-color: #2196F3; color: white; font-weight: bold; padding: 8px; font-size: 14pt;"
        )
        hdfs_restart_btn.clicked.connect(self.restart_hdfs)
        hdfs_button_layout.addWidget(hdfs_restart_btn)

        hdfs_button_layout.addStretch()
        hdfs_layout.addLayout(hdfs_button_layout)

        # HDFS 상태 표시
        self.hdfs_status_info_label = QLabel("상태: 확인 중...")
        self.hdfs_status_info_label.setStyleSheet("font-size: 14pt;")
        hdfs_layout.addWidget(self.hdfs_status_info_label)

        hdfs_group.setLayout(hdfs_layout)
        layout.addWidget(hdfs_group)

        # 데이터 적재 제어 섹션
        data_loader_group = QWidget()
        data_loader_group.setMinimumHeight(100)  # 최소 높이 증가
        data_loader_layout = QVBoxLayout()
        data_loader_layout.setSpacing(8)

        data_loader_label = QLabel("📥 데이터 적재 제어")
        data_loader_label.setFont(QFont("Arial", 16, QFont.Bold))  # 14 → 16
        data_loader_layout.addWidget(data_loader_label)

        data_loader_btn_layout = QHBoxLayout()
        self.load_data_btn = QPushButton("🔄 HDFS → DB 적재 실행")
        self.load_data_btn.setStyleSheet(
            "background-color: #FF9800; color: white; font-weight: bold; padding: 8px; font-size: 14pt;"
        )
        self.load_data_btn.clicked.connect(self.run_data_loader)
        data_loader_btn_layout.addWidget(self.load_data_btn)

        self.load_data_status_label = QLabel("상태: 대기 중")
        self.load_data_status_label.setStyleSheet("font-size: 14pt;")
        data_loader_btn_layout.addWidget(self.load_data_status_label)
        data_loader_btn_layout.addStretch()

        data_loader_layout.addLayout(data_loader_btn_layout)
        data_loader_group.setLayout(data_loader_layout)
        layout.addWidget(data_loader_group)

        # 실시간 모니터링 섹션
        monitor_group = QWidget()
        monitor_group.setMinimumHeight(80)  # 최소 높이 증가
        monitor_layout = QVBoxLayout()
        monitor_layout.setSpacing(8)

        monitor_label = QLabel("실시간 모니터링")
        monitor_label.setFont(QFont("Arial", 16, QFont.Bold))  # 14 → 16
        monitor_layout.addWidget(monitor_label)

        # 통계 표시
        stats_layout = QHBoxLayout()
        self.spider_stats_label = QLabel("Spider: 대기 중")
        self.spider_stats_label.setStyleSheet("font-size: 14pt;")
        self.kafka_stats_label = QLabel("Kafka: 대기 중")
        self.kafka_stats_label.setStyleSheet("font-size: 14pt;")
        self.backend_stats_label = QLabel("Backend: 대기 중")
        self.backend_stats_label.setStyleSheet("font-size: 14pt;")
        stats_layout.addWidget(self.spider_stats_label)
        stats_layout.addWidget(self.kafka_stats_label)
        stats_layout.addWidget(self.backend_stats_label)
        stats_layout.addStretch()
        monitor_layout.addLayout(stats_layout)

        monitor_group.setLayout(monitor_layout)
        layout.addWidget(monitor_group)

        # 로그 섹션
        log_group = QWidget()
        log_group.setMinimumHeight(250)  # 최소 높이 증가
        log_layout = QVBoxLayout()
        log_layout.setSpacing(8)

        log_label = QLabel("실시간 로그")
        log_label.setFont(QFont("Arial", 16, QFont.Bold))  # 14 → 16
        log_layout.addWidget(log_label)

        self.control_log = QTextEdit()
        self.control_log.setReadOnly(True)
        self.control_log.setMinimumHeight(220)  # 최소 높이 증가
        self.control_log.setStyleSheet(
            "background-color: #1e1e1e; color: #d4d4d4; font-family: 'Courier New', monospace; font-size: 14pt;"
        )  # 12pt → 14pt
        log_layout.addWidget(self.control_log)

        log_group.setLayout(log_layout)
        layout.addWidget(log_group)

        # 스크롤 영역에 컨텐츠 위젯 설정
        content_widget.setLayout(layout)
        scroll_area.setWidget(content_widget)

        # 메인 레이아웃 (스크롤 영역만 포함)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)

    def start_all_processes(self):
        """전체 프로세스 시작"""
        if not self.parent_app:
            return
        if hasattr(self.parent_app, "start_all_processes"):
            self.parent_app.start_all_processes()

    def stop_all_processes(self):
        """전체 프로세스 중지"""
        if not self.parent_app:
            return
        if hasattr(self.parent_app, "stop_all_processes"):
            self.parent_app.stop_all_processes()

    def restart_all_processes(self):
        """전체 프로세스 재시작"""
        if not self.parent_app:
            return
        if hasattr(self.parent_app, "restart_all_processes"):
            self.parent_app.restart_all_processes()

    def start_spider(self):
        """Spider 시작"""
        if not self.parent_app:
            return
        if hasattr(self.parent_app, "start_spider"):
            self.parent_app.start_spider()

    def stop_spider(self):
        """Spider 중지"""
        if not self.parent_app:
            return
        if hasattr(self.parent_app, "stop_spider"):
            self.parent_app.stop_spider()

    def restart_pipeline(self):
        """파이프라인 재시작"""
        if not self.parent_app:
            return
        if hasattr(self.parent_app, "restart_pipeline"):
            self.parent_app.restart_pipeline()

    def start_kafka(self):
        """Kafka Consumer 시작"""
        if not self.parent_app:
            return
        if hasattr(self.parent_app, "start_kafka"):
            self.parent_app.start_kafka()
        else:
            # 폴백: PipelineOrchestrator를 통해 시작
            if (
                hasattr(self.parent_app, "pipeline_orchestrator")
                and self.parent_app.pipeline_orchestrator
            ):
                if hasattr(self, "control_log"):
                    self.control_log.append("▶️ Kafka Consumer 시작 중...")
                result = self.parent_app.pipeline_orchestrator.start_process(
                    "kafka_consumer", wait=False
                )
                if result.get("success"):
                    if hasattr(self, "control_log"):
                        self.control_log.append("✅ Kafka Consumer 시작 완료")
                else:
                    if hasattr(self, "control_log"):
                        self.control_log.append(
                            f"❌ Kafka Consumer 시작 실패: {result.get('error')}"
                        )

                # UI 업데이트 (상태 테이블 및 Kafka 통계)
                from PyQt5.QtCore import QTimer

                def update_ui():
                    if hasattr(self.parent_app, "_update_process_status_table"):
                        self.parent_app._update_process_status_table()
                    if hasattr(self.parent_app, "_update_kafka_stats"):
                        self.parent_app._update_kafka_stats()

                QTimer.singleShot(500, update_ui)  # 0.5초 후 업데이트

    def stop_kafka(self):
        """Kafka Consumer 중지"""
        if not self.parent_app:
            return
        if hasattr(self.parent_app, "stop_kafka"):
            self.parent_app.stop_kafka()
        else:
            # 폴백: PipelineOrchestrator를 통해 중지
            if (
                hasattr(self.parent_app, "pipeline_orchestrator")
                and self.parent_app.pipeline_orchestrator
            ):
                if hasattr(self, "control_log"):
                    self.control_log.append("⏹️ Kafka Consumer 중지 중...")
                result = self.parent_app.pipeline_orchestrator.stop_process(
                    "kafka_consumer"
                )
                if result.get("success"):
                    if hasattr(self, "control_log"):
                        self.control_log.append("✅ Kafka Consumer 중지 완료")
                else:
                    if hasattr(self, "control_log"):
                        self.control_log.append(
                            f"❌ Kafka Consumer 중지 실패: {result.get('error')}"
                        )

                # UI 업데이트 (상태 테이블 및 Kafka 통계)
                from PyQt5.QtCore import QTimer

                def update_ui():
                    if hasattr(self.parent_app, "_update_process_status_table"):
                        self.parent_app._update_process_status_table()
                    if hasattr(self.parent_app, "_update_kafka_stats"):
                        self.parent_app._update_kafka_stats()

                QTimer.singleShot(500, update_ui)  # 0.5초 후 업데이트

    def restart_kafka(self):
        """Kafka Consumer 재시작 (상태 확인 후 재시작)"""
        if not self.parent_app:
            return
        if hasattr(self.parent_app, "restart_kafka"):
            self.parent_app.restart_kafka()
        else:
            # 폴백: 중지 후 상태 확인하여 재시작
            if (
                hasattr(self.parent_app, "pipeline_orchestrator")
                and self.parent_app.pipeline_orchestrator
            ):
                if hasattr(self, "control_log"):
                    self.control_log.append("🔄 Kafka Consumer 재시작 중...")

                # 먼저 중지
                stop_result = self.parent_app.pipeline_orchestrator.stop_process(
                    "kafka_consumer"
                )

                if not stop_result.get("success"):
                    if hasattr(self, "control_log"):
                        self.control_log.append(
                            f"❌ Kafka Consumer 중지 실패: {stop_result.get('error')}"
                        )
                    return

                # 상태 확인 후 재시작
                from PyQt5.QtCore import QTimer

                def check_and_restart():
                    # 상태 확인
                    status = self.parent_app.pipeline_orchestrator.get_status()
                    kafka_status = status.get("kafka_consumer", {})
                    is_stopped = kafka_status.get("status") in [
                        "stopped",
                        "error",
                    ] or not kafka_status.get("running", False)

                    if is_stopped:
                        if hasattr(self, "control_log"):
                            self.control_log.append(
                                "⏳ Kafka Consumer 중지 확인됨. 재시작 중..."
                            )
                        self.start_kafka()
                    else:
                        # 아직 중지 중이면 다시 확인
                        if hasattr(self, "control_log"):
                            self.control_log.append("⏳ Kafka Consumer 중지 대기 중...")
                        QTimer.singleShot(1000, check_and_restart)  # 1초 후 다시 확인

                QTimer.singleShot(1000, check_and_restart)  # 1초 후 상태 확인 시작

    def start_hdfs(self):
        """HDFS 데몬 시작"""
        if not self.parent_app:
            return
        if hasattr(self.parent_app, "start_hdfs"):
            self.parent_app.start_hdfs()
        else:
            # 폴백: PipelineOrchestrator를 통해 시작
            if (
                hasattr(self.parent_app, "pipeline_orchestrator")
                and self.parent_app.pipeline_orchestrator
            ):
                if hasattr(self, "control_log"):
                    self.control_log.append("▶️ HDFS 데몬 시작 중...")
                result = self.parent_app.pipeline_orchestrator.start_process(
                    "hdfs", wait=False
                )
                if result.get("success"):
                    if hasattr(self, "control_log"):
                        self.control_log.append("✅ HDFS 데몬 시작 완료")
                else:
                    if hasattr(self, "control_log"):
                        self.control_log.append(
                            f"❌ HDFS 데몬 시작 실패: {result.get('error')}"
                        )

                # UI 업데이트 (상태 테이블 및 HDFS 통계)
                from PyQt5.QtCore import QTimer

                def update_ui():
                    if hasattr(self.parent_app, "_update_process_status_table"):
                        self.parent_app._update_process_status_table()
                    if hasattr(self.parent_app, "_update_hdfs_stats"):
                        self.parent_app._update_hdfs_stats()

                QTimer.singleShot(500, update_ui)  # 0.5초 후 업데이트

    def stop_hdfs(self):
        """HDFS 데몬 중지"""
        if not self.parent_app:
            return
        if hasattr(self.parent_app, "stop_hdfs"):
            self.parent_app.stop_hdfs()
        else:
            # 폴백: PipelineOrchestrator를 통해 중지
            if (
                hasattr(self.parent_app, "pipeline_orchestrator")
                and self.parent_app.pipeline_orchestrator
            ):
                if hasattr(self, "control_log"):
                    self.control_log.append("⏹️ HDFS 데몬 중지 중...")
                result = self.parent_app.pipeline_orchestrator.stop_process("hdfs")
                if result.get("success"):
                    if hasattr(self, "control_log"):
                        self.control_log.append("✅ HDFS 데몬 중지 완료")
                else:
                    if hasattr(self, "control_log"):
                        self.control_log.append(
                            f"❌ HDFS 데몬 중지 실패: {result.get('error')}"
                        )

                # UI 업데이트 (상태 테이블 및 HDFS 통계)
                from PyQt5.QtCore import QTimer

                def update_ui():
                    if hasattr(self.parent_app, "_update_process_status_table"):
                        self.parent_app._update_process_status_table()
                    if hasattr(self.parent_app, "_update_hdfs_stats"):
                        self.parent_app._update_hdfs_stats()

                QTimer.singleShot(500, update_ui)  # 0.5초 후 업데이트

    def restart_hdfs(self):
        """HDFS 데몬 재시작 (상태 확인 후 재시작)"""
        if not self.parent_app:
            return
        if hasattr(self.parent_app, "restart_hdfs"):
            self.parent_app.restart_hdfs()
        else:
            # 폴백: 중지 후 상태 확인하여 재시작
            if (
                hasattr(self.parent_app, "pipeline_orchestrator")
                and self.parent_app.pipeline_orchestrator
            ):
                if hasattr(self, "control_log"):
                    self.control_log.append("🔄 HDFS 데몬 재시작 중...")

                # 먼저 중지
                stop_result = self.parent_app.pipeline_orchestrator.stop_process("hdfs")

                if not stop_result.get("success"):
                    if hasattr(self, "control_log"):
                        self.control_log.append(
                            f"❌ HDFS 데몬 중지 실패: {stop_result.get('error')}"
                        )
                    return

                # 상태 확인 후 재시작
                from PyQt5.QtCore import QTimer

                def check_and_restart():
                    # 상태 확인
                    status = self.parent_app.pipeline_orchestrator.get_status()
                    hdfs_status = status.get("hdfs", {})
                    is_stopped = hdfs_status.get("status") in [
                        "stopped",
                        "error",
                    ] or not hdfs_status.get("running", False)

                    if is_stopped:
                        if hasattr(self, "control_log"):
                            self.control_log.append(
                                "⏳ HDFS 데몬 중지 확인됨. 재시작 중..."
                            )
                        self.start_hdfs()
                    else:
                        # 아직 중지 중이면 다시 확인
                        if hasattr(self, "control_log"):
                            self.control_log.append("⏳ HDFS 데몬 중지 대기 중...")
                        QTimer.singleShot(1000, check_and_restart)  # 1초 후 다시 확인

                QTimer.singleShot(1000, check_and_restart)  # 1초 후 상태 확인 시작

    def run_data_loader(self):
        """HDFS → DB 데이터 적재 실행"""
        if not self.parent_app:
            return

        # 버튼 비활성화 및 상태 업데이트
        self.load_data_btn.setEnabled(False)
        self.load_data_status_label.setText("상태: 실행 중...")
        self.load_data_status_label.setStyleSheet("color: blue; font-weight: bold;")

        # 로그에 메시지 추가
        if hasattr(self, "control_log"):
            self.control_log.append("[데이터 적재] HDFS → MariaDB 적재 시작...")

        # 메인 앱의 메서드 호출
        if hasattr(self.parent_app, "run_data_loader"):
            try:
                result = self.parent_app.run_data_loader()
                if result.get("success", False):
                    self.load_data_status_label.setText("상태: ✅ 완료")
                    self.load_data_status_label.setStyleSheet(
                        "color: green; font-weight: bold;"
                    )
                    if hasattr(self, "control_log"):
                        self.control_log.append("[데이터 적재] ✅ 데이터 적재 완료!")
                else:
                    error_msg = result.get("error", "알 수 없는 오류")
                    self.load_data_status_label.setText(
                        f"상태: ❌ 실패 ({error_msg[:30]})"
                    )
                    self.load_data_status_label.setStyleSheet(
                        "color: red; font-weight: bold;"
                    )
                    if hasattr(self, "control_log"):
                        self.control_log.append(f"[데이터 적재] ❌ 오류: {error_msg}")
            except Exception as e:
                self.load_data_status_label.setText(f"상태: ❌ 오류 발생")
                self.load_data_status_label.setStyleSheet(
                    "color: red; font-weight: bold;"
                )
                if hasattr(self, "control_log"):
                    self.control_log.append(f"[데이터 적재] ❌ 예외 발생: {str(e)}")
        else:
            self.load_data_status_label.setText("상태: ❌ 기능 미구현")
            self.load_data_status_label.setStyleSheet("color: red; font-weight: bold;")

        # 버튼 다시 활성화
        self.load_data_btn.setEnabled(True)

    def update_process_status_table(self):
        """프로세스 상태 테이블 업데이트"""
        if not self.parent_app:
            return
        if hasattr(self.parent_app, "_update_process_status_table"):
            self.parent_app._update_process_status_table()

    def update_stats(self, spider_stats=None, kafka_stats=None, backend_stats=None):
        """
        통계 업데이트

        Args:
            spider_stats: Spider 통계 텍스트
            kafka_stats: Kafka 통계 텍스트
            backend_stats: Backend 통계 텍스트
        """
        if spider_stats:
            self.spider_stats_label.setText(spider_stats)
        if kafka_stats:
            self.kafka_stats_label.setText(kafka_stats)
        if backend_stats:
            self.backend_stats_label.setText(backend_stats)
