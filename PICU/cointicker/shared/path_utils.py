"""
경로 설정 유틸리티

모든 Python 파일에서 import하여 사용
PYTHONPATH 설정을 중앙 집중화
"""

import sys
from pathlib import Path
from typing import Optional


def setup_pythonpath(verbose: bool = False) -> None:
    """
    PYTHONPATH 설정 (중복 방지)

    프로젝트 구조:
    PICU/
    └── cointicker/
        ├── shared/
        ├── worker-nodes/
        ├── backend/
        └── gui/

    Args:
        verbose: 설정 정보 출력 여부
    """
    # 현재 파일 위치에서 cointicker 루트 찾기
    current_file = Path(__file__).resolve()
    shared_dir = current_file.parent  # shared/
    cointicker_root = shared_dir.parent  # cointicker/
    picu_root = cointicker_root.parent  # PICU/

    # 추가할 경로 목록
    paths_to_add = [
        str(cointicker_root),  # cointicker/
        str(shared_dir),  # cointicker/shared/
    ]

    # 중복 방지하면서 sys.path에 추가
    added_paths = []
    for path in paths_to_add:
        if path not in sys.path:
            sys.path.insert(0, path)
            added_paths.append(path)

    if verbose and added_paths:
        print(f"✅ PYTHONPATH 설정 완료:")
        for path in added_paths:
            print(f"   - {path}")


def get_project_root() -> Path:
    """
    프로젝트 루트 경로 반환 (PICU/)

    Returns:
        PICU 디렉토리의 절대 경로
    """
    current_file = Path(__file__).resolve()
    shared_dir = current_file.parent
    cointicker_root = shared_dir.parent
    picu_root = cointicker_root.parent
    return picu_root


def get_cointicker_root() -> Path:
    """
    cointicker 루트 경로 반환

    Returns:
        cointicker 디렉토리의 절대 경로
    """
    current_file = Path(__file__).resolve()
    shared_dir = current_file.parent
    cointicker_root = shared_dir.parent
    return cointicker_root


def get_shared_dir() -> Path:
    """
    shared 디렉토리 경로 반환

    Returns:
        shared 디렉토리의 절대 경로
    """
    return Path(__file__).resolve().parent


def get_worker_nodes_dir() -> Path:
    """
    worker-nodes 디렉토리 경로 반환

    Returns:
        worker-nodes 디렉토리의 절대 경로
    """
    return get_cointicker_root() / "worker-nodes"


def get_backend_dir() -> Path:
    """
    backend 디렉토리 경로 반환

    Returns:
        backend 디렉토리의 절대 경로
    """
    return get_cointicker_root() / "backend"


def get_gui_dir() -> Path:
    """
    gui 디렉토리 경로 반환

    Returns:
        gui 디렉토리의 절대 경로
    """
    return get_cointicker_root() / "gui"


# 모듈 import 시 자동으로 PYTHONPATH 설정
# verbose=True로 설정하려면 환경 변수 PICU_PATH_VERBOSE=1 사용
import os
verbose_mode = os.environ.get("PICU_PATH_VERBOSE", "0") == "1"
setup_pythonpath(verbose=verbose_mode)
