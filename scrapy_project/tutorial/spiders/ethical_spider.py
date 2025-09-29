import scrapy

class EthicalSpider(scrapy.Spider):
    name = 'ethical_crawler'

    # 윤리적 크롤링 설정
    custom_settings = {
        'ROBOTSTXT_OBEY': True,
        'USER_AGENT': 'MyCompany-EthicalCrawler (contact@mycompany.com)',
        'DOWNLOAD_DELAY': 3.0,
        'RANDOMIZE_DOWNLOAD_DELAY': True,  # [0.5*3 ~ 1.5*3] 초 사이
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 60,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,
        'HTTPCACHE_ENABLED': True,
    }

    start_urls = ['http://quotes.toscrape.com']

    def parse(self, response):
        self.logger.info(f"윤리적으로 크롤링 중: {response.url}")

        # robots.txt 확인
        if hasattr(response, 'meta') and response.meta.get('download_timeout'):
            self.logger.warning("요청 시간 초과 - 서버 부하를 고려하여 대기")

        for quote in response.css('div.quote'):
            yield {
                'text': quote.css('span.text::text').get(),
                'author': quote.css('small.author::text').get(),
                'tags': quote.css('div.tags a.tag::text').getall(),
            }

        # 다음 페이지로 이동 (신중하게)
        next_page = response.css('li.next a::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)