#!/usr/bin/env python3
"""
Scrapy 스파이더 실행 스크립트
다양한 형식으로 데이터를 추출할 수 있습니다.
"""

import subprocess
import sys
import os
from datetime import datetime


def run_spider(output_format="json", filename=None):
    """스파이더를 실행하고 결과를 지정된 형식으로 저장합니다."""

    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"quotes_{timestamp}.{output_format}"

    print(f"🕷️  Scrapy 스파이더 실행 중...")
    print(f"📄 출력 파일: {filename}")
    print(f"📊 출력 형식: {output_format.upper()}")

    # Scrapy 명령어 실행
    cmd = ["scrapy", "crawl", "mybot", "-o", filename]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ 스파이더 실행 완료!")
            print(f"📁 결과 파일: {filename}")

            # 파일 크기 확인
            if os.path.exists(filename):
                size = os.path.getsize(filename)
                print(f"📏 파일 크기: {size} bytes")
        else:
            print("❌ 스파이더 실행 실패:")
            print(result.stderr)

    except Exception as e:
        print(f"❌ 오류 발생: {e}")


if __name__ == "__main__":
    # 명령행 인수 처리
    format_arg = sys.argv[1] if len(sys.argv) > 1 else "json"
    filename_arg = sys.argv[2] if len(sys.argv) > 2 else None

    # 지원되는 형식 확인
    supported_formats = ["json", "csv", "xml", "jl"]

    if format_arg not in supported_formats:
        print(f"❌ 지원되지 않는 형식: {format_arg}")
        print(f"✅ 지원되는 형식: {', '.join(supported_formats)}")
        sys.exit(1)

    run_spider(format_arg, filename_arg)
