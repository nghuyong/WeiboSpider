#!/usr/bin/env python
# encoding: utf-8
"""
Author: nghuyong
Mail: nghuyong@163.com
Created Time: 2019-12-07 21:27
"""
import os
import sys

# ========== 新增：解决包导入问题的核心代码 ==========
# 获取 run_spider.py 自身的绝对路径
RUN_SPIDER_PATH = os.path.abspath(__file__)
# 获取 weibospider 目录路径（run_spider.py 所在目录）
WEIBOSPIDER_DIR = os.path.dirname(RUN_SPIDER_PATH)
# 获取项目根目录（WeiboSpider）
PROJECT_ROOT = os.path.dirname(WEIBOSPIDER_DIR)
# 把项目根目录加入 Python 模块搜索路径
sys.path.insert(0, PROJECT_ROOT)
# 把 weibospider 目录也加入路径（双重保险）
sys.path.insert(0, WEIBOSPIDER_DIR)

# ========== 原有代码保留（无需修改） ==========
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from spiders.tweet_by_user_id import TweetSpiderByUserID
from spiders.tweet_by_keyword import TweetSpiderByKeyword
from spiders.tweet_by_tweet_id import TweetSpiderByTweetID
from spiders.comment import CommentSpider
from spiders.follower import FollowerSpider
from spiders.user import UserSpider
from spiders.fan import FanSpider
from spiders.repost import RepostSpider

if __name__ == '__main__':
    # 新增：参数检查，避免无参数运行报错
    if len(sys.argv) < 2:
        print("用法: python run_spider.py <mode>")
        print("可选 mode: comment, fan, follower, user, repost, tweet_by_tweet_id, tweet_by_user_id, tweet_by_keyword")
        sys.exit(1)

    mode = sys.argv[1]
    os.environ['SCRAPY_SETTINGS_MODULE'] = 'settings'
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    mode_to_spider = {
        'comment': CommentSpider,
        'fan': FanSpider,
        'follow': FollowerSpider,
        'user': UserSpider,
        'repost': RepostSpider,
        'tweet_by_tweet_id': TweetSpiderByTweetID,
        'tweet_by_user_id': TweetSpiderByUserID,
        'tweet_by_keyword': TweetSpiderByKeyword,
    }
    process.crawl(mode_to_spider[mode])
    # the script will block here until the crawling is finished
    process.start()