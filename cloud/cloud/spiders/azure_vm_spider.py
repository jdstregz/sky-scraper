import scrapy
import ast
import psycopg2


class AzureSpider(scrapy.Spider):
  name = "azureVM"
  baseURL = 'https://azure.microsoft.com/en-us/pricing/details/virtual-machines/'
  start_urls = [
    baseURL+'linux/',
    baseURL+'red-hat/',
    baseURL+'r-server/',
    baseURL+'sles/',
    baseURL+'windows/',
    baseURL+'biztalk-enterprise/', 
    baseURL+'biztalk-standard/',
    baseURL+'oracle-java/',
    baseURL+'sharepoint/',
    baseURL+'sql-server-enterprise/',
    baseURL+'sql-server-standard/',
    baseURL+'sql-server-web/'
  ]
  def makeTables(self):
    conn = psycopg2.connect("dbname='testdb' user='docker' host='localhost' password='docker'")
    cur = conn.cursor()
    self.make_vm_table(cur)
    conn.commit()
    cur.close()
    conn.close()

  def make_vm_table(self, cur):
    cur.execute("select * from information_schema.tables where table_name=%s;",
                  ('azure_vm_pricing',))
    if not bool(cur.rowcount):
      cur.execute("DROP TABLE azure_vm_pricing;")
      cur.execute("""CREATE TABLE azure_vm_pricing  (
                    id bigserial NOT NULL,
                    instance_type character varying(255),
                    hourly_rate real,
                    region character varying(255),
                    platform character varying(255),
                    CONSTRAINT azure_vm_pricing_pkey PRIMARY KEY (id)
                    );"""
      )
  
  def parse(self, response):
    mainSelector = '//section[@class="section section-size3"]'

    # Select only the relevant tables and extract pricing data
    instances = []
    self.makeTables()

    conn = psycopg2.connect("dbname='testdb' user='docker' host='localhost' password='docker'")
    cur = conn.cursor()

    for table in response.xpath(mainSelector+'//table[@class="table-width-even"]'):
      for row in table.xpath('.//tbody//tr'):
        pricing = row.xpath('.//td//span[@class="price-data "]/@data-amount').extract_first()
        pricing_dict = ast.literal_eval(pricing)['regional']

        tds = []
        for td in row.xpath('.//td'):
          tds.append(td.xpath('.//text()').extract())
        for region in pricing_dict:
          rate = pricing_dict[region]
          platform = response.url.split('/')[-2]
          cur.execute("INSERT INTO azure_vm_pricing (instance_type, hourly_rate, region, platform) Values (%s, %s, %s, %s)", (tds[0][0].strip(), rate, region, platform))
    conn.commit()
    cur.close()
    conn.close()
