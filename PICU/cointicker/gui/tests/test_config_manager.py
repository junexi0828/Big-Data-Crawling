"""
ConfigManager 단위 테스트
"""

import unittest
from unittest.mock import Mock, patch, mock_open
import sys
import tempfile
import shutil
from pathlib import Path

# 프로젝트 루트를 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from gui.core.config_manager import ConfigManager


class TestConfigManager(unittest.TestCase):
    """ConfigManager 테스트 클래스"""

    def setUp(self):
        """테스트 전 설정"""
        # 임시 디렉토리 생성
        self.temp_dir = tempfile.mkdtemp()
        self.manager = ConfigManager(config_dir=self.temp_dir)

    def tearDown(self):
        """테스트 후 정리"""
        # 임시 디렉토리 삭제
        shutil.rmtree(self.temp_dir)

    def test_load_config_yaml(self):
        """YAML 설정 파일 로드 테스트"""
        config_file = Path(self.temp_dir) / "test_config.yaml"
        config_file.write_text("key: value\nnested:\n  subkey: subvalue\n")

        config = self.manager.load_config("test")
        # test는 기본 config_files에 없으므로 None 반환
        self.assertIsNone(config)

    def test_load_config_gui(self):
        """GUI 설정 로드 테스트"""
        config_file = Path(self.temp_dir) / "gui_config.yaml"
        config_file.write_text("window:\n  width: 1400\n  height: 900\n")

        config = self.manager.load_config("gui")
        self.assertIsNotNone(config)
        self.assertEqual(config.get("window", {}).get("width"), 1400)

    def test_save_config(self):
        """설정 저장 테스트"""
        config_data = {"window": {"width": 1400, "height": 900}}
        result = self.manager.save_config("gui", config_data)
        self.assertTrue(result)

        # 저장된 파일 확인
        config_file = Path(self.temp_dir) / "gui_config.yaml"
        self.assertTrue(config_file.exists())

    def test_get_config(self):
        """설정 값 가져오기 테스트"""
        config_file = Path(self.temp_dir) / "gui_config.yaml"
        config_file.write_text("window:\n  width: 1400\n  height: 900\n")

        width = self.manager.get_config("gui", "window.width")
        self.assertEqual(width, 1400)

    def test_get_config_default(self):
        """기본값으로 설정 가져오기 테스트"""
        value = self.manager.get_config(
            "gui", "nonexistent.key", default="default_value"
        )
        self.assertEqual(value, "default_value")

    def test_set_config(self):
        """설정 값 설정 테스트"""
        config_file = Path(self.temp_dir) / "gui_config.yaml"
        config_file.write_text("window:\n  width: 1400\n")

        self.manager.set_config("gui", "window.height", 900)
        height = self.manager.get_config("gui", "window.height")
        self.assertEqual(height, 900)

    def test_create_default_configs(self):
        """기본 설정 생성 테스트"""
        self.manager.create_default_configs()

        # GUI 설정 파일 확인
        gui_config = self.manager.load_config("gui")
        self.assertIsNotNone(gui_config)
        self.assertIn("window", gui_config)

    def test_validate_config_cluster(self):
        """클러스터 설정 유효성 검사 테스트"""
        # 유효한 설정
        config_file = Path(self.temp_dir) / "cluster_config.yaml"
        config_file.write_text(
            "cluster:\n  master:\n    ip: 192.168.1.1\n  workers: []\n"
        )
        self.manager.configs.clear()  # 캐시 초기화

        valid, errors = self.manager.validate_config("cluster")
        self.assertTrue(valid)
        self.assertEqual(len(errors), 0)

    def test_validate_config_invalid(self):
        """유효하지 않은 설정 검사 테스트"""
        # 마스터 IP가 없는 설정
        config_file = Path(self.temp_dir) / "cluster_config.yaml"
        config_file.write_text("cluster:\n  master: {}\n")
        self.manager.configs.clear()  # 캐시 초기화

        valid, errors = self.manager.validate_config("cluster")
        self.assertFalse(valid)
        self.assertGreater(len(errors), 0)

    def test_config_caching(self):
        """설정 캐싱 테스트"""
        config_file = Path(self.temp_dir) / "gui_config.yaml"
        config_file.write_text("window:\n  width: 1400\n")

        # 첫 번째 로드
        config1 = self.manager.load_config("gui")

        # 파일 수정
        config_file.write_text("window:\n  width: 1600\n")

        # 두 번째 로드 (캐시에서 가져옴)
        config2 = self.manager.load_config("gui")

        # 캐시 때문에 동일한 값이어야 함 (TTL 내)
        self.assertEqual(
            config1.get("window", {}).get("width"),
            config2.get("window", {}).get("width"),
        )

    def test_config_cache_invalidation(self):
        """설정 캐시 무효화 테스트"""
        config_file = Path(self.temp_dir) / "gui_config.yaml"
        config_file.write_text("window:\n  width: 1400\n")

        # 설정 로드
        self.manager.load_config("gui")

        # 설정 변경 (캐시 무효화됨)
        self.manager.set_config("gui", "window.width", 1600)

        # 새 값 확인
        width = self.manager.get_config("gui", "window.width")
        self.assertEqual(width, 1600)


if __name__ == "__main__":
    unittest.main()
