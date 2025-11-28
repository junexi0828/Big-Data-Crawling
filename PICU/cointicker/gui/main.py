"""
GUI 대시보드 실행 스크립트
엔터프라이즈급 통합 애플리케이션 진입점
"""

import sys
from pathlib import Path

# 프로젝트 루트를 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# PyQt5 기반 애플리케이션 사용 시도
try:
    from gui.app import main
except ImportError:
    # PyQt5가 없으면 tkinter 버전 사용 시도
    try:
        from gui.dashboard import main
    except ImportError:
        # GUI가 모두 없으면 CLI 모드
        def main():
            print("=" * 60)
            print("CoinTicker 통합 관리 시스템")
            print("=" * 60)
            print("\nGUI 라이브러리가 설치되지 않았습니다.")
            print("\n설치 방법:")
            print("  1. PyQt5 설치 (권장): pip install PyQt5")
            print("  2. 또는 CLI 설치 마법사: python gui/installer/installer_cli.py")
            print("  3. 또는 자동 설치: bash gui/scripts/install.sh")
            print("\n" + "=" * 60)

            try:
                response = (
                    input("\nCLI 설치 마법사를 실행하시겠습니까? [Y/n]: ")
                    .strip()
                    .lower()
                )
                if not response or response in ["y", "yes", "예", "ㅇ"]:
                    from gui.installer.installer_cli import main as cli_main

                    cli_main()
            except (KeyboardInterrupt, EOFError):
                print("\n취소되었습니다.")
            except Exception as e:
                print(f"\n오류: {e}")


if __name__ == "__main__":
    main()
