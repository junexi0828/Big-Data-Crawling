"""
모듈 매니저
모든 시스템 모듈을 통합 관리하는 핵심 컴포넌트
"""

import importlib
import inspect
from typing import Dict, List, Type, Any, Optional
from pathlib import Path
import json

from shared.logger import setup_logger

logger = setup_logger(__name__)


class ModuleInterface:
    """모듈 인터페이스"""

    def __init__(self, name: str):
        self.name = name
        self.status = "inactive"
        self.config = {}
        self.dependencies = []

    def initialize(self, config: dict) -> bool:
        """모듈 초기화"""
        raise NotImplementedError

    def start(self) -> bool:
        """모듈 시작"""
        raise NotImplementedError

    def stop(self) -> bool:
        """모듈 중지"""
        raise NotImplementedError

    def get_status(self) -> dict:
        """모듈 상태 조회"""
        return {
            "name": self.name,
            "status": self.status,
            "config": self.config
        }

    def execute(self, command: str, params: dict = None) -> dict:
        """명령어 실행"""
        raise NotImplementedError


class ModuleManager:
    """모듈 매니저 클래스"""

    def __init__(self):
        """초기화"""
        self.modules: Dict[str, ModuleInterface] = {}
        self.module_configs: Dict[str, dict] = {}
        self.module_paths: Dict[str, str] = {}

    def register_module(self, module_class: Type[ModuleInterface], config: dict = None):
        """
        모듈 등록

        Args:
            module_class: 모듈 클래스
            config: 모듈 설정
        """
        instance = module_class(module_class.__name__)
        if config:
            instance.config = config
            self.module_configs[instance.name] = config

        self.modules[instance.name] = instance
        logger.info(f"모듈 등록: {instance.name}")

    def load_module_from_path(self, module_path: str, class_name: str, config: dict = None):
        """
        경로에서 모듈 로드

        Args:
            module_path: 모듈 경로 (예: "worker-nodes.cointicker.spiders.upbit_trends")
            class_name: 클래스 이름
            config: 모듈 설정
        """
        try:
            module = importlib.import_module(module_path)
            module_class = getattr(module, class_name)

            if inspect.isclass(module_class) and issubclass(module_class, ModuleInterface):
                self.register_module(module_class, config)
            else:
                logger.warning(f"유효하지 않은 모듈 클래스: {module_path}.{class_name}")
        except Exception as e:
            logger.error(f"모듈 로드 실패 {module_path}: {e}")

    def initialize_module(self, module_name: str, config: dict = None) -> bool:
        """
        모듈 초기화

        Args:
            module_name: 모듈 이름
            config: 모듈 설정

        Returns:
            초기화 성공 여부
        """
        if module_name not in self.modules:
            logger.error(f"모듈을 찾을 수 없습니다: {module_name}")
            return False

        module = self.modules[module_name]

        # 설정 병합
        if config:
            module.config.update(config)
        elif module_name in self.module_configs:
            module.config.update(self.module_configs[module_name])

        try:
            success = module.initialize(module.config)
            if success:
                module.status = "initialized"
                logger.info(f"모듈 초기화 완료: {module_name}")
            else:
                module.status = "error"
                logger.error(f"모듈 초기화 실패: {module_name}")
            return success
        except Exception as e:
            module.status = "error"
            logger.error(f"모듈 초기화 오류 {module_name}: {e}")
            return False

    def start_module(self, module_name: str) -> bool:
        """
        모듈 시작

        Args:
            module_name: 모듈 이름

        Returns:
            시작 성공 여부
        """
        if module_name not in self.modules:
            logger.error(f"모듈을 찾을 수 없습니다: {module_name}")
            return False

        module = self.modules[module_name]

        # 의존성 확인
        for dep in module.dependencies:
            if dep not in self.modules:
                logger.error(f"의존성 모듈을 찾을 수 없습니다: {dep}")
                return False
            dep_module = self.modules[dep]
            if dep_module.status != "running":
                logger.warning(f"의존성 모듈이 실행 중이 아닙니다: {dep}")

        try:
            success = module.start()
            if success:
                module.status = "running"
                logger.info(f"모듈 시작 완료: {module_name}")
            else:
                module.status = "error"
                logger.error(f"모듈 시작 실패: {module_name}")
            return success
        except Exception as e:
            module.status = "error"
            logger.error(f"모듈 시작 오류 {module_name}: {e}")
            return False

    def stop_module(self, module_name: str) -> bool:
        """
        모듈 중지

        Args:
            module_name: 모듈 이름

        Returns:
            중지 성공 여부
        """
        if module_name not in self.modules:
            logger.error(f"모듈을 찾을 수 없습니다: {module_name}")
            return False

        module = self.modules[module_name]

        try:
            success = module.stop()
            if success:
                module.status = "stopped"
                logger.info(f"모듈 중지 완료: {module_name}")
            else:
                logger.error(f"모듈 중지 실패: {module_name}")
            return success
        except Exception as e:
            logger.error(f"모듈 중지 오류 {module_name}: {e}")
            return False

    def execute_command(self, module_name: str, command: str, params: dict = None) -> dict:
        """
        모듈 명령어 실행

        Args:
            module_name: 모듈 이름
            command: 명령어
            params: 파라미터

        Returns:
            실행 결과
        """
        if module_name not in self.modules:
            return {"success": False, "error": f"모듈을 찾을 수 없습니다: {module_name}"}

        module = self.modules[module_name]

        if module.status != "running":
            return {"success": False, "error": f"모듈이 실행 중이 아닙니다: {module_name}"}

        try:
            return module.execute(command, params or {})
        except Exception as e:
            logger.error(f"명령어 실행 오류 {module_name}.{command}: {e}")
            return {"success": False, "error": str(e)}

    def get_all_modules_status(self) -> List[dict]:
        """모든 모듈 상태 조회"""
        return [module.get_status() for module in self.modules.values()]

    def get_module_status(self, module_name: str) -> Optional[dict]:
        """특정 모듈 상태 조회"""
        if module_name in self.modules:
            return self.modules[module_name].get_status()
        return None

    def load_module_mapping(self, mapping_file: str):
        """
        모듈 매핑 파일 로드

        Args:
            mapping_file: 매핑 파일 경로 (JSON)
        """
        try:
            with open(mapping_file, 'r', encoding='utf-8') as f:
                mappings = json.load(f)

            for mapping in mappings:
                module_path = mapping.get('path')
                class_name = mapping.get('class')
                config = mapping.get('config', {})

                self.load_module_from_path(module_path, class_name, config)
                logger.info(f"모듈 매핑 로드: {module_path}.{class_name}")
        except Exception as e:
            logger.error(f"모듈 매핑 로드 실패: {e}")

    def save_module_mapping(self, mapping_file: str):
        """
        모듈 매핑 파일 저장

        Args:
            mapping_file: 매핑 파일 경로
        """
        mappings = []
        for name, module in self.modules.items():
            mappings.append({
                "name": name,
                "path": self.module_paths.get(name, ""),
                "config": module.config
            })

        try:
            with open(mapping_file, 'w', encoding='utf-8') as f:
                json.dump(mappings, f, indent=2, ensure_ascii=False)
            logger.info(f"모듈 매핑 저장: {mapping_file}")
        except Exception as e:
            logger.error(f"모듈 매핑 저장 실패: {e}")

