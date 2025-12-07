#!/usr/bin/env python3
"""
데이터 파이프라인 검증 스크립트

이 스크립트는 PICU 데이터 파이프라인의 전체 흐름을 검증합니다:
1. Kafka 브로커 실행 확인
2. Spider 프로세스 실행 확인
3. Kafka Consumer 프로세스 실행 확인
4. Kafka 토픽 존재 및 메시지 확인
5. HDFS 데이터 저장 확인
6. GUI 서비스 실행 확인

사용법:
    python verify_pipeline.py [--verbose] [--wait-time SECONDS]

옵션:
    --verbose: 상세한 출력 표시
    --wait-time: 검증 간 대기 시간 (기본값: 5초)
    --skip-hdfs: HDFS 검증 건너뛰기
"""

import sys
import subprocess
import time
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

# ANSI 색상 코드
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text: str):
    """헤더 출력"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(80)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}\n")

def print_section(text: str):
    """섹션 헤더 출력"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}▶ {text}{Colors.END}")
    print(f"{Colors.BLUE}{'-'*80}{Colors.END}")

def print_success(text: str):
    """성공 메시지 출력"""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text: str):
    """오류 메시지 출력"""
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_warning(text: str):
    """경고 메시지 출력"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_info(text: str):
    """정보 메시지 출력"""
    print(f"{Colors.CYAN}ℹ️  {text}{Colors.END}")

def run_command(cmd: List[str], timeout: int = 10, capture_output: bool = True) -> Tuple[bool, str, str]:
    """
    명령어 실행

    Returns:
        (성공 여부, stdout, stderr)
    """
    try:
        if capture_output:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode == 0, result.stdout, result.stderr
        else:
            result = subprocess.run(cmd, timeout=timeout)
            return result.returncode == 0, "", ""
    except subprocess.TimeoutExpired:
        return False, "", f"Timeout after {timeout} seconds"
    except Exception as e:
        return False, "", str(e)

def check_java_process(process_name: str) -> Tuple[bool, Optional[int]]:
    """Java 프로세스 확인 (jps 사용)"""
    success, stdout, _ = run_command(["jps"])
    if not success:
        return False, None

    for line in stdout.strip().split('\n'):
        if process_name in line:
            pid = line.split()[0]
            return True, int(pid)

    return False, None

def check_python_process(script_name: str) -> Tuple[bool, List[int]]:
    """Python 프로세스 확인"""
    success, stdout, _ = run_command(["ps", "aux"])
    if not success:
        return False, []

    pids = []
    for line in stdout.strip().split('\n'):
        if script_name in line and 'grep' not in line:
            parts = line.split()
            if len(parts) > 1:
                try:
                    pids.append(int(parts[1]))
                except ValueError:
                    continue

    return len(pids) > 0, pids

def verify_kafka_broker(verbose: bool = False) -> bool:
    """Kafka 브로커 실행 확인"""
    print_section("1. Kafka 브로커 확인")

    running, pid = check_java_process("Kafka")

    if running:
        print_success(f"Kafka 브로커 실행 중 (PID: {pid})")

        # 포트 확인
        success, stdout, _ = run_command(["lsof", "-i", ":9092"])
        if success and "LISTEN" in stdout:
            print_success("Kafka 브로커가 9092 포트에서 수신 대기 중")
        else:
            print_warning("Kafka 브로커 포트 확인 실패")

        return True
    else:
        print_error("Kafka 브로커가 실행 중이 아닙니다")
        print_info("해결: Kafka 브로커를 시작하세요")
        return False

def verify_spider_processes(verbose: bool = False) -> bool:
    """Spider 프로세스 실행 확인"""
    print_section("2. Spider 프로세스 확인")

    # Spider 종류
    spiders = [
        "saveticker",
        "upbit_trends",
        "perplexity",
        "coinness",
        "cnn_fear_greed"
    ]

    all_running = True
    for spider in spiders:
        running, pids = check_python_process(f"spider_{spider}")
        if running:
            print_success(f"Spider '{spider}' 실행 중 (PID: {', '.join(map(str, pids))})")
        else:
            print_warning(f"Spider '{spider}' 실행 중이 아님")
            all_running = False

    if all_running:
        print_success("모든 Spider 프로세스 실행 중")
    else:
        print_warning("일부 Spider 프로세스가 실행 중이 아닙니다")
        print_info("일부 Spider는 선택적으로 실행됩니다")

    return True  # Spider는 필수가 아니므로 True 반환

def verify_kafka_consumer(verbose: bool = False) -> bool:
    """Kafka Consumer 프로세스 실행 확인"""
    print_section("3. Kafka Consumer 프로세스 확인")

    running, pids = check_python_process("kafka_consumer.py")

    if running:
        print_success(f"Kafka Consumer 실행 중 (PID: {', '.join(map(str, pids))})")

        # group_id 확인
        success, stdout, _ = run_command(["ps", "aux"])
        if success:
            for line in stdout.strip().split('\n'):
                if "kafka_consumer.py" in line and "--group-id" in line:
                    if "cointicker-consumer" in line:
                        print_success("Consumer Group ID: cointicker-consumer")
                    break

        return True
    else:
        print_error("Kafka Consumer가 실행 중이 아닙니다")
        print_info("해결: GUI에서 Kafka Consumer를 시작하세요")
        return False

def verify_kafka_topics(verbose: bool = False) -> bool:
    """Kafka 토픽 존재 및 메시지 확인"""
    print_section("4. Kafka 토픽 확인")

    # Kafka 설치 경로 찾기
    kafka_paths = [
        "/opt/homebrew/bin/kafka-topics",
        "/usr/local/bin/kafka-topics",
        "/opt/kafka/bin/kafka-topics.sh"
    ]

    kafka_topics_cmd = None
    for path in kafka_paths:
        if Path(path).exists():
            kafka_topics_cmd = path
            break

    if not kafka_topics_cmd:
        print_warning("kafka-topics 명령어를 찾을 수 없습니다")
        return False

    # 토픽 목록 조회
    success, stdout, stderr = run_command([
        kafka_topics_cmd,
        "--list",
        "--bootstrap-server",
        "localhost:9092"
    ])

    if not success:
        print_error(f"토픽 목록 조회 실패: {stderr}")
        return False

    topics = stdout.strip().split('\n')

    # 필수 토픽 확인
    required_topics = {
        "cointicker.raw.saveticker": False,
        "cointicker.raw.upbit_trends": False,
        "cointicker.raw.perplexity": False,
        "cointicker.consumer.status": False,
    }

    for topic in topics:
        if topic in required_topics:
            required_topics[topic] = True
            print_success(f"토픽 발견: {topic}")

    # 상태 토픽 메시지 확인
    if required_topics.get("cointicker.consumer.status", False):
        print_info("상태 토픽 메시지 확인 중...")

        # Kafka console consumer 경로
        kafka_console_consumer = kafka_topics_cmd.replace("kafka-topics", "kafka-console-consumer")

        if Path(kafka_console_consumer).exists():
            success, stdout, _ = run_command([
                kafka_console_consumer,
                "--bootstrap-server", "localhost:9092",
                "--topic", "cointicker.consumer.status",
                "--from-beginning",
                "--max-messages", "1",
                "--timeout-ms", "3000"
            ], timeout=5)

            if success and stdout.strip():
                try:
                    message = json.loads(stdout.strip().split('\n')[0])
                    print_success(f"상태 메시지 수신: {message.get('processed_count', 0)}개 처리됨")
                    if verbose:
                        print(f"  상세: {json.dumps(message, indent=2, ensure_ascii=False)}")
                except json.JSONDecodeError:
                    print_warning("상태 메시지 파싱 실패")

    # 데이터 토픽 메시지 확인
    data_topics = [t for t in required_topics.keys() if t.startswith("cointicker.raw.")]
    for topic in data_topics:
        if required_topics.get(topic, False):
            print_info(f"토픽 '{topic}' 메시지 확인 중...")

            kafka_console_consumer = kafka_topics_cmd.replace("kafka-topics", "kafka-console-consumer")
            if Path(kafka_console_consumer).exists():
                success, stdout, _ = run_command([
                    kafka_console_consumer,
                    "--bootstrap-server", "localhost:9092",
                    "--topic", topic,
                    "--from-beginning",
                    "--max-messages", "1",
                    "--timeout-ms", "3000"
                ], timeout=5)

                if success and stdout.strip():
                    print_success(f"토픽 '{topic}'에 메시지 존재")
                else:
                    print_warning(f"토픽 '{topic}'에 메시지 없음 (Spider가 데이터를 수집하지 않았을 수 있음)")

    missing_topics = [t for t, exists in required_topics.items() if not exists]
    if missing_topics:
        print_warning(f"누락된 토픽: {', '.join(missing_topics)}")
        print_info("Spider가 데이터를 수집하면 자동으로 생성됩니다")

    return len([t for t in required_topics.values() if t]) > 0

def verify_hdfs_data(verbose: bool = False, skip_hdfs: bool = False) -> bool:
    """HDFS 데이터 저장 확인"""
    print_section("5. HDFS 데이터 저장 확인")

    if skip_hdfs:
        print_info("HDFS 검증 건너뜀 (--skip-hdfs 옵션)")
        return True

    # HDFS 명령어 경로 찾기
    hdfs_paths = [
        "/Users/juns/code/personal/notion/pknu_workspace/bigdata/hadoop_project/hadoop-3.4.1/bin/hdfs",
        "/opt/hadoop/bin/hdfs",
        "/usr/local/hadoop/bin/hdfs"
    ]

    hdfs_cmd = None
    for path in hdfs_paths:
        if Path(path).exists():
            hdfs_cmd = path
            break

    if not hdfs_cmd:
        print_warning("HDFS 명령어를 찾을 수 없습니다")
        return False

    # HDFS 데이터 디렉토리 확인
    today = datetime.now().strftime("%Y%m%d")
    hdfs_paths_to_check = [
        f"/raw/saveticker/{today}",
        f"/raw/upbit_trends/{today}",
        f"/raw/perplexity/{today}",
    ]

    any_data_found = False
    for hdfs_path in hdfs_paths_to_check:
        success, stdout, stderr = run_command([
            hdfs_cmd, "dfs", "-ls", hdfs_path
        ], timeout=10)

        if success and stdout.strip():
            # 파일 개수 세기
            file_count = len([l for l in stdout.strip().split('\n') if l.startswith('-')])
            print_success(f"HDFS 경로 '{hdfs_path}': {file_count}개 파일")
            any_data_found = True

            if verbose:
                print(f"  {stdout.strip()}")
        else:
            print_info(f"HDFS 경로 '{hdfs_path}': 데이터 없음")

    if any_data_found:
        print_success("HDFS에 데이터 저장 확인됨")
        return True
    else:
        print_warning("HDFS에 오늘 날짜의 데이터가 없습니다")
        print_info("Consumer가 메시지를 처리하면 HDFS에 저장됩니다")
        return False

def verify_gui_services(verbose: bool = False) -> bool:
    """GUI 서비스 실행 확인"""
    print_section("6. GUI 서비스 확인")

    # GUI 프로세스 확인
    running, pids = check_python_process("gui/main.py")
    if running:
        print_success(f"GUI 프로세스 실행 중 (PID: {', '.join(map(str, pids))})")
    else:
        print_warning("GUI 프로세스 실행 중이 아님")
        return False

    # Backend 확인
    success, stdout, _ = run_command(["lsof", "-i", ":5011"])
    if success and "LISTEN" in stdout:
        print_success("Backend API 서버 실행 중 (포트: 5011)")
    else:
        # 5005 포트도 확인
        success, stdout, _ = run_command(["lsof", "-i", ":5005"])
        if success and "LISTEN" in stdout:
            print_success("Backend API 서버 실행 중 (포트: 5005)")
        else:
            print_warning("Backend API 서버를 찾을 수 없습니다")

    # Frontend 확인
    success, stdout, _ = run_command(["lsof", "-i", ":3000"])
    if success and "LISTEN" in stdout:
        print_success("Frontend 웹 서버 실행 중 (포트: 3000)")
    else:
        # 3001 포트도 확인
        success, stdout, _ = run_command(["lsof", "-i", ":3001"])
        if success and "LISTEN" in stdout:
            print_success("Frontend 웹 서버 실행 중 (포트: 3001)")
        else:
            print_warning("Frontend 웹 서버를 찾을 수 없습니다")

    return True

def print_summary(results: Dict[str, bool]):
    """검증 결과 요약 출력"""
    print_header("검증 결과 요약")

    total = len(results)
    passed = sum(results.values())
    failed = total - passed

    print(f"\n{Colors.BOLD}총 검증 항목: {total}{Colors.END}")
    print(f"{Colors.GREEN}✅ 통과: {passed}{Colors.END}")
    print(f"{Colors.RED}❌ 실패: {failed}{Colors.END}\n")

    print(f"{Colors.BOLD}상세 결과:{Colors.END}")
    for name, result in results.items():
        status = f"{Colors.GREEN}✅ 통과{Colors.END}" if result else f"{Colors.RED}❌ 실패{Colors.END}"
        print(f"  {name}: {status}")

    # 종합 판정
    print()
    if failed == 0:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 모든 검증 항목 통과! 데이터 파이프라인이 정상 동작 중입니다.{Colors.END}")
        return 0
    elif passed >= total * 0.7:  # 70% 이상 통과
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠️  일부 항목 실패. 파이프라인이 부분적으로 동작 중입니다.{Colors.END}")
        return 1
    else:
        print(f"{Colors.RED}{Colors.BOLD}❌ 파이프라인에 심각한 문제가 있습니다. 로그를 확인하세요.{Colors.END}")
        return 2

def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description="PICU 데이터 파이프라인 검증 스크립트",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예제:
  %(prog)s                    # 기본 검증
  %(prog)s --verbose          # 상세 출력
  %(prog)s --wait-time 10     # 검증 간 10초 대기
  %(prog)s --skip-hdfs        # HDFS 검증 건너뛰기
        """
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="상세한 출력 표시"
    )
    parser.add_argument(
        "--wait-time", "-w",
        type=int,
        default=0,
        help="각 검증 단계 간 대기 시간 (초, 기본값: 0)"
    )
    parser.add_argument(
        "--skip-hdfs",
        action="store_true",
        help="HDFS 검증 건너뛰기"
    )

    args = parser.parse_args()

    print_header("PICU 데이터 파이프라인 검증")
    print(f"{Colors.CYAN}검증 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}\n")

    # 검증 실행
    results = {}

    # 1. Kafka 브로커
    results["Kafka 브로커"] = verify_kafka_broker(args.verbose)
    if args.wait_time > 0:
        time.sleep(args.wait_time)

    # 2. Spider 프로세스
    results["Spider 프로세스"] = verify_spider_processes(args.verbose)
    if args.wait_time > 0:
        time.sleep(args.wait_time)

    # 3. Kafka Consumer
    results["Kafka Consumer"] = verify_kafka_consumer(args.verbose)
    if args.wait_time > 0:
        time.sleep(args.wait_time)

    # 4. Kafka 토픽
    results["Kafka 토픽"] = verify_kafka_topics(args.verbose)
    if args.wait_time > 0:
        time.sleep(args.wait_time)

    # 5. HDFS 데이터
    results["HDFS 데이터"] = verify_hdfs_data(args.verbose, args.skip_hdfs)
    if args.wait_time > 0:
        time.sleep(args.wait_time)

    # 6. GUI 서비스
    results["GUI 서비스"] = verify_gui_services(args.verbose)

    # 결과 요약
    exit_code = print_summary(results)

    print(f"\n{Colors.CYAN}검증 종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}\n")

    return exit_code

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}검증이 사용자에 의해 중단되었습니다.{Colors.END}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.RED}예상치 못한 오류 발생: {e}{Colors.END}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
