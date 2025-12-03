"""
클러스터 모니터링 탭
클러스터 노드 상태를 모니터링하는 탭
"""

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
)
from PyQt5.QtCore import Qt


class ClusterTab(QWidget):
    """클러스터 모니터링 탭 클래스"""

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

        self.setLayout(layout)

    def refresh_cluster(self):
        """클러스터 상태 새로고침"""
        if not self.parent_app or not self.parent_app.cluster_monitor:
            return

        try:
            nodes = self.parent_app.cluster_monitor.get_all_nodes_status()

            self.cluster_table.setRowCount(len(nodes))
            for i, node in enumerate(nodes):
                self.cluster_table.setItem(
                    i, 0, QTableWidgetItem(node.get("host", "N/A"))
                )
                self.cluster_table.setItem(
                    i,
                    1,
                    QTableWidgetItem("온라인" if node.get("online") else "오프라인"),
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

            if self.parent_app:
                self.parent_app.statusBar().showMessage(
                    "클러스터 상태 업데이트 완료", 3000
                )
        except Exception as e:
            from shared.logger import setup_logger

            logger = setup_logger(__name__)
            logger.error(f"클러스터 새로고침 실패: {e}")
            if self.parent_app:
                self.parent_app.statusBar().showMessage(f"오류: {str(e)}", 5000)

    def show_hdfs_status(self):
        """HDFS 상태 표시"""
        if not self.parent_app or not self.parent_app.cluster_monitor:
            return

        status = self.parent_app.cluster_monitor.get_hdfs_status()
        QMessageBox.information(
            self, "HDFS 상태", status.get("report", "상태를 가져올 수 없습니다.")
        )
