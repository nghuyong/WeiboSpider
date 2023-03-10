# 准备json文件，里边内容为：{"name": "tom", "age": "28"}

import json
import pymysql
import emoji

# 连接数据库
conn = pymysql.connect(
    host='localhost',
    # 端口号
    port=3306,
    # 用户名
    user='root',
    # 密码
    passwd='123123123',
    # 数据库名称
    # db='weibo',
    # 字符编码格式
    charset='utf8')

cur = conn.cursor()

# # 插入的表名
table = 'weibo.t_follow_userprofile'

# 建表语句，字段要与json中的key值对应
# createTableSql = f'CREATE table IF NOT EXISTS {table}(uid varchar(20), nick_name varchar(20), location varchar(20), birthday varchar(20) default null, created_at varchar(20) default null, ip_location varchar(20) default null) ENGINE=InnoDB DEFAULT CHARSET=utf8;'


# json在我本地的路径
jsonPath = '/Users/yunpeng/Desktop/content/WeiboSpider/output/user_batch_spider_20230310154305.jsonl'

# 打开json文件
with open(jsonPath, 'r', encoding='utf_8_sig') as f:
    # 读取json文件
    for line in f.readlines():
        # 读取json文件格式为python的dict字典类型
        dic = json.loads(line)

        # 不需要的表头
        del_colum = ['verified_type', 'verified_reason', 'crawl_time']
        # 需要添加的表头
        add_colum = ['company', 'education']

        for item in del_colum:
            if item in dic:
                dic.pop(item)

        for item in add_colum:
            if item in dic:
                # 因为表顺序已经固定，所以只能按照add_colum 的顺序去定义 赋值
                temp = dic[item]
                dic.pop(item)
                dic[item] = temp
            if item not in dic:
                dic[item] = 'null'

        # 剔除键值为空的list
        for item in dic:
            # 如果数组为空，则复制为null
            if isinstance(dic[item], list):
                if len(dic[item]) == 0:
                    dic[item] = 'null'
            # 如果键值为dict, 则转化为字符串
            if isinstance(dic[item], dict):
                dic[item] = str(dic[item])
            # 去除 label_desc的特殊字符
            if isinstance(dic[item], list):
                dic[item] = ''.join(dic[item]).replace('，', ' & ')

        # 拼接key值为：name,age
        keys = ','.join(dic.keys())

        # 将value值存为列表类型：['tom', '28'] <class 'list'>
        valuesList = [dici for dici in dic.values()]

        # 剔除emoji表情
        for i in range(len(valuesList)):
            if isinstance(valuesList[i], str):
                valuesList[i] = emoji.demojize(valuesList[i])

        # 将value值存为元组类型：('tom', '28')
        valuesTuple = tuple(valuesList)

        # 拼接values为：%s, %s
        values = ', '.join(['%s'] * len(dic))

        # 插入sql语句
        insertSql = 'INSERT INTO {table}({keys}) VALUES ({values})'.format(table=table, keys=keys, values=values)
        print(insertSql, valuesTuple)
        #
        # 执行建表
        # 放在sql文件内执行
        # cur.execute(createTableSql)

        # 插入到sql
        cur.execute(insertSql, valuesTuple)
        # 提交commit
        conn.commit()

    # 关闭数据库连接
    conn.close()
