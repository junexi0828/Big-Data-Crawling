"""
Spider 테스트
"""

import unittest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# 프로젝트 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent / "worker-nodes"))


class TestUpbitTrendsSpider(unittest.TestCase):
    """Upbit Trends Spider 테스트"""

    def setUp(self):
        """테스트 설정"""
        import sys
        from pathlib import Path

        sys.path.insert(0, str(Path(__file__).parent.parent / "worker-nodes"))
        try:
            from cointicker.spiders.upbit_trends import UpbitTrendsSpider

            self.spider = UpbitTrendsSpider()
        except ImportError as e:
            self.skipTest(f"scrapy not installed: {e}")

    def test_spider_name(self):
        """Spider 이름 확인"""
        self.assertEqual(self.spider.name, "upbit_trends")

    def test_allowed_domains(self):
        """허용된 도메인 확인"""
        self.assertIn("upbit.com", self.spider.allowed_domains)

    def test_create_trend_item(self):
        """트렌드 아이템 생성 테스트"""
        ticker_data = {
            "market": "KRW-BTC",
            "trade_price": 50000,
            "acc_trade_volume_24h": 1000,
            "prev_closing_price": 48000,
        }

        items = list(self.spider._create_trend_item(ticker_data))
        self.assertEqual(len(items), 1)

        item = items[0]
        self.assertEqual(item["source"], "upbit")
        self.assertEqual(item["symbol"], "BTC")
        self.assertEqual(item["price"], 50000)


class TestCoinnessSpider(unittest.TestCase):
    """Coinness Spider 테스트"""

    def setUp(self):
        """테스트 설정"""
        import sys
        from pathlib import Path

        sys.path.insert(0, str(Path(__file__).parent.parent / "worker-nodes"))
        try:
            from cointicker.spiders.coinness import CoinnessSpider

            self.spider = CoinnessSpider()
        except ImportError as e:
            self.skipTest(f"scrapy not installed: {e}")

    def test_spider_name(self):
        """Spider 이름 확인"""
        self.assertEqual(self.spider.name, "coinness")


if __name__ == "__main__":
    unittest.main()
