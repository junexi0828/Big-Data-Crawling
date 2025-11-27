"""
Coinness News Spider
코인니스 암호화폐 뉴스 수집
"""

import scrapy
from datetime import datetime
from cointicker.items import CryptoNewsItem


class CoinnessSpider(scrapy.Spider):
    name = "coinness"
    allowed_domains = ["coinness.com", "www.coinness.com"]

    start_urls = [
        "https://www.coinness.com/news",
        "https://www.coinness.com/news/list",
    ]

    custom_settings = {
        "DOWNLOAD_DELAY": 3,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
    }

    def parse(self, response):
        """메인 파싱 메서드"""
        self.logger.info(f"Parsing: {response.url}")

        # 뉴스 목록 추출
        news_items = response.css('.news-item, .article-item, .list-item')

        if not news_items:
            # 다른 셀렉터 시도
            news_items = response.css('article, .news, .post')

        for item in news_items:
            title = item.css('a::text, .title::text, h2::text, h3::text').get()
            url = item.css('a::attr(href)').get()

            if not title or not url:
                continue

            # 상대 URL을 절대 URL로 변환
            if url.startswith('/'):
                url = response.urljoin(url)

            # 발행 시간 추출
            published_at = item.css('.date::text, .time::text, time::attr(datetime)').get()
            if not published_at:
                published_at = datetime.now().isoformat()

            # 키워드 추출
            keywords = item.css('.tag::text, .keyword::text').getall()

            yield scrapy.Request(
                url,
                callback=self.parse_article,
                meta={
                    'title': title.strip(),
                    'published_at': published_at,
                    'keywords': keywords
                }
            )

        # 다음 페이지 링크
        next_page = response.css('a.next::attr(href), .pagination a:contains("다음")::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        """기사 상세 페이지 파싱"""
        try:
            item = CryptoNewsItem()
            item['source'] = 'coinness'
            item['title'] = response.meta.get('title', '')

            # 제목이 없으면 페이지에서 추출
            if not item['title']:
                item['title'] = response.css('h1::text, .article-title::text, title::text').get()

            item['url'] = response.url
            item['published_at'] = response.meta.get('published_at', datetime.now().isoformat())
            item['keywords'] = response.meta.get('keywords', [])

            # 본문 추출
            content = response.css('.article-content, .content, .post-content, article p::text').getall()
            if content:
                item['content'] = ' '.join([c.strip() for c in content if c.strip()])

            item['timestamp'] = datetime.now().isoformat()

            self.logger.debug(f"Scraped article: {item['title'][:50]}")
            yield item

        except Exception as e:
            self.logger.error(f"Error parsing article {response.url}: {e}")

