# -*- coding: utf-8 -*-

BOT_NAME = 'sina'

SPIDER_MODULES = ['sina.spiders']
NEWSPIDER_MODULE = 'sina.spiders'

ROBOTSTXT_OBEY = False

DEFAULT_REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:61.0) Gecko/20100101 Firefox/61.0',
}

# Set logger:
LOG_LEVEL = 'INFO'  # to only display errors
LOG_FORMAT = '%(asctime)19s %(name)16s %(levelname)8s | %(message)s'
#LOG_FILE = 'log.txt'

# CONCURRENT_REQUESTS 和 DOWNLOAD_DELAY 根据账号池大小调整 目前的参数是账号池大小为200

CONCURRENT_REQUESTS = 128

DOWNLOAD_DELAY = 0.01

DOWNLOADER_MIDDLEWARES = {
	'scrapy.downloadermiddlewares.httpcache.HttpCacheMiddleware': 0,
    'weibo.middlewares.UserAgentMiddleware': None,
    'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': None,
    'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': None,
    'sina.middlewares.CookieMiddleware': 300,
    'sina.middlewares.RedirectMiddleware': 200,
}

ITEM_PIPELINES = {
    'sina.pipelines.MongoDBPipeline': 300,
}

HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.DbmCacheStorage'

# MongoDb 配置

LOCAL_MONGO_HOST = '127.0.0.1'
LOCAL_MONGO_PORT = 27017
DB_NAME = 'Sina'

# Redis 配置
LOCAL_REDIS_HOST = '127.0.0.1'
LOCAL_REDIS_PORT = 6379


# Ensure use this Scheduler
SCHEDULER = "scrapy_redis_bloomfilter.scheduler.Scheduler"

# Ensure all spiders share same duplicates filter through redis
DUPEFILTER_CLASS = "scrapy_redis_bloomfilter.dupefilter.RFPDupeFilter"

# Number of Hash Functions to use, defaults to 6
BLOOMFILTER_HASH_NUMBER = 6

# Redis Memory Bit of Bloomfilter Usage, 30 means 2^30 = 128MB, defaults to 30
BLOOMFILTER_BIT = 31

# Persist
SCHEDULER_PERSIST = True