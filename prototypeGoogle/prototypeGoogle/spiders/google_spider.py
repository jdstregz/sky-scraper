import scrapy
import csv

class GoogleSpider(scrapy.Spider):
    name = "google"

    def start_requests(self):
        urls = [
            'https://cloud.google.com/appengine/pricing',
            'https://cloud.google.com/bigquery/pricing',
            'https://cloud.google.com/bigtable/pricing',
            'https://cloud.google.com/compute/pricing',
            'https://cloud.google.com/container-engine/pricing',
            'https://cloud.google.com/dataflow/pricing',
            'https://cloud.google.com/dataproc/docs/resources/pricing',
            'https://cloud.google.com/datastore/#pricing',
            'https://cloud.google.com/pubsub/pricing',
            'https://cloud.google.com/dns/pricing',
            'https://cloud.google.com/sql/pricing',
            'https://cloud.google.com/storage/pricing',
            'https://cloud.google.com/prediction/pricing',
            'https://cloud.google.com/translate/v2/pricing',
            'https://cloud.google.com/vision/pricing',
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = 'google-%s.csv' % page
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
            
                tablewriter.writerow([''])
                    
                    
        #page = response.url.split("/")[-2]
        #filename = '%s.html' % page
        #with open(filename, 'wb') as f:
        #    f.write(response.body)
        #self.log('Saved file %s' % filename)


    # response.cc('td::text').extract()
    # 

#
#with open('eggs.csv', 'wb') as csvfile:
#    spamwriter = csv.writer(csvfile, delimiter=' ',
#                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
#    spamwriter.writerow(['Spam'] * 5 + ['Baked Beans'])
#    spamwriter.writerow(['Spam', 'Lovely Spam', 'Wonderful Spam'])