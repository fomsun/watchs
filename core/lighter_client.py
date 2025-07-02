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
    
    def __init__(self, on_data_callback: Callable[[LighterData], None], headless: bool = False, refresh_interval: int = 300):
        """
        初始化Lighter客户端

        Args:
            on_data_callback: 数据回调函数
            headless: 是否使用无头模式
            refresh_interval: 页面刷新间隔（秒），默认5分钟
        """
        self.on_data_callback = on_data_callback
        self.headless = headless
        self.refresh_interval = refresh_interval  # 刷新间隔（秒）
        self.page = None
        self.data = LighterData()
        self.running = False
        self.scrape_thread = None
        self.refresh_thread = None
        self.last_refresh_time = 0
        self.url = None  # 保存当前URL
        self.connection_lost_count = 0  # 连接丢失计数
        self.max_reconnect_attempts = 3  # 最大重连尝试次数

        if not DRISSION_AVAILABLE:
            print("⚠️  DrissionPage未安装")
    
    def start(self, url: str = "https://app.lighter.xyz/trade/BTC?locale=zh"):
        """启动Lighter连接"""
        if not DRISSION_AVAILABLE:
            print("❌ DrissionPage不可用")
            return False

        # 保存URL用于刷新
        self.url = url
        
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

            # 🎭 伪装成macOS Chrome浏览器
            macos_user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            co.set_user_agent(macos_user_agent)
            print("🎭 伪装成macOS Chrome浏览器")

            # 设置macOS相关的首选项
            co.set_pref('profile.default_content_settings.popups', 0)  # 禁用弹窗
            co.set_pref('credentials_enable_service', False)  # 禁用密码保存提示
            co.set_pref('profile.default_content_setting_values.notifications', 2)  # 禁用通知

            # 设置窗口大小（模拟macOS常见分辨率）
            co.set_argument('--window-size=1440,900')

            # 设置语言
            co.set_argument('--lang=zh-CN,zh,en-US,en')

            # 禁用自动化检测
            co.set_argument('--disable-blink-features=AutomationControlled')
            co.set_argument('--disable-web-security')
            co.set_argument('--disable-features=VizDisplayCompositor')

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

            # 执行JavaScript进一步伪装
            print("🎭 执行JavaScript伪装...")
            try:
                # 伪装navigator属性
                self.page.run_js("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                self.page.run_js("Object.defineProperty(navigator, 'platform', {get: () => 'MacIntel'})")
                self.page.run_js("Object.defineProperty(navigator, 'userAgent', {get: () => 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'})")
                print("✅ JavaScript伪装完成")
            except Exception as e:
                print(f"⚠️  JavaScript伪装失败: {e}")

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

                # 启动页面刷新线程
                self.refresh_thread = threading.Thread(target=self._refresh_loop, daemon=True)
                self.refresh_thread.start()
                self.last_refresh_time = time.time()

                print("✅ Lighter连接成功")
                print(f"🔄 页面将每{self.refresh_interval//60}分钟自动刷新一次")
                return True
            else:
                print("❌ Lighter页面加载失败")
                return False
                
        except Exception as e:
            print(f"❌ Lighter连接失败: {e}")
            self.data.connected = False
            return False

    def _refresh_loop(self):
        """页面刷新循环"""
        while self.running:
            try:
                # 等待刷新间隔
                time.sleep(60)  # 每分钟检查一次

                if not self.running:
                    break

                # 检查是否需要刷新
                current_time = time.time()
                if current_time - self.last_refresh_time >= self.refresh_interval:
                    print(f"🔄 页面运行已超过{self.refresh_interval//60}分钟，开始刷新...")
                    self._refresh_page()
                    self.last_refresh_time = current_time

            except Exception as e:
                print(f"❌ 页面刷新循环错误: {e}")
                time.sleep(60)

    def _refresh_page(self):
        """刷新页面"""
        try:
            if self.page and self.url:
                print("🔄 正在刷新页面...")

                # 使用DrissionPage的refresh方法刷新页面
                self.page.refresh()

                # 等待页面重新加载
                time.sleep(BROWSER_WAIT_TIME)

                # 重新执行JavaScript伪装
                try:
                    self.page.run_js("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                    self.page.run_js("Object.defineProperty(navigator, 'platform', {get: () => 'MacIntel'})")
                    self.page.run_js("Object.defineProperty(navigator, 'userAgent', {get: () => 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'})")
                    print("✅ 页面刷新后JavaScript伪装完成")
                except Exception as e:
                    print(f"⚠️  页面刷新后JavaScript伪装失败: {e}")

                # 检查页面是否正常加载
                if self._check_page_loaded():
                    print("✅ 页面刷新成功，订单簿数据正常")
                else:
                    print("⚠️  页面刷新后加载检查失败，但继续运行")

        except Exception as e:
            print(f"❌ 页面刷新失败: {e}")
            # 如果刷新失败，尝试重新加载页面
            try:
                print("🔄 尝试重新加载页面...")
                self.page.get(self.url)
                time.sleep(BROWSER_WAIT_TIME)
                print("✅ 页面重新加载完成")
            except Exception as reload_error:
                print(f"❌ 页面重新加载也失败: {reload_error}")

    def _check_page_connection(self) -> bool:
        """检查页面连接状态"""
        try:
            if not self.page:
                return False

            # 尝试获取页面标题来检查连接
            title = self.page.title
            return title is not None and len(title) > 0

        except Exception as e:
            error_msg = str(e)
            if "disconnected" in error_msg.lower() or "connection" in error_msg.lower():
                return False
            return True  # 其他错误不一定是连接问题

    def _reconnect_page(self) -> bool:
        """重连页面"""
        try:
            if not self.url:
                print("❌ 没有保存的URL，无法重连")
                return False

            print(f"🔄 正在重连到: {self.url}")

            # 尝试关闭当前页面
            try:
                if self.page:
                    self.page.quit()
            except:
                pass

            # 重新创建页面
            return self._create_page_and_connect()

        except Exception as e:
            print(f"❌ 重连失败: {e}")
            return False

    def _create_page_and_connect(self) -> bool:
        """创建页面并连接"""
        try:
            # 重新配置浏览器选项
            co = ChromiumOptions()
            if self.headless:
                co.headless()

            # 设置Chrome路径
            chrome_path = get_chrome_path()
            if chrome_path:
                co.set_browser_path(chrome_path)

            # 🎭 伪装成macOS Chrome浏览器
            macos_user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            co.set_user_agent(macos_user_agent)

            # 设置macOS相关的首选项
            co.set_pref('profile.default_content_settings.popups', 0)
            co.set_pref('credentials_enable_service', False)
            co.set_pref('profile.default_content_setting_values.notifications', 2)

            # 设置窗口大小和语言
            co.set_argument('--window-size=1440,900')
            co.set_argument('--lang=zh-CN,zh,en-US,en')

            # 禁用自动化检测
            co.set_argument('--disable-blink-features=AutomationControlled')
            co.set_argument('--disable-web-security')
            co.set_argument('--disable-features=VizDisplayCompositor')

            # Linux系统特殊配置
            import platform
            if platform.system() == 'Linux':
                co.set_argument('--no-sandbox')
                co.set_argument('--disable-dev-shm-usage')
                co.set_argument('--disable-gpu')
                co.set_argument('--disable-extensions')

            # 其他优化配置
            co.no_imgs(True)
            co.mute(True)

            # 创建新页面
            self.page = ChromiumPage(co)

            # 执行JavaScript伪装
            try:
                self.page.run_js("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                self.page.run_js("Object.defineProperty(navigator, 'platform', {get: () => 'MacIntel'})")
                self.page.run_js("Object.defineProperty(navigator, 'userAgent', {get: () => 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'})")
            except Exception as e:
                print(f"⚠️  JavaScript伪装失败: {e}")

            # 访问页面
            self.page.get(self.url)

            # 等待页面加载
            time.sleep(BROWSER_WAIT_TIME)

            # 检查页面是否加载成功
            if self._check_page_loaded():
                print("✅ 页面重连并加载成功")
                return True
            else:
                print("❌ 页面重连后加载失败")
                return False

        except Exception as e:
            print(f"❌ 创建页面连接失败: {e}")
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
            # 检查订单簿容器是否存在
            asks_container = self.page.ele('@data-testid=orderbook-asks')
            bids_container = self.page.ele('@data-testid=orderbook-bids')
            return asks_container is not None and bids_container is not None
        except:
            return False
    
    def _scrape_loop(self):
        """数据抓取循环"""
        while self.running:
            try:
                # 检查页面连接状态
                if not self._check_page_connection():
                    print("🔌 检测到页面连接断开，尝试重连...")
                    if self._reconnect_page():
                        print("✅ 页面重连成功")
                        self.connection_lost_count = 0  # 重置计数
                    else:
                        print("❌ 页面重连失败，等待下次尝试")
                        time.sleep(10)
                        continue

                orderbook = parse_orderbook_from_page(self.page)
                if orderbook and orderbook.asks and orderbook.bids:
                    self.data.orderbook = orderbook
                    self.data.timestamp = datetime.now()
                    self.connection_lost_count = 0  # 重置连接丢失计数

                    print(f"Lighter数据更新: 买一=${orderbook.best_bid:.1f}, 卖一=${orderbook.best_ask:.1f}, 中间价=${orderbook.mid_price:.1f}")

                    # 调用回调函数
                    if self.on_data_callback:
                        self.on_data_callback(self.data)
                else:
                    print("订单簿数据为空或解析失败")
                    self.connection_lost_count += 1

                    # 如果连续多次解析失败，可能是连接问题
                    if self.connection_lost_count >= 3:
                        print("🔌 连续解析失败，可能是连接问题，尝试重连...")
                        self._reconnect_page()

                time.sleep(SCRAPE_INTERVAL)  # 按配置间隔更新

            except Exception as e:
                error_msg = str(e)
                print(f"Lighter数据抓取错误: {error_msg}")

                # 检查是否是连接断开错误
                if "disconnected" in error_msg.lower() or "connection" in error_msg.lower():
                    print("🔌 检测到连接断开错误，尝试重连...")
                    if self._reconnect_page():
                        print("✅ 重连成功，继续数据抓取")
                        continue
                    else:
                        print("❌ 重连失败")

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