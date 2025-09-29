#!/usr/bin/env python3
"""
Scrapy Shell 데모 - 이미지 슬라이드 "Try at the scrapy shell!" 구현
실제 Scrapy Shell에서 Product Item을 조작하는 방법을 보여줍니다.
"""
import os
import subprocess
import tempfile


def generate_scrapy_shell_commands():
    """Scrapy Shell에서 실행할 명령어들을 생성"""
    commands = [
        # Product 클래스 정의
        "import scrapy",
        "",
        "class Product(scrapy.Item):",
        "    name = scrapy.Field()",
        "    price = scrapy.Field()",
        "    stock = scrapy.Field()",
        "    tags = scrapy.Field()",
        "    last_updated = scrapy.Field(serializer=str)",
        "",
        # Product 인스턴스 생성 (이미지의 creation 부분)
        "product = Product(name='Desktop PC', price=1000)",
        "print(product)",
        "",
        # 필드 접근 (이미지의 field access 부분)
        "print(f\"product['name'] = {product['name']}\")",
        "print(f\"product.get('name') = {product.get('name')}\")",
        "print(f\"product['price'] = {product['price']}\")",
        "",
        # KeyError 처리
        "try:",
        "    print(product['last_updated'])",
        "except KeyError:",
        "    print('KeyError: last_updated not set')",
        "",
        "print(f\"product.get('last_updated', 'not set') = {product.get('last_updated', 'not set')}\")",
        "",
        # 필드 설정
        "product['last_updated'] = 'today'",
        "print(f\"After setting: product['last_updated'] = {product['last_updated']}\")",
        "",
        # 정의되지 않은 필드 처리
        "try:",
        "    product['lala'] = 'test'",
        "except KeyError as e:",
        "    print(f'KeyError setting unknown field: {e}')",
        "",
        # 모든 값 접근
        'print(f"product.keys() = {list(product.keys())}")',
        'print(f"product.items() = {list(product.items())}")',
        "",
        # 필드 존재 확인
        "print(f\"'name' in product = {'name' in product}\")",
        "print(f\"'last_updated' in product = {'last_updated' in product}\")",
        "print(f\"'last_updated' in product.fields = {'last_updated' in product.fields}\")",
        "print(f\"'lala' in product.fields = {'lala' in product.fields}\")",
    ]

    return "\\n".join(commands)


