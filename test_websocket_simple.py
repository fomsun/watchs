#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简化的WebSocket连接测试
专门测试跨域和连接问题
"""

import socketio
import time

def test_websocket_connection():
    """测试WebSocket连接"""
    print("=== WebSocket连接测试 ===")
    print("测试跨域和连接问题")
    print("")
    
    # 创建客户端，启用详细日志
    sio = socketio.Client(logger=True, engineio_logger=True)
    
    @sio.event
    def connect():
        print("✅ WebSocket连接成功！")
        print("🎯 发送测试消息...")
        sio.emit('subscribe_lighter')
    
    @sio.event
    def disconnect():
        print("🔌 WebSocket连接断开")
    
    @sio.event
    def connect_error(data):
        print(f"❌ 连接错误: {data}")
    
    @sio.event
    def lighter_update(data):
        print(f"⚡ 收到Lighter数据: {data}")
    
    @sio.event
    def price_update(data):
        print(f"📊 收到价格数据: {data}")
    
    try:
        print("🚀 正在连接到 http://localhost:8080...")
        
        # 尝试连接
        sio.connect('http://localhost:8080', 
                   transports=['websocket', 'polling'],
                   wait_timeout=10)
        
        print("✅ 连接建立成功")
        
        # 保持连接30秒
        print("⏰ 保持连接30秒，监听数据...")
        time.sleep(30)
        
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        print("\n🔧 可能的解决方案:")
        print("1. 确保BTC价格监控程序正在运行")
        print("2. 检查端口8080是否被占用")
        print("3. 检查防火墙设置")
        print("4. 尝试重启监控程序")
    
    finally:
        try:
            sio.disconnect()
            print("🔚 连接已关闭")
        except:
            pass

def test_http_api():
    """测试HTTP API是否正常"""
    print("\n=== HTTP API测试 ===")
    try:
        import requests
        response = requests.get('http://localhost:8080/api/btc-price', timeout=5)
        if response.status_code == 200:
            print("✅ HTTP API正常工作")
            return True
        else:
            print(f"❌ HTTP API返回错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ HTTP API测试失败: {e}")
        return False

def main():
    """主函数"""
    print("开始WebSocket连接诊断...")
    print("")
    
    # 先测试HTTP API
    if test_http_api():
        # HTTP正常，测试WebSocket
        test_websocket_connection()
    else:
        print("❌ HTTP API不可用，请先启动BTC价格监控程序")
        print("启动命令: python3 btc_price_monitor.py")

if __name__ == "__main__":
    main()
