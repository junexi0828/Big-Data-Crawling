"""
Selenium WebDriver 기본 설정

이 모듈은 Selenium WebDriver의 기본 설정과 옵션을 제공합니다.
"""

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


def get_chrome_driver(headless=False):
    """
    Chrome WebDriver 생성 및 반환
    
    Args:
        headless (bool): 헤드리스 모드 사용 여부
        
    Returns:
        webdriver.Chrome: 설정된 Chrome WebDriver
    """
    # Chrome 옵션 설정
    chrome_options = Options()
    
    if headless:
        chrome_options.add_argument('--headless')  # 헤드리스 모드 (브라우저 UI 숨김)
    
    # 추가 옵션
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--window-size=1920,1080')
    
    # User-Agent 설정 (선택사항)
    chrome_options.add_argument(
        'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )
    
    # WebDriver Manager로 ChromeDriver 자동 설치
    service = Service(ChromeDriverManager().install())
    
    # WebDriver 생성
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # 암묵적 대기 시간 설정 (초)
    driver.implicitly_wait(10)
    
    return driver


def print_driver_info(driver):
    """
    WebDriver 정보 출력
    
    Args:
        driver: Selenium WebDriver 인스턴스
    """
    print("=" * 60)
    print("WebDriver 정보")
    print("=" * 60)
    print(f"브라우저: {driver.capabilities['browserName']}")
    print(f"버전: {driver.capabilities['browserVersion']}")
    print(f"플랫폼: {driver.capabilities['platformName']}")
    print(f"현재 URL: {driver.current_url}")
    print(f"창 크기: {driver.get_window_size()}")
    print("=" * 60)


if __name__ == "__main__":
    print("Selenium WebDriver 설정 테스트\n")
    
    # 일반 모드 테스트
    print("1. 일반 모드 WebDriver 생성...")
    driver = get_chrome_driver(headless=False)
    
    # 테스트 페이지 방문
    driver.get("https://www.google.com")
    print_driver_info(driver)
    
    # 브라우저 종료
    driver.quit()
    print("\n✅ 일반 모드 테스트 완료")
    
    # 헤드리스 모드 테스트
    print("\n2. 헤드리스 모드 WebDriver 생성...")
    driver_headless = get_chrome_driver(headless=True)
    
    # 테스트 페이지 방문
    driver_headless.get("https://www.google.com")
    print_driver_info(driver_headless)
    
    # 브라우저 종료
    driver_headless.quit()
    print("\n✅ 헤드리스 모드 테스트 완료")
    
    print("\n" + "=" * 60)
    print("모든 테스트가 성공적으로 완료되었습니다! 🎉")
    print("=" * 60)

