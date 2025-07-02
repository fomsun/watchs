#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
连接状态监控脚本
实时监控Lighter客户端的连接状态和数据流
"""

import time
import threading
from datetime import datetime
from core.lighter_client import LighterClient
from data.models import LighterData

class ConnectionMonitor:
    """连接状态监控器"""
    
    def __init__(self):
        self.last_data_time = None
        self.data_count = 0
        self.error_count = 0
        self.reconnect_count = 0
        self.running = True
        self.client = None
        
    def on_data_callback(self, data: LighterData):
        """数据回调函数"""
        self.last_data_time = datetime.now()
        self.data_count += 1
        
        if data.orderbook:
            print(f"📊 [{self.last_data_time.strftime('%H:%M:%S')}] 数据正常: 买一=${data.orderbook.best_bid:.1f}, 卖一=${data.orderbook.best_ask:.1f}")
        else:
            print(f"⚠️  [{self.last_data_time.strftime('%H:%M:%S')}] 数据为空")
            self.error_count += 1
    
    def start_monitoring(self):
        """开始监控"""
        print("=== Lighter连接状态监控 ===")
        print("实时监控连接状态和数据流")
        print("")
        
        # 创建客户端
        self.client = LighterClient(self.on_data_callback, headless=True, refresh_interval=300)
        
        try:
            # 启动客户端
            if self.client.start():
                print("✅ 监控客户端启动成功")
                print("🎯 开始监控连接状态...")
                print("")
                
                # 启动状态监控线程
                monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
                monitor_thread.start()
                
                # 主循环
                while self.running:
                    time.sleep(1)
                    
            else:
                print("❌ 监控客户端启动失败")
        
        except KeyboardInterrupt:
            print("\n⏹️ 用户停止监控")
        
        finally:
            self.running = False
            if self.client:
                self.client.stop()
            print("🔚 监控已停止")
    
    def _monitor_loop(self):
        """监控循环"""
        while self.running:
            try:
                current_time = datetime.now()
                
                # 检查数据流状态
                if self.last_data_time:
                    time_since_last = (current_time - self.last_data_time).total_seconds()
                    
                    if time_since_last > 30:  # 30秒没有数据
                        print(f"⚠️  [{current_time.strftime('%H:%M:%S')}] 警告: {time_since_last:.0f}秒未收到数据")
                    
                    # 检查连接状态
                    if self.client and hasattr(self.client, '_check_page_connection'):
                        try:
                            is_connected = self.client._check_page_connection()
                            if not is_connected:
                                print(f"🔌 [{current_time.strftime('%H:%M:%S')}] 检测到连接断开")
                                self.reconnect_count += 1
                        except Exception as e:
                            print(f"❌ [{current_time.strftime('%H:%M:%S')}] 连接检查失败: {e}")
                
                # 每分钟显示统计信息
                if current_time.second == 0:
                    self._print_statistics(current_time)
                
                time.sleep(10)  # 每10秒检查一次
                
            except Exception as e:
                print(f"❌ 监控循环错误: {e}")
                time.sleep(5)
    
    def _print_statistics(self, current_time):
        """打印统计信息"""
        print(f"\n📈 [{current_time.strftime('%H:%M:%S')}] 连接统计:")
        print(f"   📊 数据接收次数: {self.data_count}")
        print(f"   ❌ 错误次数: {self.error_count}")
        print(f"   🔌 重连次数: {self.reconnect_count}")
        
        if self.last_data_time:
            time_since_last = (current_time - self.last_data_time).total_seconds()
            print(f"   ⏰ 最后数据: {time_since_last:.0f}秒前")
        else:
            print(f"   ⏰ 最后数据: 无")
        
        # 连接状态
        if self.client:
            try:
                is_connected = self.client.is_connected()
                status = "✅ 正常" if is_connected else "❌ 断开"
                print(f"   🔗 连接状态: {status}")
            except:
                print(f"   🔗 连接状态: ❓ 未知")
        
        print("-" * 50)

def main():
    """主函数"""
    monitor = ConnectionMonitor()
    monitor.start_monitoring()

if __name__ == "__main__":
    main()
