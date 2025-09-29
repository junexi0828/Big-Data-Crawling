#!/usr/bin/env python3
"""
Duplication Filter 완전 데모 - 이미지 슬라이드의 3가지 방법 모두 구현
50 quotes out of 100 quotes 상황을 재현하고 해결책 제시
"""
import subprocess
import os


def demo_duplication_filter():
    """Duplication Filter 3가지 방법 데모"""
    print(
        "🎯 Duplication Filter 데모 - Spider complex_quotes scraped only 50 quotes out of 100 quotes!"
    )
    print("=" * 90)
    print("Some were not populated due to duplication filtering of author urls.")
    print()

    print("📋 이미지에서 보여준 3가지 해결 방법:")
    print()

    # 1. Global setting 방법
    print("1️⃣ Global setting: change settings.py file and run again")
    print(
        "   • Disable the duplicate filter altogether! ← be careful about crawling loop!"
    )
    print("   • 파일: tutorial/tutorial/settings.py")
    print("   • 코드: DUPEFILTER_CLASS = 'scrapy.dupefilters.BaseDupeFilter'")
    print()

    # 2. Command line option 방법
    print("2️⃣ Use command line option ← spider-wise (revoke global setting before!)")
    print("   • Explicitly override setting using the -s or --set command line option")
    print("   • 명령어:")
    print("     scrapy crawl complex_quotes --set")
    print("     DUPEFILTER_CLASS=scrapy.dupefilters.BaseDupeFilter")
    print()

    # 3. custom_settings 방법
    print("3️⃣ Add custom_settings block to your spider ← spider-wise!")
    print("   • Modify your spider and run")
    print("   • 코드:")
    print("     custom_settings = {")
    print("         'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',")
    print("     }")
    print()


def test_duplication_filter_methods():
    """각 방법들을 실제로 테스트"""
    print("🧪 실제 테스트 실행:")
    print("=" * 50)

    # 현재 디렉토리 확인
    base_dir = "/Users/juns/bigdata"
    tutorial_dir = os.path.join(base_dir, "tutorial")

    if not os.path.exists(tutorial_dir):
        print("❌ tutorial 디렉토리를 찾을 수 없습니다.")
        return

    print("1️⃣ 기본 상태에서 complex_quotes 실행 (중복 필터 활성화)")
    print("   명령어: scrapy crawl complex_quotes -o normal_result.json")
    print("   예상 결과: 50개 정도 수집 (중복 URL 필터링으로 인해)")
    print()

    print("2️⃣ Command line 옵션으로 중복 필터 비활성화")
    print(
        "   명령어: scrapy crawl complex_quotes --set DUPEFILTER_CLASS=scrapy.dupefilters.BaseDupeFilter -o no_filter_result.json"
    )
    print("   예상 결과: 100개 수집 (모든 명언 수집)")
    print()

    print("3️⃣ custom_settings가 적용된 상태에서 실행")
    print("   명령어: scrapy crawl complex_quotes -o custom_settings_result.json")
    print("   예상 결과: 100개 수집 (custom_settings 덕분에)")
    print()

    print("💡 실제 실행해보려면 다음 명령어들을 사용하세요:")
    print(f"   cd {tutorial_dir}")
    print("   scrapy crawl complex_quotes -o dupefilter_test.json")
    print(
        "   scrapy crawl complex_quotes --set DUPEFILTER_CLASS=scrapy.dupefilters.BaseDupeFilter -o no_dupefilter_test.json"
    )


def explain_duplication_filtering():
    """중복 필터링이 왜 발생하는지 설명"""
    print("\n🔍 왜 중복 필터링이 발생하나요?")
    print("=" * 50)
    print("• 여러 명언이 같은 작가의 것일 때")
    print("• 작가 상세 페이지 URL이 동일함")
    print("• Scrapy의 기본 중복 필터가 같은 URL 재방문을 차단")
    print("• 결과적으로 일부 작가 정보가 수집되지 않음")
    print()

    print("📊 이미지에서 보여준 상황:")
    print("• complex_quotes 스파이더가 50개만 수집 (100개 중)")
    print("• 'item_scraped_count': 50 (로그에서 확인 가능)")
    print("• 111 requests 전송했지만 일부는 중복으로 차단됨")
    print()

    print("⚠️ 주의사항:")
    print("• 중복 필터를 비활성화하면 무한 루프 위험")
    print("• crawling loop에 주의해야 함")
    print("• 신중하게 사용해야 함")


if __name__ == "__main__":
    print("🎯 Scrapy Duplication Filter 완전 데모")
    print("=" * 80)

    # 1. 기본 설명
    demo_duplication_filter()

    # 2. 테스트 방법
    test_duplication_filter_methods()

    # 3. 원리 설명
    explain_duplication_filtering()

    print("\n✅ Duplication Filter 데모 완료!")
    print("실제 테스트는 tutorial 디렉토리에서 위의 명령어들을 실행해보세요!")
