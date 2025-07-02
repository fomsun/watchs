# BTC价格监控程序

## 项目介绍

这是一个用于监控多个交易所BTC价格的Python程序，支持以下功能：

- 获取币安BTC/USDC价格
- 获取Backpack BTC合约交易所的当前价格
- 获取Lighter BTC的价格（通过浏览器自动化）
- 提供API接口返回所有价格数据

## 安装依赖

```bash
# 创建并激活虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或者 .venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

## 使用方法

### 启动监控程序

```bash
python btc_price_monitor.py
```

程序启动后，会自动连接各个交易所并开始监控价格。同时会启动一个API服务器，提供价格数据接口。

### API接口

- 获取所有BTC价格: `http://localhost:5000/api/btc-price`

### 配置选项

在`btc_price_monitor.py`中，可以修改以下配置：

- `headless`: 是否使用无头模式运行浏览器（默认为True）
- API服务器端口（默认为5000）

## 项目结构

```
.
├── README.md           # 项目说明
├── requirements.txt    # 依赖列表
├── btc_price_monitor.py # 主程序
├── core/               # 核心功能模块
│   ├── __init__.py
│   ├── binance_client.py   # 币安客户端
│   ├── backpack_client.py  # Backpack客户端
│   ├── lighter_client.py   # Lighter客户端
│   └── orderbook_utils.py  # 订单簿工具函数
└── data/               # 数据模型
    ├── __init__.py
    └── models.py       # 数据模型定义
```

## 注意事项

- Lighter价格获取需要使用浏览器自动化，确保已安装DrissionPage库
- 如果在Linux系统上运行，可能需要安装额外的浏览器依赖
- API服务器默认绑定到所有网络接口，如有安全需求请修改配置# watchs
