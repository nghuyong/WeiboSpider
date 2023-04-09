# encoding: utf-8
from scrapy.exceptions import CloseSpider
from threading import Lock
import logging
from requests import get
import json


logger = logging.getLogger(__name__)

class IPProxyMiddleware(object):
    """
    代理IP中间件
    """

    @staticmethod
    def fetch_proxy():
        """
        获取一个代理IP
        """
        # You need to rewrite this function if you want to add proxy pool
        # the function should return an ip in the format of "ip:port" like "12.34.1.4:9090"
        return None

    def process_request(self, request, spider):
        """
        将代理IP添加到request请求中
        """
        proxy_data = self.fetch_proxy()
        if proxy_data:
            current_proxy = f'http://{proxy_data}'
            spider.logger.debug(f"current proxy:{current_proxy}")
            request.meta['proxy'] = current_proxy

class CookiePoolMiddleware():
    """
    Cookie池中间件
    """

    ##### pool structure #####
    # pool = {
    #    "cookie name": {                       cookie name in cookies.json
    #        "cookie": "<cookie example>",      cookie value in cookies.json
    #        "status": 0                        for record failed times
    #    }
    # }
    ##########################
    pool = {}
    ck_names = []           # Cookie names.
    i = 0                   # Cookie index, for rotate cookie names.
    lock = Lock()           # For concurrent get cookie and modify cookie status.


    def __init__(self):
        """
        Middleware初始化，加载文件中的所有cookie并测试cookie可用性。
        """

        with open('cookies.json') as f:
            cookies = json.load(f)
        for ck_name in cookies.keys():
            cookie = cookies[ck_name].strip()

        # Test cookies available.
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:61.0) Gecko/20100101 Firefox/61.0',
                'Cookie': cookie
            }
            r = get('https://s.weibo.com/weibo?q=123', headers=headers, allow_redirects=False)
            if r.status_code in [302, 301]:
                logger.warning(f'Cookie not available! - name: {ck_name}, cookie: {cookie}')
            else:
                self.pool[ck_name] = {'cookie': cookie, 'status': 0}
                self.ck_names.append(ck_name)

        logger.info(f'Available cookie count: {len(self.pool)} - {self.ck_names}')
        if len(self.pool) == 0:
            # TODO - If no cookie available in init, exit program.
            pass

    def get_ck_name(self) -> bytes:
        """
        Cookie pool api

        If cookie failed consecutive for 5 times, regard as expired, remove from pool.
        Cookie success for once cookie failure will be reset.
        """

        if not self.ck_names:
            raise CloseSpider('No cookie available!')
        else:
            cookie = None
            while not cookie:
                ck_name = self.ck_names[self.i]
                cookie = self.pool[ck_name]['cookie']
                if self.pool[ck_name]['status'] >= 5:
                    self.pool.pop(ck_name)
                    self.ck_names.remove(ck_name)
                    logger.warning(f'Cookie removed(expired)! - name: {ck_name}, cookie: {cookie}')
                    logger.info(f'Available cookie count: {len(self.pool)}')
                    if not self.pool:
                        raise CloseSpider('No cookie available!')
                    self.i = 0
                    cookie = None
                else:
                    self.i = (self.i + 1) % len(self.pool)
            return ck_name

    def process_request(self, request, spider):
        """
        对请求设置cookie
        """

        with self.lock:
            ck_name = self.get_ck_name()
            request.headers['Cookie'] = bytes(self.pool[ck_name]['cookie'], 'utf-8')
            request.meta['ck_name'] = ck_name

    def process_response(self, request, response, spider):
        """
        验证cookie是否过期，处理过期cookie
        """

        cookie = request.headers['cookie'].decode('utf-8')

        # TODO - Only check search spider, check others.
        with self.lock:
            ck_name = request.meta['ck_name']
            if response.status in [301, 302, 400]:
                self.pool[ck_name]['status'] += 1
                new_ck_name = self.get_ck_name()
                request.headers['cookie'] = bytes(self.pool[new_ck_name]['cookie'], 'utf-8')
                request.dont_filter = True
                request.meta['ck_name'] = new_ck_name
                return request
            else:
                # Signal to tell cookie is alive.
                self.pool[ck_name]['status'] = 0
                return response
