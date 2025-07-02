#!/usr/bin/env python3
"""
Lighter数据客户端
"""

import time
import threading
from datetime import datetime
from typing import Callable, Optional

try:
    from DrissionPage import ChromiumPage, ChromiumOptions
    DRISSION_AVAILABLE = True
except ImportError:
    DRISSION_AVAILABLE = False

from data.models import LighterData, OrderBook
from core.orderbook_utils import parse_orderbook_from_page
from config import get_chrome_path, BROWSER_WAIT_TIME, SCRAPE_INTERVAL

class LighterClient:
    """Lighter数据客户端"""
    
    def __init__(self, on_data_callback: Callable[[LighterData], None], headless: bool = False):
        """
        初始化Lighter客户端

        Args:
            on_data_callback: 数据回调函数
            headless: 是否使用无头模式
        """
        self.on_data_callback = on_data_callback
        self.headless = headless
        self.page = None
        self.data = LighterData()
        self.running = False
        self.scrape_thread = None

        if not DRISSION_AVAILABLE:
            print("⚠️  DrissionPage未安装")
    
    def start(self, url: str = "https://app.lighter.xyz/trade/BTC?locale=zh"):
        """启动Lighter连接"""
        if not DRISSION_AVAILABLE:
            print("❌ DrissionPage不可用")
            return False
        
        try:
            print("🔷 启动Lighter浏览器...")

            # 配置浏览器选项
            co = ChromiumOptions()
            if self.headless:
                co.headless()  # 启用无头模式
                print("🔇 使用无头模式")
            else:
                print("🖥️  使用有界面模式")

            # 跨平台Chrome路径配置
            import platform

            # 自动检测Chrome路径
            chrome_path = get_chrome_path()
            if chrome_path:
                co.set_browser_path(chrome_path)
                print(f"🌐 使用Chrome路径: {chrome_path}")
            else:
                print("⚠️  未找到Chrome浏览器，请确保已安装Google Chrome")

            # Linux系统特殊配置
            if platform.system() == 'Linux':
                co.set_argument('--no-sandbox')  # Linux系统必需
                co.set_argument('--disable-dev-shm-usage')  # 避免共享内存问题
                co.set_argument('--disable-gpu')  # 禁用GPU加速
                co.set_argument('--disable-extensions')  # 禁用扩展
                print("🐧 已添加Linux兼容性参数")

            # 其他优化配置
            co.no_imgs(True)  # 不加载图片，提高速度
            co.mute(True)     # 静音

            self.page = ChromiumPage(co)
            self.page.get(url)
            
            # 等待页面加载
            print("⏳ 等待页面加载...")
            time.sleep(BROWSER_WAIT_TIME)
            
            # 检查页面是否加载成功
            if self._check_page_loaded():
                self.data.connected = True
                self.running = True
                
                # 启动数据抓取线程
                self.scrape_thread = threading.Thread(target=self._scrape_loop, daemon=True)
                self.scrape_thread.start()
                
                print("✅ Lighter连接成功")
                return True
            else:
                print("❌ Lighter页面加载失败")
                return False
                
        except Exception as e:
            print(f"❌ Lighter连接失败: {e}")
            self.data.connected = False
            return False
    
    def stop(self):
        """停止Lighter连接"""
        self.running = False
        if self.page:
            try:
                self.page.quit()
                print("✅ Lighter浏览器已关闭")
            except:
                pass
        self.data.connected = False
    
    def _check_page_loaded(self) -> bool:
        """检查页面是否加载完成"""
        try:
            # 获取页面基本信息
            title = self.page.title
            url = self.page.url

            print(f"🔍 页面调试信息:")
            print(f"   标题: {title}")
            print(f"   URL: {url}")

            # 获取页面HTML信息
            try:
                html_content = self.page.html
                print(f"   HTML长度: {len(html_content)} 字符")

                # 检查是否包含关键词
                keywords = ["Lighter", "BTC", "Bitcoin", "Trade", "Order", "Price", "orderbook"]
                found_keywords = [kw for kw in keywords if kw.lower() in html_content.lower()]
                print(f"   找到关键词: {found_keywords}")

                # 显示HTML片段（前1000字符）
                print(f"   HTML开头: {html_content[:1000]}...")

            except Exception as e:
                print(f"   获取HTML失败: {e}")

            # 检查订单簿容器是否存在
            print(f"🔍 查找订单簿元素:")

            # 尝试多种选择器
            selectors_to_try = [
                '@data-testid=orderbook-asks',
                '@data-testid=orderbook-bids',
                '.orderbook',
                '[data-testid*="orderbook"]',
                '.asks',
                '.bids',
                'table',
                '.price',
                '.order'
            ]

            found_elements = {}
            for selector in selectors_to_try:
                try:
                    element = self.page.ele(selector)
                    found_elements[selector] = element is not None
                    if element:
                        print(f"   ✅ 找到元素: {selector}")
                    else:
                        print(f"   ❌ 未找到: {selector}")
                except Exception as e:
                    print(f"   ❌ 查找 {selector} 出错: {e}")

            # 检查特定的订单簿容器
            asks_container = self.page.ele('@data-testid=orderbook-asks')
            bids_container = self.page.ele('@data-testid=orderbook-bids')

            if asks_container and bids_container:
                print("✅ 订单簿容器验证通过")
                return True
            else:
                print(f"❌ 订单簿容器验证失败")
                print(f"   asks_container: {asks_container is not None}")
                print(f"   bids_container: {bids_container is not None}")
                return False

        except Exception as e:
            print(f"❌ 检查页面加载失败: {e}")
            import traceback
            print(f"   错误详情: {traceback.format_exc()}")
            return False
    
    def _scrape_loop(self):
        """数据抓取循环"""
        while self.running:
            try:
                orderbook = parse_orderbook_from_page(self.page)
                if orderbook and orderbook.asks and orderbook.bids:
                    self.data.orderbook = orderbook
                    self.data.timestamp = datetime.now()

                    print(f"Lighter数据更新: 买一=${orderbook.best_bid:.1f}, 卖一=${orderbook.best_ask:.1f}, 中间价=${orderbook.mid_price:.1f}")

                    # 调用回调函数
                    if self.on_data_callback:
                        self.on_data_callback(self.data)
                else:
                    print("订单簿数据为空或解析失败")

                time.sleep(SCRAPE_INTERVAL)  # 按配置间隔更新

            except Exception as e:
                print(f"Lighter数据抓取错误: {e}")
                time.sleep(5)  # 出错时等待5秒再重试
    
    def get_current_data(self) -> LighterData:
        """获取当前数据"""
        return self.data
    
    def is_connected(self) -> bool:
        """检查连接状态"""
        return self.data.connected and self.running
    
    def get_orderbook_summary(self) -> str:
        """获取订单簿摘要"""
        if not self.data.orderbook:
            return "订单簿数据不可用"
        
        ob = self.data.orderbook
        summary_parts = []
        
        if ob.best_bid and ob.best_ask:
            summary_parts.append(f"买一: ${ob.best_bid:,.1f}")
            summary_parts.append(f"卖一: ${ob.best_ask:,.1f}")
            summary_parts.append(f"中间价: ${ob.mid_price:,.1f}")
            
            if ob.spread:
                summary_parts.append(f"点差: ${ob.spread:.1f}")
                
            if ob.spread_percent:
                summary_parts.append(f"({ob.spread_percent:.3f}%)")
        
        return " | ".join(summary_parts) if summary_parts else "数据解析中..."

# 测试函数
def test_lighter_client():
    """测试Lighter客户端"""
    def on_data(data: LighterData):
        if data.orderbook:
            ob = data.orderbook
            print(f"Lighter - 买一: ${ob.best_bid:,.1f}, 卖一: ${ob.best_ask:,.1f}, "
                  f"中间价: ${ob.mid_price:,.1f}, 点差: ${ob.spread:.1f}")
    
    client = LighterClient(on_data)
    
    try:
        if client.start():
            print("按 Ctrl+C 停止...")
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        print("\n停止测试...")
    finally:
        client.stop()

if __name__ == "__main__":
    test_lighter_client()