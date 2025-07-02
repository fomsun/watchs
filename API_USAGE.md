# BTC价格监控API使用指南

## 📊 API接口列表

### 1. WebSocket实时数据接口 🚀 **新增**
```
WebSocket: ws://localhost:8080/socket.io/
```

**功能**: 实时推送Lighter订单簿数据

**事件列表**:
- `connect`: 连接成功
- `disconnect`: 连接断开
- `price_update`: 价格数据更新（连接时自动发送）
- `lighter_update`: Lighter数据实时更新
- `subscribe_lighter`: 订阅Lighter数据
- `unsubscribe_lighter`: 取消订阅Lighter数据

**使用示例**:

#### JavaScript客户端
```javascript
// 连接WebSocket
const socket = io('http://localhost:8080');

// 监听连接事件
socket.on('connect', function() {
    console.log('WebSocket连接成功');
    // 订阅Lighter数据
    socket.emit('subscribe_lighter');
});

// 监听Lighter实时数据
socket.on('lighter_update', function(data) {
    console.log('Lighter数据:', data);
    // data.data.mid_price - 中间价
    // data.data.best_bid - 买一价
    // data.data.best_ask - 卖一价
    // data.data.spread - 价差
    // data.timestamp - 时间戳
});
```

#### Python客户端
```python
import socketio

sio = socketio.Client()

@sio.event
def connect():
    print('WebSocket连接成功')
    sio.emit('subscribe_lighter')

@sio.event
def lighter_update(data):
    lighter = data['data']
    print(f"中间价: ${lighter['mid_price']}")
    print(f"买一: ${lighter['best_bid']}")
    print(f"卖一: ${lighter['best_ask']}")

sio.connect('http://localhost:8080')
sio.wait()
```

**数据格式**:
```json
{
  "type": "lighter_update",
  "data": {
    "best_bid": 109350.1,
    "best_ask": 109354.3,
    "mid_price": 109352.2,
    "spread": 4.2,
    "connected": true,
    "timestamp": "2025-07-03 02:45:30"
  },
  "timestamp": "2025-07-03 02:45:30"
}
```

### 2. 实时价格接口
```
GET http://localhost:8080/api/btc-price
```

**返回示例**:
```json
{
  "binance": {
    "symbol": "BTCUSDC",
    "price": 109379.0,
    "connected": true,
    "timestamp": "2025-07-03 02:37:59"
  },
  "backpack": {
    "symbol": "BTC_USDC_PERP",
    "price": 109323.9,
    "connected": true,
    "timestamp": "2025-07-03 02:37:59"
  },
  "lighter": {
    "best_bid": 109350.1,
    "best_ask": 109354.3,
    "mid_price": 109352.2,
    "connected": true,
    "timestamp": "2025-07-03 02:37:59"
  },
  "timestamp": "2025-07-03 02:37:59"
}
```

### 3. 历史价格接口 ⭐
```
GET http://localhost:8080/api/btc-price/history
```

**查询参数**:
- `count`: 获取记录数量 (可选，默认返回所有记录，最大1000条)
- `format`: 返回格式 (可选，`json`或`raw`，默认`json`)

**使用示例**:

#### 获取最新10条记录 (JSON格式)
```bash
curl "http://localhost:8080/api/btc-price/history?count=10"
```

#### 获取最新50条记录 (原始格式)
```bash
curl "http://localhost:8080/api/btc-price/history?count=50&format=json"
```

#### 获取所有历史记录
```bash
curl "http://localhost:8080/api/btc-price/history"
```

**JSON格式返回示例**:
```json
{
  "count": 10,
  "format": "json",
  "data": [
    {
      "binance": {
        "exchange": "币安",
        "price": 109379.0
      },
      "backpack": {
        "exchange": "Backpack",
        "price": 109323.9
      },
      "lighter": {
        "exchange": "Lighter",
        "price": 109352.2
      },
      "timestamp": "2025-07-03 02:37:59"
    },
    {
      "binance": {
        "exchange": "币安",
        "price": 109381.5
      },
      "backpack": {
        "exchange": "Backpack",
        "price": 109325.1
      },
      "lighter": {
        "exchange": "Lighter",
        "price": 109354.8
      },
      "timestamp": "2025-07-03 02:37:49"
    }
  ]
}
```

**原始格式返回示例**:
```json
{
  "count": 10,
  "format": "raw",
  "data": [
    "币安:109379.0-Backpack:109323.9-Lighter:109352.2-2025-07-03 02:37:59",
    "币安:109381.5-Backpack:109325.1-Lighter:109354.8-2025-07-03 02:37:49",
    "币安:109383.2-Backpack:109327.3-Lighter:109356.1-2025-07-03 02:37:39"
  ]
}
```

### 4. 系统状态接口
```
GET http://localhost:8080/api/system/status
```

**返回示例**:
```json
{
  "system": "Darwin 23.1.0",
  "python": "3.12.0",
  "clients": {
    "binance": true,
    "backpack": true,
    "lighter": true
  },
  "masquerade_enabled": true,
  "timestamp": "2025-07-03T02:37:59.123456"
}
```

## 🕐 时间戳说明

**重要更新**: 所有时间戳现在使用**中国时间 (Asia/Shanghai)**！

- 格式: `YYYY-MM-DD HH:MM:SS`
- 时区: 中国标准时间 (UTC+8)
- 示例: `2025-07-03 02:37:59`

## 📝 使用示例

### Python示例
```python
import requests
import json

# 获取实时价格
response = requests.get('http://localhost:8080/api/btc-price')
data = response.json()
print(f"币安价格: ${data['binance']['price']}")
print(f"Lighter中间价: ${data['lighter']['mid_price']}")

# 获取历史记录
response = requests.get('http://localhost:8080/api/btc-price/history?count=5')
history = response.json()
print(f"获取到 {history['count']} 条历史记录")
for record in history['data']:
    print(f"{record['timestamp']}: 币安=${record['binance']['price']}")
```

### JavaScript示例
```javascript
// 获取实时价格
fetch('http://localhost:8080/api/btc-price')
  .then(response => response.json())
  .then(data => {
    console.log('币安价格:', data.binance.price);
    console.log('Lighter中间价:', data.lighter.mid_price);
  });

// 获取历史记录
fetch('http://localhost:8080/api/btc-price/history?count=10')
  .then(response => response.json())
  .then(data => {
    console.log(`获取到 ${data.count} 条历史记录`);
    data.data.forEach(record => {
      console.log(`${record.timestamp}: 币安=$${record.binance.price}`);
    });
  });
```

### curl示例
```bash
# 实时价格
curl -s http://localhost:8080/api/btc-price | jq '.binance.price'

# 最新10条历史记录
curl -s "http://localhost:8080/api/btc-price/history?count=10" | jq '.data[0]'

# 系统状态
curl -s http://localhost:8080/api/system/status | jq '.clients'
```

## 🔄 数据更新频率

- **实时价格**: 每秒更新
- **历史记录**: 每10秒保存一次
- **文件存储**: `btc_price_data.txt`

## 📁 本地文件格式

历史数据同时保存在本地文件中，格式为:
```
币安:109379.0-Backpack:109323.9-Lighter:109352.2-2025-07-03 02:37:59
```

每行一条记录，字段用`-`分隔，时间戳使用中国时间。
