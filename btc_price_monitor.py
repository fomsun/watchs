#!/usr/bin/env python3
"""
BTC价格监控程序
监控多个交易所的BTC价格并提供API接口
"""

import time
import threading
import json
from datetime import datetime
from typing import Dict, Any, Optional
from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import pytz

from data.models import BTCPriceData, BinanceData, BackpackData, LighterData
from core.binance_client import BinanceClient
from core.backpack_client import BackpackClient
from core.lighter_manager import create_lighter_client
from core.price_recorder import PriceRecorder
from config import PAGE_REFRESH_INTERVAL

def get_china_time():
    """获取中国时间"""
    china_tz = pytz.timezone('Asia/Shanghai')
    return datetime.now(china_tz)

class BTCPriceMonitor:
    """BTC价格监控器"""
    
    def __init__(self, headless: bool = True):
        """
        初始化BTC价格监控器
        
        Args:
            headless: 是否使用无头模式运行浏览器
        """
        self.price_data = BTCPriceData()
        self.headless = headless
        self.clients = {}
        self.running = False
        self.data_lock = threading.Lock()  # 数据锁，防止并发访问冲突
        
        # 初始化API服务器和WebSocket
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'btc_price_monitor_secret_key'

        # 配置CORS，解决跨域问题
        CORS(self.app, resources={
            r"/*": {
                "origins": "*",
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"]
            }
        })

        # 配置WebSocket，解决跨域问题
        self.socketio = SocketIO(
            self.app,
            cors_allowed_origins="*",
            async_mode='threading',
            logger=False,  # 生产环境关闭详细日志
            engineio_logger=False,
            allow_upgrades=True,
            transports=['websocket', 'polling'],
            ping_timeout=60,
            ping_interval=25
        )
        self.setup_routes()
        self.setup_websocket_events()
        self.api_thread = None

        # 初始化价格记录器
        self.price_recorder = PriceRecorder("btc_price_data.txt")

    def setup_websocket_events(self):
        """设置WebSocket事件"""

        @self.socketio.on('connect')
        def handle_connect():
            print(f"🔌 WebSocket客户端连接: {request.sid}")
            # 发送当前价格数据
            with self.data_lock:
                self.socketio.emit('price_update', self.price_data.to_dict(), room=request.sid)

        @self.socketio.on('disconnect')
        def handle_disconnect():
            print(f"🔌 WebSocket客户端断开: {request.sid}")

        @self.socketio.on('subscribe_lighter')
        def handle_subscribe_lighter():
            """订阅Lighter数据"""
            print(f"📊 客户端 {request.sid} 订阅Lighter数据")
            # 发送当前Lighter数据
            with self.data_lock:
                if self.price_data.lighter:
                    lighter_data = {
                        'type': 'lighter_update',
                        'data': self.price_data.lighter.to_dict(),
                        'timestamp': get_china_time().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    self.socketio.emit('lighter_update', lighter_data, room=request.sid)

        @self.socketio.on('unsubscribe_lighter')
        def handle_unsubscribe_lighter():
            """取消订阅Lighter数据"""
            print(f"📊 客户端 {request.sid} 取消订阅Lighter数据")

    def setup_routes(self):
        """设置API路由"""
        @self.app.route('/api/btc-price', methods=['GET'])
        def get_btc_price():
            with self.data_lock:
                return jsonify(self.price_data.to_dict())

        @self.app.route('/api/btc-price/history', methods=['GET'])
        def get_btc_price_history():
            """获取历史价格数据"""
            try:
                # 获取查询参数
                count_param = request.args.get('count')
                format_type = request.args.get('format', 'json')  # 返回格式：json 或 raw

                # 处理count参数
                if count_param is None:
                    # 如果没有提供count参数，返回全部记录
                    count = None
                else:
                    # 如果提供了count参数，限制最大返回数量
                    count = min(int(count_param), 1000)

                # 获取历史记录
                records = self.price_recorder.get_latest_records(count)

                if format_type == 'raw':
                    # 返回原始格式
                    return jsonify({
                        "count": len(records),
                        "format": "raw",
                        "data": records
                    })
                else:
                    # 解析并返回结构化数据
                    parsed_data = []
                    for record in records:
                        try:
                            # 解析格式: 币安:价格-Backpack:价格-Lighter:价格-时间
                            parts = record.split('-')
                            if len(parts) >= 4:
                                binance_part = parts[0].split(':')
                                backpack_part = parts[1].split(':')
                                lighter_part = parts[2].split(':')
                                # 时间戳可能包含多个部分（日期和时间），需要重新组合
                                timestamp = '-'.join(parts[3:]) if len(parts) > 4 else parts[3]

                                parsed_data.append({
                                    "binance": {
                                        "exchange": binance_part[0],
                                        "price": float(binance_part[1]) if len(binance_part) > 1 and binance_part[1] != 'N/A' else None
                                    },
                                    "backpack": {
                                        "exchange": backpack_part[0],
                                        "price": float(backpack_part[1]) if len(backpack_part) > 1 and backpack_part[1] != 'N/A' else None
                                    },
                                    "lighter": {
                                        "exchange": lighter_part[0],
                                        "price": float(lighter_part[1]) if len(lighter_part) > 1 and lighter_part[1] != 'N/A' else None
                                    },
                                    "timestamp": timestamp
                                })
                        except (ValueError, IndexError) as e:
                            # 跳过解析失败的记录
                            continue

                    return jsonify({
                        "count": len(parsed_data),
                        "format": "json",
                        "data": parsed_data
                    })

            except Exception as e:
                return jsonify({
                    "error": f"获取历史数据失败: {str(e)}"
                }), 500
    
    def start(self):
        """启动所有价格监控"""
        print("🚀 启动BTC价格监控...")
        self.running = True
        
        # 启动币安客户端
        self._start_binance_client()
        
        # 启动Backpack客户端
        self._start_backpack_client()
        
        # 启动Lighter客户端
        self._start_lighter_client()
        
        # 启动API服务器
        self._start_api_server()

        # 启动价格记录器
        self.price_recorder.start()

        print("✅ BTC价格监控已全部启动")
    
    def stop(self):
        """停止所有价格监控"""
        print("⏹️ 停止BTC价格监控...")
        self.running = False
        
        # 停止所有客户端
        for name, client in self.clients.items():
            if hasattr(client, 'stop'):
                client.stop()
                print(f"已停止{name}客户端")

        # 停止价格记录器
        if hasattr(self, 'price_recorder'):
            self.price_recorder.stop()

        print("✅ BTC价格监控已全部停止")
    
    def _start_binance_client(self):
        """启动币安客户端"""
        try:
            binance_client = BinanceClient(self._on_binance_data)
            if binance_client.start():
                self.clients['binance'] = binance_client
                return True
            return False
        except Exception as e:
            print(f"启动币安客户端失败: {e}")
            return False
    
    def _start_backpack_client(self):
        """启动Backpack客户端"""
        try:
            backpack_client = BackpackClient(self._on_backpack_data)
            if backpack_client.start():
                self.clients['backpack'] = backpack_client
                return True
            return False
        except Exception as e:
            print(f"启动Backpack客户端失败: {e}")
            return False
    
    def _start_lighter_client(self):
        """启动Lighter客户端"""
        try:
            # 检查环境变量，允许强制使用特定客户端
            import os
            force_type = os.getenv('LIGHTER_CLIENT_TYPE', '').lower()

            if force_type:
                print(f"🔧 环境变量指定使用: {force_type}")
                lighter_client = create_lighter_client(self._on_lighter_data, headless=self.headless, force_type=force_type, refresh_interval=PAGE_REFRESH_INTERVAL)
            else:
                # 使用智能客户端管理器，自动选择最适合的实现
                lighter_client = create_lighter_client(self._on_lighter_data, headless=self.headless, refresh_interval=PAGE_REFRESH_INTERVAL)

            print(f"🔧 使用{lighter_client.get_client_type()}客户端")

            if lighter_client.start():
                self.clients['lighter'] = lighter_client
                return True
            return False
        except Exception as e:
            print(f"启动Lighter客户端失败: {e}")
            return False
    
    def _start_api_server(self):
        """启动API和WebSocket服务器"""
        def run_socketio():
            self.socketio.run(self.app, host='0.0.0.0', port=8080, debug=False, use_reloader=False)

        self.api_thread = threading.Thread(target=run_socketio, daemon=True)
        self.api_thread.start()

        # 等待服务器启动
        time.sleep(2)
        print("✅ API和WebSocket服务器已启动")
        print("   📊 API接口: http://localhost:8080/api/btc-price")
        print("   🔌 WebSocket: ws://localhost:8080/socket.io/")
    
    def _on_binance_data(self, data: BinanceData):
        """币安数据回调"""
        with self.data_lock:
            self.price_data.binance = data
            self.price_data.timestamp = get_china_time()
            # 更新价格记录器
            self.price_recorder.update_binance_data(data)
    
    def _on_backpack_data(self, data: BackpackData):
        """Backpack数据回调"""
        with self.data_lock:
            self.price_data.backpack = data
            self.price_data.timestamp = get_china_time()
            # 更新价格记录器
            self.price_recorder.update_backpack_data(data)
    
    def _on_lighter_data(self, data: LighterData):
        """Lighter数据回调"""
        with self.data_lock:
            self.price_data.lighter = data
            self.price_data.timestamp = get_china_time()
            # 更新价格记录器
            self.price_recorder.update_lighter_data(data)

            # 🚀 WebSocket实时推送Lighter数据
            if hasattr(self, 'socketio') and data.orderbook:
                lighter_data = {
                    'type': 'lighter_update',
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
                self.socketio.emit('lighter_update', lighter_data)
    
    def get_current_data(self) -> Dict[str, Any]:
        """获取当前价格数据"""
        with self.data_lock:
            return self.price_data.to_dict()

# 主程序入口
def main():
    """主程序入口"""
    print("=== BTC价格监控程序 ===\n")
    
    # 创建监控器实例
    monitor = BTCPriceMonitor(headless=True)  # 默认使用无头模式
    
    try:
        # 启动监控
        monitor.start()
        
        print("\n监控已启动，按 Ctrl+C 停止...")
        print("API接口: http://localhost:8080/api/btc-price")
        
        # 保持程序运行
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n正在停止监控...")
    finally:
        # 确保停止所有客户端
        monitor.stop()
        print("程序已退出")

if __name__ == "__main__":
    main()