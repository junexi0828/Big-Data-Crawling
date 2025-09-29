#!/usr/bin/env python3
"""
Scrapy Item Types 데모: dict, Item class, dataclass, attr.s
이미지 슬라이드의 모든 Item 타입 구현
"""
import scrapy
from scrapy.item import Item, Field
from dataclasses import dataclass
from typing import List, Optional
import attr


# =============================================================================
# 1. dict (Python dictionaries) - 기본 파이썬 딕셔너리
# =============================================================================
def create_dict_items():
    """Python 딕셔너리로 Item 생성"""
    print("1️⃣ dict (Python dictionaries)")
    print("=" * 50)

    # d1 = dict(one=1, two=2, three=3)
    d1 = dict(one=1, two=2, three=3)
    print(f"d1 = {d1}")

    # d2 = {'one':1, 'two':2, 'three':3}
    d2 = {"one": 1, "two": 2, "three": 3}
    print(f"d2 = {d2}")

    # d3 = dict(zip(['one', 'two', 'three'], [1, 2, 3]))
    d3 = dict(zip(["one", "two", "three"], [1, 2, 3]))
    print(f"d3 = {d3}")

    return d1, d2, d3


# =============================================================================
# 2. Item class object: dict-like API + additional features
# =============================================================================
class Product(scrapy.Item):
    """Item class object with additional features"""

    name = scrapy.Field()
    price = scrapy.Field()
    stock = scrapy.Field()
    tags = scrapy.Field()
    last_updated = scrapy.Field(serializer=str)


def demo_item_class():
    """Item class 데모"""
    print("\n2️⃣ Item class object: dict-like API + additional features")
    print("=" * 60)

    # Definition & Creation
    product = Product(name="Desktop PC", price=1000)
    print(f"product = {product}")

    # Getting field values
    print(f"product['name'] = {product['name']}")
    print(f"product.get('name') = {product.get('name')}")
    print(f"product['price'] = {product['price']}")

    # KeyError 처리
    try:
        print(f"product['last_updated'] = {product['last_updated']}")
    except KeyError as e:
        print(f"KeyError: {e}")
        print(
            f"product.get('last_updated', 'not set') = {product.get('last_updated', 'not set')}"
        )

    # Setting
    product["last_updated"] = "today"
    print(f"After setting: product['last_updated'] = {product['last_updated']}")

    # Unknown field 처리
    try:
        product["lala"] = "test"
    except KeyError as e:
        print(f"KeyError setting unknown field: {e}")
        print(
            f"product.get('lala', 'unknown field') = {product.get('lala', 'unknown field')}"
        )

    # Accessing all values
    print(f"product.keys() = {list(product.keys())}")
    print(f"product.items() = {list(product.items())}")

    # Field validation
    print(f"'name' in product = {'name' in product}")
    print(f"'last_updated' in product = {'last_updated' in product}")
    print(f"'last_updated' in product.fields = {'last_updated' in product.fields}")
    print(f"'lala' in product.fields = {'lala' in product.fields}")

    return product


# =============================================================================
# 3. dataclass object: define the type & default value of each field
# =============================================================================
@dataclass
class CustomItem:
    """dataclass를 사용한 Item 정의"""

    one_field: str
    another_field: int
    tags: List[str] = None
    optional_field: Optional[str] = None


def demo_dataclass():
    """dataclass 데모"""
    print("\n3️⃣ dataclass object: define the type & default value")
    print("=" * 55)

    # 생성
    item1 = CustomItem(one_field="test", another_field=123)
    print(f"item1 = {item1}")

    # 기본값과 함께 생성
    item2 = CustomItem(one_field="hello", another_field=456, tags=["python", "scrapy"])
    print(f"item2 = {item2}")

    # 필드 접근
    print(f"item1.one_field = {item1.one_field}")
    print(f"item2.tags = {item2.tags}")

    return item1, item2


# =============================================================================
# 4. attr.s object: define the type & default value, custom field metadata
# =============================================================================
@attr.s
class CustomItemAttrs:
    """attr.s를 사용한 Item 정의"""

    one_field = attr.ib()
    another_field = attr.ib()
    tags = attr.ib(default=None)
    metadata_field = attr.ib(
        default="default_value", metadata={"description": "Field with metadata"}
    )


def demo_attrs():
    """attr.s 데모"""
    print("\n4️⃣ attr.s object: define the type & default value, custom field metadata")
    print("=" * 70)

    # 생성
    item1 = CustomItemAttrs(one_field="test", another_field=123)
    print(f"item1 = {item1}")

    # 기본값과 함께 생성
    item2 = CustomItemAttrs(
        one_field="hello", another_field=456, tags=["python", "scrapy"]
    )
    print(f"item2 = {item2}")

    # 필드 접근
    print(f"item1.one_field = {item1.one_field}")
    print(f"item2.metadata_field = {item2.metadata_field}")

    # attr.s 메타데이터 확인
    fields = attr.fields(CustomItemAttrs)
    for field in fields:
        print(f"Field: {field.name}, metadata: {field.metadata}")

    return item1, item2


# =============================================================================
# ItemAdapter를 사용한 통합 처리
# =============================================================================
def demo_itemadapter():
    """ItemAdapter로 다양한 Item 타입 통합 처리"""
    print("\n🔧 ItemAdapter를 사용한 통합 처리")
    print("=" * 50)

    try:
        from itemadapter import ItemAdapter

        # 다양한 타입의 아이템들
        dict_item = {"name": "Dict Item", "price": 100}
        scrapy_item = Product(name="Scrapy Item", price=200)
        dataclass_item = CustomItem(one_field="Dataclass Item", another_field=300)
        attrs_item = CustomItemAttrs(one_field="Attrs Item", another_field=400)

        items = [
            ("Dict", dict_item),
            ("Scrapy Item", scrapy_item),
            ("Dataclass", dataclass_item),
            ("Attrs", attrs_item),
        ]

        for item_type, item in items:
            adapter = ItemAdapter(item)
            print(f"{item_type}: {dict(adapter)}")

    except ImportError:
        print(
            "ItemAdapter가 설치되지 않았습니다. pip install itemadapter로 설치해주세요."
        )


if __name__ == "__main__":
    print("🎯 Scrapy Item Types 완전 데모")
    print("=" * 80)

    # 1. Dict 데모
    create_dict_items()

    # 2. Item class 데모
    demo_item_class()

    # 3. Dataclass 데모
    demo_dataclass()

    # 4. Attrs 데모
    demo_attrs()

    # 5. ItemAdapter 통합 데모
    demo_itemadapter()

    print("\n✅ 모든 Item Types 데모 완료!")
