#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ubuntu环境简单测试脚本
快速验证Ubuntu环境是否可以运行Lighter客户端
"""

import os
import sys
import subprocess
import platform

def test_basic_environment():
    """测试基本环境"""
    print("=== Ubuntu环境基本测试 ===")
    
    print(f"操作系统: {platform.system()} {platform.release()}")
    print(f"Python版本: {sys.version}")
    print(f"当前用户: {os.getenv('USER', 'unknown')}")
    print(f"HOME目录: {os.getenv('HOME', 'unknown')}")
    print(f"DISPLAY: {os.getenv('DISPLAY', 'None')}")
    
    return True

def test_chrome_simple():
    """简单测试Chrome"""
    print("\n=== Chrome简单测试 ===")
    
    chrome_paths = [
        '/usr/bin/google-chrome',
        '/usr/bin/google-chrome-stable',
        '/usr/bin/chromium-browser'
    ]
    
    for path in chrome_paths:
        if os.path.exists(path):
            print(f"✅ 找到Chrome: {path}")
            try:
                # 简单版本测试
                result = subprocess.run([path, '--version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    print(f"   版本: {result.stdout.strip()}")
                    return path
            except:
                pass
    
    print("❌ 未找到可用的Chrome")
    return None

def test_drissionpage():
    """测试DrissionPage"""
    print("\n=== DrissionPage测试 ===")
    
    try:
        from DrissionPage import ChromiumOptions, ChromiumPage
        print("✅ DrissionPage导入成功")
        
        # 测试基本配置
        co = ChromiumOptions()
        co.headless()
        co.set_argument('--no-sandbox')
        co.set_argument('--disable-dev-shm-usage')
        print("✅ ChromiumOptions配置成功")
        
        return True
    except ImportError as e:
        print(f"❌ DrissionPage导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ DrissionPage测试失败: {e}")
        return False

def test_chrome_headless_simple(chrome_path):
    """简单测试Chrome无头模式"""
    print(f"\n=== Chrome无头模式简单测试 ===")
    
    if not chrome_path:
        print("❌ 没有可用的Chrome路径")
        return False
    
    try:
        # 最简单的测试
        cmd = [
            chrome_path,
            '--headless',
            '--no-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--dump-dom',
            'data:text/html,<html><body>Hello Ubuntu</body></html>'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0 and 'Hello Ubuntu' in result.stdout:
            print("✅ Chrome无头模式基本测试成功")
            return True
        else:
            print("❌ Chrome无头模式测试失败")
            print(f"返回码: {result.returncode}")
            if result.stderr:
                print(f"错误: {result.stderr[:200]}...")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Chrome测试超时")
        return False
    except Exception as e:
        print(f"❌ Chrome测试异常: {e}")
        return False

def test_network():
    """测试网络连接"""
    print("\n=== 网络连接测试 ===")
    
    test_urls = [
        'google.com',
        'app.lighter.xyz',
        'fstream.binance.com'
    ]
    
    for url in test_urls:
        try:
            result = subprocess.run(['ping', '-c', '1', '-W', '3', url], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"✅ {url} 连接正常")
            else:
                print(f"❌ {url} 连接失败")
        except:
            print(f"❌ {url} 测试异常")

def test_permissions():
    """测试权限"""
    print("\n=== 权限测试 ===")
    
    # 测试临时目录写入
    try:
        test_file = '/tmp/btc_monitor_test.txt'
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        print("✅ 临时目录写入权限正常")
    except Exception as e:
        print(f"❌ 临时目录写入权限失败: {e}")
    
    # 测试当前目录写入
    try:
        test_file = './test_write.txt'
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        print("✅ 当前目录写入权限正常")
    except Exception as e:
        print(f"❌ 当前目录写入权限失败: {e}")

def main():
    """主函数"""
    print("Ubuntu环境快速测试")
    print("=" * 40)
    
    # 基本环境测试
    test_basic_environment()
    
    # Chrome测试
    chrome_path = test_chrome_simple()
    
    # DrissionPage测试
    drissionpage_ok = test_drissionpage()
    
    # Chrome无头模式测试
    if chrome_path:
        chrome_headless_ok = test_chrome_headless_simple(chrome_path)
    else:
        chrome_headless_ok = False
    
    # 网络测试
    test_network()
    
    # 权限测试
    test_permissions()
    
    # 总结
    print("\n" + "=" * 40)
    print("测试结果总结:")
    print(f"Chrome可用: {'✅' if chrome_path else '❌'}")
    print(f"DrissionPage: {'✅' if drissionpage_ok else '❌'}")
    print(f"Chrome无头模式: {'✅' if chrome_headless_ok else '❌'}")
    
    if chrome_path and drissionpage_ok and chrome_headless_ok:
        print("\n🎉 Ubuntu环境测试通过！可以运行BTC价格监控程序")
        print("\n建议运行:")
        print("python3 btc_price_monitor_ubuntu.py")
    else:
        print("\n❌ Ubuntu环境测试失败，需要修复以下问题:")
        if not chrome_path:
            print("- 安装Chrome: sudo apt install -y google-chrome-stable")
        if not drissionpage_ok:
            print("- 安装DrissionPage: pip3 install DrissionPage")
        if not chrome_headless_ok:
            print("- 安装Chrome依赖: sudo apt install -y libnss3-dev libatk-bridge2.0-dev libdrm2 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libxss1 libasound2")
        
        print("\n详细修复指南请运行:")
        print("python3 ubuntu_fix.py")

if __name__ == "__main__":
    main()
