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
from .common import parse_user_info


class UserSpider(Spider):
    """
    微博用户信息爬虫
    """
    name = "user_spider"
    base_url = "https://weibo.cn"

    def start_requests(self):
        """
        爬虫入口
        """
        # 这里user_ids可替换成实际待采集的数据
        user_ids = ['1749127163']
        urls = [f'https://weibo.com/ajax/profile/info?uid={user_id}' for user_id in user_ids]
        for url in urls:
            yield Request(url, callback=self.parse)

    def parse(self, response, **kwargs):
        """
        网页解析
        """
        try:
            self.logger.info(f"Response status: {response.status}")
            self.logger.info(f"Response text: {response.text[:500]}...")  # 只显示前500个字符
            
            data = json.loads(response.text)
            self.logger.info(f"Parsed data keys: {list(data.keys())}")
            
            if 'data' in data:
                self.logger.info(f"Data keys: {list(data['data'].keys())}")
                if 'user' in data['data']:
                    user_data = data['data']['user']
                    self.logger.info(f"User data keys: {list(user_data.keys())}")
                    
                    try:
                        item = parse_user_info(user_data)
                        self.logger.info(f"Parsed user item: {item}")
                        
                        url = f"https://weibo.com/ajax/profile/detail?uid={item['_id']}"
                        yield Request(url, callback=self.parse_detail, meta={'item': item})
                    except Exception as e:
                        self.logger.error(f"Error parsing user info: {e}")
                        import traceback
                        self.logger.error(traceback.format_exc())
                else:
                    self.logger.error("No 'user' in response data")
            else:
                self.logger.error("No 'data' in response")
        except Exception as e:
            self.logger.error(f"Error parsing response: {e}")
            self.logger.error(f"Full response text: {response.text}")
            import traceback
            self.logger.error(traceback.format_exc())

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
