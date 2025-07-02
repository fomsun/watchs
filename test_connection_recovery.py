#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试连接恢复功能
验证Lighter客户端的自动重连机制
"""

import time
from core.lighter_client import LighterClient
from data.models import LighterData

class ConnectionTestClient(LighterClient):
    """扩展的测试客户端，可以模拟连接断开"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_disconnect_count = 0
    
    def simulate_disconnect(self):
        """模拟连接断开"""
        try:
            if self.page:
                print("🔌 模拟连接断开...")
                # 强制关闭页面连接
                self.page.quit()
                self.test_disconnect_count += 1
                print(f"❌ 连接已断开 (第{self.test_disconnect_count}次)")
        except Exception as e:
            print(f"模拟断开时出错: {e}")

def on_data_callback(data: LighterData):
    """数据回调函数"""
    if data.orderbook:
        print(f"📊 收到数据: 买一=${data.orderbook.best_bid:.1f}, 卖一=${data.orderbook.best_ask:.1f}, 中间价=${data.orderbook.mid_price:.1f}")
    else:
        print("📊 收到空数据")

def main():
    """主函数"""
    print("=== Lighter连接恢复功能测试 ===")
    print("此测试将验证自动重连机制")
    print("")
    
    # 创建测试客户端
    client = ConnectionTestClient(on_data_callback, headless=True, refresh_interval=120)
    
    try:
        # 启动客户端
        if client.start():
            print("✅ 客户端启动成功")
            print("🎯 开始监控数据，将定期模拟连接断开...")
            print("")
            
            # 运行测试
            start_time = time.time()
            test_duration = 300  # 运行5分钟
            disconnect_interval = 60  # 每60秒模拟一次断开
            last_disconnect = 0
            
            while time.time() - start_time < test_duration:
                elapsed = int(time.time() - start_time)
                
                # 定期模拟连接断开
                if elapsed - last_disconnect >= disconnect_interval and elapsed > 30:
                    client.simulate_disconnect()
                    last_disconnect = elapsed
                    print("⏰ 等待自动重连...")
                
                # 显示运行状态
                next_disconnect = disconnect_interval - (elapsed - last_disconnect)
                if next_disconnect > 0:
                    print(f"⏰ 运行时间: {elapsed}秒, 下次断开测试: {next_disconnect}秒后", end='\r')
                else:
                    print(f"⏰ 运行时间: {elapsed}秒, 等待重连中...", end='\r')
                
                time.sleep(1)
            
            print(f"\n✅ 测试完成，运行了{test_duration}秒")
            print(f"📊 总共模拟了{client.test_disconnect_count}次连接断开")
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
