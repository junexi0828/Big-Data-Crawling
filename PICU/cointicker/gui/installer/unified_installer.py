"""
통합 설치 마법사
설치부터 실행까지 자동화된 통합 설치 도구
"""

import sys
import subprocess
import threading
from pathlib import Path
from typing import Optional

try:
    from PyQt5.QtWidgets import (
        QApplication,
        QMainWindow,
        QWidget,
        QVBoxLayout,
        QHBoxLayout,
        QLabel,
        QPushButton,
        QProgressBar,
        QTextEdit,
        QCheckBox,
        QMessageBox,
    )
    from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer

    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False

try:
    import tkinter as tk
    from tkinter import ttk, messagebox, scrolledtext

    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False

# 통합 경로 설정 유틸리티 사용
# unified_installer는 PyQt5/tkinter를 먼저 import하므로 나중에 경로 설정
# 먼저 기본 경로만 설정하여 path_utils를 import 가능하게 함
current_path = Path(__file__).resolve()
if "PICU" in current_path.parts:
    picu_index = current_path.parts.index("PICU")
    PROJECT_ROOT = Path("/").joinpath(*current_path.parts[: picu_index + 1])
    COINTICKER_ROOT = PROJECT_ROOT / "cointicker"
else:
    cointicker_index = current_path.parts.index("cointicker")
    PROJECT_ROOT = Path("/").joinpath(*current_path.parts[: cointicker_index - 1])
    COINTICKER_ROOT = Path("/").joinpath(*current_path.parts[: cointicker_index + 1])

# 경로를 먼저 설정한 후 import 시도
paths_to_add = [
    str(COINTICKER_ROOT),
    str(COINTICKER_ROOT / "shared"),
]
for path in paths_to_add:
    if path not in sys.path:
        sys.path.insert(0, path)

# path_utils를 사용하여 전체 경로 설정 (실패 시 하드코딩 경로 유지)
try:
    from shared.path_utils import (
        setup_pythonpath,
        get_project_root,
        get_cointicker_root,
    )

    setup_pythonpath()  # 전체 경로 설정 (중복 방지)
    # path_utils에서 가져온 경로로 업데이트
    PROJECT_ROOT = get_project_root()
    COINTICKER_ROOT = get_cointicker_root()
except (ImportError, Exception):
    # Fallback: 하드코딩된 경로 사용 (이미 위에서 설정됨)
    # 추가 경로만 설정
    additional_paths = [
        str(COINTICKER_ROOT / "worker-nodes"),
        str(COINTICKER_ROOT / "backend"),
        str(COINTICKER_ROOT / "worker-nodes" / "mapreduce"),
    ]
    for path in additional_paths:
        if path not in sys.path:
            sys.path.insert(0, path)

from gui.installer.installer import DependencyInstaller
from shared.logger import setup_logger

logger = setup_logger(__name__)


