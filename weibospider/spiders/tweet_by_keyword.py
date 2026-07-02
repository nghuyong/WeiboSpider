#!/usr/bin/env python
# encoding: utf-8
"""
Author: rightyonghu
Created Time: 2022/10/22
"""
import datetime
import json
import re
from scrapy import Spider, Request
from .common import parse_tweet_info, parse_long_tweet


class TweetSpiderByKeyword(Spider):
    """
    关键词搜索采集
    """
    name = "tweet_spider_by_keyword"
    base_url = "https://s.weibo.com/"

    def start_requests(self):
        """
        爬虫入口
        """
        # 这里keywords可替换成实际待采集的数据
        keywords = ['丽江']
        # 这里的时间可替换成实际需要的时间段
        start_time = datetime.datetime(year=2022, month=10, day=1, hour=0)
        end_time = datetime.datetime(year=2022, month=10, day=7, hour=23)
        # 是否按照小时进行切分，数据量更大; 对于非热门关键词**不需要**按照小时切分
        is_split_by_hour = True
        for keyword in keywords:
            if not is_split_by_hour:
                _start_time = start_time.strftime("%Y-%m-%d-%H")
                _end_time = end_time.strftime("%Y-%m-%d-%H")
                url = f"https://s.weibo.com/weibo?q={keyword}&timescope=custom%3A{_start_time}%3A{_end_time}&page=1"
                yield Request(url, callback=self.parse, meta={'keyword': keyword})
            else:
                time_cur = start_time
                while time_cur < end_time:
                    _start_time = time_cur.strftime("%Y-%m-%d-%H")
                    _end_time = (time_cur + datetime.timedelta(hours=1)).strftime("%Y-%m-%d-%H")
                    url = f"https://s.weibo.com/weibo?q={keyword}&timescope=custom%3A{_start_time}%3A{_end_time}&page=1"
                    yield Request(url, callback=self.parse, meta={'keyword': keyword})
                    time_cur = time_cur + datetime.timedelta(hours=1)

    def parse(self, response, **kwargs):
        """
        网页解析
        """
        html = response.text
        self.logger.info(f"Response length: {len(html)}")
        self.logger.info(f"Response content: {html}")  # 查看响应的具体内容
        
        if '<p>抱歉，未找到相关结果。</p>' in html:
            self.logger.info(f'No search result. url: {response.url}')
            return
        
        # 尝试不同的正则表达式提取微博ID
        tweet_ids = []
        
        # 尝试原始的正则表达式
        tweets_infos = re.findall('<div class="from"\s+>(.*?)</div>', html, re.DOTALL)
        self.logger.info(f'Found {len(tweets_infos)} tweet info sections')
        
        for tweets_info in tweets_infos:
            found_ids = re.findall(r'weibo\.com/\d+/(.+?)\?refer_flag=1001030103_" ', tweets_info)
            tweet_ids.extend(found_ids)
            self.logger.info(f'Found {len(found_ids)} tweet IDs in this section')
        
        # 尝试其他可能的正则表达式
        if len(tweet_ids) == 0:
            self.logger.info("Trying alternative regex patterns...")
            # 尝试不同的模式
            alt_patterns = [
                r'weibo\.com/\d+/([a-zA-Z0-9]+)\?',
                r'mblogid=([a-zA-Z0-9]+)',
                r'/([a-zA-Z0-9]+)\?refer_flag'
            ]
            
            for pattern in alt_patterns:
                alt_ids = re.findall(pattern, html)
                if alt_ids:
                    tweet_ids.extend(alt_ids)
                    self.logger.info(f'Found {len(alt_ids)} tweet IDs with pattern: {pattern}')
        
        self.logger.info(f'Total found tweet IDs: {len(tweet_ids)}')
        
        for tweet_id in tweet_ids:
            url = f"https://weibo.com/ajax/statuses/show?id={tweet_id}"
            self.logger.info(f'Fetching tweet: {tweet_id}')
            yield Request(url, callback=self.parse_tweet, meta=response.meta, priority=10)
        
        # 查找下一页
        next_page = re.search('<a href="(.*?)" class="next">下一页</a>', html)
        if next_page:
            url = "https://s.weibo.com" + next_page.group(1)
            self.logger.info(f'Found next page: {url}')
            yield Request(url, callback=self.parse, meta=response.meta)
        else:
            self.logger.info('No next page found')

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
            yield Request(url, callback=parse_long_tweet, meta={'item': item}, priority=20)
        else:
            yield item
