## docker run -p 5023:5023 -p 8050:8050 -p 8051:8051 scrapinghub/splash
## scrapy shell 'http://localhost:8050/render.html?url=https://aws.amazon.com/ec2/pricing/on-demand/&timeout=10&wait=0.5'
## scrapy shell 'http://localhost:8050/render.html?url=https://aws.amazon.com/ec2/pricing/reserved-instances/pricing/&timeout=10&wait=0.5'

# Yields JSON for one of the amazon pricing webpages

import psycopg2
import re
import scrapy
from scrapy_splash import SplashRequest


# handle check if list has contents and extracting
def ex_list(list, i):
    if (len(list) > 0):
        return list[i]


# handle extracting the double from text
def ex_double(d):
    out = re.findall(r"[-+]?\d*\.\d+|\d+", str(d))
    if out:
        return out[0]
    else:
        return 0.0


# make sure string is not None
def fix_s(var):
    if bool(var):
        return var
    else:
        return ""

def wait(conn):
    while 1:
        state = conn.poll()
        if state == psycopg2.extensions.POLL_OK:
            break
        elif state == psycopg2.extensions.POLL_WRITE:
            select.select([], [conn.fileno()], [])
        elif state == psycopg2.extensions.POLL_READ:
            select.select([conn.fileno()], [], [])
        else:
            raise psycopg2.OperationalError("poll() returned %s" % state)