if PYQT5_AVAILABLE:

    class InstallThread(QThread):
        """설치 스레드"""

        progress_update = pyqtSignal(str, int)
        finished = pyqtSignal(dict)

        def __init__(self, create_venv: bool = True):
            super().__init__()
            self.create_venv = create_venv
            self.installer = DependencyInstaller(str(PROJECT_ROOT))

        def run(self):
            """설치 실행"""
            try:
                # 설치 진행 상황을 콜백으로 전달
                def progress_callback(message: str, percent: int):
                    self.progress_update.emit(message, percent)

                result = self.installer.run_full_installation(
                    create_venv=self.create_venv, progress_callback=progress_callback
                )
                self.finished.emit(result)
            except Exception as e:
                logger.error(f"설치 중 오류 발생: {e}")
                self.finished.emit({"success": False, "errors": [str(e)]})

    class UnifiedInstallerWindow(QMainWindow):
        """통합 설치 마법사 창"""

        def __init__(self):
            super().__init__()
            self.install_thread: Optional[InstallThread] = None
            self.auto_launch = True
            self.init_ui()

        def init_ui(self):
            """UI 초기화"""
            self.setWindowTitle("PICU 통합 설치 마법사")
            self.setGeometry(100, 100, 800, 600)

            # 중앙 위젯
            central_widget = QWidget()
            self.setCentralWidget(central_widget)

            # 레이아웃
            layout = QVBoxLayout()
            central_widget.setLayout(layout)

            # 제목
            title = QLabel("🪙 PICU 프로젝트 통합 설치")
            title.setStyleSheet("font-size: 24px; font-weight: bold; padding: 20px;")
            title.setAlignment(Qt.AlignCenter)
            layout.addWidget(title)

            # 설명
            description = QLabel(
                "이 마법사는 PICU 프로젝트의 모든 의존성을 자동으로 설치하고\n"
                "설치 완료 후 애플리케이션을 자동으로 실행합니다."
            )
            description.setAlignment(Qt.AlignCenter)
            description.setWordWrap(True)
            layout.addWidget(description)

            # 옵션
            options_layout = QHBoxLayout()
            self.venv_checkbox = QCheckBox("가상환경 생성 (권장)")
            self.venv_checkbox.setChecked(True)
            options_layout.addWidget(self.venv_checkbox)

            self.auto_launch_checkbox = QCheckBox("설치 완료 후 자동 실행")
            self.auto_launch_checkbox.setChecked(True)
            options_layout.addWidget(self.auto_launch_checkbox)

            options_layout.addStretch()
            layout.addLayout(options_layout)

            # 진행 바
            self.progress_bar = QProgressBar()
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(0)
            layout.addWidget(self.progress_bar)

            # 상태 레이블
            self.status_label = QLabel("준비 완료")
            self.status_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(self.status_label)

            # 로그 영역
            log_label = QLabel("설치 로그:")
            layout.addWidget(log_label)

            self.log_text = QTextEdit()
            self.log_text.setReadOnly(True)
            self.log_text.setMaximumHeight(200)
            layout.addWidget(self.log_text)

            # 버튼
            button_layout = QHBoxLayout()
            button_layout.addStretch()

            self.install_button = QPushButton("🚀 설치 시작")
            self.install_button.setStyleSheet("font-size: 14px; padding: 10px 20px;")
            self.install_button.clicked.connect(self.start_installation)
            button_layout.addWidget(self.install_button)

            self.close_button = QPushButton("닫기")
            self.close_button.clicked.connect(self.close)
            button_layout.addWidget(self.close_button)

            layout.addLayout(button_layout)

        def start_installation(self):
            """설치 시작"""
            self.install_button.setEnabled(False)
            self.log_text.clear()
            self.progress_bar.setValue(0)
            self.status_label.setText("설치 중...")

            create_venv = self.venv_checkbox.isChecked()
            self.auto_launch = self.auto_launch_checkbox.isChecked()

            # 설치 스레드 시작
            self.install_thread = InstallThread(create_venv=create_venv)
            self.install_thread.progress_update.connect(self.update_progress)
            self.install_thread.finished.connect(self.installation_finished)
            self.install_thread.start()

        def update_progress(self, message: str, percent: int):
            """진행 상황 업데이트"""
            self.log_text.append(f"[{percent}%] {message}")
            self.progress_bar.setValue(percent)
            self.status_label.setText(message)
            QApplication.processEvents()

        def installation_finished(self, result: dict):
            """설치 완료"""
            self.install_button.setEnabled(True)
            self.progress_bar.setValue(100)

            if result.get("success"):
                self.status_label.setText("✅ 설치 완료!")
                self.log_text.append("\n✅ 설치가 성공적으로 완료되었습니다!")

                if self.auto_launch:
                    QMessageBox.information(
                        self,
                        "설치 완료",
                        "설치가 완료되었습니다.\n"
                        "애플리케이션을 자동으로 실행합니다.",
                    )
                    self.launch_application()
                else:
                    QMessageBox.information(
                        self,
                        "설치 완료",
                        "설치가 완료되었습니다.\n"
                        "애플리케이션을 실행하려면 'GUI 실행' 버튼을 클릭하세요.",
                    )
            else:
                self.status_label.setText("❌ 설치 실패")
                errors = result.get("errors", [])
                error_msg = "\n".join(f"  - {e}" for e in errors)
                self.log_text.append(f"\n❌ 설치 중 오류가 발생했습니다:\n{error_msg}")

                QMessageBox.critical(
                    self, "설치 실패", f"설치 중 오류가 발생했습니다:\n\n{error_msg}"
                )

        def launch_application(self):
            """애플리케이션 실행"""
            try:
                self.log_text.append("\n🚀 애플리케이션 실행 중...")
                self.status_label.setText("애플리케이션 실행 중...")

                # GUI 실행
                venv_python = PROJECT_ROOT / "venv" / "bin" / "python"
                if not venv_python.exists():
                    venv_python = Path(sys.executable)

                gui_script = PROJECT_ROOT / "cointicker" / "gui" / "main.py"
                subprocess.Popen(
                    [str(venv_python), str(gui_script)],
                    cwd=str(PROJECT_ROOT),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )

                self.log_text.append("✅ 애플리케이션이 실행되었습니다!")
                self.status_label.setText("✅ 애플리케이션 실행 완료")

                # 2초 후 창 닫기
                QTimer.singleShot(2000, self.close)

            except Exception as e:
                logger.error(f"애플리케이션 실행 실패: {e}")
                self.log_text.append(f"❌ 애플리케이션 실행 실패: {e}")
                QMessageBox.warning(
                    self, "실행 실패", f"애플리케이션 실행 중 오류가 발생했습니다:\n{e}"
                )

    def run_unified_installer():
        """통합 설치 마법사 실행"""
        app = QApplication(sys.argv)
        window = UnifiedInstallerWindow()
        window.show()
        sys.exit(app.exec_())

