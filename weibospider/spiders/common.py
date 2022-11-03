#!/usr/bin/env python
# encoding: utf-8
"""
Author: rightyonghu
Created Time: 2022/10/24
"""
import json

import dateutil.parser


def base62_decode(string):
    """
    base
    """
    alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    string = str(string)
    num = 0
    idx = 0
    for char in string:
        power = (len(string) - (idx + 1))
        num += alphabet.index(char) * (len(alphabet) ** power)
        idx += 1

    return num


def reverse_cut_to_length(content, code_func, cut_num=4, fill_num=7):
    """
    url to mid
    """
    content = str(content)
    cut_list = [content[i - cut_num if i >= cut_num else 0:i] for i in range(len(content), 0, (-1 * cut_num))]
    cut_list.reverse()
    result = []
    for i, item in enumerate(cut_list):
        s = str(code_func(item))
        if i > 0 and len(s) < fill_num:
            s = (fill_num - len(s)) * '0' + s
        result.append(s)
    return ''.join(result)


def url_to_mid(url: str):
    """>>> url_to_mid('z0JH2lOMb')
    3501756485200075
    """
    result = reverse_cut_to_length(url, base62_decode)
    return int(result)


def parse_time(s):
    """
    Wed Oct 19 23:44:36 +0800 2022 => 2022-10-19 23:44:36
    """
    return dateutil.parser.parse(s).strftime('%Y-%m-%d %H:%M:%S')


def parse_user_info(data):
    """
    解析用户信息
    """
    # 基础信息
    user = {
        "_id": str(data['id']),
        "avatar_hd": data['avatar_hd'],
        "nick_name": data['screen_name'],
        "verified": data['verified'],
    }
    # 额外的信息
    keys = ['description', 'followers_count', 'friends_count', 'statuses_count',
            'gender', 'location', 'mbrank', 'mbtype', 'credit_score']
    for key in keys:
        if key in data:
            user[key] = data[key]
    if 'created_at' in data:
        user['created_at'] = parse_time(data.get('created_at'))
    if user['verified']:
        user['verified_type'] = data['verified_type']
        if 'verified_reason' in data:
            user['verified_reason'] = data['verified_reason']
    return user


def parse_tweet_info(data):
    """
    解析推文数据
    """
    tweet = {
        "_id": str(data['mid']),
        "mblogid": data['mblogid'],
        "created_at": parse_time(data['created_at']),
        "geo": data['geo'],
        "ip_location": data.get('region_name', None),
        "reposts_count": data['reposts_count'],
        "comments_count": data['comments_count'],
        "attitudes_count": data['attitudes_count'],
        "source": data['source'],
        "content": data['text_raw'].replace('\u200b', ''),
        "pic_urls": ["https://wx1.sinaimg.cn/orj960/" + pic_id for pic_id in data.get('pic_ids', [])],
        "pic_num": data['pic_num'],
        'isLongText': False,
        "user": parse_user_info(data['user']),
    }
    if 'page_info' in data and data['page_info'].get('object_type', '') == 'video':
        tweet['video'] = data['page_info']['media_info']['mp4_720p_mp4']
    tweet['url'] = f"https://weibo.com/{tweet['user']['_id']}/{tweet['mblogid']}"
    if 'continue_tag' in data and data['isLongText']:
        tweet['isLongText'] = True
    return tweet


def parse_long_tweet(response):
    """
    解析长推文
    """
    data = json.loads(response.text)['data']
    item = response.meta['item']
    item['content'] = data['longTextContent']
    yield item
