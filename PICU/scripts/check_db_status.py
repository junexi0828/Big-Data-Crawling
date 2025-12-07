#!/usr/bin/env python3
"""
데이터베이스 적재 상태 확인 스크립트
"""

import sys
from pathlib import Path

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent
cointicker_root = project_root / "cointicker"
sys.path.insert(0, str(cointicker_root))
sys.path.insert(0, str(cointicker_root / "shared"))

try:
    from shared.path_utils import setup_pythonpath

    setup_pythonpath()
except ImportError:
    pass

try:
    from backend.config import get_db
    from backend.models import (
        RawNews,
        MarketTrends,
        FearGreedIndex,
        SentimentAnalysis,
        TechnicalIndicators,
        CryptoInsights,
    )
    from sqlalchemy import func, desc, text
    from datetime import datetime, timedelta
except ImportError as e:
    print(f"❌ 모듈 import 실패: {e}")
    print("가상환경을 활성화하거나 필요한 패키지를 설치하세요.")
    sys.exit(1)


def check_db_status():
    """DB 적재 상태 확인"""
    print("=" * 80)
    print("데이터베이스 적재 상태 확인")
    print("=" * 80)
    print()

    try:
        db = next(get_db())

        # 1. DB 연결 확인
        print("1. 데이터베이스 연결 상태")
        print("-" * 80)
        try:
            db.execute(text("SELECT 1"))
            print("✅ 데이터베이스 연결 성공")
        except Exception as e:
            print(f"❌ 데이터베이스 연결 실패: {e}")
            print()

            # 현재 DB 설정 확인
            try:
                from backend.config import (
                    DATABASE_TYPE,
                    DATABASE_HOST,
                    DATABASE_PORT,
                    DATABASE_NAME,
                    DATABASE_USER,
                )

                print(f"현재 설정:")
                print(f"  - 타입: {DATABASE_TYPE}")
                print(f"  - 호스트: {DATABASE_HOST}")
                print(f"  - 포트: {DATABASE_PORT}")
                print(f"  - 데이터베이스: {DATABASE_NAME}")
                print(f"  - 사용자: {DATABASE_USER}")
                print()
            except:
                pass

            print("해결 방법:")
            if DATABASE_TYPE == "postgresql":
                print("  1. PostgreSQL 서버가 실행 중인지 확인:")
                print("     - macOS: brew services start postgresql")
                print("     - Linux: sudo systemctl start postgresql")
                print("     - 또는: pg_ctl -D /usr/local/var/postgres start")
            else:
                print("  1. MariaDB/MySQL 서버가 실행 중인지 확인:")
                print("     - macOS: brew services start mariadb")
                print("     - Linux: sudo systemctl start mariadb")
            print("  2. 데이터베이스 설정 확인:")
            print("     - PICU/cointicker/config/database_config.yaml")
            print("     - 또는 환경 변수 설정 (DATABASE_TYPE=postgresql)")
            print("  3. SQLite 사용 (개발/테스트):")
            print("     - USE_SQLITE=true 환경 변수 설정")
            return
        print()

        # 2. 각 테이블 데이터 개수 확인
        print("2. 테이블별 데이터 개수")
        print("-" * 80)

        tables = {
            "raw_news": RawNews,
            "market_trends": MarketTrends,
            "fear_greed_index": FearGreedIndex,
            "sentiment_analysis": SentimentAnalysis,
            "technical_indicators": TechnicalIndicators,
            "crypto_insights": CryptoInsights,
        }

        total_count = 0
        for table_name, model in tables.items():
            try:
                count = db.query(model).count()
                total_count += count
                status = "✅" if count > 0 else "⚠️ "
                print(f"{status} {table_name:25s}: {count:6d}개")
            except Exception as e:
                print(f"❌ {table_name:25s}: 오류 - {e}")

        print(f"\n총 데이터 개수: {total_count}개")
        print()

        # 3. 최근 데이터 확인
        print("3. 최근 적재된 데이터")
        print("-" * 80)

        # 최근 뉴스
        try:
            recent_news = (
                db.query(RawNews).order_by(desc(RawNews.published_at)).limit(3).all()
            )
            if recent_news:
                print(f"✅ 최근 뉴스 ({len(recent_news)}개):")
                for news in recent_news:
                    print(f"   - {news.title[:50]}... ({news.published_at})")
            else:
                print("⚠️  최근 뉴스 없음")
        except Exception as e:
            print(f"❌ 뉴스 조회 오류: {e}")
        print()

        # 최근 시장 트렌드
        try:
            recent_trends = (
                db.query(MarketTrends)
                .order_by(desc(MarketTrends.timestamp))
                .limit(3)
                .all()
            )
            if recent_trends:
                print(f"✅ 최근 시장 트렌드 ({len(recent_trends)}개):")
                for trend in recent_trends:
                    print(
                        f"   - {trend.symbol}: 가격 {trend.price}, 거래량 {trend.volume_24h} ({trend.timestamp})"
                    )
            else:
                print("⚠️  최근 시장 트렌드 없음")
        except Exception as e:
            print(f"❌ 시장 트렌드 조회 오류: {e}")
        print()

        # 최근 공포탐욕 지수
        try:
            recent_fgi = (
                db.query(FearGreedIndex)
                .order_by(desc(FearGreedIndex.timestamp))
                .limit(3)
                .all()
            )
            if recent_fgi:
                print(f"✅ 최근 공포탐욕 지수 ({len(recent_fgi)}개):")
                for fgi in recent_fgi:
                    print(
                        f"   - 값: {fgi.value}, 분류: {fgi.classification} ({fgi.timestamp})"
                    )
            else:
                print("⚠️  최근 공포탐욕 지수 없음")
        except Exception as e:
            print(f"❌ 공포탐욕 지수 조회 오류: {e}")
        print()

        # 4. 날짜별 통계
        print("4. 날짜별 데이터 통계 (최근 7일)")
        print("-" * 80)

        try:
            seven_days_ago = datetime.now() - timedelta(days=7)

            # 뉴스 날짜별 개수
            news_by_date = (
                db.query(
                    func.date(RawNews.published_at).label("date"),
                    func.count(RawNews.id).label("count"),
                )
                .filter(RawNews.published_at >= seven_days_ago)
                .group_by(func.date(RawNews.published_at))
                .order_by(desc("date"))
                .all()
            )

            if news_by_date:
                print("뉴스 데이터:")
                for date, count in news_by_date:
                    print(f"   {date}: {count}개")
            else:
                print("⚠️  최근 7일간 뉴스 데이터 없음")
        except Exception as e:
            print(f"❌ 날짜별 통계 조회 오류: {e}")
        print()

        # 5. 종합 판정
        print("5. 종합 판정")
        print("-" * 80)

        if total_count == 0:
            print("❌ 데이터베이스에 데이터가 없습니다.")
            print(
                "   → HDFS → DB 적재를 실행하세요 (GUI에서 'HDFS → DB 적재 실행' 버튼 클릭)"
            )
        elif total_count < 10:
            print("⚠️  데이터가 매우 적습니다. 파이프라인 실행을 확인하세요.")
        else:
            print(
                f"✅ 데이터베이스에 {total_count}개의 데이터가 정상적으로 적재되어 있습니다."
            )

        db.close()

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    check_db_status()
