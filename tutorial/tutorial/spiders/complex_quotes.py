import scrapy


class ComplexQuotesSpider(scrapy.Spider):
    name = 'complex_quotes'
    start_urls = ['http://quotes.toscrape.com']

    def parse(self, response):
        # 명언 정보 수집
        for q in response.css('div.quote'):
            yield {
                'text': q.css('span.text::text').get(),
                'author': q.css('small.author::text').get(),
                'tags': q.css('div.tags a.tag::text').getall(),
            }

        # 작가 링크들을 따라가서 작가 정보 수집
        yield from response.follow_all(q.css('.author + a'), self.parse_author)

        # 다음 페이지로 이동
        yield from response.follow_all(response.css('li.next a'), callback=self.parse)

    def parse_author(self, response):
        yield {
            'name': response.css('.author-title::text').get().strip(),
            'birthdate': response.css('.author-born-date::text').get(),
            'birthplace': response.css('.author-born-location::text').get(),
            'bio': response.css('.author-description::text').get().strip(),
        }
