#!/usr/bin/env python
# encoding: utf-8
import re
from lxml import etree
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector
from scrapy.http import Request
from scrapy.utils.project import get_project_settings
from scrapy_redis.spiders import RedisSpider
from sina.items import TweetsItem, InformationItem, RelationshipsItem, CommentItem
from sina.spiders.utils import time_fix
import time
from tqdm import tqdm
from traceback import format_exc


class WeiboSpider(RedisSpider):
    name = "weibo_spider"
    base_url = "https://weibo.cn"
    edis_key = "weibo_spider:start_urls"

    custom_settings = {
        'CONCURRENT_REQUESTS': 16,
        "DOWNLOAD_DELAY": 0.1,
        "SCHEDULER": "scrapy_redis.scheduler.Scheduler",
        "DUPEFILTER_CLASS": "scrapy_redis.dupefilter.RFPDupeFilter",
        "SCHEDULER_PERSIST": True,
    }
    
    # 默认初始解析函数
    info_p               = re.compile(r'(\d+)/info')
    nick_name_p          = re.compile('昵称;?[：:]?(.*?);')
    gender_p             = re.compile('性别;?[：:]?(.*?);')
    place_p              = re.compile('地区;?[：:]?(.*?);')
    brief_introduction_p = re.compile('简介;[：:]?(.*?);')
    birthday_p           = re.compile('生日;?[：:]?(.*?);')
    sex_orientation_p    = re.compile('性取向;?[：:]?(.*?);')
    sentiment_p          = re.compile('感情状况;?[：:]?(.*?);')
    vip_level_p          = re.compile('会员等级;?[：:]?(.*?);')
    authentication_p     = re.compile('认证;?[：:]?(.*?);')
    tweets_num_p         = re.compile(r'微博\[(\d+)\]')
    follows_num_p        = re.compile(r'关注\[(\d+)\]')
    fans_num_p           = re.compile(r'粉丝\[(\d+)\]')
    IDs_in_url_p         = re.compile(r'/repost/(.*?)\?uid=(\d+)')
    integer_p            = re.compile(r'\d+')
    page_p               = re.compile(r'/>&nbsp;1/(\d+)页</div>')
    comment_user_id_p    = re.compile(r'/u/(\d+)')

    def parse(self, response):
        """ 抓取个人信息 """
        information_item = InformationItem()
        information_item['crawl_time'] = int(time.time())
        selector = Selector(response)
        information_item['_id'] = self.info_p.findall(response.url)[0]
        text1 = ";".join(selector.xpath('body/div[@class="c"]//text()').extract())  # 获取标签里的所有text()
        nick_name          = self.nick_name_p.findall(text1)
        gender             = self.gender_p.findall(text1)
        place              = self.place_p.findall(text1)
        brief_introduction = self.brief_introduction_p.findall(text1)
        birthday           = self.birthday_p.findall(text1)
        sex_orientation    = self.sex_orientation_p.findall(text1)
        sentiment          = self.sentiment_p.findall(text1)
        vip_level          = self.vip_level_p.findall(text1)
        authentication     = self.authentication_p.findall(text1)
        if nick_name and nick_name[0]:
            information_item["nick_name"] = nick_name[0].replace(u"\xa0", "")
        if gender and gender[0]:
            information_item["gender"] = gender[0].replace(u"\xa0", "")
        if place and place[0]:
            place = place[0].replace(u"\xa0", "").split(" ")
            information_item["province"] = place[0]
            if len(place) > 1:
                information_item["city"] = place[1]
        if brief_introduction and brief_introduction[0]:
            information_item["brief_introduction"] = brief_introduction[0].replace(u"\xa0", "")
        if birthday and birthday[0]:
            information_item['birthday'] = birthday[0]
        if sex_orientation and sex_orientation[0]:
            if sex_orientation[0].replace(u"\xa0", "") == gender[0]:
                information_item["sex_orientation"] = "同性恋"
            else:
                information_item["sex_orientation"] = "异性恋"
        if sentiment and sentiment[0]:
            information_item["sentiment"] = sentiment[0].replace(u"\xa0", "")
        if vip_level and vip_level[0]:
            information_item["vip_level"] = vip_level[0].replace(u"\xa0", "")
        if authentication and authentication[0]:
            information_item["authentication"] = authentication[0].replace(u"\xa0", "")
        request_meta = response.meta
        request_meta['item'] = information_item
        yield Request(self.base_url + '/u/{}'.format(information_item['_id']),
                      callback=self.parse_further_information,
                      meta=request_meta, priority=1)

    def parse_further_information(self, response, if_get_posts=True, if_get_followers=True, if_get_followees=True):
        text = response.text
        information_item = response.meta['item']
        tweets_num = self.tweets_num_p.findall(text)
        if tweets_num:
            information_item['tweets_num'] = int(tweets_num[0])
        follows_num = self.follows_num_p.findall(text)
        if follows_num:
            information_item['follows_num'] = int(follows_num[0])
        fans_num = self.fans_num_p.findall(text)
        if fans_num:
            information_item['fans_num'] = int(fans_num[0])
        yield information_item

        # 获取该用户微博
        if if_get_posts:
            yield Request(url=self.base_url + '/{}/profile?page=1'.format(information_item['_id']), callback=self.parse_tweet, priority=2)

        # 获取关注列表
        if if_get_followees:
            yield Request(url=self.base_url + '/{}/follow?page=1'.format(information_item['_id']),
                          callback=self.parse_follow)
        # 获取粉丝列表
        if if_get_followers:
            yield Request(url=self.base_url + '/{}/fans?page=1'.format(information_item['_id']),
                          callback=self.parse_fans)

    def parse_tweet(self, response, if_get_comments=False):
        if response.url.endswith('page=1'):
            # 如果是第1页，一次性获取后面的所有页
            all_page = self.page_p.search(response.text)
            if all_page:
                all_page = all_page.group(1)
                all_page = int(all_page)
                with tqdm(range(2, all_page + 1), desc=response.url[17:-15]+"'s Posts") as pbar:
                    for page_num in pbar:
                        page_url = response.url.replace('page=1', 'page={}'.format(page_num))
                        yield Request(page_url, self.parse_tweet, meta=response.meta, priority=3)
        """
        解析本页的数据
        """
        tree_node = etree.HTML(response.body)
        tweet_nodes = tree_node.xpath('//div[@class="c" and @id]')
        #with tqdm(tweet_nodes, desc='Posts on '+response.url[18:]) as pbar_posts:
        for tweet_node in tweet_nodes:#pbar_posts:
            try:
                tweet_item = TweetsItem()
                tweet_item['crawl_time'] = int(time.time())

                # Parse user id and post id, both required:
                tweet_repost_urls = tweet_node.xpath('.//a[contains(text(),"转发[")]/@href')
                assert len(tweet_repost_urls)>0, 'Repost link not found.'
                tweet_repost_url = tweet_repost_urls[0] # else, take the first link.

                user_tweet_id = self.IDs_in_url_p.search(tweet_repost_url)
                assert user_tweet_id is not None and len(user_tweet_id.groups())==2, 'Cannot parse user id and post id from the URL. Skipping.'
                tweet_item['post_id'] = user_tweet_id.group(1)
                tweet_item['user_id'] = user_tweet_id.group(2)
                tweet_item['weibo_url'] = 'https://weibo.com/{}/{}'.format(tweet_item['user_id'], tweet_item['post_id'])
                tweet_item['_id'] = tweet_item['user_id']+'_'+tweet_item['post_id']

                # Parse optional fields:
                try:
                    create_time_info = tweet_node.xpath('.//span[@class="ct" and contains(text(),"来自")]/text()')[0]
                    tweet_item['created_at'] = time_fix(create_time_info.split('来自')[0].strip())
                except: pass
                try:
                    n = tweet_node.xpath('.//a[contains(text(),"赞")]/text()')[0]
                    tweet_item['like_num'] = int(self.integer_p.search(n))
                except: pass
                try:
                    n = tweet_node.xpath('.//a[contains(text(),"转发")]/text()')[0]
                    tweet_item['repost_num'] = int(self.integer_p.search(n))
                except: pass
                try:
                    n = tweet_node.xpath('.//a[contains(text(),"评论") and not(contains(text(),"原文"))]/text()')[0]
                    tweet_item['comment_num'] = int(self.integer_p.search(n))
                except: pass

                # If full text is hidden, reveal on-demand:
                tweet_content_nodes = tweet_node.xpath('.//span[@class="ctt"]')
                assert len(tweet_content_nodes)>0, 'This post has no content??'
                tweet_content_node = tweet_content_nodes[0]
                all_content_link = tweet_content_node.xpath('.//a[text()="全文"]')
                if all_content_link:
                    all_content_url = self.base_url + all_content_link[0].xpath('./@href')[0]
                    yield Request(all_content_url, callback=self.parse_all_content, meta={'item': tweet_item}, priority=5)
                else:
                    all_content = tweet_content_node.xpath('string(.)').strip('\u200b')
                    tweet_item['content'] = all_content
                    yield tweet_item

                if if_get_comments: # 抓取该微博的评论信息
                    comment_url = self.base_url + '/comment/' + tweet_item['post_id']
                    yield Request(url=comment_url, callback=self.parse_comment, meta={'weibo_url': tweet_item['weibo_url']})

            except Exception as e:
                self.logger.error(e)
                self.logger.error(format_exc())

    def parse_all_content(self, response):
        '''有阅读全文的情况，获取全文'''
        tree_node = etree.HTML(response.body)
        tweet_item = response.meta['item']
        content_nodes = tree_node.xpath('//div[@id="M_"]//span[@class="ctt"]')
        assert len(content_nodes)>0, 'No content node found on the Full Content page??'
        content_node = content_nodes[0]
        all_content = content_node.xpath('string(.)').strip('\u200b')
        tweet_item['content'] = all_content
        yield tweet_item

    def parse_follow(self, response):
        """
        抓取关注列表
        """
        # 如果是第1页，一次性获取后面的所有页
        all_page = self.page_p.search(response.text)
        if all_page:
            all_page = all_page.group(1)
            all_page = int(all_page)
            with tqdm(range(2, all_page + 1), desc='Followees Pages') as pbar:
                for page_num in pbar:
                    page_url = response.url.replace('page=1', 'page={}'.format(page_num))
                    yield Request(page_url, self.parse_follow, meta=response.meta)
        selector = Selector(response)
        urls = selector.xpath('//a[text()="关注他" or text()="关注她" or text()="取消关注"]/@href').extract()
        uids = re.findall('uid=(\d+)', ";".join(urls), re.S)
        ID = re.findall('(\d+)/follow', response.url)[0]
        with tqdm(uids, desc='Followees') as pbar:
            for uid in pbar:
                relationships_item = RelationshipsItem()
                relationships_item['crawl_time'] = int(time.time())
                relationships_item["fan_id"] = ID
                relationships_item["followed_id"] = uid
                relationships_item["_id"] = ID + '-' + uid
                yield relationships_item
                yield Request(url="https://weibo.cn/%s/info" % uid, callback=self.parse)

    def parse_fans(self, response):
        """
        抓取粉丝列表
        """
        # 如果是第1页，一次性获取后面的所有页
        all_page = self.page_p.search(response.text)
        if all_page:
            all_page = all_page.group(1)
            all_page = int(all_page)
            with tqdm(range(2, all_page + 1), desc='Followees Pages') as pbar:
                for page_num in pbar:
                    page_url = response.url.replace('page=1', 'page={}'.format(page_num))
                    yield Request(page_url, self.parse_fans, meta=response.meta)
        selector = Selector(response)
        urls = selector.xpath('//a[text()="关注他" or text()="关注她" or text()="移除"]/@href').extract()
        uids = re.findall('uid=(\d+)', ";".join(urls), re.S)
        ID = re.findall('(\d+)/fans', response.url)[0]
        with tqdm(uids, desc='Followers') as pbar:
            for uid in pbar:
                relationships_item = RelationshipsItem()
                relationships_item['crawl_time'] = int(time.time())
                relationships_item["fan_id"] = uid
                relationships_item["followed_id"] = ID
                relationships_item["_id"] = uid + '-' + ID
                yield relationships_item
                yield Request(url="https://weibo.cn/%s/info" % uid, callback=self.parse)

    def parse_comment(self, response):
        # 如果是第1页，一次性获取后面的所有页
        all_page = self.page_p.search(response.text)
        if all_page:
            all_page = all_page.group(1)
            all_page = int(all_page)
            for page_num in range(2, all_page + 1):
                page_url = response.url.replace('page=1', 'page={}'.format(page_num))
                yield Request(page_url, self.parse_comment, meta=response.meta)
        selector = Selector(response)
        comment_nodes = selector.xpath('//div[@class="c" and contains(@id,"C_")]')
        for comment_node in comment_nodes:
            comment_user_url = comment_node.xpath('.//a[contains(@href,"/u/")]/@href').extract_first()
            if not comment_user_url: continue
            comment_item = CommentItem()
            comment_item['crawl_time'] = int(time.time())
            comment_item['weibo_url'] = response.meta['weibo_url']
            comment_item['comment_user_id'] = self.comment_user_id_p.search(comment_user_url).group(1)
            comment_item['content'] = comment_node.xpath('.//span[@class="ctt"]').xpath('string(.)').extract_first()
            comment_item['_id'] = comment_node.xpath('./@id').extract_first()
            created_at = comment_node.xpath('.//span[@class="ct"]/text()').extract_first()
            comment_item['created_at'] = time_fix(created_at.split('\xa0')[0])
            yield comment_item


if __name__ == "__main__":
    process = CrawlerProcess(get_project_settings())
    process.crawl('weibo_spider')
    process.start()
