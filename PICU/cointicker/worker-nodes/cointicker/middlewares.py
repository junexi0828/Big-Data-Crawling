"""
Scrapy Middlewares
"""

import random
import logging
import sys
from pathlib import Path
from scrapy import signals
from scrapy.http import HtmlResponse
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware

# 통합 경로 설정 유틸리티 사용
try:
    from shared.path_utils import setup_pythonpath
    setup_pythonpath()
except ImportError:
    # Fallback: 유틸리티 로드 실패 시 하드코딩 경로 사용
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent.parent
    shared_path = project_root / "shared"
    sys.path.insert(0, str(shared_path))

from shared.selenium_utils import (
    create_chrome_driver,
    wait_for_page_load,
    scroll_to_bottom,
    safe_quit_driver,
)
from shared.logger import setup_logger

logger = setup_logger(__name__)


class CoinTickerSpiderMiddleware:
    """Spider 미들웨어"""

    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        return None

    def process_spider_output(self, response, result, spider):
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        pass

    def process_start_requests(self, start_requests, spider):
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info(f"Spider opened: {spider.name}")


class CoinTickerDownloaderMiddleware:
    """다운로더 미들웨어"""

    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        return None

    def process_response(self, request, response, spider):
        return response

    def process_exception(self, request, exception, spider):
        pass

    def spider_opened(self, spider):
        spider.logger.info(f"Spider opened: {spider.name}")


class RotateUserAgentMiddleware(UserAgentMiddleware):
    """User-Agent 회전 미들웨어"""

    def __init__(self, user_agent_list=None):
        """settings.py에서 USER_AGENT_LIST를 가져옴"""
        self.user_agent_list = user_agent_list or []

    @classmethod
    def from_crawler(cls, crawler):
        """Crawler에서 설정을 읽어 미들웨어 생성"""
        user_agent_list = crawler.settings.getlist("USER_AGENT_LIST", [])
        return cls(user_agent_list=user_agent_list)

    def process_request(self, request, spider):
        """User-Agent 회전"""
        if self.user_agent_list:
            ua = random.choice(self.user_agent_list)
            request.headers["User-Agent"] = ua
        return None


class SeleniumMiddleware:
    """
    Selenium을 사용한 동적 콘텐츠 처리 미들웨어

    특정 요청에 대해 Selenium WebDriver를 사용하여 JavaScript로 렌더링된
    페이지를 처리합니다.

    사용 방법:
    1. Spider에서 request.meta['selenium'] = True 설정
    2. 또는 settings.py에서 SELENIUM_ENABLED_DOMAINS에 도메인 추가
    """

    def __init__(self, enabled_domains=None, headless=True, scroll=False):
        """
        초기화

        Args:
            enabled_domains: Selenium을 사용할 도메인 리스트 (None이면 모든 도메인)
            headless: 헤드리스 모드 사용 여부
            scroll: 페이지 끝까지 스크롤 여부 (동적 콘텐츠 로드용)
        """
        self.enabled_domains = enabled_domains or []
        self.headless = headless
        self.scroll = scroll
        self.driver = None

    @classmethod
    def from_crawler(cls, crawler):
        """Crawler에서 설정을 읽어 미들웨어 생성"""
        enabled_domains = crawler.settings.getlist("SELENIUM_ENABLED_DOMAINS", [])
        headless = crawler.settings.getbool("SELENIUM_HEADLESS", True)
        scroll = crawler.settings.getbool("SELENIUM_SCROLL", False)

        middleware = cls(
            enabled_domains=enabled_domains, headless=headless, scroll=scroll
        )

        # Spider 종료 시 WebDriver 정리
        crawler.signals.connect(middleware.spider_closed, signal=signals.spider_closed)

        return middleware

    def process_request(self, request, spider):
        """
        요청 처리

        Selenium이 필요한 요청인지 확인하고, 필요하면 WebDriver로 처리합니다.

        Args:
            request: Scrapy Request 객체
            spider: Spider 인스턴스

        Returns:
            HtmlResponse 또는 None (None이면 다음 미들웨어로 전달)
        """
        # Selenium 사용 여부 확인
        use_selenium = request.meta.get("selenium", False)

        # 도메인 기반 확인
        if not use_selenium and self.enabled_domains:
            from urllib.parse import urlparse

            parsed_url = urlparse(request.url)
            use_selenium = parsed_url.netloc in self.enabled_domains

        if not use_selenium:
            return None  # 다음 미들웨어로 전달

        spider.logger.info(f"Selenium으로 처리: {request.url}")

        # WebDriver 초기화 (아직 없으면)
        if self.driver is None:
            try:
                self.driver = create_chrome_driver(
                    headless=self.headless,
                    disable_blink=True,
                    custom_user_agent=request.headers.get("User-Agent", b"").decode(
                        "utf-8"
                    ),
                )
                spider.logger.info("Selenium WebDriver 초기화 완료")
            except Exception as e:
                spider.logger.error(f"WebDriver 초기화 실패: {e}")
                return None  # 실패 시 일반 요청으로 처리

        # Selenium으로 페이지 로드
        try:
            self.driver.get(request.url)

            # 페이지 로드 대기
            wait_for_page_load(self.driver, timeout=30)

            # 스크롤 (동적 콘텐츠 로드용)
            if self.scroll:
                scroll_to_bottom(self.driver, pause_time=1.0)

            # HTML 가져오기
            body = self.driver.page_source.encode("utf-8")

            # HtmlResponse 생성
            response = HtmlResponse(
                url=request.url, body=body, encoding="utf-8", request=request
            )

            spider.logger.debug(
                f"Selenium 처리 완료: {request.url} ({len(body)} bytes)"
            )
            return response

        except Exception as e:
            spider.logger.error(f"Selenium 처리 오류 {request.url}: {e}")
            # 오류 발생 시 일반 요청으로 폴백
            return None

    def spider_closed(self, spider):
        """Spider 종료 시 WebDriver 정리"""
        if self.driver is not None:
            spider.logger.info("Selenium WebDriver 종료 중...")
            safe_quit_driver(self.driver)
            self.driver = None
