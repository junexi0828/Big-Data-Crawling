"""
GUI 대시보드 메인 애플리케이션
Tkinter 기반 데스크톱 애플리케이션
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import json
from datetime import datetime
from typing import Dict, List

from gui.cluster_monitor import ClusterMonitor
from gui.tier2_monitor import Tier2Monitor
from shared.logger import setup_logger

logger = setup_logger(__name__)


class DashboardApp:
    """대시보드 애플리케이션"""

    def __init__(self, root):
        """
        초기화

        Args:
            root: Tkinter 루트 윈도우
        """
        self.root = root
        self.root.title("CoinTicker 모니터링 대시보드")
        self.root.geometry("1400x900")

        # 모니터 인스턴스
        self.cluster_monitor = ClusterMonitor()
        self.tier2_monitor = Tier2Monitor()

        # 자동 새로고침 플래그
        self.auto_refresh = False
        self.refresh_interval = 30  # 초

        # UI 구성
        self._create_widgets()

        # 초기 데이터 로드
        self.refresh_all()

        # 종료 시 정리
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _create_widgets(self):
        """위젯 생성"""
        # 메뉴바
        self._create_menu()

        # 노트북 (탭)
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 탭 1: 클러스터 모니터링
        cluster_frame = ttk.Frame(notebook)
        notebook.add(cluster_frame, text="클러스터 모니터링")
        self._create_cluster_tab(cluster_frame)

        # 탭 2: Tier2 서버 모니터링
        tier2_frame = ttk.Frame(notebook)
        notebook.add(tier2_frame, text="Tier2 서버")
        self._create_tier2_tab(tier2_frame)

        # 탭 3: 파이프라인 제어
        control_frame = ttk.Frame(notebook)
        notebook.add(control_frame, text="파이프라인 제어")
        self._create_control_tab(control_frame)

        # 탭 4: 설정
        config_frame = ttk.Frame(notebook)
        notebook.add(config_frame, text="설정")
        self._create_config_tab(config_frame)

        # 상태바
        self.status_var = tk.StringVar(value="준비됨")
        statusbar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        statusbar.pack(side=tk.BOTTOM, fill=tk.X)

    def _create_menu(self):
        """메뉴바 생성"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # 파일 메뉴
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="파일", menu=file_menu)
        file_menu.add_command(label="새로고침", command=self.refresh_all, accelerator="F5")
        file_menu.add_separator()
        file_menu.add_command(label="종료", command=self.on_closing)

        # 보기 메뉴
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="보기", menu=view_menu)
        view_menu.add_checkbutton(
            label="자동 새로고침",
            command=self.toggle_auto_refresh,
            variable=tk.BooleanVar(value=self.auto_refresh)
        )

        # 도움말 메뉴
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="도움말", menu=help_menu)
        help_menu.add_command(label="정보", command=self.show_about)

    def _create_cluster_tab(self, parent):
        """클러스터 모니터링 탭 생성"""
        # 상단: 새로고침 버튼
        top_frame = ttk.Frame(parent)
        top_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(top_frame, text="새로고침", command=self.refresh_cluster).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="HDFS 상태", command=self.show_hdfs_status).pack(side=tk.LEFT, padx=5)

        # 노드 상태 테이블
        columns = ("호스트", "상태", "CPU", "메모리", "디스크", "Hadoop", "Scrapy")
        self.cluster_tree = ttk.Treeview(parent, columns=columns, show="headings", height=10)

        for col in columns:
            self.cluster_tree.heading(col, text=col)
            self.cluster_tree.column(col, width=120)

        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.cluster_tree.yview)
        self.cluster_tree.configure(yscrollcommand=scrollbar.set)

        self.cluster_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

    def _create_tier2_tab(self, parent):
        """Tier2 서버 모니터링 탭 생성"""
        # 상단: 새로고침 버튼
        top_frame = ttk.Frame(parent)
        top_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(top_frame, text="새로고침", command=self.refresh_tier2).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="인사이트 생성", command=self.generate_insights).pack(side=tk.LEFT, padx=5)

        # 서버 상태 프레임
        status_frame = ttk.LabelFrame(parent, text="서버 상태")
        status_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.tier2_status_text = scrolledtext.ScrolledText(status_frame, height=15, wrap=tk.WORD)
        self.tier2_status_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 대시보드 요약 프레임
        summary_frame = ttk.LabelFrame(parent, text="대시보드 요약")
        summary_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.tier2_summary_text = scrolledtext.ScrolledText(summary_frame, height=10, wrap=tk.WORD)
        self.tier2_summary_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def _create_control_tab(self, parent):
        """파이프라인 제어 탭 생성"""
        # Spider 제어
        spider_frame = ttk.LabelFrame(parent, text="Spider 제어")
        spider_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 호스트 선택
        host_frame = ttk.Frame(spider_frame)
        host_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(host_frame, text="호스트:").pack(side=tk.LEFT, padx=5)
        self.host_var = tk.StringVar()
        host_combo = ttk.Combobox(host_frame, textvariable=self.host_var, width=30)
        host_combo.pack(side=tk.LEFT, padx=5)

        # Spider 선택
        spider_frame2 = ttk.Frame(spider_frame)
        spider_frame2.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(spider_frame2, text="Spider:").pack(side=tk.LEFT, padx=5)
        self.spider_var = tk.StringVar()
        spider_combo = ttk.Combobox(
            spider_frame2,
            textvariable=self.spider_var,
            values=["upbit_trends", "coinness", "saveticker", "perplexity", "cnn_fear_greed"],
            width=30
        )
        spider_combo.pack(side=tk.LEFT, padx=5)

        # 버튼
        button_frame = ttk.Frame(spider_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(button_frame, text="Spider 시작", command=self.start_spider).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Spider 중지", command=self.stop_spider).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="파이프라인 재시작", command=self.restart_pipeline).pack(side=tk.LEFT, padx=5)

        # 로그 출력
        log_frame = ttk.LabelFrame(parent, text="실행 로그")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.control_log_text = scrolledtext.ScrolledText(log_frame, height=20, wrap=tk.WORD)
        self.control_log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def _create_config_tab(self, parent):
        """설정 탭 생성"""
        # 클러스터 설정
        cluster_config_frame = ttk.LabelFrame(parent, text="클러스터 설정")
        cluster_config_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.config_text = scrolledtext.ScrolledText(cluster_config_frame, height=15, wrap=tk.WORD)
        self.config_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Tier2 설정
        tier2_config_frame = ttk.LabelFrame(parent, text="Tier2 서버 설정")
        tier2_config_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        tier2_inner = ttk.Frame(tier2_config_frame)
        tier2_inner.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(tier2_inner, text="서버 URL:").pack(side=tk.LEFT, padx=5)
        self.tier2_url_var = tk.StringVar(value="http://localhost:5000")
        ttk.Entry(tier2_inner, textvariable=self.tier2_url_var, width=40).pack(side=tk.LEFT, padx=5)
        ttk.Button(tier2_inner, text="적용", command=self.update_tier2_url).pack(side=tk.LEFT, padx=5)

    def refresh_cluster(self):
        """클러스터 상태 새로고침"""
        self.status_var.set("클러스터 상태 확인 중...")

        def _refresh():
            try:
                nodes = self.cluster_monitor.get_all_nodes_status()

                # UI 업데이트는 메인 스레드에서
                self.root.after(0, self._update_cluster_tree, nodes)
                self.root.after(0, lambda: self.status_var.set("클러스터 상태 업데이트 완료"))
            except Exception as e:
                logger.error(f"클러스터 새로고침 실패: {e}")
                self.root.after(0, lambda: self.status_var.set(f"오류: {str(e)}"))

        threading.Thread(target=_refresh, daemon=True).start()

    def _update_cluster_tree(self, nodes: List[Dict]):
        """클러스터 트리 업데이트"""
        # 기존 항목 삭제
        for item in self.cluster_tree.get_children():
            self.cluster_tree.delete(item)

        # 새 항목 추가
        for node in nodes:
            values = (
                node.get('host', 'N/A'),
                "온라인" if node.get('online') else "오프라인",
                f"{node.get('cpu_usage', 0):.1f}%" if node.get('cpu_usage') else "N/A",
                f"{node.get('memory_usage', 0):.1f}%" if node.get('memory_usage') else "N/A",
                f"{node.get('disk_usage', 0):.1f}%" if node.get('disk_usage') else "N/A",
                node.get('hadoop_status', 'N/A'),
                node.get('scrapy_status', 'N/A')
            )
            self.cluster_tree.insert("", tk.END, values=values)

    def refresh_tier2(self):
        """Tier2 서버 상태 새로고침"""
        self.status_var.set("Tier2 서버 상태 확인 중...")

        def _refresh():
            try:
                status = self.tier2_monitor.get_server_status()
                summary = self.tier2_monitor.get_dashboard_summary()

                # UI 업데이트
                self.root.after(0, self._update_tier2_status, status, summary)
                self.root.after(0, lambda: self.status_var.set("Tier2 서버 상태 업데이트 완료"))
            except Exception as e:
                logger.error(f"Tier2 새로고침 실패: {e}")
                self.root.after(0, lambda: self.status_var.set(f"오류: {str(e)}"))

        threading.Thread(target=_refresh, daemon=True).start()

    def _update_tier2_status(self, status: Dict, summary: Dict):
        """Tier2 상태 텍스트 업데이트"""
        self.tier2_status_text.delete(1.0, tk.END)
        self.tier2_status_text.insert(tk.END, json.dumps(status, indent=2, ensure_ascii=False))

        self.tier2_summary_text.delete(1.0, tk.END)
        if summary and summary.get('success'):
            self.tier2_summary_text.insert(tk.END, json.dumps(summary.get('data', {}), indent=2, ensure_ascii=False))
        else:
            self.tier2_summary_text.insert(tk.END, "데이터를 가져올 수 없습니다.")

    def refresh_all(self):
        """모든 데이터 새로고침"""
        self.refresh_cluster()
        self.refresh_tier2()

    def show_hdfs_status(self):
        """HDFS 상태 표시"""
        def _show():
            try:
                status = self.cluster_monitor.get_hdfs_status()
                messagebox.showinfo("HDFS 상태", status.get('report', '상태를 가져올 수 없습니다.'))
            except Exception as e:
                messagebox.showerror("오류", f"HDFS 상태 확인 실패: {str(e)}")

        threading.Thread(target=_show, daemon=True).start()

    def start_spider(self):
        """Spider 시작"""
        host = self.host_var.get()
        spider = self.spider_var.get()

        if not host or not spider:
            messagebox.showwarning("경고", "호스트와 Spider를 선택하세요.")
            return

        def _start():
            try:
                result = self.cluster_monitor.start_spider(host, spider)
                self.control_log_text.insert(tk.END, f"[{datetime.now()}] Spider 시작: {spider} @ {host}\n")
                self.control_log_text.insert(tk.END, f"결과: {json.dumps(result, indent=2, ensure_ascii=False)}\n\n")
                self.control_log_text.see(tk.END)
            except Exception as e:
                self.control_log_text.insert(tk.END, f"[{datetime.now()}] 오류: {str(e)}\n\n")

        threading.Thread(target=_start, daemon=True).start()

    def stop_spider(self):
        """Spider 중지"""
        host = self.host_var.get()
        spider = self.spider_var.get()

        if not host or not spider:
            messagebox.showwarning("경고", "호스트와 Spider를 선택하세요.")
            return

        def _stop():
            try:
                result = self.cluster_monitor.stop_spider(host, spider)
                self.control_log_text.insert(tk.END, f"[{datetime.now()}] Spider 중지: {spider} @ {host}\n")
                self.control_log_text.insert(tk.END, f"결과: {json.dumps(result, indent=2, ensure_ascii=False)}\n\n")
                self.control_log_text.see(tk.END)
            except Exception as e:
                self.control_log_text.insert(tk.END, f"[{datetime.now()}] 오류: {str(e)}\n\n")

        threading.Thread(target=_stop, daemon=True).start()

    def restart_pipeline(self):
        """파이프라인 재시작"""
        host = self.host_var.get()

        if not host:
            messagebox.showwarning("경고", "호스트를 선택하세요.")
            return

        def _restart():
            try:
                result = self.cluster_monitor.restart_pipeline(host)
                self.control_log_text.insert(tk.END, f"[{datetime.now()}] 파이프라인 재시작: {host}\n")
                self.control_log_text.insert(tk.END, f"결과: {json.dumps(result, indent=2, ensure_ascii=False)}\n\n")
                self.control_log_text.see(tk.END)
            except Exception as e:
                self.control_log_text.insert(tk.END, f"[{datetime.now()}] 오류: {str(e)}\n\n")

        threading.Thread(target=_restart, daemon=True).start()

    def generate_insights(self):
        """인사이트 생성"""
        def _generate():
            try:
                result = self.tier2_monitor.generate_insights()
                if result.get('success'):
                    messagebox.showinfo("성공", "인사이트 생성이 완료되었습니다.")
                else:
                    messagebox.showerror("실패", f"인사이트 생성 실패: {result.get('error', '알 수 없는 오류')}")
            except Exception as e:
                messagebox.showerror("오류", f"인사이트 생성 실패: {str(e)}")

        threading.Thread(target=_generate, daemon=True).start()

    def toggle_auto_refresh(self):
        """자동 새로고침 토글"""
        self.auto_refresh = not self.auto_refresh
        if self.auto_refresh:
            self._start_auto_refresh()
        else:
            self._stop_auto_refresh()

    def _start_auto_refresh(self):
        """자동 새로고침 시작"""
        if self.auto_refresh:
            self.refresh_all()
            self.root.after(self.refresh_interval * 1000, self._start_auto_refresh)

    def _stop_auto_refresh(self):
        """자동 새로고침 중지"""
        self.auto_refresh = False

    def update_tier2_url(self):
        """Tier2 URL 업데이트"""
        url = self.tier2_url_var.get()
        self.tier2_monitor = Tier2Monitor(url)
        messagebox.showinfo("완료", f"Tier2 서버 URL이 업데이트되었습니다: {url}")

    def show_about(self):
        """정보 표시"""
        messagebox.showinfo(
            "정보",
            "CoinTicker 모니터링 대시보드\n\n"
            "버전: 1.0.0\n"
            "라즈베리파이 클러스터 및 Tier2 서버 모니터링 및 제어"
        )

    def on_closing(self):
        """종료 시 정리"""
        self.cluster_monitor.close()
        self.root.destroy()


def main():
    """메인 함수"""
    root = tk.Tk()
    app = DashboardApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

