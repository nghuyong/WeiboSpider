#!/usr/bin/env python
# encoding: utf-8
"""
File Description: 
Author: nghuyong
Mail: nghuyong@163.com
Created Time: 2020/4/14
"""
import re
from scrapy import Selector, Spider
from scrapy.http import Request
import time
from items import UserItem


class UserSpider(Spider):
    name = "user_spider"
    base_url = "https://weibo.cn"

    def start_requests(self):
        user_ids = ['1087770692', '1699432410', '1266321801','1749127163']
        urls = [f'{self.base_url}/{user_id}/info' for user_id in user_ids]
        for url in urls:
            yield Request(url, callback=self.parse)

    def parse(self, response):
        user_item = UserItem()
        user_item['crawl_time'] = int(time.time())
        selector = Selector(response)
        user_item['_id'] = re.findall('(\d+)/info', response.url)[0]
        user_info_text = ";".join(selector.xpath('body/div[@class="c"]//text()').extract())
        nick_name = re.findall('昵称;?:?(.*?);', user_info_text)
        gender = re.findall('性别;?:?(.*?);', user_info_text)
        place = re.findall('地区;?:?(.*?);', user_info_text)
        brief_introduction = re.findall('简介;?:?(.*?);', user_info_text)
        birthday = re.findall('生日;?:?(.*?);', user_info_text)
        sex_orientation = re.findall('性取向;?:?(.*?);', user_info_text)
        sentiment = re.findall('感情状况;?:?(.*?);', user_info_text)
        vip_level = re.findall('会员等级;?:?(.*?);', user_info_text)
        authentication = re.findall('认证;?:?(.*?);', user_info_text)
        labels = re.findall('标签;?:?(.*?)更多>>', user_info_text)
        if nick_name and nick_name[0]:
            user_item["nick_name"] = nick_name[0].replace(u"\xa0", "")
        if gender and gender[0]:
            user_item["gender"] = gender[0].replace(u"\xa0", "")
        if place and place[0]:
            place = place[0].replace(u"\xa0", "").split(" ")
            user_item["province"] = place[0]
            if len(place) > 1:
                user_item["city"] = place[1]
        if brief_introduction and brief_introduction[0]:
            user_item["brief_introduction"] = brief_introduction[0].replace(u"\xa0", "")
        if birthday and birthday[0]:
            user_item['birthday'] = birthday[0]
        if sex_orientation and sex_orientation[0]:
            if sex_orientation[0].replace(u"\xa0", "") == gender[0]:
                user_item["sex_orientation"] = "同性恋"
            else:
                user_item["sex_orientation"] = "异性恋"
        if sentiment and sentiment[0]:
            user_item["sentiment"] = sentiment[0].replace(u"\xa0", "")
        if vip_level and vip_level[0]:
            user_item["vip_level"] = vip_level[0].replace(u"\xa0", "")
        if authentication and authentication[0]:
            user_item["authentication"] = authentication[0].replace(u"\xa0", "")
        if labels and labels[0]:
            user_item["labels"] = labels[0].replace(u"\xa0", ",").replace(';', '').strip(',')
        education_info = selector.xpath('//div[contains(text(),"学习经历")]/following-sibling::div[1]'). \
            xpath('string(.)').extract()
        if education_info:
            user_item['education'] = education_info[0].replace(u"\xa0", "")
        work_info = selector.xpath('//div[contains(text(),"工作经历")]/following-sibling::div[1]'). \
            xpath('string(.)').extract()
        if work_info:
            user_item['work'] = work_info[0].replace(u"\xa0", "")
        request_meta = response.meta
        request_meta['item'] = user_item
        yield Request(self.base_url + '/u/{}'.format(user_item['_id']),
                      callback=self.parse_further_information,
                      meta=request_meta, dont_filter=True, priority=1)

    def parse_further_information(self, response):
        text = response.text
        user_item = response.meta['item']
        tweets_num = re.findall('微博\[(\d+)\]', text)
        if tweets_num:
            user_item['tweets_num'] = int(tweets_num[0])
        follows_num = re.findall('关注\[(\d+)\]', text)
        if follows_num:
            user_item['follows_num'] = int(follows_num[0])
        fans_num = re.findall('粉丝\[(\d+)\]', text)
        if fans_num:
            user_item['fans_num'] = int(fans_num[0])
        yield user_item
