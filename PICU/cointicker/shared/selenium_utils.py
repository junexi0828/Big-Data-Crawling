"""
Selenium WebDriver 유틸리티
Scrapy와 통합하여 동적 콘텐츠를 처리하는 유틸리티 함수
"""

import os
import stat
import time
from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException

try:
    from webdriver_manager.chrome import ChromeDriverManager

    WEBDRIVER_MANAGER_AVAILABLE = True
except ImportError:
    WEBDRIVER_MANAGER_AVAILABLE = False

from shared.logger import setup_logger

logger = setup_logger(__name__)


def ensure_chromedriver_executable(chromedriver_path: str) -> bool:
    """
    ChromeDriver에 실행 권한이 있는지 확인하고, 없으면 부여합니다.

    Args:
        chromedriver_path: ChromeDriver 경로

    Returns:
        권한 설정 성공 여부
    """
    try:
        if not os.path.exists(chromedriver_path):
            logger.warning(f"ChromeDriver를 찾을 수 없습니다: {chromedriver_path}")
            return False

        # 현재 권한 확인
        current_permissions = os.stat(chromedriver_path).st_mode

        # 실행 권한이 있는지 확인
        if not (current_permissions & stat.S_IXUSR):
            logger.info(f"ChromeDriver에 실행 권한 부여 중: {chromedriver_path}")
            # 소유자에게 실행 권한 부여
            os.chmod(
                chromedriver_path,
                current_permissions | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH,
            )
            logger.info("실행 권한 부여 완료")

        return True

    except Exception as e:
        logger.error(f"권한 설정 실패: {e}")
        return False


def get_chromedriver_path() -> str:
    """
    ChromeDriver 경로를 반환합니다.

    1. 환경변수 CHROMEDRIVER_PATH 확인
    2. 미리 다운로드된 경로 확인
    3. 없으면 webdriver-manager로 자동 다운로드

    Returns:
        ChromeDriver 경로
    """
    # 1. 환경변수 확인
    env_path = os.environ.get("CHROMEDRIVER_PATH")
    if env_path and os.path.exists(env_path):
        ensure_chromedriver_executable(env_path)
        return env_path

    # 2. 미리 다운로드된 ChromeDriver 경로 (macOS)
    predefined_paths = [
        os.path.expanduser(
            "~/.wdm/drivers/chromedriver/mac64/*/chromedriver-mac-arm64/chromedriver"
        ),
        os.path.expanduser(
            "~/.wdm/drivers/chromedriver/mac64/*/chromedriver-mac-x64/chromedriver"
        ),
        os.path.expanduser("~/.wdm/drivers/chromedriver/linux64/*/chromedriver"),
        os.path.expanduser("~/.wdm/drivers/chromedriver/win64/*/chromedriver.exe"),
    ]

    import glob

    for pattern in predefined_paths:
        matches = glob.glob(pattern)
        if matches:
            driver_path = matches[0]
            if ensure_chromedriver_executable(driver_path):
                logger.info(f"ChromeDriver 발견: {driver_path}")
                return driver_path

    # 3. webdriver-manager로 자동 다운로드
    if WEBDRIVER_MANAGER_AVAILABLE:
        logger.info("ChromeDriver를 자동으로 다운로드합니다...")
        try:
            driver_path = ChromeDriverManager().install()
            ensure_chromedriver_executable(driver_path)
            logger.info(f"ChromeDriver 다운로드 완료: {driver_path}")
            return driver_path
        except Exception as e:
            logger.error(f"ChromeDriver 다운로드 실패: {e}")
            raise

    raise RuntimeError(
        "ChromeDriver를 찾을 수 없습니다. "
        "환경변수 CHROMEDRIVER_PATH를 설정하거나 webdriver-manager를 설치하세요."
    )


