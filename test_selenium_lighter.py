#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试Selenium Lighter客户端
"""

import time
from core.lighter_selenium_client import LighterSeleniumClient
from data.models import LighterData

def on_data_callback(data: LighterData):
    """数据回调函数"""
    if data.orderbook:
        print(f"📊 收到数据: 买一=${data.orderbook.best_bid:.1f}, 卖一=${data.orderbook.best_ask:.1f}, 中间价=${data.orderbook.mid_price:.1f}")
    else:
        print("📊 收到空数据")

def main():
    """主函数"""
    print("=== Selenium Lighter客户端测试 ===")
    
    # 创建客户端
    client = LighterSeleniumClient(on_data_callback, headless=True)
    
    try:
        # 启动客户端
        if client.start():
            print("✅ 客户端启动成功，等待数据...")
            
            # 运行30秒
            for i in range(30):
                time.sleep(1)
                if i % 5 == 0:
                    print(f"⏰ 运行中... {i+1}/30秒")
            
            print("✅ 测试完成")
        else:
            print("❌ 客户端启动失败")
    
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断测试")
    
    finally:
        # 停止客户端
        client.stop()
        print("🔚 客户端已停止")

if __name__ == "__main__":
    main()
