"""
配置文件
"""

# 网站基础URL
BASE_URL = "https://www.iseehair.com"

# 请求头
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.iseehair.com/",
}

# 请求超时时间(秒)
TIMEOUT = 30

# 请求延迟时间(秒)
REQUEST_DELAY = 1

# 数据保存路径
DATA_DIR = "../data"
