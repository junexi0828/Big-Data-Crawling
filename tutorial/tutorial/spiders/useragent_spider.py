import scrapy
import random

class UserAgentSpider(scrapy.Spider):
    name = 'useragent_spider'

    # 다양한 User-Agent 목록
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    ]

    def start_requests(self):
        urls = ['http://quotes.toscrape.com']
        for url in urls:
            # 랜덤한 User-Agent 선택
            user_agent = random.choice(self.user_agents)
            yield scrapy.Request(
                url=url,
                headers={'User-Agent': user_agent},
                callback=self.parse,
                meta={'user_agent': user_agent}
            )

    def parse(self, response):
        used_ua = response.meta.get('user_agent', 'Unknown')
        self.logger.info(f"사용된 User-Agent: {used_ua}")

        for quote in response.css('div.quote'):
            yield {
                'text': quote.css('span.text::text').get(),
                'author': quote.css('small.author::text').get(),
                'user_agent_used': used_ua,
            }