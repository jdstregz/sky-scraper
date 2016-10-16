## scrapy shell 'http://localhost:8050/render.html?url=https://aws.amazon.com/ec2/pricing/on-demand/&timeout=10&wait=0.5'

# Yields JSON for one of the amazon pricing webpages

import scrapy
from scrapy_splash import SplashRequest

class AWSSpider(scrapy.Spider):
    name = "aws"
    urls = [
        'http://localhost:8050/render.html?url=https://aws.amazon.com/ec2/pricing/on-demand/&timeout=10&wait=0.5',
    ]

    # start_urls = [
    #     'https://aws.amazon.com/ec2/pricing/on-demand',
    # ]

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse, args={'wait':0.5})

    def parse(self, response):
        tables = response.xpath('//table')

        # Extract all data for each table and place in list
        table_list = []
        for table in tables:

            # Extract all data for a single table and place into json
            body_list = []
            for body in table.xpath('.//tbody'):

                # Extract the row data and place json into list
                rows = []
                for row in body.xpath('.//tr[@class="sizes"]'):
                    row_json = {
                        'row' : row.xpath('.//td/text()').extract()
                    }
                    rows.append(row_json)

                # Extract the header for the body and append to list
                body_json = {
                    'header' : body.xpath('.//th/text()').extract_first(),
                    'rows' : rows,
                }
                body_list.append(body_json)

            # Appened json to table list
            table_json = {
                'caption' : table.xpath('.//caption/text()').extract(),
                'cols' : table.xpath('.//thead').xpath('.//th/text()').extract(),
                'bodies': body_list,
            }
            table_list.append(table_json)

            # Generate individual jsons for readability
            yield table_json

        # Consolidated json
        yield {
            'data_tables' : table_list,
        }
