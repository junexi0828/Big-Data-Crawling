"""
Naver Finance 환율 정보 스크래핑

슬라이드에 제시된 Naver Finance의 환율고시 정보를 스크래핑하는 스파이더입니다.
iframe 내부의 동적 콘텐츠를 Selenium을 사용하여 수집합니다.

Target URL: https://finance.naver.com/marketindex/
Data Source: https://finance.naver.com/marketindex/exchangeList.nhn (iframe 내부)
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import json
import time
from datetime import datetime


class NaverExchangeSpider:
    """
    Naver Finance 환율 정보 스크래핑 클래스
    """
    
    def __init__(self, headless=False):
        """
        초기화
        
        Args:
            headless (bool): 헤드리스 모드 사용 여부
        """
        self.name = "n_exchange"
        self.start_url = "https://finance.naver.com/marketindex/"
        self.headless = headless
        self.driver = None
        
    def setup_driver(self):
        """WebDriver 설정"""
        import os
        
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless')
        
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # ROBOTSTXT_OBEY=False와 유사한 설정
        chrome_options.add_argument(
            'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        # ChromeDriver 경로 직접 지정
        chromedriver_path = os.path.expanduser(
            "~/.wdm/drivers/chromedriver/mac64/141.0.7390.78/chromedriver-mac-arm64/chromedriver"
        )
        
        # 경로가 없으면 webdriver-manager 사용
        if not os.path.exists(chromedriver_path):
            service = Service(ChromeDriverManager().install())
        else:
            service = Service(chromedriver_path)
        
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(10)
        
        print("✅ WebDriver 설정 완료")
    
    def parse(self):
        """
        메인 페이지 파싱
        
        1. 시장지표 페이지 접속
        2. 환율고시 날짜 추출
        3. iframe URL 추출
        4. iframe 내부 데이터 스크래핑을 위한 요청 생성
        """
        print(f"\n{'='*60}")
        print(f"[parse] 시작: {self.start_url}")
        print(f"{'='*60}")
        
        self.driver.get(self.start_url)
        time.sleep(2)  # 페이지 로드 대기
        
        try:
            # 1. 환율고시 날짜 추출
            date_xpath = "//div[@class='exchange_info']/span[1]"
            date_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, date_xpath))
            )
            date = date_element.text
            print(f"\n[parse] 환율고시 날짜: {date}")
            
            # 2. iframe URL 추출
            iframe = self.driver.find_element(By.XPATH, '//iframe[@id="frame_ex1"]')
            iframe_url = iframe.get_attribute("src")
            
            # 상대 URL인 경우 절대 URL로 변환
            if not iframe_url.startswith("http"):
                iframe_url = "https://finance.naver.com" + iframe_url
            
            print(f"[parse] iframe URL: {iframe_url}")
            
            # 3. iframe 내부 데이터 스크래핑
            result = self.parse_iframe(date)
            
            return result
            
        except Exception as e:
            print(f"\n❌ [parse] 오류 발생: {e}")
            return None
    
    def parse_iframe(self, date):
        """
        iframe 내부 데이터 파싱
        
        Args:
            date (str): 환율고시 날짜
            
        Returns:
            dict: 수집된 환율 정보
        """
        print(f"\n{'='*60}")
        print("[parse_iframe] 시작")
        print(f"{'='*60}")
        
        try:
            # iframe으로 전환
            iframe = self.driver.find_element(By.ID, "frame_ex1")
            self.driver.switch_to.frame(iframe)
            
            # meta 데이터로 전달된 날짜 정보 사용
            item = {"date": date}
            
            print(f"\n[parse_iframe] 환율고시 날짜: {date}")
            
            # 테이블 행 추출
            rows_xpath = "//html/body/div/table/tbody/tr"
            rows = self.driver.find_elements(By.XPATH, rows_xpath)
            
            print(f"[parse_iframe] 찾은 테이블 행 개수: {len(rows)}")
            
            # 각 행에서 데이터 추출
            for i, row in enumerate(rows):
                try:
                    # 국가/통화명 추출
                    title = row.find_element(
                        By.XPATH, 
                        ".//td[@class='tit']/a"
                    ).text.strip()
                    
                    # 환율 (매매기준율) 추출
                    rate = row.find_element(
                        By.XPATH, 
                        ".//td[@class='sale']"
                    ).text.strip()
                    
                    # 딕셔너리에 추가
                    item[title] = rate
                    
                    print(f"  {i+1}. {title}: {rate}")
                    
                except Exception as e:
                    print(f"  ⚠️  행 {i+1} 처리 중 오류: {e}")
                    continue
            
            # 메인 콘텐츠로 복귀
            self.driver.switch_to.default_content()
            
            print(f"\n✅ [parse_iframe] 완료: {len(item)-1}개 환율 정보 수집")
            
            return item
            
        except Exception as e:
            print(f"\n❌ [parse_iframe] 오류 발생: {e}")
            # 오류 발생 시에도 메인 콘텐츠로 복귀
            self.driver.switch_to.default_content()
            return None
    
    def save_to_json(self, data, filename=None):
        """
        데이터를 JSON 파일로 저장
        
        Args:
            data (dict): 저장할 데이터
            filename (str): 파일명 (기본값: exchange_rates.json)
        """
        if not data:
            print("\n⚠️  저장할 데이터가 없습니다.")
            return
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"outputs/json/exchange_rates_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"\n✅ 데이터 저장 완료: {filename}")
            
        except Exception as e:
            print(f"\n❌ 파일 저장 실패: {e}")
    
    def run(self):
        """스파이더 실행"""
        print("\n" + "=" * 60)
        print("🚀 Naver Finance 환율 정보 스크래핑 시작")
        print("=" * 60)
        
        try:
            # WebDriver 설정
            self.setup_driver()
            
            # 데이터 스크래핑
            result = self.parse()
            
            if result:
                # 결과 출력
                print("\n" + "=" * 60)
                print("📊 수집된 데이터")
                print("=" * 60)
                print(json.dumps(result, ensure_ascii=False, indent=2))
                
                # JSON 파일로 저장
                self.save_to_json(result, "outputs/json/exchange_rates.json")
            
            print("\n" + "=" * 60)
            print("✅ 스크래핑 완료!")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ 스크래핑 실패: {e}")
            
        finally:
            if self.driver:
                self.driver.quit()
                print("\n브라우저 종료")


def main():
    """메인 함수"""
    # 스파이더 생성 및 실행
    spider = NaverExchangeSpider(headless=False)
    spider.run()


if __name__ == "__main__":
    main()

