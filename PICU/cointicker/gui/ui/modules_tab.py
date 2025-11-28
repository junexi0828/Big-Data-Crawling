"""
모듈 관리 탭
시스템 모듈을 관리하는 탭
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


class ModulesTab(QWidget):
    """모듈 관리 탭 클래스"""

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
        load_btn = QPushButton("모듈 로드")
        load_btn.clicked.connect(self.load_modules)
        button_layout.addWidget(load_btn)

        refresh_btn = QPushButton("상태 새로고침")
        refresh_btn.clicked.connect(self.refresh_modules)
        button_layout.addWidget(refresh_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        # 모듈 테이블
        self.modules_table = QTableWidget()
        self.modules_table.setColumnCount(3)
        self.modules_table.setHorizontalHeaderLabels(["모듈 이름", "상태", "설정"])
        layout.addWidget(self.modules_table)

        self.setLayout(layout)

    def load_modules(self):
        """모듈 로드"""
        if not self.parent_app:
            return

        if hasattr(self.parent_app, "load_modules"):
            self.parent_app.load_modules()
        if hasattr(self.parent_app, "refresh_modules"):
            self.parent_app.refresh_modules()
        QMessageBox.information(self, "완료", "모듈이 로드되었습니다.")

    def refresh_modules(self):
        """모듈 상태 새로고침"""
        if not self.parent_app or not self.parent_app.module_manager:
            return

        modules = self.parent_app.module_manager.get_all_modules_status()

        self.modules_table.setRowCount(len(modules))
        for i, module in enumerate(modules):
            self.modules_table.setItem(
                i, 0, QTableWidgetItem(module.get("name", "N/A"))
            )
            self.modules_table.setItem(
                i, 1, QTableWidgetItem(module.get("status", "N/A"))
            )
            self.modules_table.setItem(
                i, 2, QTableWidgetItem(str(len(module.get("config", {}))))
            )
