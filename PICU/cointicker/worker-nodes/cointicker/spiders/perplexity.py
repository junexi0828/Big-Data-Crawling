"""
Perplexity Finance Spider
Perplexity AI 기반 금융 요약 및 시장 분석 수집
"""

import scrapy
from datetime import datetime
from cointicker.items import CryptoNewsItem


class PerplexitySpider(scrapy.Spider):
    name = "perplexity"
    allowed_domains = ["perplexity.ai", "www.perplexity.ai"]

    start_urls = [
        "https://www.perplexity.ai/search?q=cryptocurrency+market+analysis",
        "https://www.perplexity.ai/search?q=bitcoin+ethereum+market+trends",
    ]

    custom_settings = {
        "DOWNLOAD_DELAY": 5,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    }

    def parse(self, response):
        """메인 파싱 메서드"""
        self.logger.info(f"Parsing: {response.url}")

        # Perplexity는 주로 JavaScript로 렌더링되므로
        # API를 사용하거나 Selenium이 필요할 수 있음
        # 여기서는 기본적인 HTML 파싱 시도

        # 요약 내용 추출
        summaries = response.css('.summary, .answer, .content, article p::text').getall()

        if summaries:
            # 첫 번째 요약을 아이템으로 생성
            content = ' '.join([s.strip() for s in summaries if s.strip()])

            item = CryptoNewsItem()
            item['source'] = 'perplexity'
            item['title'] = f"Perplexity AI Analysis - {datetime.now().strftime('%Y-%m-%d')}"
            item['url'] = response.url
            item['content'] = content[:5000]  # 최대 5000자
            item['published_at'] = datetime.now().isoformat()
            item['keywords'] = ['AI Analysis', 'Market Trends', 'Cryptocurrency']
            item['timestamp'] = datetime.now().isoformat()

            yield item

        # 검색 결과 링크 추출
        links = response.css('a[href*="search"]::attr(href)').getall()
        for link in links[:5]:  # 최대 5개만
            if link.startswith('/'):
                link = response.urljoin(link)
            yield scrapy.Request(link, callback=self.parse)

