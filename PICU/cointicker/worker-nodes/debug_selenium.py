"""
Selenium을 사용하여 실제 웹사이트 구조 분석
"""

import sys
from pathlib import Path

# 공통 라이브러리 import
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
shared_path = project_root / "shared"
sys.path.insert(0, str(shared_path))

from shared.selenium_utils import (
    create_chrome_driver,
    wait_for_page_load,
    scroll_to_bottom,
    safe_quit_driver,
)
import time


def analyze_saveticker():
    """SaveTicker 페이지 구조 분석"""
    print("=" * 60)
    print("SaveTicker 페이지 구조 분석")
    print("=" * 60)

    driver = create_chrome_driver(headless=True, disable_blink=True)

    try:
        url = "https://www.saveticker.com/app/news"
        print(f"\n접속 중: {url}")
        driver.get(url)

        wait_for_page_load(driver, timeout=30)
        time.sleep(3)  # 추가 대기

        scroll_to_bottom(driver, pause_time=1.0)
        time.sleep(2)

        # HTML 구조 분석
        print("\n=== 페이지 제목 ===")
        print(driver.title)

        print("\n=== 링크 분석 ===")
        links = driver.find_elements("tag name", "a")
        print(f"전체 링크 수: {len(links)}")

        news_links = []
        for link in links[:50]:  # 처음 50개만
            href = link.get_attribute("href")
            text = link.text.strip()
            if href and any(
                x in href.lower()
                for x in ["news", "article", "post", "detail", "/app/"]
            ):
                news_links.append((href, text[:50]))

        print(f"\n뉴스 관련 링크: {len(news_links)}개")
        for i, (href, text) in enumerate(news_links[:10], 1):
            print(f"{i}. {text} -> {href}")

        print("\n=== 주요 요소 분석 ===")
        # 다양한 선택자 시도
        selectors = [
            "article",
            "[class*='news']",
            "[class*='article']",
            "[class*='post']",
            "[class*='item']",
            "[class*='card']",
            "[class*='list']",
        ]

        for selector in selectors:
            elements = driver.find_elements("css selector", selector)
            if elements:
                print(f"\n{selector}: {len(elements)}개 발견")
                if len(elements) > 0:
                    first = elements[0]
                    print(f"  첫 번째 요소 클래스: {first.get_attribute('class')}")
                    print(f"  첫 번째 요소 텍스트: {first.text[:100]}")

        # body 전체 텍스트 샘플
        print("\n=== 페이지 텍스트 샘플 (처음 500자) ===")
        body_text = driver.find_element("tag name", "body").text
        print(body_text[:500])

    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback

        traceback.print_exc()
    finally:
        safe_quit_driver(driver)


def analyze_perplexity():
    """Perplexity 페이지 구조 분석"""
    print("\n" + "=" * 60)
    print("Perplexity 페이지 구조 분석")
    print("=" * 60)

    driver = create_chrome_driver(headless=True, disable_blink=True)

    try:
        url = "https://www.perplexity.ai/search?q=cryptocurrency+market+analysis"
        print(f"\n접속 중: {url}")
        driver.get(url)

        wait_for_page_load(driver, timeout=30)
        time.sleep(5)  # Perplexity는 로딩 시간이 더 필요

        scroll_to_bottom(driver, pause_time=1.0)
        time.sleep(3)

        # HTML 구조 분석
        print("\n=== 페이지 제목 ===")
        print(driver.title)

        print("\n=== 주요 콘텐츠 영역 분석 ===")
        selectors = [
            "[class*='answer']",
            "[class*='summary']",
            "[class*='content']",
            "[class*='text']",
            "article",
            "main",
            "[class*='prose']",
        ]

        for selector in selectors:
            elements = driver.find_elements("css selector", selector)
            if elements:
                print(f"\n{selector}: {len(elements)}개 발견")
                if len(elements) > 0:
                    first = elements[0]
                    text = first.text[:200]
                    print(f"  첫 번째 요소 텍스트: {text}")

        # body 전체 텍스트 샘플
        print("\n=== 페이지 텍스트 샘플 (처음 1000자) ===")
        body_text = driver.find_element("tag name", "body").text
        print(body_text[:1000])

    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback

        traceback.print_exc()
    finally:
        safe_quit_driver(driver)


if __name__ == "__main__":
    analyze_saveticker()
    analyze_perplexity()
