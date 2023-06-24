#!/usr/bin/env python
# encoding: utf-8
"""
Author: nghuyong
Mail: nghuyong@163.com
Created Time: 2020/4/14
"""
import json

import pymongo
from scrapy import Spider
from scrapy.http import Request
from spiders.comment import parse_user_info


class FollowerSpider(Spider):
    """
    微博关注数据采集
    """
    name = "follower"
    base_url = 'https://weibo.com/ajax/friendships/friends'

    def start_requests(self):
        """
        爬虫入口
        """
        # 这里user_ids可替换成实际待采集的数据
        client = pymongo.MongoClient('127.0.0.1', 27017)
        collection = client['weibo']["users"]
        cur = collection.find()
        user_ids = []
        for item in cur:
            if not item['is_finish_follower']:
                user_ids.append(item['_id'])
        for user_id in user_ids:
            url = self.base_url + f"?page=1&uid={user_id}"
            yield Request(url, callback=self.parse, meta={'user': user_id, 'page_num': 1})

    def finish_spider_one_user(self, user_id):
        client = pymongo.MongoClient('127.0.0.1', 27017)
        collection = client['weibo']["users"]
        collection.find_one_and_update({'_id': user_id},
                                       {'$set': {'is_finish_follower': True}})
        self.log(f"finish spider {user_id}")

    def parse(self, response, **kwargs):
        """
        网页解析
        """
        data = json.loads(response.text)
        if 'users' not in data['users']:
            self.finish_spider_one_user(response.meta['user'])
            return
        for user in data['users']:
            item = dict()
            item['follower_info'] = parse_user_info(user)
            item['fan_id'] = response.meta['user']
            item['follower_id'] = item['follower_info']['_id']
            item['_id'] = item['fan_id'] + '-' + item['follower_id']
            yield item
        if data['users']:
            response.meta['page_num'] += 1
            url = self.base_url + f"?page={response.meta['page_num']}&uid={response.meta['user']}"
            yield Request(url, callback=self.parse, meta=response.meta, priority=100)
        else:
            self.finish_spider_one_user(response.meta['user'])
