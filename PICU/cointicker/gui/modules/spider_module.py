"""
Spider 모듈
Scrapy Spider를 관리하는 모듈
"""

import subprocess
import threading
import os
from typing import Dict, Any, Optional, Callable
from pathlib import Path
from datetime import datetime

from gui.core.module_manager import ModuleInterface
from gui.modules.process_monitor import get_monitor
from shared.logger import setup_logger

logger = setup_logger(__name__)


class SpiderModule(ModuleInterface):
    """Spider 모듈 클래스"""

    def __init__(self, name: str = "SpiderModule"):
        super().__init__(name)
        self.spiders = {
            "upbit_trends": {"status": "stopped", "schedule": "5분"},
            "coinness": {"status": "stopped", "schedule": "10분"},
            "saveticker": {"status": "stopped", "schedule": "5분"},
            "perplexity": {"status": "stopped", "schedule": "1시간"},
            "cnn_fear_greed": {"status": "stopped", "schedule": "1일"},
        }
        # 프로젝트 루트 기준으로 경로 해결
        # gui/modules/spider_module.py -> cointicker/worker-nodes
        project_root = Path(__file__).parent.parent.parent
        self.worker_nodes_path = project_root / "worker-nodes"
        self.monitor = get_monitor()
        self.log_callbacks: Dict[str, Callable] = {}  # Spider별 로그 콜백

    def initialize(self, config: dict) -> bool:
        """모듈 초기화"""
        try:
            self.config = config
            # 프로젝트 루트 기준으로 경로 해결
            project_root = Path(__file__).parent.parent.parent
            worker_nodes_relative = config.get("worker_nodes_path", "worker-nodes")
            self.worker_nodes_path = (project_root / worker_nodes_relative).resolve()
            logger.info(
                f"Spider 모듈 초기화 완료: worker-nodes 경로 = {self.worker_nodes_path}"
            )
            return True
        except Exception as e:
            logger.error(f"Spider 모듈 초기화 실패: {e}")
            return False

    def start(self) -> bool:
        """모듈 시작"""
        self.status = "running"
        logger.info("Spider 모듈 시작")
        return True

    def stop(self) -> bool:
        """모듈 중지"""
        # 실행 중인 모든 Spider 중지
        for spider_name in self.spiders:
            if self.spiders[spider_name]["status"] == "running":
                self.stop_spider(spider_name)

        self.status = "stopped"
        logger.info("Spider 모듈 중지")
        return True

    def execute(self, command: str, params: dict = None) -> dict:
        """명령어 실행"""
        params = params or {}

        if command == "list_spiders":
            return {"success": True, "spiders": list(self.spiders.keys())}

        elif command == "start_spider":
            spider_name = params.get("spider_name")
            host = params.get("host")
            log_callback = params.get("log_callback")
            if not spider_name:
                return {"success": False, "error": "spider_name이 필요합니다"}

            return self.start_spider(spider_name, host, log_callback)

        elif command == "stop_spider":
            spider_name = params.get("spider_name")
            host = params.get("host")
            if not spider_name:
                return {"success": False, "error": "spider_name이 필요합니다"}

            return self.stop_spider(spider_name, host)

        elif command == "get_spider_status":
            spider_name = params.get("spider_name")
            if spider_name:
                spider_info = self.spiders.get(spider_name, {}).copy()
                process_id = spider_info.get("process_id")

                # 실시간 통계 추가
                if process_id:
                    stats = self.monitor.get_stats(process_id)
                    spider_info["stats"] = stats
                    logs = self.monitor.get_logs(process_id, limit=50)
                    spider_info["recent_logs"] = logs

                return {"success": True, "status": spider_info}
            else:
                # 모든 Spider 상태
                spiders_info = {}
                for name, info in self.spiders.items():
                    spiders_info[name] = info.copy()
                    process_id = info.get("process_id")
                    if process_id:
                        spiders_info[name]["stats"] = self.monitor.get_stats(process_id)

                return {"success": True, "spiders": spiders_info}

        elif command == "get_spider_logs":
            spider_name = params.get("spider_name")
            limit = params.get("limit", 100)

            if spider_name and spider_name in self.spiders:
                process_id = self.spiders[spider_name].get("process_id")
                if process_id:
                    logs = self.monitor.get_logs(process_id, limit=limit)
                    return {"success": True, "logs": logs}

            return {"success": False, "error": "Spider를 찾을 수 없습니다"}

        else:
            return {"success": False, "error": f"알 수 없는 명령어: {command}"}

    def start_spider(
        self,
        spider_name: str,
        host: str = None,
        log_callback: Optional[Callable] = None,
    ) -> dict:
        """
        Spider 시작

        Args:
            spider_name: Spider 이름
            host: 호스트 주소 (None이면 로컬)
            log_callback: 로그 콜백 함수 (process_id, log_entry) -> None

        Returns:
            실행 결과
        """
        if spider_name not in self.spiders:
            return {"success": False, "error": f"알 수 없는 Spider: {spider_name}"}

        try:
            # 프로젝트 루트 찾기 (venv Python 경로를 위해)
            project_root = Path(__file__).parent.parent.parent.parent
            venv_python = project_root / "venv" / "bin" / "python"

            if host:
                # 원격 실행 (SSH 필요) - scrapy.cfg가 있는 디렉토리로 이동
                cmd = f"ssh {host} 'cd ~/cointicker/worker-nodes/cointicker && scrapy crawl {spider_name}'"
            else:
                # 로컬 실행 - venv Python을 사용하여 scrapy 실행
                cointicker_dir = self.worker_nodes_path / "cointicker"
                cointicker_abs = str(cointicker_dir.resolve())

                # venv Python이 있으면 사용, 없으면 시스템 scrapy 사용 (fallback)
                if venv_python.exists():
                    cmd = f"cd {cointicker_abs} && {venv_python} -m scrapy crawl {spider_name}"
                    logger.debug(f"venv Python 사용: {venv_python}")
                else:
                    cmd = f"cd {cointicker_abs} && scrapy crawl {spider_name}"
                    logger.warning(
                        f"venv Python 없음, 시스템 scrapy 사용: {cointicker_abs}"
                    )

            # 프로젝트 루트를 PYTHONPATH에 추가 (shared 모듈 import를 위해)
            project_root = Path(__file__).parent.parent.parent
            env = os.environ.copy()
            pythonpath = env.get("PYTHONPATH", "")

            # worker-nodes 경로를 PYTHONPATH에 추가 (cointicker 모듈 import를 위해)
            worker_nodes_path = str(self.worker_nodes_path.resolve())

            # PYTHONPATH 구성: worker-nodes, project_root, 기존 PYTHONPATH
            paths = [worker_nodes_path, str(project_root)]
            if pythonpath:
                paths.append(pythonpath)
            env["PYTHONPATH"] = ":".join(paths)

            # 작업 디렉토리를 cointicker로 설정
            cointicker_dir = self.worker_nodes_path / "cointicker"
            process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1,
                cwd=str(cointicker_dir.resolve()),  # scrapy.cfg가 있는 디렉토리
                env=env,  # PYTHONPATH가 설정된 환경 변수 사용
            )

            process_id = f"spider_{spider_name}_{process.pid}"
            self.spiders[spider_name]["status"] = "starting"  # 시작 중 상태
            self.spiders[spider_name]["process"] = process
            self.spiders[spider_name]["process_id"] = process_id
            self.spiders[spider_name]["start_time"] = datetime.now().isoformat()

            # 로그 콜백 저장
            if log_callback:
                self.log_callbacks[process_id] = log_callback

            # 프로세스 모니터링 시작
            self.monitor.start_monitoring(process_id, process, log_callback)

            # 프로세스가 실제로 실행 중인지 확인하는 스레드 시작
            def check_process_status():
                import time
                from gui.core.timing_config import TimingConfig

                status_check_delay = TimingConfig.get("spider.status_check_delay", 2)
                time.sleep(status_check_delay)
                if spider_name in self.spiders:
                    # 프로세스가 여전히 실행 중이면 "running"으로 변경
                    if "process" in self.spiders[spider_name]:
                        proc = self.spiders[spider_name]["process"]
                        if proc and proc.poll() is None:  # 프로세스가 실행 중
                            self.spiders[spider_name]["status"] = "running"
                            logger.debug(
                                f"Spider {spider_name} 상태: starting -> running"
                            )
                        else:  # 프로세스가 종료됨
                            self.spiders[spider_name]["status"] = "error"
                            # 실제 오류 메시지 확인
                            try:
                                if proc:
                                    # 프로세스가 종료되었으므로 stderr 읽기 시도
                                    stdout, stderr = proc.communicate(timeout=1)
                                    if stderr:
                                        stderr_text = (
                                            stderr.strip()
                                            if isinstance(stderr, str)
                                            else stderr.decode(
                                                "utf-8", errors="ignore"
                                            ).strip()
                                        )
                                        if stderr_text:
                                            logger.error(
                                                f"Spider {spider_name} 시작 실패 (프로세스 종료): {stderr_text[:500]}"
                                            )
                                        else:
                                            logger.warning(
                                                f"Spider {spider_name} 시작 실패 (프로세스 종료, 오류 메시지 없음)"
                                            )
                                    elif stdout:
                                        stdout_text = (
                                            stdout.strip()
                                            if isinstance(stdout, str)
                                            else stdout.decode(
                                                "utf-8", errors="ignore"
                                            ).strip()
                                        )
                                        if stdout_text:
                                            logger.debug(
                                                f"Spider {spider_name} stdout: {stdout_text[:500]}"
                                            )
                                    else:
                                        logger.warning(
                                            f"Spider {spider_name} 시작 실패 (프로세스 종료, 종료 코드: {proc.returncode})"
                                        )
                            except subprocess.TimeoutExpired:
                                logger.warning(
                                    f"Spider {spider_name} 시작 실패 (프로세스 종료, 통신 타임아웃)"
                                )
                            except Exception as e:
                                logger.warning(
                                    f"Spider {spider_name} 시작 실패 (프로세스 종료): {e}"
                                )

            threading.Thread(target=check_process_status, daemon=True).start()

            logger.info(f"Spider 시작: {spider_name} (PID: {process.pid})")
            return {
                "success": True,
                "spider_name": spider_name,
                "pid": process.pid,
                "process_id": process_id,
            }
        except Exception as e:
            logger.error(f"Spider 시작 실패 {spider_name}: {e}")
            return {"success": False, "error": str(e)}

    def stop_spider(self, spider_name: str, host: str = None) -> dict:
        """
        Spider 중지

        Args:
            spider_name: Spider 이름
            host: 호스트 주소

        Returns:
            실행 결과
        """
        if spider_name not in self.spiders:
            return {"success": False, "error": f"알 수 없는 Spider: {spider_name}"}

        try:
            if host:
                cmd = f"ssh {host} 'pkill -f \"scrapy crawl {spider_name}\"'"
            else:
                if "process" in self.spiders[spider_name]:
                    process = self.spiders[spider_name]["process"]
                    process.terminate()
                cmd = f"pkill -f 'scrapy crawl {spider_name}'"

            subprocess.run(cmd, shell=True, timeout=5)

            self.spiders[spider_name]["status"] = "stopped"
            if "process" in self.spiders[spider_name]:
                del self.spiders[spider_name]["process"]

            logger.info(f"Spider 중지: {spider_name}")
            return {"success": True, "spider_name": spider_name}
        except Exception as e:
            logger.error(f"Spider 중지 실패 {spider_name}: {e}")
            return {"success": False, "error": str(e)}
