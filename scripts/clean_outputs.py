#!/usr/bin/env python3
"""
🧹 출력 파일 정리 스크립트

이 스크립트는 크롤링 결과 파일들을 정리하고 관리합니다.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import argparse


class OutputCleaner:
    """출력 파일 정리 클래스"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.outputs_dir = self.project_root / "scrapy_project" / "outputs"

    def get_file_info(self, file_path):
        """파일 정보 조회"""
        stat = file_path.stat()
        return {
            "path": file_path,
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime),
            "created": datetime.fromtimestamp(stat.st_ctime),
        }

    def list_all_files(self):
        """모든 출력 파일 목록 조회"""
        files = []

        for subdir in ["json", "csv", "databases"]:
            subdir_path = self.outputs_dir / subdir
            if subdir_path.exists():
                for file_path in subdir_path.rglob("*"):
                    if file_path.is_file():
                        files.append(self.get_file_info(file_path))

        return sorted(files, key=lambda x: x["modified"], reverse=True)

    def clean_old_files(self, days=7):
        """오래된 파일 삭제"""
        print(f"🧹 {days}일 이전 파일들을 정리합니다...")

        cutoff_date = datetime.now() - timedelta(days=days)
        files = self.list_all_files()

        deleted_count = 0
        deleted_size = 0

        for file_info in files:
            if file_info["modified"] < cutoff_date:
                file_path = file_info["path"]
                file_size = file_info["size"]

                print(f"🗑️ 삭제: {file_path.name} ({self.format_size(file_size)})")
                file_path.unlink()

                deleted_count += 1
                deleted_size += file_size

        if deleted_count > 0:
            print(
                f"✅ {deleted_count}개 파일 삭제 완료 ({self.format_size(deleted_size)} 절약)"
            )
        else:
            print("✅ 삭제할 오래된 파일이 없습니다.")

    def clean_empty_files(self):
        """빈 파일 삭제"""
        print("🧹 빈 파일들을 정리합니다...")

        files = self.list_all_files()
        deleted_count = 0

        for file_info in files:
            if file_info["size"] == 0:
                file_path = file_info["path"]
                print(f"🗑️ 빈 파일 삭제: {file_path.name}")
                file_path.unlink()
                deleted_count += 1

        if deleted_count > 0:
            print(f"✅ {deleted_count}개 빈 파일 삭제 완료")
        else:
            print("✅ 삭제할 빈 파일이 없습니다.")

    def clean_duplicates(self):
        """중복 파일 삭제 (같은 크기와 수정 시간)"""
        print("🧹 중복 파일들을 정리합니다...")

        files = self.list_all_files()
        seen = {}
        deleted_count = 0

        for file_info in files:
            key = (file_info["size"], file_info["modified"].timestamp())

            if key in seen:
                # 중복 파일 발견
                file_path = file_info["path"]
                print(f"🗑️ 중복 파일 삭제: {file_path.name}")
                file_path.unlink()
                deleted_count += 1
            else:
                seen[key] = file_info

        if deleted_count > 0:
            print(f"✅ {deleted_count}개 중복 파일 삭제 완료")
        else:
            print("✅ 삭제할 중복 파일이 없습니다.")

    def show_statistics(self):
        """출력 파일 통계 표시"""
        print("📊 출력 파일 통계")
        print("=" * 50)

        files = self.list_all_files()

        if not files:
            print("📁 출력 파일이 없습니다.")
            return

        # 전체 통계
        total_files = len(files)
        total_size = sum(f["size"] for f in files)

        print(f"📁 전체 파일: {total_files}개")
        print(f"💾 전체 크기: {self.format_size(total_size)}")

        # 타입별 통계
        by_type = {}
        for file_info in files:
            file_type = file_info["path"].suffix.lower()
            if file_type not in by_type:
                by_type[file_type] = {"count": 0, "size": 0}
            by_type[file_type]["count"] += 1
            by_type[file_type]["size"] += file_info["size"]

        print("\n📋 파일 타입별 분석:")
        for file_type, stats in sorted(by_type.items()):
            print(
                f"   {file_type or '확장자 없음'}: {stats['count']}개, {self.format_size(stats['size'])}"
            )

        # 최신/오래된 파일
        if files:
            newest = max(files, key=lambda x: x["modified"])
            oldest = min(files, key=lambda x: x["modified"])

            print(
                f"\n📅 최신 파일: {newest['path'].name} ({newest['modified'].strftime('%Y-%m-%d %H:%M')})"
            )
            print(
                f"📅 오래된 파일: {oldest['path'].name} ({oldest['modified'].strftime('%Y-%m-%d %H:%M')})"
            )

    def backup_important_files(self, backup_dir="backup"):
        """중요한 파일들 백업"""
        backup_path = self.outputs_dir / backup_dir
        backup_path.mkdir(exist_ok=True)

        print(f"💾 중요한 파일들을 백업합니다... ({backup_path})")

        files = self.list_all_files()
        important_patterns = ["final", "result", "complete", "production"]

        backed_up = 0

        for file_info in files:
            file_name = file_info["path"].name.lower()

            # 중요한 패턴이 포함된 파일 확인
            if any(pattern in file_name for pattern in important_patterns):
                source = file_info["path"]
                destination = backup_path / source.name

                if not destination.exists():
                    shutil.copy2(source, destination)
                    print(f"💾 백업: {source.name}")
                    backed_up += 1

        if backed_up > 0:
            print(f"✅ {backed_up}개 파일 백업 완료")
        else:
            print("✅ 백업할 중요한 파일이 없습니다.")

    @staticmethod
    def format_size(size_bytes):
        """파일 크기를 읽기 쉬운 형태로 변환"""
        if size_bytes == 0:
            return "0B"

        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024.0

        return f"{size_bytes:.1f}TB"


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description="🧹 Scrapy 출력 파일 정리 도구")
    parser.add_argument(
        "--days", type=int, default=7, help="삭제할 파일의 기준 일수 (기본: 7일)"
    )
    parser.add_argument("--stats", action="store_true", help="파일 통계만 표시")
    parser.add_argument("--clean-old", action="store_true", help="오래된 파일 삭제")
    parser.add_argument("--clean-empty", action="store_true", help="빈 파일 삭제")
    parser.add_argument(
        "--clean-duplicates", action="store_true", help="중복 파일 삭제"
    )
    parser.add_argument("--backup", action="store_true", help="중요한 파일 백업")
    parser.add_argument("--all", action="store_true", help="모든 정리 작업 수행")

    args = parser.parse_args()

    cleaner = OutputCleaner()

    # 통계 표시
    if args.stats or not any(
        [args.clean_old, args.clean_empty, args.clean_duplicates, args.backup, args.all]
    ):
        cleaner.show_statistics()
        return

    print("🧹 Scrapy 출력 파일 정리 도구")
    print("=" * 50)

    # 백업 먼저 수행
    if args.backup or args.all:
        cleaner.backup_important_files()
        print()

    # 정리 작업 수행
    if args.clean_empty or args.all:
        cleaner.clean_empty_files()
        print()

    if args.clean_duplicates or args.all:
        cleaner.clean_duplicates()
        print()

    if args.clean_old or args.all:
        cleaner.clean_old_files(args.days)
        print()

    # 최종 통계
    print("📊 정리 후 통계:")
    cleaner.show_statistics()

    print("\n🎉 파일 정리 완료!")


if __name__ == "__main__":
    main()
