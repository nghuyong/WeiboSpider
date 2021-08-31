#!/usr/bin/env python
# encoding: utf-8
"""
File Description:
Author: FengWei
Mail: 1552526971@qq.com
Created Time: 2021/8/29
"""
import datetime
import re
from lxml import etree
from scrapy import Spider
from scrapy.http import Request
import time
from items import TextItem
from urllib.parse import unquote
from spiders.utils import time_fix, extract_weibo_content


class TextSpider(Spider):
    name = "text_spider"
    base_url = "https://weibo.cn"

    def start_requests(self):
        tweet_ids = ['Ftyf09QEd', 'IyUGaiZi8', 'Jmda1EbSj', 'F8BbIoUB1', 'F3ObOsUC2']

        urls = [f"{self.base_url}/comment/{tweet_id}" for tweet_id in tweet_ids]
        for url in urls:
            yield Request(url, callback=self.parse)

    def parse(self, response):
        tree_node = etree.HTML(response.body)

        try:
            text_item = TextItem()
            text_item['crawl_time'] = int(time.time())
            text_repost_url = tree_node.xpath('.//a[contains(text(),"转发")]/@href')[
                0]  # /repost/Ftyf09QEd?uid=6333655397&#rt
            user_text_id = re.search(r'/repost/(.*?)\?uid=(\d+)', text_repost_url)
            text_item['weibo_url'] = 'https://weibo.com/{}/{}'.format(user_text_id.group(2),
                                                                      user_text_id.group(1))
            text_item['user_id'] = user_text_id.group(2)
            text_item['_id'] = user_text_id.group(1)

            like_num = tree_node.xpath('.//a[contains(text(),"赞")]')[0].text
            text_item['like_num'] = int(re.search('\d+', like_num).group())

            repost_num = tree_node.xpath('.//a[contains(text(),"转发")]')[0].text
            try:
                text_item['repost_num'] = int(re.search('\d+', repost_num).group())
            except Exception as e:
                text_item['repost_num'] = 0

            comment_num = tree_node.xpath(
                './/span[contains(text(),"评论")]')[0].text
            try:
                text_item['comment_num'] = int(re.search('\d+', comment_num).group())
            except Exception as e:
                text_item['comment_num'] = 0

            # 有一点小问题 Ftyf09QEd 获取内容不全
            content = tree_node.xpath(
                '//*[@id="M_"]/div/span[1]')[0].text
            text_item['content'] = str(content)

            create_time_info_node = tree_node.xpath('.//span[@class="ct"]')[0].text
            text_item['created_at'] = create_time_info_node  # 保存为str类型

            images = tree_node.xpath('.//img[@alt="图片"]/@src')
            if images:
                text_item['image_url'] = images
            else:
                text_item['image_url'] = None

            videos = tree_node.xpath('.//a[contains(@href,"https://m.weibo.cn/s/video/show?object_id=")]/@href')
            if videos:
                text_item['video_url'] = videos
            else:
                text_item['video_url'] = None

            map_node = tree_node.xpath('.//a[contains(@href,"https://weibo.cn/sinaurl?")]/@href')
            if map_node:
                text_item['location_map_info'] = str(map_node)

                map_name_node = tree_node.xpath('.//a[contains(@href,"https://weibo.cn/sinaurl?")]')
                try:
                    text_item['location_map_name_info'] = map_name_node[0].text
                except Exception as e:
                    text_item['location_map_name_info'] = None
            else:
                text_item['location_map_info'] = None
                text_item['location_map_name_info'] = None

            yield text_item

        except Exception as e:
            self.logger.error(e)
