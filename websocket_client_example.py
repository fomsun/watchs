#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WebSocket客户端示例
演示如何订阅Lighter实时数据
"""

import socketio
import time
import json

class LighterWebSocketClient:
    """Lighter WebSocket客户端"""
    
    def __init__(self, server_url="http://47.245.62.204:8080"):
        self.server_url = server_url
        self.sio = socketio.Client()
        self.connected = False
        self.setup_events()
    
    def setup_events(self):
        """设置事件处理"""
        
        @self.sio.event
        def connect():
            print("🔌 WebSocket连接成功")
            self.connected = True
        
        @self.sio.event
        def disconnect():
            print("🔌 WebSocket连接断开")
            self.connected = False
        
        @self.sio.event
        def price_update(data):
            """接收价格更新"""
            print("📊 收到价格更新:")
            if data.get('binance'):
                print(f"   币安: ${data['binance'].get('price', 'N/A')}")
            if data.get('backpack'):
                print(f"   Backpack: ${data['backpack'].get('price', 'N/A')}")
            if data.get('lighter'):
                lighter = data['lighter']
                print(f"   Lighter: ${lighter.get('mid_price', 'N/A')} (买一: ${lighter.get('best_bid', 'N/A')}, 卖一: ${lighter.get('best_ask', 'N/A')})")
            print(f"   时间: {data.get('timestamp', 'N/A')}")
            print("-" * 50)
        
        @self.sio.event
        def lighter_update(data):
            """接收Lighter数据更新"""
            print("⚡ 收到Lighter实时数据:")
            lighter_data = data.get('data', {})
            print(f"   中间价: ${lighter_data.get('mid_price', 'N/A')}")
            print(f"   买一价: ${lighter_data.get('best_bid', 'N/A')}")
            print(f"   卖一价: ${lighter_data.get('best_ask', 'N/A')}")
            print(f"   价差: ${lighter_data.get('spread', 'N/A')}")
            print(f"   连接状态: {'✅' if lighter_data.get('connected') else '❌'}")
            print(f"   时间: {lighter_data.get('timestamp', 'N/A')}")
            print("=" * 50)
    
    def connect(self):
        """连接到服务器"""
        try:
            print(f"🚀 正在连接到 {self.server_url}...")
            self.sio.connect(self.server_url)
            return True
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            return False
    
    def disconnect(self):
        """断开连接"""
        if self.connected:
            self.sio.disconnect()
            print("🔌 已断开连接")
    
    def subscribe_lighter(self):
        """订阅Lighter数据"""
        if self.connected:
            self.sio.emit('subscribe_lighter')
            print("📊 已发送Lighter订阅请求")
        else:
            print("❌ 未连接，无法订阅")
    
    def unsubscribe_lighter(self):
        """取消订阅Lighter数据"""
        if self.connected:
            self.sio.emit('unsubscribe_lighter')
            print("📊 已发送Lighter取消订阅请求")
        else:
            print("❌ 未连接，无法取消订阅")
    
    def wait(self):
        """等待事件"""
        self.sio.wait()

def main():
    """主函数"""
    print("=== Lighter WebSocket客户端示例 ===")
    print("请确保BTC价格监控程序正在运行...")
    print("启动命令: python3 btc_price_monitor.py")
    print("")
    
    # 创建客户端
    client = LighterWebSocketClient()
    
    try:
        # 连接到服务器
        if not client.connect():
            return
        
        # 等待连接稳定
        time.sleep(1)
        
        # 订阅Lighter数据
        client.subscribe_lighter()
        
        print("🎯 开始接收实时数据，按Ctrl+C停止...")
        print("=" * 50)
        
        # 保持连接并接收数据
        client.wait()
        
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断")
    except Exception as e:
        print(f"❌ 运行错误: {e}")
    finally:
        # 清理连接
        client.disconnect()
        print("✅ 程序结束")

if __name__ == "__main__":
    main()
