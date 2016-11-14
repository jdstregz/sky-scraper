import scrapy
import csv
import psycopg2
import re
from scrapy_splash import SplashRequest


class GoogleSpider(scrapy.Spider):
    name = "googlev2"

    def start_requests(self):
        urls = [
            'https://cloud.google.com/compute/pricing',
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)
            #yield SplashRequest(url, self.parse, args={'wait':0.5})

    def parse(self, response):
        # create file names for the outputted csv files (will remove after database implementation)
        page = response.url.split("/")
        filename = 'google-%s.csv' % page

        # attempt connection to the postgresql database
        try:
            conn = psycopg2.connect("dbname='testdb' user='docker' host='localhost' password='docker'")
        except:
            print "UNABLE TO CONNECT TO DATABASE. IS YOUR DOCKER RUNNING? HMMM"
        # this is a test to see if table output can happen
        cur = conn.cursor()
        cur.execute("""SELECT * from test""")
        rows = cur.fetchall()
        print "\nShow me the databases:\n"
        for row in rows:
            print "     ", row[1]

        # open the csvfile before scrape parsing
        with open(filename, 'wb') as csvfile:
            tablewrite = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)

            # search through all tables in the page
            tables = response.xpath('//table')

            # create an htmlxpathselector
            hxs = scrapy.selector.HtmlXPathSelector(response)

            # Extract all data for each table and place in list
            for table in tables:

                for header in table.xpath('.//thead'):
                    header_array = []
                    i = 0
                    # print out headings and append to header_array
                    for header in table.xpath('.//th/text()').extract():
                        print(header, i)
                        header_array.append(header)
                        i += 1
                    # write heading row to csv file
                    tablewrite.writerow(header_array)
                # go through table body
                for body in table.xpath('.//tbody'):
                    for row in body.xpath('//tr'):
                        j = 0
                        row_array = []
                        for item in row.xpath('.//td').extract():
                            output = re.findall(r'us-hourly=\"(.+?)\"', item)
                            print output
                            print(item, j)
                            row_array.append(item)
                            j += 1
                        tablewrite.writerow(row_array)




