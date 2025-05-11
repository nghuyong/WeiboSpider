# -*- coding: utf-8 -*-
import datetime
import json
import os.path
import time
import logging

logger = logging.getLogger(__name__)

class JsonWriterPipeline(object):
    """
    写入json文件的pipline
    """

    def __init__(self):
        self.file = None
        self.item_count = 0
        if not os.path.exists('../output'):
            os.mkdir('../output')
            logger.info("Created output directory")

    def process_item(self, item, spider):
        """
        处理item
        """
        if not self.file:
            now = datetime.datetime.now()
            file_name = spider.name + "_" + now.strftime("%Y%m%d%H%M%S") + '.jsonl'
            self.file = open(f'../output/{file_name}', 'wt', encoding='utf-8')
            logger.info(f"Created new output file: {file_name}")
        
        item['crawl_time'] = int(time.time())
        line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(line)
        self.file.flush()
        
        self.item_count += 1
        if self.item_count % 100 == 0:
            logger.info(f"Written {self.item_count} items to {self.file.name}")
        
        return item

    def close_spider(self, spider):
        """
        Called when spider is closed
        """
        if self.file:
            logger.info(f"Spider closed. Total items written: {self.item_count}")
            self.file.close()
