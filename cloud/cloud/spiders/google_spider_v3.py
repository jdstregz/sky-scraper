import re
import scrapy
import psycopg2

class GoogleSpider(scrapy.Spider):
    name = "googlev3"
    try:
        conn = psycopg2.connect("dbname='testdb' user='docker' host='localhost' password='docker'")
    except:
        print "Unable to connect to database..."

    cur = conn.cursor()
    
    def start_requests(self):
        urls = [
            'https://cloud.google.com/compute/pricing',
        ]

        self.make_demand_table()

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):

        db_type = ''
        db_region = ''
        db_cpus = ''
        db_memory = ''
        db_price = ''
        db_preprice = ''

        tables = response.xpath('//table')

        #response.xpath('.//div[@class="table-bar"]/md-select/md-option').extract_first()

        regions = ['US', 'Europe', 'Asia (Taiwan)', 'Asia (Japan)']

        for region in regions:
            tables = response.xpath('//table')
            for table in tables:
                bodies = table.xpath('.//tbody')
                for body in bodies:
                    rows = body.xpath('.//tr')
                    for row in rows:
                        row_array = []
                        items = row.xpath('.//td').extract()
                        for item in items:
                            if region == 'US':
                                output = re.findall(r'us-hourly=\"(.+?)\"', item)
                                if output:
                                    row_array.append(output)
                                    #print output
                                else:
                                    fixed_output = re.findall(r'<td>(.+?)<', item)
                                    row_array.append(fixed_output)
                                    #print fixed_output
                            elif region == 'Europe':
                                output = re.findall(r'eu-hourly=\"(.+?)\"', item)
                                if output:
                                    row_array.append(output)
                                    #print output
                                else:
                                    fixed_output = re.findall(r'<td>(.+?)<', item)
                                    row_array.append(fixed_output)
                                    #print fixed_output
                            elif region == 'Asia (Taiwan)':
                                output = re.findall(r'tw-hourly=\"(.+?)\"', item)
                                if output:
                                    row_array.append(output)
                                    #print output
                                else:
                                    fixed_output = re.findall(r'<td>(.+?)<', item)
                                    row_array.append(fixed_output)
                                    #print fixed_output')
                            elif region == 'Asia (Japan)':
                                output = re.findall(r'ja-hourly=\"(.+?)\"', item)
                                if output:
                                    row_array.append(output)
                                    #print output
                                else:
                                    fixed_output = re.findall(r'<td>(.+?)<', item)
                                    row_array.append(fixed_output)
                                    #print fixed_output')
                        if len(row_array) == 5:
                            db_type = row_array[0]
                            db_cpus = row_array[1]
                            db_region = region
                            db_memory = row_array[2]
                            db_price = row_array[3]
                            db_preprice = row_array[4]

                            self.cur.execute("INSERT INTO gcp_compute_pricing (instance_type, hourly_rate_price, preemptible_hourly_price, region, memory) VALUES (%s, %s, %s, %s, %s)",
                            (db_type, db_price, db_preprice, db_region, db_memory))
        self.conn.commit()
        self.cur.close()
        self.conn.close()              

    def make_demand_table(self):
        self.cur.execute("select * from information_schema.tables where table_name=%s;", ('gcp_compute_pricing',))
        if bool(self.cur.rowcount):
            self.cur.execute("DROP TABLE gcp_compute_pricing;")
        self.cur.execute("""CREATE TABLE gcp_compute_pricing (
                id bigserial NOT NULL,
                instance_type character varying(255),
                hourly_rate_price character varying(255),
                preemptible_hourly_price character varying(255),
                region character varying(255),
                memory character varying(255),
                last_updated_timestamp timestamp without time zone DEFAULT now(),
                CONSTRAINT gcp_compute_pricing_pkey PRIMARY KEY (id)
                );""")
