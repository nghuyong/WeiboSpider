<p align="center">
    <br>
    <img src="./.github/weibospider.png" width="400"/>
    <br>
<p>
<p align="center">
  <a href="https://www.codacy.com/gh/nghuyong/WeiboSpider/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=nghuyong/WeiboSpider&amp;utm_campaign=Badge_Grade">
    <img src="https://app.codacy.com/project/badge/Grade/cf88a8b1e6e44c5d993d2cbea7d44c85"
         alt="Codacy Badge">
  </a>
    <a href="https://scan.coverity.com/projects/nghuyong-weibospider">
    <img alt="Coverity Scan Build Status"
       src="https://scan.coverity.com/projects/26928/badge.svg"/>
  </a>
    <a href="https://github.com/nghuyong/WeiboSpider/stargazers">
    <img src="https://img.shields.io/github/stars/nghuyong/WeiboSpider.svg?colorA=orange&colorB=orange&logo=github"
         alt="GitHub stars">
  </a>
  <a href="https://github.com/nghuyong/WeiboSpider/issues">
        <img src="https://img.shields.io/github/issues/nghuyong/WeiboSpider.svg"
             alt="GitHub issues">
  </a>
  <a href="https://github.com/nghuyong/WeiboSpider/forks">
        <img src="https://img.shields.io/github/forks/nghuyong/WeiboSpider.svg"
             alt="GitHub forks">
  </a>
  <a href="https://github.com/nghuyong/WeiboSpider/">
        <img src="https://img.shields.io/github/last-commit/nghuyong/WeiboSpider.svg">
  </a>
  <a href="https://github.com/nghuyong/WeiboSpider/blob/master/LICENSE">
        <img src="https://img.shields.io/github/license/nghuyong/WeiboSpider.svg"
             alt="GitHub license">
  </a>
</p>

<h4 align="center">
    <p>持续维护的新浪微博采集工具🚀🚀🚀</p>
</h4>

## 补充
- cookie.txt 处于失效状态，需更新为有效的
- batchUser 批量从json文件内获取userid,去获得其user profile
- 将user profile的信息，导入到数据库内 
- mysql -u root -p < user.sql , 需要注意表名，需要与jsonTosql.py内的table的变量一致
- 然后执行jsonTosql.py文件


## 项目特色

- 基于weibo.com的新版API构建，拥有最丰富的字段信息
- 多种采集模式，包含微博用户,推文,粉丝,关注,转发,评论,关键词搜索
- 核心代码仅100行，代码可读性高，可快速按需进行定制化改造

## 快速开始

### 拉取&&安装

```bash
git clone git@github.com:nghuyong/WeiboSpider.git --depth 1 --no-single-branch
cd WeiboSpider
pip install -r requirements.txt
```

### 替换Cookie

