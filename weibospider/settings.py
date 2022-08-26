# -*- coding: utf-8 -*-

BOT_NAME = 'spider'

SPIDER_MODULES = ['spiders']
NEWSPIDER_MODULE = 'spiders'

ROBOTSTXT_OBEY = False

# change cookie to yours
DEFAULT_REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:61.0) Gecko/20100101 Firefox/61.0',
    'Cookie': 'SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9Wh9eBGkaC9wQ3PhJeh9NX_.5NHD95QpS0nE1h57eK-pWs4DqcjxKgvQqgf_qgxkBgpDwJ8.9gnt; SCF=AooKFXGlf0m7HsyOoy1_USSt0EmGm_vpQclLi5tPcfWu3QUO8POmUVyiHNtRA_v81uumHJybh86osfzp1q6sYdI.; SUB=_2A25P-0avDeRhGedJ41AZ8C7Nzj2IHXVtBGrnrDV6PUJbktANLRnskW1NUaL1YwWGjaJeO5oW2TWp8WEv84RAA3TC; _T_WM=81a8106cdddcb95a9bf80e4bb9a968d4; _WEIBO_UID=1782800151; MLOGIN=1; WEIBOCN_FROM=1110106030; XSRF-TOKEN=c15087; mweibo_short_token=0ba57c57e7; M_WEIBOCN_PARAMS=lfid%3D231093_-_selffollowed%26luicode%3D20000174%26uicode%3D20000174'}

CONCURRENT_REQUESTS = 16

DOWNLOAD_DELAY = 3

DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': None,
    'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': None,
    'middlewares.IPProxyMiddleware': 100,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 101,
}

ITEM_PIPELINES = {
    'pipelines.JsonWriterPipeline':300,
    # 'pipelines.MongoDBPipeline': 300,
}

MONGO_HOST = '127.0.0.1'
MONGO_PORT = 27017
