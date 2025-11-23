# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class TutorialSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    async def process_start(self, start):
        # Called with an async iterator over the spider start() method or the
        # maching method of an earlier spider middleware.
        async for item_or_request in start:
            yield item_or_request

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class TutorialDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


# ==============================================================================
# 강의 슬라이드: ExchangeRateDownloaderMiddleware
# ==============================================================================


class ExchangeRateDownloaderMiddleware:
    """
    Downloader Middleware 예제
    강의 슬라이드에 따라 process_request, process_response, process_exception에 print() 추가
    """

    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        """
        Called for each request that goes through the downloader middleware.
        Must either:
        - return None: continue processing this request
        - or return a Response object
        - or return a Request object
        - or raise IgnoreRequest: process_exception() methods of installed downloader middleware will be called
        """
        print(
            "===ExchangeRateDownloaderMiddleware.process_request({}): return None.".format(
                request.url
            )
        )
        return None

    def process_response(self, request, response, spider):
        """
        Called with the response returned from the downloader.
        Must either;
        - return a Response object
        - return a Request object
        - or raise IgnoreRequest
        """
        print(
            "===ExchangeRateDownloaderMiddleware.process_response({}): return response.".format(
                response.url
            )
        )
        return response

    def process_exception(self, request, exception, spider):
        """
        Called when a download handler or a process_request()
        (from other downloader middleware) raises an exception.
        Must either:
        - return None: continue processing this exception
        - return a Response object: stops process_exception() chain
        - return a Request object: stops process_exception() chain
        """
        print(
            "===ExchangeRateDownloaderMiddleware.process_exception({}): pass.".format(
                exception
            )
        )
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


# ==============================================================================
# 강의 슬라이드: ExchangeRate2DownloaderMiddleware
# ==============================================================================


class ExchangeRate2DownloaderMiddleware:
    """
    Downloader Middleware 예제 2
    ExchangeRateDownloaderMiddleware를 복사한 버전
    """

    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        """
        Called for each request that goes through the downloader middleware.
        Must either:
        - return None: continue processing this request
        - or return a Response object
        - or return a Request object
        - or raise IgnoreRequest: process_exception() methods of installed downloader middleware will be called
        """
        print(
            "===ExchangeRate2DownloaderMiddleware.process_request({}): return None.".format(
                request.url
            )
        )
        return None

    def process_response(self, request, response, spider):
        """
        Called with the response returned from the downloader.
        Must either;
        - return a Response object
        - return a Request object
        - or raise IgnoreRequest
        """
        print(
            "===ExchangeRate2DownloaderMiddleware.process_response({}): return response.".format(
                response.url
            )
        )
        return response

    def process_exception(self, request, exception, spider):
        """
        Called when a download handler or a process_request()
        (from other downloader middleware) raises an exception.
        Must either:
        - return None: continue processing this exception
        - return a Response object: stops process_exception() chain
        - return a Request object: stops process_exception() chain
        """
        print(
            "===ExchangeRate2DownloaderMiddleware.process_exception({}): pass.".format(
                exception
            )
        )
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


# ==============================================================================
# 강의 슬라이드: Selenium Downloader Middleware
# ==============================================================================

from scrapy.http import HtmlResponse
from selenium import webdriver


class SeleniumExchangeRateDownloaderMiddleware:
    """
    Selenium을 사용하는 Downloader Middleware
    강의 슬라이드의 "Modify ExchangeRateDownloaderMiddleware" 내용 구현
    """

    def __init__(self):
        self.driver = None

    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(s.spider_closed, signal=signals.spider_closed)
        return s

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36"
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        options.add_argument("lang=ko_KR")
        options.add_argument('user-agent="{}"'.format(user_agent))
        self.driver = webdriver.Chrome(options=options)

    def spider_closed(self, spider):
        if self.driver:
            self.driver.quit()

    def process_request(self, request, spider):
        """
        Selenium으로 페이지를 로드하고 HtmlResponse를 반환
        request.meta에 driver와 driver_response를 저장
        """
        self.driver.get(request.url)
        request.meta["driver"] = self.driver
        body = str.encode(self.driver.page_source)
        request.meta["driver_response"] = HtmlResponse(
            self.driver.current_url, body=body, encoding="utf-8", request=request
        )
        return None

    def process_response(self, request, response, spider):
        return response

    def process_exception(self, request, exception, spider):
        pass
