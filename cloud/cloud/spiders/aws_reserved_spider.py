## docker run -p 5023:5023 -p 8050:8050 -p 8051:8051 scrapinghub/splash
## scrapy shell 'http://localhost:8050/render.html?url=https://aws.amazon.com/ec2/pricing/on-demand/&timeout=10&wait=0.5'

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

class AWSReservedSpider(scrapy.Spider):
    name = "aws_reserved"


    def __init__(self):
        self.conn = psycopg2.connect("dbname='testdb' user='docker' host='localhost' password='docker'")
        self.cur = self.conn.cursor()
        self.url = 'http://localhost:8050/render.html?url=https://aws.amazon.com/ec2/pricing/reserved-instances/pricing/&timeout=10&wait=0.5'

        self.total_entries = 28320
        self.scrape_attempts = 0


    def start_requests(self):
        self.make_reserved_table()
        yield SplashRequest(self.url, self.parse, dont_filter=True, args={'wait':0.5})


    def parse(self, response):
        db_type = ''
        db_region = ''
        db_platform = ''
        db_utilitization = '' # Not used yet
        db_term = ''
        db_rate = 0.0
        db_upfront = 0.0
        db_service = '' # Not used yet
        db_timestamp = 0


        tabs = response.xpath('//div[@class="section tab-wrapper"]').xpath('.//li/a/text()').extract()
        tab_count = 0
        entry_count = 0

        platforms = response.xpath('//div[@class="tab-content"]/div')
        for platform in platforms:
            db_platform = tabs[tab_count]

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

                            self.cur.execute("INSERT INTO reserved_rate_plan_v3 (type, region, platform, utilization, term, rate, upfront, service) Values (%s, %s, %s, %s, %s, %s, %s, %s)",
                            (db_type, db_region, db_platform, db_utilitization, db_term, db_rate, db_upfront, db_service))

                            entry_count += 1

            tab_count += 1


        print "Attempt " + str(self.scrape_attempts)
        print "Scraped " + str(entry_count) + " out of " + str(self.total_entries)

        if entry_count < self.total_entries :
            if self.scrape_attempts < 10:
                print "Going to attempt to scrape again..."
                self.scrape_attempts += 1
                self.make_reserved_table()
                yield SplashRequest(self.url, self.parse, dont_filter=True, args={'wait':0.5})
            else:
                print "Reached max number of scrapes. Either run again for this spider or check if anything is wrong."
                self.cur.close()
                self.conn.close()
        else:
            if entry_count > self.total_entries :
                print "Scraped more than we expected. Might want to check if anything changed on the page. Continuing..."
            self.conn.commit()
            self.cur.close()
            self.conn.close()




    def make_reserved_table(self):
        self.cur.execute("select * from information_schema.tables where table_name=%s;", ('reserved_rate_plan_v3',))
        if bool(self.cur.rowcount):
            self.cur.execute("DROP TABLE reserved_rate_plan_v3;")
        self.cur.execute("""CREATE TABLE reserved_rate_plan_v3 (

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
