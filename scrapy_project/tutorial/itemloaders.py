"""
ItemLoader 클래스와 전처리 함수들 정의
"""

from itemloaders import ItemLoader
from itemloaders.processors import MapCompose, TakeFirst, Join
import re
from datetime import datetime


def remove_mark(text):
    """유니코드 따옴표 제거 함수 - 이미지의 \u201c, \u201d 처리"""
    if text:
        # strip the unicode quotation marks (이미지에서 강조된 부분)
        return text.strip("\u201c").strip("\u201d").strip('"').strip("'")
    return text


def convert_date(text):
    """날짜 형식 변환 함수 - 이미지의 str → date format"""
    if text:
        try:
            # "March 14, 1879" 형식을 Python date로 변환 (이미지 예시)
            return datetime.strptime(text.strip(), "%B %d, %Y").strftime("%Y-%m-%d")
        except ValueError:
            return text.strip()
    return text


def parse_location(text):
    """출생지 정보 파싱 함수 - 이미지의 remove unnecessary string 'in'"""
    if text:
        # "in Ulm, Germany" -> "Ulm, Germany" (이미지 예시)
        # simply remove 'in ' from the author's birthplace string
        return text.strip()[3:] if text.strip().startswith("in ") else text.strip()
    return text


def clean_text(text):
    """텍스트 정리 함수"""
    if text:
        # 여러 공백을 하나로 정리
        text = re.sub(r"\s+", " ", text.strip())
        return text
    return text


class QuotesItemLoader(ItemLoader):
    """명언 데이터를 위한 ItemLoader"""

    # 기본 전처리 - 모든 필드에 적용
    default_input_processor = MapCompose(str.strip)
    default_output_processor = TakeFirst()

    # 명언 텍스트 전처리
    quote_content_in = MapCompose(remove_mark, clean_text)
    quote_content_out = TakeFirst()

    # 태그 처리 - 리스트로 유지
    tags_in = MapCompose(str.strip)

    def tags_out(self, values):
        """태그 리스트를 그대로 반환"""
        return values

    # 작가명 처리
    author_name_in = MapCompose(clean_text)
    author_name_out = TakeFirst()

    # 생년월일 처리
    birthdate_in = MapCompose(convert_date)
    birthdate_out = TakeFirst()

    # 출생지 처리
    birthplace_in = MapCompose(parse_location)
    birthplace_out = TakeFirst()

    # 전기 처리
    bio_in = MapCompose(clean_text)
    bio_out = TakeFirst()


class AuthorItemLoader(ItemLoader):
    """작가 정보를 위한 ItemLoader"""

    default_input_processor = MapCompose(str.strip)
    default_output_processor = TakeFirst()

    # 이름 처리
    name_in = MapCompose(clean_text)
    name_out = TakeFirst()

    # 생년월일 처리
    birthdate_in = MapCompose(convert_date)
    birthdate_out = TakeFirst()

    # 출생지 처리
    birthplace_in = MapCompose(parse_location)
    birthplace_out = TakeFirst()

    # 전기 처리
    bio_in = MapCompose(clean_text)
    bio_out = TakeFirst()
