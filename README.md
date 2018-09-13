# WeiboSpider
This is a sina weibo spider built by scrapy

**这是一个持续维护彻底的微博开源项目**

更多关于微博爬虫的介绍请移步:[微博爬虫总结：构建单机千万级别的微博爬虫系统](http://www.nghuyong.top/2018/09/12/spider/%E5%BE%AE%E5%8D%9A%E7%88%AC%E8%99%AB%E6%80%BB%E7%BB%93%EF%BC%9A%E6%9E%84%E5%BB%BA%E5%8D%95%E6%9C%BA%E5%8D%83%E4%B8%87%E7%BA%A7%E5%88%AB%E7%9A%84%E5%BE%AE%E5%8D%9A%E7%88%AC%E8%99%AB%E7%B3%BB%E7%BB%9F/)

## 项目说明
该项目分为3个分支，以满足不同的需要

|    分支   | 特点 | 单机每日抓取量 |
| :---: | :----: |:----: |
| simple | 单账号 | 十万级|
| master | 账号池 | 百万级|
| senior | 账号池+分布式 | 千万级+ | 

## 如何使用
下面是master分支，也就是构建单机百万级的爬虫

如果你只想用你自己的一个账号简单爬取微博，每日十万级即可，请移步simple分支

如果你需要大规模爬取微博，需要单机千万级别，请移步senior分支

### 克隆本项目 && 安装依赖
本项目Python版本为Python3.6
```bash
git clone git@github.com:nghuyong/WeiboSpider.git
cd WeiboSpider
pip install -r requirements.txt
```
除此之外，还需要安装mongodb和phantomjs，这个自行Google把

### 购买账号
小号购买地址(**访问需要翻墙**): http://www.xiaohao.shop/ 

购买普通国内手机号注册的小号即可

![](./images/xiaohao.shop.png)

购买越多，sina/settings.py 中的延迟就可以越低，并发也就可以越大

**将购买的账号复制到`sina/account_build/account.txt`中，格式与`account_sample.txt`保持一致**。

### 构建账号池

```bash
python sina/account_build/login.py
```
运行截图:

![](./images/account_build_screenshot.png)

这是你的mongodb中将多一个账号表，如下所示:

![](./images/account.png)

### 运行爬虫
```bash
scrapy crawl weibo_spider 
```
运行截图:

![](./images/spider.png)

导入pycharm后，也可以直接执行`sina/spider/weibo_spider.py`

该爬虫是示例爬虫，将爬取 人民日报 和 新华视点 的 用户信息，全部微博，每条微博的评论，还有用户关系。

可以根据你的实际需求改写示例爬虫。


## 微博数据字段

### 用户数据
|    字段   | 说明 |
| :---: | :----: |
|_id       | 用户的ID，可以作为用户的唯一标识 |
|nick_name|昵称|
|gender|性别|
|province | 所在省|
|city |所在市|
|brief_introduction|个人简介|
|birthday |生日|
|tweets_num | 微博发表数|
|fans_num| 粉丝数|
|followers_num|关注数|
|sex_orientation|性取向|
|sentiment|感情状况|
|vip_level| 会员等级|
|authentication|认证情况|
|person_url|用户首页链接|
|crawl_time|抓取时间戳|

示例:
![](./images/information.png)


### 微博数据
|    字段   | 说明 |
| :---: | :----: |
| _id | 微博id |
|user_id       | 这则微博作者的ID |
|content |微博的内容|
|created_at |微博发表时间|
|repost_num |转发数|
|comment_num |评论数|
|like_num| 点赞数|
|crawl_time|抓取时间戳|

示例:
![](./images/tweet.png)

### 用户关系数据
|    字段   | 说明 |
| :---: | :----: |
| _id | 用户关系id |
|fan_id| 关注者的用户ID |
|follower_id|被关注者的用户ID|
|crawl_time|抓取时间戳|

示例:
![](./images/relationship.png)

### 评论数据
|    字段   | 说明 |
| :---: | :----: |
| _id | 评论的id |
|comment_user_id|评论的用户ID|
|weibo_url|weibo的URL|
|content|评论内容|
|created_at| 评论创建时间|
|crawl_time|抓取时间戳|

示例:
![](./images/comment.png)

