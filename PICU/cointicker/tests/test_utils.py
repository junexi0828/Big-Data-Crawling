"""
유틸리티 함수 테스트
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
    sys.path.insert(0, str(Path(__file__).parent.parent / "shared"))


class TestUtils(unittest.TestCase):
    """유틸리티 함수 테스트"""

    def test_generate_hash(self):
        """해시 생성 테스트"""
        from shared.utils import generate_hash

        hash1 = generate_hash("test")
        hash2 = generate_hash("test")
        hash3 = generate_hash("different")

        # 같은 입력은 같은 해시
        self.assertEqual(hash1, hash2)
        # 다른 입력은 다른 해시
        self.assertNotEqual(hash1, hash3)
        # 해시 길이 확인 (MD5는 32자)
        self.assertEqual(len(hash1), 32)

    def test_get_timestamp(self):
        """타임스탬프 생성 테스트"""
        from shared.utils import get_timestamp

        timestamp = get_timestamp()
        self.assertIsInstance(timestamp, str)
        self.assertEqual(len(timestamp), 15)  # YYYYMMDD_HHMMSS 형식

    def test_clean_text(self):
        """텍스트 정제 테스트"""
        from shared.utils import clean_text

        # 공백 정리
        self.assertEqual(clean_text("  test   text  "), "test text")
        # 빈 문자열
        self.assertEqual(clean_text(""), "")
        self.assertEqual(clean_text(None), "")

    def test_validate_json(self):
        """JSON 유효성 검사 테스트"""
        from shared.utils import validate_json

        # 유효한 딕셔너리
        self.assertTrue(validate_json({"key": "value"}))
        # 순환 참조가 있는 경우 (실패해야 함)
        # self.assertFalse(validate_json(...))  # 복잡한 케이스는 생략


if __name__ == "__main__":
    unittest.main()
