#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
txt数据迁移工具
将btc_price_data.txt中的历史数据迁移到SQLite数据库
每分钟只保存一条数据，避免重复
"""

import sqlite3
import re
from datetime import datetime, timedelta
from collections import defaultdict
import pytz

def parse_txt_line(line):
    """解析txt文件中的一行数据"""
    try:
        # 格式: 币安:109379.0-Backpack:109323.9-Lighter:109352.2-2025-07-03 02:37:59
        line = line.strip()
        if not line:
            return None
        
        # 分割数据
        parts = line.split('-')
        if len(parts) < 4:
            return None
        
        # 解析价格数据
        binance_price = None
        backpack_price = None
        lighter_price = None
        
        for part in parts[:-1]:  # 最后一部分是时间戳
            if part.startswith('币安:'):
                try:
                    binance_price = float(part.split(':')[1])
                except:
                    pass
            elif part.startswith('Backpack:'):
                try:
                    backpack_price = float(part.split(':')[1])
                except:
                    pass
            elif part.startswith('Lighter:'):
                try:
                    lighter_price = float(part.split(':')[1])
                except:
                    pass
        
        # 解析时间戳 - 处理可能的格式问题
        timestamp_str = parts[-1].strip()
        
        # 如果时间戳格式不完整，尝试修复
        if len(timestamp_str.split()) == 2 and not timestamp_str.startswith('20'):
            # 格式可能是 "03 02:01:13"，需要添加年月
            time_parts = timestamp_str.split()
            if len(time_parts) == 2:
                day_part = time_parts[0]
                time_part = time_parts[1]
                # 假设是2025年7月
                timestamp_str = f"2025-07-{day_part.zfill(2)} {time_part}"
        
        return {
            'timestamp': timestamp_str,
            'binance_price': binance_price,
            'backpack_price': backpack_price,
            'lighter_price': lighter_price
        }
        
    except Exception as e:
        print(f"解析行失败: {line[:50]}... 错误: {e}")
        return None

def group_by_minute(records):
    """按分钟分组数据，每分钟只保留一条"""
    grouped = defaultdict(list)
    
    for record in records:
        if not record:
            continue
        
        try:
            # 解析时间戳，提取到分钟级别
            timestamp = datetime.strptime(record['timestamp'], '%Y-%m-%d %H:%M:%S')
            minute_key = timestamp.strftime('%Y-%m-%d %H:%M:00')  # 秒数设为00
            grouped[minute_key].append(record)
        except Exception as e:
            print(f"时间解析失败: {record['timestamp']} 错误: {e}")
            continue
    
    # 每分钟选择一条记录（选择最后一条，通常是最新的）
    result = []
    for minute_key, minute_records in grouped.items():
        if minute_records:
            # 选择该分钟内的最后一条记录
            selected_record = minute_records[-1]
            selected_record['timestamp'] = minute_key  # 统一时间戳格式
            result.append(selected_record)
    
    # 按时间排序
    result.sort(key=lambda x: x['timestamp'])
    return result

def migrate_to_sqlite(txt_file, db_file):
    """迁移数据到SQLite"""
    print(f"🚀 开始迁移数据: {txt_file} -> {db_file}")
    
    # 读取txt文件
    try:
        with open(txt_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        print(f"📖 读取到 {len(lines)} 行数据")
    except FileNotFoundError:
        print(f"❌ 文件不存在: {txt_file}")
        return
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return
    
    # 解析数据
    print("🔍 解析数据中...")
    records = []
    for i, line in enumerate(lines):
        record = parse_txt_line(line)
        if record:
            records.append(record)
        
        if (i + 1) % 1000 == 0:
            print(f"   已处理 {i + 1} 行...")
    
    print(f"✅ 成功解析 {len(records)} 条记录")
    
    # 按分钟分组
    print("📊 按分钟分组数据...")
    minute_records = group_by_minute(records)
    print(f"✅ 分组后得到 {len(minute_records)} 条分钟级数据")
    
    # 连接数据库
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='price_records'")
        if not cursor.fetchone():
            print("❌ 数据库表不存在，请先运行主程序初始化数据库")
            conn.close()
            return
        
        # 插入数据
        print("💾 插入数据到SQLite...")
        inserted_count = 0
        skipped_count = 0
        
        for record in minute_records:
            try:
                # 检查是否已存在
                cursor.execute("SELECT id FROM price_records WHERE timestamp = ?", (record['timestamp'],))
                if cursor.fetchone():
                    skipped_count += 1
                    continue
                
                # 插入新记录
                cursor.execute('''
                    INSERT INTO price_records 
                    (timestamp, binance_price, backpack_price, lighter_mid)
                    VALUES (?, ?, ?, ?)
                ''', (
                    record['timestamp'],
                    record['binance_price'],
                    record['backpack_price'],
                    record['lighter_price']
                ))
                
                inserted_count += 1
                
                if inserted_count % 100 == 0:
                    print(f"   已插入 {inserted_count} 条...")
                    
            except Exception as e:
                print(f"插入记录失败: {record} 错误: {e}")
        
        conn.commit()
        conn.close()
        
        print(f"✅ 迁移完成!")
        print(f"   📊 插入新记录: {inserted_count} 条")
        print(f"   ⏭️  跳过重复记录: {skipped_count} 条")
        print(f"   📈 总处理记录: {len(minute_records)} 条")
        
    except Exception as e:
        print(f"❌ 数据库操作失败: {e}")

def main():
    """主函数"""
    print("=== txt数据迁移到SQLite工具 ===")
    print("将btc_price_data.txt中的历史数据迁移到SQLite数据库")
    print("每分钟只保存一条数据，避免数据冗余")
    print("")
    
    txt_file = "btc_price_data.txt"
    db_file = "btc_price_data.db"
    
    # 检查文件是否存在
    try:
        with open(txt_file, 'r') as f:
            pass
    except FileNotFoundError:
        print(f"❌ 找不到txt文件: {txt_file}")
        print("请确保文件存在后再运行迁移")
        return
    
    # 确认迁移
    print(f"源文件: {txt_file}")
    print(f"目标数据库: {db_file}")
    print("")
    
    confirm = input("确认开始迁移吗？(y/n): ").lower().strip()
    if confirm not in ['y', 'yes', '是']:
        print("❌ 迁移已取消")
        return
    
    # 开始迁移
    migrate_to_sqlite(txt_file, db_file)
    
    print("\n🎉 迁移工具运行完成!")
    print("现在可以删除txt文件，使用SQLite数据库了")

if __name__ == "__main__":
    main()
