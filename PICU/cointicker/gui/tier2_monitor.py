"""
Tier2 서버 모니터링 모듈
REST API를 통한 백엔드 서버 상태 확인 및 제어
"""

import requests
import json
from typing import Dict, Optional
from datetime import datetime

from shared.logger import setup_logger

logger = setup_logger(__name__)


class Tier2Monitor:
    """Tier2 서버 모니터 클래스"""

    def __init__(self, base_url: str = "http://localhost:5000"):
        """
        초기화

        Args:
            base_url: Tier2 서버 기본 URL
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.timeout = 5

    def check_health(self) -> Dict[str, any]:
        """
        서버 헬스 체크

        Returns:
            헬스 체크 결과
        """
        try:
            response = self.session.get(f"{self.base_url}/health")
            response.raise_for_status()
            data = response.json()

            return {
                "success": True,
                "online": True,
                "status": data.get("status", "unknown"),
                "database": data.get("database", "unknown"),
                "timestamp": data.get("timestamp", datetime.now().isoformat())
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"헬스 체크 실패: {e}")
            return {
                "success": False,
                "online": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def get_dashboard_summary(self) -> Dict[str, any]:
        """
        대시보드 요약 정보 가져오기

        Returns:
            대시보드 요약 데이터
        """
        try:
            response = self.session.get(f"{self.base_url}/api/dashboard/summary")
            response.raise_for_status()
            return {
                "success": True,
                "data": response.json(),
                "timestamp": datetime.now().isoformat()
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"대시보드 요약 가져오기 실패: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
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
                params={"hours": hours}
            )
            response.raise_for_status()
            return {
                "success": True,
                "data": response.json(),
                "timestamp": datetime.now().isoformat()
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"감성 추이 가져오기 실패: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
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
                f"{self.base_url}/api/news/latest",
                params={"limit": limit}
            )
            response.raise_for_status()
            return {
                "success": True,
                "data": response.json(),
                "timestamp": datetime.now().isoformat()
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"최신 뉴스 가져오기 실패: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
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
                f"{self.base_url}/api/insights/recent",
                params={"limit": limit}
            )
            response.raise_for_status()
            return {
                "success": True,
                "data": response.json(),
                "timestamp": datetime.now().isoformat()
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"최신 인사이트 가져오기 실패: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
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
                "timestamp": datetime.now().isoformat()
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"인사이트 생성 실패: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
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
            "dashboard_summary": summary.get("data") if summary and summary.get("success") else None,
            "timestamp": datetime.now().isoformat()
        }

