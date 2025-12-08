"""
데이터 로더 서비스
HDFS에서 데이터를 가져와 MariaDB에 적재
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.models import RawNews, MarketTrends, FearGreedIndex
from shared.hdfs_client import HDFSClient

logger = logging.getLogger(__name__)


class DataLoader:
    """데이터 로더 클래스"""

    def __init__(self, db_session: Session, hdfs_client: HDFSClient):
        """
        초기화

        Args:
            db_session: 데이터베이스 세션
            hdfs_client: HDFS 클라이언트
        """
        self.db = db_session
        self.hdfs = hdfs_client

    def load_from_hdfs(self, date: Optional[datetime] = None) -> bool:
        """
        HDFS에서 정제된 데이터를 스트리밍으로 읽어 DB에 직접 적재 (임시 파일 없음)

        Args:
            date: 날짜 (None이면 오늘)

        Returns:
            성공 여부
        """
        if date is None:
            date = datetime.now()

        try:
            # HDFS 경로 조회
            hdfs_path = self.hdfs.get_cleaned_path(date)

            # HDFS에서 파일 목록 조회
            files = self.hdfs.list_files(hdfs_path)

            if not files:
                logger.warning(f"No files found in {hdfs_path}")
                return False

            # 각 파일을 HDFS에서 직접 스트리밍 처리 (임시 파일 없음)
            for file_path in files:
                if file_path.endswith(".json"):
                    content = self.hdfs.cat(file_path)
                    if content:
                        self._load_json_content(Path(file_path).name, content)

            return True

        except Exception as e:
            logger.error(f"Error loading data from HDFS: {e}")
            return False

    def _load_json_content(self, filename: str, content: str):
        """JSON 콘텐츠를 파싱하여 DB에 적재 (JSON Lines 형식 지원, 스트리밍)"""
        try:
            # 빈 내용 확인
            if not content or not content.strip():
                logger.warning(f"빈 내용 스킵: {filename}")
                return

            item_count = 0

            # JSON Lines 형식 처리 (각 줄이 하나의 JSON 객체)
            for line_num, line in enumerate(content.strip().split('\n'), 1):
                line = line.strip()
                if not line:
                    continue

                try:
                    data = json.loads(line)

                    # 빈 데이터 확인
                    if not data:
                        continue

                    # 데이터 타입별 처리
                    if isinstance(data, dict):
                        if "data" in data:
                            # 집계된 데이터 형식 (MapReduce 출력)
                            for item in data["data"]:
                                self._load_item(item)
                                item_count += 1
                        else:
                            # 단일 아이템
                            self._load_item(data)
                            item_count += 1
                    elif isinstance(data, list):
                        # 리스트 형식
                        for item in data:
                            self._load_item(item)
                            item_count += 1

                except json.JSONDecodeError as e:
                    logger.error(f"JSON 파싱 오류 {filename}:{line_num} - {e}")
                    continue

            logger.info(f"Loaded {filename}: {item_count}개 아이템 처리")

        except Exception as e:
            logger.error(f"콘텐츠 로드 오류 {filename}: {e}")

    def _load_json_file(self, file_path: Path):
        """JSON 파일을 파싱하여 DB에 적재 (JSON Lines 형식 지원)"""
        try:
            # 파일 크기 확인
            if file_path.stat().st_size == 0:
                logger.warning(f"빈 파일 스킵: {file_path.name}")
                return

            item_count = 0

            # JSON Lines 형식 처리 (각 줄이 하나의 JSON 객체)
            with open(file_path, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        data = json.loads(line)

                        # 빈 데이터 확인
                        if not data:
                            continue

                        # 데이터 타입별 처리
                        if isinstance(data, dict):
                            if "data" in data:
                                # 집계된 데이터 형식 (MapReduce 출력)
                                for item in data["data"]:
                                    self._load_item(item)
                                    item_count += 1
                            else:
                                # 단일 아이템
                                self._load_item(data)
                                item_count += 1
                        elif isinstance(data, list):
                            # 리스트 형식
                            for item in data:
                                self._load_item(item)
                                item_count += 1

                    except json.JSONDecodeError as e:
                        logger.error(f"JSON 파싱 오류 {file_path}:{line_num} - {e}")
                        continue

            logger.info(f"Loaded {file_path.name}: {item_count}개 아이템 처리")

        except Exception as e:
            logger.error(f"파일 로드 오류 {file_path}: {e}")

    def _load_item(self, item: Dict[str, Any]):
        """개별 아이템을 DB에 적재"""
        source = item.get("source", "").lower()

        if source in ["coinness", "perplexity"]:
            self._load_news(item)
        elif source in ["upbit", "saveticker"]:
            self._load_market_trend(item)
        elif source == "cnn_fear_greed":
            self._load_fear_greed(item)

    def _load_news(self, item: Dict[str, Any]):
        """뉴스 데이터 적재"""
        try:
            # 중복 체크
            url = item.get("url")
            if url:
                existing = self.db.query(RawNews).filter_by(url=url).first()
                if existing:
                    return

            news = RawNews(
                source=item.get("source"),
                title=item.get("title", ""),
                url=item.get("url"),
                content=item.get("content"),
                published_at=self._parse_datetime(item.get("published_at")),
                keywords=item.get("keywords", []),
                collected_at=datetime.now(),
            )

            self.db.add(news)
            self.db.commit()

        except Exception as e:
            logger.error(f"Error loading news: {e}")
            self.db.rollback()

    def _load_market_trend(self, item: Dict[str, Any]):
        """시장 트렌드 데이터 적재"""
        try:
            trend = MarketTrends(
                source=item.get("source"),
                symbol=item.get("symbol"),
                price=item.get("price"),
                volume_24h=item.get("volume_24h"),
                change_24h=item.get("change_24h"),
                timestamp=self._parse_datetime(item.get("timestamp")),
            )

            self.db.add(trend)
            self.db.commit()

        except Exception as e:
            logger.error(f"Error loading market trend: {e}")
            self.db.rollback()

    def _load_fear_greed(self, item: Dict[str, Any]):
        """공포·탐욕 지수 적재"""
        try:
            timestamp = self._parse_datetime(item.get("timestamp"))

            # 중복 체크 (같은 날짜)
            if timestamp:
                date_only = timestamp.date()
                existing = (
                    self.db.query(FearGreedIndex)
                    .filter(
                        FearGreedIndex.timestamp
                        >= datetime.combine(date_only, datetime.min.time()),
                        FearGreedIndex.timestamp
                        < datetime.combine(date_only, datetime.max.time()),
                    )
                    .first()
                )
                if existing:
                    return

            fgi = FearGreedIndex(
                value=item.get("value"),
                classification=item.get("classification"),
                timestamp=timestamp or datetime.now(),
            )

            self.db.add(fgi)
            self.db.commit()

        except Exception as e:
            logger.error(f"Error loading fear greed index: {e}")
            self.db.rollback()

    def _parse_datetime(self, dt_str: Any) -> datetime:
        """문자열을 datetime으로 변환"""
        if dt_str is None:
            return datetime.now()

        if isinstance(dt_str, datetime):
            return dt_str

        try:
            return datetime.fromisoformat(str(dt_str).replace("Z", "+00:00"))
        except:
            return datetime.now()