elif TKINTER_AVAILABLE:

    class UnifiedInstallerWindow:
        """Tkinter 기반 통합 설치 마법사"""

        def __init__(self, root):
            self.root = root
            self.root.title("PICU 통합 설치 마법사")
            self.root.geometry("800x600")
            self.installer = DependencyInstaller(str(PROJECT_ROOT))
            self.auto_launch = True
            self._create_widgets()

        def _create_widgets(self):
            """위젯 생성"""
            # 제목
            title = tk.Label(
                self.root, text="🪙 PICU 프로젝트 통합 설치", font=("Arial", 20, "bold")
            )
            title.pack(pady=20)

            # 설명
            desc = tk.Label(
                self.root,
                text="이 마법사는 PICU 프로젝트의 모든 의존성을 자동으로 설치하고\n"
                "설치 완료 후 애플리케이션을 자동으로 실행합니다.",
                font=("Arial", 11),
            )
            desc.pack(pady=10)

            # 옵션
            options_frame = tk.Frame(self.root)
            options_frame.pack(pady=10)

            self.venv_var = tk.BooleanVar(value=True)
            venv_check = tk.Checkbutton(
                options_frame,
                text="가상환경 생성 (권장)",
                variable=self.venv_var,
                font=("Arial", 10),
            )
            venv_check.pack(side=tk.LEFT, padx=10)

            self.auto_launch_var = tk.BooleanVar(value=True)
            auto_launch_check = tk.Checkbutton(
                options_frame,
                text="설치 완료 후 자동 실행",
                variable=self.auto_launch_var,
                font=("Arial", 10),
            )
            auto_launch_check.pack(side=tk.LEFT, padx=10)

            # 진행 바
            self.progress = ttk.Progressbar(self.root, mode="determinate", length=400)
            self.progress.pack(pady=10)

            # 상태 레이블
            self.status_label = tk.Label(
                self.root, text="준비 완료", font=("Arial", 10)
            )
            self.status_label.pack()

            # 로그
            log_label = tk.Label(self.root, text="설치 로그:", font=("Arial", 10))
            log_label.pack(anchor=tk.W, padx=20, pady=(20, 5))

            self.log_text = scrolledtext.ScrolledText(self.root, height=15)
            self.log_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

            # 버튼
            button_frame = tk.Frame(self.root)
            button_frame.pack(pady=20)

            self.install_button = tk.Button(
                button_frame,
                text="🚀 설치 시작",
                command=self.start_installation,
                font=("Arial", 12, "bold"),
                width=15,
                height=2,
            )
            self.install_button.pack(side=tk.LEFT, padx=10)

            self.close_button = tk.Button(
                button_frame, text="닫기", command=self.root.destroy, width=15, height=2
            )
            self.close_button.pack(side=tk.LEFT, padx=10)

        def start_installation(self):
            """설치 시작"""
            self.install_button.config(state=tk.DISABLED)
            self.log_text.delete(1.0, tk.END)
            self.progress["value"] = 0
            self.status_label.config(text="설치 중...")

            self.auto_launch = self.auto_launch_var.get()

            import threading

            thread = threading.Thread(target=self._run_installation, daemon=True)
            thread.start()

        def _run_installation(self):
            """설치 실행"""

            def progress_callback(message: str, percent: int):
                self.root.after(0, self._update_progress, message, percent)

            result = self.installer.run_full_installation(
                create_venv=self.venv_var.get(), progress_callback=progress_callback
            )
            self.root.after(0, self._installation_finished, result)

        def _update_progress(self, message: str, percent: int):
            """진행 상황 업데이트"""
            self.log_text.insert(tk.END, f"[{percent}%] {message}\n")
            self.progress["value"] = percent
            self.status_label.config(text=message)
            self.log_text.see(tk.END)

        def _installation_finished(self, result: dict):
            """설치 완료"""
            self.install_button.config(state=tk.NORMAL)
            self.progress["value"] = 100

            if result.get("success"):
                self.status_label.config(text="✅ 설치 완료!")
                self.log_text.insert(tk.END, "\n✅ 설치가 성공적으로 완료되었습니다!\n")

                if self.auto_launch:
                    messagebox.showinfo(
                        "설치 완료",
                        "설치가 완료되었습니다.\n애플리케이션을 자동으로 실행합니다.",
                    )
                    self._launch_application()
                else:
                    messagebox.showinfo(
                        "설치 완료",
                        "설치가 완료되었습니다.\n애플리케이션을 실행하려면 'GUI 실행' 버튼을 클릭하세요.",
                    )
            else:
                self.status_label.config(text="❌ 설치 실패")
                errors = result.get("errors", [])
                error_msg = "\n".join(f"  - {e}" for e in errors)
                self.log_text.insert(
                    tk.END, f"\n❌ 설치 중 오류가 발생했습니다:\n{error_msg}\n"
                )
                messagebox.showerror(
                    "설치 실패", f"설치 중 오류가 발생했습니다:\n\n{error_msg}"
                )

        def _launch_application(self):
            """애플리케이션 실행"""
            try:
                self.log_text.insert(tk.END, "\n🚀 애플리케이션 실행 중...\n")
                self.status_label.config(text="애플리케이션 실행 중...")

                venv_python = PROJECT_ROOT / "venv" / "bin" / "python"
                if not venv_python.exists():
                    venv_python = Path(sys.executable)

                gui_script = PROJECT_ROOT / "cointicker" / "gui" / "main.py"
                subprocess.Popen(
                    [str(venv_python), str(gui_script)],
                    cwd=str(PROJECT_ROOT),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )

                self.log_text.insert(tk.END, "✅ 애플리케이션이 실행되었습니다!\n")
                self.status_label.config(text="✅ 애플리케이션 실행 완료")

                # 2초 후 창 닫기
                self.root.after(2000, self.root.destroy)

            except Exception as e:
                logger.error(f"애플리케이션 실행 실패: {e}")
                self.log_text.insert(tk.END, f"❌ 애플리케이션 실행 실패: {e}\n")
                messagebox.showerror(
                    "실행 실패", f"애플리케이션 실행 중 오류가 발생했습니다:\n{e}"
                )

    def run_unified_installer():
        """통합 설치 마법사 실행"""
        root = tk.Tk()
        app = UnifiedInstallerWindow(root)
        root.mainloop()

else:
    # CLI 버전
    def run_unified_installer():
        """통합 설치 마법사 실행 (CLI)"""
        from gui.installer.installer_cli import main

        main()


if __name__ == "__main__":
    run_unified_installer()
