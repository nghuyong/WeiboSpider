# -*- coding: utf-8 -*-
import os

BOT_NAME = 'spider'

SPIDER_MODULES = ['spiders']
NEWSPIDER_MODULE = 'spiders'

# 核心：不遵守robots协议（爬微博必须开）
ROBOTSTXT_OBEY = False

# ========== 1. 修复Cookie读取（保留，但不再用这里的Cookie） ==========
SETTINGS_PATH = os.path.abspath(__file__)
WEIBOSPIDER_DIR = os.path.dirname(SETTINGS_PATH)
COOKIE_PATH = os.path.join(WEIBOSPIDER_DIR, 'cookie.txt')

try:
    with open(COOKIE_PATH, 'rt', encoding='utf-8') as f:
        cookie = f.read().strip()
except FileNotFoundError:
    print(f"警告：未找到 cookie.txt 文件，路径：{COOKIE_PATH}")
    cookie = ""

# ========== 2. 修复请求头（替换成Windows真实UA，核心反爬修复） ==========
DEFAULT_REQUEST_HEADERS = {
    # 替换成你浏览器的真实UA（F12复制），以下是示例
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0',
    'Cookie': cookie,
    'Referer': 'https://weibo.com/',
    'X-Requested-With': 'XMLHttpRequest',
    # 新增：补齐浏览器关键请求头，模拟真人
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Connection': 'keep-alive',
    'Host': 'weibo.com',
}

# ========== 3. 反爬核心配置（降低频率，禁用重定向） ==========
# 并发数：1个（模拟真人单次操作）
CONCURRENT_REQUESTS = 1
# 延时：5秒（避免请求过快）
DOWNLOAD_DELAY = 5
# 超时时间：15秒（避免网络波动导致失败）
DOWNLOAD_TIMEOUT = 15
# 全局禁用重定向（关键：阻止跳转到登录页）
REDIRECT_ENABLED = False

# ========== 4. 禁用不必要的中间件 ==========
DOWNLOADER_MIDDLEWARES = {
    # 禁用默认的重定向中间件（双重保障）
    'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': None,
    # 禁用CookiesMiddleware，避免冲突
    'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': None,
    # 添加微博爬虫中间件，设置请求头（提高优先级）
    'weibospider.middlewares.WeiboSpiderMiddleware': 700,
}

# ========== 5. 数据输出配置（修复"Unknown feed storage scheme: e"错误） ==========
ITEM_PIPELINES = {
    'weibospider.pipelines.JsonWriterPipeline': 300,
}

# 定义output目录（用相对路径，避免Windows路径问题）
OUTPUT_DIR = os.path.join(WEIBOSPIDER_DIR, 'output')
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# 废弃旧的FEED_URI/FEED_FORMAT，改用新的FEEDS配置（Scrapy推荐）
FEED_EXPORT_ENCODING = 'utf-8'
FEED_EXPORT_INDENT = 2
# 核心修复：用file://协议指定路径，避免scheme错误
FEEDS = {
    os.path.join(OUTPUT_DIR, '%(name)s_%(time)s.jsonl'): {
        'format': 'jsonlines',
        'encoding': 'utf-8',
        'indent': 2,
        'overwrite': False,  # 不覆盖已有文件
    }
}
# 注释掉旧的错误配置
# FEED_FORMAT = 'jsonlines'
# FEED_URI = os.path.join(OUTPUT_DIR, '%(name)s_%(time)s.jsonl')

# ========== 6. 额外优化：禁用Telnet，减少日志干扰 ==========
TELNETCONSOLE_ENABLED = False