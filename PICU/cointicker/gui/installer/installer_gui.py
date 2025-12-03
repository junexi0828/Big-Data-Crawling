"""
설치 마법사 GUI
PyQt5 기반 설치 마법사 인터페이스
"""

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
        QWizard,
        QWizardPage,
    )
    from PyQt5.QtCore import Qt, QThread, pyqtSignal

    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False

# tkinter fallback은 별도로 처리 (macOS Python 3.14에서 tkinter가 없을 수 있음)
try:
    import tkinter as tk
    from tkinter import ttk, messagebox, scrolledtext

    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False

from gui.installer.installer import DependencyInstaller
from shared.logger import setup_logger

logger = setup_logger(__name__)


if PYQT5_AVAILABLE:

    class InstallThread(QThread):
        """설치 스레드"""

        progress = pyqtSignal(int, str)
        finished = pyqtSignal(dict)

        def __init__(self, create_venv: bool = True):
            super().__init__()
            self.create_venv = create_venv
            self.installer = DependencyInstaller()

        def run(self):
            """설치 실행"""
            result = self.installer.run_full_installation(create_venv=self.create_venv)
            self.finished.emit(result)

    class InstallWizard(QWizard):
        """설치 마법사"""

        def __init__(self, parent=None):
            super().__init__(parent)
            self.setWindowTitle("CoinTicker 설치 마법사")
            self.setWizardStyle(QWizard.ModernStyle)
            self.setPage(0, WelcomePage())
            self.setPage(1, OptionsPage())
            self.setPage(2, InstallPage())
            self.setPage(3, CompletePage())

    class WelcomePage(QWizardPage):
        """환영 페이지"""

        def __init__(self):
            super().__init__()
            self.setTitle("환영합니다")
            self.setSubTitle("CoinTicker 설치 마법사에 오신 것을 환영합니다")

            layout = QVBoxLayout()

            label = QLabel(
                "이 마법사는 CoinTicker 프로젝트의 모든 의존성을 자동으로 설치합니다.\n\n"
                "설치 과정:\n"
                "1. Python 버전 확인\n"
                "2. pip 확인\n"
                "3. 가상환경 생성 (선택)\n"
                "4. 시스템 의존성 설치\n"
                "5. Python 의존성 설치\n"
                "6. 설치 확인\n\n"
                "계속하려면 '다음' 버튼을 클릭하세요."
            )
            label.setWordWrap(True)
            layout.addWidget(label)

            self.setLayout(layout)

    class OptionsPage(QWizardPage):
        """옵션 페이지"""

        def __init__(self):
            super().__init__()
            self.setTitle("설치 옵션")
            self.setSubTitle("설치 옵션을 선택하세요")

            layout = QVBoxLayout()

            self.venv_checkbox = QCheckBox("가상환경 생성 (권장)")
            self.venv_checkbox.setChecked(True)
            layout.addWidget(self.venv_checkbox)

            layout.addStretch()
            self.setLayout(layout)

        def nextId(self):
            return 2

    class InstallPage(QWizardPage):
        """설치 페이지"""

        def __init__(self):
            super().__init__()
            self.setTitle("설치 진행")
            self.setSubTitle("의존성을 설치하고 있습니다. 잠시만 기다려주세요...")

            layout = QVBoxLayout()

            self.progress_bar = QProgressBar()
            self.progress_bar.setRange(0, 0)  # 무한 진행
            layout.addWidget(self.progress_bar)

            self.log_text = QTextEdit()
            self.log_text.setReadOnly(True)
            layout.addWidget(self.log_text)

            self.setLayout(layout)
            self.install_thread = None

        def initializePage(self):
            """페이지 초기화 시 설치 시작"""
            create_venv = self.wizard().page(1).venv_checkbox.isChecked()

            self.install_thread = InstallThread(create_venv=create_venv)
            self.install_thread.progress.connect(self.update_progress)
            self.install_thread.finished.connect(self.installation_finished)
            self.install_thread.start()

        def update_progress(self, step: int, message: str):
            """진행 상황 업데이트"""
            self.log_text.append(f"[{step}] {message}")

        def installation_finished(self, result: dict):
            """설치 완료"""
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(100)

            if result["success"]:
                self.log_text.append("\n✅ 설치가 완료되었습니다!")
            else:
                self.log_text.append("\n❌ 설치 중 오류가 발생했습니다:")
                for error in result.get("errors", []):
                    self.log_text.append(f"  - {error}")

    class CompletePage(QWizardPage):
        """완료 페이지"""

        def __init__(self):
            super().__init__()
            self.setTitle("설치 완료")
            self.setSubTitle("설치가 완료되었습니다!")

            layout = QVBoxLayout()

            label = QLabel(
                "CoinTicker 설치가 성공적으로 완료되었습니다.\n\n"
                "다음 단계:\n"
                "1. 설정 파일을 확인하세요 (config/ 디렉토리)\n"
                "2. 데이터베이스를 초기화하세요: python backend/init_db.py\n"
                "3. GUI 애플리케이션을 실행하세요: python gui/main.py\n\n"
                "마법사를 닫으려면 '완료' 버튼을 클릭하세요."
            )
            label.setWordWrap(True)
            layout.addWidget(label)

            layout.addStretch()
            self.setLayout(layout)

    def run_installer():
        """설치 마법사 실행"""
        app = QApplication([])
        wizard = InstallWizard()
        wizard.show()
        app.exec_()

