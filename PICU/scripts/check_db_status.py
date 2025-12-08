#!/usr/bin/env python3
"""
데이터베이스 적재 상태 확인 스크립트 (고도화 버전)
테이블 구조, 데이터 샘플, 통계, 인덱스 등 종합 분석
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
    from sqlalchemy import func, desc, text, inspect
    from datetime import datetime, timedelta
    from collections import defaultdict
except ImportError as e:
    print(f"❌ 모듈 import 실패: {e}")
    print("가상환경을 활성화하거나 필요한 패키지를 설치하세요.")
    sys.exit(1)


def print_section(title, char="="):
    """섹션 제목 출력"""
    print()
    print(char * 100)
    print(f"  {title}")
    print(char * 100)
    print()


def print_subsection(title):
    """서브섹션 제목 출력"""
    print()
    print(f"📊 {title}")
    print("-" * 100)


def check_connection(db):
    """DB 연결 확인"""
    print_section("1. 데이터베이스 연결 상태", "=")

    try:
        db.execute(text("SELECT 1"))
        print("✅ 데이터베이스 연결 성공")

        # DB 설정 정보 출력
        try:
            from backend.config import (
                DATABASE_TYPE,
                DATABASE_HOST,
                DATABASE_PORT,
                DATABASE_NAME,
                DATABASE_USER,
            )

            print(f"\n🔧 현재 설정:")
            print(f"   타입      : {DATABASE_TYPE}")
            print(f"   호스트    : {DATABASE_HOST}")
            print(f"   포트      : {DATABASE_PORT}")
            print(f"   데이터베이스: {DATABASE_NAME}")
            print(f"   사용자    : {DATABASE_USER}")
        except:
            pass

        return True

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
        return False


def check_table_structures(db):
    """테이블 구조 확인"""
    print_section("2. 테이블 구조 및 스키마", "=")

    tables = {
        "raw_news": RawNews,
        "market_trends": MarketTrends,
        "fear_greed_index": FearGreedIndex,
        "sentiment_analysis": SentimentAnalysis,
        "technical_indicators": TechnicalIndicators,
        "crypto_insights": CryptoInsights,
    }

    inspector = inspect(db.bind)

    for table_name, model in tables.items():
        print_subsection(f"{table_name} 테이블")

        try:
            # 컬럼 정보
            columns = inspector.get_columns(table_name)
            print(f"\n{'컬럼명':<30} {'타입':<25} {'Nullable':<10} {'기본값'}")
            print("-" * 100)
            for col in columns:
                nullable = "Yes" if col['nullable'] else "No"
                default = col['default'] if col['default'] else ""
                print(f"{col['name']:<30} {str(col['type']):<25} {nullable:<10} {default}")

            # 인덱스 정보
            indexes = inspector.get_indexes(table_name)
            if indexes:
                print(f"\n📑 인덱스:")
                for idx in indexes:
                    cols = ", ".join(idx['column_names'])
                    unique = "UNIQUE" if idx['unique'] else "NON-UNIQUE"
                    print(f"   - {idx['name']}: ({cols}) [{unique}]")

            # Primary Key
            pk = inspector.get_pk_constraint(table_name)
            if pk and pk['constrained_columns']:
                print(f"\n🔑 Primary Key: {', '.join(pk['constrained_columns'])}")

        except Exception as e:
            print(f"❌ 구조 조회 실패: {e}")


def check_data_counts(db):
    """테이블별 데이터 개수 확인"""
    print_section("3. 테이블별 데이터 개수 및 통계", "=")

    tables = {
        "raw_news": RawNews,
        "market_trends": MarketTrends,
        "fear_greed_index": FearGreedIndex,
        "sentiment_analysis": SentimentAnalysis,
        "technical_indicators": TechnicalIndicators,
        "crypto_insights": CryptoInsights,
    }

    print(f"{'테이블명':<30} {'데이터 개수':>15} {'상태'}")
    print("-" * 100)

    total_count = 0
    table_stats = {}

    for table_name, model in tables.items():
        try:
            count = db.query(model).count()
            total_count += count
            table_stats[table_name] = count

            if count > 10000:
                status = "✅ 충분"
            elif count > 100:
                status = "✅ 양호"
            elif count > 0:
                status = "⚠️  적음"
            else:
                status = "❌ 없음"

            print(f"{table_name:<30} {count:>15,}개 {status}")
        except Exception as e:
            print(f"{table_name:<30} {'오류':>15} ❌")
            print(f"   → {e}")

    print("-" * 100)
    print(f"{'총 데이터 개수':<30} {total_count:>15,}개")

    return table_stats


def check_recent_data(db):
    """최근 적재된 데이터 확인"""
    print_section("4. 최근 적재 데이터 샘플", "=")

    # 최근 뉴스
    print_subsection("최근 뉴스 (raw_news)")
    try:
        recent_news = (
            db.query(RawNews).order_by(desc(RawNews.published_at)).limit(5).all()
        )
        if recent_news:
            for i, news in enumerate(recent_news, 1):
                print(f"\n{i}. {news.title[:80]}")
                print(f"   소스: {news.source} | URL: {news.url}")
                print(f"   발행: {news.published_at} | 수집: {news.collected_at}")
                if news.keywords:
                    keywords = news.keywords if isinstance(news.keywords, list) else []
                    print(f"   키워드: {', '.join(keywords[:5])}")
        else:
            print("⚠️  데이터 없음")
    except Exception as e:
        print(f"❌ 조회 오류: {e}")

    # 최근 시장 트렌드
    print_subsection("최근 시장 트렌드 (market_trends)")
    try:
        recent_trends = (
            db.query(MarketTrends)
            .order_by(desc(MarketTrends.timestamp))
            .limit(10)
            .all()
        )
        if recent_trends:
            print(f"\n{'심볼':<8} {'가격':>15} {'24h 거래량':>20} {'24h 변동':>12} {'시간'}")
            print("-" * 100)
            for trend in recent_trends:
                symbol = trend.symbol or "N/A"
                price = f"{trend.price:,.0f}" if trend.price else "N/A"
                volume = f"{trend.volume_24h:,.0f}" if trend.volume_24h else "N/A"
                change = f"{trend.change_24h:+.2f}%" if trend.change_24h else "N/A"
                timestamp = trend.timestamp.strftime("%Y-%m-%d %H:%M:%S") if trend.timestamp else "N/A"
                print(f"{symbol:<8} {price:>15} {volume:>20} {change:>12} {timestamp}")
        else:
            print("⚠️  데이터 없음")
    except Exception as e:
        print(f"❌ 조회 오류: {e}")

    # 최근 공포탐욕 지수
    print_subsection("최근 공포탐욕 지수 (fear_greed_index)")
    try:
        recent_fgi = (
            db.query(FearGreedIndex)
            .order_by(desc(FearGreedIndex.timestamp))
            .limit(5)
            .all()
        )
        if recent_fgi:
            print(f"\n{'값':>8} {'분류':<20} {'시간'}")
            print("-" * 100)
            for fgi in recent_fgi:
                value = fgi.value if fgi.value else "N/A"
                classification = fgi.classification or "N/A"
                timestamp = fgi.timestamp.strftime("%Y-%m-%d %H:%M:%S") if fgi.timestamp else "N/A"
                print(f"{value:>8} {classification:<20} {timestamp}")
        else:
            print("⚠️  데이터 없음")
    except Exception as e:
        print(f"❌ 조회 오류: {e}")

    # 감성 분석
    print_subsection("최근 감성 분석 (sentiment_analysis)")
    try:
        recent_sentiment = (
            db.query(SentimentAnalysis)
            .order_by(desc(SentimentAnalysis.analyzed_at))
            .limit(5)
            .all()
        )
        if recent_sentiment:
            print(f"\n{'뉴스ID':>8} {'감성점수':>12} {'분류':<15} {'분석시간'}")
            print("-" * 100)
            for sa in recent_sentiment:
                news_id = sa.news_id or "N/A"
                score = f"{sa.sentiment_score:.4f}" if sa.sentiment_score else "N/A"
                category = sa.sentiment_category or "N/A"
                analyzed = sa.analyzed_at.strftime("%Y-%m-%d %H:%M:%S") if sa.analyzed_at else "N/A"
                print(f"{news_id:>8} {score:>12} {category:<15} {analyzed}")
        else:
            print("⚠️  데이터 없음")
    except Exception as e:
        print(f"❌ 조회 오류: {e}")


def check_statistics(db):
    """통계 분석"""
    print_section("5. 데이터 통계 분석", "=")

    # 소스별 뉴스 개수
    print_subsection("소스별 뉴스 개수")
    try:
        source_counts = (
            db.query(RawNews.source, func.count(RawNews.id))
            .group_by(RawNews.source)
            .order_by(desc(func.count(RawNews.id)))
            .all()
        )
        if source_counts:
            print(f"\n{'소스':<20} {'개수':>15}")
            print("-" * 100)
            for source, count in source_counts:
                print(f"{source or 'Unknown':<20} {count:>15,}개")
        else:
            print("⚠️  데이터 없음")
    except Exception as e:
        print(f"❌ 조회 오류: {e}")

    # 심볼별 시장 트렌드 개수
    print_subsection("심볼별 시장 데이터 개수")
    try:
        symbol_counts = (
            db.query(MarketTrends.symbol, func.count(MarketTrends.id))
            .group_by(MarketTrends.symbol)
            .order_by(desc(func.count(MarketTrends.id)))
            .all()
        )
        if symbol_counts:
            print(f"\n{'심볼':<20} {'개수':>15}")
            print("-" * 100)
            for symbol, count in symbol_counts:
                print(f"{symbol or 'Unknown':<20} {count:>15,}개")
        else:
            print("⚠️  데이터 없음")
    except Exception as e:
        print(f"❌ 조회 오류: {e}")

    # 날짜별 통계 (최근 7일)
    print_subsection("날짜별 데이터 통계 (최근 7일)")
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

        # 시장 데이터 날짜별 개수
        market_by_date = (
            db.query(
                func.date(MarketTrends.timestamp).label("date"),
                func.count(MarketTrends.id).label("count"),
            )
            .filter(MarketTrends.timestamp >= seven_days_ago)
            .group_by(func.date(MarketTrends.timestamp))
            .order_by(desc("date"))
            .all()
        )

        print(f"\n{'날짜':<15} {'뉴스':>15} {'시장데이터':>15}")
        print("-" * 100)

        # 날짜별로 병합
        date_stats = defaultdict(lambda: {"news": 0, "market": 0})
        for date, count in news_by_date:
            date_stats[str(date)]["news"] = count
        for date, count in market_by_date:
            date_stats[str(date)]["market"] = count

        for date in sorted(date_stats.keys(), reverse=True):
            stats = date_stats[date]
            print(f"{date:<15} {stats['news']:>15,}개 {stats['market']:>15,}개")

        if not date_stats:
            print("⚠️  최근 7일간 데이터 없음")

    except Exception as e:
        print(f"❌ 날짜별 통계 조회 오류: {e}")


def check_data_quality(db):
    """데이터 품질 체크"""
    print_section("6. 데이터 품질 체크", "=")

    # NULL 값 체크
    print_subsection("NULL 값 체크")

    try:
        # raw_news 필수 필드 체크
        null_title = db.query(RawNews).filter(RawNews.title == None).count()
        null_url = db.query(RawNews).filter(RawNews.url == None).count()
        total_news = db.query(RawNews).count()

        print(f"\n📰 raw_news 테이블:")
        print(f"   전체: {total_news:,}개")
        print(f"   제목 NULL: {null_title:,}개 ({null_title/total_news*100:.1f}%)" if total_news > 0 else "   제목 NULL: 0개")
        print(f"   URL NULL: {null_url:,}개 ({null_url/total_news*100:.1f}%)" if total_news > 0 else "   URL NULL: 0개")

        # market_trends 필수 필드 체크
        null_symbol = db.query(MarketTrends).filter(MarketTrends.symbol == None).count()
        null_price = db.query(MarketTrends).filter(MarketTrends.price == None).count()
        total_market = db.query(MarketTrends).count()

        print(f"\n📈 market_trends 테이블:")
        print(f"   전체: {total_market:,}개")
        print(f"   심볼 NULL: {null_symbol:,}개 ({null_symbol/total_market*100:.1f}%)" if total_market > 0 else "   심볼 NULL: 0개")
        print(f"   가격 NULL: {null_price:,}개 ({null_price/total_market*100:.1f}%)" if total_market > 0 else "   가격 NULL: 0개")

    except Exception as e:
        print(f"❌ NULL 체크 오류: {e}")

    # 중복 데이터 체크
    print_subsection("중복 데이터 체크")
    try:
        # URL 기반 중복 뉴스
        duplicate_urls = (
            db.query(RawNews.url, func.count(RawNews.id))
            .group_by(RawNews.url)
            .having(func.count(RawNews.id) > 1)
            .count()
        )

        print(f"\n📰 중복 URL: {duplicate_urls:,}개")

    except Exception as e:
        print(f"❌ 중복 체크 오류: {e}")


def final_summary(table_stats):
    """종합 판정"""
    print_section("7. 종합 판정 및 권장사항", "=")

    total_count = sum(table_stats.values())

    print(f"📊 전체 데이터 개수: {total_count:,}개\n")

    if total_count == 0:
        print("❌ 데이터베이스에 데이터가 없습니다.")
        print()
        print("💡 권장사항:")
        print("   1. GUI에서 '데이터 적재' 버튼을 클릭하여 HDFS → DB 적재를 실행하세요")
        print("   2. 또는 CLI에서 실행: python3 scripts/run_pipeline.py")
        print("   3. 오케스트레이터를 실행하여 자동화: GUI 제어탭에서 '오케스트레이터 시작'")

    elif total_count < 100:
        print("⚠️  데이터가 매우 적습니다.")
        print()
        print("💡 권장사항:")
        print("   1. 파이프라인이 정상적으로 실행되고 있는지 확인하세요")
        print("   2. 크롤링 → MapReduce → DB 적재 과정에 오류가 없는지 로그를 확인하세요")
        print("   3. HDFS에 데이터가 정상적으로 저장되어 있는지 확인하세요:")
        print("      hdfs dfs -ls /raw/")
        print("      hdfs dfs -ls /cleaned/")

    else:
        print("✅ 데이터베이스가 정상적으로 작동하고 있습니다!")
        print()
        print("📈 데이터 현황:")
        for table_name, count in sorted(table_stats.items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                percentage = (count / total_count * 100)
                print(f"   {table_name:<30}: {count:>10,}개 ({percentage:>5.1f}%)")

        print()
        print("💡 권장사항:")
        print("   1. 정기적으로 데이터 품질을 모니터링하세요")
        print("   2. 오케스트레이터를 통해 자동화된 데이터 수집을 유지하세요")
        print("   3. 백업을 정기적으로 수행하세요")


def check_db_status():
    """DB 적재 상태 종합 확인"""
    print("\n" + "=" * 100)
    print(" " * 30 + "📊 데이터베이스 상태 종합 분석 📊")
    print("=" * 100)

    try:
        db = next(get_db())

        # 1. DB 연결 확인
        if not check_connection(db):
            return

        # 2. 테이블 구조 확인
        check_table_structures(db)

        # 3. 데이터 개수 확인
        table_stats = check_data_counts(db)

        # 4. 최근 데이터 샘플
        check_recent_data(db)

        # 5. 통계 분석
        check_statistics(db)

        # 6. 데이터 품질
        check_data_quality(db)

        # 7. 종합 판정
        final_summary(table_stats)

        print("\n" + "=" * 100)
        print(" " * 35 + "✅ 분석 완료!")
        print("=" * 100 + "\n")

        db.close()

    except Exception as e:
        print(f"\n❌ 오류 발생: {e}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    check_db_status()
