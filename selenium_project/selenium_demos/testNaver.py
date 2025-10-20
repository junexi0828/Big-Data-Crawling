"""
testNaver.py - Naver Finance 스크래핑 테스트

이 스크립트는 Naver Finance의 환율 정보를 스크래핑합니다:
1. 페이지 소스 확인
2. iframe으로 전환
3. 환율 데이터 추출
4. 메인 윈도우로 복귀
5. 탭 클릭 및 테이블 추출
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os


def test_naver_finance():
    """
    Naver Finance 환율 정보 스크래핑
    """
    print("=" * 60)
    print("testNaver - Naver Finance 스크래핑 테스트")
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
        # 1. Naver Finance 페이지 접속
        print("\n1. Naver Finance 페이지 접속...")
        driver.get("https://finance.naver.com/marketindex/")
        
        time.sleep(2)
        
        # 2. 전체 웹페이지 소스 확인
        print("\n2. 전체 웹페이지 소스 확인...")
        html = driver.page_source
        print("=== Whole Webpage ===")
        print(html[:500])  # 처음 500자만 출력
        
        # 3. 환율고시 날짜 추출
        print("\n3. 환율고시 날짜 추출...")
        date = driver.find_element(By.XPATH, "//div[@class='exchange_info']/span[1]")
        item = {"date": date.text}
        print(f"   환율고시 날짜: {item['date']}")
        
        # 4. iframe으로 전환
        print("\n4. iframe으로 전환: 'frame_ex1'")
        driver.switch_to.frame('frame_ex1')
        print("=== iframe Webpage ===")
        print(driver.page_source[:500])  # 처음 500자만 출력
        
        # 5. iframe 내부 환율 데이터 추출
        print("\n5. iframe 내부 환율 데이터 추출...")
        rows = driver.find_elements(By.XPATH, "//html/body/div/table/tbody/tr")
        
        print(f"   찾은 행 개수: {len(rows)}")
        print("\n   환율 정보 (처음 10개):")
        
        for i, row in enumerate(rows[:10]):
            try:
                title = row.find_element(By.XPATH, ".//td[@class='tit']/a").text
                rate = float(row.find_element(By.XPATH, ".//td[@class='sale']").text.replace(',', ''))
                item[title] = rate
                print(f"   {i+1}. {title}: {rate}")
            except Exception as e:
                print(f"   ⚠️  행 {i+1} 처리 실패: {e}")
        
        print(f"\nitem: {item}")
        
        # 6. 메인 윈도우로 복귀
        print("\n6. 메인 윈도우로 복귀...")
        driver.switch_to.default_content()
        
        # 7. 추가 기능: 탭 클릭 및 테이블 추출
        print("\n7. 추가 기능: 탭 클릭 및 테이블 추출...")
        
        # 특정 탭 클릭 (예: 세 번째 li의 a 태그)
        try:
            targetTab = driver.find_element(By.XPATH, "//*[@id='tab_section']/ul/li[3]/a")
            targetTab.click()
            time.sleep(2)
            print("   ✅ 탭 클릭 완료")
            
            # 테이블 정보 추출
            tables = driver.find_elements(By.XPATH, "//table[@class='tbl_exchange']")
            for i, table in enumerate(tables):
                summary = table.get_attribute("summary")
                print(f"   테이블 {i+1} summary: {summary}")
        except Exception as e:
            print(f"   ⚠️  탭 클릭/테이블 추출 실패: {e}")
        
        time.sleep(3)
        
        print("\n✅ Naver Finance 스크래핑 테스트 완료!")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\n브라우저 종료")
        driver.quit()


if __name__ == "__main__":
    test_naver_finance()

