"""
설치 마법사 CLI 버전
GUI 없이 터미널에서 실행 가능한 설치 마법사
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트 찾기 (PICU 또는 cointicker)
current_path = Path(__file__).resolve()
if current_path.parts[-4] == "PICU":
    # PICU 루트에서 실행
    project_root = current_path.parent.parent.parent
    cointicker_root = project_root / "cointicker"
else:
    # cointicker에서 실행
    project_root = current_path.parent.parent.parent
    cointicker_root = project_root

sys.path.insert(0, str(project_root))
sys.path.insert(0, str(cointicker_root))

from gui.installer.installer import DependencyInstaller
from shared.logger import setup_logger

logger = setup_logger(__name__)


def print_header(text: str):
    """헤더 출력"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def print_step(step_num: int, total: int, text: str):
    """단계 출력"""
    print(f"[{step_num}/{total}] {text}")
    print("-" * 60)


def print_success(text: str):
    """성공 메시지 출력"""
    print(f"✅ {text}")


def print_error(text: str):
    """오류 메시지 출력"""
    print(f"❌ {text}")


def print_warning(text: str):
    """경고 메시지 출력"""
    print(f"⚠️  {text}")


def ask_yes_no(prompt: str, default: bool = True) -> bool:
    """예/아니오 질문"""
    default_text = "Y/n" if default else "y/N"
    response = input(f"{prompt} [{default_text}]: ").strip().lower()

    if not response:
        return default

    return response in ["y", "yes", "예", "ㅇ"]


def main():
    """메인 함수"""
    print_header("CoinTicker 설치 마법사")

    print("이 마법사는 CoinTicker 프로젝트의 모든 의존성을 자동으로 설치합니다.")
    print("\n설치 과정:")
    print("  1. Python 버전 확인")
    print("  2. pip 확인")
    print("  3. 가상환경 생성 (선택)")
    print("  4. 시스템 의존성 설치")
    print("  5. Python 의존성 설치")
    print("  6. 설치 확인")

    if not ask_yes_no("\n계속하시겠습니까?", default=True):
        print("설치가 취소되었습니다.")
        return

    # 가상환경 생성 여부
    create_venv = ask_yes_no("\n가상환경을 생성하시겠습니까? (권장)", default=True)

    # 프로젝트 루트 찾기
    current_path = Path(__file__).resolve()
    if "PICU" in current_path.parts:
        picu_index = current_path.parts.index("PICU")
        project_root = str(Path("/").joinpath(*current_path.parts[: picu_index + 1]))
    else:
        cointicker_index = current_path.parts.index("cointicker")
        project_root = str(
            Path("/").joinpath(*current_path.parts[: cointicker_index + 1])
        )

    # 설치 시작
    installer = DependencyInstaller(project_root=project_root)
    result = installer.run_full_installation(create_venv=create_venv)

    # 결과 출력
    print_header("설치 결과")

    for step in result.get("steps", []):
        step_name = step.get("name", "알 수 없음")
        success = step.get("success", False)

        if success:
            print_success(f"{step_name}: 완료")
            if "logs" in step:
                for log in step["logs"][-5:]:  # 마지막 5줄만
                    if log.strip():
                        print(f"  {log}")
        else:
            print_error(f"{step_name}: 실패")
            if "message" in step:
                print(f"  {step['message']}")
            if "logs" in step:
                for log in step["logs"]:
                    if "실패" in log or "오류" in log or "✗" in log:
                        print(f"  {log}")

    # 최종 결과
    print_header("최종 결과")

    if result["success"]:
        print_success("설치가 성공적으로 완료되었습니다!")
        print("\n다음 단계:")
        if "PICU" in str(Path(__file__).resolve()):
            print("  1. 가상환경 활성화:")
            print("     source venv/bin/activate")
            print("  2. 설정 파일을 확인하세요 (cointicker/config/ 디렉토리)")
            print("  3. 데이터베이스를 초기화하세요:")
            print("     python cointicker/backend/init_db.py")
            print("  4. GUI 애플리케이션을 실행하세요:")
            print("     python cointicker/gui/main.py")
            print("     또는: bash run_gui.sh")
        else:
            print("  1. 설정 파일을 확인하세요 (config/ 디렉토리)")
            print("  2. 데이터베이스를 초기화하세요:")
            print("     python backend/init_db.py")
            print("  3. GUI 애플리케이션을 실행하세요:")
            print("     python gui/main.py")
    else:
        print_error("설치 중 오류가 발생했습니다.")
        print("\n오류 목록:")
        for error in result.get("errors", []):
            print(f"  - {error}")
        print("\n문제 해결:")
        print("  1. 로그를 확인하세요")
        print("  2. 필요한 권한이 있는지 확인하세요 (sudo)")
        print("  3. 네트워크 연결을 확인하세요")
        print("  4. 수동으로 설치를 시도하세요:")
        print("     pip install -r requirements.txt")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n설치가 사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print_error(f"예상치 못한 오류가 발생했습니다: {e}")
        logger.exception("설치 마법사 오류")
        sys.exit(1)
