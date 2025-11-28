"""
통합 테스트 스크립트
실제 기능 동작 확인
"""

import sys
from pathlib import Path

# 프로젝트 루트를 경로에 추가
# gui/tests/test_integration.py -> gui/ -> cointicker/
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def test_pipeline_orchestrator_integration():
    """PipelineOrchestrator와 매니저 통합 테스트"""
    print("=" * 60)
    print("PipelineOrchestrator 통합 테스트")
    print("=" * 60)

    try:
        from gui.modules.pipeline_orchestrator import PipelineOrchestrator

        # 인스턴스 생성
        orchestrator = PipelineOrchestrator()
        print("✅ PipelineOrchestrator 인스턴스 생성")

        # 매니저가 올바르게 연결되었는지 확인
        assert orchestrator.hdfs_manager is not None, "hdfs_manager가 None입니다"
        assert orchestrator.kafka_manager is not None, "kafka_manager가 None입니다"
        assert orchestrator.ssh_manager is not None, "ssh_manager가 None입니다"
        print("✅ 모든 매니저가 올바르게 연결됨")

        # 매니저 메서드 호출 가능 여부 확인
        # (실제 실행은 하지 않고 메서드 존재만 확인)
        assert hasattr(
            orchestrator.kafka_manager, "start_broker"
        ), "kafka_manager.start_broker 메서드 없음"
        assert hasattr(
            orchestrator.kafka_manager, "check_broker_running"
        ), "kafka_manager.check_broker_running 메서드 없음"
        print("✅ KafkaManager 메서드 확인")

        assert hasattr(
            orchestrator.hdfs_manager, "check_running"
        ), "hdfs_manager.check_running 메서드 없음"
        assert hasattr(
            orchestrator.hdfs_manager, "check_and_start"
        ), "hdfs_manager.check_and_start 메서드 없음"
        print("✅ HDFSManager 메서드 확인")

        assert hasattr(
            orchestrator.ssh_manager, "test_connection"
        ), "ssh_manager.test_connection 메서드 없음"
        assert hasattr(
            orchestrator.ssh_manager, "setup_local_ssh"
        ), "ssh_manager.setup_local_ssh 메서드 없음"
        print("✅ SSHManager 메서드 확인")

        # 초기화 테스트
        result = orchestrator.initialize({})
        assert result, "초기화 실패"
        print("✅ PipelineOrchestrator 초기화 성공")

        # 상태 확인
        status = orchestrator.get_status()
        assert isinstance(status, dict), "상태가 딕셔너리가 아닙니다"
        print(f"✅ 프로세스 상태 확인: {len(status)}개 프로세스")

        return True
    except Exception as e:
        print(f"❌ 통합 테스트 실패: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_manager_method_calls():
    """매니저 메서드 호출 테스트 (실제 실행 없이)"""
    print("\n" + "=" * 60)
    print("매니저 메서드 호출 테스트")
    print("=" * 60)

    try:
        from gui.modules.managers import HDFSManager, KafkaManager, SSHManager

        # SSHManager 테스트
        ssh_manager = SSHManager()
        # test_connection은 실제로 호출하지 않고 메서드 존재만 확인
        assert callable(
            ssh_manager.test_connection
        ), "test_connection이 호출 가능하지 않습니다"
        assert callable(
            ssh_manager.setup_local_ssh
        ), "setup_local_ssh가 호출 가능하지 않습니다"
        print("✅ SSHManager 메서드 호출 가능")

        # KafkaManager 테스트
        kafka_manager = KafkaManager()
        # check_broker_running은 실제로 호출 가능 (포트 확인만)
        result = kafka_manager.check_broker_running()
        assert isinstance(
            result, bool
        ), "check_broker_running이 bool을 반환하지 않습니다"
        print(f"✅ KafkaManager.check_broker_running() 호출 성공 (결과: {result})")

        # HDFSManager 테스트
        hdfs_manager = HDFSManager()
        # check_running은 실제로 호출 가능 (포트 확인만)
        result = hdfs_manager.check_running()
        assert isinstance(result, bool), "check_running이 bool을 반환하지 않습니다"
        print(f"✅ HDFSManager.check_running() 호출 성공 (결과: {result})")

        return True
    except Exception as e:
        print(f"❌ 매니저 메서드 호출 테스트 실패: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_ui_tabs_structure():
    """UI 탭 구조 테스트 (PyQt5 필요)"""
    print("\n" + "=" * 60)
    print("UI 탭 구조 테스트")
    print("=" * 60)

    try:
        # PyQt5 확인
        try:
            from PyQt5.QtWidgets import QApplication

            app = QApplication([])
        except ImportError:
            print("⚠️ PyQt5가 없어 UI 탭 구조 테스트를 건너뜁니다.")
            return True

        from gui.ui import (
            DashboardTab,
            ClusterTab,
            Tier2Tab,
            ModulesTab,
            ControlTab,
            ConfigTab,
        )

        # 각 탭 클래스의 필수 메서드 확인
        tabs = [
            ("DashboardTab", DashboardTab),
            ("ClusterTab", ClusterTab),
            ("Tier2Tab", Tier2Tab),
            ("ModulesTab", ModulesTab),
            ("ControlTab", ControlTab),
            ("ConfigTab", ConfigTab),
        ]

        for name, tab_class in tabs:
            # __init__ 메서드 확인
            assert hasattr(tab_class, "__init__"), f"{name}에 __init__ 메서드 없음"

            # 인스턴스 생성 테스트 (None 전달)
            try:
                tab = tab_class(parent=None)
                assert tab is not None, f"{name} 인스턴스 생성 실패"
                print(f"✅ {name} 인스턴스 생성 성공")
            except Exception as e:
                print(f"❌ {name} 인스턴스 생성 실패: {e}")
                return False

        app.quit()
        return True
    except Exception as e:
        print(f"❌ UI 탭 구조 테스트 실패: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """메인 테스트 함수"""
    print("\n" + "=" * 60)
    print("GUI 리팩토링 통합 테스트 시작")
    print("=" * 60 + "\n")

    results = []

    # 테스트 실행
    results.append(
        ("PipelineOrchestrator 통합", test_pipeline_orchestrator_integration())
    )
    results.append(("매니저 메서드 호출", test_manager_method_calls()))
    results.append(("UI 탭 구조", test_ui_tabs_structure()))

    # 결과 요약
    print("\n" + "=" * 60)
    print("통합 테스트 결과 요약")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ 통과" if result else "❌ 실패"
        print(f"{status}: {test_name}")

    print(f"\n총 {total}개 테스트 중 {passed}개 통과 ({passed/total*100:.1f}%)")

    if passed == total:
        print("\n🎉 모든 통합 테스트 통과!")
        return 0
    else:
        print(f"\n⚠️ {total - passed}개 테스트 실패")
        return 1


if __name__ == "__main__":
    sys.exit(main())
