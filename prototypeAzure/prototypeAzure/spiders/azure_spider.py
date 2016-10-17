import scrapy

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
      tables_json = []
      for table in response.xpath(mainSelector+'//table[@class="table-width-even"]'):
        # Pull the labels for each column
        cols = table.xpath('.//thead//th//text()').extract()

        # Select each row in the table and generate a list of column values
        rows = []
        for row in table.xpath('.//tbody//tr'):
          tds = []
          for td in row.xpath('.//td'):
            tds.append(td.xpath('.//text()').extract())
          rows  = {
            'row' : tds
          }

        # Generate a table json for each table 
        table_json = {
          'cols' :   cols,
          'rows' :   rows
        }
        # Add the new table json to the master json of tables
        tables_json.append(table_json)

      # Create a selector and extract information about the current service
      serviceSel = response.xpath(mainSelector+'//div[@class="row column"]')
      services = {
        'service' :     serviceSel.xpath('./h2/text()').extract_first(),
        'description' : serviceSel.xpath('./p/text()').extract_first(),
        'tables':       tables_json
      }
      yield services
