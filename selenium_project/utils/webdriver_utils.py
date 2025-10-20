"""
WebDriver 유틸리티 모듈

ChromeDriver 설정, 권한 관리, 공통 옵션 등을 제공합니다.
"""

import os
import stat
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


def ensure_chromedriver_executable(chromedriver_path):
    """
    ChromeDriver에 실행 권한이 있는지 확인하고, 없으면 부여합니다.
    
    Args:
        chromedriver_path (str): ChromeDriver 경로
        
    Returns:
        bool: 권한 설정 성공 여부
    """
    try:
        if not os.path.exists(chromedriver_path):
            print(f"⚠️  ChromeDriver를 찾을 수 없습니다: {chromedriver_path}")
            return False
        
        # 현재 권한 확인
        current_permissions = os.stat(chromedriver_path).st_mode
        
        # 실행 권한이 있는지 확인
        if not (current_permissions & stat.S_IXUSR):
            print(f"🔧 ChromeDriver에 실행 권한 부여 중: {chromedriver_path}")
            # 소유자에게 실행 권한 부여 (현재 권한 + 실행 권한)
            os.chmod(chromedriver_path, current_permissions | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            print("✅ 실행 권한 부여 완료")
        
        return True
        
    except Exception as e:
        print(f"❌ 권한 설정 실패: {e}")
        return False


def get_chromedriver_path():
    """
    ChromeDriver 경로를 반환합니다.
    
    1. 미리 다운로드된 경로 확인
    2. 없으면 webdriver-manager로 자동 다운로드
    
    Returns:
        str: ChromeDriver 경로
    """
    # 1. 미리 다운로드된 ChromeDriver 경로
    predefined_path = os.path.expanduser(
        "~/.wdm/drivers/chromedriver/mac64/141.0.7390.78/chromedriver-mac-arm64/chromedriver"
    )
    
    if os.path.exists(predefined_path):
        print(f"✅ ChromeDriver 발견: {predefined_path}")
        # 실행 권한 확인 및 부여
        ensure_chromedriver_executable(predefined_path)
        return predefined_path
    
    # 2. webdriver-manager로 자동 다운로드
    print("🔍 ChromeDriver를 자동으로 다운로드합니다...")
    try:
        driver_path = ChromeDriverManager().install()
        print(f"✅ ChromeDriver 다운로드 완료: {driver_path}")
        # 실행 권한 확인 및 부여
        ensure_chromedriver_executable(driver_path)
        return driver_path
    except Exception as e:
        print(f"❌ ChromeDriver 다운로드 실패: {e}")
        raise


def create_chrome_driver(headless=False, disable_blink=False, custom_user_agent=None):
    """
    Chrome WebDriver를 생성합니다.
    
    Args:
        headless (bool): 헤드리스 모드 사용 여부
        disable_blink (bool): AutomationControlled 비활성화 (Google 감지 우회)
        custom_user_agent (str): 커스텀 User-Agent (None이면 기본값 사용)
        
    Returns:
        webdriver.Chrome: 설정된 Chrome WebDriver
    """
    print("\n" + "=" * 60)
    print("Chrome WebDriver 초기화")
    print("=" * 60)
    
    # Chrome 옵션 설정
    options = Options()
    
    # 헤드리스 모드
    if headless:
        print("🔹 헤드리스 모드 활성화")
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
    
    # AutomationControlled 비활성화 (Google 감지 우회)
    if disable_blink:
        print("🔹 AutomationControlled 비활성화 (감지 우회)")
        options.add_argument("--disable-blink-features=AutomationControlled")
    
    # 기본 옵션
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    
    # User-Agent 설정
    if custom_user_agent:
        print(f"🔹 커스텀 User-Agent 설정")
        options.add_argument(f'user-agent={custom_user_agent}')
    else:
        # 기본 User-Agent
        default_ua = (
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        options.add_argument(f'user-agent={default_ua}')
    
    # ChromeDriver 경로 가져오기 (권한 자동 설정 포함)
    chromedriver_path = get_chromedriver_path()
    
    # Service 생성
    service = Service(chromedriver_path)
    
    # WebDriver 생성
    print("🔹 Chrome WebDriver 생성 중...")
    driver = webdriver.Chrome(service=service, options=options)
    
    # 암묵적 대기 시간 설정
    driver.implicitly_wait(10)
    
    print("✅ Chrome WebDriver 초기화 완료")
    print("=" * 60 + "\n")
    
    return driver


def setup_navigator_webdriver_false(driver):
    """
    navigator.webdriver를 false로 설정합니다. (Google 감지 우회)
    
    Args:
        driver: Selenium WebDriver 인스턴스
    """
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {
            "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            """
        }
    )
    print("✅ navigator.webdriver = undefined 설정 완료")


def fix_all_chromedrivers_permissions():
    """
    webdriver-manager가 다운로드한 모든 ChromeDriver에 실행 권한을 부여합니다.
    """
    print("\n" + "=" * 60)
    print("모든 ChromeDriver 권한 설정")
    print("=" * 60)
    
    wdm_dir = os.path.expanduser("~/.wdm/drivers/chromedriver")
    
    if not os.path.exists(wdm_dir):
        print(f"⚠️  ChromeDriver 디렉토리를 찾을 수 없습니다: {wdm_dir}")
        return
    
    count = 0
    for root, dirs, files in os.walk(wdm_dir):
        for file in files:
            if file == "chromedriver":
                filepath = os.path.join(root, file)
                if ensure_chromedriver_executable(filepath):
                    count += 1
    
    print(f"\n✅ {count}개의 ChromeDriver에 실행 권한 부여 완료")
    print("=" * 60)


if __name__ == "__main__":
    print("🚀 ChromeDriver 유틸리티 테스트\n")
    
    # 1. 모든 ChromeDriver 권한 설정
    fix_all_chromedrivers_permissions()
    
    # 2. WebDriver 생성 테스트
    print("\n\n=== WebDriver 생성 테스트 ===\n")
    driver = create_chrome_driver(headless=True)
    
    # 3. 간단한 테스트
    driver.get("https://www.google.com")
    print(f"\n페이지 제목: {driver.title}")
    
    # 4. 종료
    driver.quit()
    print("\n✅ 모든 테스트 완료!")

