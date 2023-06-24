#!/usr/bin/env python
# encoding: utf-8
"""
File Description:
Author: rightyonghu
Created Time: 2023/6/13
"""
import pymongo
from tqdm import tqdm


def import_data_to_mongo():
    """
    导入数据到mongo
    """
    client = pymongo.MongoClient('127.0.0.1', 27017)
    collection = client['weibo']["users"]
    with open('uids.txt', 'rt', encoding='utf-8') as f:
        for line in tqdm(f):
            try:
                collection.insert_one({"_id": line.strip(), 'is_finish_follower': False, 'is_finish_followee': False})
            except Exception as e:
                pass


if __name__ == '__main__':
    import_data_to_mongo()
