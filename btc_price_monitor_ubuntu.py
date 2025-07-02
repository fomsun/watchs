#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
BTC价格监控程序 - Ubuntu优化版
专门针对Ubuntu服务器环境优化
"""

import signal
import sys
import threading
import time
import platform
from datetime import datetime
from flask import Flask, jsonify, request

# 导入核心模块
from core.binance_client import BinanceClient
from core.backpack_client import BackpackClient
from core.price_recorder import PriceRecorder
from data.models import BinanceData, BackpackData, LighterData, PriceData

# 使用标准Lighter管理器（伪装问题已解决）
from core.lighter_manager import create_lighter_client

class BTCPriceMonitorUbuntu:
    """BTC价格监控程序 - Ubuntu优化版"""
    
    def __init__(self):
        """初始化监控程序"""
        print("=== BTC价格监控程序 (Ubuntu优化版) ===")
        print(f"系统: {platform.system()} {platform.release()}")
        
        # 数据存储
        self.price_data = PriceData()
        self.data_lock = threading.Lock()
        
        # 客户端字典
        self.clients = {}
        
        # 初始化客户端
        self.binance_client = BinanceClient(self._on_binance_data)
        self.backpack_client = BackpackClient(self._on_backpack_data)
        
        # 使用智能Lighter客户端管理器（伪装问题已解决）
        print("🎭 Ubuntu系统使用DrissionPage客户端（已解决伪装问题）")
        self.lighter_client = create_lighter_client(self._on_lighter_data, headless=True)
        
        self.clients = {
            "币安": self.binance_client,
            "Backpack": self.backpack_client,
            "Lighter": self.lighter_client
        }
        
        # 初始化API服务器
        self.app = Flask(__name__)
        self.setup_routes()
        self.api_thread = None
        
        # 初始化价格记录器
        self.price_recorder = PriceRecorder("btc_price_data_ubuntu.txt")
    
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
                format_type = request.args.get('format', 'json')
                
                # 处理count参数
                if count_param is None:
                    count = None
                else:
                    count = min(int(count_param), 1000)
                
                # 获取历史记录
                records = self.price_recorder.get_latest_records(count)
                
                if format_type == 'raw':
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
                            parts = record.split('-')
                            if len(parts) >= 4:
                                binance_part = parts[0].split(':')
                                backpack_part = parts[1].split(':')
                                lighter_part = parts[2].split(':')
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
                        except (ValueError, IndexError):
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
        
        @self.app.route('/api/system/status', methods=['GET'])
        def get_system_status():
            """获取系统状态"""
            return jsonify({
                "system": f"{platform.system()} {platform.release()}",
                "python": sys.version,
                "clients": {
                    name: client.is_connected() if hasattr(client, 'is_connected') else True
                    for name, client in self.clients.items()
                },
                "masquerade_enabled": True,
                "timestamp": datetime.now().isoformat()
            })
    
    def start(self):
        """启动监控程序"""
        print("\n🚀 启动Ubuntu BTC价格监控...")
        
        # 启动各个客户端
        for name, client in self.clients.items():
            try:
                print(f"🔷 启动{name}客户端...")
                if hasattr(client, 'start'):
                    success = client.start()
                    if success:
                        print(f"✅ {name}客户端启动成功")
                    else:
                        print(f"❌ {name}客户端启动失败")
                else:
                    print(f"⚠️  {name}客户端无start方法")
            except Exception as e:
                print(f"❌ {name}客户端启动异常: {e}")
        
        # 启动API服务器
        self._start_api_server()
        
        # 启动价格记录器
        self.price_recorder.start()
        
        print("✅ Ubuntu BTC价格监控已全部启动")
        print(f"\n监控已启动，按 Ctrl+C 停止...")
        print(f"API接口: http://localhost:8080/api/btc-price")
        print(f"系统状态: http://localhost:8080/api/system/status")
        print(f"历史数据: http://localhost:8080/api/btc-price/history")
    
    def stop(self):
        """停止监控程序"""
        print("\n🛑 停止Ubuntu BTC价格监控...")
        
        # 停止所有客户端
        for name, client in self.clients.items():
            if hasattr(client, 'stop'):
                client.stop()
                print(f"已停止{name}客户端")
        
        # 停止价格记录器
        if hasattr(self, 'price_recorder'):
            self.price_recorder.stop()
        
        print("✅ Ubuntu BTC价格监控已全部停止")
    
    def _start_api_server(self):
        """启动API服务器"""
        def run_server():
            self.app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)
        
        self.api_thread = threading.Thread(target=run_server, daemon=True)
        self.api_thread.start()
        
        # 等待服务器启动
        time.sleep(2)
        print("✅ API服务器已启动 - http://localhost:8080/api/btc-price")
    
    def _on_binance_data(self, data: BinanceData):
        """币安数据回调"""
        with self.data_lock:
            self.price_data.binance = data
            self.price_data.timestamp = datetime.now()
            self.price_recorder.update_binance_data(data)
    
    def _on_backpack_data(self, data: BackpackData):
        """Backpack数据回调"""
        with self.data_lock:
            self.price_data.backpack = data
            self.price_data.timestamp = datetime.now()
            self.price_recorder.update_backpack_data(data)
    
    def _on_lighter_data(self, data: LighterData):
        """Lighter数据回调"""
        with self.data_lock:
            self.price_data.lighter = data
            self.price_data.timestamp = datetime.now()
            self.price_recorder.update_lighter_data(data)

def signal_handler(signum, frame):
    """信号处理器"""
    print(f"\n收到信号 {signum}，正在停止程序...")
    if 'monitor' in globals():
        monitor.stop()
    sys.exit(0)

def main():
    """主函数"""
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 创建并启动监控程序
    global monitor
    monitor = BTCPriceMonitorUbuntu()
    monitor.start()
    
    # 保持程序运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        monitor.stop()

if __name__ == "__main__":
    main()
