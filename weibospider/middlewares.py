# encoding: utf-8
from scrapy.exceptions import StopDownload


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

    def __init__(self):
        """
        Middleware初始化，加载文件中的所有cookie。
        """

        self.pool = []
        self.i = 0
        with open('cookies.txt') as f:
            self.pool = f.readlines()

    def process_request(self, request, spider):
        """
        对请求设置cookie
        """

        cookie = self.pool[self.i]
        self.i = (self.i + 1) % len(self.pool)
        request.headers['Cookie'] = bytes(cookie, 'utf-8')

    def process_response(self, request, response, spider):
        """
        验证cookie是否过期，处理过期cookie
        """

        if spider.name == 'search_spider' and response.status in [301, 302]:
            if len(self.pool) == 1:
                spider.logger.warn('No cookie available!')
                StopDownload()
            spider.logger.warn(f"Cookie expired: {request.headers['cookie']}")
            self.pool.remove(request.headers['cookie'].decode('utf-8'))
            # Cookie expired, request again
            request.headers['cookie'] = self.pool[0]
            request.dont_filter = True
            return request
        else:
            return response
