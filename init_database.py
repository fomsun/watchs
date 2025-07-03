#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据库初始化工具
创建SQLite数据库表结构和完整索引，用于迁移前的准备
"""

import sqlite3
import os

def init_database(db_file="btc_price_data.db"):
    """初始化数据库表和索引"""
    try:
        print(f"🚀 初始化数据库: {db_file}")
        
        # 如果数据库文件已存在，询问是否覆盖
        if os.path.exists(db_file):
            print(f"⚠️  数据库文件已存在: {db_file}")
            choice = input("是否继续初始化？(会保留现有数据) (y/n): ").lower().strip()
            if choice not in ['y', 'yes', '是']:
                print("❌ 初始化已取消")
                return False
        
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        print("⚙️  配置数据库性能参数...")
        # 启用WAL模式提高并发性能
        cursor.execute('PRAGMA journal_mode=WAL')
        cursor.execute('PRAGMA synchronous=NORMAL')
        cursor.execute('PRAGMA cache_size=10000')
        cursor.execute('PRAGMA temp_store=memory')
        cursor.execute('PRAGMA mmap_size=268435456')  # 256MB内存映射
        
        print("📋 创建数据表...")
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
        
        print("🔍 创建索引...")
        # 主要查询索引 - 时间戳降序（最常用）
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp_desc 
            ON price_records(timestamp DESC)
        ''')
        
        # 创建时间降序索引
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_created_at_desc 
            ON price_records(created_at DESC)
        ''')
        
        # Lighter价格索引（只对非空值建索引）
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_lighter_mid 
            ON price_records(lighter_mid) WHERE lighter_mid IS NOT NULL
        ''')
        
        # 复合索引用于时间范围查询
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp_lighter 
            ON price_records(timestamp, lighter_mid) WHERE lighter_mid IS NOT NULL
        ''')
        
        # 时间范围查询优化索引
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp_asc 
            ON price_records(timestamp ASC)
        ''')
        
        # 币安价格索引
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_binance_price 
            ON price_records(binance_price) WHERE binance_price IS NOT NULL
        ''')
        
        # Backpack价格索引
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_backpack_price 
            ON price_records(backpack_price) WHERE backpack_price IS NOT NULL
        ''')
        
        # 复合索引用于多字段查询
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp_all_prices 
            ON price_records(timestamp, binance_price, backpack_price, lighter_mid)
        ''')
        
        # 日期查询索引（用于按日期查询）
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_date 
            ON price_records(substr(timestamp, 1, 10))
        ''')
        
        print("📊 验证表结构...")
        # 验证表结构
        cursor.execute("PRAGMA table_info(price_records)")
        columns = cursor.fetchall()
        print("   表字段:")
        for col in columns:
            print(f"     {col[1]} ({col[2]})")
        
        print("📈 验证索引...")
        # 验证索引
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='price_records'")
        indexes = cursor.fetchall()
        print(f"   创建了 {len(indexes)} 个索引:")
        for idx in indexes:
            print(f"     {idx[0]}")
        
        # 获取数据库统计信息
        cursor.execute("SELECT COUNT(*) FROM price_records")
        record_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
        db_size = cursor.fetchone()[0]
        
        conn.commit()
        conn.close()
        
        print(f"✅ SQLite3数据库初始化完成!")
        print(f"   📁 数据库文件: {db_file}")
        print(f"   📊 现有记录数: {record_count}")
        print(f"   💾 数据库大小: {db_size / 1024 / 1024:.2f} MB")
        print(f"   🚀 WAL模式: 已启用")
        print(f"   🔍 索引数量: {len(indexes)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        return False

def show_database_info(db_file="btc_price_data.db"):
    """显示数据库信息"""
    try:
        if not os.path.exists(db_file):
            print(f"❌ 数据库文件不存在: {db_file}")
            return
        
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        print(f"📊 数据库信息: {db_file}")
        print("=" * 50)
        
        # 记录数
        cursor.execute("SELECT COUNT(*) FROM price_records")
        total_records = cursor.fetchone()[0]
        print(f"总记录数: {total_records:,}")
        
        # 数据库大小
        cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
        db_size = cursor.fetchone()[0]
        print(f"数据库大小: {db_size / 1024 / 1024:.2f} MB")
        
        # 时间范围
        if total_records > 0:
            cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM price_records")
            min_time, max_time = cursor.fetchone()
            print(f"时间范围: {min_time} 到 {max_time}")
        
        # 索引信息
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='price_records'")
        indexes = cursor.fetchall()
        print(f"索引数量: {len(indexes)}")
        
        # WAL模式
        cursor.execute("PRAGMA journal_mode")
        journal_mode = cursor.fetchone()[0]
        print(f"日志模式: {journal_mode}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 获取数据库信息失败: {e}")

def main():
    """主函数"""
    print("=== SQLite数据库初始化工具 ===")
    print("创建数据库表结构和完整索引，为数据迁移做准备")
    print("")
    
    db_file = "btc_price_data.db"
    
    if len(os.sys.argv) > 1:
        command = os.sys.argv[1].lower()
        if command == 'info':
            show_database_info(db_file)
            return
        elif command == 'help':
            print("用法:")
            print("  python3 init_database.py        # 初始化数据库")
            print("  python3 init_database.py info   # 显示数据库信息")
            print("  python3 init_database.py help   # 显示帮助")
            return
    
    # 初始化数据库
    if init_database(db_file):
        print("\n🎉 数据库初始化完成!")
        print("现在可以运行:")
        print("  python3 migrate_txt_to_sqlite.py  # 迁移历史数据")
        print("  python3 btc_price_monitor.py      # 启动主程序")
        print("  python3 init_database.py info     # 查看数据库信息")

if __name__ == "__main__":
    import sys
    main()
