#!/usr/bin/env python3
"""
Working with Item objects - 이미지 슬라이드 완전 구현
- Copying items: shallow copy vs. deep copy
- Creating dicts from items or items from dicts
- Extending Item subclasses
"""
import scrapy
from scrapy.item import Item, Field
import copy


# =============================================================================
# Product Item 정의 (이미지와 동일)
# =============================================================================
class Product(scrapy.Item):
    name = scrapy.Field()
    price = scrapy.Field()
    stock = scrapy.Field()
    tags = scrapy.Field()
    last_updated = scrapy.Field(serializer=str)


# =============================================================================
# 1. Copying items: shallow copy vs. deep copy
# =============================================================================
def demo_copying_items():
    """Item 복사 데모 - shallow copy vs deep copy"""
    print("📋 Copying items: shallow copy vs. deep copy")
    print("=" * 60)

    # 원본 product 생성
    product = Product(name="Desktop PC", price=1000)
    product["tags"] = ["electronics", "computer"]  # mutable 값
    print(f"원본 product = {product}")

    # 1. Shallow copy - keep references to the same mutable values
    print("\n1️⃣ Shallow copy")
    product2 = product.copy()  # ← shallow copy of a product
    product3 = Product(product2)  # ← create with shallow copy

    print(f"product2 = product.copy() → {product2}")
    print(f"product3 = Product(product2) → {product3}")

    # shallow copy의 특성 확인
    print(f"product['tags'] is product2['tags']: {product['tags'] is product2['tags']}")
    print(f"product['tags'] is product3['tags']: {product['tags'] is product3['tags']}")

    # 원본의 tags 수정 - shallow copy들도 영향받음
    product["tags"].append("desktop")
    print(f"원본 tags 수정 후:")
    print(f"  product['tags'] = {product['tags']}")
    print(f"  product2['tags'] = {product2['tags']}")
    print(f"  product3['tags'] = {product3['tags']}")

    # 2. Deep copy clones all nested values
    print("\n2️⃣ Deep copy")
    product4 = product3.deepcopy()
    print(f"product4 = product3.deepcopy() → {product4}")
    print(
        f"product3['tags'] is product4['tags']: {product3['tags'] is product4['tags']}"
    )

    # 원본 tags 수정 - deep copy는 영향받지 않음
    product3["tags"].append("office")
    print(f"product3 tags 수정 후:")
    print(f"  product3['tags'] = {product3['tags']}")
    print(f"  product4['tags'] = {product4['tags']}")


# =============================================================================
# 2. Creating dicts from items or items from dicts
# =============================================================================
def demo_dict_conversion():
    """Item과 Dict 간 변환 데모"""
    print("\n📋 Creating dicts from items or items from dicts")
    print("=" * 60)

    # Product Item 생성
    product4 = Product(name="Laptop PC", price=1500, tags=["electronics", "portable"])
    print(f"product4 = {product4}")

    # p5 = dict(product4) ← create a dict from all populated values
    p5 = dict(product4)
    print(f"p5 = dict(product4) → {p5}")
    print(f"type(p5) = {type(p5)}")

    # p6 = Product({'name': 'Laptop PC', 'price': 1500})
    p6 = Product({"name": "Laptop PC", "price": 1500})
    print(f"p6 = Product({{'name': 'Laptop PC', 'price': 1500}}) → {p6}")

    # p7 = Product({'name': 'Laptop PC', 'lala': 1500}) ← KeyError!
    print("\n❌ 정의되지 않은 필드로 생성 시도:")
    try:
        p7 = Product({"name": "Laptop PC", "lala": 1500})
        print(f"p7 = {p7}")
    except KeyError as e:
        print(f"KeyError: {e}")


# =============================================================================
# 3. Extending Item subclasses
# =============================================================================
class DiscountedProduct(Product):
    """Product를 확장한 할인 상품 클래스"""

    discount_percent = scrapy.Field(serializer=str)
    discount_expiration_date = scrapy.Field()


class SpecificProduct(Product):
    """Product의 특정 필드를 커스터마이징한 클래스"""

    name = scrapy.Field()


def demo_extending_items():
    """Item 확장 데모"""
    print("\n📋 Extending Item subclasses")
    print("=" * 60)

    # 1. DiscountedProduct - 필드 추가
    print("1️⃣ DiscountedProduct - 추가 필드")
    discounted = DiscountedProduct(
        name="Gaming Laptop",
        price=2000,
        discount_percent="15%",
        discount_expiration_date="2024-12-31",
    )
    print(f"discounted = {discounted}")
    print(f"discounted.fields.keys() = {list(discounted.fields.keys())}")

    # 2. SpecificProduct - 필드 메타데이터 변경
    print("\n2️⃣ SpecificProduct - 커스텀 serializer")
    specific = SpecificProduct(name="Ultra Gaming PC", price=3000)
    print(f"specific = {specific}")

    # 커스텀 클래스 동작 확인
    print(f"SpecificProduct name field: {specific['name']}")
    print(f"SpecificProduct 클래스 확장 완료")


# =============================================================================
# 4. Product Item으로 실제 Scrapy Shell 동작 시뮬레이션
# =============================================================================
def simulate_scrapy_shell():
    """Scrapy Shell에서의 Item 조작 시뮬레이션"""
    print("\n📋 Scrapy Shell 시뮬레이션")
    print("=" * 60)

    print(">>> class Product(scrapy.Item):")
    print("...     name = scrapy.Field()")
    print("...     price = scrapy.Field()")
    print("...     stock = scrapy.Field()")
    print("...     tags = scrapy.Field()")
    print("...     last_updated = scrapy.Field(serializer=str)")
    print("...")

    # Definition & Creation
    print(">>> product = Product(name='Desktop PC', price=1000)")
    product = Product(name="Desktop PC", price=1000)
    print(f">>> print(product)")
    print(f"{product}")

    # Getting field values
    print(f">>> product['name']")
    print(f"'{product['name']}'")
    print(f">>> product.get('name')")
    print(f"'{product.get('name')}'")
    print(f">>> product['price']")
    print(f"{product['price']}")

    # KeyError 처리
    print(f">>> product['last_updated']")
    print("Traceback (most recent call last):")
    print("  ...")
    print("KeyError: 'last_updated'")
    print(f">>> product.get('last_updated', 'not set')")
    print(f"'{product.get('last_updated', 'not set')}'")

    # Setting
    print(f">>> product['last_updated'] = 'today'")
    product["last_updated"] = "today"
    print(f">>> product['last_updated']")
    print(f"'{product['last_updated']}'")

    # Unknown field
    print(f">>> product['lala'] = 'test'  # setting unknown field")
    print("Traceback (most recent call last):")
    print("  ...")
    print("KeyError: 'Product does not support field: lala'")

    # Accessing all values
    print(f">>> product.keys()")
    print(f"{list(product.keys())}")
    print(f">>> product.items()")
    print(f"{list(product.items())}")


if __name__ == "__main__":
    print("🎯 Working with Item objects - 완전 데모")
    print("=" * 80)

    # 1. 복사 데모
    demo_copying_items()

    # 2. Dict 변환 데모
    demo_dict_conversion()

    # 3. Item 확장 데모
    demo_extending_items()

    # 4. Scrapy Shell 시뮬레이션
    simulate_scrapy_shell()

    print("\n✅ 모든 Item Operations 데모 완료!")
