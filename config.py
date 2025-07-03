#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
配置文件 - BTC价格监控系统
"""

import os
import platform

# Chrome浏览器路径配置
CHROME_PATHS = {
    'Linux': [
        '/usr/bin/google-chrome',           # 标准安装路径
        '/usr/bin/google-chrome-stable',    # 稳定版
        '/usr/bin/chromium-browser',        # Chromium浏览器
        '/usr/bin/chromium',                # Chromium简化路径
        '/snap/bin/chromium',               # Snap包安装
        '/opt/google/chrome/chrome',        # 可选安装路径
        '/usr/local/bin/google-chrome',     # 本地安装
    ],
    'Darwin': [  # macOS
        '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        '/Applications/Chromium.app/Contents/MacOS/Chromium',
    ],
    'Windows': [
        r'C:\Program Files\Google\Chrome\Application\chrome.exe',
        r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
        r'C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe'.format(os.getenv('USERNAME', '')),
    ]
}

# API服务器配置
API_HOST = '0.0.0.0'
API_PORT = 8080

# 价格记录配置
PRICE_RECORD_FILE = 'btc_price_data.txt'
PRICE_RECORD_INTERVAL = 10  # 秒

# WebSocket配置
BINANCE_WS_URL = 'wss://fstream.binance.com/ws/btcusdc@ticker'
BACKPACK_WS_URL = 'wss://ws.backpack.exchange'

# Lighter配置
LIGHTER_URL = 'https://app.lighter.xyz/trade/BTC?locale=zh'
LIGHTER_HEADLESS = True  # 默认使用无头模式

# 浏览器配置
BROWSER_WAIT_TIME = 10  # 页面加载等待时间（秒）
SCRAPE_INTERVAL = 1     # 数据抓取间隔（秒）

def get_chrome_path():
    """
    自动检测Chrome浏览器路径
    
    Returns:
        str: Chrome浏览器路径，如果未找到返回None
    """
    system = platform.system()
    paths = CHROME_PATHS.get(system, [])
    
    for path in paths:
        if os.path.exists(path):
            return path
    
    return None

def validate_config():
    """
    验证配置是否有效
    
    Returns:
        tuple: (is_valid, error_message)
    """
    # 检查Chrome路径
    chrome_path = get_chrome_path()
    if not chrome_path:
        return False, f"未找到Chrome浏览器，请安装Google Chrome或Chromium"
    
    # 检查端口是否可用
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((API_HOST, API_PORT))
    except OSError:
        return False, f"端口 {API_PORT} 已被占用，请修改 API_PORT 配置"
    
    return True, "配置验证通过"

# 调试模式
DEBUG = False

# 页面刷新间隔（秒），默认5分钟
PAGE_REFRESH_INTERVAL = 300

# 数据库保存间隔（秒），默认1分钟
DATABASE_SAVE_INTERVAL = 60

# 连接重试配置
MAX_RECONNECT_ATTEMPTS = 3  # 最大重连尝试次数
RECONNECT_DELAY = 10  # 重连延迟（秒）
CONNECTION_CHECK_INTERVAL = 30  # 连接检查间隔（秒）

if __name__ == "__main__":
    print("=== BTC价格监控系统配置 ===")
    print(f"操作系统: {platform.system()}")
    print(f"Chrome路径: {get_chrome_path()}")
    print(f"API服务器: http://{API_HOST}:{API_PORT}")
    print(f"价格记录文件: {PRICE_RECORD_FILE}")
    print(f"记录间隔: {PRICE_RECORD_INTERVAL}秒")
    
    is_valid, message = validate_config()
    if is_valid:
        print(f"✅ {message}")
    else:
        print(f"❌ {message}")
