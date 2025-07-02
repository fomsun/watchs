#!/bin/bash

# Ubuntu Selenium安装脚本
# 安装Selenium、Chrome和ChromeDriver

echo "=== Ubuntu Selenium安装脚本 ==="

# 检查是否为root用户
if [ "$EUID" -eq 0 ]; then
    echo "⚠️  请不要使用root用户运行此脚本"
    exit 1
fi

# 更新系统
echo "📦 更新系统包..."
sudo apt update

# 安装Python3和pip
echo "🐍 安装Python3和pip..."
sudo apt install -y python3 python3-pip

# 安装Chrome
echo "🌐 安装Google Chrome..."
if ! command -v google-chrome &> /dev/null; then
    # 下载Chrome的GPG密钥
    wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
    
    # 添加Chrome仓库
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
    
    # 更新包列表并安装Chrome
    sudo apt update
    sudo apt install -y google-chrome-stable
    
    echo "✅ Google Chrome安装完成"
else
    echo "✅ Google Chrome已安装: $(google-chrome --version)"
fi

# 安装Chrome依赖
echo "📦 安装Chrome运行依赖..."
sudo apt install -y \
    libnss3-dev \
    libatk-bridge2.0-dev \
    libdrm2 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libxss1 \
    libasound2 \
    libatspi2.0-0 \
    libgtk-3-0 \
    xvfb

echo "✅ Chrome依赖安装完成"

# 安装ChromeDriver
echo "🚗 安装ChromeDriver..."

# 获取Chrome版本
CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d. -f1)
echo "Chrome版本: $CHROME_VERSION"

# 下载对应版本的ChromeDriver
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION")
echo "ChromeDriver版本: $CHROMEDRIVER_VERSION"

# 下载ChromeDriver
cd /tmp
wget -O chromedriver.zip "https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip"

# 解压并安装
unzip chromedriver.zip
sudo mv chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver

# 验证安装
if command -v chromedriver &> /dev/null; then
    echo "✅ ChromeDriver安装成功: $(chromedriver --version)"
else
    echo "❌ ChromeDriver安装失败"
fi

# 清理临时文件
rm -f chromedriver.zip

# 安装Python依赖
echo "🐍 安装Python依赖..."
pip3 install selenium>=4.0.0

# 验证Selenium安装
echo "🧪 验证Selenium安装..."
python3 -c "
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    print('✅ Selenium导入成功')
    
    # 测试Chrome选项
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    print('✅ Chrome选项配置成功')
    
    print('🎉 Selenium安装验证通过')
except ImportError as e:
    print(f'❌ Selenium导入失败: {e}')
except Exception as e:
    print(f'❌ Selenium测试失败: {e}')
"

# 创建测试脚本
echo "📝 创建Selenium测试脚本..."
cat > test_selenium_simple.py << 'EOF'
#!/usr/bin/env python3

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

def test_selenium():
    print("=== Selenium简单测试 ===")
    
    try:
        # 配置Chrome选项
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        
        # 创建WebDriver
        service = Service()
        driver = webdriver.Chrome(service=service, options=options)
        
        # 访问测试页面
        print("🔗 访问测试页面...")
        driver.get('data:text/html,<html><body><h1>Hello Selenium</h1></body></html>')
        
        # 检查页面标题
        if 'Hello Selenium' in driver.page_source:
            print("✅ Selenium测试成功")
            result = True
        else:
            print("❌ Selenium测试失败")
            result = False
        
        # 关闭浏览器
        driver.quit()
        return result
        
    except Exception as e:
        print(f"❌ Selenium测试异常: {e}")
        return False

if __name__ == "__main__":
    if test_selenium():
        print("🎉 Selenium环境配置成功！")
    else:
        print("❌ Selenium环境配置失败")
EOF

chmod +x test_selenium_simple.py

echo ""
echo "🎉 Ubuntu Selenium安装完成！"
echo ""
echo "📍 安装信息:"
echo "   Chrome: $(google-chrome --version 2>/dev/null || echo '未安装')"
echo "   ChromeDriver: $(chromedriver --version 2>/dev/null || echo '未安装')"
echo "   Python: $(python3 --version)"
echo ""
echo "🧪 测试命令:"
echo "   python3 test_selenium_simple.py"
echo "   python3 test_selenium_lighter.py"
echo ""
echo "🚀 启动BTC监控:"
echo "   python3 btc_price_monitor.py"
echo ""
echo "⚠️  注意事项:"
echo "   - 确保网络连接正常"
echo "   - Ubuntu系统会自动选择Selenium客户端"
echo "   - 如果遇到问题，请检查Chrome和ChromeDriver版本是否匹配"
