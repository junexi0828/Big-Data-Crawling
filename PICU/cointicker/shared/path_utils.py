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

    # 추가할 경로 목록 (기존 하드코딩된 모든 경로 포함)
    paths_to_add = [
        str(cointicker_root),  # cointicker/
        str(shared_dir),  # cointicker/shared/
        str(cointicker_root / "worker-nodes"),  # cointicker/worker-nodes/
        str(cointicker_root / "backend"),  # cointicker/backend/
        str(cointicker_root / "worker-nodes" / "mapreduce"),  # cointicker/worker-nodes/mapreduce/
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


def get_hadoop_home() -> Optional[Path]:
    """
    Hadoop 설치 경로 자동 감지

    다음 순서로 Hadoop 경로를 찾습니다:
    1. HADOOP_HOME 환경변수
    2. cluster_config.yaml 설정 파일
    3. hadoop 명령어 위치에서 추론
    4. 프로젝트 인접 경로 (PICU/../hadoop_project/hadoop-*)
    5. 표준 설치 경로들 (/opt/hadoop*, /usr/local/hadoop*, etc.)

    Returns:
        Hadoop 설치 경로, 없으면 None
    """
    import os
    import shutil
    import glob

    # 1. 환경변수 확인
    hadoop_home = os.environ.get("HADOOP_HOME")
    if hadoop_home and Path(hadoop_home).exists():
        return Path(hadoop_home)

    # 2. cluster_config.yaml에서 hadoop.home 확인
    try:
        cointicker_root = get_cointicker_root()
        config_file = cointicker_root / "config" / "cluster_config.yaml"
        if config_file.exists():
            import yaml
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
                if config and 'hadoop' in config:
                    # 'home' 또는 'hadoop_home' 필드 확인
                    hadoop_home_value = config['hadoop'].get('home') or config['hadoop'].get('hadoop_home')
                    if hadoop_home_value:
                        hadoop_path = Path(hadoop_home_value)
                        if hadoop_path.exists():
                            return hadoop_path
    except Exception:
        pass  # yaml이 없거나 파일을 읽을 수 없으면 스킵

    # 3. hadoop 명령어가 PATH에 있으면 그 위치에서 HADOOP_HOME 추론
    hadoop_bin = shutil.which("hadoop")
    if hadoop_bin:
        # hadoop 명령어 경로: /path/to/hadoop-x.x.x/bin/hadoop
        # HADOOP_HOME: /path/to/hadoop-x.x.x
        hadoop_path = Path(hadoop_bin).parent.parent
        if (hadoop_path / "bin" / "hadoop").exists():
            return hadoop_path

    # 4. 프로젝트 인접 경로 확인 (hadoop_project/hadoop-*)
    picu_root = get_project_root()
    hadoop_project_dir = picu_root.parent / "hadoop_project"
    if hadoop_project_dir.exists():
        # hadoop-3.4.1, hadoop-3.3.0 등 모든 버전 검색
        hadoop_dirs = sorted(hadoop_project_dir.glob("hadoop-*"), reverse=True)
        for hadoop_dir in hadoop_dirs:
            if (hadoop_dir / "bin" / "hadoop").exists():
                return hadoop_dir

    # 5. 표준 설치 경로들 확인
    standard_paths = [
        "/opt/hadoop",           # 기본
        "/opt/hadoop-*",         # 버전 포함 (예: /opt/hadoop-3.4.1)
        "/usr/local/hadoop",     # 로컬 설치
        "/usr/local/hadoop-*",   # 버전 포함
        "/home/*/hadoop-*",      # 사용자 홈 디렉토리
    ]

    for pattern in standard_paths:
        if "*" in pattern:
            # glob 패턴
            matches = sorted(glob.glob(pattern), reverse=True)
            for match in matches:
                hadoop_path = Path(match)
                if (hadoop_path / "bin" / "hadoop").exists():
                    return hadoop_path
        else:
            # 고정 경로
            hadoop_path = Path(pattern)
            if (hadoop_path / "bin" / "hadoop").exists():
                return hadoop_path

    return None


def setup_hadoop_env(verbose: bool = False) -> bool:
    """
    Hadoop 환경변수 자동 설정

    HADOOP_HOME이 설정되지 않은 경우 자동으로 찾아서 설정합니다.
    PATH에 $HADOOP_HOME/bin과 $HADOOP_HOME/sbin을 추가합니다.

    Args:
        verbose: 설정 정보 출력 여부

    Returns:
        성공 여부
    """
    import os

    # 이미 HADOOP_HOME이 설정되어 있으면 스킵
    if os.environ.get("HADOOP_HOME"):
        if verbose:
            print(f"✅ HADOOP_HOME 이미 설정됨: {os.environ['HADOOP_HOME']}")
        return True

    # Hadoop 경로 자동 감지
    hadoop_home = get_hadoop_home()
    if not hadoop_home:
        if verbose:
            print("⚠️  Hadoop 설치 경로를 찾을 수 없습니다.")
        return False

    # 환경변수 설정
    os.environ["HADOOP_HOME"] = str(hadoop_home)

    # PATH에 Hadoop bin과 sbin 추가
    hadoop_bin = hadoop_home / "bin"
    hadoop_sbin = hadoop_home / "sbin"

    current_path = os.environ.get("PATH", "")
    new_paths = []

    if hadoop_bin.exists() and str(hadoop_bin) not in current_path:
        new_paths.append(str(hadoop_bin))

    if hadoop_sbin.exists() and str(hadoop_sbin) not in current_path:
        new_paths.append(str(hadoop_sbin))

    if new_paths:
        os.environ["PATH"] = ":".join(new_paths) + ":" + current_path

    if verbose:
        print(f"✅ HADOOP_HOME 자동 설정: {hadoop_home}")
        if new_paths:
            print(f"✅ PATH에 Hadoop 경로 추가:")
            for path in new_paths:
                print(f"   - {path}")

    return True


# 모듈 import 시 자동으로 PYTHONPATH 및 Hadoop 환경 설정
# verbose=True로 설정하려면 환경 변수 PICU_PATH_VERBOSE=1 사용
import os
verbose_mode = os.environ.get("PICU_PATH_VERBOSE", "0") == "1"
setup_pythonpath(verbose=verbose_mode)
setup_hadoop_env(verbose=verbose_mode)
