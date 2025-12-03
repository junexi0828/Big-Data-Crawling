"""
백엔드 API 테스트
"""

import unittest
import sys
from pathlib import Path

# 통합 경로 설정 유틸리티 사용
try:
    from shared.path_utils import setup_pythonpath
    setup_pythonpath()
except ImportError:
    # Fallback: 유틸리티 로드 실패 시 하드코딩 경로 사용
    sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))


class TestModels(unittest.TestCase):
    """데이터베이스 모델 테스트"""

    def test_raw_news_model(self):
        """RawNews 모델 테스트"""
        import sys
        from pathlib import Path

        sys.path.insert(0, str(Path(__file__).parent.parent))
        try:
            from backend.models import RawNews
        except ImportError:
            self.skipTest("sqlalchemy not installed")
        from datetime import datetime

        now = datetime.now()
        news = RawNews(
            source="coinness",
            title="Test News",
            url="https://example.com/news",
            published_at=now,
            collected_at=now,
        )

        self.assertEqual(news.source, "coinness")
        self.assertEqual(news.title, "Test News")
        self.assertIsNotNone(news.collected_at)

    def test_market_trends_model(self):
        """MarketTrends 모델 테스트"""
        import sys
        from pathlib import Path

        sys.path.insert(0, str(Path(__file__).parent.parent))
        try:
            from backend.models import MarketTrends
        except ImportError:
            self.skipTest("sqlalchemy not installed")
        from datetime import datetime

        trend = MarketTrends(
            source="upbit",
            symbol="BTC",
            price=50000,
            volume_24h=1000000,
            change_24h=3.5,
            timestamp=datetime.now(),
        )

        self.assertEqual(trend.symbol, "BTC")
        self.assertEqual(trend.price, 50000)
        self.assertEqual(trend.change_24h, 3.5)


class TestServices(unittest.TestCase):
    """서비스 레이어 테스트"""

    def test_sentiment_analyzer_mock(self):
        """감성 분석기 Mock 테스트"""
        import sys
        from pathlib import Path

        sys.path.insert(0, str(Path(__file__).parent.parent))
        try:
            from backend.services.sentiment_analyzer import SentimentAnalyzer
        except ImportError:
            self.skipTest("sqlalchemy not installed")
        from unittest.mock import Mock

        # Mock DB 세션
        mock_db = Mock()
        analyzer = SentimentAnalyzer(mock_db)

        # 모델이 없을 때 Mock 분석
        result = analyzer.analyze_news(1, "Test text")
        self.assertIn("sentiment_score", result)
        self.assertIn("sentiment_label", result)

    def test_technical_indicators(self):
        """기술적 지표 계산 테스트"""
        import sys
        from pathlib import Path

        sys.path.insert(0, str(Path(__file__).parent.parent))
        try:
            from backend.services.technical_indicators import (
                TechnicalIndicatorsCalculator,
            )
        except ImportError:
            self.skipTest("sqlalchemy not installed")
        from unittest.mock import Mock

        mock_db = Mock()
        calc = TechnicalIndicatorsCalculator(mock_db)

        # RSI 계산 테스트
        prices = [
            100,
            102,
            101,
            103,
            105,
            104,
            106,
            108,
            107,
            109,
            110,
            112,
            111,
            113,
            115,
        ]
        rsi = calc.calculate_rsi(prices)

        self.assertGreaterEqual(rsi, 0)
        self.assertLessEqual(rsi, 100)


if __name__ == "__main__":
    unittest.main()
