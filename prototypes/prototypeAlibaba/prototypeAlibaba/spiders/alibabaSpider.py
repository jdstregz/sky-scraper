import scrapy

class QuotesSpider(scrapy.Spider):
    name = "alibaba"

    def start_requests(self):
        urls = [
        'https://intl.aliyun.com/product/oss#pricing',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split("/")[-2]
        data = response.css('td::text').extract()
        with open('alibaba.csv', 'wb') as f:
            for d in data:
                print str(d)
                f.write("%s, " % d)
