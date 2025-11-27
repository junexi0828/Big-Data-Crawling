"""
ItemLoader 정의
데이터 정제 및 변환을 자동화
"""

from itemloaders import ItemLoader
from itemloaders.processors import MapCompose, TakeFirst, Join, Compose
from cointicker.items import (
    CryptoNewsItem,
    MarketTrendItem,
    UpbitTrendItem,
    FearGreedItem,
)
import re
from datetime import datetime


def clean_text(text):
    """텍스트 정제"""
    if not text:
        return ""
    if isinstance(text, list):
        text = " ".join(text)
    # 공백 정리
    text = re.sub(r"\s+", " ", str(text).strip())
    # 특수 문자 제거 (필요시)
    # text = re.sub(r'[^\w\s가-힣.,!?]', '', text)
    return text


def parse_datetime(date_str):
    """날짜 문자열 파싱"""
    if not date_str:
        return None

    if isinstance(date_str, datetime):
        return date_str.isoformat()

    # ISO 형식인 경우
    if isinstance(date_str, str):
        try:
            # ISO 형식 파싱 시도
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            return dt.isoformat()
        except:
            pass

    return date_str


def extract_keywords(keywords):
    """키워드를 리스트로 변환"""
    if not keywords:
        return []

    if isinstance(keywords, list):
        # 리스트인 경우 정제
        return [clean_text(k) for k in keywords if k and clean_text(k)]

    if isinstance(keywords, str):
        # 문자열인 경우 분리
        # 쉼표, 세미콜론, 공백으로 분리
        keywords_list = re.split(r"[,;]\s*|\s+", keywords)
        return [clean_text(k) for k in keywords_list if k and clean_text(k)]

    return []


def validate_title(title):
    """제목 검증 및 정제"""
    if not title:
        return None

    title = clean_text(title)

    # 최소 길이 체크
    if len(title) < 3:
        return None

    # 최대 길이 제한
    if len(title) > 500:
        title = title[:500]

    return title


def validate_content(content):
    """본문 검증 및 정제"""
    if not content:
        return None

    content = clean_text(content)

    # 최소 길이 체크
    if len(content) < 10:
        return None

    # 최대 길이 제한
    if len(content) > 50000:
        content = content[:50000]

    return content


def validate_url(url):
    """URL 검증"""
    if not url:
        return None

    url = str(url).strip()

    # 기본 URL 검증
    if not url.startswith(("http://", "https://")):
        return None

    return url


class CryptoNewsItemLoader(ItemLoader):
    """암호화폐 뉴스 ItemLoader"""

    default_item_class = CryptoNewsItem
    default_input_processor = MapCompose(str.strip)
    default_output_processor = TakeFirst()

    # 필드별 프로세서
    source_in = MapCompose(str.strip, str.lower)
    title_in = MapCompose(str.strip, clean_text, validate_title)
    url_in = MapCompose(str.strip, validate_url)
    content_in = MapCompose(str.strip, clean_text, validate_content)
    published_at_in = MapCompose(str.strip, parse_datetime)

    # 키워드 처리: 리스트는 그대로, 문자열은 extract_keywords로 변환
    def keywords_in(self, value):
        """키워드 입력 처리"""
        if isinstance(value, list):
            # 리스트인 경우 그대로 반환
            return value
        # 문자열인 경우 extract_keywords로 변환
        return extract_keywords(value)

    def keywords_out(self, values):
        """키워드 출력 처리 - 모든 값을 합쳐서 리스트로 반환"""
        if not values:
            return []

        result = []
        for v in values:
            if isinstance(v, list):
                result.extend(v)
            elif v:
                result.append(v)

        # 중복 제거 및 정제
        cleaned = [clean_text(str(k)) for k in result if k]
        unique = list(set(cleaned))
        return unique if unique else []

    timestamp_in = MapCompose(str.strip, parse_datetime)


class MarketTrendItemLoader(ItemLoader):
    """시장 트렌드 ItemLoader"""

    default_item_class = MarketTrendItem
    default_input_processor = MapCompose(str.strip)
    default_output_processor = TakeFirst()

    source_in = MapCompose(str.strip, str.lower)
    symbol_in = MapCompose(str.strip, str.upper)
    price_in = MapCompose(str.strip, lambda x: float(x.replace(",", "")) if x else None)
    volume_24h_in = MapCompose(
        str.strip, lambda x: float(x.replace(",", "")) if x else None
    )
    change_24h_in = MapCompose(
        str.strip, lambda x: float(x.replace(",", "").replace("%", "")) if x else None
    )
    market_cap_in = MapCompose(
        str.strip, lambda x: float(x.replace(",", "")) if x else None
    )
    timestamp_in = MapCompose(str.strip, parse_datetime)


class UpbitTrendItemLoader(ItemLoader):
    """Upbit 트렌드 ItemLoader"""

    default_item_class = UpbitTrendItem
    default_input_processor = MapCompose(str.strip)
    default_output_processor = TakeFirst()

    source_in = MapCompose(str.strip, str.lower)
    trending_searches_out = Compose(
        TakeFirst(), lambda v: v if isinstance(v, list) else []
    )
    top_volume_out = Compose(TakeFirst(), lambda v: v if isinstance(v, list) else [])
    timestamp_in = MapCompose(str.strip, parse_datetime)


class FearGreedItemLoader(ItemLoader):
    """공포·탐욕 지수 ItemLoader"""

    default_item_class = FearGreedItem
    default_input_processor = MapCompose(str.strip)
    default_output_processor = TakeFirst()

    source_in = MapCompose(str.strip, str.lower)
    value_in = MapCompose(str.strip, lambda x: int(x) if x and x.isdigit() else None)
    classification_in = MapCompose(str.strip, str.title)
    timestamp_in = MapCompose(str.strip, parse_datetime)