def create_chrome_driver(
    headless: bool = True,
    disable_blink: bool = True,
    custom_user_agent: Optional[str] = None,
    window_size: tuple = (1920, 1080),
    implicit_wait: int = 10,
) -> webdriver.Chrome:
    """
    Chrome WebDriver를 생성합니다.

    Args:
        headless: 헤드리스 모드 사용 여부
        disable_blink: AutomationControlled 비활성화 (감지 우회)
        custom_user_agent: 커스텀 User-Agent
        window_size: 창 크기 (width, height)
        implicit_wait: 암묵적 대기 시간 (초)

    Returns:
        설정된 Chrome WebDriver
    """
    logger.info("Chrome WebDriver 초기화 시작")

    # Chrome 옵션 설정
    options = Options()

    # 헤드리스 모드
    if headless:
        logger.debug("헤드리스 모드 활성화")
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

    # AutomationControlled 비활성화 (감지 우회)
    if disable_blink:
        logger.debug("AutomationControlled 비활성화 (감지 우회)")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

    # 기본 옵션
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"--window-size={window_size[0]},{window_size[1]}")
    options.add_argument("--disable-blink-features=AutomationControlled")

    # User-Agent 설정
    if custom_user_agent:
        logger.debug(f"커스텀 User-Agent 설정: {custom_user_agent[:50]}...")
        options.add_argument(f"user-agent={custom_user_agent}")
    else:
        # 기본 User-Agent
        default_ua = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        options.add_argument(f"user-agent={default_ua}")

    # ChromeDriver 경로 가져오기
    try:
        chromedriver_path = get_chromedriver_path()
    except Exception as e:
        logger.error(f"ChromeDriver 경로 가져오기 실패: {e}")
        raise

    # Service 생성
    service = Service(chromedriver_path)

    # WebDriver 생성
    try:
        driver = webdriver.Chrome(service=service, options=options)

        # navigator.webdriver 비활성화 (감지 우회)
        if disable_blink:
            driver.execute_cdp_cmd(
                "Page.addScriptToEvaluateOnNewDocument",
                {
                    "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                    """
                },
            )
            logger.debug("navigator.webdriver = undefined 설정 완료")

        # 암묵적 대기 시간 설정
        driver.implicitly_wait(implicit_wait)

        logger.info("Chrome WebDriver 초기화 완료")
        return driver

    except WebDriverException as e:
        logger.error(f"WebDriver 생성 실패: {e}")
        raise


def wait_for_element(
    driver: webdriver.Chrome, by: By, value: str, timeout: int = 10
) -> Optional[object]:
    """
    요소가 나타날 때까지 대기합니다.

    Args:
        driver: WebDriver 인스턴스
        by: 요소 찾기 방식 (By.ID, By.CSS_SELECTOR 등)
        value: 요소 선택자
        timeout: 타임아웃 (초)

    Returns:
        찾은 요소 또는 None
    """
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return element
    except TimeoutException:
        logger.warning(f"요소를 찾을 수 없습니다: {by}={value} (timeout: {timeout}초)")
        return None


def wait_for_page_load(driver: webdriver.Chrome, timeout: int = 30) -> bool:
    """
    페이지 로드가 완료될 때까지 대기합니다.

    Args:
        driver: WebDriver 인스턴스
        timeout: 타임아웃 (초)

    Returns:
        로드 완료 여부
    """
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        return True
    except TimeoutException:
        logger.warning(f"페이지 로드 타임아웃: {timeout}초")
        return False


def scroll_to_bottom(driver: webdriver.Chrome, pause_time: float = 1.0) -> None:
    """
    페이지를 끝까지 스크롤합니다 (동적 콘텐츠 로드용).

    Args:
        driver: WebDriver 인스턴스
        pause_time: 스크롤 간 대기 시간 (초)
    """
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # 페이지 끝까지 스크롤
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # 새 콘텐츠 로드 대기
        time.sleep(pause_time)

        # 새로운 높이 계산
        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            break

        last_height = new_height

    logger.debug("페이지 스크롤 완료")


def safe_quit_driver(driver: Optional[webdriver.Chrome]) -> None:
    """
    WebDriver를 안전하게 종료합니다.

    Args:
        driver: WebDriver 인스턴스 (None 가능)
    """
    if driver is None:
        return

    try:
        driver.quit()
        logger.debug("WebDriver 종료 완료")
    except Exception as e:
        logger.warning(f"WebDriver 종료 중 오류: {e}")
        try:
            driver.close()
        except:
            pass
