#!/usr/bin/env python3
"""
실제 Scrapy Shell에서 실행할 스크립트
"""

# 이 스크립트는 실제 scrapy shell에서 실행하세요:
# cd /Users/juns/bigdata/tutorial
# scrapy shell "http://quotes.toscrape.com"

# 아래 명령어들을 하나씩 실행해보세요:

import scrapy\n\nclass Product(scrapy.Item):\n    name = scrapy.Field()\n    price = scrapy.Field()\n    stock = scrapy.Field()\n    tags = scrapy.Field()\n    last_updated = scrapy.Field(serializer=str)\n\nproduct = Product(name='Desktop PC', price=1000)\nprint(product)\n\nprint(f"product['name'] = {product['name']}")\nprint(f"product.get('name') = {product.get('name')}")\nprint(f"product['price'] = {product['price']}")\n\ntry:\n    print(product['last_updated'])\nexcept KeyError:\n    print('KeyError: last_updated not set')\n\nprint(f"product.get('last_updated', 'not set') = {product.get('last_updated', 'not set')}")\n\nproduct['last_updated'] = 'today'\nprint(f"After setting: product['last_updated'] = {product['last_updated']}")\n\ntry:\n    product['lala'] = 'test'\nexcept KeyError as e:\n    print(f'KeyError setting unknown field: {e}')\n\nprint(f"product.keys() = {list(product.keys())}")\nprint(f"product.items() = {list(product.items())}")\n\nprint(f"'name' in product = {'name' in product}")\nprint(f"'last_updated' in product = {'last_updated' in product}")\nprint(f"'last_updated' in product.fields = {'last_updated' in product.fields}")\nprint(f"'lala' in product.fields = {'lala' in product.fields}")

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
