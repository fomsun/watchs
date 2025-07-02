#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试DrissionPage伪装效果
验证是否成功伪装成macOS Chrome
"""

import time
from DrissionPage import ChromiumPage, ChromiumOptions
from config import get_chrome_path

def test_masquerade():
    """测试DrissionPage伪装"""
    print("=== DrissionPage伪装测试 ===")
    
    try:
        # 配置Chrome选项（与Lighter客户端相同）
        co = ChromiumOptions()
        co.headless()  # 使用无头模式
        
        # 设置Chrome路径
        chrome_path = get_chrome_path()
        if chrome_path:
            co.set_browser_path(chrome_path)
            print(f"🌐 使用Chrome路径: {chrome_path}")
        
        # 🎭 伪装成macOS Chrome浏览器
        macos_user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        co.set_user_agent(macos_user_agent)
        print("🎭 伪装成macOS Chrome浏览器")
        
        # 设置macOS相关的首选项
        co.set_pref('profile.default_content_settings.popups', 0)
        co.set_pref('credentials_enable_service', False)
        co.set_pref('profile.default_content_setting_values.notifications', 2)
        
        # 设置窗口大小
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
            print("🐧 已添加Linux兼容性参数")
        
        # 其他优化配置
        co.no_imgs(True)
        co.mute(True)
        
        # 创建页面
        page = ChromiumPage(co)
        
        # 执行JavaScript伪装
        print("🎭 执行JavaScript伪装...")
        try:
            page.run_js("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            page.run_js("Object.defineProperty(navigator, 'platform', {get: () => 'MacIntel'})")
            page.run_js("Object.defineProperty(navigator, 'userAgent', {get: () => 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'})")
            print("✅ JavaScript伪装完成")
        except Exception as e:
            print(f"⚠️  JavaScript伪装失败: {e}")
        
        # 测试不同的网站
        test_urls = [
            "https://httpbin.org/headers",
            "https://app.lighter.xyz/trade/BTC?locale=zh"
        ]
        
        for url in test_urls:
            try:
                print(f"\n🔗 访问: {url}")
                page.get(url)
                time.sleep(5)
                
                # 验证伪装效果
                try:
                    user_agent = page.run_js("return navigator.userAgent")
                    platform_info = page.run_js("return navigator.platform")
                    webdriver_prop = page.run_js("return navigator.webdriver")
                    language = page.run_js("return navigator.language")
                    
                    print(f"   User-Agent: {user_agent}")
                    print(f"   Platform: {platform_info}")
                    print(f"   WebDriver: {webdriver_prop}")
                    print(f"   Language: {language}")
                    
                    # 检查页面标题
                    print(f"   页面标题: {page.title}")
                    
                    # 对于Lighter页面，检查特殊元素
                    if "lighter.xyz" in url:
                        print("   🔍 检查Lighter页面元素...")
                        
                        # 等待页面加载
                        time.sleep(15)
                        
                        # 查找订单簿元素
                        asks_elements = page.eles('@data-testid=orderbook-asks')
                        bids_elements = page.eles('@data-testid=orderbook-bids')
                        
                        print(f"   订单簿asks容器: {len(asks_elements)} 个")
                        print(f"   订单簿bids容器: {len(bids_elements)} 个")
                        
                        # 查找所有data-testid元素
                        testid_elements = page.eles('@data-testid')
                        print(f"   data-testid元素总数: {len(testid_elements)}")
                        
                        # 显示前10个data-testid
                        for i, elem in enumerate(testid_elements[:10]):
                            try:
                                testid = elem.attr('data-testid')
                                print(f"      {i+1}. data-testid='{testid}'")
                            except:
                                pass
                        
                        # 保存页面源码
                        with open(f'/tmp/lighter_drissionpage_test.html', 'w', encoding='utf-8') as f:
                            f.write(page.html)
                        print(f"   页面源码已保存到: /tmp/lighter_drissionpage_test.html")
                        
                        # 检查是否找到订单簿
                        if asks_elements and bids_elements:
                            print("   ✅ 成功找到订单簿容器！")
                        else:
                            print("   ❌ 未找到订单簿容器")
                    
                    # 验证伪装成功
                    if "Mac" in platform_info and webdriver_prop is None:
                        print("   ✅ 伪装成功")
                    else:
                        print("   ⚠️  伪装可能不完全")
                        
                except Exception as e:
                    print(f"   ❌ 验证失败: {e}")
                    
            except Exception as e:
                print(f"   ❌ 访问失败: {e}")
        
        # 关闭浏览器
        page.quit()
        print("\n✅ 伪装测试完成")
        
    except Exception as e:
        print(f"❌ 伪装测试失败: {e}")
        import traceback
        print(f"错误详情: {traceback.format_exc()}")

def main():
    """主函数"""
    test_masquerade()

if __name__ == "__main__":
    main()