def create_interactive_demo():
    """대화형 데모 생성"""
    print("🐚 Scrapy Shell 시뮬레이션 - Product Item 조작")
    print("=" * 60)
    print("이미지 슬라이드의 'Try at the scrapy shell!' 내용을 시뮬레이션합니다.")
    print()

    # Product 클래스 정의 시뮬레이션
    print("🔧 Product 클래스 정의 (이미지의 definition 부분)")
    print("-" * 40)

    import scrapy

    class Product(scrapy.Item):
        name = scrapy.Field()
        price = scrapy.Field()
        stock = scrapy.Field()
        tags = scrapy.Field()
        last_updated = scrapy.Field(serializer=str)

    print(">>> class Product(scrapy.Item):")
    print("...     name = scrapy.Field()")
    print("...     price = scrapy.Field()")
    print("...     stock = scrapy.Field()")
    print("...     tags = scrapy.Field()")
    print("...     last_updated = scrapy.Field(serializer=str)")
    print("...")

    # Product 생성 (이미지의 creation 부분)
    print("\\n📦 Product 인스턴스 생성 (이미지의 creation 부분)")
    print("-" * 40)

    print(">>> product = Product(name='Desktop PC', price=1000)")
    product = Product(name="Desktop PC", price=1000)
    print(">>> print(product)")
    print(f"{product}")

    # 필드 접근 (이미지의 field access 부분)
    print("\\n🔍 필드 접근 (이미지의 field access 부분)")
    print("-" * 40)

    print(">>> product['name']")
    print(f"'{product['name']}'")
    print(">>> product.get('name')")
    print(f"'{product.get('name')}'")
    print(">>> product['price']")
    print(f"{product['price']}")

    # KeyError 처리
    print("\\n❌ 설정되지 않은 필드 접근")
    print("-" * 40)

    print(">>> product['last_updated']")
    print("Traceback (most recent call last):")
    print('  File "<console>", line 1, in <module>')
    print(
        '  File "d:\\\\allprojects\\\\vpython\\\\quote_scrapy\\\\lib\\\\site-packages\\\\scrapy\\\\item.py", line 93, in __getitem__'
    )
    print("    return self._values[key]")
    print("KeyError: 'last_updated'")
    print(">>> product.get('last_updated', 'not set')")
    print(f"'{product.get('last_updated', 'not set')}'")

    print(">>> product['lala']")
    print("Traceback (most recent call last):")
    print('  File "<console>", line 1, in <module>')
    print(
        '  File "d:\\\\allprojects\\\\vpython\\\\quote_scrapy\\\\lib\\\\site-packages\\\\scrapy\\\\item.py", line 93, in __getitem__'
    )
    print("    return self._values[key]")
    print("KeyError: 'lala'")

    # 필드 설정
    print("\\n✏️ 필드 값 설정")
    print("-" * 40)

    print(">>> product['last_updated'] = 'today'")
    product["last_updated"] = "today"
    print(">>> product['last_updated']")
    print(f"'{product['last_updated']}'")

    # 정의되지 않은 필드 설정 시도
    print("\\n❌ 정의되지 않은 필드 설정 시도")
    print("-" * 40)

    print(">>> product['lala'] = 'test'  # setting unknown field")
    print("Traceback (most recent call last):")
    print("  ...")
    print("KeyError: 'Product does not support field: lala'")

    # 모든 값 접근
    print("\\n📋 모든 값 접근")
    print("-" * 40)

    print(">>> product.keys()")
    print(f"{list(product.keys())}")
    print(">>> product.items()")
    print(f"{list(product.items())}")

    # 필드 존재 확인
    print("\\n🔍 필드 존재 확인")
    print("-" * 40)

    print(">>> 'name' in product  # is name field populated?")
    print(f"{bool('name' in product)}")
    print(">>> 'last_updated' in product  # is last_updated populated?")
    print(f"{bool('last_updated' in product)}")
    print(">>> 'last_updated' in product.fields  # is last_updated a declared field?")
    print(f"{bool('last_updated' in product.fields)}")
    print(">>> 'lala' in product.fields  # is lala a declared field?")
    print(f"{bool('lala' in product.fields)}")


def create_scrapy_shell_script():
    """실제 Scrapy Shell 실행 스크립트 생성"""
    script_content = f'''#!/usr/bin/env python3
"""
실제 Scrapy Shell에서 실행할 스크립트
"""

# 이 스크립트는 실제 scrapy shell에서 실행하세요:
# cd /Users/juns/bigdata/tutorial
# scrapy shell "http://quotes.toscrape.com"

# 아래 명령어들을 하나씩 실행해보세요:

{generate_scrapy_shell_commands()}

# 추가로 response 객체를 사용한 실습:
# response.css('div.quote')
# response.css('div.quote span.text::text').getall()
#
# Product 아이템 생성 실습:
# for q in response.css('div.quote'):
#     item = Product()
#     item['name'] = q.css('span.text::text').get()
#     item['price'] = 100  # 예시
#     print(item)
'''

    return script_content


if __name__ == "__main__":
    print("🎯 Scrapy Shell 데모 - Product Item 조작 완전 구현")
    print("=" * 80)

    # 1. 대화형 데모 실행
    create_interactive_demo()

    # 2. 실제 Scrapy Shell 스크립트 생성
    shell_script = create_scrapy_shell_script()

    with open(
        "/Users/juns/bigdata/scrapy_shell_commands.py", "w", encoding="utf-8"
    ) as f:
        f.write(shell_script)

    print("\\n📝 추가 파일 생성:")
    print("- scrapy_shell_commands.py: 실제 Scrapy Shell에서 실행할 명령어들")
    print("\\n💡 실제 Scrapy Shell 사용법:")
    print("cd /Users/juns/bigdata/tutorial")
    print("scrapy shell 'http://quotes.toscrape.com'")
    print("그 후 scrapy_shell_commands.py의 명령어들을 하나씩 실행해보세요!")

    print("\\n✅ Scrapy Shell 데모 완료!")
