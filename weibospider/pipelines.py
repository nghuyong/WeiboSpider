# -*- coding: utf-8 -*-
import datetime
import json
import os.path
import time

import pymongo


class JsonWriterPipeline(object):
    """
    写入json文件的pipline
    """

    def __init__(self):
        self.client = pymongo.MongoClient(os.environ.get('IP'), 27017)
        self.collection = self.client['weibo']["relationships"]

    def process_item(self, item, spider):
        """
        处理item
        """
        try:
            self.collection.insert_one(item)
        except:
            pass
        return item
