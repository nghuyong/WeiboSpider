# -*- coding: utf-8 -*-

BOT_NAME = 'spider'

SPIDER_MODULES = ['spiders']
NEWSPIDER_MODULE = 'spiders'

ROBOTSTXT_OBEY = False

# change cookie to yours
DEFAULT_REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
    'Cookie': '_T_WM=34721861f0d8b03ed47adabed0e1ade8; SCF=AqVSTARJXRNZouo6nNF9xKz9Al9c_XbFdUndXfHBZANMf_O3I1wzz_pEtetOy0hNNNfGEZdvePHWT6mws0tpf34.; SUB=_2A25MAgzSDeRhGeNG6VEW-CbFzDSIHXVvDJSarDV6PUJbktCOLWzdkW1NS3quSpCtBv8GexSqIkwuF3tet7x7E4PT; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5-_hGmCeI-rYRjN3uql2sS5NHD95Qf1hz0S0nR1KMRWs4Dqcj-i--fi-z7iKysi--fi-2RiKnp9Jqt'}

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
