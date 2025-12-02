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

        # 데이터 적재 제어 섹션
        data_loader_group = QWidget()
        data_loader_layout = QVBoxLayout()

        data_loader_label = QLabel("📥 데이터 적재 제어")
        data_loader_label.setFont(QFont("Arial", 10, QFont.Bold))
        data_loader_layout.addWidget(data_loader_label)

        data_loader_btn_layout = QHBoxLayout()
        self.load_data_btn = QPushButton("🔄 HDFS → DB 적재 실행")
        self.load_data_btn.setStyleSheet(
            "background-color: #FF9800; color: white; font-weight: bold; padding: 8px;"
        )
        self.load_data_btn.clicked.connect(self.run_data_loader)
        data_loader_btn_layout.addWidget(self.load_data_btn)

        self.load_data_status_label = QLabel("상태: 대기 중")
        data_loader_btn_layout.addWidget(self.load_data_status_label)
        data_loader_btn_layout.addStretch()

        data_loader_layout.addLayout(data_loader_btn_layout)
        data_loader_group.setLayout(data_loader_layout)
        layout.addWidget(data_loader_group)

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

        self.setLayout(layout)

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
                    self.load_data_status_label.setStyleSheet("color: green; font-weight: bold;")
                    if hasattr(self, "control_log"):
                        self.control_log.append("[데이터 적재] ✅ 데이터 적재 완료!")
                else:
                    error_msg = result.get("error", "알 수 없는 오류")
                    self.load_data_status_label.setText(f"상태: ❌ 실패 ({error_msg[:30]})")
                    self.load_data_status_label.setStyleSheet("color: red; font-weight: bold;")
                    if hasattr(self, "control_log"):
                        self.control_log.append(f"[데이터 적재] ❌ 오류: {error_msg}")
            except Exception as e:
                self.load_data_status_label.setText(f"상태: ❌ 오류 발생")
                self.load_data_status_label.setStyleSheet("color: red; font-weight: bold;")
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
