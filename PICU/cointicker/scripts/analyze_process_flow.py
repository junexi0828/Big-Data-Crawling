#!/usr/bin/env python3
"""
프로세스 흐름 분석 스크립트
각 컴포넌트를 순서대로 실행하고 분석
"""
import sys
import os
import time
import subprocess
import json
from pathlib import Path
from datetime import datetime

# 프로젝트 루트 추가
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "cointicker"))

from shared.logger import setup_logger

logger = setup_logger(__name__)


def run_command(cmd: list, timeout: int = 30) -> dict:
    """명령어 실행"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "타임아웃"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def analyze_spider():
    """1. Spider 분석"""
    print("\n" + "=" * 60)
    print("1단계: Spider (Scrapy) 분석")
    print("=" * 60)

    worker_nodes = PROJECT_ROOT / "cointicker" / "worker-nodes"
    os.chdir(worker_nodes)

    result = run_command(["scrapy", "crawl", "upbit_trends", "-L", "INFO"], timeout=30)

    if result["success"]:
        output = result["stdout"]
        # 통계 추출
        items = 0
        errors = 0
        for line in output.split("\n"):
            if "item_scraped_count" in line.lower():
                items += 1
            if "error" in line.lower():
                errors += 1

        print(f"✅ Spider 실행 성공")
        print(f"  - 아이템 수집: {items}개")
        print(f"  - 에러: {errors}개")
        return {"success": True, "items": items, "errors": errors}
    else:
        print(f"❌ Spider 실행 실패: {result.get('error', result.get('stderr', ''))}")
        return {"success": False}


def analyze_kafka():
    """2. Kafka 분석"""
    print("\n" + "=" * 60)
    print("2단계: Kafka 분석")
    print("=" * 60)

    # Kafka 브로커 확인
    result = run_command(
        ["kafka-topics.sh", "--list", "--bootstrap-server", "localhost:9092"], timeout=5
    )

    if result["success"]:
        topics = [t.strip() for t in result["stdout"].split("\n") if t.strip()]
        print(f"✅ Kafka 브로커 연결 성공")
        print(f"  - 토픽 수: {len(topics)}")
        print(f"  - 토픽 목록: {', '.join(topics[:5])}")
        return {"success": True, "topics": topics}
    else:
        print(f"⚠️  Kafka 브로커 연결 실패 (Kafka가 설치되지 않았을 수 있음)")
        return {"success": False, "error": "Kafka 브로커 연결 실패"}


def analyze_hdfs():
    """3. HDFS 분석"""
    print("\n" + "=" * 60)
    print("3단계: HDFS 분석")
    print("=" * 60)

    result = run_command(["hdfs", "dfsadmin", "-report"], timeout=10)

    if result["success"]:
        print(f"✅ HDFS 연결 성공")
        print(f"  - 리포트 길이: {len(result['stdout'])} 문자")
        return {"success": True}
    else:
        print(f"⚠️  HDFS 연결 실패 (Hadoop이 설치되지 않았을 수 있음)")
        return {"success": False, "error": "HDFS 연결 실패"}


def analyze_backend():
    """4. Backend 분석"""
    print("\n" + "=" * 60)
    print("4단계: Backend (FastAPI) 분석")
    print("=" * 60)

    import requests

    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend 서버 실행 중")
            print(f"  - 상태: {data.get('status')}")
            print(f"  - 데이터베이스: {data.get('database')}")
            return {"success": True, "data": data}
        else:
            print(f"⚠️  Backend 서버 응답 오류: {response.status_code}")
            return {"success": False}
    except requests.exceptions.RequestException as e:
        print(f"⚠️  Backend 서버 연결 실패: {e}")
        print(f"  실행 방법: bash cointicker/backend/run_server.sh")
        return {"success": False, "error": str(e)}


def analyze_frontend():
    """5. Frontend 분석"""
    print("\n" + "=" * 60)
    print("5단계: Frontend (React) 분석")
    print("=" * 60)

    import requests

    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print(f"✅ Frontend 서버 실행 중")
            print(f"  - 상태 코드: {response.status_code}")
            return {"success": True}
        else:
            print(f"⚠️  Frontend 서버 응답 오류: {response.status_code}")
            return {"success": False}
    except requests.exceptions.RequestException as e:
        print(f"⚠️  Frontend 서버 연결 실패: {e}")
        print(f"  실행 방법: bash cointicker/frontend/run_dev.sh")
        return {"success": False, "error": str(e)}


def main():
    """메인 함수"""
    print("=" * 60)
    print("프로세스 흐름 분석 시작")
    print("=" * 60)
    print(f"시작 시간: {datetime.now().isoformat()}")

    results = {}

    # 각 단계 실행
    results["spider"] = analyze_spider()
    time.sleep(2)

    results["kafka"] = analyze_kafka()
    time.sleep(1)

    results["hdfs"] = analyze_hdfs()
    time.sleep(1)

    results["backend"] = analyze_backend()
    time.sleep(1)

    results["frontend"] = analyze_frontend()

    # 결과 요약
    print("\n" + "=" * 60)
    print("분석 결과 요약")
    print("=" * 60)

    for component, result in results.items():
        status = "✅ 성공" if result.get("success") else "❌ 실패"
        print(f"{component.upper()}: {status}")

    # 결과 저장
    output_file = (
        PROJECT_ROOT / "cointicker" / "tests" / "process_flow_results" / "analysis.json"
    )
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n결과 저장: {output_file}")
    print(f"종료 시간: {datetime.now().isoformat()}")


if __name__ == "__main__":
    main()
