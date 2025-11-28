"""
Tier2 서버 탭
백엔드 서버 상태를 모니터링하는 탭
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit
import json


class Tier2Tab(QWidget):
    """Tier2 서버 탭 클래스"""

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

        self.setLayout(layout)

    def refresh_tier2(self):
        """Tier2 서버 상태 새로고침"""
        if not self.parent_app:
            return

        # 부모 앱의 refresh_tier2 메서드 호출
        if hasattr(self.parent_app, "refresh_tier2"):
            self.parent_app.refresh_tier2()

        # 상태 텍스트 업데이트
        if not self.parent_app.tier2_monitor:
            return

        try:
            status = self.parent_app.tier2_monitor.get_server_status()
            summary = self.parent_app.tier2_monitor.get_dashboard_summary()

            status_text = json.dumps(status, indent=2, ensure_ascii=False)
            if summary and summary.get("success"):
                status_text += "\n\n=== 대시보드 요약 ===\n"
                status_text += json.dumps(
                    summary.get("data", {}), indent=2, ensure_ascii=False
                )

            self.tier2_status_text.setPlainText(status_text)
        except Exception as e:
            from shared.logger import setup_logger

            logger = setup_logger(__name__)
            logger.error(f"Tier2 상태 표시 실패: {e}")

    def generate_insights(self):
        """인사이트 생성"""
        if not self.parent_app or not self.parent_app.tier2_monitor:
            return

        from PyQt5.QtWidgets import QMessageBox

        result = self.parent_app.tier2_monitor.generate_insights()
        if result.get("success"):
            QMessageBox.information(self, "성공", "인사이트 생성이 완료되었습니다.")
        else:
            QMessageBox.warning(
                self,
                "실패",
                f"인사이트 생성 실패: {result.get('error', '알 수 없는 오류')}",
            )
