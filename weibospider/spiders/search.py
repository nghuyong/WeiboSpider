#!/usr/bin/env python
# encoding: utf-8
"""
Author: rightyonghu
Created Time: 2022/10/22
"""
import json
import re
from datetime import datetime, timedelta
from scrapy import Spider, Request
from spiders.common import parse_tweet_info, parse_long_tweet


class SearchSpider(Spider):
    """
    关键词搜索采集
    """
    name = "search_spider"
    base_url = "https://s.weibo.com/"

    ###################### 可配置参数 ######################
    keyword = '北京'    # 检索关键词
    # format: yyyy-mm-dd-hh
    tf = "2023-03-28-00"    # time from
    tt = "2023-04-05-00"    # time to

    #---- 检索内容类型 ----#
    # default:  默认
    # hot:      热门
    # ori:      原创
    # verify:   认证用户
    # media:    媒体
    # all:      全部
    #--------------------#
    ct = 'all'  # content type

    #--- 检索内容限定包含 ---#
    # default:  默认
    # pic:      图片
    # video:    视频
    # link:     短链
    # all:      全部
    #----------------------#
    ci = 'all'  # content include
    ######################################################

    dt_parse_format = '%Y-%m-%d-%H'
    ctd = {     # content type dict
        'default': '',
        'hot': '&xsort=hot',
        'ori': '&scope=ori',
        'verify': 'vip=1',
        'media': 'category=4'
    }
    cid = {     # content include dict
        'default': '',
        'pic': '&haspic=1',
        'video': '&hasvideo=1',
        'link': '&haslink=1'
    }

    ctdr = {    # content type dict reverse, for log
        '': 'default',
        '&xsort=hot': 'hot',
        '&scope=ori': 'ori',
        'vip=1': 'verify',
        'category=4': 'media'
    }
    cidr = {    # content include dict reverse, for log
        '': 'default',
        '&haspic=1': 'pic',
        '&hasvideo=1': 'vedio',
        '&haslink=1': 'link'
    }

    def start_requests(self):
        """
        爬虫入口
        """

        self.logger.info(
            f'Search spider start...\n' +
            f'--- keyword: {self.keyword}\n' +
            f'--- from: {self.tf}\n' +
            f'--- to: {self.tt}\n' +
            f'--- content type: {self.ct}\n' +
            f'--- content include: {self.ci}'
        )

        # format datetime
        dt_from = datetime.strptime(self.tf, self.dt_parse_format)
        dt_to = datetime.strptime(self.tt, self.dt_parse_format)
        dt = dt_from

        # traverse timescope
        while(dt < dt_to):
            # traverse search content type and content include
            # scrapy会自动过滤重复web请求，最终爬取到的数据不会冗余
            dt_str_from = dt.strftime(self.dt_parse_format)
            dt_str_to = (dt + timedelta(hours=1)).strftime(self.dt_parse_format)
            self.logger.info(f"Crawling: keyword={self.keyword} timescope=:{dt_str_from}:{dt_str_to}")
            if self.ct == 'all' and self.ci == 'all':
                for ct in self.ctd.values():
                    for ci in self.cid.values():
                        yield self.search_req(dt, ct, ci)
            elif self.ci == 'all':
                for ci in self.cid.values():
                    yield self.search_req(dt, self.ctd[self.ct], ci)
            elif self.ct == 'all':
                for ct in self.ctd.values():
                    yield self.search_req(dt, ct, self.cid[self.ci])
            else:
                yield self.search_req(dt, self.ctd[self.ct], self.cid[self.ci])
            dt += timedelta(hours=1)

    def search_req(self, dt, ct, ci):
        """
        拼接url，返回search请求
        """

        dt_str_from = dt.strftime(self.dt_parse_format)
        dt_str_to = (dt + timedelta(hours=1)).strftime(self.dt_parse_format)

        url = (
            f"https://s.weibo.com/weibo?q={self.keyword}" +
            f"&timescope=custom%:{dt_str_from}:{dt_str_to}" +
            f"{ct}" +
            f"{ci}"
        )
        return Request(url, meta={'keyword': self.keyword})

    def parse(self, response, **kwargs):
        """
        检索结果页面解析
        """

        html = response.text
        if 'card-no-result' in html:
            pass
        else:
            tweet_ids = re.findall(r'weibo\.com/\d+/(.+?)\?refer_flag=1001030103_" ', html)
            for tweet_id in tweet_ids:
                url = f"https://weibo.com/ajax/statuses/show?id={tweet_id}"
                yield Request(url, callback=self.parse_tweet, meta=response.meta, priority=9)
            next_page = re.search('<a href="(.*?)" class="next">下一页</a>', html)
            if next_page:
                url = "https://s.weibo.com" + next_page.group(1)
                yield Request(url, callback=self.parse, meta=response.meta, priority=8)

    @staticmethod
    def parse_tweet(response):
        """
        解析推文
        """

        data = json.loads(response.text)
        item = parse_tweet_info(data)
        item['keyword'] = response.meta['keyword']
        if item['isLongText']:
            url = "https://weibo.com/ajax/statuses/longtext?id=" + item['mblogid']
            yield Request(url, callback=parse_long_tweet, meta={'item': item}, priority=10)
        else:
            yield item
