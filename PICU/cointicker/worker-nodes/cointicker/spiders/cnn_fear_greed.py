"""
CNN Fear & Greed Index Spider
CNN 공포·탐욕 지수 수집
"""

import scrapy
import json
import re
from datetime import datetime
from cointicker.items import FearGreedItem
from cointicker.itemloaders import FearGreedItemLoader


class CNNFearGreedSpider(scrapy.Spider):
    name = "cnn_fear_greed"
    allowed_domains = ["edition.cnn.com", "alternative.me"]

    # CNN Fear & Greed Index는 alternative.me에서 제공
    # API를 우선 사용 (더 안정적)
    start_urls = [
        "https://api.alternative.me/fng/",  # API 우선
    ]

    custom_settings = {
        "DOWNLOAD_DELAY": 3,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
    }

    def parse(self, response):
        """메인 파싱 메서드"""
        self.logger.info(f"Parsing: {response.url}")

        if "api.alternative.me" in response.url:
            yield from self.parse_api(response)
        else:
            # API 실패 시 웹페이지 파싱 시도
            yield from self.parse_webpage(response)

    def parse_api(self, response):
        """API 응답 파싱"""
        try:
            data = json.loads(response.text)

            # API 응답 형식 확인
            if (
                "data" in data
                and isinstance(data["data"], list)
                and len(data["data"]) > 0
            ):
                latest = data["data"][0]

                if isinstance(latest, dict):
                    value = latest.get("value")
                    if value is not None:
                        try:
                            value = int(value)
                            classification = self._get_classification(value)

                            # ItemLoader 사용
                            loader = FearGreedItemLoader(item=FearGreedItem())
                            loader.add_value("source", "cnn_fear_greed")
                            loader.add_value("value", value)
                            loader.add_value("classification", classification)
                            loader.add_value("timestamp", datetime.now().isoformat())

                            item = loader.load_item()

                            self.logger.info(
                                f"Fear & Greed Index 수집: {value} ({item.get('classification', '')})"
                            )
                            yield item
                        except (ValueError, TypeError) as e:
                            self.logger.error(f"값 변환 오류: {value} - {e}")
                    else:
                        self.logger.warning("API 응답에 value 필드가 없습니다")
                else:
                    self.logger.warning(f"예상하지 못한 데이터 형식: {type(latest)}")
            else:
                self.logger.warning(f"API 응답에 데이터가 없습니다: {response.url}")
                # API 실패 시 웹페이지 파싱 시도
                yield scrapy.Request(
                    "https://alternative.me/crypto/fear-and-greed-index/",
                    callback=self.parse_webpage,
                    dont_filter=True,
                )

        except json.JSONDecodeError as e:
            self.logger.error(f"JSON 파싱 오류 {response.url}: {e}")
            # JSON 파싱 실패 시 웹페이지 파싱 시도
            yield scrapy.Request(
                "https://alternative.me/crypto/fear-and-greed-index/",
                callback=self.parse_webpage,
                dont_filter=True,
            )
        except Exception as e:
            self.logger.error(f"API 파싱 오류 {response.url}: {e}")

    def parse_webpage(self, response):
        """웹페이지 파싱"""
        try:
            # 지수 값 추출
            value_text = response.css(
                '.fng-value::text, .fng-circle::text, [class*="value"]::text'
            ).get()

            if not value_text:
                # JavaScript에서 값 추출 시도
                scripts = response.css("script::text").getall()
                for script in scripts:
                    match = re.search(r'value["\']?\s*[:=]\s*(\d+)', script)
                    if match:
                        value_text = match.group(1)
                        break

            if value_text:
                match = re.search(r"\d+", value_text)
                if match:
                    value = int(match.group())
                else:
                    self.logger.warning(f"값을 추출할 수 없습니다: {value_text}")
                    return

                classification = self._get_classification(value)

                # ItemLoader 사용
                loader = FearGreedItemLoader(item=FearGreedItem())
                loader.add_value("source", "cnn_fear_greed")
                loader.add_value("value", value)
                loader.add_value("classification", classification)
                loader.add_value("timestamp", datetime.now().isoformat())

                item = loader.load_item()
                yield item

        except Exception as e:
            self.logger.error(f"Error parsing webpage: {e}")

    def _get_classification(self, value):
        """값에 따른 분류 반환"""
        if value <= 25:
            return "Extreme Fear"
        elif value <= 45:
            return "Fear"
        elif value <= 55:
            return "Neutral"
        elif value <= 75:
            return "Greed"
        else:
            return "Extreme Greed"
