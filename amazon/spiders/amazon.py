import scrapy
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher

import pandas as pd

class AmazonSpider(scrapy.Spider):
    name = "amazon"
    keyword = "자전거"
    def __init__(self):
        dispatcher.connect(self.spider_closed, signals.spider_closed)
        self.data = []

    def start_requests(self):
        urls = [
	    'http://m.bunjang.co.kr/search/products?q=' + keyword
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        num = response.css('.tit_rst')[0].css('strong::text')[0].extract()
        num = int(num)
        index = num / 10
        if index > 10: index = 10
        for i in range(index):
            url = str(response.url) + "&page=" + str(i)
            yield scrapy.Request(url=url, callback=self.parse_list, meta={'page': i})
    def parse_list(self, response):
        data = response.css('.goodslist_03')[1].css('li')
        print(response.meta.get('page'))
        for product in data:
            url = product.css('a::attr(href)')[0].extract()
            name = product.css('.name::text')[0].extract()
            price  = product.css('.price')[0].css('em::text')[0].extract()
            
            data = [name, price, url]
            self.data.append(data)
    def spider_closed(self, spider):
        print("End of spider")
        my_df = pd.DataFrame(self.data)
        my_df.to_csv('output.csv', index=False, header=False)
