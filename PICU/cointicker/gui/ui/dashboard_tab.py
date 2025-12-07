"""
대시보드 탭
시스템 요약 정보를 표시하는 탭
"""

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QProgressBar,
    QGroupBox,
    QGridLayout,
)
from PyQt5.QtGui import QFont, QColor, QPainter, QPen
from PyQt5.QtCore import Qt

from gui.ui.pipeline_status_widget import PipelineStatusWidget


class DashboardTab(QWidget):
    """대시보드 탭 클래스"""

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

        # 시스템 자원 모니터링 섹션 (psutil 사용 가능 시)
        if (
            hasattr(self.parent_app, "system_monitor")
            and self.parent_app.system_monitor
            and self.parent_app.system_monitor.available
        ):
            resource_group = QGroupBox("시스템 자원")
            resource_layout = QGridLayout()

            # CPU
            cpu_label = QLabel("CPU:")
            self.cpu_progress = QProgressBar()
            self.cpu_progress.setRange(0, 100)
            self.cpu_progress.setFixedWidth(200)
            self.cpu_progress.setTextVisible(True)
            self.cpu_progress.setFormat("%p%")

            # 메모리
            mem_label = QLabel("메모리:")
            self.mem_progress = QProgressBar()
            self.mem_progress.setRange(0, 100)
            self.mem_progress.setFixedWidth(200)
            self.mem_progress.setTextVisible(True)
            self.mem_progress.setFormat("%p%")

            # 디스크
            disk_label = QLabel("디스크:")
            self.disk_progress = QProgressBar()
            self.disk_progress.setRange(0, 100)
            self.disk_progress.setFixedWidth(200)
            self.disk_progress.setTextVisible(True)
            self.disk_progress.setFormat("%p%")

            # 네트워크 (텍스트로 표시)
            self.network_label = QLabel("네트워크: -")
            self.network_label.setToolTip("네트워크 I/O 정보")

            # 프로세스 수
            self.process_label = QLabel("프로세스: -")

            resource_layout.addWidget(cpu_label, 0, 0)
            resource_layout.addWidget(self.cpu_progress, 0, 1)
            resource_layout.addWidget(mem_label, 0, 2)
            resource_layout.addWidget(self.mem_progress, 0, 3)
            resource_layout.addWidget(disk_label, 1, 0)
            resource_layout.addWidget(self.disk_progress, 1, 1)
            resource_layout.addWidget(self.network_label, 1, 2)
            resource_layout.addWidget(self.process_label, 1, 3)

            resource_group.setLayout(resource_layout)
            layout.addWidget(resource_group)

        # 파이프라인 모니터링 섹션
        pipeline_group = QGroupBox("파이프라인 모니터링")
        pipeline_layout = QVBoxLayout()

        # 파이프라인 단계별 상태
        self.pipeline_status_widget = PipelineStatusWidget()
        pipeline_layout.addWidget(self.pipeline_status_widget)

        # 컴포넌트별 통계
        stats_layout = QGridLayout()

        # Spider 통계
        self.spider_status_label = QLabel("Spider: -")
        self.spider_items_label = QLabel("수집 아이템: 0")

        # Kafka 통계
        self.kafka_status_label = QLabel("Kafka: -")
        self.kafka_messages_label = QLabel("처리 메시지: 0")
        self.kafka_rate_label = QLabel("소비율: 0 msg/s")
        self.kafka_groups_label = QLabel("Consumer Groups: -")

        # HDFS 통계
        self.hdfs_status_label = QLabel("HDFS: -")
        self.hdfs_files_label = QLabel("저장 파일: -")

        # Backend/Frontend 통계
        self.backend_status_label = QLabel("Backend: -")
        self.frontend_status_label = QLabel("Frontend: -")

        # Selenium 통계
        self.selenium_status_label = QLabel("Selenium: -")

        stats_layout.addWidget(QLabel("스파이더:"), 0, 0)
        stats_layout.addWidget(self.spider_status_label, 0, 1)
        stats_layout.addWidget(self.spider_items_label, 0, 2)

        stats_layout.addWidget(QLabel("Kafka:"), 0, 3)
        stats_layout.addWidget(self.kafka_status_label, 0, 4)
        stats_layout.addWidget(self.kafka_messages_label, 0, 5)
        stats_layout.addWidget(self.kafka_rate_label, 0, 6)
        stats_layout.addWidget(self.kafka_groups_label, 0, 7)

        stats_layout.addWidget(QLabel("HDFS:"), 1, 0)
        stats_layout.addWidget(self.hdfs_status_label, 1, 1)
        stats_layout.addWidget(self.hdfs_files_label, 1, 2)

        stats_layout.addWidget(QLabel("Backend:"), 1, 3)
        stats_layout.addWidget(self.backend_status_label, 1, 4)

        stats_layout.addWidget(QLabel("Frontend:"), 1, 5)
        stats_layout.addWidget(self.frontend_status_label, 1, 6)

        stats_layout.addWidget(QLabel("Selenium:"), 2, 0)
        stats_layout.addWidget(self.selenium_status_label, 2, 1)

        pipeline_layout.addLayout(stats_layout)
        pipeline_group.setLayout(pipeline_layout)
        layout.addWidget(pipeline_group)

        # 요약 정보
        summary_label = QLabel("시스템 요약")
        summary_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(summary_label)

        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        layout.addWidget(self.summary_text)

        self.setLayout(layout)

    def update_summary(self, summary: str):
        """
        요약 정보 업데이트

        Args:
            summary: 요약 텍스트
        """
        self.summary_text.setPlainText(summary)

    def update_resource_display(self, stats: dict):
        """
        시스템 자원 정보 업데이트 (DashboardTab 내부)

        Args:
            stats: 시스템 통계 딕셔너리
        """
        if not hasattr(self, "cpu_progress") or not hasattr(self, "mem_progress"):
            return

        try:
            if not stats.get("success"):
                return

            # CPU 정보 업데이트
            cpu_percent = stats.get("cpu_percent", 0)
            self.cpu_progress.setValue(int(cpu_percent))
            self._update_progress_bar_style(self.cpu_progress, cpu_percent)

            # 메모리 정보 업데이트
            mem_percent = stats.get("memory_percent", 0)
            mem_used_gb = stats.get("memory_used_gb", 0)
            mem_total_gb = stats.get("memory_total_gb", 0)
            self.mem_progress.setValue(int(mem_percent))
            self.mem_progress.setToolTip(
                f"메모리: {mem_used_gb}GB / {mem_total_gb}GB 사용 중"
            )
            self._update_progress_bar_style(self.mem_progress, mem_percent)

            # 디스크 정보 업데이트
            if hasattr(self, "disk_progress"):
                disk_percent = stats.get("disk_percent")
                if disk_percent is not None:
                    self.disk_progress.setValue(int(disk_percent))
                    disk_used_gb = stats.get("disk_used_gb", 0)
                    disk_total_gb = stats.get("disk_total_gb", 0)
                    self.disk_progress.setToolTip(
                        f"디스크: {disk_used_gb}GB / {disk_total_gb}GB 사용 중"
                    )
                    self._update_progress_bar_style(self.disk_progress, disk_percent)

            # 네트워크 정보 업데이트
            if hasattr(self, "network_label"):
                net_sent = stats.get("network_sent_mb")
                net_recv = stats.get("network_recv_mb")
                if net_sent is not None and net_recv is not None:
                    self.network_label.setText(f"네트워크: ↑{net_sent}MB ↓{net_recv}MB")
                    self.network_label.setToolTip(
                        f"전송: {net_sent}MB, 수신: {net_recv}MB"
                    )

            # 프로세스 수 업데이트
            if hasattr(self, "process_label"):
                process_count = stats.get("process_count")
                if process_count is not None:
                    self.process_label.setText(f"프로세스: {process_count}개")
        except Exception as e:
            # 조용히 실패
            pass

    def update_pipeline_status(self, pipeline_data: dict):
        """
        파이프라인 상태 업데이트

        Args:
            pipeline_data: 파이프라인 통계 딕셔너리
        """
        try:
            # Spider 상태
            spiders = pipeline_data.get("spiders", {})
            running_spiders = sum(
                1 for s in spiders.values() if s.get("status") == "running"
            )
            total_items = sum(
                s.get("stats", {}).get("items_processed", 0) for s in spiders.values()
            )
            self.spider_status_label.setText(
                f"Spider: 실행 중 {running_spiders}/{len(spiders)}개"
            )
            self.spider_items_label.setText(f"수집 아이템: {total_items}개")

            # Kafka 상태
            kafka_status = pipeline_data.get("kafka", {})
            kafka_running = kafka_status.get("running", False)
            kafka_connected = kafka_status.get("connected", False)
            kafka_service_status = kafka_status.get("service_status", "unknown")
            kafka_processed = kafka_status.get("processed_count", 0)
            kafka_rate = kafka_status.get("messages_per_second", 0.0)
            kafka_pid = kafka_status.get("pid")  # PID 추가
            consumer_groups = kafka_status.get("consumer_groups", {})

            # 실제 연결 상태를 반영하여 표시 (PID 포함)
            if kafka_connected:
                status_text = f"Kafka: 실행 중 (PID: {kafka_pid})" if kafka_pid else "Kafka: 실행 중"
            elif kafka_status.get("process_running", False):
                # 프로세스는 실행 중이지만 연결되지 않음
                pid_text = f", PID: {kafka_pid}" if kafka_pid else ""
                status_text = f"Kafka: 연결 중... (상태: {kafka_service_status}{pid_text})"
            else:
                status_text = "Kafka: 중지됨"

            self.kafka_status_label.setText(status_text)
            self.kafka_messages_label.setText(f"처리 메시지: {kafka_processed}개")

            # Kafka 소비율 표시
            if kafka_rate > 0:
                self.kafka_rate_label.setText(f"소비율: {kafka_rate:.2f} msg/s")
            else:
                self.kafka_rate_label.setText("소비율: 0 msg/s")

            # Consumer Groups 상태 표시
            if consumer_groups and not consumer_groups.get("error"):
                group_id = kafka_status.get("group_id", "unknown")
                subscription = consumer_groups.get("subscription", [])
                num_partitions = consumer_groups.get("num_partitions", 0)
                if subscription:
                    # subscription과 partitions 모두 있는 경우
                    self.kafka_groups_label.setText(
                        f"Groups: {group_id} ({len(subscription)} topics, {num_partitions} partitions)"
                    )
                elif num_partitions > 0:
                    # partitions만 있는 경우 (subscription은 아직 파싱되지 않았을 수 있음)
                    self.kafka_groups_label.setText(
                        f"Groups: {group_id} ({num_partitions} partitions)"
                    )
                else:
                    # 정보가 불완전한 경우
                    self.kafka_groups_label.setText(f"Groups: {group_id} (구독 중...)")
            else:
                # consumer_groups가 없거나 에러인 경우
                group_id = kafka_status.get("group_id", "unknown")
                self.kafka_groups_label.setText(f"Consumer Groups: {group_id} (정보 없음)")

            # HDFS 상태
            hdfs_status = pipeline_data.get("hdfs", {})
            hdfs_running = hdfs_status.get("running", False)
            hdfs_connected = hdfs_status.get("connected", False)
            pending_files = hdfs_status.get("pending_files_count", 0)

            # HDFS 연결 상태 표시
            if hdfs_connected:
                status_text = "HDFS: 연결됨"
            else:
                status_text = "HDFS: 연결 안됨"
                if pending_files > 0:
                    status_text += f" (대기 파일: {pending_files}개)"

            self.hdfs_status_label.setText(status_text)

            # 저장된 파일 수 표시 (우선순위: saved_files_count > files)
            saved_files = hdfs_status.get("saved_files_count", 0)
            if saved_files > 0:
                self.hdfs_files_label.setText(f"저장 파일: {saved_files}개")
            elif pending_files > 0:
                self.hdfs_files_label.setText(
                    f"대기 파일: {pending_files}개 (자동 업로드 대기 중)"
                )
            else:
                files_display = hdfs_status.get("files", "-")
                if files_display == "-":
                    self.hdfs_files_label.setText("저장 파일: -")
                else:
                    self.hdfs_files_label.setText(f"저장 파일: {files_display}")

            # Backend/Frontend 상태
            backend_status = pipeline_data.get("backend", {})
            backend_running = backend_status.get("running", False)
            self.backend_status_label.setText(
                f"Backend: {'온라인' if backend_running else '오프라인'}"
            )

            frontend_status = pipeline_data.get("frontend", {})
            frontend_running = frontend_status.get("running", False)
            self.frontend_status_label.setText(
                f"Frontend: {'온라인' if frontend_running else '오프라인'}"
            )

            # Selenium 상태
            selenium_enabled = pipeline_data.get("selenium", {}).get("enabled", False)
            self.selenium_status_label.setText(
                f"Selenium: {'활성화' if selenium_enabled else '비활성화'}"
            )

            # 파이프라인 플로우 업데이트
            if hasattr(self, "pipeline_status_widget"):
                self.pipeline_status_widget.update_status(pipeline_data)
        except Exception as e:
            pass

    def _update_progress_bar_style(self, progress_bar: QProgressBar, value: float):
        """값에 따라 프로그레스 바의 색상을 변경합니다."""
        try:
            if value > 90:
                style = "QProgressBar::chunk { background-color: #d9534f; }"
            elif value > 75:
                style = "QProgressBar::chunk { background-color: #f0ad4e; }"
            else:
                style = "QProgressBar::chunk { background-color: #5cb85c; }"
            progress_bar.setStyleSheet(style)
        except Exception:
            pass
