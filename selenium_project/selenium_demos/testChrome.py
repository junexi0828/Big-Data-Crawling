"""
testChrome.py - Selenium WebDriver 기본 사용법

이 스크립트는 Selenium의 기본 기능을 테스트합니다:
- 브라우저 열기 및 페이지 접속
- 요소 찾기 (By.NAME, By.XPATH 등)
- 텍스트 입력 (send_keys)
- 조건부 대기 (WebDriverWait)
- 폼 제출 (click)
- 다양한 입력 요소 처리 (password, textarea, select, checkbox, radio)
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import os


def test_selenium_form():
    """
    Selenium 폼 입력 테스트
    """
    print("=" * 60)
    print("testChrome - Selenium WebDriver 기본 테스트")
    print("=" * 60)
    
    # ChromeDriver 경로 설정
    chromedriver_path = os.path.expanduser(
        "~/.wdm/drivers/chromedriver/mac64/141.0.7390.78/chromedriver-mac-arm64/chromedriver"
    )
    
    from selenium.webdriver.chrome.service import Service
    service = Service(chromedriver_path)
    
    # WebDriver 초기화
    driver = webdriver.Chrome(service=service)
    
    try:
        # 1. 테스트 페이지 열기
        print("\n1. 페이지 열기: https://www.selenium.dev/selenium/web/web-form.html")
        driver.get("https://www.selenium.dev/selenium/web/web-form.html")
        
        # 2. 조건부 대기 (페이지가 로드될 때까지)
        print("\n2. 조건부 대기: form 요소가 나타날 때까지 대기...")
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.TAG_NAME, "form"))
        )
        
        print(f"[testChrome] 페이지 제목: {driver.title}")
        
        # 3. 텍스트 입력
        print("\n3. 텍스트 입력...")
        text_box = driver.find_element(By.NAME, "my-text")
        text_box.send_keys("minsky")
        print(f"   텍스트 입력 완료: {text_box.get_attribute('value')}")
        
        input("Press Enter to continue.")
        
        # 4. 추가 폼 요소 테스트
        print("\n4. 추가 폼 요소 테스트...")
        
        # Password 입력
        try:
            password_box = driver.find_element(By.NAME, "my-password")
            password_box.send_keys("secret")
            print("   ✅ Password 입력 완료")
        except Exception as e:
            print(f"   ⚠️  Password 입력 실패: {e}")
        
        # Textarea 입력
        try:
            textarea = driver.find_element(By.NAME, "my-textarea")
            textarea.send_keys("This is a sample text.")
            print("   ✅ Textarea 입력 완료")
        except Exception as e:
            print(f"   ⚠️  Textarea 입력 실패: {e}")
        
        # Select (드롭다운) 선택
        try:
            select_elem = Select(driver.find_element(By.NAME, "my-select"))
            select_elem.select_by_visible_text("Two")
            print("   ✅ Select 선택 완료: Two")
        except Exception as e:
            print(f"   ⚠️  Select 선택 실패: {e}")
        
        # Checkbox 선택
        try:
            checkbox = driver.find_element(By.NAME, "my-check")
            if not checkbox.is_selected():
                checkbox.click()
            print("   ✅ Checkbox 선택 완료")
        except Exception as e:
            print(f"   ⚠️  Checkbox 선택 실패: {e}")
        
        # Radio 버튼 선택
        try:
            radio = driver.find_element(By.ID, "my-radio-2")
            radio.click()
            print("   ✅ Radio 버튼 선택 완료")
        except Exception as e:
            print(f"   ⚠️  Radio 버튼 선택 실패: {e}")
        
        input("Press Enter to continue.")
        
        # 5. 폼 제출
        print("\n5. 폼 제출...")
        submit_button = driver.find_element(By.XPATH, '//button[@type="submit"]')
        submit_button.click()
        
        print("Form submitted.")
        
        input("Press Enter to continue.")
        
        print("\n✅ 테스트 완료!")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\n브라우저 종료")
        driver.quit()


if __name__ == "__main__":
    test_selenium_form()

