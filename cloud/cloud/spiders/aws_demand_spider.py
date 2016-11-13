## docker run -p 5023:5023 -p 8050:8050 -p 8051:8051 scrapinghub/splash
## scrapy shell 'http://localhost:8050/render.html?url=https://aws.amazon.com/ec2/pricing/reserved-instances/pricing/&timeout=10&wait=0.5'

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


class AWSDemandSpider(scrapy.Spider):
    name = "aws_demand"

    conn = psycopg2.connect("dbname=testdb user=postgres")
    cur = conn.cursor()

    url = 'http://localhost:8050/render.html?url=https://aws.amazon.com/ec2/pricing/on-demand/&timeout=10&wait=0.5'

    def start_requests(self):
        # self.conn = psycopg2.connect("dbname=testdb user=postgres")
        # self.cur = conn.cursor()

        self.make_demand_table()

        yield SplashRequest(self.url, self.parse, args={'wait':0.5})

        # wait(self.conn)


    def parse(self, response):
        db_type = ''
        db_region = ''
        db_platform = ''
        db_rate = 0.0
        db_service = '' # Not used yet
        db_timestamp = 0

        tables = response.xpath('//table[@class="tan-table"]')
        sanity = 0
        for table in tables:

            db_region = table.xpath('.//caption/text()').extract_first()
            db_region = fix_s(db_region)
            db_platform = ex_list(table.xpath('.//thead').xpath('.//th/text()').extract(), -1)
            db_platform = fix_s(db_platform)

            for body in table.xpath('.//tbody'):

                for row in body.xpath('.//tr[@class="sizes"]'):

                    db_type = row.xpath('.//td/text()').extract_first()
                    db_type = fix_s(db_type)

                    db_rate = ex_double(ex_list(row.xpath('.//td/text()').extract(), 5))

                    self.cur.execute("INSERT INTO ondemand_rate_plan_v4 (type, region, platform, rate, service) Values (%s, %s, %s, %s, %s)",
                    (db_type, db_region, db_platform, db_rate, db_service))

                    sanity += 1

        print sanity

        self.conn.commit()
        self.cur.close()
        self.conn.close()


    def make_demand_table(self):
        self.cur.execute("select * from information_schema.tables where table_name=%s;", ('ondemand_rate_plan_v4',))
        if bool(self.cur.rowcount):
            self.cur.execute("DROP TABLE ondemand_rate_plan_v4;")
        self.cur.execute("""CREATE TABLE ondemand_rate_plan_v4 (

  type character varying NOT NULL,

  region character varying NOT NULL,

  platform character varying NOT NULL,

  rate double precision,

  service character varying NOT NULL,

  lastupdated timestamp without time zone DEFAULT now(),

  CONSTRAINT ondemand_rate_plan_v4_pkey PRIMARY KEY (type, region, platform, service)

);""")
