"""
Scrapyd 스케줄러
크롤링 작업을 스케줄링
"""

import schedule
import time
import logging
import requests
import yaml
import os
import subprocess
import shutil
import configparser
from datetime import datetime
from pathlib import Path
from typing import Optional

from shared.logger import setup_logger
from shared.path_utils import get_cointicker_root

# 로그 파일 경로 설정
cointicker_root = get_cointicker_root()
log_file = str(cointicker_root / "logs" / "scheduler.log")
logger = setup_logger(__name__, log_file=log_file)


class ScrapydScheduler:
    """Scrapyd 스케줄러"""

    def __init__(self, scrapyd_url: Optional[str] = None):
        """
        초기화

        Args:
            scrapyd_url: Scrapyd 서버 URL (None이면 설정 파일 또는 기본값 사용)
        """
        # 설정 파일에서 scrapyd_url 로드
        if scrapyd_url is None:
            scrapyd_url = self._load_scrapyd_url()

        # scrapyd_url이 None이면 기본값 사용
        if scrapyd_url is None:
            scrapyd_url = "http://localhost:6800"

        self.scrapyd_url = scrapyd_url
        self.project = "cointicker"
        self.spiders = self._load_spider_config()
        self.scrapyd_process = None

        # 프로젝트 경로 설정 (배포용)
        cointicker_root = get_cointicker_root()
        self.project_path = cointicker_root / "worker-nodes" / "cointicker"

    def _load_scrapyd_url(self):
        """설정 파일에서 Scrapyd URL 로드"""
        try:
            from shared.path_utils import get_cointicker_root

            config_file = get_cointicker_root() / "config" / "spider_config.yaml"
            if config_file.exists():
                with open(config_file, "r", encoding="utf-8") as f:
                    config = yaml.safe_load(f)
                    # spider_config.yaml에 scrapyd_url이 있으면 사용
                    if config and "scrapyd" in config:
                        return config["scrapyd"].get("url", "http://localhost:6800")
        except Exception as e:
            logger.debug(f"Failed to load scrapyd_url from config: {e}")

        # 환경 변수 또는 기본값
        return os.getenv("SCRAPYD_URL", "http://localhost:6800")

    def _load_spider_config(self):
        """spider_config.yaml에서 Spider 스케줄 정보 로드"""
        try:
            from shared.path_utils import get_cointicker_root

            config_file = get_cointicker_root() / "config" / "spider_config.yaml"
            if config_file.exists():
                with open(config_file, "r", encoding="utf-8") as f:
                    config = yaml.safe_load(f)
                    if config and "spiders" in config:
                        spiders = {}
                        for name, spider_config in config["spiders"].items():
                            if spider_config.get("enabled", True):
                                spiders[name] = {
                                    "schedule": spider_config.get(
                                        "schedule", "*/5 * * * *"
                                    ),
                                }
                        enabled_names = list(spiders.keys())
                        logger.info(
                            f"✅ {len(spiders)}개 Spider 로드 완료: {enabled_names}"
                        )
                        return spiders
        except Exception as e:
            logger.warning(f"Failed to load spider_config.yaml: {e}")

        # 기본값 (설정 파일 로드 실패 시)
        default_spiders = {
            "upbit_trends": {"schedule": "*/5 * * * *"},
            "saveticker": {"schedule": "*/5 * * * *"},
            "coinness": {"schedule": "*/10 * * * *"},
            "perplexity": {"schedule": "0 * * * *"},
            "cnn_fear_greed": {"schedule": "0 0 * * *"},
        }
        logger.warning(
            f"⚠️ spider_config.yaml 로드 실패. 기본값 사용: {list(default_spiders.keys())}"
        )
        return default_spiders

    def _install_scrapyd(self):
        """Scrapyd 자동 설치"""
        try:
            import sys

            python_cmd = sys.executable

            logger.info("Scrapyd 패키지 자동 설치 시도 중...")
            result = subprocess.run(
                [python_cmd, "-m", "pip", "install", "scrapyd>=1.3.0"],
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.returncode == 0:
                logger.info("✅ Scrapyd 설치 완료")
                return True
            else:
                logger.error(f"Scrapyd 설치 실패: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            logger.error("Scrapyd 설치 타임아웃 (120초 초과)")
            return False
        except Exception as e:
            logger.error(f"Scrapyd 설치 중 오류: {e}")
            return False

    def _install_scrapyd_client(self):
        """scrapyd-client 자동 설치 (scrapyd-deploy 명령어 포함)"""
        try:
            import sys

            python_cmd = sys.executable

            logger.info("scrapyd-client 패키지 자동 설치 시도 중...")
            result = subprocess.run(
                [python_cmd, "-m", "pip", "install", "scrapyd-client>=1.2.0"],
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.returncode == 0:
                logger.info("✅ scrapyd-client 설치 완료")
                return True
            else:
                logger.error(f"scrapyd-client 설치 실패: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            logger.error("scrapyd-client 설치 타임아웃 (120초 초과)")
            return False
        except Exception as e:
            logger.error(f"scrapyd-client 설치 중 오류: {e}")
            return False

    def _start_scrapyd_server(self):
        """Scrapyd 서버 자동 시작"""
        try:
            # scrapyd 명령어 확인 (여러 venv 경로 확인)
            scrapyd_cmd = shutil.which("scrapyd")
            if not scrapyd_cmd:
                # venv의 scrapyd 확인 (우선순위: PICU/venv > cointicker/venv > bigdata/venv)
                cointicker_root = get_cointicker_root()
                project_root = cointicker_root.parent  # PICU/
                bigdata_root = project_root.parent  # bigdata/

                venv_paths = [
                    project_root / "venv" / "bin" / "scrapyd",  # PICU/venv
                    cointicker_root / "venv" / "bin" / "scrapyd",  # cointicker/venv
                    bigdata_root / "venv" / "bin" / "scrapyd",  # bigdata/venv
                ]

                for venv_scrapyd in venv_paths:
                    if venv_scrapyd.exists():
                        scrapyd_cmd = str(venv_scrapyd)
                        logger.info(f"Scrapyd 명령어 발견: {scrapyd_cmd}")
                        break

                if not scrapyd_cmd:
                    # scrapyd가 없으면 자동 설치 시도
                    logger.warning(
                        "scrapyd 명령어를 찾을 수 없습니다. 자동 설치를 시도합니다..."
                    )
                    if self._install_scrapyd():
                        # 설치 후 다시 확인
                        scrapyd_cmd = shutil.which("scrapyd")
                        if not scrapyd_cmd:
                            # venv 경로 다시 확인
                            for venv_scrapyd in venv_paths:
                                if venv_scrapyd.exists():
                                    scrapyd_cmd = str(venv_scrapyd)
                                    break

                    if not scrapyd_cmd:
                        logger.error(
                            "scrapyd 설치 후에도 명령어를 찾을 수 없습니다. "
                            "수동으로 설치하세요: pip install scrapyd"
                        )
                        return False

            # 이미 실행 중인지 확인
            if self._check_scrapyd_connection():
                logger.info("Scrapyd 서버가 이미 실행 중입니다.")
                return True

            # Scrapyd 서버 시작
            logger.info(f"Scrapyd 서버 시작 중: {scrapyd_cmd}")
            self.scrapyd_process = subprocess.Popen(
                [scrapyd_cmd],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True,  # 부모 프로세스 종료 시에도 계속 실행
            )

            # 시작 확인 (최대 5초 대기)
            for _ in range(5):
                time.sleep(1)
                if self._check_scrapyd_connection():
                    logger.info("✅ Scrapyd 서버 시작 완료")
                    return True

            logger.warning("Scrapyd 서버 시작 확인 실패 (타임아웃)")
            return False

        except Exception as e:
            logger.error(f"Scrapyd 서버 시작 실패: {e}")
            return False

    def _check_scrapyd_connection(self):
        """Scrapyd 서버 연결 확인"""
        try:
            url = f"{self.scrapyd_url}/listprojects.json"
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.debug(f"Scrapyd connection check failed: {e}")
            return False

    def _deploy_project(self):
        """Scrapy 프로젝트를 Scrapyd에 배포"""
        try:
            # 프로젝트가 이미 배포되어 있는지 확인
            url = f"{self.scrapyd_url}/listprojects.json"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                projects = response.json().get("projects", [])
                if self.project in projects:
                    logger.info(f"프로젝트 '{self.project}'가 이미 배포되어 있습니다.")
                    return True

            # scrapyd-deploy 명령어 찾기
            deploy_cmd = shutil.which("scrapyd-deploy")
            if not deploy_cmd:
                # venv의 scrapyd-deploy 확인
                cointicker_root = get_cointicker_root()
                project_root = cointicker_root.parent  # PICU/
                bigdata_root = project_root.parent  # bigdata/

                venv_paths = [
                    project_root / "venv" / "bin" / "scrapyd-deploy",  # PICU/venv
                    cointicker_root
                    / "venv"
                    / "bin"
                    / "scrapyd-deploy",  # cointicker/venv
                    bigdata_root / "venv" / "bin" / "scrapyd-deploy",  # bigdata/venv
                ]

                for venv_deploy in venv_paths:
                    if venv_deploy.exists():
                        deploy_cmd = str(venv_deploy)
                        logger.info(f"scrapyd-deploy 명령어 발견: {deploy_cmd}")
                        break

                if not deploy_cmd:
                    # scrapyd-deploy가 없으면 자동 설치 시도
                    logger.warning(
                        "scrapyd-deploy 명령어를 찾을 수 없습니다. 자동 설치를 시도합니다..."
                    )
                    if self._install_scrapyd_client():
                        # 설치 후 다시 확인
                        deploy_cmd = shutil.which("scrapyd-deploy")
                        if not deploy_cmd:
                            # venv 경로 다시 확인
                            for venv_deploy in venv_paths:
                                if venv_deploy.exists():
                                    deploy_cmd = str(venv_deploy)
                                    break

                    if not deploy_cmd:
                        logger.error(
                            "scrapyd-deploy 설치 후에도 명령어를 찾을 수 없습니다. "
                            "수동으로 설치하세요: pip install scrapyd-client"
                        )
                        return False

            # scrapy.cfg 파일 확인
            scrapy_cfg = self.project_path / "scrapy.cfg"
            if not scrapy_cfg.exists():
                logger.error(f"scrapy.cfg 파일을 찾을 수 없습니다: {scrapy_cfg}")
                return False

            # scrapy.cfg에 deploy URL 설정 (없으면 추가)
            import configparser

            config = configparser.ConfigParser()
            config.read(scrapy_cfg)

            if "deploy" not in config:
                config.add_section("deploy")

            # deploy URL 설정
            config.set("deploy", "url", self.scrapyd_url)
            config.set("deploy", "project", self.project)

            with open(scrapy_cfg, "w") as f:
                config.write(f)

            logger.info(f"프로젝트 배포 중: {self.project_path} -> {self.scrapyd_url}")

            # scrapyd-deploy 실행
            result = subprocess.run(
                [deploy_cmd],
                cwd=str(self.project_path),
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                logger.info(f"✅ 프로젝트 '{self.project}' 배포 완료")
                return True
            else:
                logger.error(f"프로젝트 배포 실패: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"프로젝트 배포 중 오류: {e}")
            return False

    def schedule_spider(self, spider_name: str):
        """
        Spider 스케줄링

        Args:
            spider_name: Spider 이름
        """
        # Scrapyd 서버 연결 확인
        if not self._check_scrapyd_connection():
            logger.error(
                f"Scrapyd 서버에 연결할 수 없습니다: {self.scrapyd_url}\n"
                f"Scrapyd 서버를 시작하세요: scrapyd 또는 scrapyd &"
            )
            return False

        try:
            url = f"{self.scrapyd_url}/schedule.json"
            data = {"project": self.project, "spider": spider_name}

            response = requests.post(url, data=data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "ok":
                    job_id = result.get("jobid", "unknown")
                    logger.info(f"Scheduled spider: {spider_name} (jobid: {job_id})")
                    return True
                else:
                    logger.error(
                        f"Failed to schedule {spider_name}: {result.get('message', 'unknown error')}"
                    )
                    return False
            else:
                logger.error(
                    f"Failed to schedule {spider_name}: HTTP {response.status_code} - {response.text}"
                )
                return False

        except requests.exceptions.ConnectionError as e:
            logger.error(
                f"Scrapyd 서버 연결 실패: {self.scrapyd_url}\n"
                f"오류: {e}\n"
                f"Scrapyd 서버를 시작하세요: scrapyd 또는 scrapyd &"
            )
            return False
        except Exception as e:
            logger.error(f"Error scheduling {spider_name}: {e}")
            return False

    def start(self):
        """스케줄러 시작"""
        # Scrapyd 서버 연결 확인 및 자동 시작
        if not self._check_scrapyd_connection():
            logger.warning(
                f"⚠️ Scrapyd 서버에 연결할 수 없습니다: {self.scrapyd_url}\n"
                f"Scrapyd 서버를 자동으로 시작합니다..."
            )
            if not self._start_scrapyd_server():
                logger.error(
                    f"Scrapyd 서버 자동 시작 실패. 수동으로 시작하세요:\n"
                    f"  scrapyd\n"
                    f"또는 백그라운드 실행:\n"
                    f"  scrapyd &\n"
                    f"스케줄러는 계속 실행되지만 Scrapyd가 시작될 때까지 작업 할당이 실패합니다."
                )
                return
        else:
            logger.info(f"✅ Scrapyd 서버 연결 확인: {self.scrapyd_url}")

        # 프로젝트 배포 확인 및 자동 배포
        logger.info("프로젝트 배포 상태 확인 중...")
        if not self._deploy_project():
            logger.warning(
                "프로젝트 배포 실패. 스케줄링은 계속 시도하지만 실패할 수 있습니다.\n"
                "수동으로 배포하세요: cd worker-nodes/cointicker && scrapyd-deploy"
            )

        # 설정 파일에서 로드한 Spider 스케줄 등록
        for spider_name, spider_info in self.spiders.items():
            schedule_str = spider_info.get("schedule", "*/5 * * * *")
            # cron 형식 파싱 (간단한 형식만 지원: "*/5 * * * *" -> 5분마다)
            if schedule_str.startswith("*/"):
                minutes = int(schedule_str.split()[0].replace("*/", ""))
                schedule.every(minutes).minutes.do(
                    lambda name=spider_name: self.schedule_spider(name)
                )
            elif schedule_str.startswith("0 * * * *"):
                schedule.every(1).hours.do(
                    lambda name=spider_name: self.schedule_spider(name)
                )
            elif schedule_str.startswith("0 0 * * *"):
                schedule.every().day.at("00:00").do(
                    lambda name=spider_name: self.schedule_spider(name)
                )
            else:
                # 기본값: 5분마다
                schedule.every(5).minutes.do(
                    lambda name=spider_name: self.schedule_spider(name)
                )

        enabled_spider_names = list(self.spiders.keys())
        logger.info("=" * 60)
        logger.info(f"✅ Scrapyd 스케줄러 시작 완료")
        logger.info(f"📋 스케줄링 대상 Spider ({len(self.spiders)}개):")
        for spider_name, spider_info in self.spiders.items():
            schedule_str = spider_info.get("schedule", "*/5 * * * *")
            logger.info(f"  - {spider_name}: {schedule_str}")
        logger.info("=" * 60)
        logger.info(
            f"💡 참고: spider_config.yaml에서 enabled: false로 설정하면 스케줄링에서 제외됩니다."
        )

        while True:
            schedule.run_pending()
            time.sleep(60)


if __name__ == "__main__":
    scheduler = ScrapydScheduler()
    scheduler.start()
