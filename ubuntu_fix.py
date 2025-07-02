#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ubuntu系统Lighter客户端修复脚本
专门解决Ubuntu系统上的Chrome和DrissionPage问题
"""

import os
import sys
import subprocess
import platform
import time
from pathlib import Path

def check_system():
    """检查系统信息"""
    print("=== 系统信息检查 ===")
    print(f"操作系统: {platform.system()}")
    print(f"系统版本: {platform.release()}")
    print(f"架构: {platform.machine()}")
    print(f"Python版本: {sys.version}")
    
    # 检查是否为Ubuntu
    if platform.system() != 'Linux':
        print("⚠️  此脚本专为Ubuntu/Linux系统设计")
        return False
    
    return True

def check_chrome_installation():
    """检查Chrome安装情况"""
    print("\n=== Chrome安装检查 ===")
    
    chrome_paths = [
        '/usr/bin/google-chrome',
        '/usr/bin/google-chrome-stable',
        '/usr/bin/chromium-browser',
        '/usr/bin/chromium',
        '/snap/bin/chromium',
        '/opt/google/chrome/chrome',
        '/usr/local/bin/google-chrome'
    ]
    
    found_chrome = None
    for path in chrome_paths:
        if os.path.exists(path):
            print(f"✅ 找到Chrome: {path}")
            try:
                # 测试Chrome版本
                result = subprocess.run([path, '--version'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    print(f"   版本: {result.stdout.strip()}")
                    found_chrome = path
                    break
                else:
                    print(f"   ❌ 无法获取版本信息")
            except Exception as e:
                print(f"   ❌ 测试失败: {e}")
        else:
            print(f"❌ 未找到: {path}")
    
    if not found_chrome:
        print("\n❌ 未找到可用的Chrome浏览器")
        print("请运行以下命令安装Chrome:")
        print("sudo apt update")
        print("wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -")
        print("echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' | sudo tee /etc/apt/sources.list.d/google-chrome.list")
        print("sudo apt update")
        print("sudo apt install -y google-chrome-stable")
        return None
    
    return found_chrome

def check_display_environment():
    """检查显示环境"""
    print("\n=== 显示环境检查 ===")
    
    display = os.environ.get('DISPLAY')
    print(f"DISPLAY环境变量: {display}")
    
    if not display:
        print("⚠️  未设置DISPLAY环境变量")
        print("对于无头服务器，这是正常的，将使用无头模式")
        return False
    
    # 检查X11转发
    try:
        result = subprocess.run(['xdpyinfo'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ X11显示正常")
            return True
        else:
            print("❌ X11显示不可用")
            return False
    except FileNotFoundError:
        print("⚠️  xdpyinfo未安装，无法检查X11")
        return False
    except Exception as e:
        print(f"❌ X11检查失败: {e}")
        return False

def check_dependencies():
    """检查Python依赖"""
    print("\n=== Python依赖检查 ===")
    
    required_packages = [
        'DrissionPage',
        'flask',
        'websocket-client',
        'requests'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.lower().replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n缺少依赖包: {', '.join(missing_packages)}")
        print("请运行: pip3 install " + " ".join(missing_packages))
        return False
    
    return True

def test_chrome_headless(chrome_path):
    """测试Chrome无头模式"""
    print(f"\n=== 测试Chrome无头模式 ===")
    
    try:
        # 测试Chrome无头模式启动
        cmd = [
            chrome_path,
            '--headless',
            '--no-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--disable-extensions',
            '--remote-debugging-port=9222',
            '--dump-dom',
            'https://www.google.com'
        ]
        
        print("测试命令:", ' '.join(cmd))
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and 'google' in result.stdout.lower():
            print("✅ Chrome无头模式测试成功")
            return True
        else:
            print("❌ Chrome无头模式测试失败")
            print(f"返回码: {result.returncode}")
            print(f"错误输出: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Chrome启动超时")
        return False
    except Exception as e:
        print(f"❌ Chrome测试失败: {e}")
        return False

def create_ubuntu_lighter_client():
    """创建Ubuntu优化版的Lighter客户端"""
    print("\n=== 创建Ubuntu优化版Lighter客户端 ===")
    
    ubuntu_client_code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ubuntu优化版Lighter客户端
"""

import time
import threading
import platform
from datetime import datetime
from typing import Callable, Optional

try:
    from DrissionPage import ChromiumPage, ChromiumOptions
    DRISSION_AVAILABLE = True
except ImportError:
    DRISSION_AVAILABLE = False

from data.models import LighterData, OrderBook
from core.orderbook_utils import parse_orderbook_from_page
from config import get_chrome_path

