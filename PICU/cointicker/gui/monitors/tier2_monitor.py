"""
Tier2 서버 모니터링 모듈
REST API를 통한 백엔드 서버 상태 확인 및 제어

⚠️ 주의: 삭제 및 수정 금지 ⚠️

이 모듈은 백엔드 포트 파일과 연동되어 있습니다:
- get_backend_port_from_file(): config/.backend_port 파일에서 포트 읽기
- get_default_backend_url(): 포트 파일 우선 확인 후 기본값 사용
- Tier2Monitor.__init__(): base_url이 None이면 자동으로 포트 파일에서 읽기

연동된 컴포넌트:
- backend/scripts/run_server.sh: 백엔드 포트 파일 생성 (config/.backend_port)
- gui/app.py: _load_config(), refresh_all(), _reinitialize_tier2_monitor()에서 사용
- gui/modules/backend_module.py: 백엔드 모듈 초기화 시 사용

이 모듈의 포트 파일 읽기 로직을 수정하면 GUI의 백엔드 포트 자동 감지가 작동하지 않습니다.
"""

import requests
import json
from typing import Dict, Optional
from datetime import datetime
from pathlib import Path

from shared.logger import setup_logger
from gui.core.retry_utils import execute_with_retry
from gui.core.timing_config import TimingConfig

logger = setup_logger(__name__)


def get_backend_port_from_file() -> Optional[int]:
    """
    백엔드 포트 파일에서 포트 읽기

    Returns:
        백엔드 포트 번호, 파일이 없으면 None
    """
    try:
        # cointicker/config/.backend_port 파일 확인
        # 경로 계산: gui/tier2_monitor.py -> gui -> cointicker -> cointicker/config
        current_file = Path(__file__)
        logger.debug(f"get_backend_port_from_file: 현재 파일 경로 = {current_file}")

        # ConfigManager와 동일한 방식으로 경로 계산
        # gui/tier2_monitor.py -> gui -> cointicker -> cointicker/config
        config_dir = current_file.parent.parent / "config"
        logger.debug(f"get_backend_port_from_file: config 디렉토리 = {config_dir}")

        port_file = config_dir / ".backend_port"
        logger.debug(f"get_backend_port_from_file: 포트 파일 경로 = {port_file}")

        if port_file.exists():
            port_str = port_file.read_text().strip()
            logger.debug(f"get_backend_port_from_file: 포트 파일 내용 = '{port_str}'")
            if port_str:
                port = int(port_str)
                logger.debug(f"백엔드 포트를 파일에서 읽었습니다: {port}")
                return port
            else:
                logger.debug("포트 파일이 비어있습니다.")
        else:
            logger.debug(f"포트 파일이 존재하지 않습니다: {port_file}")
    except Exception as e:
        logger.error(f"백엔드 포트 파일 읽기 실패: {e}", exc_info=True)

    return None


def get_default_backend_url() -> str:
    """
    기본 백엔드 URL 가져오기 (포트 파일 우선 확인)

    Returns:
        백엔드 URL
    """
    port = get_backend_port_from_file()
    if port:
        url = f"http://localhost:{port}"
        logger.debug(f"get_default_backend_url: 포트 파일에서 읽은 URL = {url}")
        return url
    default_url = "http://localhost:5000"
    logger.warning(
        f"get_default_backend_url: 포트 파일 없음 또는 읽기 실패, 기본 URL 사용 = {default_url}"
    )
    return default_url


