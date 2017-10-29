import random
from sina.cookies import cookies, init_cookies
from sina.user_agents import agents


class UserAgentMiddleware(object):
    """ 换User-Agent """

    def process_request(self, request, spider):
        agent = random.choice(agents)
        request.headers["User-Agent"] = agent


class CookiesMiddleware(object):
    """ 换Cookie """

    def __init__(self):
        init_cookies()

    def process_request(self, request, spider):
        cookie = random.choice(cookies)
        request.cookies = cookie


