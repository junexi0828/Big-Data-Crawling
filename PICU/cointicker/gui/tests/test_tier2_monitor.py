"""
Tier2Monitor 단위 테스트
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# 프로젝트 루트를 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from gui.monitors import (
    Tier2Monitor,
    get_default_backend_url,
    get_backend_port_from_file,
)


class TestTier2Monitor(unittest.TestCase):
    """Tier2Monitor 테스트 클래스"""

    def setUp(self):
        """테스트 전 설정"""
        self.base_url = "http://localhost:5000"
        self.monitor = Tier2Monitor(base_url=self.base_url)

    @patch("gui.monitors.tier2_monitor.requests.Session")
    def test_check_health_success(self, mock_session_class):
        """헬스 체크 성공 테스트"""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "healthy",
            "database": "connected",
            "timestamp": "2025-01-01T00:00:00",
        }
        mock_response.raise_for_status = Mock()
        mock_session.get.return_value = mock_response

        monitor = Tier2Monitor(base_url=self.base_url)
        result = monitor.check_health()

        self.assertTrue(result.get("success"))
        self.assertTrue(result.get("online"))
        self.assertEqual(result.get("status"), "healthy")

    @patch("gui.monitors.tier2_monitor.requests.Session")
    def test_check_health_failure(self, mock_session_class):
        """헬스 체크 실패 테스트"""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        import requests

        mock_session.get.side_effect = requests.exceptions.ConnectionError(
            "Connection failed"
        )

        monitor = Tier2Monitor(base_url=self.base_url)
        result = monitor.check_health()

        self.assertFalse(result.get("success"))
        self.assertFalse(result.get("online"))
        self.assertIn("error", result)

    @patch("gui.monitors.tier2_monitor.requests.Session")
    def test_get_dashboard_summary_success(self, mock_session_class):
        """대시보드 요약 가져오기 성공 테스트"""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_response = MagicMock()
        mock_response.json.return_value = {"total_items": 100, "total_errors": 5}
        mock_response.raise_for_status = Mock()
        mock_session.get.return_value = mock_response

        monitor = Tier2Monitor(base_url=self.base_url)
        result = monitor.get_dashboard_summary()

        self.assertTrue(result.get("success"))
        self.assertIn("data", result)
        self.assertEqual(result["data"]["total_items"], 100)

    @patch("gui.monitors.tier2_monitor.requests.Session")
    def test_get_dashboard_summary_failure(self, mock_session_class):
        """대시보드 요약 가져오기 실패 테스트"""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        import requests

        mock_session.get.side_effect = requests.exceptions.Timeout("Request timeout")

        monitor = Tier2Monitor(base_url=self.base_url)
        result = monitor.get_dashboard_summary()

        self.assertFalse(result.get("success"))
        self.assertIn("error", result)

    @patch("gui.monitors.tier2_monitor.get_backend_port_from_file")
    def test_get_default_backend_url_with_port_file(self, mock_get_port):
        """포트 파일이 있을 때 기본 URL 테스트"""
        mock_get_port.return_value = 8080
        url = get_default_backend_url()
        self.assertEqual(url, "http://localhost:8080")

    @patch("gui.monitors.tier2_monitor.get_backend_port_from_file")
    def test_get_default_backend_url_without_port_file(self, mock_get_port):
        """포트 파일이 없을 때 기본 URL 테스트"""
        mock_get_port.return_value = None
        url = get_default_backend_url()
        self.assertEqual(url, "http://localhost:5000")

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.read_text")
    def test_get_backend_port_from_file_success(self, mock_read_text, mock_exists):
        """포트 파일 읽기 성공 테스트"""
        mock_exists.return_value = True
        mock_read_text.return_value = "8080"

        port = get_backend_port_from_file()
        self.assertEqual(port, 8080)

    @patch("pathlib.Path.exists")
    def test_get_backend_port_from_file_not_found(self, mock_exists):
        """포트 파일이 없을 때 테스트"""
        mock_exists.return_value = False

        port = get_backend_port_from_file()
        self.assertIsNone(port)

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.read_text")
    def test_get_backend_port_from_file_invalid(self, mock_read_text, mock_exists):
        """포트 파일이 유효하지 않을 때 테스트"""
        mock_exists.return_value = True
        mock_read_text.return_value = "invalid"

        port = get_backend_port_from_file()
        # int 변환 실패 시 None 반환
        self.assertIsNone(port)

    @patch("gui.monitors.tier2_monitor.requests.Session")
    def test_retry_mechanism(self, mock_session_class):
        """재시도 메커니즘 테스트"""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        import requests

        # 첫 번째 시도 실패, 두 번째 시도 성공
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "healthy"}
        mock_response.raise_for_status = Mock()

        mock_session.get.side_effect = [
            requests.exceptions.ConnectionError("Connection failed"),
            mock_response,
        ]

        monitor = Tier2Monitor(base_url=self.base_url)
        result = monitor.check_health()

        # 재시도 후 성공해야 함
        self.assertTrue(result.get("success"))
        self.assertEqual(mock_session.get.call_count, 2)  # 재시도 1회 포함


if __name__ == "__main__":
    unittest.main()
