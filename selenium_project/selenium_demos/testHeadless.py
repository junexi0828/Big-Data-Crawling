"""
testHeadless.py - WebDriver Configuration (헤드리스 모드 & User-Agent)

이 스크립트는 WebDriver의 고급 설정을 테스트합니다:
1. 헤드리스 브라우징 (브라우저 UI 없이 실행)
2. User-Agent 변경
3. 다양한 Chrome 옵션
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import os


def test_headless_and_useragent():
    """
    헤드리스 모드 및 User-Agent 테스트
    """
    print("=" * 60)
    print("testHeadless - WebDriver Configuration 테스트")
    print("=" * 60)
    
    # Chrome 옵션 설정
    options = Options()
    
    # 1. 헤드리스 모드
    print("\n1. 헤드리스 모드 활성화...")
    options.add_argument('--headless')
    
    # 2. GPU 비활성화 (헤드리스 모드에서 권장)
    options.add_argument('--disable-gpu')
    
    # 3. 언어 설정
    options.add_argument('--lang=ko_KR')
    
    # 4. User-Agent 변경
    print("2. User-Agent 변경...")
    user_agent = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/91.0.4472.77 Safari/537.36"
    )
    options.add_argument(f'user-agent={user_agent}')
    
    print(f"   설정된 User-Agent: {user_agent}")
    
    # ChromeDriver 경로 설정
    chromedriver_path = os.path.expanduser(
        "~/.wdm/drivers/chromedriver/mac64/141.0.7390.78/chromedriver-mac-arm64/chromedriver"
    )
    
    from selenium.webdriver.chrome.service import Service
    service = Service(chromedriver_path)
    
    # WebDriver 초기화
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        # Naver Finance 접속
        print("\n3. Naver Finance 접속 (헤드리스 모드)...")
        driver.get("https://finance.naver.com/marketindex/")
        
        time.sleep(2)
        
        # User-Agent 확인
        print("\n4. User-Agent 확인...")
        user_agent_result = driver.execute_script("return navigator.userAgent;")
        print(f"   실제 User-Agent: {user_agent_result}")
        
        # 환율고시 날짜 추출
        print("\n5. 환율고시 날짜 추출...")
        date = driver.find_element(By.XPATH, "//div[@class='exchange_info']/span[1]")
        print(f"   환율고시 날짜: {date.text}")
        
        # iframe으로 전환하여 환율 정보 추출
        print("\n6. iframe으로 전환하여 환율 정보 추출...")
        driver.switch_to.frame('frame_ex1')
        
        rows = driver.find_elements(By.XPATH, "//html/body/div/table/tbody/tr")
        print(f"   찾은 환율 정보: {len(rows)}개")
        
        print("\n   처음 5개 환율:")
        for i, row in enumerate(rows[:5]):
            try:
                title = row.find_element(By.XPATH, ".//td[@class='tit']/a").text
                rate = row.find_element(By.XPATH, ".//td[@class='sale']").text
                print(f"   {i+1}. {title}: {rate}")
            except Exception as e:
                pass
        
        # 메인 윈도우로 복귀
        driver.switch_to.default_content()
        
        print("\n✅ 헤드리스 모드 및 User-Agent 테스트 완료!")
        print("   (브라우저 UI가 표시되지 않았지만 정상적으로 작동했습니다)")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\n브라우저 종료")
        driver.quit()


def compare_normal_vs_headless():
    """
    일반 모드와 헤드리스 모드 비교
    """
    print("\n" + "=" * 60)
    print("일반 모드 vs 헤드리스 모드 비교")
    print("=" * 60)
    
    # ChromeDriver 경로
    chromedriver_path = os.path.expanduser(
        "~/.wdm/drivers/chromedriver/mac64/141.0.7390.78/chromedriver-mac-arm64/chromedriver"
    )
    
    from selenium.webdriver.chrome.service import Service
    service = Service(chromedriver_path)
    
    # 1. 일반 모드
    print("\n1. 일반 모드 테스트...")
    driver_normal = webdriver.Chrome(service=service)
    
    start_time = time.time()
    driver_normal.get("https://www.google.com")
    normal_time = time.time() - start_time
    print(f"   일반 모드 로딩 시간: {normal_time:.2f}초")
    
    driver_normal.quit()
    
    # 2. 헤드리스 모드
    print("\n2. 헤드리스 모드 테스트...")
    options = Options()
    options.add_argument('--headless')
    
    driver_headless = webdriver.Chrome(service=service, options=options)
    
    start_time = time.time()
    driver_headless.get("https://www.google.com")
    headless_time = time.time() - start_time
    print(f"   헤드리스 모드 로딩 시간: {headless_time:.2f}초")
    
    driver_headless.quit()
    
    # 비교
    print("\n" + "=" * 60)
    print(f"일반 모드:     {normal_time:.2f}초")
    print(f"헤드리스 모드: {headless_time:.2f}초")
    print(f"속도 차이:     {abs(normal_time - headless_time):.2f}초")
    print("=" * 60)


if __name__ == "__main__":
    # 헤드리스 및 User-Agent 테스트
    test_headless_and_useragent()
    
    # 일반 모드 vs 헤드리스 모드 비교
    # compare_normal_vs_headless()