访问[https://weibo.com/](https://weibo.com/)， 登陆账号，打开浏览器的开发者模式，再次刷新

![](.github/cookie.png)

复制`weibo.com`数据包，network中的cookie值。编辑`weibospider/cookie.txt`并替换成刚刚复制的Cookie

### 添加代理IP(可选)

重写[fetch_proxy](./weibospider/middlewares.py#6L)
方法，该方法需要返回一个代理ip，具体参考[这里](https://github.com/nghuyong/WeiboSpider/issues/124#issuecomment-654335439)

## 运行程序

根据自己实际需要重写`./weibospider/spiders/*`中的`start_requests`函数

采集的数据存在`output`文件中，命名为`{spider.name}_{datetime}.jsonl`

### 用户信息采集

```bash
cd weibospider
python run_spider.py user
```

```json
{
  "crawl_time": 1666863485,
  "_id": "1749127163",
  "avatar_hd": "https://tvax4.sinaimg.cn/crop.0.0.1080.1080.1024/001Un9Srly8h3fpj11yjyj60u00u0q7f02.jpg?KID=imgbed,tva&Expires=1666874283&ssig=a%2FMfgFzvRo",
  "nick_name": "雷军",
  "verified": true,
  "description": "小米董事长，金山软件董事长。业余爱好是天使投资。",
  "followers_count": 22756103,
  "friends_count": 1373,
  "statuses_count": 14923,
  "gender": "m",
  "location": "北京 海淀区",
  "mbrank": 7,
  "mbtype": 12,
  "verified_type": 0,
  "verified_reason": "小米创办人，董事长兼CEO；金山软件董事长；天使投资人。",
  "birthday": "",
  "created_at": "2010-05-31 23:07:59",
  "desc_text": "小米创办人，董事长兼CEO；金山软件董事长；天使投资人。",
  "ip_location": "IP属地：北京",
  "sunshine_credit": "信用极好",
  "label_desc": [
    "V指数 财经 75.30分",
    "热门财经博主 数据飙升",
    "昨日发博3，阅读数100万+，互动数1.9万",
    "视频累计播放量9819.3万",
    "群友 3132"
  ],
  "company": "金山软件",
  "education": {
    "school": "武汉大学"
  }
}
```

### 用户粉丝列表采集

```bash
python run_spider.py fan
```

```json
{
  "crawl_time": 1666863563,
  "_id": "1087770692_5968044974",
  "follower_id": "1087770692",
  "fan_info": {
    "_id": "5968044974",
    "avatar_hd": "https://tvax1.sinaimg.cn/default/images/default_avatar_male_180.gif?KID=imgbed,tva&Expires=1666874363&ssig=UuzaeK437R",
    "nick_name": "用户5968044974",
    "verified": false,
    "description": "",
    "followers_count": 0,
    "friends_count": 195,
    "statuses_count": 9,
    "gender": "m",
    "location": "其他",
    "mbrank": 0,
    "mbtype": 0,
    "credit_score": 80,
    "created_at": "2016-06-25 22:30:13"
  }
}
...
```

### 用户关注列表采集

```bash
python run_spider.py follow
```

```json
{
  "crawl_time": 1666863679,
  "_id": "1087770692_7083568088",
  "fan_id": "1087770692",
  "follower_info": {
    "_id": "7083568088",
    "avatar_hd": "https://tvax4.sinaimg.cn/crop.0.0.1080.1080.1024/007JnVEcly8gyqd9jadjlj30u00u0gpn.jpg?KID=imgbed,tva&Expires=1666874479&ssig=9zhfeMPLzr",
    "nick_name": "蒋昀霖",
    "verified": true,
    "description": "工作请联系：lijialun@kpictures.cn",
    "followers_count": 329216,
    "friends_count": 58,
    "statuses_count": 342,
    "gender": "m",
    "location": "北京",
    "mbrank": 6,
    "mbtype": 12,
    "credit_score": 80,
    "created_at": "2019-04-17 16:25:43",
    "verified_type": 0,
    "verified_reason": "东申未来 演员"
  }
}
...
```

### 用户的微博采集

```bash
python run_spider.py tweet
```

```json
{
  "crawl_time": 1666864583,
  "_id": "4762810834227120",
  "mblogid": "LqlZNhJFm",
  "created_at": "2022-04-27 10:20:54",
  "geo": null,
  "ip_location": null,
  "reposts_count": 1907,
  "comments_count": 1924,
  "attitudes_count": 12169,
  "source": "三星Galaxy S22 Ultra",
  "content": "生于乱世纵横四海，义之所在不计生死，孤勇者陈恭一生当如是。#风起陇西今日开播# #风起陇西#  今晚，恭候你！",
  "pic_urls": [],
  "pic_num": 0,
  "video": "http://f.video.weibocdn.com/o0/CmQEWK1ylx07VAm0nrxe01041200YDIc0E010.mp4?label=mp4_720p&template=1280x720.25.0&ori=0&ps=1CwnkDw1GXwCQx&Expires=1666868183&ssig=RlIeOt286i&KID=unistore,video",
  "url": "https://weibo.com/1087770692/LqlZNhJFm"
}
...
```

### 微博评论采集

```bash
python run_spider.py comment
```

```json
{
  "crawl_time": 1666863805,
  "_id": 4826279188108038,
  "created_at": "2022-10-19 13:41:29",
  "like_counts": 1,
  "ip_location": "来自河南",
  "content": "五周年快乐呀，请坤哥哥继续保持这份热爱，奔赴下一场山海",
  "comment_user": {
    "_id": "2380967841",
    "avatar_hd": "https://tvax4.sinaimg.cn/crop.0.0.888.888.1024/002B8iv7ly8gv647ipgxvj60oo0oojtk02.jpg?KID=imgbed,tva&Expires=1666874604&ssig=%2FdGaaIRkhf",
    "nick_name": "流年执念的二瓜娇",
    "verified": false,
    "description": "蓝桉已遇释怀鸟，不爱万物唯爱你。",
    "followers_count": 238,
    "friends_count": 1655,
    "statuses_count": 12546,
    "gender": "f",
    "location": "河南",
    "mbrank": 6,
    "mbtype": 11
  }
}
...
```

### 微博转发采集

```bash
python run_spider.py repost
```

```json
{
  "_id": "4826312651310475",
  "mblogid": "Mb2vL5uUH",
  "created_at": "2022-10-19 15:54:27",
  "geo": null,
  "ip_location": "发布于 德国",
  "reposts_count": 0,
  "comments_count": 0,
  "attitudes_count": 0,
  "source": "iPhone客户端",
  "content": "共享[鼓掌][太开心][鼓掌]五周年快乐！//@陈坤:#山下学堂五周年# 五年， 感谢同行。",
  "pic_urls": [],
  "pic_num": 0,
  "user": {
    "_id": "2717869081",
    "avatar_hd": "https://tvax1.sinaimg.cn/crop.0.0.160.160.1024/a1ff6419ly8gz1xoq9oolj204g04g745.jpg?KID=imgbed,tva&Expires=1666876939&ssig=Cl93CLjdB%2F",
    "nick_name": "YuFeeC",
    "verified": false,
    "mbrank": 0,
    "mbtype": 0
  },
  "url": "https://weibo.com/2717869081/Mb2vL5uUH",
  "crawl_time": 1666866139
}
...
```

### 基于关键词的微博检索

```bash
python run_spider.py search
```

```json
{
  "crawl_time": 1666869049,
  "keyword": "丽江",
  "_id": "4829255386537989",
  "mblogid": "Mch46rqPr",
  "created_at": "2022-10-27 18:47:50",
  "geo": {
    "type": "Point",
    "coordinates": [
      26.962427,
      100.248299
    ],
    "detail": {
      "poiid": "B2094251D06FAAF44299",
      "title": "山野文创旅拍圣地",
      "type": "checkin",
      "spot_type": "0"
    }
  },
  "ip_location": "发布于 云南",
  "reposts_count": 0,
  "comments_count": 0,
  "attitudes_count": 1,
  "source": "iPhone1314iPhone客户端",
  "content": "丽江小漾日出\n推出户外移动餐桌\n接受私人定制\n让美食融入美景心情自然美丽了！\n#小众宝藏旅行地##超出片的艺术街区#  ",
  "pic_urls": [
    "https://wx1.sinaimg.cn/orj960/4b138405gy1h7k1a56c4oj234022onph",
    "https://wx1.sinaimg.cn/orj960/4b138405gy1h7k19eb2kxj22ts1vvb2a",
    "https://wx1.sinaimg.cn/orj960/4b138405gy1h7k1a0wzglj22ua1w7hdw",
    "https://wx1.sinaimg.cn/orj960/4b138405gy1h7k19wsafnj231x21a7wj",
    "https://wx1.sinaimg.cn/orj960/4b138405gy1h7k19jd1xkj22oh1sbkjo",
    "https://wx1.sinaimg.cn/orj960/4b138405gy1h7k19mma74j22ru1ukx6q",
    "https://wx1.sinaimg.cn/orj960/4b138405gy1h7k19tf1bfj234022oe85",
    "https://wx1.sinaimg.cn/orj960/4b138405gy1h7k19pk37pj234022okjm",
    "https://wx1.sinaimg.cn/orj960/4b138405gy1h7k19g6nzfj20wi0lo7my"
  ],
  "pic_num": 9,
  "user": {
    "_id": "1259570181",
    "avatar_hd": "https://tvax1.sinaimg.cn/crop.0.0.1080.1080.1024/4b138405ly8gzfkfikyqvj20u00u0ag1.jpg?KID=imgbed,tva&Expires=1666879848&ssig=6PUDG5RonQ",
    "nick_name": "飞鸟与鱼",
    "verified": true,
    "mbrank": 7,
    "mbtype": 12,
    "verified_type": 0
  },
  "url": "https://weibo.com/1259570181/Mch46rqPr"
}
...
```

## 更新日志

- 2022.11: 支持针对单个关键词获取单天超过1200页的检索结果 [#257](https://github.com/nghuyong/WeiboSpider/issues/257)
- 2022.11: 支持长微博全文的获取
- 2022.11: 基于关键词微博搜索支持指定时间范围
- 2022.10: 添加IP归属地信息的采集，包括用户数据，微博数据和微博评论数据
- 2022.10: 基于weibo.com站点对项目进行重构

## 其他工作

- 已构建超大规模数据集WeiboCOV，可免费申请，包含2千万微博活跃用户以及6千万推文数据，参见[这里](https://github.com/nghuyong/weibo-public-opinion-datasets)
