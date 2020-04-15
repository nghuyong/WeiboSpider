# encoding: utf-8
import random

import pymongo
from settings import MONGO_PORT, MONGO_HOST


class CookieMiddleware(object):
    """
    每次请求都随机从账号池中选择一个账号去访问
    """

    def __init__(self):
        client = pymongo.MongoClient(MONGO_HOST, MONGO_PORT)
        self.account_collection = client['weibo']['account']

    def process_request(self, request, spider):
        all_count = self.account_collection.find({'status': 'success'}).count()
        if all_count == 0:
            raise Exception('Current account pool is empty!! The spider will stop!!')
        random_index = random.randint(0, all_count - 1)
        random_account = self.account_collection.find({'status': 'success'})[random_index]
        request.headers.setdefault('Cookie', random_account['cookie'])
        request.meta['account'] = random_account


class RedirectMiddleware(object):
    """
    check account status
    HTTP Code = 302/418 -> cookie is expired or banned, and account status will change to 'error'
    """

    def __init__(self):
        client = pymongo.MongoClient(MONGO_HOST, MONGO_PORT)
        self.account_collection = client['weibo']['account']

    def process_response(self, request, response, spider):
        http_code = response.status
        if http_code == 302 or http_code == 403:
            self.account_collection.find_one_and_update({'_id': request.meta['account']['_id']},
                                                        {'$set': {'status': 'error'}}, )
            return request
        elif http_code == 418:
            spider.logger.error('IP Proxy is invalid, please change the ip proxy or stop the programme!')
            return request
        else:
            return response


class IPProxyMiddleware(object):

    def fetch_proxy(self):
        # You need to rewrite this function if you want to add proxy pool
        # the function should return a ip in the format of "ip:port" like "12.34.1.4:9090"
        return None

    def process_request(self, request, spider):
        proxy_data = self.fetch_proxy()
        if proxy_data:
            current_proxy = f'http://{proxy_data}'
            spider.logger.debug(f"current proxy:{current_proxy}")
            request.meta['proxy'] = current_proxy
