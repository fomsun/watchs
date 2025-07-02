#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Lighter客户端管理器
自动选择最适合的客户端实现（DrissionPage或Selenium）
"""

import platform
from typing import Callable, Optional
from data.models import LighterData

# 尝试导入不同的客户端实现
try:
    from core.lighter_client import LighterClient
    DRISSION_AVAILABLE = True
except ImportError:
    DRISSION_AVAILABLE = False

try:
    from core.lighter_selenium_client import LighterSeleniumClient
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

class LighterManager:
    """Lighter客户端管理器"""
    
    def __init__(self, on_data_callback: Callable[[LighterData], None], headless: bool = True, refresh_interval: int = 300):
        self.on_data_callback = on_data_callback
        self.headless = headless
        self.refresh_interval = refresh_interval
        self.client = None
        self.client_type = None

        # 选择最适合的客户端
        self.client = self._select_best_client()
    
    def _select_best_client(self):
        """选择最适合的客户端实现"""
        system = platform.system()

        print("🔍 选择Lighter客户端实现...")

        # 所有系统都优先使用DrissionPage（伪装问题已解决）
        if DRISSION_AVAILABLE:
            print(f"🎭 {system}系统，优先使用DrissionPage客户端（已解决伪装问题）")
            self.client_type = "DrissionPage"
            return LighterClient(self.on_data_callback, self.headless, self.refresh_interval)
        elif SELENIUM_AVAILABLE:
            print(f"⚠️  DrissionPage不可用，使用Selenium客户端作为备选")
            self.client_type = "Selenium"
            return LighterSeleniumClient(self.on_data_callback, self.headless)
        else:
            print("❌ 没有可用的Lighter客户端实现")
            return None
    
    def start(self, url: str = "https://app.lighter.xyz/trade/BTC?locale=zh"):
        """启动Lighter连接"""
        if not self.client:
            print("❌ 没有可用的Lighter客户端")
            return False
        
        print(f"🚀 启动{self.client_type}客户端...")
        return self.client.start(url)
    
    def stop(self):
        """停止Lighter连接"""
        if self.client:
            self.client.stop()
    
    def get_current_data(self) -> LighterData:
        """获取当前数据"""
        if self.client:
            return self.client.get_current_data()
        return LighterData()
    
    def is_connected(self) -> bool:
        """检查连接状态"""
        if self.client:
            return self.client.is_connected()
        return False
    
    def get_client_type(self) -> str:
        """获取当前使用的客户端类型"""
        return self.client_type or "None"

def create_lighter_client(on_data_callback: Callable[[LighterData], None],
                         headless: bool = True,
                         force_type: Optional[str] = None,
                         refresh_interval: int = 300) -> LighterManager:
    """
    创建Lighter客户端

    Args:
        on_data_callback: 数据回调函数
        headless: 是否使用无头模式
        force_type: 强制使用特定类型 ("selenium" 或 "drissionpage")
        refresh_interval: 页面刷新间隔（秒），默认5分钟

    Returns:
        LighterManager: 客户端管理器
    """
    if force_type:
        force_type = force_type.lower()
        
        if force_type == "selenium" and SELENIUM_AVAILABLE:
            print("🔧 强制使用Selenium客户端")
            manager = LighterManager(on_data_callback, headless, refresh_interval)
            manager.client = LighterSeleniumClient(on_data_callback, headless)
            manager.client_type = "Selenium"
            return manager

        elif force_type == "drissionpage" and DRISSION_AVAILABLE:
            print("🔧 强制使用DrissionPage客户端")
            manager = LighterManager(on_data_callback, headless, refresh_interval)
            manager.client = LighterClient(on_data_callback, headless, refresh_interval)
            manager.client_type = "DrissionPage"
            return manager
        
        else:
            print(f"⚠️  强制类型 '{force_type}' 不可用，使用自动选择")
    
    return LighterManager(on_data_callback, headless, refresh_interval)
