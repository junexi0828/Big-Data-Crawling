"""
대시보드 API 라우트
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, text
from datetime import datetime, timedelta
from typing import List, Optional

from backend.models import (
    RawNews, SentimentAnalysis, MarketTrends,
    FearGreedIndex, CryptoInsights
)
from backend.config import get_db

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary")
async def get_summary(db: Session = Depends(get_db)):
    """대시보드 요약 정보"""
    try:
        # 공포·탐욕 지수 (최신)
        fgi = None
        try:
            fgi = db.query(FearGreedIndex).order_by(desc(FearGreedIndex.timestamp)).first()
        except Exception as e:
            # 테이블이 없거나 데이터가 없는 경우 기본값 사용
            pass

        # 최근 24시간 감성 평균
        sentiment_avg = None
        try:
            day_ago = datetime.now() - timedelta(hours=24)
            sentiment_avg = db.query(func.avg(SentimentAnalysis.sentiment_score)).join(
                RawNews, SentimentAnalysis.news_id == RawNews.id
            ).filter(RawNews.published_at >= day_ago).scalar()
        except Exception as e:
            # 테이블이 없거나 데이터가 없는 경우 기본값 사용
            pass

        # 거래량 Top 5
        top_volume = []
        try:
            top_volume = db.query(MarketTrends).order_by(
                desc(MarketTrends.volume_24h)
            ).limit(5).all()
        except Exception as e:
            # 테이블이 없거나 데이터가 없는 경우 빈 리스트 사용
            pass

        # 최신 인사이트
        latest_insights = []
        try:
            latest_insights = db.query(CryptoInsights).order_by(
                desc(CryptoInsights.created_at)
            ).limit(10).all()
        except Exception as e:
            # 테이블이 없거나 데이터가 없는 경우 빈 리스트 사용
            pass

        return {
            "fear_greed_index": {
                "value": fgi.value if fgi else 50,
                "classification": fgi.classification if fgi else "Neutral"
            },
            "sentiment_average": round(sentiment_avg, 2) if sentiment_avg else 0.0,
            "top_volume_coins": [
                {
                    "symbol": t.symbol,
                    "volume_24h": t.volume_24h,
                    "change_24h": t.change_24h
                }
                for t in top_volume
            ],
            "latest_insights": [
                {
                    "type": i.insight_type,
                    "symbol": i.symbol,
                    "description": i.description,
                    "severity": i.severity
                }
                for i in latest_insights
            ]
        }

    except Exception as e:
        # 예상치 못한 오류 발생 시 상세 정보 반환
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sentiment-timeline")
async def get_sentiment_timeline(
    hours: Optional[int] = Query(None, ge=1, le=720),
    days: Optional[int] = Query(None, ge=1, le=30),
    db: Session = Depends(get_db)
):
    """감성 추이 데이터"""
    try:
        # days 파라미터가 있으면 hours로 변환
        if days is not None:
            hours = days * 24

        start_time = datetime.now() - timedelta(hours=hours)

        # 데이터베이스 타입 확인
        from backend.config import DATABASE_TYPE

        # DB 타입에 따라 다른 함수 사용
        if DATABASE_TYPE in ['mariadb', 'mysql']:
            # MySQL/MariaDB는 date_format 사용
            results = db.query(
                func.date_format(RawNews.published_at, '%Y-%m-%d %H:00:00').label('hour'),
                func.avg(SentimentAnalysis.sentiment_score).label('avg_sentiment'),
                func.count(RawNews.id).label('news_count')
            ).join(
                SentimentAnalysis, RawNews.id == SentimentAnalysis.news_id
            ).filter(
                RawNews.published_at >= start_time
            ).group_by('hour').order_by('hour').all()
        else:
            # PostgreSQL, SQLite 등은 strftime 또는 date_trunc 사용
            try:
                # PostgreSQL의 경우
                if DATABASE_TYPE == 'postgresql':
                    result_rows = db.execute(
                        text("""
                            SELECT
                                DATE_TRUNC('hour', raw_news.published_at) as hour,
                                AVG(sentiment_analysis.sentiment_score) as avg_sentiment,
                                COUNT(raw_news.id) as news_count
                            FROM raw_news
                            JOIN sentiment_analysis ON raw_news.id = sentiment_analysis.news_id
                            WHERE raw_news.published_at >= :start_time
                            GROUP BY hour
                            ORDER BY hour
                        """),
                        {"start_time": start_time}
                    ).fetchall()

                    # Row 객체를 dict로 변환
                    results = []
                    for row in result_rows:
                        results.append({
                            'hour': row.hour.strftime('%Y-%m-%d %H:00:00') if hasattr(row.hour, 'strftime') else str(row.hour),
                            'avg_sentiment': float(row.avg_sentiment) if row.avg_sentiment else 0.0,
                            'news_count': int(row.news_count) if row.news_count else 0
                        })
                else:
                    # SQLite의 경우
                    results = db.query(
                        func.strftime('%Y-%m-%d %H:00:00', RawNews.published_at).label('hour'),
                        func.avg(SentimentAnalysis.sentiment_score).label('avg_sentiment'),
                        func.count(RawNews.id).label('news_count')
                    ).join(
                        SentimentAnalysis, RawNews.id == SentimentAnalysis.news_id
                    ).filter(
                        RawNews.published_at >= start_time
                    ).group_by('hour').order_by('hour').all()
            except Exception as e:
                # 모든 방법이 실패하면 Python에서 처리
                all_news = db.query(
                    RawNews, SentimentAnalysis
                ).join(
                    SentimentAnalysis, RawNews.id == SentimentAnalysis.news_id
                ).filter(
                    RawNews.published_at >= start_time
                ).all()

                # 시간별로 그룹화
                from collections import defaultdict
                hourly_data = defaultdict(lambda: {'scores': [], 'count': 0})

                for news, sentiment in all_news:
                    if news.published_at:
                        hour_key = news.published_at.replace(minute=0, second=0, microsecond=0)
                        hourly_data[hour_key]['scores'].append(sentiment.sentiment_score)
                        hourly_data[hour_key]['count'] += 1

                results = []
                for hour_key in sorted(hourly_data.keys()):
                    data = hourly_data[hour_key]
                    avg_sentiment = sum(data['scores']) / len(data['scores']) if data['scores'] else 0
                    results.append({
                        'hour': hour_key.strftime('%Y-%m-%d %H:00:00'),
                        'avg_sentiment': avg_sentiment,
                        'news_count': data['count']
                    })

        # 결과 포맷팅
        timeline = []
        for row in results:
            if hasattr(row, 'hour'):
                hour_str = row.hour if isinstance(row.hour, str) else row.hour.strftime('%Y-%m-%d %H:00:00')
                timeline.append({
                    "timestamp": hour_str,
                    "sentiment": round(float(row.avg_sentiment), 2) if row.avg_sentiment else 0.0,
                    "count": int(row.news_count) if row.news_count else 0
                })
            else:
                # dict 형태인 경우
                timeline.append({
                    "timestamp": row.get('hour', ''),
                    "sentiment": round(float(row.get('avg_sentiment', 0)), 2),
                    "count": int(row.get('news_count', 0))
                })

        return {
            "timeline": timeline
        }

    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)

