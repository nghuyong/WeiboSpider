#!/usr/bin/env python
# encoding: utf-8

import datetime
import requests
import re
from lxml import etree
from scrapy import Spider
from scrapy.selector import Selector
from scrapy.http import Request

from sina.config import weiboID
from sina.items import TweetsItem, InformationItem, RelationshipsItem


class Spider(Spider):
    name = "SinaSpider"
    host = "https://weibo.cn"
    start_urls = list(set(weiboID))

    def start_requests(self):
        for uid in self.start_urls:
            yield Request(url="https://weibo.cn/%s/info" % uid, callback=self.parse_information)

    def parse_information(self, response):
        """ 抓取个人信息 """
        informationItem = InformationItem()
        selector = Selector(response)
        ID = re.findall('(\d+)/info', response.url)[0]
        try:
            text1 = ";".join(selector.xpath('body/div[@class="c"]//text()').extract())  # 获取标签里的所有text()
            nickname = re.findall('昵称;?[：:]?(.*?);', text1)
            gender = re.findall('性别;?[：:]?(.*?);', text1)
            place = re.findall('地区;?[：:]?(.*?);', text1)
            briefIntroduction = re.findall('简介;?[：:]?(.*?);', text1)
            birthday = re.findall('生日;?[：:]?(.*?);', text1)
            sexOrientation = re.findall('性取向;?[：:]?(.*?);', text1)
            sentiment = re.findall('感情状况;?[：:]?(.*?);', text1)
            vipLevel = re.findall('会员等级;?[：:]?(.*?);', text1)
            authentication = re.findall('认证;?[：:]?(.*?);', text1)
            url = re.findall('互联网;?[：:]?(.*?);', text1)

            informationItem["_id"] = ID
            if nickname and nickname[0]:
                informationItem["NickName"] = nickname[0].replace(u"\xa0", "")
            if gender and gender[0]:
                informationItem["Gender"] = gender[0].replace(u"\xa0", "")
            if place and place[0]:
                place = place[0].replace(u"\xa0", "").split(" ")
                informationItem["Province"] = place[0]
                if len(place) > 1:
                    informationItem["City"] = place[1]
            if briefIntroduction and briefIntroduction[0]:
                informationItem["BriefIntroduction"] = briefIntroduction[0].replace(u"\xa0", "")
            if birthday and birthday[0]:
                try:
                    birthday = datetime.datetime.strptime(birthday[0], "%Y-%m-%d")
                    informationItem["Birthday"] = birthday - datetime.timedelta(hours=8)
                except Exception:
                    informationItem['Birthday'] = birthday[0]  # 有可能是星座，而非时间
            if sexOrientation and sexOrientation[0]:
                if sexOrientation[0].replace(u"\xa0", "") == gender[0]:
                    informationItem["SexOrientation"] = "同性恋"
                else:
                    informationItem["SexOrientation"] = "异性恋"
            if sentiment and sentiment[0]:
                informationItem["Sentiment"] = sentiment[0].replace(u"\xa0", "")
            if vipLevel and vipLevel[0]:
                informationItem["VIPlevel"] = vipLevel[0].replace(u"\xa0", "")
            if authentication and authentication[0]:
                informationItem["Authentication"] = authentication[0].replace(u"\xa0", "")
            if url:
                informationItem["URL"] = url[0]

            try:
                urlothers = "https://weibo.cn/attgroup/opening?uid=%s" % ID
                new_ck = {}
                for ck in response.request.cookies:
                    new_ck[ck['name']] = ck['value']
                r = requests.get(urlothers, cookies=new_ck, timeout=5)
                if r.status_code == 200:
                    selector = etree.HTML(r.content)
                    texts = ";".join(selector.xpath('//body//div[@class="tip2"]/a//text()'))
                    if texts:
                        num_tweets = re.findall('微博\[(\d+)\]', texts)
                        num_follows = re.findall('关注\[(\d+)\]', texts)
                        num_fans = re.findall('粉丝\[(\d+)\]', texts)
                        if num_tweets:
                            informationItem["Num_Tweets"] = int(num_tweets[0])
                        if num_follows:
                            informationItem["Num_Follows"] = int(num_follows[0])
                        if num_fans:
                            informationItem["Num_Fans"] = int(num_fans[0])
            except Exception as e:
                pass
        except Exception as e:
            pass
        else:
            yield informationItem
        if informationItem["Num_Tweets"] and informationItem["Num_Tweets"] < 5000:
            yield Request(url="https://weibo.cn/%s/profile?filter=1&page=1" % ID, callback=self.parse_tweets,
                          dont_filter=True)
        if informationItem["Num_Follows"] and informationItem["Num_Follows"] < 500:
            yield Request(url="https://weibo.cn/%s/follow" % ID, callback=self.parse_relationship, dont_filter=True)
        if informationItem["Num_Fans"] and informationItem["Num_Fans"] < 500:
            yield Request(url="https://weibo.cn/%s/fans" % ID, callback=self.parse_relationship, dont_filter=True)

    def parse_tweets(self, response):
        """ 抓取微博数据 """
        selector = Selector(response)
        ID = re.findall('(\d+)/profile', response.url)[0]
        divs = selector.xpath('body/div[@class="c" and @id]')
        for div in divs:
            try:
                tweetsItems = TweetsItem()
                id = div.xpath('@id').extract_first()  # 微博ID
                content = div.xpath('div/span[@class="ctt"]//text()').extract()  # 微博内容
                cooridinates = div.xpath('div/a/@href').extract()  # 定位坐标
                like = re.findall('赞\[(\d+)\]', div.extract())  # 点赞数
                transfer = re.findall('转发\[(\d+)\]', div.extract())  # 转载数
                comment = re.findall('评论\[(\d+)\]', div.extract())  # 评论数
                others = div.xpath('div/span[@class="ct"]/text()').extract()  # 求时间和使用工具（手机或平台）

                tweetsItems["_id"] = ID + "-" + id
                tweetsItems["ID"] = ID
                if content:
                    tweetsItems["Content"] = " ".join(content).strip('[位置]')  # 去掉最后的"[位置]"
                if cooridinates:
                    cooridinates = re.findall('center=([\d.,]+)', cooridinates[0])
                    if cooridinates:
                        tweetsItems["Co_oridinates"] = cooridinates[0]
                if like:
                    tweetsItems["Like"] = int(like[0])
                if transfer:
                    tweetsItems["Transfer"] = int(transfer[0])
                if comment:
                    tweetsItems["Comment"] = int(comment[0])
                if others:
                    others = others[0].split('来自')
                    tweetsItems["PubTime"] = others[0].replace(u"\xa0", "")
                    if len(others) == 2:
                        tweetsItems["Tools"] = others[1].replace(u"\xa0", "")
                yield tweetsItems
            except Exception as e:
                self.logger.info(e)
                pass

        url_next = selector.xpath('body/div[@class="pa" and @id="pagelist"]/form/div/a[text()="下页"]/@href').extract()
        if url_next:
            yield Request(url=self.host + url_next[0], callback=self.parse_tweets, dont_filter=True)

    def parse_relationship(self, response):
        """ 打开url爬取里面的个人ID """
        selector = Selector(response)
        if "/follow" in response.url:
            ID = re.findall('(\d+)/follow', response.url)[0]
            flag = True
        else:
            ID = re.findall('(\d+)/fans', response.url)[0]
            flag = False
        urls = selector.xpath('//a[text()="关注他" or text()="关注她"]/@href').extract()
        uids = re.findall('uid=(\d+)', ";".join(urls), re.S)
        for uid in uids:
            relationshipsItem = RelationshipsItem()
            relationshipsItem["fan_id"] = ID if flag else uid
            relationshipsItem["followed_id"] = uid if flag else ID
            yield relationshipsItem
            yield Request(url="https://weibo.cn/%s/info" % uid, callback=self.parse_information)

        next_url = selector.xpath('//a[text()="下页"]/@href').extract()
        if next_url:
            yield Request(url=self.host + next_url[0], callback=self.parse_relationship, dont_filter=True)
