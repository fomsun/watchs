#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
价格记录器 - 定期保存价格数据到本地文件
"""

import os
import threading
import time
from datetime import datetime
from typing import Optional
from data.models import BinanceData, BackpackData, LighterData


class PriceRecorder:
    """价格记录器 - 每10秒保存一次价格数据"""
    
    def __init__(self, file_path: str = "price_data.txt"):
        """
        初始化价格记录器
        
        Args:
            file_path: 保存文件路径
        """
        self.file_path = file_path
        self.running = False
        self.record_thread = None
        
        # 价格数据存储
        self.binance_data: Optional[BinanceData] = None
        self.backpack_data: Optional[BackpackData] = None
        self.lighter_data: Optional[LighterData] = None
        
        # 数据锁
        self.data_lock = threading.Lock()
        
        # 确保数据目录存在
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        
        # 创建文件头部（如果文件不存在）
        if not os.path.exists(file_path):
            self._write_header()
    
    def _write_header(self):
        """写入文件头部"""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                f.write("# BTC价格监控数据记录\n")
                f.write("# 格式: 币安价格-Backpack价格-Lighter价格-时间\n")
                f.write("# 记录间隔: 10秒\n")
                f.write("# 开始时间: {}\n".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                f.write("-" * 80 + "\n")
        except Exception as e:
            print(f"❌ 创建价格记录文件失败: {e}")
    
    def update_binance_data(self, data: BinanceData):
        """更新币安价格数据"""
        with self.data_lock:
            self.binance_data = data
    
    def update_backpack_data(self, data: BackpackData):
        """更新Backpack价格数据"""
        with self.data_lock:
            self.backpack_data = data
    
    def update_lighter_data(self, data: LighterData):
        """更新Lighter价格数据"""
        with self.data_lock:
            self.lighter_data = data
    
    def start(self):
        """启动价格记录"""
        if self.running:
            return
        
        print(f"🔷 启动价格记录器 - 文件: {self.file_path}")
        self.running = True
        
        # 启动记录线程
        self.record_thread = threading.Thread(target=self._record_loop, daemon=True)
        self.record_thread.start()
        
        print("✅ 价格记录器已启动 (每10秒保存一次)")
    
    def stop(self):
        """停止价格记录"""
        self.running = False
        print("✅ 价格记录器已停止")
    
    def _record_loop(self):
        """价格记录循环"""
        while self.running:
            try:
                # 等待10秒
                time.sleep(10)
                
                if not self.running:
                    break
                
                # 记录当前价格
                self._record_current_prices()
                
            except Exception as e:
                print(f"❌ 价格记录错误: {e}")
                time.sleep(5)  # 出错时等待5秒再重试
    
    def _record_current_prices(self):
        """记录当前价格数据"""
        with self.data_lock:
            # 获取当前时间
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 获取各交易所价格
            binance_price = f"币安:{self.binance_data.price:.1f}" if self.binance_data else "币安:N/A"
            backpack_price = f"Backpack:{self.backpack_data.price:.1f}" if self.backpack_data else "Backpack:N/A"
            
            # Lighter价格使用中间价 (买一+卖一)/2
            if self.lighter_data and self.lighter_data.connected and self.lighter_data.orderbook:
                mid_price = (self.lighter_data.orderbook.best_bid + self.lighter_data.orderbook.best_ask) / 2
                lighter_price = f"Lighter:{mid_price:.1f}"
            else:
                lighter_price = "Lighter:N/A"
            
            # 构建记录行
            record_line = f"{binance_price}-{backpack_price}-{lighter_price}-{current_time}\n"
            
            # 写入文件
            try:
                with open(self.file_path, 'a', encoding='utf-8') as f:
                    f.write(record_line)
                
                print(f"💾 价格已保存: {binance_price} | {backpack_price} | {lighter_price} | {current_time}")
                
            except Exception as e:
                print(f"❌ 写入价格记录失败: {e}")
    
    def get_latest_records(self, count: int = None) -> list:
        """获取最新的记录"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # 过滤掉注释行和空行
            data_lines = [line.strip() for line in lines if line.strip() and not line.startswith('#') and not line.startswith('-')]

            # 如果count为None，返回所有记录；否则返回最新的count条记录
            if count is None:
                return data_lines
            else:
                return data_lines[-count:] if data_lines else []

        except Exception as e:
            print(f"❌ 读取价格记录失败: {e}")
            return []


# 测试函数
def test_price_recorder():
    """测试价格记录器"""
    from data.models import BinanceData, BackpackData, LighterData
    
    recorder = PriceRecorder("test_price_data.txt")
    
    try:
        recorder.start()
        
        # 模拟价格数据更新
        for i in range(5):
            # 模拟币安数据
            binance_data = BinanceData(symbol="BTCUSDC")
            binance_data.price = 109500.0 + i * 10
            binance_data.timestamp = datetime.now()
            recorder.update_binance_data(binance_data)
            
            # 模拟Backpack数据
            backpack_data = BackpackData(symbol="BTC_USDC_PERP")
            backpack_data.price = 109480.0 + i * 10
            backpack_data.timestamp = datetime.now()
            recorder.update_backpack_data(backpack_data)
            
            # 模拟Lighter数据
            lighter_data = LighterData()
            lighter_data.best_bid = 109490.0 + i * 10
            lighter_data.best_ask = 109510.0 + i * 10
            lighter_data.mid_price = (lighter_data.best_bid + lighter_data.best_ask) / 2
            lighter_data.connected = True
            lighter_data.timestamp = datetime.now()
            recorder.update_lighter_data(lighter_data)
            
            print(f"第{i+1}次更新价格数据")
            time.sleep(12)  # 等待12秒，确保记录器记录数据
        
        # 显示最新记录
        print("\n最新记录:")
        records = recorder.get_latest_records(5)
        for record in records:
            print(record)
            
    except KeyboardInterrupt:
        print("\n停止测试...")
    finally:
        recorder.stop()


if __name__ == "__main__":
    test_price_recorder()
