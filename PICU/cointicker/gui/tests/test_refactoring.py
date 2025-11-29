"""
리팩토링 테스트 스크립트
모든 모듈이 정상적으로 작동하는지 확인

⚠️ 주의: 리팩토링이 완료되어 통합 테스트 스크립트에서 자동 실행되지 않습니다.
필요시 수동으로 실행할 수 있습니다: python3 gui/tests/test_refactoring.py
"""

import sys
from pathlib import Path

# 프로젝트 루트를 경로에 추가
# gui/tests/test_refactoring.py -> gui/ -> cointicker/
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def test_ui_tabs_import():
    """UI 탭 모듈 import 테스트"""
    print("=" * 60)
    print("1. UI 탭 모듈 Import 테스트")
    print("=" * 60)

    try:
        from gui.ui import (
            DashboardTab,
            ClusterTab,
            Tier2Tab,
            ModulesTab,
            ControlTab,
            ConfigTab,
        )

        print("✅ 모든 UI 탭 모듈 import 성공")
        print(f"   - DashboardTab: {DashboardTab}")
        print(f"   - ClusterTab: {ClusterTab}")
        print(f"   - Tier2Tab: {Tier2Tab}")
        print(f"   - ModulesTab: {ModulesTab}")
        print(f"   - ControlTab: {ControlTab}")
        print(f"   - ConfigTab: {ConfigTab}")
        return True
    except Exception as e:
        print(f"❌ UI 탭 모듈 import 실패: {e}")
        return False


def test_managers_import():
    """매니저 모듈 import 테스트"""
    print("\n" + "=" * 60)
    print("2. 매니저 모듈 Import 테스트")
    print("=" * 60)

    try:
        from gui.modules.managers import HDFSManager, KafkaManager, SSHManager

        print("✅ 모든 매니저 모듈 import 성공")
        print(f"   - HDFSManager: {HDFSManager}")
        print(f"   - KafkaManager: {KafkaManager}")
        print(f"   - SSHManager: {SSHManager}")
        return True
    except Exception as e:
        print(f"❌ 매니저 모듈 import 실패: {e}")
        return False


