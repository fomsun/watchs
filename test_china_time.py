#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试中国时间功能
"""

from datetime import datetime
import pytz

def test_china_time():
    """测试中国时间"""
    print("=== 中国时间测试 ===")
    
    # 获取当前UTC时间
    utc_time = datetime.utcnow()
    print(f"UTC时间: {utc_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 获取本地时间
    local_time = datetime.now()
    print(f"本地时间: {local_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 获取中国时间
    china_tz = pytz.timezone('Asia/Shanghai')
    china_time = datetime.now(china_tz)
    print(f"中国时间: {china_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 测试格式化
    formatted_time = china_time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"格式化中国时间: {formatted_time}")
    
    # 模拟价格记录格式
    sample_record = f"币安:109379.0-Backpack:109323.9-Lighter:109352.2-{formatted_time}"
    print(f"示例记录: {sample_record}")
    
    print("✅ 中国时间测试完成")

if __name__ == "__main__":
    test_china_time()
