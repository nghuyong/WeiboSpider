#!/usr/bin/env python
# encoding: utf-8
"""
Author: rightyonghu
Created Time: 2022/10/22
"""
import datetime
import json
import re
import logging
from scrapy import Spider, Request
from scrapy.exceptions import IgnoreRequest
from spiders.common import parse_tweet_info, parse_long_tweet

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('weibo_spider.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

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
        keywords = ['房价']
        # 设置固定的时间范围：2020.01.01 - 2023.06.30
        start_time = datetime.datetime(2020, 1, 1, 0, 0, 0)
        end_time = datetime.datetime(2023, 6, 30, 23, 59, 59)
        
        logger.info(f"Starting spider for keywords: {keywords}")
        logger.info(f"Time range: {start_time} to {end_time}")
        
        # 是否按照小时进行切分，数据量更大; 对于非热门关键词**不需要**按照小时切分
        is_split_by_hour = True
        
        total_requests = 0
        for keyword in keywords:
            if not is_split_by_hour:
                _start_time = start_time.strftime("%Y-%m-%d-%H")
                _end_time = end_time.strftime("%Y-%m-%d-%H")
                url = f"https://s.weibo.com/weibo?q={keyword}&timescope=custom%3A{_start_time}%3A{_end_time}&page=1"
                total_requests += 1
                yield Request(url, callback=self.parse, meta={'keyword': keyword})
            else:
                time_cur = start_time
                while time_cur < end_time:
                    _start_time = time_cur.strftime("%Y-%m-%d-%H")
                    _end_time = (time_cur + datetime.timedelta(hours=1)).strftime("%Y-%m-%d-%H")
                    url = f"https://s.weibo.com/weibo?q={keyword}&timescope=custom%3A{_start_time}%3A{_end_time}&page=1"
                    total_requests += 1
                    yield Request(url, callback=self.parse, meta={'keyword': keyword})
                    time_cur = time_cur + datetime.timedelta(hours=1)
        
        logger.info(f"Total search requests to be made: {total_requests}")

    def parse(self, response, **kwargs):
        """
        网页解析
        """
        html = response.text
        keyword = response.meta['keyword']
        current_url = response.url
        
        logger.info(f"Parsing search page for keyword '{keyword}': {current_url}")
        
        if '<p>抱歉，未找到相关结果。</p>' in html:
            logger.info(f'No search results found for keyword "{keyword}" at URL: {current_url}')
            return
            
        tweets_infos = re.findall('<div class="from"\s+>(.*?)</div>', html, re.DOTALL)
        tweet_count = 0
        for tweets_info in tweets_infos:
            tweet_ids = re.findall(r'weibo\.com/\d+/(.+?)\?refer_flag=1001030103_" ', tweets_info)
            for tweet_id in tweet_ids:
                tweet_count += 1
                url = f"https://weibo.com/ajax/statuses/show?id={tweet_id}"
                yield Request(url, callback=self.parse_tweet, meta=response.meta, priority=10)
        
        logger.info(f"Found {tweet_count} tweets on page for keyword '{keyword}'")
        
        next_page = re.search('<a href="(.*?)" class="next">下一页</a>', html)
        if next_page:
            url = "https://s.weibo.com" + next_page.group(1)
            logger.info(f"Following next page for keyword '{keyword}': {url}")
            yield Request(url, callback=self.parse, meta=response.meta)

    @staticmethod
    def parse_tweet(response):
        """
        解析推文
        """
        try:
            data = json.loads(response.text)
            item = parse_tweet_info(data)
            item['keyword'] = response.meta['keyword']
            
            logger.info(f"Successfully parsed tweet {item.get('mblogid', 'unknown')} for keyword '{item['keyword']}'")
            
            if item['isLongText']:
                url = "https://weibo.com/ajax/statuses/longtext?id=" + item['mblogid']
                logger.info(f"Fetching long text for tweet {item['mblogid']}")
                yield Request(url, callback=parse_long_tweet, meta={'item': item}, priority=20)
            else:
                yield item
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON for tweet at URL: {response.url}")
            raise IgnoreRequest("Invalid JSON response")
        except Exception as e:
            logger.error(f"Error processing tweet: {str(e)}")
            raise IgnoreRequest(f"Error processing tweet: {str(e)}")
