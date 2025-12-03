#!/usr/bin/env python3
"""
HDFS 연결 테스트 스크립트
HDFS 클라이언트의 연결, 읽기, 쓰기, 삭제 기능을 테스트합니다.
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Optional

# 통합 경로 설정 유틸리티 사용
try:
    from shared.path_utils import setup_pythonpath
    setup_pythonpath()
except ImportError:
    # Fallback: 유틸리티 로드 실패 시 하드코딩 경로 사용
    current_file = Path(__file__).resolve()
    cointicker_root = current_file.parent.parent
    sys.path.insert(0, str(cointicker_root))

try:
    from shared.hdfs_client import HDFSClient
except ImportError as e:
    print(f"❌ HDFS 클라이언트를 import할 수 없습니다: {e}")
    print(f"   cointicker 루트 경로 확인: {cointicker_root}")
    print(f"   shared 경로 확인: {cointicker_root / 'shared'}")
    print(f"   sys.path: {sys.path[:3]}")  # 처음 3개만 표시
    sys.exit(1)


def test_hdfs_connection(namenode: Optional[str] = None):
    """
    HDFS 연결 테스트

    Args:
        namenode: NameNode 주소 (None이면 기본값 사용)
    """
    print("=" * 50)
    print("HDFS 연결 테스트")
    print("=" * 50)
    print()

    # NameNode 주소 설정
    if namenode is None:
        # 환경변수 또는 기본값 사용
        namenode = os.environ.get("HDFS_NAMENODE", "hdfs://localhost:9000")

    print(f"NameNode 주소: {namenode}")
    print()
    print("⚠️  참고: HDFS 서버가 실행 중이어야 테스트가 성공합니다.")
    print("   HDFS를 시작하는 방법:")
    print("   1. GUI에서 HDFS 시작 (권장)")
    print("   2. 수동 실행:")
    print("      - HADOOP_HOME 환경변수 확인: echo $HADOOP_HOME")
    print("      - 일반 경로: hadoop_project/hadoop-3.4.1/sbin/start-dfs.sh")
    print("      - 실행: bash $HADOOP_HOME/sbin/start-dfs.sh")
    print("      - 또는: bash hadoop_project/hadoop-3.4.1/sbin/start-dfs.sh")
    print()

    # HDFS 클라이언트 초기화
    try:
        client = HDFSClient(namenode=namenode)
        print("✅ HDFS 클라이언트 초기화 성공")
    except Exception as e:
        print(f"❌ HDFS 클라이언트 초기화 실패: {e}")
        return False

    print()

    # 1. 루트 디렉토리 확인
    print("1. 루트 디렉토리 확인 중...")
    try:
        if client.exists("/"):
            print("   ✅ HDFS 루트 디렉토리 접근 성공")
        else:
            print("   ❌ HDFS 루트 디렉토리 접근 실패")
            print("   ⚠️  HDFS 서버가 실행되지 않았을 수 있습니다.")
            print("   💡 해결 방법:")
            print("      1. GUI에서 HDFS 시작 (권장)")
            print("      2. 수동 실행:")
            print("         - HADOOP_HOME 확인: echo $HADOOP_HOME")
            print("         - 실행: bash $HADOOP_HOME/sbin/start-dfs.sh")
            print("         - 또는: bash hadoop_project/hadoop-3.4.1/sbin/start-dfs.sh")
            print(f"      3. NameNode 주소 확인: {namenode}")
            return False
    except Exception as e:
        print(f"   ❌ 루트 디렉토리 확인 중 오류: {e}")
        error_msg = str(e).lower()
        if (
            "connection" in error_msg
            or "refused" in error_msg
            or "timeout" in error_msg
        ):
            print("   ⚠️  HDFS 서버 연결 실패")
            print("   💡 해결 방법:")
            print("      - HDFS 서버가 실행 중인지 확인하세요")
            print(f"      - NameNode 주소 확인: {namenode}")
            print("      - 방화벽 설정 확인")
        return False

    print()

    # 2. 테스트 디렉토리 생성
    test_dir = "/tmp/cointicker_test"
    print(f"2. 테스트 디렉토리 생성 중: {test_dir}")
    try:
        if client.mkdir(test_dir):
            print(f"   ✅ 테스트 디렉토리 생성 성공: {test_dir}")
        else:
            print(f"   ⚠️  테스트 디렉토리 생성 실패 (이미 존재할 수 있음)")
    except Exception as e:
        print(f"   ❌ 테스트 디렉토리 생성 중 오류: {e}")
        return False

    print()

    # 3. 테스트 파일 쓰기
    test_file = f"{test_dir}/test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    test_content = f"HDFS connection test\nTimestamp: {datetime.now().isoformat()}\n"
    print(f"3. 테스트 파일 쓰기 중: {test_file}")
    print(f"   내용: {test_content.strip()}")

    # 임시 로컬 파일 생성
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as tmp_file:
        tmp_file.write(test_content)
        tmp_local_path = tmp_file.name

    try:
        if client.put(tmp_local_path, test_file):
            print(f"   ✅ 파일 쓰기 성공: {test_file}")
        else:
            print(f"   ❌ 파일 쓰기 실패")
            os.unlink(tmp_local_path)
            return False
    except Exception as e:
        print(f"   ❌ 파일 쓰기 중 오류: {e}")
        os.unlink(tmp_local_path)
        return False
    finally:
        # 임시 파일 삭제
        if os.path.exists(tmp_local_path):
            os.unlink(tmp_local_path)

    print()

    # 4. 파일 읽기
    print(f"4. 테스트 파일 읽기 중: {test_file}")
    try:
        content = client.cat(test_file)
        if content:
            # 줄바꿈 문자 정규화
            content_normalized = content.replace("\r\n", "\n").strip()
            expected_normalized = test_content.replace("\r\n", "\n").strip()
            if content_normalized == expected_normalized:
                print(f"   ✅ 파일 읽기 성공")
                print(f"   내용: {content.strip()}")
            else:
                print(f"   ⚠️  파일 내용 불일치")
                print(f"   예상: {expected_normalized}")
                print(f"   실제: {content_normalized}")
        else:
            print(f"   ❌ 파일 읽기 실패 (내용 없음)")
            return False
    except Exception as e:
        print(f"   ❌ 파일 읽기 중 오류: {e}")
        return False

    print()

    # 5. 파일 존재 확인
    print(f"5. 파일 존재 확인 중: {test_file}")
    try:
        if client.exists(test_file):
            print(f"   ✅ 파일 존재 확인 성공")
        else:
            print(f"   ❌ 파일이 존재하지 않음")
            return False
    except Exception as e:
        print(f"   ❌ 파일 존재 확인 중 오류: {e}")
        return False

    print()

    # 6. 파일 목록 조회
    print(f"6. 디렉토리 파일 목록 조회 중: {test_dir}")
    try:
        files = client.list_files(test_dir)
        if files:
            print(f"   ✅ 파일 목록 조회 성공 ({len(files)}개 파일)")
            for file_path in files[:5]:  # 최대 5개만 표시
                print(f"      - {file_path}")
            if len(files) > 5:
                print(f"      ... 외 {len(files) - 5}개 파일")
        else:
            print(f"   ⚠️  파일 목록이 비어있음")
    except Exception as e:
        print(f"   ❌ 파일 목록 조회 중 오류: {e}")

    print()

    # 7. 파일 삭제
    print(f"7. 테스트 파일 삭제 중: {test_file}")
    try:
        if client.rm(test_file):
            print(f"   ✅ 파일 삭제 성공")
        else:
            print(f"   ❌ 파일 삭제 실패")
            return False
    except Exception as e:
        print(f"   ❌ 파일 삭제 중 오류: {e}")
        return False

    print()

    # 8. 테스트 디렉토리 삭제 (선택적)
    print(f"8. 테스트 디렉토리 삭제 중: {test_dir}")
    try:
        if client.rm(test_dir, recursive=True):
            print(f"   ✅ 테스트 디렉토리 삭제 성공")
        else:
            print(f"   ⚠️  테스트 디렉토리 삭제 실패 (수동 삭제 필요)")
    except Exception as e:
        print(f"   ⚠️  테스트 디렉토리 삭제 중 오류: {e} (수동 삭제 필요)")

    print()
    print("=" * 50)
    print("✅ 모든 HDFS 연결 테스트 통과!")
    print("=" * 50)
    return True


def main():
    """메인 함수"""
    import argparse

    parser = argparse.ArgumentParser(description="HDFS 연결 테스트")
    parser.add_argument(
        "--namenode",
        type=str,
        default=None,
        help="NameNode 주소 (예: hdfs://raspberry-master:9000, 기본값: hdfs://localhost:9000)",
    )
    args = parser.parse_args()

    success = test_hdfs_connection(namenode=args.namenode)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
