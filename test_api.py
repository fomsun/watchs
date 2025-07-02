#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试API接口
"""

import requests
import json
import time

def test_api():
    """测试API接口"""
    print("=== API接口测试 ===")
    
    base_url = "http://localhost:8080"
    
    try:
        # 1. 测试实时价格接口
        print("\n1. 测试实时价格接口...")
        response = requests.get(f"{base_url}/api/btc-price", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ 实时价格接口正常")
            print(f"   币安价格: ${data.get('binance', {}).get('price', 'N/A')}")
            print(f"   Backpack价格: ${data.get('backpack', {}).get('price', 'N/A')}")
            print(f"   Lighter中间价: ${data.get('lighter', {}).get('mid_price', 'N/A')}")
            print(f"   时间戳: {data.get('timestamp', 'N/A')}")
        else:
            print(f"❌ 实时价格接口失败: {response.status_code}")
    
    except Exception as e:
        print(f"❌ 实时价格接口错误: {e}")
    
    try:
        # 2. 测试历史记录接口 (JSON格式)
        print("\n2. 测试历史记录接口 (JSON格式)...")
        response = requests.get(f"{base_url}/api/btc-price/history?count=3", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ 历史记录接口 (JSON) 正常")
            print(f"   记录数量: {data.get('count', 0)}")
            print(f"   格式: {data.get('format', 'unknown')}")
            
            records = data.get('data', [])
            for i, record in enumerate(records[:2]):
                print(f"   记录{i+1}: {record.get('timestamp', 'N/A')}")
                print(f"     币安: ${record.get('binance', {}).get('price', 'N/A')}")
                print(f"     Lighter: ${record.get('lighter', {}).get('price', 'N/A')}")
        else:
            print(f"❌ 历史记录接口失败: {response.status_code}")
    
    except Exception as e:
        print(f"❌ 历史记录接口错误: {e}")
    
    try:
        # 3. 测试历史记录接口 (原始格式)
        print("\n3. 测试历史记录接口 (原始格式)...")
        response = requests.get(f"{base_url}/api/btc-price/history?count=2&format=raw", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ 历史记录接口 (原始) 正常")
            print(f"   记录数量: {data.get('count', 0)}")
            print(f"   格式: {data.get('format', 'unknown')}")
            
            records = data.get('data', [])
            for i, record in enumerate(records):
                print(f"   记录{i+1}: {record}")
        else:
            print(f"❌ 历史记录接口 (原始) 失败: {response.status_code}")
    
    except Exception as e:
        print(f"❌ 历史记录接口 (原始) 错误: {e}")
    
    try:
        # 4. 测试系统状态接口
        print("\n4. 测试系统状态接口...")
        response = requests.get(f"{base_url}/api/system/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ 系统状态接口正常")
            print(f"   系统: {data.get('system', 'N/A')}")
            print(f"   Python: {data.get('python', 'N/A')}")
            
            clients = data.get('clients', {})
            for name, status in clients.items():
                print(f"   {name}: {'✅' if status else '❌'}")
            
            print(f"   伪装启用: {'✅' if data.get('masquerade_enabled') else '❌'}")
            print(f"   时间戳: {data.get('timestamp', 'N/A')}")
        else:
            print(f"❌ 系统状态接口失败: {response.status_code}")
    
    except Exception as e:
        print(f"❌ 系统状态接口错误: {e}")
    
    print("\n=== API测试完成 ===")

def main():
    """主函数"""
    print("请确保BTC价格监控程序正在运行...")
    print("启动命令: python3 btc_price_monitor.py")
    print("")
    
    # 等待用户确认
    input("按回车键开始测试...")
    
    test_api()
    
    print("\n📖 API使用说明:")
    print("1. 实时价格: GET http://localhost:8080/api/btc-price")
    print("2. 历史记录: GET http://localhost:8080/api/btc-price/history?count=10")
    print("3. 原始格式: GET http://localhost:8080/api/btc-price/history?format=raw")
    print("4. 系统状态: GET http://localhost:8080/api/system/status")
    print("")
    print("详细文档请查看: API_USAGE.md")

if __name__ == "__main__":
    main()
