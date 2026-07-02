#!/usr/bin/env python
# encoding: utf-8
"""
Author: rightyonghu
Created Time: 2022/10/24
"""
import json
import re

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
    try:
        # 基本信息
        user = {
            "_id": str(data.get('id', '')),     
            "avatar_hd": data.get('avatar_hd', ''),
            "nick_name": data.get('screen_name', ''),
            "verified": data.get('verified', False),
        }
        # 额外的信息
        keys = ['description', 'followers_count', 'friends_count', 'statuses_count',
                'gender', 'location', 'mbrank', 'mbtype', 'credit_score']   
        for key in keys:
            if key in data:
                user[key] = data[key]   
        if 'created_at' in data:        
            try:
                user['created_at'] = parse_time(data.get('created_at'))
            except Exception:
                user['created_at'] = data.get('created_at', '')
        if user['verified']:
            user['verified_type'] = data.get('verified_type', 0)
            if 'verified_reason' in data:
                user['verified_reason'] = data['verified_reason']
        return user
    except Exception as e:
        print(f"Error parsing user info: {e}")
        return {}


def parse_tweet_info(data):
    """
    解析推文数据
    """
    try:
        tweet = {
            "_id": str(data.get('mid', '')),
            "mblogid": data.get('mblogid', ''),
            "created_at": parse_time(data.get('created_at')) if 'created_at' in data else '',
            "geo": data.get('geo', None),
            "ip_location": data.get('region_name', None),
            "reposts_count": data.get('reposts_count', 0),
            "comments_count": data.get('comments_count', 0),
            "attitudes_count": data.get('attitudes_count', 0),
            "source": data.get('source', ''),
            "content": data.get('text_raw', '').replace('\u200b', ''),
            "pic_urls": ["https://wx1.sinaimg.cn/orj960/" + pic_id for pic_id in data.get('pic_ids', [])],
            "pic_num": data.get('pic_num', 0),
            'isLongText': False,
            'is_retweet': False,
            "user": parse_user_info(data.get('user', {})) if 'user' in data else {},
        }
        if '</a>' in tweet['source']:
            try:
                tweet['source'] = re.search(r'>(.*?)</a>', tweet['source']).group(1)
            except Exception:
                pass
        if 'page_info' in data and data['page_info'].get('object_type', '') == 'video':
            media_info = None
            if 'media_info' in data['page_info']:
                media_info = data['page_info']['media_info']
            elif 'cards' in data['page_info'] and len(data['page_info']['cards']) > 0 and 'media_info' in data['page_info']['cards'][0]:
                media_info = data['page_info']['cards'][0]['media_info']
            if media_info:
                tweet['video'] = media_info.get('stream_url', '')
                # 视频播放量
                tweet['video_online_numbers'] = media_info.get('online_users_number', None)
        if 'user' in data and data['user'].get('id') and data.get('mblogid'):
            tweet['url'] = f"https://weibo.com/{data['user']['id']}/{data['mblogid']}"
        elif tweet['user'].get('_id') and tweet['mblogid']:
            tweet['url'] = f"https://weibo.com/{tweet['user']['_id']}/{tweet['mblogid']}"
        if 'continue_tag' in data and data.get('isLongText'):
            tweet['isLongText'] = True
        if 'retweeted_status' in data:
            tweet['is_retweet'] = True
            tweet['retweet_id'] = data['retweeted_status'].get('mid', '')
        if 'reads_count' in data:
            tweet['reads_count'] = data['reads_count']
        return tweet
    except Exception as e:
        print(f"Error parsing tweet info: {e}")
        import traceback
        traceback.print_exc()
        return {}


def parse_long_tweet(response):
    """
    解析长推文
    """
    data = json.loads(response.text)['data']
    item = response.meta['item']
    item['content'] = data['longTextContent']
    yield item
