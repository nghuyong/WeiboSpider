# 准备json文件，里边内容为：{"name": "tom", "age": "28"}

import json
import pymysql

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

# 建表语句，字段要与json中的key值对应
createTableSql = 'CREATE table IF NOT EXISTS weibo.t_fan_userprofile(uid varchar(20), nick_name varchar(20), location varchar(20), birthday varchar(20) default null, created_at varchar(20) default null, ip_location varchar(20) default null) ENGINE=InnoDB DEFAULT CHARSET=utf8;'
# json在我本地的路径
jsonPath = '/Users/yunpeng/Desktop/content/WeiboSpider/output/user_spider_20230209213322.jsonl'

# 打开json文件
with open(jsonPath, 'r', encoding='utf_8_sig') as f:
    # 读取json文件
    for line in f.readlines():
        # 读取json文件格式为python的dict字典类型
        dic = json.loads(line)

        # 不需要的表头
        noNeedColums = ['verified_type', 'verified_reason', 'crawl_time']
        # 需要添加的表头
        needAddColums = ['company', 'education']
        for notclm in noNeedColums:
            if (notclm in dic):
                 dic.pop(notclm)

        for needclm in needAddColums:
            if (needclm in dic):
                temp = dic[needclm]
                dic.pop(needclm)
                dic[needclm] = temp
            if (needclm not in dic):
                 dic[needclm] = 'null'

        # 剔除空list
        for eitem in dic:
            if(isinstance(dic[eitem], list)):
                if len(dic[eitem]) == 0:
                    dic[eitem] = 'null'
            if (isinstance(dic[eitem], dict)):
                dic[eitem] = str(dic[eitem])
                # print(type(dic[eitem]), ))



        # 拼接key值为：name,age
        keys = ','.join(dic.keys())


        # 将value值存为列表类型：['tom', '28'] <class 'list'>
        valuesList = [dici for dici in dic.values()]


        # 将value值存为元组类型：('tom', '28')
        valuesTuple = tuple(valuesList)

        # 拼接values为：%s, %s
        values = ', '.join(['%s'] * len(dic))


        # # 插入的表名
        table = 'weibo.t_fan_userprofile'
        #
        # 插入sql语句
        insertSql = 'INSERT INTO {table}({keys}) VALUES ({values})'.format(table=table, keys=keys, values=values)
        print(insertSql, valuesTuple)
        #
        # 执行建表与插入sql
        # cur.execute(createTableSql)
        cur.execute(insertSql, valuesTuple)
        #
        # 提交commit
        conn.commit()

    # 关闭数据库连接
    conn.close()




