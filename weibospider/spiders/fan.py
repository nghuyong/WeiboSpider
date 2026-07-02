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

# 补充缺失的 parse_user_info 函数（原代码依赖但没定义）
def parse_user_info(user):
    """解析用户基本信息"""
    info = {
        '_id': str(user.get('id', '')),
        'screen_name': user.get('screen_name', ''),  # 昵称
        'gender': user.get('gender', ''),            # 性别
        'follow_count': user.get('follow_count', 0), # 关注数
        'followers_count': user.get('followers_count', 0), # 粉丝数
        'description': user.get('description', ''),  # 简介
        'location': user.get('location', '')         # 所在地
    }
    return info

class FanSpider(Spider):
    """
    微博粉丝数据采集
    """
    name = "fan"
    base_url = 'https://weibo.com/ajax/friendships/friends'

    def start_requests(self):
        """
        爬虫入口（补充Cookie和Headers配置，这是核心）
        """
        try:
            # 你的实际cookie.txt路径（注意加r避免转义，或用双反斜杠）
            cookie_path = r'E:\qiqi\WeiboSpider\weibospider\cookie.txt'
            with open(cookie_path, 'r', encoding='utf-8') as f:
                cookie = f.read().strip()
        except FileNotFoundError:
            self.logger.error(f"未找到cookie.txt文件，路径：{cookie_path}，请检查路径是否正确！")
            return

        # 2. 配置请求头（模拟浏览器，避免被识别为爬虫）
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0',
            'Cookie': cookie,
            'Referer': 'https://weibo.com/',
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json, text/plain, */*'
        }

        # 3. 待采集的用户ID（可替换）
        user_ids = ['1087770692']
        for user_id in user_ids:
            url = self.base_url + f"?relate=fans&page=1&uid={user_id}&type=fans"
            yield Request(
                url,
                callback=self.parse,
                meta={'user': user_id, 'page_num': 1},
                headers=headers,  # 新增：传递Headers（含Cookie）
                dont_filter=True  # 新增：避免URL去重
            )

    def parse(self, response, **kwargs):
        """
        网页解析（增加完整异常处理，避免KeyError）
        """
        try:
            # 1. 解析JSON数据
            data = json.loads(response.text)
            self.logger.info(f"【第{response.meta['page_num']}页】API返回数据：{list(data.keys()) if data else '空'}")

            # 2. 处理无users字段的情况（权限不足/无粉丝）
            if 'users' not in data or not data['users']:
                self.logger.warning(f"用户{response.meta['user']}第{response.meta['page_num']}页无粉丝数据（权限不足/无粉丝）")
                return

            # 3. 正常解析粉丝数据
            for user in data['users']:
                item = dict()
                item['follower_id'] = response.meta['user']
                item['fan_info'] = parse_user_info(user)
                item['_id'] = response.meta['user'] + '_' + item['fan_info']['_id']
                yield item

            # 4. 翻页（仅当有数据时翻页）
            response.meta['page_num'] += 1
            url = self.base_url + f"?relate=fans&page={response.meta['page_num']}&uid={response.meta['user']}&type=fans"
            yield Request(
                url,
                callback=self.parse,
                meta=response.meta,
                headers=response.request.headers,  # 复用Headers
                dont_filter=True
            )

        # 5. 异常捕获（避免爬虫崩溃）
        except json.JSONDecodeError:
            self.logger.error(f"JSON解析失败，响应内容：{response.text[:500]}")
        except KeyError as e:
            self.logger.error(f"字段缺失：{str(e)}，返回数据：{data if 'data' in locals() else response.text[:500]}")
        except Exception as e:
            self.logger.error(f"解析出错：{str(e)}，响应内容：{response.text[:500]}")