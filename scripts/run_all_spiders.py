#!/usr/bin/env python3
"""
🕷️ 모든 스파이더 실행 스크립트

이 스크립트는 프로젝트의 모든 스파이더를 순차적으로 실행하고
결과를 정리된 형태로 저장합니다.
"""

import subprocess
import os
import sys
import json
from datetime import datetime
from pathlib import Path


class SpiderRunner:
    """스파이더 실행 및 관리 클래스"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.scrapy_project = self.project_root / "scrapy_project"
        self.outputs_dir = self.scrapy_project / "outputs"

        # 출력 디렉토리 생성
        (self.outputs_dir / "json").mkdir(parents=True, exist_ok=True)
        (self.outputs_dir / "csv").mkdir(parents=True, exist_ok=True)
        (self.outputs_dir / "databases").mkdir(parents=True, exist_ok=True)

        # 실행 결과 저장
        self.results = []

    def get_available_spiders(self):
        """사용 가능한 스파이더 목록 조회"""
        try:
            os.chdir(self.scrapy_project)
            result = subprocess.run(
                ["scrapy", "list"], capture_output=True, text=True, check=True
            )
            spiders = result.stdout.strip().split("\n")
            return [spider.strip() for spider in spiders if spider.strip()]
        except subprocess.CalledProcessError as e:
            print(f"❌ 스파이더 목록 조회 실패: {e}")
            return []

    def run_spider(self, spider_name, output_format="json", delay=1):
        """개별 스파이더 실행"""
        print(f"\n🕷️ {spider_name} 스파이더를 실행합니다...")

        # 타임스탬프 추가
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"{spider_name}_{timestamp}.{output_format}"
        output_path = self.outputs_dir / output_format / output_file

        # Scrapy 명령어 구성
        cmd = [
            "scrapy",
            "crawl",
            spider_name,
            "-o",
            str(output_path),
            "-s",
            f"DOWNLOAD_DELAY={delay}",
            "-L",
            "INFO",
        ]

        try:
            # 실행 시작 시간
            start_time = datetime.now()

            # 스파이더 실행
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=True, cwd=self.scrapy_project
            )

            # 실행 완료 시간
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            # 결과 파일 크기 확인
            file_size = output_path.stat().st_size if output_path.exists() else 0

            # 수집된 아이템 수 계산 (JSON 파일인 경우)
            item_count = 0
            if output_format == "json" and output_path.exists():
                try:
                    with open(output_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        item_count = len(data) if isinstance(data, list) else 1
                except:
                    pass

            # 결과 저장
            spider_result = {
                "spider": spider_name,
                "status": "success",
                "duration": round(duration, 2),
                "output_file": str(output_path),
                "file_size": file_size,
                "item_count": item_count,
                "timestamp": start_time.isoformat(),
            }

            self.results.append(spider_result)

            print(f"✅ {spider_name} 완료!")
            print(f"   📊 수집 아이템: {item_count}개")
            print(f"   ⏱️ 실행 시간: {duration:.2f}초")
            print(f"   📁 출력 파일: {output_file}")

            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ {spider_name} 실행 실패:")
            print(f"   오류: {e}")

            spider_result = {
                "spider": spider_name,
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

            self.results.append(spider_result)
            return False

    def run_all_spiders(self):
        """모든 스파이더 실행"""
        print("🚀 모든 스파이더 실행을 시작합니다!")
        print("=" * 60)

        spiders = self.get_available_spiders()

        if not spiders:
            print("❌ 사용 가능한 스파이더가 없습니다.")
            return

        print(f"📋 실행할 스파이더: {len(spiders)}개")
        for spider in spiders:
            print(f"   • {spider}")

        # 각 스파이더별 설정
        spider_configs = {
            "quotes_spider": {"delay": 1, "format": "json"},
            "complex_quotes": {"delay": 1, "format": "json"},
            "useragent_spider": {"delay": 1, "format": "json"},
            "ethical_spider": {
                "delay": 2,
                "format": "json",
            },  # 윤리적 크롤링은 더 느리게
        }

        # 스파이더 실행
        successful = 0
        failed = 0

        for spider in spiders:
            config = spider_configs.get(spider, {"delay": 1, "format": "json"})

            if self.run_spider(spider, config["format"], config["delay"]):
                successful += 1
            else:
                failed += 1

        # 결과 요약
        self.print_summary(successful, failed)
        self.save_report()

    def print_summary(self, successful, failed):
        """실행 결과 요약 출력"""
        print("\n" + "=" * 60)
        print("📊 실행 결과 요약")
        print("=" * 60)

        total = successful + failed
        print(f"🎯 전체 스파이더: {total}개")
        print(f"✅ 성공: {successful}개")
        print(f"❌ 실패: {failed}개")

        if self.results:
            print("\n📋 개별 결과:")
            for result in self.results:
                status_icon = "✅" if result["status"] == "success" else "❌"
                spider_name = result["spider"]

                if result["status"] == "success":
                    print(
                        f"   {status_icon} {spider_name}: {result['item_count']}개 아이템, {result['duration']}초"
                    )
                else:
                    print(f"   {status_icon} {spider_name}: 실패")

    def save_report(self):
        """실행 보고서 저장"""
        report_file = self.outputs_dir / "execution_report.json"

        report = {
            "timestamp": datetime.now().isoformat(),
            "total_spiders": len(self.results),
            "successful": len([r for r in self.results if r["status"] == "success"]),
            "failed": len([r for r in self.results if r["status"] == "failed"]),
            "results": self.results,
        }

        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n📄 실행 보고서 저장: {report_file}")


def main():
    """메인 함수"""
    print("🕷️ Scrapy 전체 스파이더 실행기")
    print("=" * 60)

    runner = SpiderRunner()

    if len(sys.argv) > 1:
        # 특정 스파이더만 실행
        spider_name = sys.argv[1]
        print(f"🎯 특정 스파이더 실행: {spider_name}")
        runner.run_spider(spider_name)
    else:
        # 모든 스파이더 실행
        runner.run_all_spiders()

    print("\n🎉 스파이더 실행 완료!")


if __name__ == "__main__":
    main()
