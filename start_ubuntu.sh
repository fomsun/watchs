#!/bin/bash

# Ubuntu专用启动脚本
# 强制使用Selenium客户端并设置优化参数

echo "=== Ubuntu BTC价格监控启动脚本 ==="

# 检查依赖
echo "🔍 检查依赖..."

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3未安装"
    exit 1
fi

# 检查Chrome
if ! command -v google-chrome &> /dev/null; then
    echo "❌ Google Chrome未安装"
    echo "请运行: sudo apt install -y google-chrome-stable"
    exit 1
fi

# 检查ChromeDriver
if ! command -v chromedriver &> /dev/null; then
    echo "❌ ChromeDriver未安装"
    echo "请运行安装脚本: ./install_selenium_ubuntu.sh"
    exit 1
fi

# 检查Selenium
python3 -c "import selenium" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Selenium未安装"
    echo "请运行: pip3 install selenium"
    exit 1
fi

echo "✅ 依赖检查通过"

# 设置环境变量
export LIGHTER_CLIENT_TYPE=selenium
export DISPLAY=:99  # 虚拟显示器
export CHROME_BIN=/usr/bin/google-chrome
export CHROMEDRIVER_PATH=/usr/local/bin/chromedriver

echo "🔧 环境变量设置:"
echo "   LIGHTER_CLIENT_TYPE=$LIGHTER_CLIENT_TYPE"
echo "   DISPLAY=$DISPLAY"
echo "   CHROME_BIN=$CHROME_BIN"
echo "   CHROMEDRIVER_PATH=$CHROMEDRIVER_PATH"

# 启动虚拟显示器（如果需要）
if ! pgrep -x "Xvfb" > /dev/null; then
    echo "🖥️  启动虚拟显示器..."
    Xvfb :99 -screen 0 1440x900x24 &
    sleep 2
fi

# 显示系统信息
echo "📊 系统信息:"
echo "   操作系统: $(lsb_release -d | cut -f2)"
echo "   Python版本: $(python3 --version)"
echo "   Chrome版本: $(google-chrome --version)"
echo "   ChromeDriver版本: $(chromedriver --version | head -1)"

# 测试选项
echo ""
echo "🧪 可用测试:"
echo "   1. 测试Selenium环境: python3 test_masquerade.py"
echo "   2. 测试Lighter客户端: python3 test_selenium_lighter.py"
echo "   3. 启动完整监控: python3 btc_price_monitor.py"
echo ""

# 询问用户选择
read -p "请选择操作 (1-3) 或直接回车启动监控: " choice

case $choice in
    1)
        echo "🧪 运行Selenium环境测试..."
        python3 test_masquerade.py
        ;;
    2)
        echo "🧪 运行Lighter客户端测试..."
        python3 test_selenium_lighter.py
        ;;
    3|"")
        echo "🚀 启动BTC价格监控..."
        python3 btc_price_monitor.py
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac
