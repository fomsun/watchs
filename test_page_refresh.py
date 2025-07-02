#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试页面刷新功能
验证Lighter客户端的自动刷新机制
"""

import time
from core.lighter_client import LighterClient
from data.models import LighterData

def on_data_callback(data: LighterData):
    """数据回调函数"""
    if data.orderbook:
        print(f"📊 收到数据: 买一=${data.orderbook.best_bid:.1f}, 卖一=${data.orderbook.best_ask:.1f}, 中间价=${data.orderbook.mid_price:.1f}")
    else:
        print("📊 收到空数据")

def main():
    """主函数"""
    print("=== Lighter页面刷新功能测试 ===")
    print("此测试将验证页面自动刷新功能")
    print("设置刷新间隔为60秒（测试用）")
    print("")
    
    # 创建客户端，设置短刷新间隔用于测试
    refresh_interval = 60  # 1分钟刷新一次（测试用）
    client = LighterClient(on_data_callback, headless=True, refresh_interval=refresh_interval)
    
    try:
        # 启动客户端
        if client.start():
            print("✅ 客户端启动成功")
            print(f"🔄 页面将每{refresh_interval}秒刷新一次")
            print("⏰ 等待刷新事件...")
            print("")
            
            # 运行足够长的时间来观察刷新
            start_time = time.time()
            test_duration = 180  # 运行3分钟
            
            while time.time() - start_time < test_duration:
                elapsed = int(time.time() - start_time)
                next_refresh = refresh_interval - (elapsed % refresh_interval)
                
                print(f"⏰ 运行时间: {elapsed}秒, 下次刷新: {next_refresh}秒后", end='\r')
                time.sleep(1)
            
            print(f"\n✅ 测试完成，运行了{test_duration}秒")
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