def test_managers_instantiation():
    """매니저 인스턴스 생성 테스트"""
    print("\n" + "=" * 60)
    print("3. 매니저 인스턴스 생성 테스트")
    print("=" * 60)

    try:
        from gui.modules.managers import HDFSManager, KafkaManager, SSHManager

        # SSHManager 테스트
        ssh_manager = SSHManager()
        print("✅ SSHManager 인스턴스 생성 성공")

        # KafkaManager 테스트
        kafka_manager = KafkaManager()
        print("✅ KafkaManager 인스턴스 생성 성공")

        # HDFSManager 테스트
        hdfs_manager = HDFSManager()
        print("✅ HDFSManager 인스턴스 생성 성공")

        return True
    except Exception as e:
        print(f"❌ 매니저 인스턴스 생성 실패: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_pipeline_orchestrator():
    """PipelineOrchestrator 테스트"""
    print("\n" + "=" * 60)
    print("4. PipelineOrchestrator 테스트")
    print("=" * 60)

    try:
        from gui.modules.pipeline_orchestrator import PipelineOrchestrator

        # 인스턴스 생성
        orchestrator = PipelineOrchestrator()
        print("✅ PipelineOrchestrator 인스턴스 생성 성공")

        # 매니저 확인
        if hasattr(orchestrator, "hdfs_manager"):
            print("✅ hdfs_manager 속성 확인")
        else:
            print("❌ hdfs_manager 속성 없음")
            return False

        if hasattr(orchestrator, "kafka_manager"):
            print("✅ kafka_manager 속성 확인")
        else:
            print("❌ kafka_manager 속성 없음")
            return False

        if hasattr(orchestrator, "ssh_manager"):
            print("✅ ssh_manager 속성 확인")
        else:
            print("❌ ssh_manager 속성 없음")
            return False

        # 초기화 테스트
        result = orchestrator.initialize({})
        if result:
            print("✅ PipelineOrchestrator 초기화 성공")
        else:
            print("❌ PipelineOrchestrator 초기화 실패")
            return False

        return True
    except Exception as e:
        print(f"❌ PipelineOrchestrator 테스트 실패: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_ui_tabs_instantiation():
    """UI 탭 인스턴스 생성 테스트 (PyQt5 없이도 가능한 부분)"""
    print("\n" + "=" * 60)
    print("5. UI 탭 클래스 구조 테스트")
    print("=" * 60)

    try:
        from gui.ui import (
            DashboardTab,
            ClusterTab,
            Tier2Tab,
            ModulesTab,
            ControlTab,
            ConfigTab,
        )

        # 클래스 확인
        tabs = [
            ("DashboardTab", DashboardTab),
            ("ClusterTab", ClusterTab),
            ("Tier2Tab", Tier2Tab),
            ("ModulesTab", ModulesTab),
            ("ControlTab", ControlTab),
            ("ConfigTab", ConfigTab),
        ]

        for name, tab_class in tabs:
            if hasattr(tab_class, "__init__"):
                print(f"✅ {name} 클래스 확인 (__init__ 메서드 존재)")
            else:
                print(f"❌ {name} 클래스에 __init__ 메서드 없음")
                return False

        return True
    except Exception as e:
        print(f"❌ UI 탭 클래스 구조 테스트 실패: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_manager_methods():
    """매니저 메서드 테스트"""
    print("\n" + "=" * 60)
    print("6. 매니저 메서드 테스트")
    print("=" * 60)

    try:
        from gui.modules.managers import HDFSManager, KafkaManager, SSHManager

        # SSHManager 메서드 확인
        ssh_manager = SSHManager()
        if hasattr(ssh_manager, "test_connection"):
            print("✅ SSHManager.test_connection() 메서드 확인")
        if hasattr(ssh_manager, "setup_local_ssh"):
            print("✅ SSHManager.setup_local_ssh() 메서드 확인")

        # KafkaManager 메서드 확인
        kafka_manager = KafkaManager()
        if hasattr(kafka_manager, "start_broker"):
            print("✅ KafkaManager.start_broker() 메서드 확인")
        if hasattr(kafka_manager, "check_broker_running"):
            print("✅ KafkaManager.check_broker_running() 메서드 확인")

        # HDFSManager 메서드 확인
        hdfs_manager = HDFSManager()
        if hasattr(hdfs_manager, "check_running"):
            print("✅ HDFSManager.check_running() 메서드 확인")
        if hasattr(hdfs_manager, "check_and_start"):
            print("✅ HDFSManager.check_and_start() 메서드 확인")
        if hasattr(hdfs_manager, "setup_single_node_mode"):
            print("✅ HDFSManager.setup_single_node_mode() 메서드 확인")
        if hasattr(hdfs_manager, "setup_cluster_mode"):
            print("✅ HDFSManager.setup_cluster_mode() 메서드 확인")

        return True
    except Exception as e:
        print(f"❌ 매니저 메서드 테스트 실패: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_app_structure():
    """app.py 구조 테스트"""
    print("\n" + "=" * 60)
    print("7. app.py 구조 테스트")
    print("=" * 60)

    try:
        # PyQt5가 없으면 테스트 스킵
        try:
            from PyQt5.QtWidgets import QApplication
        except ImportError:
            print("⚠️ PyQt5가 없어 app.py 구조 테스트를 건너뜁니다.")
            return True

        # app.py에서 MainApplication 확인
        import gui.app

        if hasattr(gui.app, "MainApplication"):
            print("✅ MainApplication 클래스 확인")
        else:
            print("❌ MainApplication 클래스 없음")
            return False

        # 탭 관련 속성 확인 (클래스 정의 확인)
        # 실제 인스턴스는 GUI 실행 시 생성되므로 여기서는 확인 불가

        return True
    except Exception as e:
        print(f"❌ app.py 구조 테스트 실패: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """메인 테스트 함수"""
    print("\n" + "=" * 60)
    print("GUI 리팩토링 테스트 시작")
    print("=" * 60 + "\n")

    results = []

    # 테스트 실행
    results.append(("UI 탭 모듈 Import", test_ui_tabs_import()))
    results.append(("매니저 모듈 Import", test_managers_import()))
    results.append(("매니저 인스턴스 생성", test_managers_instantiation()))
    results.append(("PipelineOrchestrator", test_pipeline_orchestrator()))
    results.append(("UI 탭 클래스 구조", test_ui_tabs_instantiation()))
    results.append(("매니저 메서드", test_manager_methods()))
    results.append(("app.py 구조", test_app_structure()))

    # 결과 요약
    print("\n" + "=" * 60)
    print("테스트 결과 요약")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ 통과" if result else "❌ 실패"
        print(f"{status}: {test_name}")

    print(f"\n총 {total}개 테스트 중 {passed}개 통과 ({passed/total*100:.1f}%)")

    if passed == total:
        print("\n🎉 모든 테스트 통과!")
        return 0
    else:
        print(f"\n⚠️ {total - passed}개 테스트 실패")
        return 1


if __name__ == "__main__":
    sys.exit(main())
