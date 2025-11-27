"""
CNN Fear & Greed Index Spider
CNN 공포·탐욕 지수 수집
"""

import scrapy
import json
import re
from datetime import datetime
from cointicker.items import FearGreedItem


class CNNFearGreedSpider(scrapy.Spider):
    name = "cnn_fear_greed"
    allowed_domains = ["edition.cnn.com", "alternative.me"]

    # CNN Fear & Greed Index는 alternative.me에서 제공
    start_urls = [
        "https://alternative.me/crypto/fear-and-greed-index/",
        "https://api.alternative.me/fng/",
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
            yield from self.parse_webpage(response)

    def parse_api(self, response):
        """API 응답 파싱"""
        try:
            data = json.loads(response.text)

            if 'data' in data and len(data['data']) > 0:
                latest = data['data'][0]

                item = FearGreedItem()
                item['source'] = 'cnn_fear_greed'
                item['value'] = int(latest.get('value', 0))
                item['classification'] = self._get_classification(item['value'])
                item['timestamp'] = datetime.now().isoformat()

                yield item

        except json.JSONDecodeError:
            self.logger.error(f"Failed to parse JSON from {response.url}")
        except Exception as e:
            self.logger.error(f"Error parsing API: {e}")

    def parse_webpage(self, response):
        """웹페이지 파싱"""
        try:
            # 지수 값 추출
            value_text = response.css('.fng-value::text, .fng-circle::text, [class*="value"]::text').get()

            if not value_text:
                # JavaScript에서 값 추출 시도
                scripts = response.css('script::text').getall()
                for script in scripts:
                    match = re.search(r'value["\']?\s*[:=]\s*(\d+)', script)
                    if match:
                        value_text = match.group(1)
                        break

            if value_text:
                value = int(re.search(r'\d+', value_text).group())

                item = FearGreedItem()
                item['source'] = 'cnn_fear_greed'
                item['value'] = value
                item['classification'] = self._get_classification(value)
                item['timestamp'] = datetime.now().isoformat()

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

