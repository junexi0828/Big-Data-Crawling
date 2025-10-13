"""
복잡한 HTTP 요청 처리 데모
- cURL 형식을 Scrapy Request로 변환
- Request.from_curl() 메서드 사용
- scrapy.utils.curl.curl_to_request_kwargs() 유틸리티 사용
"""

import scrapy
from scrapy.utils.curl import curl_to_request_kwargs


class ComplexRequestSpider(scrapy.Spider):
    name = "complex_request_spider"
    allowed_domains = ["quotes.toscrape.com"]

    def start_requests(self):
        # 방법 1: Request.from_curl() 메서드 사용
        # 이미지에서 보여준 cURL 명령어를 Scrapy Request로 변환
        curl_command = """
        curl 'http://quotes.toscrape.com/api/quotes?page=1' -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:67.0) Gecko/20100101 Firefox/67.0' -H 'Accept: */*' -H 'Accept-Language: ca,en-US;q=0.7,en;q=0.3' --compressed -H 'X-Requested-With: XMLHttpRequest' -H 'Proxy-Authorization: Basic QFRLLTzEwZTAxLTkSMWUtNDFiNCIZWRmLTJjNGI4N2ZiNDEtOTkxZS00Mw' -H 'Connection: keep-alive' -H 'Referer: http://quotes.toscrape.com/scroll' -H 'Cache-Control: max-age=0'
        """

        request = scrapy.Request.from_curl(
            curl_command.strip(), callback=self.parse_curl_response
        )
        yield request

        # 방법 2: curl_to_request_kwargs() 유틸리티 사용
        curl_kwargs = curl_to_request_kwargs(
            curl_command.strip(), ignore_unknown_options=True
        )
        yield scrapy.Request(**curl_kwargs, callback=self.parse_kwargs_response)

    def parse_curl_response(self, response):
        """from_curl() 메서드로 만든 요청의 응답 처리"""
        self.logger.info(f"✅ from_curl() 방법으로 받은 응답: {response.status}")
        self.logger.info(
            f"Content-Type: {response.headers.get('Content-Type', b'').decode()}"
        )

        # JSON 응답 파싱
        import json

        try:
            data = json.loads(response.text)
            self.logger.info(f"📊 quotes 개수: {len(data.get('quotes', []))}")

            for quote in data.get("quotes", [])[:3]:  # 처음 3개만 출력
                yield {
                    "method": "from_curl",
                    "quote": quote["text"][:50] + "...",
                    "author": quote["author"]["name"],
                    "tags": quote["tags"],
                }
        except json.JSONDecodeError:
            self.logger.error("❌ JSON 파싱 실패")

    def parse_kwargs_response(self, response):
        """curl_to_request_kwargs() 유틸리티로 만든 요청의 응답 처리"""
        self.logger.info(
            f"✅ curl_to_request_kwargs() 방법으로 받은 응답: {response.status}"
        )

        import json

        try:
            data = json.loads(response.text)
            self.logger.info(f"📊 quotes 개수: {len(data.get('quotes', []))}")

            for quote in data.get("quotes", [])[:3]:  # 처음 3개만 출력
                yield {
                    "method": "curl_to_request_kwargs",
                    "quote": quote["text"][:50] + "...",
                    "author": quote["author"]["name"],
                    "tags": quote["tags"],
                }
        except json.JSONDecodeError:
            self.logger.error("❌ JSON 파싱 실패")
