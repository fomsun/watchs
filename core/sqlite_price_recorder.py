#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SQLite价格记录器
使用SQLite数据库存储价格数据，替代txt文件
"""

import sqlite3
import threading
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
import pytz

from data.models import BinanceData, BackpackData, LighterData

class SQLitePriceRecorder:
    """SQLite价格记录器"""
    
    def __init__(self, db_path: str = "btc_price_data.db"):
        self.db_path = db_path
        self.data_lock = threading.Lock()
        self.running = False
        self.record_thread = None
        
        # 当前数据
        self.binance_data = None
        self.backpack_data = None
        self.lighter_data = None
        
        # 初始化数据库
        self._init_database()
    
    def _init_database(self):
        """初始化数据库表和索引"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 启用WAL模式提高并发性能
            cursor.execute('PRAGMA journal_mode=WAL')
            cursor.execute('PRAGMA synchronous=NORMAL')
            cursor.execute('PRAGMA cache_size=10000')
            cursor.execute('PRAGMA temp_store=memory')

            # 创建价格记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS price_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    binance_price REAL,
                    backpack_price REAL,
                    lighter_bid REAL,
                    lighter_ask REAL,
                    lighter_mid REAL,
                    lighter_spread REAL,
                    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now'))
                )
            ''')

            # 创建高效索引
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_timestamp_desc
                ON price_records(timestamp DESC)
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_created_at_desc
                ON price_records(created_at DESC)
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_lighter_mid
                ON price_records(lighter_mid) WHERE lighter_mid IS NOT NULL
            ''')

            # 创建复合索引用于时间范围查询
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_timestamp_lighter
                ON price_records(timestamp, lighter_mid) WHERE lighter_mid IS NOT NULL
            ''')

            conn.commit()
            conn.close()
            print(f"✅ SQLite3数据库初始化完成: {self.db_path}")
            print("📈 已启用WAL模式和性能优化")

        except Exception as e:
            print(f"❌ 数据库初始化失败: {e}")
    
    def get_china_time(self):
        """获取中国时间"""
        china_tz = pytz.timezone('Asia/Shanghai')
        return datetime.now(china_tz)
    
    def update_binance_data(self, data: BinanceData):
        """更新币安数据"""
        with self.data_lock:
            self.binance_data = data
    
    def update_backpack_data(self, data: BackpackData):
        """更新Backpack数据"""
        with self.data_lock:
            self.backpack_data = data
    
    def update_lighter_data(self, data: LighterData):
        """更新Lighter数据"""
        with self.data_lock:
            self.lighter_data = data
    
    def _record_current_prices(self):
        """记录当前价格到数据库"""
        with self.data_lock:
            try:
                # 获取中国时间
                china_time = self.get_china_time()
                timestamp_str = china_time.strftime("%Y-%m-%d %H:%M:%S")
                
                # 准备数据
                binance_price = self.binance_data.price if self.binance_data else None
                backpack_price = self.backpack_data.price if self.backpack_data else None
                
                lighter_bid = None
                lighter_ask = None
                lighter_mid = None
                lighter_spread = None
                
                if self.lighter_data and self.lighter_data.orderbook:
                    lighter_bid = self.lighter_data.orderbook.best_bid
                    lighter_ask = self.lighter_data.orderbook.best_ask
                    lighter_mid = self.lighter_data.orderbook.mid_price
                    lighter_spread = self.lighter_data.orderbook.spread
                
                # 插入数据库（使用连接池和事务优化）
                conn = sqlite3.connect(self.db_path, timeout=30.0)
                try:
                    cursor = conn.cursor()

                    cursor.execute('''
                        INSERT INTO price_records
                        (timestamp, binance_price, backpack_price, lighter_bid, lighter_ask, lighter_mid, lighter_spread)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (timestamp_str, binance_price, backpack_price, lighter_bid, lighter_ask, lighter_mid, lighter_spread))

                    conn.commit()
                finally:
                    conn.close()
                
                print(f"💾 价格数据已保存到数据库: {timestamp_str}")

            except Exception as e:
                print(f"❌ 保存价格数据失败: {e}")

    def get_database_info(self) -> Dict[str, Any]:
        """获取数据库信息和性能统计"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=10.0)
            cursor = conn.cursor()

            # 获取数据库大小
            cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
            db_size = cursor.fetchone()[0]

            # 获取记录数
            cursor.execute("SELECT COUNT(*) FROM price_records")
            total_records = cursor.fetchone()[0]

            # 获取索引信息
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='price_records'")
            indexes = [row[0] for row in cursor.fetchall()]

            # 获取最新记录时间
            cursor.execute("SELECT MAX(timestamp) FROM price_records")
            latest_time = cursor.fetchone()[0]

            conn.close()

            return {
                'database_size_bytes': db_size,
                'database_size_mb': round(db_size / 1024 / 1024, 2),
                'total_records': total_records,
                'indexes': indexes,
                'latest_timestamp': latest_time,
                'wal_mode_enabled': True
            }

        except Exception as e:
            print(f"❌ 获取数据库信息失败: {e}")
            return {}
    
    def get_latest_records(self, count: int = 10) -> List[Dict[str, Any]]:
        """获取最新的价格记录（优化版）"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=10.0)
            # 设置行工厂以获得字典结果
            conn.row_factory = sqlite3.Row

            try:
                cursor = conn.cursor()

                cursor.execute('''
                    SELECT timestamp, binance_price, backpack_price,
                           lighter_bid, lighter_ask, lighter_mid, lighter_spread
                    FROM price_records
                    ORDER BY created_at DESC
                    LIMIT ?
                ''', (count,))

                rows = cursor.fetchall()

                # 直接转换为字典列表
                records = [dict(row) for row in rows]
                return records

            finally:
                conn.close()

        except Exception as e:
            print(f"❌ 获取历史记录失败: {e}")
            return []
    
    def get_records_by_time_range(self, start_time: str, end_time: str) -> List[Dict[str, Any]]:
        """根据时间范围获取记录（优化版）"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=10.0)
            conn.row_factory = sqlite3.Row

            try:
                cursor = conn.cursor()

                cursor.execute('''
                    SELECT timestamp, binance_price, backpack_price,
                           lighter_bid, lighter_ask, lighter_mid, lighter_spread
                    FROM price_records
                    WHERE timestamp BETWEEN ? AND ?
                    ORDER BY timestamp ASC
                ''', (start_time, end_time))

                rows = cursor.fetchall()
                records = [dict(row) for row in rows]
                return records

            finally:
                conn.close()

        except Exception as e:
            print(f"❌ 获取时间范围记录失败: {e}")
            return []

    def get_records_from_time(self, start_time: str, count: int = 100) -> List[Dict[str, Any]]:
        """从指定时间开始获取记录"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=10.0)
            conn.row_factory = sqlite3.Row

            try:
                cursor = conn.cursor()

                cursor.execute('''
                    SELECT timestamp, binance_price, backpack_price,
                           lighter_bid, lighter_ask, lighter_mid, lighter_spread
                    FROM price_records
                    WHERE timestamp >= ?
                    ORDER BY timestamp ASC
                    LIMIT ?
                ''', (start_time, count))

                rows = cursor.fetchall()
                records = [dict(row) for row in rows]
                return records

            finally:
                conn.close()

        except Exception as e:
            print(f"❌ 获取指定时间记录失败: {e}")
            return []


    
    def get_record_count(self) -> int:
        """获取记录总数"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM price_records')
            count = cursor.fetchone()[0]
            
            conn.close()
            return count
            
        except Exception as e:
            print(f"❌ 获取记录数量失败: {e}")
            return 0
    
    def cleanup_old_records(self, keep_days: int = 30):
        """清理旧记录，只保留指定天数的数据"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 计算截止时间
            cutoff_time = self.get_china_time().replace(hour=0, minute=0, second=0, microsecond=0)
            cutoff_time = cutoff_time.replace(day=cutoff_time.day - keep_days)
            cutoff_str = cutoff_time.strftime("%Y-%m-%d %H:%M:%S")
            
            cursor.execute('DELETE FROM price_records WHERE timestamp < ?', (cutoff_str,))
            deleted_count = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            if deleted_count > 0:
                print(f"🗑️  清理了 {deleted_count} 条旧记录")
            
        except Exception as e:
            print(f"❌ 清理旧记录失败: {e}")
    
    def _record_loop(self):
        """记录循环"""
        while self.running:
            try:
                self._record_current_prices()
                time.sleep(60)  # 每60秒(1分钟)记录一次
            except Exception as e:
                print(f"❌ 记录循环错误: {e}")
                time.sleep(30)  # 出错时等待30秒
    
    def start(self):
        """启动记录器"""
        if self.running:
            return
        
        self.running = True
        self.record_thread = threading.Thread(target=self._record_loop, daemon=True)
        self.record_thread.start()
        print(f"✅ SQLite3价格记录器已启动 (每60秒保存一次)")
    
    def stop(self):
        """停止记录器"""
        self.running = False
        if self.record_thread:
            self.record_thread.join(timeout=5)
        print("✅ SQLite价格记录器已停止")
