import scrapy
import ast
import psycopg2


class AzureSpider(scrapy.Spider):
    name = "azureStorage"
    # try:
    #     conn = psycopg2.connect("dbname='testdb' user='docker' host='localhost' password='docker'")
    # except:
    #     print("Unable to connect to database...")
    #
    # cur = conn.cursor()



    def make_storage_table(self):
        conn = psycopg2.connect("dbname='testdb' user='docker' host='localhost' password='docker'")
        cur = conn.cursor()
        cur.execute("select * from information_schema.tables where table_name=%s;",
        ('azure_storage_pricing',))
        if bool(cur.rowcount):
            cur.execute("DROP TABLE azure_storage_pricing;")
        cur.execute("""CREATE TABLE azure_storage_pricing  (
            id bigserial NOT NULL,
            capacity_limit real,
            cost_per_gb real,
            region character varying(1024),
            storage_type character varying(1024),
            redundancy_type character varying(1024),
            CONSTRAINT azure_storage_pricing_v2_pkey PRIMARY KEY (id)
            );""")
        conn.commit()
        cur.close()
        conn.close()

    def start_requests(self):
        self.make_storage_table()
        baseURL = 'https://azure.microsoft.com/en-us/pricing/details/storage/'
        urls = [
            baseURL+'disks/',
            baseURL+'tables/',
            baseURL+'queues/'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)  

    def parse(self, response):

        conn = psycopg2.connect("dbname='testdb' user='docker' host='localhost' password='docker'")
        cur = conn.cursor()

        stoType = response.url.split('/')[-2]

        if stoType == 'disks':
            table = 2
        else:
            table = 1
        tableSel = response.xpath('//table')[table]
        redTypes = tableSel.xpath('.//th/text()').extract()[1:]
        # capLims = ['1 TB', '50 TB', '500 TB', '1000 TB', '5000 TB']
        capLims = ['1', '50', '500', '1000', '5000']

        rows = tableSel.xpath('.//tr')[1:]
        for i in range(len(capLims)):
            row = rows[i]
            priceData = row.xpath('.//span[@class="price-data "]/@data-amount').extract()
            for j in range(len(redTypes)):
                pricing = priceData[j]
                pricing_dict = ast.literal_eval(pricing)['regional']
                for region in pricing_dict:
                    rate = pricing_dict[region]
                    cur.execute("INSERT INTO azure_storage_pricing (capacity_limit, cost_per_gb, region, storage_type, redundancy_type) Values (%s, %s, %s, %s, %s)", (capLims[i], rate, region, stoType, redTypes[j]))

        conn.commit()
        cur.close()
        conn.close()
