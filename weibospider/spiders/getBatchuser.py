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
from spiders.common import parse_user_info


class UserBatchSpider(Spider):
    """
    微博用户信息爬虫
    """
    name = "user_batch_spider"
    base_url = "https://weibo.cn"

    def start_requests(self):
        """
        爬虫入口
        """
        # 数据路径
        # 指定选定的Json数据
        path = '/Users/yunpeng/Desktop/content/WeiboSpider/output/follower_20230310152918.jsonl'
        fan_all_userid = []

        def parse_json(parse_path):
            g = open(parse_path, 'rb')
            for ls in g:
                yield json.loads(ls)

        # 读取每条数据
        for d in parse_json(path):
            # get内的参数 参考json文件内 动态修改就可以。
            fan_all_userid.append(d.get('follower_info').get('_id'))

        # 这里user_ids可替换成实际待采集的数据
        # 改为批量
        urls = [f'https://weibo.com/ajax/profile/info?uid={user_id}' for user_id in fan_all_userid]
        for url in urls:
            yield Request(url, callback=self.parse)

    def parse(self, response, **kwargs):
        """
        网页解析
        """
        data = json.loads(response.text)
        item = parse_user_info(data['data']['user'])
        url = f"https://weibo.com/ajax/profile/detail?uid={item['_id']}"
        yield Request(url, callback=self.parse_detail, meta={'item': item})

    @staticmethod
    def parse_detail(response):
        """
        解析详细数据
        """
        item = response.meta['item']
        data = json.loads(response.text)['data']
        item['birthday'] = data.get('birthday', '')
        if 'created_at' not in item:
            item['created_at'] = data.get('created_at', '')
        item['desc_text'] = data.get('desc_text', '')
        item['ip_location'] = data.get('ip_location', '')
        item['sunshine_credit'] = data.get('sunshine_credit', {}).get('level', '')
        item['label_desc'] = [label['name'] for label in data.get('label_desc', [])]
        if 'company' in data:
            item['company'] = data['company']
        if 'education' in data:
            item['education'] = data['education']
        yield item
