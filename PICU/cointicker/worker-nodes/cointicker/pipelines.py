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
project_root = current_file.parent.parent.parent  # cointicker/worker-nodes/cointicker -> cointicker/worker-nodes -> cointicker
shared_path = project_root / "shared"
sys.path.insert(0, str(shared_path))

from shared.utils import generate_hash, get_timestamp, get_date_path, clean_text, validate_json
from shared.hdfs_client import HDFSClient
from shared.logger import setup_logger

logger = setup_logger(__name__)


class ValidationPipeline:
    """데이터 검증 파이프라인"""

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # 필수 필드 검증
        if not adapter.get('source'):
            raise DropItem(f"Missing source in {item}")

        if not adapter.get('timestamp'):
            adapter['timestamp'] = datetime.now().isoformat()

        # 텍스트 정제
        if adapter.get('title'):
            adapter['title'] = clean_text(adapter['title'])

        if adapter.get('content'):
            adapter['content'] = clean_text(adapter['content'])

        logger.debug(f"Validated item from {adapter.get('source')}")
        return item


class DuplicatesPipeline:
    """중복 제거 파이프라인"""

    def __init__(self):
        self.seen_urls = set()
        self.seen_hashes = set()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # URL 기준 중복 체크
        url = adapter.get('url')
        if url:
            if url in self.seen_urls:
                raise DropItem(f"Duplicate URL found: {url}")
            self.seen_urls.add(url)

        # 해시 기준 중복 체크 (URL이 없는 경우)
        if not url and adapter.get('title'):
            item_hash = generate_hash(f"{adapter.get('source')}_{adapter.get('title')}_{adapter.get('timestamp')}")
            if item_hash in self.seen_hashes:
                raise DropItem(f"Duplicate item found: {adapter.get('title')[:50]}")
            self.seen_hashes.add(item_hash)

        return item


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
            namenode = spider.settings.get('HDFS_NAMENODE', 'hdfs://localhost:9000')
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
            source = self.items[0].get('source', 'unknown')
            date_path = get_date_path('data/temp', datetime.now())
            date_path.mkdir(parents=True, exist_ok=True)

            local_file = date_path / f"{source}_{timestamp}.json"

            with open(local_file, 'w', encoding='utf-8') as f:
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

