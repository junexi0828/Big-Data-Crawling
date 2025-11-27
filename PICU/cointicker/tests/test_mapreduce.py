"""
MapReduce 작업 테스트
"""

import unittest
import sys
import json
import io
from pathlib import Path

# 프로젝트 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent / "worker-nodes" / "mapreduce"))


class TestMapper(unittest.TestCase):
    """Mapper 테스트"""

    def test_mapper_processing(self):
        """Mapper 데이터 처리 테스트"""
        from cleaner_mapper import clean_data

        # 유효한 데이터
        data = {
            "source": "upbit",
            "symbol": "BTC",
            "price": 50000,
            "timestamp": "2025-11-27T10:00:00"
        }

        cleaned = clean_data(data)
        self.assertIsNotNone(cleaned)
        self.assertEqual(cleaned["source"], "upbit")
        self.assertIn("_hash", cleaned)

    def test_mapper_invalid_data(self):
        """무효한 데이터 필터링 테스트"""
        from cleaner_mapper import clean_data

        # 필수 필드 없는 데이터
        invalid_data = {"price": 50000}  # source, timestamp 없음
        cleaned = clean_data(invalid_data)
        self.assertIsNone(cleaned)


class TestReducer(unittest.TestCase):
    """Reducer 테스트"""

    def test_remove_duplicates(self):
        """중복 제거 테스트"""
        from cleaner_reducer import remove_duplicates

        data_list = [
            {"_hash": "abc123", "source": "upbit", "symbol": "BTC"},
            {"_hash": "abc123", "source": "upbit", "symbol": "BTC"},  # 중복
            {"_hash": "def456", "source": "upbit", "symbol": "ETH"},
        ]

        unique = remove_duplicates(data_list)
        self.assertEqual(len(unique), 2)  # 중복 제거 후 2개


if __name__ == "__main__":
    unittest.main()

