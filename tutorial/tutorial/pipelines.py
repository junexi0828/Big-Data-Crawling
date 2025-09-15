# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


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
