"""
iframe 처리 예제

이 스크립트는 Selenium을 사용하여 iframe 내부의 콘텐츠에 접근하는 방법을 보여줍니다.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time


def demonstrate_iframe_handling():
    """
    iframe 처리 기본 예제
    """
    print("=" * 60)
    print("iframe 처리 데모")
    print("=" * 60)
    
    # WebDriver 설정
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    
    try:
        # W3Schools iframe 예제 페이지 방문
        url = "https://www.w3schools.com/html/html_iframe.asp"
        print(f"\n1. 페이지 로드: {url}")
        driver.get(url)
        
        # 페이지 로드 대기
        time.sleep(2)
        
        # 페이지 제목 출력
        print(f"   메인 페이지 제목: {driver.title}")
        
        # iframe 찾기 (첫 번째 iframe)
        print("\n2. iframe 찾기...")
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        print(f"   찾은 iframe 개수: {len(iframes)}")
        
        if iframes:
            # 첫 번째 iframe으로 전환
            print("\n3. iframe으로 전환...")
            driver.switch_to.frame(iframes[0])
            
            # iframe 내부 콘텐츠 확인
            iframe_title = driver.title
            print(f"   iframe 내부 제목: {iframe_title}")
            
            # iframe 내부의 요소 찾기 시도
            try:
                body_text = driver.find_element(By.TAG_NAME, "body").text[:100]
                print(f"   iframe 내부 텍스트: {body_text}...")
            except Exception as e:
                print(f"   iframe 내부 텍스트 읽기 실패: {e}")
            
            # 메인 콘텐츠로 복귀
            print("\n4. 메인 콘텐츠로 복귀...")
            driver.switch_to.default_content()
            print(f"   메인 페이지 제목: {driver.title}")
        
        print("\n✅ iframe 처리 데모 완료")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
    
    finally:
        # 브라우저 종료 전 대기
        time.sleep(2)
        driver.quit()
        print("\n브라우저 종료")


def demonstrate_naver_finance_iframe():
    """
    Naver Finance의 실제 iframe 처리 예제
    """
    print("\n" + "=" * 60)
    print("Naver Finance iframe 처리 데모")
    print("=" * 60)
    
    # WebDriver 설정
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    
    try:
        # Naver Finance 시장지표 페이지
        url = "https://finance.naver.com/marketindex/"
        print(f"\n1. 페이지 로드: {url}")
        driver.get(url)
        
        # 페이지 로드 대기
        time.sleep(3)
        
        # 페이지 제목 출력
        print(f"   페이지 제목: {driver.title}")
        
        # iframe 찾기 (ID로 찾기)
        print("\n2. iframe 찾기 (id='frame_ex1')...")
        try:
            iframe = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "frame_ex1"))
            )
            print("   ✅ iframe 찾기 성공")
            
            # iframe의 src 속성 확인
            iframe_src = iframe.get_attribute("src")
            print(f"   iframe src: {iframe_src}")
            
            # iframe으로 전환
            print("\n3. iframe으로 전환...")
            driver.switch_to.frame(iframe)
            
            # iframe 내부의 테이블 찾기
            print("\n4. iframe 내부 데이터 확인...")
            
            # 환율고시 날짜 찾기
            try:
                date_element = driver.find_element(
                    By.XPATH, 
                    "//div[@class='exchange_info']/span[1]"
                )
                date = date_element.text
                print(f"   환율고시 날짜: {date}")
            except Exception as e:
                print(f"   날짜 찾기 실패: {e}")
            
            # 테이블 행 찾기
            try:
                rows = driver.find_elements(By.XPATH, "//table/tbody/tr")
                print(f"   테이블 행 개수: {len(rows)}")
                
                if rows:
                    print("\n   처음 3개 환율 정보:")
                    for i, row in enumerate(rows[:3]):
                        try:
                            title = row.find_element(By.XPATH, ".//td[@class='tit']/a").text
                            rate = row.find_element(By.XPATH, ".//td[@class='sale']").text
                            print(f"   - {title}: {rate}")
                        except Exception as e:
                            print(f"   행 {i+1} 처리 실패: {e}")
            except Exception as e:
                print(f"   테이블 찾기 실패: {e}")
            
            # 메인 콘텐츠로 복귀
            print("\n5. 메인 콘텐츠로 복귀...")
            driver.switch_to.default_content()
            print(f"   메인 페이지 제목: {driver.title}")
            
            print("\n✅ Naver Finance iframe 처리 완료")
            
        except Exception as e:
            print(f"   ❌ iframe 찾기 실패: {e}")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
    
    finally:
        # 브라우저 종료 전 대기
        time.sleep(3)
        driver.quit()
        print("\n브라우저 종료")


if __name__ == "__main__":
    print("\n🚀 Selenium iframe 처리 실습\n")
    
    # 기본 iframe 처리 데모
    demonstrate_iframe_handling()
    
    # Naver Finance iframe 처리 데모
    demonstrate_naver_finance_iframe()
    
    print("\n" + "=" * 60)
    print("모든 데모가 완료되었습니다! 🎉")
    print("=" * 60)

