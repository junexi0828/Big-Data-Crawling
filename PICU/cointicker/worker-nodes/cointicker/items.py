"""
Scrapy Items 정의
"""
import scrapy
from itemadapter import ItemAdapter


class CryptoNewsItem(scrapy.Item):
    """암호화폐 뉴스 아이템"""
    source = scrapy.Field()  # 데이터 소스 (upbit, coinness 등)
    title = scrapy.Field()  # 제목
    url = scrapy.Field()  # URL
    content = scrapy.Field()  # 본문 (선택)
    published_at = scrapy.Field()  # 발행 시간
    keywords = scrapy.Field()  # 키워드 리스트
    timestamp = scrapy.Field()  # 수집 시간


class MarketTrendItem(scrapy.Item):
    """시장 트렌드 아이템"""
    source = scrapy.Field()  # 데이터 소스
    symbol = scrapy.Field()  # 코인 심볼 (BTC, ETH 등)
    price = scrapy.Field()  # 가격
    volume_24h = scrapy.Field()  # 24시간 거래량
    change_24h = scrapy.Field()  # 24시간 변동률
    market_cap = scrapy.Field()  # 시가총액 (선택)
    timestamp = scrapy.Field()  # 수집 시간


class UpbitTrendItem(scrapy.Item):
    """Upbit 트렌드 아이템"""
    source = scrapy.Field()
    trending_searches = scrapy.Field()  # 인기 검색어 리스트
    top_volume = scrapy.Field()  # 거래량 급증 코인 리스트
    timestamp = scrapy.Field()


class FearGreedItem(scrapy.Item):
    """공포·탐욕 지수 아이템"""
    source = scrapy.Field()
    value = scrapy.Field()  # 0-100 값
    classification = scrapy.Field()  # Extreme Fear, Fear, Neutral, Greed, Extreme Greed
    timestamp = scrapy.Field()

