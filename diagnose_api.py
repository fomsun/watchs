#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API诊断脚本
检查服务器上的API问题
"""

import sys
import traceback
import inspect

def diagnose_sqlite_recorder():
    """诊断SQLite记录器"""
    print("=== SQLite记录器诊断 ===")
    
    try:
        from core.sqlite_price_recorder import SQLitePriceRecorder
        
        # 检查类方法
        methods = [method for method in dir(SQLitePriceRecorder) if not method.startswith('_')]
        print(f"✅ SQLitePriceRecorder类加载成功")
        print(f"📋 可用方法: {methods}")
        
        # 检查关键方法是否存在
        required_methods = ['get_latest_records', 'get_records_by_time_range', 'get_records_from_time']
        for method in required_methods:
            if hasattr(SQLitePriceRecorder, method):
                print(f"✅ 方法存在: {method}")
                # 检查方法签名
                sig = inspect.signature(getattr(SQLitePriceRecorder, method))
                print(f"   签名: {method}{sig}")
            else:
                print(f"❌ 方法缺失: {method}")
        
        # 尝试实例化
        recorder = SQLitePriceRecorder("test_diagnose.db")
        print(f"✅ 实例化成功")
        
        # 测试方法调用
        print("\n=== 方法调用测试 ===")
        
        # 测试get_latest_records
        try:
            result = recorder.get_latest_records(1)
            print(f"✅ get_latest_records: 返回 {len(result)} 条记录")
            print(f"   类型: {type(result)}")
            if result:
                print(f"   第一条记录类型: {type(result[0])}")
                print(f"   第一条记录: {result[0]}")
        except Exception as e:
            print(f"❌ get_latest_records 失败: {e}")
            traceback.print_exc()
        
        # 测试get_records_from_time
        try:
            result = recorder.get_records_from_time("2025-07-03 00:00:00", 1)
            print(f"✅ get_records_from_time: 返回 {len(result)} 条记录")
            print(f"   类型: {type(result)}")
            if result:
                print(f"   第一条记录类型: {type(result[0])}")
                print(f"   第一条记录: {result[0]}")
        except Exception as e:
            print(f"❌ get_records_from_time 失败: {e}")
            traceback.print_exc()
        
        # 测试get_records_by_time_range
        try:
            result = recorder.get_records_by_time_range("2025-07-03 00:00:00", "2025-07-03 23:59:59")
            print(f"✅ get_records_by_time_range: 返回 {len(result)} 条记录")
            print(f"   类型: {type(result)}")
            if result:
                print(f"   第一条记录类型: {type(result[0])}")
                print(f"   第一条记录: {result[0]}")
        except Exception as e:
            print(f"❌ get_records_by_time_range 失败: {e}")
            traceback.print_exc()
            
    except ImportError as e:
        print(f"❌ 导入SQLitePriceRecorder失败: {e}")
        traceback.print_exc()
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        traceback.print_exc()

def diagnose_api_route():
    """诊断API路由"""
    print("\n=== API路由诊断 ===")
    
    try:
        # 模拟API调用
        from core.sqlite_price_recorder import SQLitePriceRecorder
        
        recorder = SQLitePriceRecorder("btc_price_data.db")
        
        # 模拟不同的查询参数
        test_cases = [
            {"count": 5},
            {"start_time": "2025-07-03 10:00:00", "end_time": "2025-07-03 20:00:00"},
            {"start_time": "2025-07-03 15:00:00", "count": 3}
        ]
        
        for i, params in enumerate(test_cases, 1):
            print(f"\n测试用例 {i}: {params}")
            
            try:
                # 模拟API逻辑
                count = params.get('count', 100)
                start_time = params.get('start_time')
                end_time = params.get('end_time')
                
                count = min(count, 1000)
                
                if start_time and end_time:
                    records = recorder.get_records_by_time_range(start_time, end_time)
                    query_type = 'time_range'
                elif start_time:
                    records = recorder.get_records_from_time(start_time, count)
                    query_type = 'from_time'
                else:
                    records = recorder.get_latest_records(count)
                    query_type = 'latest'
                
                result = {
                    'count': len(records),
                    'query_type': query_type,
                    'query_params': params,
                    'data': records,
                    'source': 'sqlite_database'
                }
                
                print(f"✅ 测试成功: {query_type}, 返回 {len(records)} 条记录")
                
            except Exception as e:
                print(f"❌ 测试失败: {e}")
                traceback.print_exc()
                
    except Exception as e:
        print(f"❌ API路由诊断失败: {e}")
        traceback.print_exc()

def main():
    """主函数"""
    print("🔍 API问题诊断工具")
    print("=" * 50)
    
    diagnose_sqlite_recorder()
    diagnose_api_route()
    
    print("\n" + "=" * 50)
    print("🎯 诊断完成！")
    print("如果看到错误，请将完整输出发送给开发者")

if __name__ == "__main__":
    main()
