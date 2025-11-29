"""
ModuleManager 단위 테스트
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# 프로젝트 루트를 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from gui.core.module_manager import ModuleManager, ModuleInterface


class TestModule(ModuleInterface):
    """테스트용 모듈 클래스"""

    def initialize(self, config: dict) -> bool:
        """모듈 초기화"""
        self.status = "initialized"
        return True

    def start(self) -> bool:
        """모듈 시작"""
        self.status = "running"
        return True

    def stop(self) -> bool:
        """모듈 중지"""
        self.status = "stopped"
        return True

    def execute(self, command: str, params: dict = None) -> dict:
        """명령어 실행"""
        return {"success": True, "command": command, "params": params or {}}


class TestModuleManager(unittest.TestCase):
    """ModuleManager 테스트 클래스"""

    def setUp(self):
        """테스트 전 설정"""
        self.manager = ModuleManager()

    def test_register_module(self):
        """모듈 등록 테스트"""
        self.manager.register_module(TestModule)
        self.assertIn("TestModule", self.manager.modules)
        self.assertEqual(self.manager.modules["TestModule"].name, "TestModule")

    def test_register_module_with_config(self):
        """설정과 함께 모듈 등록 테스트"""
        config = {"key": "value"}
        self.manager.register_module(TestModule, config=config)
        module = self.manager.modules["TestModule"]
        self.assertEqual(module.config, config)

    def test_register_module_with_custom_name(self):
        """커스텀 이름으로 모듈 등록 테스트"""
        self.manager.register_module(TestModule, module_name="CustomModule")
        self.assertIn("CustomModule", self.manager.modules)
        self.assertNotIn("TestModule", self.manager.modules)

    def test_get_module(self):
        """모듈 가져오기 테스트"""
        self.manager.register_module(TestModule)
        # ModuleManager에는 get_module 메서드가 없으므로 modules 딕셔너리에서 직접 가져옴
        module = self.manager.modules.get("TestModule")
        self.assertIsNotNone(module)
        self.assertIsInstance(module, TestModule)

    def test_get_module_not_found(self):
        """존재하지 않는 모듈 가져오기 테스트"""
        # ModuleManager에는 get_module 메서드가 없으므로 modules 딕셔너리에서 직접 가져옴
        module = self.manager.modules.get("NonExistent")
        self.assertIsNone(module)

    def test_get_all_modules_status(self):
        """모든 모듈 상태 조회 테스트"""
        self.manager.register_module(TestModule)
        statuses = self.manager.get_all_modules_status()
        self.assertEqual(len(statuses), 1)
        self.assertEqual(statuses[0]["name"], "TestModule")

    def test_get_module_status(self):
        """특정 모듈 상태 조회 테스트"""
        self.manager.register_module(TestModule)
        status = self.manager.get_module_status("TestModule")
        self.assertIsNotNone(status)
        self.assertEqual(status["name"], "TestModule")

    def test_execute_command(self):
        """명령어 실행 테스트"""
        self.manager.register_module(TestModule)
        result = self.manager.execute_command(
            "TestModule", "test_command", {"param": "value"}
        )
        self.assertTrue(result.get("success"))
        self.assertEqual(result.get("command"), "test_command")

    def test_execute_command_module_not_found(self):
        """존재하지 않는 모듈에 명령어 실행 테스트"""
        result = self.manager.execute_command("NonExistent", "test_command")
        self.assertFalse(result.get("success"))
        self.assertIn("error", result)

    def test_module_initialization(self):
        """모듈 초기화 테스트"""
        self.manager.register_module(TestModule)
        # ModuleManager에는 get_module 메서드가 없으므로 modules 딕셔너리에서 직접 가져옴
        module = self.manager.modules.get("TestModule")
        config = {"test": "config"}
        result = module.initialize(config)
        self.assertTrue(result)
        self.assertEqual(module.status, "initialized")

    def test_module_start_stop(self):
        """모듈 시작/중지 테스트"""
        self.manager.register_module(TestModule)
        # ModuleManager에는 get_module 메서드가 없으므로 modules 딕셔너리에서 직접 가져옴
        module = self.manager.modules.get("TestModule")
        module.initialize({})

        # 시작
        result = module.start()
        self.assertTrue(result)
        self.assertEqual(module.status, "running")

        # 중지
        result = module.stop()
        self.assertTrue(result)
        self.assertEqual(module.status, "stopped")

    def test_cache_invalidation(self):
        """모듈 상태 캐시 무효화 테스트"""
        self.manager.register_module(TestModule)

        # 첫 번째 조회 (캐시 생성)
        status1 = self.manager.get_all_modules_status()

        # 캐시 무효화
        self.manager.invalidate_module_cache()

        # 두 번째 조회 (새로 조회)
        status2 = self.manager.get_all_modules_status()

        # 결과는 동일해야 함
        self.assertEqual(len(status1), len(status2))


if __name__ == "__main__":
    unittest.main()
