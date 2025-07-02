#!/usr/bin/env python3
"""
币安数据客户端
"""

import json
import threading
import websocket
from datetime import datetime
from typing import Callable, Optional

from data.models import BinanceData

class BinanceClient:
    """币安数据客户端 - 使用WebSocket实时推送"""

    def __init__(self, on_data_callback: Callable[[BinanceData], None], symbol: str = "BTCUSDC"):
        """
        初始化币安客户端

        Args:
            on_data_callback: 数据回调函数
            symbol: 交易对符号
        """
        self.on_data_callback = on_data_callback
        self.symbol = symbol
        self.data = BinanceData(symbol=symbol)
        self.running = False
        self.ws = None
        self.ws_thread = None
        # 币安期货WebSocket URL
        self.ws_url = f"wss://fstream.binance.com/ws/{symbol.lower()}@ticker"
    
    def start(self):
        """启动币安WebSocket连接"""
        try:
            print(f"🔷 启动币安永续合约{self.symbol}价格监控 (WebSocket)...")

            self.running = True

            # 创建WebSocket连接
            self.ws = websocket.WebSocketApp(
                self.ws_url,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close,
                on_open=self._on_open
            )

            # 启动WebSocket线程
            self.ws_thread = threading.Thread(target=self.ws.run_forever, daemon=True)
            self.ws_thread.start()

            print(f"✅ 币安永续合约{self.symbol}价格监控已启动 (WebSocket)")
            return True

        except Exception as e:
            print(f"❌ 币安WebSocket连接失败: {e}")
            return False
    
    def stop(self):
        """停止币安WebSocket连接"""
        self.running = False
        if self.ws:
            self.ws.close()
        print("✅ 币安价格监控已停止")
    
    def _on_open(self, ws):
        """WebSocket连接打开回调"""
        print(f"🔗 币安WebSocket连接已建立: {self.symbol}")

    def _on_message(self, ws, message):
        """WebSocket消息回调"""
        try:
            data = json.loads(message)

            # 获取最新价格 (c字段是lastPrice)
            price = float(data.get('c', 0))

            self.data.price = price
            self.data.timestamp = datetime.now()

            print(f"币安永续合约{self.symbol}价格更新: ${price:.1f}")

            # 调用回调函数
            if self.on_data_callback:
                self.on_data_callback(self.data)

        except Exception as e:
            print(f"币安WebSocket消息处理错误: {e}")

    def _on_error(self, ws, error):
        """WebSocket错误回调"""
        print(f"❌ 币安WebSocket错误: {error}")

    def _on_close(self, ws, close_status_code, close_msg):
        """WebSocket连接关闭回调"""
        print(f"🔌 币安WebSocket连接已关闭: {close_status_code} - {close_msg}")

        # 如果还在运行状态，尝试重连
        if self.running:
            print("🔄 尝试重新连接币安WebSocket...")
            import time
            time.sleep(5)  # 等待5秒后重连
            if self.running:
                self.start()
    
    def get_current_data(self) -> BinanceData:
        """获取当前数据"""
        return self.data

# 测试函数
def test_binance_client():
    """测试币安客户端"""
    import time

    def on_data(data: BinanceData):
        print(f"币安 - {data.symbol}: ${data.price:,.2f}")

    client = BinanceClient(on_data)

    try:
        if client.start():
            print("按 Ctrl+C 停止...")
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        print("\n停止测试...")
    finally:
        client.stop()

if __name__ == "__main__":
    test_binance_client()