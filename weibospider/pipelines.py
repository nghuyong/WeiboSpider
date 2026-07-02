# -*- coding: utf-8 -*-
import datetime
import json
import os.path
import time


class JsonWriterPipeline(object):
    """
    写入json文件的pipline
    """

    def __init__(self):
        self.file = None
        # 获取当前文件目录
        current_dir = os.path.dirname(__file__)
        output_dir = os.path.join(current_dir, 'output')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def process_item(self, item, spider):
        """
        处理item
        """
        if not self.file:
            now = datetime.datetime.now()
            file_name = spider.name + "_" + now.strftime("%Y%m%d%H%M%S") + '.jsonl'
            # 确保output目录存在
            current_dir = os.path.dirname(__file__)
            output_dir = os.path.join(current_dir, 'output')
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                spider.logger.info(f'Created output directory: {output_dir}')
            self.file = open(f'{output_dir}/{file_name}', 'wt', encoding='utf-8')
            spider.logger.info(f'Created output file: {output_dir}/{file_name}')
        item['crawl_time'] = int(time.time())
        line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(line)
        self.file.flush()
        spider.logger.info(f'Saved item: {item.get("_id", "unknown")}')
        return item
