"""
Scrapy Pipelines
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem

# 공통 라이브러리 import
import sys
from pathlib import Path as PathLib

# pipelines.py 위치: cointicker/worker-nodes/cointicker/pipelines.py
# shared 위치: cointicker/shared
current_file = PathLib(__file__).resolve()
project_root = (
    current_file.parent.parent.parent
)  # cointicker/worker-nodes/cointicker -> cointicker/worker-nodes -> cointicker
shared_path = project_root / "shared"
sys.path.insert(0, str(shared_path))

from shared.utils import (
    generate_hash,
    get_timestamp,
    get_date_path,
    clean_text,
    validate_json,
)
from shared.hdfs_client import HDFSClient
from shared.logger import setup_logger

logger = setup_logger(__name__)


class ValidationPipeline:
    """강화된 데이터 검증 파이프라인"""

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # 1. 필수 필드 검증
        if not adapter.get("source"):
            raise DropItem(f"Missing source in {item}")

        source = str(adapter.get("source")).strip()
        if not source or len(source) < 2:
            raise DropItem(f"Invalid source: {source}")

        # 2. timestamp 자동 설정
        if not adapter.get("timestamp"):
            adapter["timestamp"] = datetime.now().isoformat()
        else:
            # timestamp 형식 검증
            try:
                datetime.fromisoformat(
                    str(adapter.get("timestamp")).replace("Z", "+00:00")
                )
            except:
                adapter["timestamp"] = datetime.now().isoformat()

        # 3. 아이템 타입별 검증
        item_type = adapter.get("_item_type", self._detect_item_type(adapter))

        if item_type == "news":
            self._validate_news_item(adapter, spider)
        elif item_type == "market_trend":
            self._validate_market_trend_item(adapter, spider)
        elif item_type == "fear_greed":
            self._validate_fear_greed_item(adapter, spider)

        logger.debug(f"Validated {item_type} item from {adapter.get('source')}")
        return item

    def _detect_item_type(self, adapter):
        """아이템 타입 자동 감지"""
        if adapter.get("title") or adapter.get("content"):
            return "news"
        elif adapter.get("symbol") or adapter.get("price"):
            return "market_trend"
        elif adapter.get("value") is not None or adapter.get("classification"):
            return "fear_greed"
        return "unknown"

    def _validate_news_item(self, adapter, spider):
        """뉴스 아이템 검증"""
        # 제목 검증
        title = adapter.get("title")
        if not title:
            raise DropItem("Missing title in news item")

        title = str(title).strip()
        if len(title) < 5:
            raise DropItem(f"Title too short: {title[:50]}")

        if len(title) > 500:
            adapter["title"] = title[:500]
            logger.warning(f"Title truncated: {adapter.get('source')}")

        # URL 검증
        url = adapter.get("url")
        if url:
            url = str(url).strip()
            if not url.startswith(("http://", "https://")):
                logger.warning(f"Invalid URL format: {url}")
                adapter["url"] = None
            else:
                adapter["url"] = url

        # 본문 검증
        content = adapter.get("content")
        if content:
            content = str(content).strip()
            if len(content) < 10:
                logger.warning(f"Content too short: {len(content)} chars")
                adapter["content"] = None
            elif len(content) > 50000:
                adapter["content"] = content[:50000]
                logger.warning(f"Content truncated: {adapter.get('source')}")
            else:
                adapter["content"] = content

        # 키워드 검증
        keywords = adapter.get("keywords")
        if keywords:
            if isinstance(keywords, str):
                # 문자열을 리스트로 변환
                keywords = [k.strip() for k in keywords.split(",") if k.strip()]
            elif not isinstance(keywords, list):
                keywords = []

            # 빈 키워드 제거 및 최대 개수 제한
            keywords = [k for k in keywords if k and len(k) > 1][:20]
            adapter["keywords"] = keywords

        # published_at 검증
        published_at = adapter.get("published_at")
        if published_at:
            try:
                datetime.fromisoformat(str(published_at).replace("Z", "+00:00"))
            except:
                logger.warning(f"Invalid published_at format: {published_at}")
                adapter["published_at"] = None

    def _validate_market_trend_item(self, adapter, spider):
        """시장 트렌드 아이템 검증"""
        # 심볼 검증
        symbol = adapter.get("symbol")
        if not symbol:
            raise DropItem("Missing symbol in market trend item")

        symbol = str(symbol).strip().upper()
        if len(symbol) < 2 or len(symbol) > 10:
            raise DropItem(f"Invalid symbol: {symbol}")
        adapter["symbol"] = symbol

        # 가격 검증
        price = adapter.get("price")
        if price is not None:
            try:
                price_float = float(price)
                if price_float < 0:
                    raise DropItem(f"Invalid price: {price_float}")
                adapter["price"] = price_float
            except (ValueError, TypeError):
                raise DropItem(f"Invalid price type: {price}")

        # 거래량 검증
        volume = adapter.get("volume_24h")
        if volume is not None:
            try:
                volume = float(volume)
                if volume < 0:
                    adapter["volume_24h"] = None
                else:
                    adapter["volume_24h"] = volume
            except (ValueError, TypeError):
                adapter["volume_24h"] = None

    def _validate_fear_greed_item(self, adapter, spider):
        """공포·탐욕 지수 아이템 검증"""
        # 값 검증
        value = adapter.get("value")
        if value is None:
            raise DropItem("Missing value in fear greed item")

        try:
            value = int(value)
            if value < 0 or value > 100:
                raise DropItem(f"Invalid fear greed value: {value}")
            adapter["value"] = value
        except (ValueError, TypeError):
            raise DropItem(f"Invalid value type: {value}")

        # 분류 검증
        classification = adapter.get("classification")
        if classification:
            valid_classifications = [
                "Extreme Fear",
                "Fear",
                "Neutral",
                "Greed",
                "Extreme Greed",
            ]
            if classification not in valid_classifications:
                logger.warning(f"Invalid classification: {classification}")
                # 값 기반으로 자동 분류
                if value <= 20:
                    adapter["classification"] = "Extreme Fear"
                elif value <= 40:
                    adapter["classification"] = "Fear"
                elif value <= 60:
                    adapter["classification"] = "Neutral"
                elif value <= 80:
                    adapter["classification"] = "Greed"
                else:
                    adapter["classification"] = "Extreme Greed"


class DuplicatesPipeline:
    """강화된 중복 제거 파이프라인 (URL + 내용 기반)"""

    def __init__(self):
        self.seen_urls = set()
        self.seen_hashes = set()
        self.seen_content_hashes = set()  # 내용 기반 중복 체크

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # 1. URL 기준 중복 체크 (가장 빠른 방법)
        url = adapter.get("url")
        if url:
            url = str(url).strip()
            if url in self.seen_urls:
                raise DropItem(f"Duplicate URL found: {url}")
            self.seen_urls.add(url)

        # 2. 내용 기반 중복 체크 (제목 + 본문 해시)
        content_hash = self._generate_content_hash(adapter)
        if content_hash:
            if content_hash in self.seen_content_hashes:
                raise DropItem(
                    f"Duplicate content found: {adapter.get('title', '')[:50]}"
                )
            self.seen_content_hashes.add(content_hash)

        # 3. 해시 기준 중복 체크 (URL이 없는 경우, fallback)
        if not url and adapter.get("title"):
            title = adapter.get("title", "")
            item_hash = generate_hash(
                f"{adapter.get('source')}_{title}_{adapter.get('timestamp')}"
            )
            if item_hash in self.seen_hashes:
                raise DropItem(
                    f"Duplicate item found: {title[:50] if title else 'N/A'}"
                )
            self.seen_hashes.add(item_hash)

        return item

    def _generate_content_hash(self, adapter):
        """내용 기반 해시 생성"""
        title = adapter.get("title", "")
        content = adapter.get("content", "")
        source = adapter.get("source", "")

        if not title and not content:
            return None

        # 제목 + 본문 일부(처음 500자)로 해시 생성
        content_text = str(title).strip() if title else ""
        if content:
            # 본문의 처음 500자만 사용 (너무 긴 본문은 해시 생성 비용이 큼)
            content_preview = str(content)[:500].strip()
            if content_text:
                content_text += " " + content_preview
            else:
                content_text = content_preview

        if not content_text:
            return None

        # 소스도 포함하여 같은 내용이라도 다른 소스면 다른 것으로 간주
        content_text = f"{source}_{content_text}"

        # 해시 생성
        return generate_hash(content_text)


class HDFSPipeline:
    """HDFS 저장 파이프라인"""

    def __init__(self):
        self.hdfs_client = None
        self.items = []
        self.batch_size = 100  # 배치 크기

    def open_spider(self, spider):
        """Spider 시작 시 HDFS 클라이언트 초기화"""
        try:
            # 설정에서 HDFS 정보 가져오기
            namenode = spider.settings.get("HDFS_NAMENODE", "hdfs://localhost:9000")
            self.hdfs_client = HDFSClient(namenode=namenode)
            logger.info(f"HDFS Pipeline initialized for {spider.name}")
        except Exception as e:
            logger.error(f"Failed to initialize HDFS client: {e}")
            self.hdfs_client = None

    def close_spider(self, spider):
        """Spider 종료 시 배치 데이터 저장"""
        if self.items:
            self._save_batch(spider)
        logger.info(f"HDFS Pipeline closed for {spider.name}")

    def process_item(self, item, spider):
        """아이템 처리"""
        adapter = ItemAdapter(item)

        # 아이템을 딕셔너리로 변환
        item_dict = dict(adapter)

        # JSON 유효성 검사
        if not validate_json(item_dict):
            logger.warning(f"Invalid JSON item: {item}")
            return item

        self.items.append(item_dict)

        # 배치 크기 도달 시 저장
        if len(self.items) >= self.batch_size:
            self._save_batch(spider)
            self.items = []

        return item

    def _save_batch(self, spider):
        """배치 데이터를 HDFS에 저장"""
        if not self.hdfs_client or not self.items:
            return

        try:
            # 로컬 임시 파일에 저장
            timestamp = get_timestamp()
            source = self.items[0].get("source", "unknown")
            date_path = get_date_path("data/temp", datetime.now())
            date_path.mkdir(parents=True, exist_ok=True)

            local_file = date_path / f"{source}_{timestamp}.json"

            with open(local_file, "w", encoding="utf-8") as f:
                json.dump(self.items, f, ensure_ascii=False, indent=2)

            # HDFS 경로 생성
            hdfs_path = self.hdfs_client.get_raw_path(source, datetime.now())

            # HDFS 디렉토리 생성
            if not self.hdfs_client.exists(hdfs_path):
                self.hdfs_client.mkdir(hdfs_path)

            # HDFS에 업로드
            hdfs_file = f"{hdfs_path}/{local_file.name}"
            success = self.hdfs_client.put(str(local_file), hdfs_file)

            if success:
                logger.info(f"Saved {len(self.items)} items to HDFS: {hdfs_file}")
                # 로컬 임시 파일 삭제
                local_file.unlink()
            else:
                logger.error(f"Failed to save to HDFS: {hdfs_file}")

        except Exception as e:
            logger.error(f"Error saving batch to HDFS: {e}")
