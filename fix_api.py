#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API修复脚本
自动修复SQLite记录器中的重复方法定义问题
"""

import os
import re

def fix_sqlite_recorder():
    """修复SQLite记录器文件"""
    file_path = "core/sqlite_price_recorder.py"
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return False
    
    print(f"🔧 修复文件: {file_path}")
    
    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否有重复的get_records_from_time方法
    pattern = r'def get_records_from_time\(self.*?\n(?:.*?\n)*?.*?return \[\]'
    matches = re.findall(pattern, content, re.DOTALL)
    
    print(f"🔍 找到 {len(matches)} 个 get_records_from_time 方法定义")
    
    if len(matches) > 1:
        print("⚠️  发现重复方法定义，正在修复...")
        
        # 找到所有方法的位置
        method_positions = []
        for match in re.finditer(pattern, content, re.DOTALL):
            method_positions.append((match.start(), match.end()))
        
        # 保留第一个，删除其他的
        if len(method_positions) > 1:
            # 从后往前删除，避免位置偏移
            for start, end in reversed(method_positions[1:]):
                content = content[:start] + content[end:]
                print(f"🗑️  删除重复方法定义 (位置: {start}-{end})")
        
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ 修复完成")
        return True
    else:
        print("✅ 没有发现重复方法定义")
        return True

def verify_fix():
    """验证修复结果"""
    print("\n🔍 验证修复结果...")
    
    try:
        # 重新导入模块
        import importlib
        import sys
        
        # 清除模块缓存
        if 'core.sqlite_price_recorder' in sys.modules:
            del sys.modules['core.sqlite_price_recorder']
        
        from core.sqlite_price_recorder import SQLitePriceRecorder
        
        # 检查方法是否正常
        recorder = SQLitePriceRecorder("test_fix.db")
        
        # 测试方法调用
        result = recorder.get_latest_records(1)
        print(f"✅ get_latest_records 测试通过: {len(result)} 条记录")
        
        result = recorder.get_records_from_time("2025-07-03 00:00:00", 1)
        print(f"✅ get_records_from_time 测试通过: {len(result)} 条记录")
        
        result = recorder.get_records_by_time_range("2025-07-03 00:00:00", "2025-07-03 23:59:59")
        print(f"✅ get_records_by_time_range 测试通过: {len(result)} 条记录")
        
        print("🎉 所有方法测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("🛠️  API修复工具")
    print("=" * 50)
    
    # 修复文件
    if fix_sqlite_recorder():
        # 验证修复
        if verify_fix():
            print("\n🎉 修复成功！")
            print("现在可以重启服务器测试API接口")
        else:
            print("\n❌ 修复验证失败")
    else:
        print("\n❌ 修复失败")

if __name__ == "__main__":
    main()
