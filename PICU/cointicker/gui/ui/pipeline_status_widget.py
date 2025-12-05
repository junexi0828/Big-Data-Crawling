"""
파이프라인 상태 시각화 위젯
파이프라인 단계별 흐름을 시각적으로 표시
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QPainter, QPen, QColor, QFont
from PyQt5.QtCore import Qt


class PipelineStatusWidget(QWidget):
    """파이프라인 단계별 상태를 시각화하는 위젯"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(120)
        self.setMaximumHeight(150)

        # 파이프라인 단계별 상태
        self.stages = {
            "spider": {
                "name": "Spider",
                "status": "unknown",
                "color": QColor(100, 100, 100),
            },
            "kafka": {
                "name": "Kafka",
                "status": "unknown",
                "color": QColor(100, 100, 100),
            },
            "hdfs": {
                "name": "HDFS",
                "status": "unknown",
                "color": QColor(100, 100, 100),
            },
            "mapreduce": {
                "name": "MapReduce",
                "status": "unknown",
                "color": QColor(100, 100, 100),
            },
            "backend": {
                "name": "Backend",
                "status": "unknown",
                "color": QColor(100, 100, 100),
            },
            "frontend": {
                "name": "Frontend",
                "status": "unknown",
                "color": QColor(100, 100, 100),
            },
        }

    def update_status(self, pipeline_data: dict):
        """
        파이프라인 상태 업데이트

        Args:
            pipeline_data: 파이프라인 통계 딕셔너리
        """
        # Spider 상태
        spiders = pipeline_data.get("spiders", {})
        running_spiders = sum(
            1 for s in spiders.values() if s.get("status") == "running"
        )
        if running_spiders > 0:
            self.stages["spider"]["status"] = "running"
            self.stages["spider"]["color"] = QColor(92, 184, 92)  # 초록색
        else:
            self.stages["spider"]["status"] = "stopped"
            self.stages["spider"]["color"] = QColor(217, 83, 79)  # 빨간색

        # Kafka 상태
        kafka_running = pipeline_data.get("kafka", {}).get("running", False)
        if kafka_running:
            self.stages["kafka"]["status"] = "running"
            self.stages["kafka"]["color"] = QColor(92, 184, 92)
        else:
            self.stages["kafka"]["status"] = "stopped"
            self.stages["kafka"]["color"] = QColor(240, 173, 78)  # 주황색 (선택적)

        # HDFS 상태
        hdfs_running = pipeline_data.get("hdfs", {}).get("running", False)
        if hdfs_running:
            self.stages["hdfs"]["status"] = "running"
            self.stages["hdfs"]["color"] = QColor(92, 184, 92)
        else:
            self.stages["hdfs"]["status"] = "stopped"
            self.stages["hdfs"]["color"] = QColor(240, 173, 78)  # 주황색 (선택적)

        # MapReduce 상태 (간단히 표시)
        mapreduce_running = pipeline_data.get("mapreduce", {}).get("running", False)
        if mapreduce_running:
            self.stages["mapreduce"]["status"] = "running"
            self.stages["mapreduce"]["color"] = QColor(92, 184, 92)
        else:
            self.stages["mapreduce"]["status"] = "stopped"
            self.stages["mapreduce"]["color"] = QColor(100, 100, 100)

        # Backend 상태
        backend_running = pipeline_data.get("backend", {}).get("running", False)
        if backend_running:
            self.stages["backend"]["status"] = "running"
            self.stages["backend"]["color"] = QColor(92, 184, 92)
        else:
            self.stages["backend"]["status"] = "stopped"
            self.stages["backend"]["color"] = QColor(217, 83, 79)

        # Frontend 상태
        frontend_running = pipeline_data.get("frontend", {}).get("running", False)
        if frontend_running:
            self.stages["frontend"]["status"] = "running"
            self.stages["frontend"]["color"] = QColor(92, 184, 92)
        else:
            self.stages["frontend"]["status"] = "stopped"
            self.stages["frontend"]["color"] = QColor(217, 83, 79)

        self.update()  # 위젯 다시 그리기

    def paintEvent(self, event):
        """위젯 그리기"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        width = self.width()
        height = self.height()
        stage_count = len(self.stages)
        stage_width = (width - 40) / stage_count
        stage_height = height - 40
        y_start = 20

        # 단계별 박스 그리기
        x = 20
        stage_list = list(self.stages.values())

        for i, stage in enumerate(stage_list):
            # 박스 그리기
            color = stage["color"]
            painter.setPen(QPen(color, 2))
            painter.setBrush(color.lighter(150))
            painter.drawRoundedRect(
                int(x), int(y_start), int(stage_width - 10), int(stage_height), 5, 5
            )

            # 텍스트 그리기
            painter.setPen(QColor(0, 0, 0))
            font = QFont("Arial", 9, QFont.Bold)
            painter.setFont(font)
            text_rect = painter.fontMetrics().boundingRect(stage["name"])
            text_x = x + (stage_width - 10) / 2 - text_rect.width() / 2
            text_y = y_start + stage_height / 2 - text_rect.height() / 2
            painter.drawText(
                int(text_x), int(text_y + text_rect.height()), stage["name"]
            )

            # 상태 표시
            status_text = "●" if stage["status"] == "running" else "○"
            status_font = QFont("Arial", 12)
            painter.setFont(status_font)
            status_rect = painter.fontMetrics().boundingRect(status_text)
            status_x = x + (stage_width - 10) / 2 - status_rect.width() / 2
            status_y = y_start + stage_height / 2 + 15
            painter.setPen(color)
            painter.drawText(int(status_x), int(status_y), status_text)

            # 화살표 그리기 (마지막 단계 제외)
            if i < len(stage_list) - 1:
                arrow_x = x + stage_width - 10
                arrow_y = y_start + stage_height / 2
                painter.setPen(QPen(QColor(100, 100, 100), 2))
                painter.drawLine(
                    int(arrow_x), int(arrow_y), int(arrow_x + 10), int(arrow_y)
                )
                # 화살표 머리
                painter.drawLine(
                    int(arrow_x + 10), int(arrow_y), int(arrow_x + 7), int(arrow_y - 3)
                )
                painter.drawLine(
                    int(arrow_x + 10), int(arrow_y), int(arrow_x + 7), int(arrow_y + 3)
                )

            x += stage_width

        painter.end()
