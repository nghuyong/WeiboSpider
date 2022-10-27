#!/usr/bin/env python
# encoding: utf-8
"""
Author: nghuyong
Mail: nghuyong@163.com
Created Time: 2020/4/14
"""
import json
from scrapy import Spider
from scrapy.http import Request
from spiders.comment import parse_user_info


class FanSpider(Spider):
    """
    微博粉丝数据采集
    """
    name = "fan"
    base_url = 'https://weibo.com/ajax/friendships/friends'

    def start_requests(self):
        """
        爬虫入口
        """
        # 这里user_ids可替换成实际待采集的数据
        user_ids = ['1087770692']
        for user_id in user_ids:
            url = self.base_url + f"?relate=fans&page=1&uid={user_id}&type=fans"
            yield Request(url, callback=self.parse, meta={'user': user_id, 'page_num': 1})

    def parse(self, response, **kwargs):
        """
        网页解析
        """
        data = json.loads(response.text)
        for user in data['users']:
            item = dict()
            item['follower_id'] = response.meta['user']
            item['fan_info'] = parse_user_info(user)
            item['_id'] = response.meta['user'] + '_' + item['fan_info']['_id']
            yield item
        if data['users']:
            response.meta['page_num'] += 1
            url = self.base_url + f"?relate=fans&page={response.meta['page_num']}&uid={response.meta['user']}&type=fans"
            yield Request(url, callback=self.parse, meta=response.meta)
