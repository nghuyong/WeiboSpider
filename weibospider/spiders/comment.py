#!/usr/bin/env python
# encoding: utf-8
"""
Author: rightyonghu
Created Time: 2022/10/24
"""
import json
import logging
import random
import time
import os
import sys

# 把spiders目录加入Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import parse_user_info, parse_time, url_to_mid
from scrapy import Spider
from scrapy.http import Request

# 日志配置
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# 获取cookie路径
current_file_path = os.path.abspath(__file__)
spiders_dir = os.path.dirname(current_file_path)
weibospider_dir = os.path.dirname(spiders_dir)
cookie_path = os.path.join(weibospider_dir, 'cookie.txt')

# 读取cookie
try:
    with open(cookie_path, 'r', encoding='utf-8') as f:
        cookie = f.read().strip()
except FileNotFoundError:
    logger.error(f"未找到cookie.txt文件，路径：{cookie_path}")
    cookie = ""

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0',
    'Referer': 'https://weibo.com/',
    'X-Requested-With': 'XMLHttpRequest',
    'Cookie': cookie,
}


class CommentSpider(Spider):
    """
    微博评论数据采集
    """
    name = "comment"
    max_pages = 30
    count = 20
    # 替换成你要采集的微博ID
    tweet_ids = ['QsQD07oyx']

    def start_requests(self):
        """
        Scrapy爬虫入口
        """
        logger.info(f"开始采集以下微博的评论：{self.tweet_ids}")
        for tweet_id in self.tweet_ids:
            mid = url_to_mid(tweet_id)
            url_template = (
                "https://weibo.com/ajax/statuses/buildComments?"
                "is_reload=0&id={id}&is_show_bulletin=2&is_mix=1&count=50&max_id={max_id}&fetch_level=0&locale=zh-CN"
            )
            url = url_template.format(id=mid, max_id=0)
            yield Request(
                url,
                headers=HEADERS,
                callback=self.parse_comments,
                meta={
                    'tweet_id': tweet_id,
                    'mid': mid,
                    'max_id': 0,
                    'page_num': 1,
                    'download_timeout': 10
                }
            )

    def parse_comments(self, response):
        """
        解析评论
        """
        meta = response.meta
        tweet_id = meta['tweet_id']
        page_num = meta['page_num']

        logger.info(f"[微博 {tweet_id} 第 {page_num} 页] 请求URL: {response.url}")

        try:
            data = json.loads(response.text)
        except Exception as e:
            logger.error(f"[第 {page_num} 页] 解析失败: {e}，响应内容预览：{response.text[:200]}")
            return

        comments = data.get('data', [])
        logger.info(f"[第 {page_num} 页] 抓取到 {len(comments)} 条评论")

        if not comments:
            logger.info(f"微博 {tweet_id} 无更多评论，结束采集")
            return

        # 解析评论并返回
        for comment_info in comments:
            item = self.parse_comment(comment_info)
            item['tweet_id'] = tweet_id
            item['weibo_url'] = f"https://weibo.com/{item['comment_user']['_id']}/{tweet_id}"
            yield item

        # 翻页逻辑
        new_max_id = data.get('max_id', 0)
        if new_max_id == 0 or page_num >= self.max_pages:
            logger.info(f"微博 {tweet_id} 采集完成（达到最大页数/无更多评论）")
            return

        # 构造下一页请求
        url_template = (
            "https://weibo.com/ajax/statuses/buildComments?"
            "is_reload=1&id={id}&is_show_bulletin=2&is_mix=1&count={count}&max_id={max_id}&fetch_level=0"
        )
        next_url = url_template.format(id=meta['mid'], count=self.count, max_id=new_max_id)
        time.sleep(random.uniform(1, 3))

        # 更新meta参数
        meta['max_id'] = new_max_id
        meta['page_num'] += 1
        yield Request(
            next_url,
            headers=HEADERS,
            callback=self.parse_comments,
            meta=meta
        )

    def parse_comment(self, data):
        """
        解析单条评论
        """
        item = dict()
        item['created_at'] = parse_time(data['created_at'])
        item['_id'] = data['id']
        item['like_counts'] = data['like_counts']
        item['ip_location'] = data.get('source', '')
        item['content'] = data.get('text_raw', '')
        item['comment_user'] = parse_user_info(data['user'])

        # 增加reply_comment非空判断
        if 'reply_comment' in data and data['reply_comment']:
            item['reply_comment'] = {
                '_id': data['reply_comment']['id'],
                'text': data['reply_comment'].get('text_raw', data['reply_comment'].get('text', '')),
                'user': parse_user_info(data['reply_comment']['user']),
            }
        return item