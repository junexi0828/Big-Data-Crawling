"""
대시보드 탭
시스템 요약 정보를 표시하는 탭
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit
from PyQt5.QtGui import QFont


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
