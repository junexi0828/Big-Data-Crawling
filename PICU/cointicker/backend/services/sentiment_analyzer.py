"""
감성 분석 서비스 (FinBERT)
"""

import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from backend.models import RawNews, SentimentAnalysis

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """감성 분석기 클래스"""

    def __init__(self, db_session: Session):
        """
        초기화

        Args:
            db_session: 데이터베이스 세션
        """
        self.db = db_session
        self.model = None
        self.tokenizer = None
        self._load_model()

    def _load_model(self):
        """FinBERT 모델 로드"""
        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            import torch

            model_name = 'ProsusAI/finbert'
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
            self.model.eval()

            logger.info("FinBERT model loaded successfully")

        except ImportError:
            logger.warning("transformers library not installed. Using mock analyzer.")
            self.model = None
        except Exception as e:
            logger.error(f"Error loading FinBERT model: {e}")
            self.model = None

    def analyze_news(self, news_id: int, text: str) -> Dict[str, Any]:
        """
        뉴스 텍스트 감성 분석

        Args:
            news_id: 뉴스 ID
            text: 분석할 텍스트

        Returns:
            감성 분석 결과
        """
        if not self.model:
            # Mock 분석 (모델이 없을 때)
            return {
                'news_id': news_id,
                'sentiment_score': 0.0,
                'sentiment_label': 'neutral',
                'confidence': 0.5
            }

        try:
            import torch

            # 텍스트 토크나이징
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=512
            )

            # 감성 분석
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probabilities = torch.softmax(logits, dim=1)

            # 결과 파싱
            sentiment_map = {0: 'positive', 1: 'negative', 2: 'neutral'}
            predicted_class = torch.argmax(probabilities, dim=1).item()
            confidence = probabilities[0][predicted_class].item()

            # 점수 계산 (-1.0 ~ 1.0)
            if sentiment_map[predicted_class] == 'positive':
                score = confidence
            elif sentiment_map[predicted_class] == 'negative':
                score = -confidence
            else:
                score = 0.0

            return {
                'news_id': news_id,
                'sentiment_score': round(score, 2),
                'sentiment_label': sentiment_map[predicted_class],
                'confidence': round(confidence, 2)
            }

        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {
                'news_id': news_id,
                'sentiment_score': 0.0,
                'sentiment_label': 'neutral',
                'confidence': 0.0
            }

    def batch_analyze(self, limit: int = 100) -> int:
        """
        미분석 뉴스 배치 처리

        Args:
            limit: 처리할 최대 개수

        Returns:
            처리된 개수
        """
        try:
            # 미분석 뉴스 조회
            news_list = self.db.query(RawNews).outerjoin(
                SentimentAnalysis, RawNews.id == SentimentAnalysis.news_id
            ).filter(SentimentAnalysis.id == None).limit(limit).all()

            count = 0
            for news in news_list:
                # 제목과 본문 결합
                text = f"{news.title} {news.content or ''}"

                # 감성 분석
                result = self.analyze_news(news.id, text)

                # 결과 저장
                sentiment = SentimentAnalysis(
                    news_id=result['news_id'],
                    sentiment_score=result['sentiment_score'],
                    sentiment_label=result['sentiment_label'],
                    confidence=result['confidence']
                )

                self.db.add(sentiment)
                count += 1

            self.db.commit()
            logger.info(f"Analyzed {count} news articles")
            return count

        except Exception as e:
            logger.error(f"Error in batch analysis: {e}")
            self.db.rollback()
            return 0

