"""
testGoogle.py - Google 검색 테스트 (navigator.webdriver 우회)

Google 사이트는 Selenium을 감지할 수 있습니다 (navigator.webdriver = true).
이 스크립트는 CDP(Chrome DevTool Protocol)를 사용하여 이를 우회합니다.
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import os


def test_google_search():
    """
    Google 검색 테스트 (navigator.webdriver 비활성화)
    """
    print("=" * 60)
    print("testGoogle - Google 검색 테스트")
    print("=" * 60)
    
    # Chrome 옵션 설정
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    # ChromeDriver 경로 설정
    chromedriver_path = os.path.expanduser(
        "~/.wdm/drivers/chromedriver/mac64/141.0.7390.78/chromedriver-mac-arm64/chromedriver"
    )
    
    from selenium.webdriver.chrome.service import Service
    service = Service(chromedriver_path)
    
    # WebDriver 초기화
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        # CDP를 사용하여 navigator.webdriver를 undefined로 설정
        print("\n1. CDP를 사용하여 navigator.webdriver 비활성화...")
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
        
        # Google 접속
        print("\n2. Google 접속...")
        driver.get("https://www.google.com")
        print(f"[testChrome] 페이지 제목: {driver.title}")
        
        time.sleep(2)
        
        # 검색창 찾기 및 키워드 입력
        print("\n3. 검색창 찾기 및 키워드 입력...")
        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys("scrapy selenium")
        print(f"[testChrome] 검색창 입력: {search_box.get_attribute('value')}")
        
        time.sleep(3)
        
        # 검색 제출 (Enter 키)
        print("\n4. 검색 제출...")
        search_box.send_keys(Keys.RETURN)  # search_box.submit()와 동일
        
        time.sleep(5)
        
        print("\n✅ Google 검색 테스트 완료!")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\n브라우저 종료")
        driver.quit()


if __name__ == "__main__":
    test_google_search()

