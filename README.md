# BTC价格监控系统

实时监控比特币价格的Python应用程序，支持多个交易所数据源和WebSocket实时推送。

## 🚀 功能特性

- **实时价格监控**: 通过WebSocket获取币安、Backpack实时价格
- **订单簿数据**: 从Lighter获取实时订单簿和中间价
- **历史数据记录**: 每10秒自动保存价格数据到本地文件
- **RESTful API**: 提供HTTP接口获取当前价格和历史数据
- **跨平台支持**: 支持Linux、macOS、Windows

## 📊 数据源

| 交易所 | 数据类型 | 交易对 | 连接方式 |
|--------|----------|--------|----------|
| 币安 | 永续合约价格 | BTCUSDC | WebSocket |
| Backpack | 永续合约价格 | BTC_USDC_PERP | WebSocket |
| Lighter | 订单簿中间价 | BTC | 浏览器抓取 |

## 🛠️ 安装说明

### Linux系统 (推荐)

1. **自动安装**:
   ```bash
   chmod +x setup_linux.sh
   ./setup_linux.sh
   ```

2. **手动安装**:
   ```bash
   # 安装依赖
   sudo apt update
   sudo apt install -y python3 python3-pip google-chrome-stable

   # 安装Python包
   pip3 install -r requirements.txt
   ```

### 其他系统

1. **安装Python依赖**:
   ```bash
   pip install -r requirements.txt
   ```

2. **安装Chrome浏览器**:
   - 下载并安装Google Chrome
   - 确保Chrome在系统PATH中

## 🚀 使用方法

### 启动监控程序

```bash
# 方式1: 使用启动脚本 (Linux)
./start_monitor.sh

# 方式2: 直接运行
python3 btc_price_monitor.py
```

### API接口

#### 获取当前价格
```bash
curl http://localhost:8080/api/btc-price
```

#### 获取历史数据
```bash
# 获取全部历史记录
curl http://localhost:8080/api/btc-price/history

# 获取最新10条记录
curl http://localhost:8080/api/btc-price/history?count=10

# 获取原始格式数据
curl http://localhost:8080/api/btc-price/history?format=raw
```

## 📁 文件结构

```
watchs/
├── btc_price_monitor.py          # 主程序 (包含WebSocket服务)
├── config.py                     # 配置文件
├── requirements.txt              # Python依赖
├── API_USAGE.md                  # API使用文档
├── websocket_client_example.py   # WebSocket客户端示例
├── websocket_test.html           # WebSocket测试页面
├── core/                         # 核心模块
│   ├── binance_client.py         # 币安WebSocket客户端
│   ├── backpack_client.py        # Backpack WebSocket客户端
│   ├── lighter_client.py         # Lighter浏览器客户端 (自动重连)
│   ├── lighter_manager.py        # Lighter客户端管理器
│   ├── lighter_selenium_client.py # Selenium备选客户端
│   ├── price_recorder.py         # 价格记录器
│   └── orderbook_utils.py        # 订单簿工具
├── data/                         # 数据模型
│   └── models.py                 # 数据结构定义
└── btc_price_data.txt            # 价格数据文件 (自动生成)
```

## ⚙️ 配置说明

### Chrome路径配置

程序会自动检测以下Chrome路径:

**Linux**:
- `/usr/bin/google-chrome` ⭐ (您的路径)
- `/usr/bin/google-chrome-stable`
- `/usr/bin/chromium-browser`
- `/usr/bin/chromium`
- `/snap/bin/chromium`

**macOS**:
- `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`

**Windows**:
- `C:\Program Files\Google\Chrome\Application\chrome.exe`

### 自定义配置

编辑 `config.py` 文件可以修改:
- API服务器端口 (默认: 8080)
- 价格记录间隔 (默认: 10秒)
- 浏览器等待时间
- Chrome路径

## 🔧 故障排除

### Chrome路径问题
```bash
# 检查Chrome安装
which google-chrome
google-chrome --version

# 测试配置
python3 config.py
```

### 权限问题 (Linux)
```bash
# 添加用户到必要组
sudo usermod -a -G audio,video $USER

# 重新登录或重启
```

## 📄 许可证

MIT License
