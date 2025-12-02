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
from gui.core.cache_manager import get_cache_manager

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
        self.cache = get_cache_manager()
        # 설정 파일 캐시 TTL: 60초 (설정 파일은 자주 변경되지 않음)
        self.cache_ttl = 60.0

    def load_config(self, config_name: str) -> Optional[dict]:
        """
        설정 파일 로드 (캐싱 적용)

        Args:
            config_name: 설정 이름 (cluster, database, spider, gui)

        Returns:
            설정 딕셔너리 또는 None
        """
        # 메모리 캐시 확인 (가장 빠름)
        if config_name in self.configs:
            return self.configs[config_name]

        if config_name not in self.config_files:
            logger.error(f"알 수 없는 설정 이름: {config_name}")
            return None

        cache_key = f"config_file:{config_name}"

        # 디스크 캐시 확인 (TTL 기반)
        config = self.cache.get(
            cache_key,
            ttl_seconds=self.cache_ttl,
            factory=lambda: self._load_config_from_file(config_name),
        )

        if config is not None:
            self.configs[config_name] = config

        return config

    def _load_config_from_file(self, config_name: str) -> Optional[dict]:
        """
        설정 파일에서 실제 로드 (캐싱 없이)

        Args:
            config_name: 설정 이름

        Returns:
            설정 딕셔너리 또는 None
        """
        config_file = self.config_dir / self.config_files[config_name]

        # 실제 config 파일이 없으면 example에서 생성
        if not config_file.exists():
            example_file = (
                self.config_dir
                / "examples"
                / (self.config_files[config_name] + ".example")
            )
            if example_file.exists():
                try:
                    # example 파일을 config 파일로 복사 (자동 생성)
                    shutil.copy2(example_file, config_file)
                    logger.info(
                        f"예제 파일에서 설정 파일 생성: {config_name} ({config_file})"
                    )
                except Exception as e:
                    logger.error(f"설정 파일 생성 실패 {config_name}: {e}")
                    # 복사 실패 시 example 파일 읽기 (폴백)
                    logger.warning(f"예제 파일을 직접 사용합니다: {config_file}")
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

            logger.info(f"설정 로드 완료: {config_name}")
            return config or {}
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

        # 설정 변경 시 캐시 무효화
        cache_key = f"config_file:{config_name}"
        self.cache.delete(cache_key)
        if config_name in self.configs:
            del self.configs[config_name]

    def create_default_configs(self):
        """기본 설정 파일 생성 (예제 파일에서 복사)"""
        # GUI 설정은 기본값으로 생성
        default_configs = {
            "gui": {
                "window": {"width": 1400, "height": 900, "theme": "default"},
                "refresh": {"auto_refresh": False, "interval": 30},
                "tier2": {"base_url": "http://localhost:5000", "timeout": 5},
                "cluster": {"ssh_timeout": 10, "retry_count": 3},
                "auto_start": {
                    "enabled": True,  # GUI 시작 시 자동 시작 활성화
                    "processes": ["backend", "frontend"],  # 자동 시작할 프로세스 목록
                },
                "systemd": {
                    "enabled": False,  # systemd 서비스 사용 여부
                    "services": {
                        "tier1_orchestrator": {
                            "enabled": False,  # Tier 1 오케스트레이터 서비스
                            "auto_start_on_boot": False,  # 부팅 시 자동 시작
                        },
                        "tier2_scheduler": {
                            "enabled": False,  # Tier 2 파이프라인 스케줄러 서비스
                            "auto_start_on_boot": False,  # 부팅 시 자동 시작
                        },
                    },
                },
                "timing": {
                    "auto_start_delay": 1000,  # GUI 시작 후 백엔드/프론트엔드 자동 시작 지연 (ms)
                    "process_status_update_delay": 2000,  # 프로세스 상태 업데이트 지연 (ms)
                    "initial_refresh_delay": 5000,  # 초기 데이터 로드 지연 (ms)
                    "stats_update_interval": 2000,  # 통계 업데이트 간격 (ms)
                    "tier2_reconnect_delay": 3000,  # Tier2 재연결 지연 (ms)
                    "tier2_refresh_delay": 5000,  # Tier2 새로고침 지연 (ms)
                    "dialog_wait_delay": 0.2,  # 다이얼로그 대기 시간 (초)
                    "config_refresh_delay": 500,  # 설정 새로고침 지연 (ms)
                    "user_confirm_timeout": 30,  # 사용자 확인 대기 시간 (초, 30초)
                },
                "retry": {
                    "default_max_retries": 3,  # 기본 최대 재시도 횟수
                    "default_delay": 1.0,  # 기본 재시도 지연 시간 (초)
                    "backoff_factor": 1.5,  # 재시도 간격 증가 배수
                },
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
            example_file = (
                self.config_dir
                / "examples"
                / (self.config_files[config_name] + ".example")
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
