#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Lighter Selenium客户端 - Ubuntu兼容版
使用Selenium替代DrissionPage，兼容性更强
"""

import time
import threading
import platform
from datetime import datetime
from typing import Callable, Optional

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

from data.models import LighterData, OrderBook, OrderBookLevel, OrderType
from config import get_chrome_path

class LighterSeleniumClient:
    """Lighter Selenium客户端 - Ubuntu兼容版"""

    def __init__(self, on_data_callback: Callable[[LighterData], None], headless: bool = True):
        self.on_data_callback = on_data_callback
        self.headless = headless
        self.driver = None
        self.data = LighterData()
        self.running = False
        self.scrape_thread = None

        if not SELENIUM_AVAILABLE:
            print("⚠️  Selenium未安装，请运行: pip3 install selenium")
    
    def start(self, url: str = "https://app.lighter.xyz/trade/BTC?locale=zh"):
        """启动Lighter连接"""
        if not SELENIUM_AVAILABLE:
            print("❌ Selenium不可用")
            return False
        
        try:
            print("🔷 启动Selenium Lighter客户端...")

            # 配置Chrome选项
            chrome_options = Options()
            
            # 无头模式
            if self.headless:
                chrome_options.add_argument('--headless')
                print("🔇 使用无头模式")
            
            # Ubuntu必需参数
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--disable-features=VizDisplayCompositor')
            chrome_options.add_argument('--disable-background-timer-throttling')
            chrome_options.add_argument('--disable-backgrounding-occluded-windows')
            chrome_options.add_argument('--disable-renderer-backgrounding')
            
            # 内存和性能优化
            chrome_options.add_argument('--memory-pressure-off')
            chrome_options.add_argument('--max_old_space_size=4096')
            chrome_options.add_argument('--aggressive-cache-discard')
            chrome_options.add_argument('--disable-background-networking')
            
            # 禁用图片和CSS（提高速度）
            prefs = {
                "profile.managed_default_content_settings.images": 2,
                "profile.default_content_setting_values.notifications": 2,
                "profile.managed_default_content_settings.stylesheets": 2,
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            # 设置Chrome路径
            chrome_path = get_chrome_path()
            if chrome_path:
                chrome_options.binary_location = chrome_path
                print(f"🌐 使用Chrome路径: {chrome_path}")
            
            # 创建WebDriver
            service = Service()  # 使用系统PATH中的chromedriver
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # 设置超时
            self.driver.set_page_load_timeout(30)
            self.driver.implicitly_wait(10)
            
            print(f"🔗 访问页面: {url}")
            self.driver.get(url)
            
            # 等待页面加载
            print("⏳ 等待页面加载...")
            time.sleep(15)
            
            # 检查页面是否加载成功
            if self._check_page_loaded():
                self.data.connected = True
                self.running = True
                
                # 启动数据抓取线程
                self.scrape_thread = threading.Thread(target=self._scrape_loop, daemon=True)
                self.scrape_thread.start()
                
                print("✅ Selenium Lighter连接成功")
                return True
            else:
                print("❌ Selenium Lighter页面加载失败")
                self._debug_page_info()
                return False
                
        except Exception as e:
            print(f"❌ Selenium Lighter连接失败: {e}")
            import traceback
            print(f"详细错误: {traceback.format_exc()}")
            self.data.connected = False
            return False
    
    def _check_page_loaded(self) -> bool:
        """检查页面是否加载完成"""
        try:
            # 等待订单簿容器出现
            wait = WebDriverWait(self.driver, 20)
            
            # 检查订单簿容器
            asks_container = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="orderbook-asks"]'))
            )
            bids_container = self.driver.find_element(By.CSS_SELECTOR, '[data-testid="orderbook-bids"]')
            
            if asks_container and bids_container:
                print("✅ 订单簿容器找到")
                return True
            else:
                print("❌ 订单簿容器未找到")
                return False
                
        except TimeoutException:
            print("❌ 页面加载超时")
            return False
        except Exception as e:
            print(f"❌ 页面检查失败: {e}")
            return False
    
    def _debug_page_info(self):
        """调试页面信息"""
        try:
            print("🔍 Selenium调试信息:")
            print(f"   页面标题: {self.driver.title}")
            print(f"   页面URL: {self.driver.current_url}")
            
            # 保存页面源码
            with open('/tmp/lighter_selenium_debug.html', 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            print(f"   页面源码已保存到: /tmp/lighter_selenium_debug.html")
            
        except Exception as e:
            print(f"   调试信息获取失败: {e}")
    
    def _scrape_loop(self):
        """数据抓取循环"""
        while self.running:
            try:
                orderbook = self._parse_orderbook()
                if orderbook and orderbook.asks and orderbook.bids:
                    self.data.orderbook = orderbook
                    self.data.timestamp = datetime.now()

                    print(f"Selenium Lighter数据更新: 买一=${orderbook.best_bid:.1f}, 卖一=${orderbook.best_ask:.1f}, 中间价=${orderbook.mid_price:.1f}")

                    # 调用回调函数
                    if self.on_data_callback:
                        self.on_data_callback(self.data)
                else:
                    print("Selenium: 订单簿数据为空或解析失败")

                time.sleep(3)  # 3秒间隔

            except Exception as e:
                print(f"Selenium Lighter数据抓取错误: {e}")
                time.sleep(10)  # 出错时等待更长时间
    
    def _parse_orderbook(self) -> Optional[OrderBook]:
        """解析订单簿数据"""
        try:
            asks = []
            bids = []
            
            # 查找卖单元素
            ask_elements = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid^="ob-ask-"]')
            print(f"找到 {len(ask_elements)} 个卖单元素")
            
            for ask_elem in ask_elements:
                level = self._parse_order_level(ask_elem, OrderType.ASK)
                if level:
                    asks.append(level)
            
            # 查找买单元素
            bid_elements = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid^="ob-bid-"]')
            print(f"找到 {len(bid_elements)} 个买单元素")
            
            for bid_elem in bid_elements:
                level = self._parse_order_level(bid_elem, OrderType.BID)
                if level:
                    bids.append(level)
            
            if asks and bids:
                return OrderBook(asks=asks, bids=bids)
            else:
                return None
                
        except Exception as e:
            print(f"订单簿解析错误: {e}")
            return None
    
    def _parse_order_level(self, element, order_type: OrderType) -> Optional[OrderBookLevel]:
        """解析单个订单档位"""
        try:
            # 查找价格、数量、总量元素
            price_elem = element.find_element(By.CSS_SELECTOR, '[data-testid="price"]')
            size_elem = element.find_element(By.CSS_SELECTOR, '[data-testid="size"]')
            total_elem = element.find_element(By.CSS_SELECTOR, '[data-testid="total-size"]')
            
            if not (price_elem and size_elem and total_elem):
                return None
            
            # 获取文本并转换为数字
            price_text = price_elem.text.replace(',', '').strip()
            size_text = size_elem.text.replace(',', '').strip()
            total_text = total_elem.text.replace(',', '').strip()
            
            price = float(price_text)
            size = float(size_text)
            total_size = float(total_text)
            
            return OrderBookLevel(
                price=price,
                size=size,
                total_size=total_size,
                order_type=order_type
            )
            
        except Exception:
            return None
    
    def stop(self):
        """停止Lighter连接"""
        self.running = False
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
        self.data.connected = False
        print("✅ Selenium Lighter客户端已停止")
    
    def get_current_data(self) -> LighterData:
        """获取当前数据"""
        return self.data
    
    def is_connected(self) -> bool:
        """检查连接状态"""
        return self.data.connected and self.running
