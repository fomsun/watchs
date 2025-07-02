#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试WebSocket推送功能
验证Lighter数据的实时推送
"""

import socketio
import time
import threading
from datetime import datetime

class WebSocketTester:
    """WebSocket测试器"""
    
    def __init__(self, server_url="http://localhost:8080"):
        self.server_url = server_url
        self.sio = socketio.Client()
        self.connected = False
        self.lighter_updates = 0
        self.price_updates = 0
        self.last_lighter_data = None
        self.setup_events()
    
    def setup_events(self):
        """设置事件处理"""
        
        @self.sio.event
        def connect():
            print("🔌 WebSocket连接成功")
            self.connected = True
            print("📊 发送Lighter订阅请求...")
            self.sio.emit('subscribe_lighter')
        
        @self.sio.event
        def disconnect():
            print("🔌 WebSocket连接断开")
            self.connected = False
        
        @self.sio.event
        def price_update(data):
            """接收价格更新"""
            self.price_updates += 1
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"📊 [{timestamp}] 收到价格更新 (第{self.price_updates}次):")
            
            if data.get('binance'):
                print(f"   币安: ${data['binance'].get('price', 'N/A')}")
            if data.get('backpack'):
                print(f"   Backpack: ${data['backpack'].get('price', 'N/A')}")
            if data.get('lighter'):
                lighter = data['lighter']
                print(f"   Lighter: ${lighter.get('mid_price', 'N/A')} (买一: ${lighter.get('best_bid', 'N/A')}, 卖一: ${lighter.get('best_ask', 'N/A')})")
            print("-" * 50)
        
        @self.sio.event
        def lighter_update(data):
            """接收Lighter数据更新"""
            self.lighter_updates += 1
            self.last_lighter_data = data
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            print(f"⚡ [{timestamp}] 收到Lighter实时数据 (第{self.lighter_updates}次):")
            
            if 'data' in data:
                lighter_data = data['data']
                print(f"   中间价: ${lighter_data.get('mid_price', 'N/A')}")
                print(f"   买一价: ${lighter_data.get('best_bid', 'N/A')}")
                print(f"   卖一价: ${lighter_data.get('best_ask', 'N/A')}")
                print(f"   价差: ${lighter_data.get('spread', 'N/A')}")
                print(f"   连接状态: {'✅' if lighter_data.get('connected') else '❌'}")
                print(f"   数据时间: {lighter_data.get('timestamp', 'N/A')}")
            
            print(f"   推送时间: {data.get('timestamp', 'N/A')}")
            print("=" * 50)
        
        @self.sio.event
        def connect_error(error):
            print(f"❌ 连接错误: {error}")
            self.connected = False
    
    def connect_to_server(self):
        """连接到服务器"""
        try:
            print(f"🚀 正在连接到 {self.server_url}...")
            self.sio.connect(self.server_url)
            return True
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            return False
    
    def disconnect_from_server(self):
        """断开连接"""
        if self.connected:
            self.sio.emit('unsubscribe_lighter')
            time.sleep(0.5)
            self.sio.disconnect()
            print("🔌 已断开连接")
    
    def print_statistics(self):
        """打印统计信息"""
        print(f"\n📈 WebSocket推送统计:")
        print(f"   🔌 连接状态: {'✅ 已连接' if self.connected else '❌ 未连接'}")
        print(f"   📊 价格更新次数: {self.price_updates}")
        print(f"   ⚡ Lighter更新次数: {self.lighter_updates}")
        
        if self.last_lighter_data:
            print(f"   🕐 最后数据时间: {self.last_lighter_data.get('timestamp', 'N/A')}")
        
        print("-" * 50)
    
    def wait_for_data(self, duration=60):
        """等待数据推送"""
        print(f"⏰ 等待{duration}秒，监听数据推送...")
        start_time = time.time()
        
        while time.time() - start_time < duration:
            elapsed = int(time.time() - start_time)
            remaining = duration - elapsed
            
            print(f"⏰ 已运行{elapsed}秒，剩余{remaining}秒 | 价格更新:{self.price_updates}次 | Lighter更新:{self.lighter_updates}次", end='\r')
            time.sleep(1)
        
        print(f"\n⏰ 监听完成")

def main():
    """主函数"""
    print("=== WebSocket推送功能测试 ===")
    print("此测试将验证Lighter数据的实时推送")
    print("")
    print("⚠️  请确保BTC价格监控程序正在运行:")
    print("   python3 btc_price_monitor.py")
    print("")
    
    # 等待用户确认
    input("按回车键开始测试...")
    
    # 创建测试器
    tester = WebSocketTester()
    
    try:
        # 连接到服务器
        if tester.connect_to_server():
            print("✅ WebSocket连接成功")
            
            # 等待初始连接稳定
            time.sleep(2)
            
            # 监听数据推送
            tester.wait_for_data(120)  # 监听2分钟
            
            # 打印最终统计
            tester.print_statistics()
            
            # 测试取消订阅
            print("\n🔄 测试取消订阅...")
            tester.sio.emit('unsubscribe_lighter')
            time.sleep(5)
            
            # 重新订阅
            print("🔄 测试重新订阅...")
            tester.sio.emit('subscribe_lighter')
            time.sleep(10)
            
            print("✅ 测试完成")
        else:
            print("❌ 无法连接到WebSocket服务器")
            print("请确保BTC价格监控程序正在运行")
    
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断测试")
    
    finally:
        # 清理连接
        tester.disconnect_from_server()
        print("🔚 测试结束")

if __name__ == "__main__":
    main()
