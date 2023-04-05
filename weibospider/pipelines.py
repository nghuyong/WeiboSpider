# -*- coding: utf-8 -*-
from datetime import datetime
import json
import time


class JsonlWriterPipeline(object):
    """
    写入jsonl文件的pipline
    """

    def open_spider(self, spider):
        now_str = datetime.now().strftime("%Y%m%d%H%M%S")
        # TODO format other spider file name
        if spider.name == 'search_spider':
            # search spider file name format: search_<keyword>_<content_type>_<content_include>_<time_from>_<time_to>_<crawl_time>.jsonl
            file_name = f'search_{spider.keyword}_{spider.ct}_{spider.ci}_{spider.tf}_{spider.tt}_{now_str}.jsonl'
        else:
            file_name = spider.name + "_" + now_str + '.jsonl'
        self.file = open(f'../output/{file_name}', 'wt', encoding='utf-8')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        """
        处理item
        """

        item['crawl_ts'] = int(time.time())
        line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(line)
        self.file.flush()
        return item