elif TKINTER_AVAILABLE:
    # Tkinter fallback
    class InstallerGUI:
        """Tkinter 기반 설치 마법사"""

        def __init__(self, root):
            self.root = root
            self.root.title("CoinTicker 설치 마법사")
            self.root.geometry("600x500")

            self.installer = DependencyInstaller()
            self.create_venv = tk.BooleanVar(value=True)

            self._create_widgets()

        def _create_widgets(self):
            """위젯 생성"""
            # 제목
            title = tk.Label(
                self.root, text="CoinTicker 설치 마법사", font=("Arial", 16, "bold")
            )
            title.pack(pady=10)

            # 옵션
            options_frame = tk.Frame(self.root)
            options_frame.pack(pady=10)

            venv_check = tk.Checkbutton(
                options_frame, text="가상환경 생성 (권장)", variable=self.create_venv
            )
            venv_check.pack()

            # 로그
            log_label = tk.Label(self.root, text="설치 로그:")
            log_label.pack(anchor=tk.W, padx=10)

            self.log_text = scrolledtext.ScrolledText(self.root, height=20)
            self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

            # 버튼
            button_frame = tk.Frame(self.root)
            button_frame.pack(pady=10)

            self.install_button = tk.Button(
                button_frame,
                text="설치 시작",
                command=self.start_installation,
                width=20,
            )
            self.install_button.pack(side=tk.LEFT, padx=5)

            self.close_button = tk.Button(
                button_frame, text="닫기", command=self.root.destroy, width=20
            )
            self.close_button.pack(side=tk.LEFT, padx=5)

        def start_installation(self):
            """설치 시작"""
            self.install_button.config(state=tk.DISABLED)
            self.log_text.delete(1.0, tk.END)
            self.log_text.insert(tk.END, "설치를 시작합니다...\n\n")

            import threading

            thread = threading.Thread(target=self._run_installation, daemon=True)
            thread.start()

        def _run_installation(self):
            """설치 실행 (백그라운드)"""
            result = self.installer.run_full_installation(
                create_venv=self.create_venv.get()
            )

            self.root.after(0, self._installation_finished, result)

        def _installation_finished(self, result: dict):
            """설치 완료"""
            self.install_button.config(state=tk.NORMAL)

            if result["success"]:
                self.log_text.insert(tk.END, "\n✅ 설치가 완료되었습니다!\n")
                messagebox.showinfo("완료", "설치가 성공적으로 완료되었습니다!")
            else:
                self.log_text.insert(tk.END, "\n❌ 설치 중 오류가 발생했습니다:\n")
                for error in result.get("errors", []):
                    self.log_text.insert(tk.END, f"  - {error}\n")
                messagebox.showerror(
                    "오류", "설치 중 오류가 발생했습니다. 로그를 확인하세요."
                )

    def run_installer():
        """설치 마법사 실행"""
        root = tk.Tk()
        app = InstallerGUI(root)
        root.mainloop()

else:
    # GUI가 모두 없을 때는 CLI 버전 사용
    def run_installer():
        """설치 마법사 실행 (CLI 버전)"""
        from gui.installer.installer_cli import main

        main()


if __name__ == "__main__":
    run_installer()
