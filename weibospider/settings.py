# -*- coding: utf-8 -*-

BOT_NAME = 'spider'

SPIDER_MODULES = ['spiders']
NEWSPIDER_MODULE = 'spiders'

ROBOTSTXT_OBEY = False

# change cookie to yours
DEFAULT_REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:61.0) Gecko/20100101 Firefox/61.0',
    'Cookie': 'OUTFOX_SEARCH_USER_ID_NCOO=1521427420.3020706; SCF=AlvwCT3ltiVc36wsKpuvTV8uWF4V1tZ17ms9t-bZCAuiV-ZsmkYB9TEWXW7sd-gDxW34UesUalWH5lMgGsFIVAY.; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WWYACoMUZFHDoS6U9MYf.vu5NHD95Qce0zNSo-f1hq0Ws4DqcjzdJUQUPLadJMt; SUB=_2A25NMZbHDeRhGeBN6VUX9SvEzT-IHXVu3TqPrDV6PUJbkdAKLXnikW1NRJ24IENfNQhgKlnrWsrJzXjq5AY_x0Mb; _T_WM=391c3b6aaf54f1ca5a8688cdd9cfec2c'}

CONCURRENT_REQUESTS = 16

DOWNLOAD_DELAY = 3

DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': None,
    'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': None,
    'middlewares.IPProxyMiddleware': 100,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 101,
}

ITEM_PIPELINES = {
    'pipelines.MongoDBPipeline': 300,
}

MONGO_HOST = '127.0.0.1'
MONGO_PORT = 27017
