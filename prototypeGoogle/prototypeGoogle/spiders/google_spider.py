import scrapy
import csv
import psycopg2


class GoogleSpider(scrapy.Spider):
    name = "google"

    def start_requests(self):
        urls = [
            #'https://cloud.google.com/appengine/pricing',
            #'https://cloud.google.com/bigquery/pricing',
            #'https://cloud.google.com/bigtable/pricing',
            'https://cloud.google.com/compute/pricing',
            #'https://cloud.google.com/container-engine/pricing',
            #'https://cloud.google.com/dataflow/pricing',
            #'https://cloud.google.com/dataproc/docs/resources/pricing',
            #'https://cloud.google.com/datastore/#pricing',
            #'https://cloud.google.com/pubsub/pricing',
            #'https://cloud.google.com/dns/pricing',
            #'https://cloud.google.com/sql/pricing',
            #'https://cloud.google.com/storage/pricing',
            #'https://cloud.google.com/prediction/pricing',
            #'https://cloud.google.com/translate/v2/pricing',
            #'https://cloud.google.com/vision/pricing',
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)
# For google vm postgres table
# - id
# - instance_type
# - hourly rate
# - typical price 
# - hourly rate without sustained
# - hourly rate preemptible 
# - region
# - platform
# - last updated (timestamp)


    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = 'google-%s.csv' % page
        try:
            conn = psycopg2.connect("dbname='testdb' user='postgres' host='localhost' password='whatisthematrix'")
        except:
            print "UNABLE TO CONNECT TO DATABASE"

        cur = conn.cursor()

        cur.execute("""SELECT * from test""")

        rows = cur.fetchall()
        
        print "\nShow me the databases:\n"
        for row in rows:
            print "     ", row[1]

        with open(filename, 'wb') as csvfile:
            tablewriter = csv.writer(csvfile,quoting=csv.QUOTE_MINIMAL)

            for table in response.css('table'):
                headerArray = []
                i = 0    
                for header in table.css('th::text').extract():
                    print(header, i)
                    headerArray.append(header)
                    i += 1

                tablewriter.writerow(headerArray)
                for row in table.css('tr'):
                    j = 0
                    rowArray = []
                    for item in row.css('td::text').extract():
                        print(item, j)
                        rowArray.append(item)
                        j += 1
                    tablewriter.writerow(rowArray)
                    #if length(rowArray) => 5:
                     #   instanceType = rowArray[0]
                      #  region = "US"
                       # hourlyRate = rowArray[3]
                        #preemptiblePrice = rowArray[4]
                    
                    #cur.execute("""INSERT INTO gcp_compute_pricing (instance_type, hourly_rate_full_lowest_price_with_full_sustained_usage, hourly_rate_preemptible_price_per_hour, region) VALUES ()")

                
                #tablewriter.writerow([''])

