import scrapy

class GoogleSpider(scrapy.Spider):
    name = "google"

    def start_requests(self):
        urls = [
            'https://cloud.google.com/appengine/pricing',
            #'https://cloud.google.com/bigquery/pricing',
            #'https://cloud.google.com/bigtable/pricing',
            #'https://cloud.google.com/compute/pricing',
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
            #'https://cloud.google.com/support/'
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        for table in response.css('table'):
            i = 0
            
            for header in table.css('th::text').extract():
                print(header, i)
                i += 1
            for row in table.css('tr::text').extract():
                j = 0
                for 
                print(item, j)
                j += 1
        #page = response.url.split("/")[-2]
        #filename = '%s.html' % page
        #with open(filename, 'wb') as f:
        #    f.write(response.body)
        #self.log('Saved file %s' % filename)


    # response.cc('td::text').extract()
    # 