class Tier2Monitor:
    """Tier2 서버 모니터 클래스"""

    def __init__(self, base_url: str = None):
        """
        초기화

        Args:
            base_url: Tier2 서버 기본 URL (None이면 자동으로 포트 파일에서 읽기)
        """
        if base_url is None:
            base_url = get_default_backend_url()
            logger.info(f"백엔드 URL 자동 감지: {base_url}")

        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.timeout = 5

    def check_health(self) -> Dict[str, any]:
        """
        서버 헬스 체크 (포트 파일을 다시 확인하여 최신 포트 사용)

        Returns:
            헬스 체크 결과
        """
        try:
            # 매번 포트 파일을 다시 확인하여 최신 포트 사용
            current_url = get_default_backend_url()
            if current_url != self.base_url:
                logger.debug(f"포트 변경 감지: {self.base_url} -> {current_url}")
                self.base_url = current_url.rstrip("/")

            # 재시도 메커니즘 적용
            max_retries = TimingConfig.get("retry.default_max_retries", 3)
            delay = TimingConfig.get("retry.default_delay", 1.0)

            def make_request():
                response = self.session.get(f"{self.base_url}/health")
                response.raise_for_status()
                return response.json()

            data = execute_with_retry(
                make_request,
                max_retries=max_retries,
                delay=delay,
                exceptions=(requests.exceptions.RequestException,),
            )

            return {
                "success": True,
                "online": True,
                "status": data.get("status", "unknown"),
                "database": data.get("database", "unknown"),
                "timestamp": data.get("timestamp", datetime.now().isoformat()),
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"헬스 체크 실패 (재시도 후): {e}")
            return {
                "success": False,
                "online": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def get_dashboard_summary(self) -> Dict[str, any]:
        """
        대시보드 요약 정보 가져오기 (포트 파일을 다시 확인하여 최신 포트 사용)

        Returns:
            대시보드 요약 데이터
        """
        try:
            # 매번 포트 파일을 다시 확인하여 최신 포트 사용
            current_url = get_default_backend_url()
            if current_url != self.base_url:
                logger.debug(f"포트 변경 감지: {self.base_url} -> {current_url}")
                self.base_url = current_url.rstrip("/")

            # 재시도 메커니즘 적용
            max_retries = TimingConfig.get("retry.default_max_retries", 3)
            delay = TimingConfig.get("retry.default_delay", 1.0)

            def make_request():
                response = self.session.get(f"{self.base_url}/api/dashboard/summary")
                response.raise_for_status()
                return response.json()

            data = execute_with_retry(
                make_request,
                max_retries=max_retries,
                delay=delay,
                exceptions=(requests.exceptions.RequestException,),
            )

            return {
                "success": True,
                "data": data,
                "timestamp": datetime.now().isoformat(),
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"대시보드 요약 가져오기 실패 (재시도 후): {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def get_sentiment_timeline(self, hours: int = 24) -> Dict[str, any]:
        """
        감성 추이 데이터 가져오기

        Args:
            hours: 시간 범위

        Returns:
            감성 추이 데이터
        """
        try:
            response = self.session.get(
                f"{self.base_url}/api/dashboard/sentiment-timeline",
                params={"hours": hours},
            )
            response.raise_for_status()
            return {
                "success": True,
                "data": response.json(),
                "timestamp": datetime.now().isoformat(),
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"감성 추이 가져오기 실패: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def get_latest_news(self, limit: int = 50) -> Dict[str, any]:
        """
        최신 뉴스 가져오기

        Args:
            limit: 뉴스 개수 제한

        Returns:
            최신 뉴스 데이터
        """
        try:
            response = self.session.get(
                f"{self.base_url}/api/news/latest", params={"limit": limit}
            )
            response.raise_for_status()
            return {
                "success": True,
                "data": response.json(),
                "timestamp": datetime.now().isoformat(),
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"최신 뉴스 가져오기 실패: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def get_recent_insights(self, limit: int = 20) -> Dict[str, any]:
        """
        최신 인사이트 가져오기

        Args:
            limit: 인사이트 개수 제한

        Returns:
            최신 인사이트 데이터
        """
        try:
            response = self.session.get(
                f"{self.base_url}/api/insights/recent", params={"limit": limit}
            )
            response.raise_for_status()
            return {
                "success": True,
                "data": response.json(),
                "timestamp": datetime.now().isoformat(),
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"최신 인사이트 가져오기 실패: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def generate_insights(self) -> Dict[str, any]:
        """
        인사이트 생성 (수동 트리거)

        Returns:
            인사이트 생성 결과
        """
        try:
            response = self.session.post(f"{self.base_url}/api/insights/generate")
            response.raise_for_status()
            return {
                "success": True,
                "data": response.json(),
                "timestamp": datetime.now().isoformat(),
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"인사이트 생성 실패: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def get_server_status(self) -> Dict[str, any]:
        """
        서버 전체 상태 확인

        Returns:
            서버 상태 정보
        """
        health = self.check_health()
        summary = self.get_dashboard_summary() if health.get("online") else None

        return {
            "online": health.get("online", False),
            "health": health,
            "dashboard_summary": (
                summary.get("data") if summary and summary.get("success") else None
            ),
            "timestamp": datetime.now().isoformat(),
        }
