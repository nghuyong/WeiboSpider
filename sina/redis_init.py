#!/usr/bin/env python
# encoding: utf-8
import redis
import sys
import os
from tqdm import tqdm
sys.path.append(os.getcwd())
from sina.settings import LOCAL_REDIS_HOST, LOCAL_REDIS_PORT

r = redis.Redis(host=LOCAL_REDIS_HOST, port=LOCAL_REDIS_PORT)

for key in r.scan_iter("weibo_spider*"):
    r.delete(key)

try:
    import pandas as pd
    start_uids = pd.read_csv('UIDs_to_scrape.csv').uid
except:
    start_uids = [
        '2803301701',  # 人民日报
        '1699432410']  # 新华社

with tqdm(start_uids, desc='Initializing User IDs') as pbar:
    for uid in pbar: r.lpush('weibo_spider:start_urls', "https://weibo.cn/%s/info" % uid)

print('redis初始化完毕。')
