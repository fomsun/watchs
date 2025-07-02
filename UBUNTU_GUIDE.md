# Ubuntu系统BTC价格监控部署指南

## 🚀 快速部署

### 1. 系统要求
- Ubuntu 18.04+ (推荐 20.04 或 22.04)
- Python 3.8+
- 至少 2GB RAM
- 网络连接

### 2. 一键安装脚本
```bash
# 下载并运行安装脚本
chmod +x setup_linux.sh
./setup_linux.sh

# 或者手动安装
sudo apt update
sudo apt install -y python3 python3-pip google-chrome-stable
pip3 install -r requirements.txt
```

### 3. Ubuntu问题诊断
```bash
# 运行Ubuntu修复脚本
python3 ubuntu_fix.py
```

### 4. 启动Ubuntu优化版
```bash
# 使用Ubuntu优化版程序
python3 btc_price_monitor_ubuntu.py
```

## 🔧 常见问题解决

### 问题1: Chrome无法启动
**症状**: `Chrome failed to start` 或 `DevToolsActivePort file doesn't exist`

**解决方案**:
```bash
# 安装Chrome依赖
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

# 如果仍然失败，尝试安装Chromium
sudo apt install -y chromium-browser
```

### 问题2: 权限问题
**症状**: `Permission denied` 或 `Operation not permitted`

**解决方案**:
```bash
# 添加用户到必要组
sudo usermod -a -G audio,video $USER

# 创建Chrome用户数据目录
mkdir -p ~/.config/google-chrome
chmod 755 ~/.config/google-chrome

# 重新登录或重启
sudo reboot
```

### 问题3: 内存不足
**症状**: `Out of memory` 或程序崩溃

**解决方案**:
```bash
# 增加swap空间
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 永久启用
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### 问题4: 网络连接问题
**症状**: `Connection refused` 或 `Timeout`

**解决方案**:
```bash
# 检查防火墙
sudo ufw status
sudo ufw allow 8080

# 检查DNS
nslookup app.lighter.xyz
nslookup fstream.binance.com

# 如果DNS有问题，使用公共DNS
echo "nameserver 8.8.8.8" | sudo tee -a /etc/resolv.conf
```

### 问题5: DrissionPage问题
**症状**: `DrissionPage` 相关错误

**解决方案**:
```bash
# 重新安装DrissionPage
pip3 uninstall DrissionPage
pip3 install DrissionPage==4.0.5.6

# 或使用最新版本
pip3 install --upgrade DrissionPage
```

## 🐧 Ubuntu优化配置

### Chrome启动参数优化
Ubuntu版本使用了以下优化参数：
```
--no-sandbox                    # 禁用沙盒（必需）
--disable-dev-shm-usage         # 禁用/dev/shm使用
--disable-gpu                   # 禁用GPU
--disable-extensions            # 禁用扩展
--disable-web-security          # 禁用Web安全
--memory-pressure-off           # 关闭内存压力检测
--max_old_space_size=4096       # 设置最大内存
```

### 系统服务配置
创建systemd服务：
```bash
# 复制服务文件
sudo cp btc-monitor.service /etc/systemd/system/

# 启用服务
sudo systemctl enable btc-monitor
sudo systemctl start btc-monitor

# 查看状态
sudo systemctl status btc-monitor

# 查看日志
sudo journalctl -u btc-monitor -f
```

## 📊 性能监控

### 系统资源监控
```bash
# 实时监控
htop

# 内存使用
free -h

# 磁盘使用
df -h

# 网络连接
netstat -tulpn | grep 8080
```

### 程序日志
```bash
# 查看程序输出
tail -f btc_price_data_ubuntu.txt

# 查看系统日志
sudo journalctl -f
```

## 🔒 安全配置

### 防火墙设置
```bash
# 只允许必要端口
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 8080
sudo ufw deny 9222  # Chrome调试端口
```

### 用户权限
```bash
# 创建专用用户
sudo useradd -m -s /bin/bash btcmonitor
sudo usermod -a -G audio,video btcmonitor

# 切换到专用用户
sudo su - btcmonitor
```

## 🚀 生产环境部署

### 使用Docker (推荐)
```dockerfile
FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    python3 python3-pip \
    google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

COPY . /app
WORKDIR /app

RUN pip3 install -r requirements.txt

EXPOSE 8080

CMD ["python3", "btc_price_monitor_ubuntu.py"]
```

### 使用进程管理器
```bash
# 安装PM2
npm install -g pm2

# 启动程序
pm2 start btc_price_monitor_ubuntu.py --name btc-monitor --interpreter python3

# 设置开机启动
pm2 startup
pm2 save
```

## 📞 故障排除

### 调试模式
```bash
# 启用详细日志
export DEBUG=1
python3 btc_price_monitor_ubuntu.py

# 保存调试信息
python3 btc_price_monitor_ubuntu.py 2>&1 | tee debug.log
```

### 常用检查命令
```bash
# 检查Chrome
google-chrome --version
which google-chrome

# 检查Python包
pip3 list | grep -E "(DrissionPage|flask|websocket)"

# 检查端口占用
sudo lsof -i :8080

# 检查进程
ps aux | grep python
```

### 联系支持
如果问题仍然存在：
1. 运行 `python3 ubuntu_fix.py` 获取诊断信息
2. 保存错误日志
3. 提供系统信息：`uname -a` 和 `lsb_release -a`

## 🎯 性能优化建议

1. **使用SSD存储** - 提高I/O性能
2. **增加内存** - 至少4GB推荐
3. **使用CDN** - 如果网络较慢
4. **定期清理日志** - 避免磁盘空间不足
5. **监控资源使用** - 设置告警

## ✅ 验证部署

部署完成后，验证以下接口：
- http://your-server:8080/api/btc-price
- http://your-server:8080/api/system/status
- http://your-server:8080/api/btc-price/history
