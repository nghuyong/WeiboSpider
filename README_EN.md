# WeiboSpider
<a href="https://github.com/nghuyong/WeiboSpider/stargazers">
    <img src="https://img.shields.io/github/stars/nghuyong/WeiboSpider.svg?colorA=orange&colorB=orange&logo=github"
         alt="GitHub stars">
  </a>
  <a href="https://github.com/nghuyong/WeiboSpider/issues">
        <img src="https://img.shields.io/github/issues/nghuyong/WeiboSpider.svg"
             alt="GitHub issues">
  </a>
  <a href="https://github.com/nghuyong/WeiboSpider/">
        <img src="https://img.shields.io/github/last-commit/nghuyong/WeiboSpider.svg">
  </a>
  <a href="https://github.com/nghuyong/WeiboSpider/blob/master/LICENSE">
        <img src="https://img.shields.io/github/license/nghuyong/WeiboSpider.svg"
             alt="GitHub license">
</a>

This may be the most powerful Weibo spider in the whole Internet[Ongoing maintenance]

## Introduction

### Branches
The project has 2 branches to meet different needs:

|Branch|Features|Magnitude of the crawled data|
|:---:|:---:|:---:|
|[simple](https://github.com/nghuyong/WeiboSpider/tree/simple)|Single account, single IP, single machine|Hundreds of thousands|
|[master](https://github.com/nghuyong/WeiboSpider/tree/master)|Account pool, IP pool, Docker|Hundreds of millions(**Theoretical unlimited**)|

### Supported crawling types
- User Information
- Tweets post by user
- Users' social relationships (fans/followers)
- Comments of tweets
- Tweets based on keywords and time period

### Data Structure
The spider based on the `weibo.cn`, 
and the crawled fields are very rich.
More detail:
[Data Structure Description](./.github/data_stracture.md)

## Get Started

### Pull Docker images

```bash
docker pull portainer/portainer
docker pull mongo
docker pull mongo-express
docker pull redis
docker pull registry.cn-hangzhou.aliyuncs.com/weibospider/account
docker pull registry.cn-hangzhou.aliyuncs.com/weibospider/spider
```

### Run the project
```bash
docker stack deploy -c <(docker-compose config) weibospider
```

```bash
docker service ls 
-----------------
ID                  NAME                               MODE                REPLICAS            IMAGE                                                          PORTS
f7yx1cjh1izt        weibospider_portainer              replicated          1/1                 portainer/portainer:latest                                     *:7000->9000/tcp
5szekv996su0        weibospider_mongodb                replicated          1/1                 mongo:latest                                                   *:7001->27017/tcp
lq7kmlekcrlg        weibospider_mongo-express          replicated          1/1                 mongo-express:latest                                           *:7002->8081/tcp
xjbddlf53hai        weibospider_redis                  replicated          1/1                 redis:latest                                                   *:7003->6379/tcp
mk8dmh6nl17i        weibospider_account                replicated          1/1                 registry.cn-hangzhou.aliyuncs.com/weibospider/account:latest
nvo9dt0r5v2t        weibospider_weibo-spider-comment   replicated          1/1                 registry.cn-hangzhou.aliyuncs.com/weibospider/spider:latest
vbnyacpm3xle        weibospider_weibo-spider-fan       replicated          1/1                 registry.cn-hangzhou.aliyuncs.com/weibospider/spider:latest
qyvu9wt0fzny        weibospider_weibo-spider-follow    replicated          1/1                 registry.cn-hangzhou.aliyuncs.com/weibospider/spider:latest
h3dfh8qr1eak        weibospider_weibo-spider-tweet     replicated          1/1                 registry.cn-hangzhou.aliyuncs.com/weibospider/spider:latest
jiaz176hzbls        weibospider_weibo-spider-user      replicated          1/1                 registry.cn-hangzhou.aliyuncs.com/weibospider/spider:latest
```
- portainer http://127.0.0.1:7000 

Through the portainer, we can easily manage all services, 
monitor the service status, and view logs of services.

Through the setting of `scale`, we can quickly run the service (set to 1),
stop the service (set to 0), and expand the service (such as, set to 100).

<img src="./.github/images/protainer.png" width = "80%" height = "80%" alt="protainer" align=center />

- mongo-express http://127.0.0.1:7002

We can easily manage mongodb through mongo-express.

<img src="./.github/images/mongo-express.png" width = "80%" height = "80%" alt="mongo-express" align=center />


### Build Account Pool
**Prepare accounts without verification code**, we will discuss at [here](https://github.com/nghuyong/WeiboSpider/issues/139).

Fill the purchased accounts into the file`./weibospider/account/account.txt`,
and the format should be the same as `./weibospider/account/account_sample.txt`

Get the container id of `account_service` and enter into the container.
```bash
docker container ls | grep weibospider_account
1f15415443f8        registry.cn-hangzhou.aliyuncs.com/weibospider/account:latest   "python3"                22 minutes ago      Up 22 minutes                           weibospider_account.1.h091uc5sm0l1iz9oxpa7ypwak

docker exec -it 1f15415443f8 bash
root@1f15415443f8:/app#
```

Build accounts pool
```bash
root@1f15415443f8:/app# cd account
root@1f15415443f8:/app# python login.py
2020-04-15 11:56:56 ==============================
2020-04-15 11:56:56 start fetching cookie [zhanyuanben85c@163.com]
2020-04-15 11:57:04 cookie: _T_WM=0bfd51e7d3bdc1f914c5dbce3a4b20e0; SSOLoginState=1586923020; SUHB=010GS1NzSA-zOR; SCF=AmfAT-ydYBWL_ip0UMdV5KYFRwiWaFNTPoxWBgCc76c8PHXBkcp-CSNZArDRyyt1oShEm-T4Qukkw9W9n5eGrXA.; SUB=_2A25zkvZcDeRhGeFN71AY9i7FyzuIHXVRfJoUrDV6PUJbkdANLXjTkW1NQDAS-yKGeo_seRGTTKVAeOs1IG_ucher
2020-04-15 11:57:04 ==============================
2020-04-15 11:57:04 start fetching cookie [chuicong7188031104@163.com]
2020-04-15 11:57:11 cookie: _T_WM=6cf59fb4e2df7ba2b15e93d6bc184940; SSOLoginState=1586923028; SUHB=06ZV1_UTgTUirk; SCF=AvGBrUc4rNRZapeLXnQjOvrK9SyaN8dtGH_JfZamRkCRwCC6H1NJmJ6EVdZG26_lwfURJ233mRb5G-ZiM3WgGWA.; SUB=_2A25zkvZEDeRhGeFN71ET9S_Fzj6IHXVRfJoMrDV6PUJbkdANLRahkW1NQDAPyyhLB1NH_XSKtFoOQ2xwxkKWEMh5
2020-04-15 11:57:11 ==============================
2020-04-15 11:57:11 start fetching cookie [zhi21614055@163.com]
2020-04-15 11:57:19 cookie: _T_WM=6cc104aff523785aed114eb28996cb84; SSOLoginState=1586923035; SUHB=0bts1yfOjc42hI; SCF=AtAdd0uPAxdek8Hhh6JBOkxqFANmv7EqVebH6aHdY-3T_LUHoaIp6TaCo_57zCFZ-izJVcs01qs20b5cBpuwS_c.; SUB=_2A25zkvZLDeRhGeFN71AY9CjLwjuIHXVRfJoDrDV6PUJbkdANLWXjkW1NQDAJWlhRm6NkHCqHoOG9PBE1DOsaqX39
```
----
If you can’t buy accounts without a verification code, you can also [get cookies directly from the web](https://github.com/nghuyong/WeiboSpider/tree/simple#%E6%9B%BF%E6%8D%A2cookie),
Modify the parameters of  [insert_cookie](./weibospider/account/db_utils.py#L33).

```bash
# Add cookie one by one manually
root@1f15415443f8:/app# python db_utils.py
```

### Add Proxy IP
Rewrite the function [fetch_proxy](./weibospider/middlewares.py#L52).

### Init Redis

```bash
root@be3ac5910132:/app# python redis_init.py <arg>
```
The `arg` could be:
- `user`: Initialize the user information crawler queue, corresponding to `weibospider_weibo-spider-user`
- `fan`: Initialize the fans crawler queue, corresponding to `weibospider_weibo-spider-fan`
- `follow`: Initialize the follow crawler queue, corresponding to `weibospider_weibo-spider-follow`
- `comment`: Initialize the comment crawler queue, corresponding to `weibospider_weibo-spider-comment`
- `tweet_by_user_id`: Initialize the tweets based on users crawler queue, corresponding to `weibospider_weibo-spider-tweet`
- `tweet_by_keyword`: Initialize the tweets based on keywords and time crawler queue, corresponding to`weibospider_weibo-spider-tweet`

You can modify the `./weibospider/redis_init.py` according to your needs.

We take the arg to be `tweet_by_user_id` as example:
```bash
root@be3ac5910132:/app# python redis_init.py tweet_by_user_id
Add urls to tweet_spider:start_urls
Added: https://weibo.cn/1087770692/profile?page=1
Added: https://weibo.cn/1699432410/profile?page=1
Added: https://weibo.cn/1266321801/profile?page=1
```

### Run Spider
The spider will monitor whether the corresponding queue in the redis has urls, and 
when the queue has urls, the spider will auto run to crawl data.

<img src="./.github/images/spider.png" width = "80%" height = "80%" alt="spider" align=center />

We can see the real-time crawled data by mongo-express

<img src="./.github/images/data.png" width = "80%" height = "80%" alt="spider" align=center />


## Note for Speed
The final speed of the distributed crawler is related to the size of the account pool, 
the quality and quantity of the IP proxy, 
the bandwidth of the server, 
and the performance of the server (IO / memory / CPU).

The following is the settings and the corresponding speeds I tested for reference:

|Settings|Value|
|:---:|:---:|
|size of the account pool|1000+|
|size of the proxy IP pool|50+|
|[CONCURRENT_REQUESTS](./weibospider/settings.py#15)|16|
|[DOWNLOAD_DELAY](./weibospider/settings.py#18)|0.1s|
|[DOWNLOAD_TIMEOUT](./weibospider/settings.py#21)|3|
|numbers of spider containers|100|
|bandwidth of the server|30M|
|memory of the server|256GB|
|CPU of the server|E5-2650 v4 @ 2.20GHz * 48|

The result is that the number of crawled web pages per container and per minute is: **300+**, and the numbers of web pages crawled in one day is:

`300(pages/(container*min)) * 100(containers) * 60*24(mins/day) = 43,200,000(pages/day)` **43 million web pages**

If we crawl data of user information，`1(data/page)`, the amount of data crawled in one day is:

`43,200,000(pages/day) * 1(data/page) = 43,200,000(data/day)` **43 million**

If we crawl data of tweet/comment/relationship，`10(data/page)`, the amount of data crawled in one day is:
 
 `43,200,000(pages/day) * 10(data/page) = 432,000,000(data/day)` **4.3 billion**

## Last But Not The Least
Based on this project, I have crawled millions weibo active user data, and have built many weibo public opinion datasets: [weibo-public-opinion-datasets](https://github.com/nghuyong/weibo-public-opinion-datasets).

If you have any problems in using the project, you can open an issue to discuss.

If you have good ideas in social media computing / public opinion analysis, feel free to email me: nghuyong@163.com