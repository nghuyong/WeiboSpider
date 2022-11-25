#!/usr/bin/env python
# encoding: utf-8
"""
Author: rightyonghu
Created Time: 2022/10/22
"""
import json
import re
from scrapy import Spider, Request
from spiders.common import parse_tweet_info, parse_long_tweet


class SearchSpider(Spider):
    """
    关键词搜索采集
    """
    name = "search_spider"
    base_url = "https://s.weibo.com/"

    def start_requests(self):
        """
        爬虫入口
        """
        # 这里keywords可替换成实际待采集的数据
        keywords = ['丽江']
        start_time = "2022-10-01-0"  # 格式为 年-月-日-小时, 2022-10-01-0 表示2022年10月1日0时
        end_time = "2022-10-07-23"  # 格式为 年-月-日-小时, 2022-10-07-23 表示2022年10月7日23时
        is_search_with_specific_time_scope = True  # 是否在指定的时间区间进行推文搜索
        is_sort_by_hot = True  # 是否按照热度排序,默认按照时间排序
        for keyword in keywords:
            if is_search_with_specific_time_scope:
                url = f"https://s.weibo.com/weibo?q={keyword}&timescope=custom%3A{start_time}%3A{end_time}&page=1"
            else:
                url = f"https://s.weibo.com/weibo?q={keyword}&page=1"
            if is_sort_by_hot:
                url += "&xsort=hot"
            yield Request(url, callback=self.parse, meta={'keyword': keyword})

    def parse(self, response, **kwargs):
        """
        网页解析
        """
        html = response.text
        tweet_ids = re.findall(r'\d+/(.*?)\?refer_flag=1001030103_\'\)">复制微博地址</a>', html)
        for tweet_id in tweet_ids:
            url = f"https://weibo.com/ajax/statuses/show?id={tweet_id}"
            yield Request(url, callback=self.parse_tweet, meta=response.meta)
        next_page = re.search('<a href="(.*?)" class="next">下一页</a>', html)
        if next_page:
            url = "https://s.weibo.com" + next_page.group(1)
            yield Request(url, callback=self.parse, meta=response.meta)

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
            yield Request(url, callback=parse_long_tweet, meta={'item': item})
        else:
            yield item
