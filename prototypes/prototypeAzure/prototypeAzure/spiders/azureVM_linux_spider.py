import scrapy
import ast

# Prototype spider for scraping the Microsoft Azure pricing data. Should be easily
# extensible for services other than virtual machines as each page has similar
# enough structure and formatting


class AzureSpider(scrapy.Spider):
    name = "azure"
    start_urls = [
        'https://azure.microsoft.com/en-us/pricing/details/virtual-machines/linux/'
    ]

    def parse(self, response):
      mainSelector = '//section[@class="section section-size3"]'

      # Select only the relevant tables and extract pricing data
      instances = []
      for table in response.xpath(mainSelector+'//table[@class="table-width-even"]'):

        for row in table.xpath('.//tbody//tr'):
          pricing = row.xpath('.//td//span[@class="price-data "]/@data-amount').extract_first()
          pricing_dict = ast.literal_eval(pricing)['regional']

          tds = []
          for td in row.xpath('.//td'):
            tds.append(td.xpath('.//text()').extract())
          for region in pricing_dict:
            rate = pricing_dict[region]
            instance = {'instance_type':tds[0], 'hourly_rate':rate, 'region':region, 
                        'platform': 'linux'}
            instances.append(instance)

      yield {'instances':instances}