class UbuntuLighterClient:
    """Ubuntu优化版Lighter数据客户端"""
    
    def __init__(self, on_data_callback: Callable[[LighterData], None], headless: bool = True):
        self.on_data_callback = on_data_callback
        self.headless = headless  # Ubuntu默认使用无头模式
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
            print("🔷 启动Ubuntu优化版Lighter浏览器...")

            # Ubuntu优化配置
            co = ChromiumOptions()
            
            # 强制无头模式（Ubuntu服务器环境）
            co.headless()
            print("🔇 使用无头模式（Ubuntu优化）")
            
            # 设置Chrome路径
            chrome_path = get_chrome_path()
            if chrome_path:
                co.set_browser_path(chrome_path)
                print(f"🌐 使用Chrome路径: {chrome_path}")
            
            # Ubuntu必需参数
            co.set_argument('--no-sandbox')
            co.set_argument('--disable-dev-shm-usage')
            co.set_argument('--disable-gpu')
            co.set_argument('--disable-extensions')
            co.set_argument('--disable-web-security')
            co.set_argument('--disable-features=VizDisplayCompositor')
            co.set_argument('--disable-background-timer-throttling')
            co.set_argument('--disable-backgrounding-occluded-windows')
            co.set_argument('--disable-renderer-backgrounding')
            co.set_argument('--disable-field-trial-config')
            co.set_argument('--disable-ipc-flooding-protection')
            
            # 内存优化
            co.set_argument('--memory-pressure-off')
            co.set_argument('--max_old_space_size=4096')
            
            # 网络优化
            co.set_argument('--aggressive-cache-discard')
            co.set_argument('--disable-background-networking')
            
            # 其他优化
            co.no_imgs(True)  # 不加载图片
            co.mute(True)     # 静音
            
            print("✅ Ubuntu优化参数已设置")

            self.page = ChromiumPage(co)
            print(f"🔗 访问页面: {url}")
            self.page.get(url)
            
            # 增加等待时间（Ubuntu可能较慢）
            print("⏳ 等待页面加载（Ubuntu优化等待时间）...")
            time.sleep(15)
            
            # 检查页面是否加载成功
            if self._check_page_loaded():
                self.data.connected = True
                self.running = True
                
                # 启动数据抓取线程
                self.scrape_thread = threading.Thread(target=self._scrape_loop, daemon=True)
                self.scrape_thread.start()
                
                print("✅ Ubuntu Lighter连接成功")
                return True
            else:
                print("❌ Ubuntu Lighter页面加载失败")
                self._debug_page_info()
                return False
                
        except Exception as e:
            print(f"❌ Ubuntu Lighter连接失败: {e}")
            import traceback
            print(f"详细错误: {traceback.format_exc()}")
            self.data.connected = False
            return False
    
    def _debug_page_info(self):
        """调试页面信息"""
        try:
            print("🔍 Ubuntu调试信息:")
            print(f"   页面标题: {self.page.title}")
            print(f"   页面URL: {self.page.url}")
            
            # 保存页面HTML用于调试
            html_content = self.page.html
            with open('/tmp/lighter_debug.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"   HTML已保存到: /tmp/lighter_debug.html")
            print(f"   HTML长度: {len(html_content)} 字符")
            
        except Exception as e:
            print(f"   调试信息获取失败: {e}")
    
    def _check_page_loaded(self) -> bool:
        """检查页面是否加载完成"""
        try:
            # 多次尝试检查
            for attempt in range(3):
                print(f"   尝试检查页面 {attempt + 1}/3...")
                
                asks_container = self.page.ele('@data-testid=orderbook-asks')
                bids_container = self.page.ele('@data-testid=orderbook-bids')
                
                if asks_container and bids_container:
                    print("   ✅ 订单簿容器找到")
                    return True
                
                print("   ⏳ 等待2秒后重试...")
                time.sleep(2)
            
            print("   ❌ 订单簿容器未找到")
            return False
            
        except Exception as e:
            print(f"   ❌ 页面检查失败: {e}")
            return False
    
    def _scrape_loop(self):
        """数据抓取循环"""
        while self.running:
            try:
                orderbook = parse_orderbook_from_page(self.page)
                if orderbook and orderbook.asks and orderbook.bids:
                    self.data.orderbook = orderbook
                    self.data.timestamp = datetime.now()

                    print(f"Ubuntu Lighter数据更新: 买一=${orderbook.best_bid:.1f}, 卖一=${orderbook.best_ask:.1f}, 中间价=${orderbook.mid_price:.1f}")

                    # 调用回调函数
                    if self.on_data_callback:
                        self.on_data_callback(self.data)
                else:
                    print("Ubuntu: 订单簿数据为空或解析失败")

                time.sleep(3)  # Ubuntu使用较长间隔

            except Exception as e:
                print(f"Ubuntu Lighter数据抓取错误: {e}")
                time.sleep(10)  # 出错时等待更长时间
    
    def stop(self):
        """停止Lighter连接"""
        self.running = False
        if self.page:
            try:
                self.page.quit()
            except:
                pass
        self.data.connected = False
    
    def get_current_data(self) -> LighterData:
        """获取当前数据"""
        return self.data
    
    def is_connected(self) -> bool:
        """检查连接状态"""
        return self.data.connected and self.running
'''
    
    # 保存Ubuntu优化版客户端
    with open('core/ubuntu_lighter_client.py', 'w', encoding='utf-8') as f:
        f.write(ubuntu_client_code)
    
    print("✅ Ubuntu优化版Lighter客户端已创建: core/ubuntu_lighter_client.py")

def main():
    """主函数"""
    print("Ubuntu Lighter修复脚本")
    print("=" * 50)
    
    # 1. 检查系统
    if not check_system():
        return
    
    # 2. 检查Chrome
    chrome_path = check_chrome_installation()
    if not chrome_path:
        return
    
    # 3. 检查显示环境
    has_display = check_display_environment()
    
    # 4. 检查依赖
    if not check_dependencies():
        return
    
    # 5. 测试Chrome
    if not test_chrome_headless(chrome_path):
        print("\n❌ Chrome无头模式测试失败，可能需要安装额外依赖:")
        print("sudo apt install -y libnss3-dev libatk-bridge2.0-dev libdrm2 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libxss1 libasound2")
        return
    
    # 6. 创建Ubuntu优化版客户端
    create_ubuntu_lighter_client()
    
    print("\n🎉 Ubuntu修复完成！")
    print("\n使用方法:")
    print("1. 在主程序中导入: from core.ubuntu_lighter_client import UbuntuLighterClient")
    print("2. 替换原来的LighterClient")
    print("3. 确保使用无头模式")

if __name__ == "__main__":
    main()
