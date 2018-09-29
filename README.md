# WeiboSpider

![Screen Shot](https://ws4.sinaimg.cn/large/006tNc79ly1fvp0xwknxvj31gx0q7duh.jpg)

This is a sina weibo spider built by [nghuyong][] largely tailored to run on [WWBP](http://wwbp.org)'s servers by [Mingyang Li](http://seas.upenn.edu/~myli).

[nghuyong]: https://github.com/nghuyong

A detailed explanation, written by [nghuyong][], can be found at [微博爬虫总结：构建单机千万级别的微博爬虫系统](http://www.nghuyong.top/2018/09/12/spider/%E5%BE%AE%E5%8D%9A%E7%88%AC%E8%99%AB%E6%80%BB%E7%BB%93%EF%BC%9A%E6%9E%84%E5%BB%BA%E5%8D%95%E6%9C%BA%E5%8D%83%E4%B8%87%E7%BA%A7%E5%88%AB%E7%9A%84%E5%BE%AE%E5%8D%9A%E7%88%AC%E8%99%AB%E7%B3%BB%E7%BB%9F/).

Description of data structure can be found at [数据字段说明与示例](./data_stracture.md).

## Other Branches
The original repo by [nghuyong][] has 3 branches:

|    Branch   | Structure | Posts per Day |
| :---: | :----: |:----: |
| [simple](https://github.com/nghuyong/WeiboSpider/tree/simple) | single account | 100,000 |
| [master](https://github.com/nghuyong/WeiboSpider/tree/master) | account pool | 1,000,000 |
| [senior](https://github.com/nghuyong/WeiboSpider/tree/senior) | distributed pool | 10,000,000 | 

## Usage

1. Clone thre repo. Install dependencies.
   ```bash
   git clone git@github.com:nghuyong/WeiboSpider.git
   cd WeiboSpider
   pip install -r requirements.txt
   ```
2. Install `phantomjs`, `mongodb`, and `redis`. Start the latter two.
3. Write down the usernames and passwords of some Sina Weibo accounts in `sina/account_build/account.txt`. Follow the format indicated in `account_sample.txt`.
4. Populate the account pool by running `python sina/account_build/login.py`.
5. Populate URLs to start scraping with by issuing `python sina/redis_init.py`.
5. Run scraper by running `scrapy crawl weibo_spider`.

## Data Storage

Posts, user profiles, and user relationships (and comments optionally) are stored in the MongoDB.

## Performance

![](https://ws2.sinaimg.cn/large/006tNc79ly1fvqx0yrnd3j31am0qojz8.jpg)

With the default setting, 16GB memory, 8-core CPU, Ubuntu, and 36 processes, we are hitting an average of 2,000 posts per second.
