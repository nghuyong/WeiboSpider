# encoding: utf-8


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

    def get_cookie(self) -> str:
        """
        获取cookie，从cookie池中轮流返回调用
        """

        cookie = self.pool[self.i]
        self.i = (self.i + 1) % len(self.pool)
        return cookie

    def process_request(self, request, spider):
        """
        对请求设置cookie
        """

        request.headers['Cookie'] = bytes(self.get_cookie(), 'utf-8')
