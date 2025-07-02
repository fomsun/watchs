#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试浏览器伪装效果
验证是否成功伪装成macOS Chrome
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

def test_masquerade():
    """测试浏览器伪装"""
    print("=== 浏览器伪装测试 ===")
    
    try:
        # 配置Chrome选项（与Selenium客户端相同）
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--disable-features=VizDisplayCompositor')
        
        # 🎭 伪装成macOS Chrome浏览器
        macos_user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        chrome_options.add_argument(f'--user-agent={macos_user_agent}')
        
        # 设置窗口大小
        chrome_options.add_argument('--window-size=1440,900')
        chrome_options.add_argument('--lang=zh-CN,zh,en-US,en')
        
        # 禁用自动化检测
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # 创建WebDriver
        service = Service()
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # 执行JavaScript伪装
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.execute_script("Object.defineProperty(navigator, 'platform', {get: () => 'MacIntel'})")
        driver.execute_script("Object.defineProperty(navigator, 'userAgent', {get: () => 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'})")
        
        print("🎭 伪装配置完成，测试检测网站...")
        
        # 访问检测网站
        test_urls = [
            "https://httpbin.org/headers",
            "https://www.whatismybrowser.com/detect/what-is-my-user-agent",
            "https://app.lighter.xyz/trade/BTC?locale=zh"
        ]
        
        for url in test_urls:
            try:
                print(f"\n🔗 访问: {url}")
                driver.get(url)
                time.sleep(3)
                
                # 验证伪装效果
                user_agent = driver.execute_script("return navigator.userAgent")
                platform_info = driver.execute_script("return navigator.platform")
                webdriver_prop = driver.execute_script("return navigator.webdriver")
                language = driver.execute_script("return navigator.language")
                
                print(f"   User-Agent: {user_agent}")
                print(f"   Platform: {platform_info}")
                print(f"   WebDriver: {webdriver_prop}")
                print(f"   Language: {language}")
                
                # 检查页面标题
                print(f"   页面标题: {driver.title}")
                
                # 对于Lighter页面，检查特殊元素
                if "lighter.xyz" in url:
                    print("   🔍 检查Lighter页面元素...")
                    
                    # 等待页面加载
                    time.sleep(10)
                    
                    # 查找订单簿元素
                    asks_elements = driver.find_elements(By.CSS_SELECTOR, '[data-testid="orderbook-asks"]')
                    bids_elements = driver.find_elements(By.CSS_SELECTOR, '[data-testid="orderbook-bids"]')
                    
                    print(f"   订单簿asks容器: {len(asks_elements)} 个")
                    print(f"   订单簿bids容器: {len(bids_elements)} 个")
                    
                    # 查找所有data-testid元素
                    testid_elements = driver.find_elements(By.CSS_SELECTOR, '[data-testid]')
                    print(f"   data-testid元素总数: {len(testid_elements)}")
                    
                    # 显示前10个data-testid
                    for i, elem in enumerate(testid_elements[:10]):
                        try:
                            testid = elem.get_attribute('data-testid')
                            print(f"      {i+1}. data-testid='{testid}'")
                        except:
                            pass
                    
                    # 保存页面源码
                    with open(f'/tmp/lighter_masquerade_test.html', 'w', encoding='utf-8') as f:
                        f.write(driver.page_source)
                    print(f"   页面源码已保存到: /tmp/lighter_masquerade_test.html")
                
                # 验证伪装成功
                if "Mac" in platform_info and webdriver_prop is None:
                    print("   ✅ 伪装成功")
                else:
                    print("   ⚠️  伪装可能不完全")
                    
            except Exception as e:
                print(f"   ❌ 访问失败: {e}")
        
        # 关闭浏览器
        driver.quit()
        print("\n✅ 伪装测试完成")
        
    except Exception as e:
        print(f"❌ 伪装测试失败: {e}")

def main():
    """主函数"""
    test_masquerade()

if __name__ == "__main__":
    main()
