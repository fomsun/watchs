#!/bin/bash

# BTC价格监控系统 - Linux安装脚本

echo "=== BTC价格监控系统 Linux安装脚本 ==="

# 检查是否为Linux系统
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "❌ 此脚本仅适用于Linux系统"
    exit 1
fi

# 更新包管理器
echo "📦 更新包管理器..."
sudo apt update

# 安装Python3和pip
echo "🐍 检查Python3安装..."
if ! command -v python3 &> /dev/null; then
    echo "安装Python3..."
    sudo apt install -y python3 python3-pip
else
    echo "✅ Python3已安装: $(python3 --version)"
fi

# 安装Google Chrome和依赖
echo "🌐 检查Google Chrome安装..."
if ! command -v google-chrome &> /dev/null; then
    echo "安装Google Chrome..."

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

# 安装Chrome运行依赖（Ubuntu重要）
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
    libgtk-3-0

echo "✅ Chrome依赖安装完成"

# 检查Chrome路径
echo "🔍 检查Chrome路径..."
CHROME_PATHS=(
    "/usr/bin/google-chrome"
    "/usr/bin/google-chrome-stable"
    "/usr/bin/chromium-browser"
    "/usr/bin/chromium"
    "/snap/bin/chromium"
)

FOUND_CHROME=""
for path in "${CHROME_PATHS[@]}"; do
    if [[ -f "$path" ]]; then
        FOUND_CHROME="$path"
        echo "✅ 找到Chrome: $path"
        break
    fi
done

if [[ -z "$FOUND_CHROME" ]]; then
    echo "❌ 未找到Chrome浏览器，请手动安装"
    exit 1
fi

# 安装Python依赖
echo "📚 安装Python依赖..."
pip3 install --user -r requirements.txt

# 创建requirements.txt（如果不存在）
if [[ ! -f "requirements.txt" ]]; then
    echo "📝 创建requirements.txt..."
    cat > requirements.txt << EOF
flask==2.3.3
websocket-client==1.6.4
DrissionPage==4.0.5.6
selenium==4.15.2
requests==2.31.0
EOF
    pip3 install --user -r requirements.txt
fi

# 设置权限
echo "🔐 设置执行权限..."
chmod +x btc_price_monitor.py
chmod +x btc_price_monitor_ubuntu.py
chmod +x config.py
chmod +x ubuntu_fix.py
chmod +x test_ubuntu_simple.py

# 创建启动脚本
echo "🚀 创建启动脚本..."
cat > start_monitor.sh << 'EOF'
#!/bin/bash

# BTC价格监控启动脚本

echo "=== 启动BTC价格监控系统 ==="

# 检查配置
echo "🔧 检查系统配置..."
python3 config.py

if [[ $? -ne 0 ]]; then
    echo "❌ 配置检查失败，请检查Chrome安装"
    exit 1
fi

# 启动监控程序
echo "🚀 启动价格监控..."
python3 btc_price_monitor.py
EOF

chmod +x start_monitor.sh

# 创建systemd服务文件（可选）
echo "⚙️  创建systemd服务文件..."
cat > btc-monitor.service << EOF
[Unit]
Description=BTC Price Monitor
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
ExecStart=/usr/bin/python3 $(pwd)/btc_price_monitor.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "📋 systemd服务文件已创建: btc-monitor.service"
echo "   要安装服务，请运行:"
echo "   sudo cp btc-monitor.service /etc/systemd/system/"
echo "   sudo systemctl enable btc-monitor"
echo "   sudo systemctl start btc-monitor"

# 显示安装完成信息
echo ""
# 运行Ubuntu环境测试
echo "🧪 运行Ubuntu环境测试..."
python3 test_ubuntu_simple.py

echo ""
echo "🎉 安装完成！"
echo ""
echo "📍 Chrome路径: $FOUND_CHROME"
echo "🐍 Python版本: $(python3 --version)"
echo "📁 工作目录: $(pwd)"
echo ""
echo "🚀 启动方式:"
echo "   Ubuntu优化版: python3 btc_price_monitor_ubuntu.py"
echo "   标准版: python3 btc_price_monitor.py"
echo "   启动脚本: ./start_monitor.sh"
echo ""
echo "🌐 API接口: http://localhost:8080/api/btc-price"
echo "📊 历史数据: http://localhost:8080/api/btc-price/history"
echo "🔧 系统状态: http://localhost:8080/api/system/status"
echo ""
echo "📝 日志文件: btc_price_data_ubuntu.txt"
echo ""
echo "🔧 故障排除:"
echo "   环境测试: python3 test_ubuntu_simple.py"
echo "   详细诊断: python3 ubuntu_fix.py"
echo "   Ubuntu指南: cat UBUNTU_GUIDE.md"
echo ""
echo "⚠️  注意事项:"
echo "   - Ubuntu推荐使用优化版程序"
echo "   - 确保网络连接正常"
echo "   - 首次运行可能需要较长时间加载"
echo "   - 使用Ctrl+C停止程序"
EOF
