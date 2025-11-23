"""
Naver Finance 환율 정보 스크래핑 스파이더
강의 슬라이드의 n_exchange.py 구현

Selenium Downloader Middleware를 사용하여 동적 콘텐츠를 수집합니다.
response.meta['driver']와 response.meta['driver_response']를 사용합니다.
"""

import scrapy


class NExchangeSpider(scrapy.Spider):
    name = 'n_exchange'
    allowed_domains = ['finance.naver.com']
    start_urls = ['http://finance.naver.com/marketindex/']

    def parse(self, response):
        """
        메인 페이지 파싱
        response.meta['driver']와 response.meta['driver_response'] 사용
        """
        # response.meta['driver'] 확인
        if 'driver' in response.meta:
            driver = response.meta['driver']
            user_agent = driver.execute_script("return navigator.userAgent;")
            print(f"User-Agent: {user_agent}")

        # response.meta['driver_response'] 확인
        if 'driver_response' in response.meta:
            driver_response = response.meta['driver_response']
            print(f"Driver Response Text (first 500 chars): {driver_response.text[:500]}")

        # 환율고시 날짜 추출
        date = response.xpath("//div[@class='exchange_info']/span[1]/text()").get()
        print(f"[parse] date: {date}")

        # driver가 있으면 iframe 처리
        if 'driver' in response.meta:
            from selenium.webdriver.common.by import By
            driver = response.meta['driver']
            driver.switch_to.frame('frame_ex1')

            # iframe 내부 테이블 행 추출
            rows = driver.find_elements(By.XPATH, "/html/body/div/table/tbody/tr")

            for row in rows:
                try:
                    title = row.find_element(By.XPATH, ".//td[@class='tit']/a").text
                    rate_text = row.find_element(By.XPATH, ".//td[@class='sale']").text
                    rate = float(rate_text.replace(',', ''))

                    item = {
                        'date': date,
                        'title': title,
                        'rate': rate
                    }
                    yield item
                except Exception as e:
                    self.logger.warning(f"Error extracting row data: {e}")
                    continue

