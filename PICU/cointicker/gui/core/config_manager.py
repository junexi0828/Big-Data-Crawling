"""
설정 관리자
애플리케이션 설정을 중앙에서 관리
"""

import yaml
import json
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from shared.logger import setup_logger

logger = setup_logger(__name__)


class ConfigManager:
    """설정 관리자 클래스"""

    def __init__(self, config_dir: str = None):
        """
        초기화

        Args:
            config_dir: 설정 디렉토리 경로 (None이면 자동 탐지)
        """
        if config_dir is None:
            # 프로젝트 루트에서 cointicker/config 찾기
            current_file = Path(__file__)
            # gui/core/config_manager.py -> cointicker/config
            project_root = current_file.parent.parent.parent
            config_dir = project_root / "config"
        else:
            config_dir = Path(config_dir)

        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.configs: Dict[str, dict] = {}
        self.config_files = {
            "cluster": "cluster_config.yaml",
            "database": "database_config.yaml",
            "spider": "spider_config.yaml",
            "gui": "gui_config.yaml",
        }

    def load_config(self, config_name: str) -> Optional[dict]:
        """
        설정 파일 로드

        Args:
            config_name: 설정 이름 (cluster, database, spider, gui)

        Returns:
            설정 딕셔너리 또는 None
        """
        if config_name in self.configs:
            return self.configs[config_name]

        if config_name not in self.config_files:
            logger.error(f"알 수 없는 설정 이름: {config_name}")
            return None

        config_file = self.config_dir / self.config_files[config_name]

        # 예제 파일이 있으면 사용
        if not config_file.exists():
            example_file = self.config_dir / (
                self.config_files[config_name] + ".example"
            )
            if example_file.exists():
                logger.warning(
                    f"설정 파일이 없어 예제 파일을 사용합니다: {config_file}"
                )
                config_file = example_file
            else:
                logger.error(f"설정 파일을 찾을 수 없습니다: {config_file}")
                return None

        try:
            with open(config_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    logger.warning(f"설정 파일이 비어있습니다: {config_file}")
                    return {}

                if config_file.suffix == ".yaml" or config_file.suffix == ".yml":
                    config = yaml.safe_load(content)
                else:
                    config = json.loads(content)

            self.configs[config_name] = config or {}
            logger.info(f"설정 로드 완료: {config_name}")
            return self.configs[config_name]
        except yaml.YAMLError as e:
            logger.error(f"YAML 파싱 오류 {config_name}: {e}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 오류 {config_name}: {e}")
            return {}
        except Exception as e:
            logger.error(f"설정 로드 실패 {config_name}: {e}")
            return {}

    def save_config(self, config_name: str, config: dict):
        """
        설정 파일 저장

        Args:
            config_name: 설정 이름
            config: 설정 딕셔너리
        """
        if config_name not in self.config_files:
            logger.error(f"알 수 없는 설정 이름: {config_name}")
            return False

        config_file = self.config_dir / self.config_files[config_name]

        try:
            with open(config_file, "w", encoding="utf-8") as f:
                if config_file.suffix == ".yaml" or config_file.suffix == ".yml":
                    yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
                else:
                    json.dump(config, f, indent=2, ensure_ascii=False)

            self.configs[config_name] = config
            logger.info(f"설정 저장 완료: {config_name}")
            return True
        except Exception as e:
            logger.error(f"설정 저장 실패 {config_name}: {e}")
            return False

    def get_config(self, config_name: str, key: str = None, default: Any = None) -> Any:
        """
        설정 값 가져오기

        Args:
            config_name: 설정 이름
            key: 설정 키 (점으로 구분된 경로, 예: "cluster.master.ip")
            default: 기본값

        Returns:
            설정 값
        """
        config = self.load_config(config_name)
        if config is None:
            return default

        if key is None:
            return config

        # 점으로 구분된 키 경로 처리
        keys = key.split(".")
        value = config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set_config(self, config_name: str, key: str, value: Any):
        """
        설정 값 설정

        Args:
            config_name: 설정 이름
            key: 설정 키 (점으로 구분된 경로)
            value: 설정 값
        """
        config = self.load_config(config_name)
        if config is None:
            config = {}

        # 점으로 구분된 키 경로 처리
        keys = key.split(".")
        current = config

        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]

        current[keys[-1]] = value
        self.save_config(config_name, config)

    def create_default_configs(self):
        """기본 설정 파일 생성 (예제 파일에서 복사)"""
        # GUI 설정은 기본값으로 생성
        default_configs = {
            "gui": {
                "window": {"width": 1400, "height": 900, "theme": "default"},
                "refresh": {"auto_refresh": False, "interval": 30},
                "tier2": {"base_url": "http://localhost:5000", "timeout": 5},
                "cluster": {"ssh_timeout": 10, "retry_count": 3},
            }
        }

        # GUI 설정 생성
        for config_name, config_data in default_configs.items():
            config_file = self.config_dir / self.config_files[config_name]
            if not config_file.exists():
                self.save_config(config_name, config_data)
                logger.info(f"기본 설정 생성: {config_name}")

        # 다른 설정 파일들은 예제 파일에서 복사
        configs_to_copy = ["cluster", "database", "spider"]
        for config_name in configs_to_copy:
            config_file = self.config_dir / self.config_files[config_name]
            example_file = self.config_dir / (
                self.config_files[config_name] + ".example"
            )

            # 실제 설정 파일이 없고 예제 파일이 있으면 복사
            if not config_file.exists() and example_file.exists():
                try:
                    shutil.copy2(example_file, config_file)
                    logger.info(
                        f"예제 파일에서 설정 파일 생성: {config_name} ({config_file})"
                    )
                except Exception as e:
                    logger.error(f"설정 파일 복사 실패 {config_name}: {e}")

    def validate_config(self, config_name: str) -> tuple[bool, list[str]]:
        """
        설정 유효성 검사

        Args:
            config_name: 설정 이름

        Returns:
            (유효 여부, 오류 목록)
        """
        config = self.load_config(config_name)
        if config is None:
            return False, ["설정 파일을 찾을 수 없습니다"]

        errors = []

        if config_name == "cluster":
            if "cluster" not in config:
                errors.append("'cluster' 섹션이 없습니다")
            else:
                cluster = config["cluster"]
                if "master" not in cluster:
                    errors.append("'master' 노드 설정이 없습니다")
                elif "ip" not in cluster["master"]:
                    errors.append("'master.ip' 설정이 없습니다")

        elif config_name == "database":
            if "database" not in config:
                errors.append("'database' 섹션이 없습니다")
            else:
                db = config["database"]
                required = ["host", "port", "user", "password", "database"]
                for key in required:
                    if key not in db:
                        errors.append(f"'database.{key}' 설정이 없습니다")

        return len(errors) == 0, errors
