# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import json
import sqlite3
import mariadb
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from scrapy.utils.project import get_project_settings


class TutorialPipeline:
    def process_item(self, item, spider):
        # 데이터 검증 및 정리
        if item.get("quote"):
            item["quote"] = item["quote"].strip()
        if item.get("author"):
            item["author"] = item["author"].strip()

        # 빈 값 체크
        if not item.get("quote") or not item.get("author"):
            spider.logger.warning(f"Missing data in item: {item}")

        return item


class QuotesValidationPipeline:
    """명언 데이터 검증 파이프라인"""

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # 필수 필드 검증
        if not adapter.get("quote_content"):
            raise DropItem(f"Missing quote_content in {item}")

        if not adapter.get("author_name"):
            raise DropItem(f"Missing author_name in {item}")

        # 데이터 정리
        if adapter.get("quote_content"):
            adapter["quote_content"] = adapter["quote_content"].strip()

        if adapter.get("author_name"):
            adapter["author_name"] = adapter["author_name"].strip()

        # 태그가 빈 리스트인 경우 처리
        if not adapter.get("tags"):
            adapter["tags"] = []

        spider.logger.info(f"Validated item: {adapter['author_name']}")
        return item


class DuplicatesPipeline:
    """중복 제거 파이프라인"""

    def __init__(self):
        self.seen_quotes = set()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        quote_content = adapter.get("quote_content", "").strip()

        if quote_content in self.seen_quotes:
            raise DropItem(f"Duplicate quote found: {quote_content[:50]}...")
        else:
            self.seen_quotes.add(quote_content)
            spider.logger.info(f"New quote added: {quote_content[:50]}...")
            return item


class JsonWriterPipeline:
    """JSON 파일 저장 파이프라인"""

    def open_spider(self, spider):
        self.file = open(f"{spider.name}_items.json", "w", encoding="utf-8")
        self.file.write("[\n")
        self.first_item = True

    def close_spider(self, spider):
        self.file.write("\n]")
        self.file.close()

    def process_item(self, item, spider):
        if not self.first_item:
            self.file.write(",\n")
        else:
            self.first_item = False

        line = json.dumps(ItemAdapter(item).asdict(), ensure_ascii=False, indent=2)
        self.file.write(line)
        return item


class SQLitePipeline:
    """SQLite 데이터베이스 저장 파이프라인"""

    def __init__(self):
        self.connection = None
        self.cursor = None

    def open_spider(self, spider):
        self.connection = sqlite3.connect("quotes.db")
        self.cursor = self.connection.cursor()

        # 테이블 생성
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS quotes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quote_content TEXT NOT NULL,
                author_name TEXT NOT NULL,
                birthdate TEXT,
                birthplace TEXT,
                bio TEXT,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )
        self.connection.commit()

    def close_spider(self, spider):
        if self.connection:
            self.connection.close()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # 태그를 JSON 문자열로 변환
        tags_json = json.dumps(adapter.get("tags", []), ensure_ascii=False)

        # 데이터 삽입
        self.cursor.execute(
            """
            INSERT INTO quotes (quote_content, author_name, birthdate, birthplace, bio, tags)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                adapter.get("quote_content"),
                adapter.get("author_name"),
                adapter.get("birthdate"),
                adapter.get("birthplace"),
                adapter.get("bio"),
                tags_json,
            ),
        )

        self.connection.commit()
        spider.logger.info(f"Saved to database: {adapter.get('author_name')}")
        return item


class MariaDBPipeline:
    """MariaDB 데이터베이스 저장 파이프라인"""

    def __init__(self):
        self.connection = None
        self.cursor = None

    def open_spider(self, spider):
        # settings.py에서 CONNECTION_STRING 가져오기
        settings = get_project_settings()
        db_settings = settings.get("CONNECTION_STRING")

        try:
            # MariaDB 연결
            self.connection = mariadb.connect(
                user=db_settings["user"],
                password=db_settings["password"],
                host=db_settings["host"],
                port=db_settings["port"],
                database=db_settings["database"],
            )
            self.cursor = self.connection.cursor()

            # 테이블이 존재하지 않으면 생성 (이미 생성되어 있지만 안전을 위해)
            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS quotes (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    quote_content TEXT NOT NULL,
                    author_name VARCHAR(255) NOT NULL,
                    birthdate VARCHAR(100),
                    birthplace TEXT,
                    bio TEXT,
                    tags JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )
            self.connection.commit()
            spider.logger.info("Successfully connected to MariaDB")

        except mariadb.Error as e:
            spider.logger.error(f"Error connecting to MariaDB: {e}")
            raise

    def close_spider(self, spider):
        if self.connection:
            self.connection.close()
            spider.logger.info("MariaDB connection closed")

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        try:
            # 태그를 JSON 문자열로 변환
            tags_json = json.dumps(adapter.get("tags", []), ensure_ascii=False)

            # 데이터 삽입
            self.cursor.execute(
                """
                INSERT INTO quotes (quote_content, author_name, birthdate, birthplace, bio, tags)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    adapter.get("quote_content"),
                    adapter.get("author_name"),
                    adapter.get("birthdate"),
                    adapter.get("birthplace"),
                    adapter.get("bio"),
                    tags_json,
                ),
            )

            self.connection.commit()
            spider.logger.info(f"Saved to MariaDB: {adapter.get('author_name')}")
            return item

        except mariadb.Error as e:
            spider.logger.error(f"Error inserting data to MariaDB: {e}")
            # 에러가 발생해도 아이템을 드랍하지 않고 다음 파이프라인으로 전달
            return item
