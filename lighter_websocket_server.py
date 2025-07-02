#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Lighter专用WebSocket服务器
只推送Lighter价格数据，不包含币安和Backpack
"""

import time
import threading
from datetime import datetime
from flask import Flask, request
from flask_socketio import SocketIO
from flask_cors import CORS
import pytz

from data.models import LighterData
from core.lighter_manager import create_lighter_client
from config import PAGE_REFRESH_INTERVAL

def get_china_time():
    """获取中国时间"""
    china_tz = pytz.timezone('Asia/Shanghai')
    return datetime.now(china_tz)

class LighterWebSocketServer:
    """Lighter专用WebSocket服务器"""
    
    def __init__(self, port=8081, headless=True):
        self.port = port
        self.headless = headless
        self.running = False
        self.data_lock = threading.Lock()
        self.lighter_data = LighterData()
        
        # 初始化Flask应用和WebSocket
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'lighter_websocket_secret_key'
        
        # 配置CORS
        CORS(self.app, resources={
            r"/*": {
                "origins": "*",
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"]
            }
        })
        
        # 配置WebSocket
        self.socketio = SocketIO(
            self.app, 
            cors_allowed_origins="*",
            async_mode='threading',
            logger=False,
            engineio_logger=False,
            allow_upgrades=True,
            transports=['websocket', 'polling'],
            ping_timeout=60,
            ping_interval=25
        )
        
        self.setup_websocket_events()
        self.setup_routes()
        
        # Lighter客户端
        self.lighter_client = None
        self.api_thread = None
    
    def setup_websocket_events(self):
        """设置WebSocket事件"""
        
        @self.socketio.on('connect')
        def handle_connect():
            print(f"🔌 Lighter WebSocket客户端连接: {request.sid}")
            # 发送当前Lighter数据
            with self.data_lock:
                if self.lighter_data.orderbook:
                    lighter_data = {
                        'type': 'lighter_data',
                        'data': {
                            'best_bid': self.lighter_data.orderbook.best_bid,
                            'best_ask': self.lighter_data.orderbook.best_ask,
                            'mid_price': self.lighter_data.orderbook.mid_price,
                            'spread': self.lighter_data.orderbook.spread,
                            'connected': self.lighter_data.connected,
                            'timestamp': get_china_time().strftime("%Y-%m-%d %H:%M:%S")
                        },
                        'timestamp': get_china_time().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    self.socketio.emit('lighter_data', lighter_data, room=request.sid)
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            print(f"🔌 Lighter WebSocket客户端断开: {request.sid}")
        
        @self.socketio.on('subscribe')
        def handle_subscribe():
            """订阅Lighter数据"""
            print(f"📊 客户端 {request.sid} 订阅Lighter数据")
            # 立即发送当前数据
            with self.data_lock:
                if self.lighter_data.orderbook:
                    lighter_data = {
                        'type': 'lighter_data',
                        'data': {
                            'best_bid': self.lighter_data.orderbook.best_bid,
                            'best_ask': self.lighter_data.orderbook.best_ask,
                            'mid_price': self.lighter_data.orderbook.mid_price,
                            'spread': self.lighter_data.orderbook.spread,
                            'connected': self.lighter_data.connected,
                            'timestamp': get_china_time().strftime("%Y-%m-%d %H:%M:%S")
                        },
                        'timestamp': get_china_time().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    self.socketio.emit('lighter_data', lighter_data, room=request.sid)
        
        @self.socketio.on('unsubscribe')
        def handle_unsubscribe():
            """取消订阅Lighter数据"""
            print(f"📊 客户端 {request.sid} 取消订阅Lighter数据")
    
    def setup_routes(self):
        """设置API路由"""
        
        @self.app.route('/api/lighter', methods=['GET'])
        def get_lighter_data():
            """获取当前Lighter数据"""
            with self.data_lock:
                if self.lighter_data.orderbook:
                    return {
                        'best_bid': self.lighter_data.orderbook.best_bid,
                        'best_ask': self.lighter_data.orderbook.best_ask,
                        'mid_price': self.lighter_data.orderbook.mid_price,
                        'spread': self.lighter_data.orderbook.spread,
                        'connected': self.lighter_data.connected,
                        'timestamp': get_china_time().strftime("%Y-%m-%d %H:%M:%S")
                    }
                else:
                    return {
                        'error': 'No data available',
                        'connected': False,
                        'timestamp': get_china_time().strftime("%Y-%m-%d %H:%M:%S")
                    }
        
        @self.app.route('/api/status', methods=['GET'])
        def get_status():
            """获取服务状态"""
            return {
                'service': 'Lighter WebSocket Server',
                'running': self.running,
                'connected': self.lighter_data.connected if self.lighter_data else False,
                'port': self.port,
                'timestamp': get_china_time().strftime("%Y-%m-%d %H:%M:%S")
            }
    
    def _on_lighter_data(self, data: LighterData):
        """Lighter数据回调"""
        with self.data_lock:
            self.lighter_data = data
            
            # 🚀 WebSocket实时推送Lighter数据
            if data.orderbook:
                lighter_data = {
                    'type': 'lighter_data',
                    'data': {
                        'best_bid': data.orderbook.best_bid,
                        'best_ask': data.orderbook.best_ask,
                        'mid_price': data.orderbook.mid_price,
                        'spread': data.orderbook.spread,
                        'connected': data.connected,
                        'timestamp': get_china_time().strftime("%Y-%m-%d %H:%M:%S")
                    },
                    'timestamp': get_china_time().strftime("%Y-%m-%d %H:%M:%S")
                }
                # 广播给所有连接的客户端
                self.socketio.emit('lighter_data', lighter_data)
    
    def start(self):
        """启动服务器"""
        print(f"🚀 启动Lighter WebSocket服务器...")
        
        # 启动Lighter客户端
        self.lighter_client = create_lighter_client(
            self._on_lighter_data, 
            headless=self.headless, 
            refresh_interval=PAGE_REFRESH_INTERVAL
        )
        
        if self.lighter_client.start():
            print("✅ Lighter客户端启动成功")
            self.running = True
            
            # 启动WebSocket服务器
            def run_server():
                self.socketio.run(self.app, host='0.0.0.0', port=self.port, debug=False, use_reloader=False)
            
            self.api_thread = threading.Thread(target=run_server, daemon=True)
            self.api_thread.start()
            
            print(f"✅ Lighter WebSocket服务器已启动")
            print(f"   📊 API接口: http://localhost:{self.port}/api/lighter")
            print(f"   🔌 WebSocket: ws://localhost:{self.port}/socket.io/")
            print(f"   📈 状态接口: http://localhost:{self.port}/api/status")
            
            return True
        else:
            print("❌ Lighter客户端启动失败")
            return False
    
    def stop(self):
        """停止服务器"""
        print("🛑 正在停止Lighter WebSocket服务器...")
        self.running = False
        
        if self.lighter_client:
            self.lighter_client.stop()
        
        print("✅ Lighter WebSocket服务器已停止")

def main():
    """主程序入口"""
    print("=== Lighter专用WebSocket服务器 ===")
    print("只推送Lighter价格数据")
    print("")
    
    # 创建服务器实例
    server = LighterWebSocketServer(port=8081, headless=True)
    
    try:
        if server.start():
            print("🎯 服务器运行中，按Ctrl+C停止...")
            
            # 保持运行
            while server.running:
                time.sleep(1)
        else:
            print("❌ 服务器启动失败")
    
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断")
    
    finally:
        server.stop()
        print("🔚 程序结束")

if __name__ == "__main__":
    main()
