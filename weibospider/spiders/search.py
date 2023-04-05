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

    # 这里keywords可替换成实际待采集的数据
    keyword = '丽江'
    start_time = "2023-04-01-00"        # format: yyyy-mm-dd-hh
    end_time = "2023-04-04-23"

    def start_requests(self):
        """
        爬虫入口
        """

        dt_parse_str = '%Y-%m-%d-%H'
        # TODO set sort methods
        # is_sort_by_hot = True               # 是否按照热度排序,默认按照时间排序

        start_dt = datetime.strptime(self.start_time, dt_parse_str)
        end_dt = datetime.strptime(self.end_time, dt_parse_str)
        ahour_delta = timedelta(hours=1)

        dt = start_dt
        while(dt < end_dt):
            url = f"https://s.weibo.com/weibo?q={self.keyword}&timescope=custom%:{dt.strftime(dt_parse_str)}:{(dt + ahour_delta).strftime(dt_parse_str)}"
            # if is_sort_by_hot:
            #     url += "&xsort=hot"
            yield Request(url, callback=self.parse, meta={'keyword': self.keyword})
            dt += ahour_delta

    def parse(self, response, **kwargs):
        """
        检索结果页面解析
        """

        html = response.text
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
