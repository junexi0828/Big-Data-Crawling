"""
Scrapy와 Selenium 통합 예제

이 예제는 Selenium을 Scrapy의 Downloader Middleware로 통합하는 방법을 보여줍니다.
슬라이드의 "Modify ExchangeRateDownloaderMiddleware" 내용을 구현합니다.
"""

import scrapy
from scrapy import signals
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time


class SeleniumDownloaderMiddleware:
    """
    Selenium을 사용하여 동적 콘텐츠를 로드하는 Downloader Middleware
    """
    
    def __init__(self):
        """미들웨어 초기화"""
        self.driver = None
    
    @classmethod
    def from_crawler(cls, crawler):
        """
        Scrapy 크롤러에서 미들웨어 인스턴스 생성
        
        Args:
            crawler: Scrapy Crawler 인스턴스
            
        Returns:
            SeleniumDownloaderMiddleware: 미들웨어 인스턴스
        """
        middleware = cls()
        crawler.signals.connect(middleware.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(middleware.spider_closed, signal=signals.spider_closed)
        return middleware
    
    def spider_opened(self, spider):
        """
        스파이더 시작 시 WebDriver 초기화
        
        Args:
            spider: Scrapy Spider 인스턴스
        """
        spider.logger.info("🚀 Selenium WebDriver 초기화 중...")
        
        chrome_options = Options()
        
        # 헤드리스 모드 (선택사항)
        # chrome_options.add_argument('--headless')
        
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(10)
        
        spider.logger.info("✅ Selenium WebDriver 초기화 완료")
    
    def spider_closed(self, spider):
        """
        스파이더 종료 시 WebDriver 정리
        
        Args:
            spider: Scrapy Spider 인스턴스
        """
        if self.driver:
            self.driver.quit()
            spider.logger.info("✅ Selenium WebDriver 종료")
    
    def process_request(self, request, spider):
        """
        요청 처리: Selenium으로 페이지 로드
        
        Args:
            request: Scrapy Request 객체
            spider: Scrapy Spider 인스턴스
            
        Returns:
            HtmlResponse: Selenium으로 로드한 페이지의 응답
        """
        spider.logger.info(f"🌐 Selenium으로 페이지 로드: {request.url}")
        
        # Selenium으로 페이지 로드
        self.driver.get(request.url)
        
        # 페이지 로드 대기
        time.sleep(2)
        
        # 페이지 소스 가져오기
        body = self.driver.page_source
        
        # HtmlResponse 객체 생성하여 반환
        return HtmlResponse(
            url=request.url,
            body=body,
            encoding='utf-8',
            request=request
        )


class NaverExchangeSpider(scrapy.Spider):
    """
    Selenium Middleware를 사용하는 Naver Finance 스파이더
    """
    
    name = 'n_exchange_with_middleware'
    allowed_domains = ['finance.naver.com']
    start_urls = ['https://finance.naver.com/marketindex/']
    
    custom_settings = {
        # Selenium Middleware 활성화
        'DOWNLOADER_MIDDLEWARES': {
            '__main__.SeleniumDownloaderMiddleware': 543,
        },
        # ROBOTSTXT_OBEY 설정
        'ROBOTSTXT_OBEY': False,
        # UTF-8 인코딩 설정
        'FEED_EXPORT_ENCODING': 'utf-8',
    }
    
    def parse(self, response):
        """
        메인 페이지 파싱
        
        Args:
            response: Scrapy Response 객체
            
        Yields:
            dict: 환율 정보
        """
        self.logger.info(f"{'='*60}")
        self.logger.info(f"[parse] 시작: {response.url}")
        self.logger.info(f"{'='*60}")
        
        # 환율고시 날짜 추출
        date = response.xpath("//div[@class='exchange_info']/span[1]/text()").get()
        self.logger.info(f"[parse] 환율고시 날짜: {date}")
        
        # iframe URL 추출
        iframe_url = response.xpath('//iframe[@id="frame_ex1"]/@src').get()
        
        # 상대 URL인 경우 절대 URL로 변환
        if iframe_url and not iframe_url.startswith("http"):
            iframe_url = "https://finance.naver.com" + iframe_url
        
        self.logger.info(f"[parse] iframe URL: {iframe_url}")
        
        # iframe 페이지로 요청 전송 (meta로 날짜 전달)
        if iframe_url:
            yield scrapy.Request(
                url=iframe_url,
                callback=self.parse_iframe,
                meta={'date': date}
            )
    
    def parse_iframe(self, response):
        """
        iframe 내부 데이터 파싱
        
        Args:
            response: Scrapy Response 객체
            
        Yields:
            dict: 환율 정보
        """
        self.logger.info(f"{'='*60}")
        self.logger.info("[parse_iframe] 시작")
        self.logger.info(f"{'='*60}")
        
        # meta에서 날짜 정보 가져오기
        date = response.meta['date']
        
        # 테이블 행 추출
        rows = response.xpath("//html/body/div/table/tbody/tr")
        
        self.logger.info(f"[parse_iframe] 찾은 테이블 행 개수: {len(rows)}")
        
        # 각 행에서 데이터 추출
        item = {"date": date}
        
        for i, row in enumerate(rows):
            # 국가/통화명 추출
            title = row.xpath(".//td[@class='tit']/a/text()").get()
            
            # 환율 (매매기준율) 추출
            rate = row.xpath(".//td[@class='sale']/text()").get()
            
            if title and rate:
                title = title.strip()
                rate = rate.strip()
                item[title] = rate
                self.logger.info(f"  {i+1}. {title}: {rate}")
        
        self.logger.info(f"✅ [parse_iframe] 완료: {len(item)-1}개 환율 정보 수집")
        
        yield item


def run_spider():
    """
    스파이더를 프로그래밍 방식으로 실행
    """
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings
    
    print("\n" + "=" * 60)
    print("🚀 Selenium Middleware를 사용한 Naver Finance 스크래핑")
    print("=" * 60)
    
    # Scrapy 설정
    settings = {
        'DOWNLOADER_MIDDLEWARES': {
            '__main__.SeleniumDownloaderMiddleware': 543,
        },
        'ROBOTSTXT_OBEY': False,
        'FEED_EXPORT_ENCODING': 'utf-8',
        'FEEDS': {
            'outputs/json/exchange_rates_middleware.json': {
                'format': 'json',
                'encoding': 'utf-8',
                'overwrite': True,
            }
        }
    }
    
    # CrawlerProcess 생성 및 실행
    process = CrawlerProcess(settings)
    process.crawl(NaverExchangeSpider)
    process.start()


if __name__ == "__main__":
    # 스파이더 실행
    run_spider()

