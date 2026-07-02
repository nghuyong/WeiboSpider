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


class WeiboSpiderMiddleware(object):
    """
    微博爬虫中间件，添加必要的请求头
    """

    def process_request(self, request, spider):
        """
        处理请求，添加必要的请求头
        """
        import os
        # 读取cookie.txt文件中的Cookie值
        cookie_path = os.path.join(os.path.dirname(__file__), 'cookie.txt')
        if os.path.exists(cookie_path):
            with open(cookie_path, 'r', encoding='utf-8') as f:
                cookie = f.read().strip()
            request.headers['Cookie'] = cookie
            spider.logger.info(f"Cookie loaded: {cookie[:50]}...")  # 只显示前50个字符
        else:
            spider.logger.error(f"Cookie file not found: {cookie_path}")
        
        # 添加User-Agent
        request.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
        # 添加Referer
        request.headers['Referer'] = 'https://weibo.com/'
        # 添加Accept-Language
        request.headers['Accept-Language'] = 'zh-CN,zh;q=0.9'
        # 添加Accept
        request.headers['Accept'] = 'application/json, text/plain, */*'
        return None
