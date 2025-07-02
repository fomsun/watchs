#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Lighter网页调试测试脚本
用于分析网页内容和元素结构
"""

import time
import os
from datetime import datetime

try:
    from DrissionPage import ChromiumPage, ChromiumOptions
    DRISSION_AVAILABLE = True
except ImportError:
    DRISSION_AVAILABLE = False
    print("❌ DrissionPage未安装")
    exit(1)

from config import get_chrome_path

def test_lighter_page():
    """测试Lighter页面加载和元素分析"""
    
    print("=== Lighter网页调试测试 ===")
    
    # 配置浏览器
    co = ChromiumOptions()
    
    # 设置Chrome路径
    chrome_path = get_chrome_path()
    if chrome_path:
        co.set_browser_path(chrome_path)
        print(f"🌐 使用Chrome路径: {chrome_path}")
    
    # 启用JavaScript（确保不禁用）
    print("✅ JavaScript已启用")
    
    # 基本配置
    co.mute(True)  # 静音
    
    # 可选：使用有界面模式进行调试
    use_headless = input("是否使用无头模式？(y/n): ").lower() == 'y'
    if use_headless:
        co.headless()
        print("🔇 使用无头模式")
    else:
        print("🖥️ 使用有界面模式")
    
    try:
        # 创建页面
        page = ChromiumPage(co)
        
        # 访问Lighter页面
        url = "https://app.lighter.xyz/trade/BTC?locale=zh"
        print(f"🔗 访问页面: {url}")
        page.get(url)
        
        # 等待页面加载
        print("⏳ 等待页面加载...")
        time.sleep(15)  # 增加等待时间
        
        # 获取页面基本信息
        print("\n📊 页面基本信息:")
        print(f"   标题: {page.title}")
        print(f"   URL: {page.url}")
        
        # 检查页面状态
        print(f"   加载状态: {page.states.is_loading}")
        print(f"   就绪状态: {page.states.ready_state}")
        
        # 获取HTML内容
        html_content = page.html
        print(f"   HTML长度: {len(html_content)} 字符")
        
        # 保存完整HTML到文件
        with open("lighter_page_debug.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        print("   ✅ HTML已保存到 lighter_page_debug.html")
        
        # 检查关键词
        keywords = ["Lighter", "BTC", "orderbook", "ask", "bid", "price"]
        found_keywords = []
        for kw in keywords:
            if kw.lower() in html_content.lower():
                found_keywords.append(kw)
        print(f"   关键词: {found_keywords}")
        
        # 等待JavaScript执行
        print("\n⏳ 等待JavaScript执行...")
        time.sleep(10)
        
        # 分析订单簿相关元素
        print("\n🔍 分析订单簿元素:")
        
        # 1. 查找订单簿容器
        containers_to_check = [
            '@data-testid=orderbook-asks',
            '@data-testid=orderbook-bids',
            '.orderbook',
            '[data-testid*="orderbook"]',
            '.asks',
            '.bids'
        ]
        
        found_containers = {}
        for selector in containers_to_check:
            try:
                element = page.ele(selector)
                found_containers[selector] = element is not None
                if element:
                    print(f"   ✅ 容器: {selector}")
                    print(f"      HTML片段: {element.html[:200]}...")
                else:
                    print(f"   ❌ 容器: {selector}")
            except Exception as e:
                print(f"   ❌ 容器 {selector} 错误: {e}")
        
        # 2. 查找具体的订单元素
        print("\n🔍 查找订单元素:")
        order_selectors = [
            '@data-testid^ob-ask-',
            '@data-testid^ob-bid-',
            '@data-testid*ask',
            '@data-testid*bid',
            'div[data-testid*="ask"]',
            'div[data-testid*="bid"]',
            'tr[data-testid*="ask"]',
            'tr[data-testid*="bid"]',
            '.ask',
            '.bid',
            '.price',
            'tr',
            'table tr'
        ]
        
        for selector in order_selectors:
            try:
                elements = page.eles(selector)
                if elements:
                    print(f"   ✅ {selector}: 找到 {len(elements)} 个元素")
                    # 显示前3个元素的内容
                    for i, elem in enumerate(elements[:3]):
                        print(f"      元素{i+1}: {elem.text[:50]}...")
                        print(f"      HTML: {elem.html[:100]}...")
                else:
                    print(f"   ❌ {selector}: 未找到")
            except Exception as e:
                print(f"   ❌ {selector} 错误: {e}")
        
        # 3. 查找所有包含数字的元素（可能是价格）
        print("\n🔍 查找包含数字的元素:")
        try:
            import re
            all_elements = page.eles('*')
            price_elements = []
            
            for elem in all_elements:
                try:
                    text = elem.text.strip()
                    if text and re.search(r'\d+[,.]?\d*', text):
                        # 检查是否可能是价格（包含较大的数字）
                        numbers = re.findall(r'[\d,]+\.?\d*', text)
                        for num_str in numbers:
                            try:
                                num = float(num_str.replace(',', ''))
                                if 50000 < num < 200000:  # BTC价格范围
                                    price_elements.append((elem, text, num))
                                    break
                            except:
                                continue
                except:
                    continue
            
            print(f"   找到 {len(price_elements)} 个可能的价格元素:")
            for i, (elem, text, price) in enumerate(price_elements[:10]):
                print(f"      价格{i+1}: {price} - 文本: '{text}' - 标签: {elem.tag}")
                print(f"      HTML: {elem.html[:100]}...")
                
        except Exception as e:
            print(f"   查找价格元素错误: {e}")
        
        # 4. 检查页面是否有错误
        print("\n🔍 检查页面错误:")
        try:
            # 检查控制台错误
            errors = page.run_js("return window.console.errors || []")
            if errors:
                print(f"   发现 {len(errors)} 个控制台错误:")
                for error in errors[:5]:
                    print(f"      {error}")
            else:
                print("   ✅ 无控制台错误")
        except Exception as e:
            print(f"   检查控制台错误失败: {e}")
        
        # 5. 执行JavaScript检查
        print("\n🔍 JavaScript检查:")
        try:
            # 检查jQuery是否可用
            jquery_available = page.run_js("return typeof $ !== 'undefined'")
            print(f"   jQuery可用: {jquery_available}")
            
            # 检查React是否可用
            react_available = page.run_js("return typeof React !== 'undefined'")
            print(f"   React可用: {react_available}")
            
            # 检查页面是否完全加载
            ready_state = page.run_js("return document.readyState")
            print(f"   文档状态: {ready_state}")
            
            # 尝试查找订单簿数据
            orderbook_data = page.run_js("""
                // 尝试查找订单簿相关的数据
                const askElements = document.querySelectorAll('[data-testid*="ask"]');
                const bidElements = document.querySelectorAll('[data-testid*="bid"]');
                return {
                    askCount: askElements.length,
                    bidCount: bidElements.length,
                    askTexts: Array.from(askElements).slice(0, 3).map(el => el.textContent),
                    bidTexts: Array.from(bidElements).slice(0, 3).map(el => el.textContent)
                };
            """)
            print(f"   JS查找结果: {orderbook_data}")
            
        except Exception as e:
            print(f"   JavaScript检查错误: {e}")
        
        # 等待用户输入（如果是有界面模式）
        if not use_headless:
            input("\n按回车键继续...")
        
        # 关闭浏览器
        page.quit()
        print("\n✅ 测试完成")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        print(f"错误详情: {traceback.format_exc()}")

if __name__ == "__main__":
    test_lighter_page()