class AWSSpider(scrapy.Spider):
    name = "aws"

    demand_url = 'http://localhost:8050/render.html?url=https://aws.amazon.com/ec2/pricing/on-demand/&timeout=10&wait=0.5'
    reserved_url = 'http://localhost:8050/render.html?url=https://aws.amazon.com/ec2/pricing/reserved-instances/pricing/&timeout=10&wait=0.5'


    conn = 0
    cur = 0

    # start_urls = [
    #     'https://aws.amazon.com/ec2/pricing/on-demand',
    # ]

    def make_tables(self):
        conn = psycopg2.connect("dbname=testdb user=postgres")
        cur = conn.cursor()

        self.make_demand_table(cur);
        self.make_reserved_table(cur);

        conn.commit()
        cur.close()
        conn.close()

    def make_demand_table(self, cur):
        cur.execute("select * from information_schema.tables where table_name=%s;", ('ondemand_rate_plan_v4',))
        if bool(cur.rowcount):
            cur.execute("DROP TABLE ondemand_rate_plan_v4;")
        cur.execute("""CREATE TABLE ondemand_rate_plan_v4 (

  type character varying NOT NULL,

  region character varying NOT NULL,

  platform character varying NOT NULL,

  rate double precision,

  service character varying NOT NULL,

  lastupdated timestamp without time zone DEFAULT now(),

  CONSTRAINT ondemand_rate_plan_v4_pkey PRIMARY KEY (type, region, platform, service)

);""")

    def make_reserved_table(self, cur):
        cur.execute("select * from information_schema.tables where table_name=%s;", ('reserved_rate_plan_v3',))
        if bool(cur.rowcount):
            cur.execute("DROP TABLE reserved_rate_plan_v3;")
        cur.execute("""CREATE TABLE reserved_rate_plan_v3 (

  type character varying NOT NULL,

  region character varying NOT NULL,

  platform character varying NOT NULL,

  utilization character varying NOT NULL,

  term character varying NOT NULL,

  rate double precision,

  upfront double precision,

  service character varying NOT NULL,

  lastupdated timestamp without time zone,

  CONSTRAINT reserved_rate_plan_v3_pkey PRIMARY KEY (type, region, platform, utilization, term, service)

);""")

    def start_requests(self):
        # self.conn = psycopg2.connect("dbname=testdb user=postgres")
        # self.cur = conn.cursor()

        self.make_tables()

        yield SplashRequest(self.demand_url, self.demand_parse, args={'wait':0.5})
        yield SplashRequest(self.reserved_url, self.reserved_parse, args={'wait':0.5})

        # wait(self.conn)


    def demand_parse(self, response):
        db_type = ''
        db_region = ''
        db_platform = ''
        db_rate = 0.0
        db_service = '' # Not used yet
        db_timestamp = 0

        conn = psycopg2.connect("dbname=testdb user=postgres")
        cur = conn.cursor()

        tables = response.xpath('//table[@class="tan-table"]')

        table_list = []
        for table in tables:

            db_region = table.xpath('.//caption/text()').extract_first()
            db_region = fix_s(db_region)
            db_platform = ex_list(table.xpath('.//thead').xpath('.//th/text()').extract(), -1)
            db_platform = fix_s(db_platform)

            body_list = []
            for body in table.xpath('.//tbody'):

                rows = []
                for row in body.xpath('.//tr[@class="sizes"]'):

                    db_type = row.xpath('.//td/text()').extract_first()
                    db_type = fix_s(db_type)

                    db_rate = ex_double(ex_list(row.xpath('.//td/text()').extract(), 5))

                    cur.execute("INSERT INTO ondemand_rate_plan_v4 (type, region, platform, rate, service) Values (%s, %s, %s, %s, %s)",
                    (db_type, db_region, db_platform, db_rate, db_service))


        conn.commit()
        cur.close()
        conn.close()



    def reserved_parse(self, response):
        db_type = ''
        db_region = ''
        db_platform = ''
        db_utilitization = '' # Not used yet
        db_term = ''
        db_rate = 0.0
        db_upfront = 0.0
        db_service = '' # Not used yet
        db_timestamp = 0

        conn = psycopg2.connect("dbname=testdb user=postgres")
        cur = conn.cursor()

        tabs = response.xpath('//div[@class="section tab-wrapper"]').xpath('.//li/a/text()').extract()
        tab_count = 0

        sanity = 0;

        print len(tabs)
        platforms = response.xpath('//div[@class="tab-content"]/div')
        print len(platforms)
        for platform in platforms:
            db_platform = tabs[tab_count]

            print db_platform

            for div in platform.xpath('.//div[@class="puretmpl"]/div'):

                db_region = div.xpath('.//table/caption/text()').extract_first()

                for body in div.xpath('.//div'):

                    db_type = body.xpath('.//h2/text()').extract_first()



                    for table in body.xpath('.//table'):

                        db_term = table.xpath('.//th[@class="term"]/text()').extract_first()

                        for row in table.xpath('.//tbody/tr'):

                            db_service = ex_list(row.xpath('.//td/text()').extract(), 0)
                            db_upfront = ex_double(ex_list(row.xpath('.//td/text()').extract(), 1))
                            db_rate = ex_double(ex_list(row.xpath('.//td/text()').extract(), 2))

                            cur.execute("INSERT INTO reserved_rate_plan_v3 (type, region, platform, utilization, term, rate, upfront, service) Values (%s, %s, %s, %s, %s, %s, %s, %s)",
                            (db_type, db_region, db_platform, db_utilitization, db_term, db_rate, db_upfront, db_service))

                            sanity += 1

            tab_count += 1
            print tab_count

        print sanity
        conn.commit()
        cur.close()
        conn.close()






            # def parse(self, response):
            #
            #
            #
    #
    #     tables = response.xpath('//table')
    #
    #     # Extract all data for each table and place in list
    #     table_list = []
    #     for table in tables:
    #
    #         # Extract all data for a single table and place into json
    #         body_list = []
    #         for body in table.xpath('.//tbody'):
    #
    #             # Extract the row data and place json into list
    #             rows = []
    #             for row in body.xpath('.//tr[@class="sizes"]'):
    #                 row_json = {
    #                     'row' : row.xpath('.//td/text()').extract()
    #                 }
    #                 rows.append(row_json)
    #
    #             # Extract the header for the body and append to list
    #             body_json = {
    #                 'header' : body.xpath('.//th/text()').extract_first(),
    #                 'rows' : rows,
    #             }
    #             body_list.append(body_json)
    #
    #         # Appened json to table list
    #         table_json = {
    #             'caption' : table.xpath('.//caption/text()').extract(),
    #             'cols' : table.xpath('.//thead').xpath('.//th/text()').extract(),
    #             'bodies': body_list,
    #         }
    #         table_list.append(table_json)
    #
    #         # Generate individual jsons for readability
    #         yield table_json
    #
    #     # Consolidated json
    #     yield {
    #         'data_tables' : table_list,
    #     }
