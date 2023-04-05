# encoding: utf-8
from scrapy.exceptions import CloseSpider
from threading import Lock
import logging
from requests import get


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

    pool = []               # Store cookies.
    i = 0                   # Cookie index, for rotate cookie.
    cookie_status = {}      # Record cookie failed times.
    lock = Lock()           # For concurrent get cookie and modify cookie status.


    def __init__(self):
        """
        Middleware初始化，加载文件中的所有cookie并测试cookie可用性。
        """

        # Load cookies from file.
        with open('cookies.txt') as f:
            cookies = [l.strip() for l in f.readlines()]
        # Test cookies available.
        for cookie in cookies:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:61.0) Gecko/20100101 Firefox/61.0',
                'Cookie': cookie
            }
            r = get('https://s.weibo.com/weibo?q=123', headers=headers, allow_redirects=False)
            if r.status_code in [302, 301]:
                logger.warning(f'Cookie not available! - {cookie}')
            else:
                self.pool.append(cookie)
                self.cookie_status[cookie] = 0
        logger.info(f'Available cookie count: {len(self.pool)}')

    def get_cookie_b(self) -> bytes:
        """
        Cookie pool api

        If cookie failed consecutive for 5 times, regard as expired, remove from pool.
        Cookie success for once cookie failure will be reset.
        """

        if not self.pool:
            raise CloseSpider('No cookie available!')
        else:
            cookie = None
            while not cookie:
                # TODO - Log pool length for every minute.
                # print(f'[DEBUG] - len(pool)={len(self.pool)}, i={self.i}')
                cookie = self.pool[self.i]
                if self.cookie_status[cookie] >= 5:
                    self.pool.remove(cookie)
                    logger.warning(f'Cookie removed(expired)! - {cookie}')
                    if not self.pool:
                        raise CloseSpider('No cookie available!')
                    self.i = 0
                    cookie = None
                else:
                    self.i = (self.i + 1) % len(self.pool)
            # print(f'[DEBUG] - cookie_now = {cookie_now}')
            return bytes(cookie, 'utf-8')

    def process_request(self, request, spider):
        """
        对请求设置cookie
        """

        with self.lock:
            request.headers['Cookie'] = self.get_cookie_b()

    def process_response(self, request, response, spider):
        """
        验证cookie是否过期，处理过期cookie
        """

        cookie = request.headers['cookie'].decode('utf-8')

        # TODO - Only check search spider, check others.
        with self.lock:
            if response.status in [301, 302]:
                # Cookie expired, request again
                self.cookie_status[cookie] += 1
                request.headers['cookie'] = self.get_cookie_b()
                request.dont_filter = True
                return request
            else:
                # Signal to tell cookie is alive.
                self.cookie_status[cookie] = 0
                return response
