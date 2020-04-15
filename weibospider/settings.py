# -*- coding: utf-8 -*-

BOT_NAME = 'spider'

SPIDER_MODULES = ['spiders']
NEWSPIDER_MODULE = 'spiders'

ROBOTSTXT_OBEY = False

DEFAULT_REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:61.0) Gecko/20100101 Firefox/61.0',
}

# https://docs.scrapy.org/en/latest/topics/settings.html#concurrent-requests
CONCURRENT_REQUESTS = 4

# https://docs.scrapy.org/en/latest/topics/settings.html#std:setting-DOWNLOAD_DELAY
DOWNLOAD_DELAY = 0.5

# https://docs.scrapy.org/en/latest/topics/settings.html#download-timeout
DOWNLOAD_TIMEOUT = 3

# https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#retry-times
RETRY_TIMES = 20

DOWNLOADER_MIDDLEWARES = {
    'weibo.middlewares.UserAgentMiddleware': None,
    'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': None,
    'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': None,
    'middlewares.CookieMiddleware': 300,
    'middlewares.RedirectMiddleware': 200,
    'middlewares.IPProxyMiddleware': 100,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 101,

}

ITEM_PIPELINES = {
    'pipelines.MongoDBPipeline': 300,
}

# MongoDb Config
MONGO_HOST = 'mongodb'
MONGO_PORT = 27017


# Redis Config
REDIS_HOST = 'redis'
REDIS_PORT = 6379

# Ensure use this Scheduler
SCHEDULER = "scrapy_redis_bloomfilter.scheduler.Scheduler"

# Ensure all spiders share same duplicates filter through redis
DUPEFILTER_CLASS = "scrapy_redis_bloomfilter.dupefilter.RFPDupeFilter"

# Redis URL
REDIS_URL = 'redis://{}:{}'.format(REDIS_HOST, REDIS_PORT)

# Number of Hash Functions to use, defaults to 6
BLOOMFILTER_HASH_NUMBER = 6

# Redis Memory Bit of Bloomfilter Usage, 30 means 2^30 = 128MB, defaults to 30
BLOOMFILTER_BIT = 31

# Persist
SCHEDULER_PERSIST = True