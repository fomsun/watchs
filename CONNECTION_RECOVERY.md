# 🔌 连接恢复机制说明

## 问题描述

在长时间运行过程中，DrissionPage可能会出现以下连接问题：
```
The connection to the page has been disconnected.
Version: 4.1.0.18
订单簿数据为空或解析失败
```

这通常是由于：
1. 网页长时间运行后失去响应
2. 浏览器内存不足或崩溃
3. 网络连接不稳定
4. 页面JavaScript执行错误

## 🛠️ 解决方案

### 1. 自动连接检测
- **连接状态检查**: 每次数据抓取前检查页面连接状态
- **错误识别**: 识别连接断开相关的错误信息
- **计数机制**: 跟踪连续失败次数，触发重连

### 2. 智能重连机制
- **自动重连**: 检测到连接断开时自动尝试重连
- **页面重建**: 完全重新创建浏览器页面和连接
- **配置恢复**: 重新应用所有浏览器配置和伪装设置

### 3. 定期页面刷新
- **定时刷新**: 每5分钟自动刷新页面（可配置）
- **预防性维护**: 防止页面长时间运行导致的问题
- **状态保持**: 刷新后重新应用所有设置

## 📊 监控和诊断

### 连接状态监控
```bash
# 启动连接监控
python3 monitor_connection.py
```

**监控功能**:
- 实时显示连接状态
- 统计数据接收次数
- 记录错误和重连次数
- 检测数据流中断

### 连接恢复测试
```bash
# 测试自动重连功能
python3 test_connection_recovery.py
```

**测试功能**:
- 模拟连接断开
- 验证自动重连机制
- 测试恢复时间
- 评估稳定性

## ⚙️ 配置选项

### config.py 配置
```python
# 页面刷新间隔（秒）
PAGE_REFRESH_INTERVAL = 300  # 5分钟

# 连接重试配置
MAX_RECONNECT_ATTEMPTS = 3   # 最大重连尝试次数
RECONNECT_DELAY = 10         # 重连延迟（秒）
CONNECTION_CHECK_INTERVAL = 30  # 连接检查间隔（秒）
```

### 客户端配置
```python
# 创建带重连功能的客户端
client = LighterClient(
    on_data_callback=callback,
    headless=True,
    refresh_interval=300  # 页面刷新间隔
)
```

## 🔧 故障排除

### 常见问题

1. **频繁重连**
   - 检查网络连接稳定性
   - 增加 `RECONNECT_DELAY` 延迟
   - 检查系统资源使用情况

2. **重连失败**
   - 确认Chrome浏览器路径正确
   - 检查系统权限
   - 查看详细错误日志

3. **数据中断**
   - 监控连接状态
   - 检查页面加载情况
   - 验证订单簿元素是否存在

### 调试步骤

1. **启用详细日志**
   ```python
   # 在config.py中设置
   DEBUG = True
   ```

2. **运行连接监控**
   ```bash
   python3 monitor_connection.py
   ```

3. **检查浏览器状态**
   - 查看浏览器进程
   - 检查内存使用
   - 验证页面响应

## 📈 性能优化

### 减少连接问题
1. **定期刷新**: 设置合适的刷新间隔
2. **资源优化**: 禁用图片和不必要的资源
3. **内存管理**: 定期重启浏览器进程

### 提高恢复速度
1. **快速检测**: 减少连接检查间隔
2. **并行处理**: 异步执行重连操作
3. **缓存配置**: 重用浏览器配置

## 🚀 最佳实践

### 生产环境建议
1. **监控部署**: 部署连接状态监控
2. **告警设置**: 配置连接失败告警
3. **日志记录**: 记录所有连接事件
4. **定期维护**: 定时重启服务

### 开发环境建议
1. **测试工具**: 使用连接恢复测试脚本
2. **调试模式**: 启用详细日志输出
3. **快速迭代**: 使用较短的刷新间隔

## 📝 使用示例

### 基本使用
```python
from core.lighter_client import LighterClient

def on_data(data):
    if data.orderbook:
        print(f"价格: {data.orderbook.mid_price}")

# 创建带自动重连的客户端
client = LighterClient(on_data, refresh_interval=300)
client.start()
```

### 高级配置
```python
# 自定义重连参数
client = LighterClient(
    on_data_callback=on_data,
    headless=True,
    refresh_interval=180,  # 3分钟刷新
)

# 启动并监控
if client.start():
    print("客户端启动成功，具备自动重连功能")
```

通过这些改进，系统现在能够：
- ✅ 自动检测连接断开
- ✅ 智能重连页面
- ✅ 定期刷新防止问题
- ✅ 实时监控连接状态
- ✅ 提供详细的诊断工具
