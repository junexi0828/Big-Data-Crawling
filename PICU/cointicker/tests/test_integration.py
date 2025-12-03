"""
통합 테스트
전체 파이프라인 통합 테스트
"""

import unittest
import sys
import json
from pathlib import Path
from unittest.mock import Mock, patch

# 통합 경로 설정 유틸리티 사용
try:
    from shared.path_utils import setup_pythonpath
    setup_pythonpath()
except ImportError:
    # Fallback: 유틸리티 로드 실패 시 하드코딩 경로 사용
    sys.path.insert(0, str(Path(__file__).parent.parent))


class TestDataPipeline(unittest.TestCase):
    """데이터 파이프라인 통합 테스트"""

    def test_spider_to_item(self):
        """Spider → Item 파이프라인 테스트"""
        import sys
        from pathlib import Path

        sys.path.insert(0, str(Path(__file__).parent.parent / "worker-nodes"))
        from cointicker.items import MarketTrendItem
        from datetime import datetime

        item = MarketTrendItem()
        item["source"] = "upbit"
        item["symbol"] = "BTC"
        item["price"] = 50000
        item["timestamp"] = datetime.now().isoformat()

        self.assertEqual(item["source"], "upbit")
        self.assertEqual(item["symbol"], "BTC")
        self.assertIsNotNone(item["timestamp"])

    def test_item_to_json(self):
        """Item → JSON 변환 테스트"""
        import sys
        from pathlib import Path

        sys.path.insert(0, str(Path(__file__).parent.parent / "worker-nodes"))
        from cointicker.items import MarketTrendItem

        try:
            from itemadapter import ItemAdapter
        except ImportError:
            # itemadapter가 없으면 스킵
            self.skipTest("itemadapter not installed")
        from datetime import datetime

        item = MarketTrendItem()
        item["source"] = "upbit"
        item["symbol"] = "BTC"
        item["price"] = 50000
        item["timestamp"] = datetime.now().isoformat()

        adapter = ItemAdapter(item)
        item_dict = dict(adapter)

        # JSON 직렬화 가능한지 확인
        json_str = json.dumps(item_dict)
        self.assertIsInstance(json_str, str)

        # 역직렬화 확인
        parsed = json.loads(json_str)
        self.assertEqual(parsed["source"], "upbit")


class TestBackendIntegration(unittest.TestCase):
    """백엔드 통합 테스트"""

    def test_database_models(self):
        """데이터베이스 모델 통합 테스트"""
        import sys
        from pathlib import Path

        sys.path.insert(0, str(Path(__file__).parent.parent))
        try:
            from backend.models import Base
        except ImportError:
            self.skipTest("sqlalchemy not installed")

        # 테이블 목록 확인
        tables = list(Base.metadata.tables.keys())
        expected_tables = [
            "raw_news",
            "sentiment_analysis",
            "market_trends",
            "technical_indicators",
            "fear_greed_index",
            "crypto_insights",
        ]

        for table in expected_tables:
            self.assertIn(table, tables)


if __name__ == "__main__":
    unittest.main()
