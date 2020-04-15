#!/usr/bin/env python
# encoding: utf-8
"""
File Description: 
Author: nghuyong
Mail: nghuyong@163.com
Created Time: 2020/4/9
"""
import pymongo
from pymongo.errors import DuplicateKeyError

mongo_client = pymongo.MongoClient(host='mongodb')
collection = mongo_client["weibo"]["account"]


def insert_cookie(username, password, cookie_str):
    """
    insert cookie to database
    :param username: username of weibo account
    :param password: password of weibo account
    :param cookie_str: cookie str
    :return:
    """
    try:
        collection.insert(
            {"_id": username, "password": password, "cookie": cookie_str, "status": "success"})
    except DuplicateKeyError as e:
        collection.find_one_and_update({'_id': username}, {'$set': {'cookie': cookie_str, "status": "success"}})


if __name__ == '__main__':
    # You can add cookie manually by the following code, change the value !!
    insert_cookie(
        username='zhanyuanben85c@163.com',
        password='ORBtws829I4',
        cookie_str='_T_WM=5f7b46e3ad489944a4c22494b27b4aaa; SSOLoginState=1586873545; SUHB=0BLorNcpLMJsnD; SCF=AmfAT-ydYBWL_ip0UMdV5KYFRwiWaFNTPoxWBgCc76c8Pkt9oVwVg5a2ieoqdkrHa2aOmz4gKe6nE1SREywSD5w.; SUB=_2A25zkbSZDeRhGeFN71AY9i7FyzuIHXVRfdzRrDV6PUJbkdANLXbakW1NQDAS-0TOtMGiKXWy4aD1rzyAk4J2mRqv'
    )
