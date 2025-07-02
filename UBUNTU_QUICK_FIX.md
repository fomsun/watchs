# Ubuntu快速修复指南

## 🚨 最常见问题及解决方案

### 1. Chrome启动失败
```bash
# 症状: Chrome failed to start, DevToolsActivePort file doesn't exist
# 解决方案:
sudo apt install -y libnss3-dev libatk-bridge2.0-dev libdrm2 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libxss1 libasound2

# 如果还是失败，尝试:
sudo apt install -y chromium-browser
```

### 2. 权限问题
```bash
# 症状: Permission denied
# 解决方案:
sudo usermod -a -G audio,video $USER
mkdir -p ~/.config/google-chrome
chmod 755 ~/.config/google-chrome
# 然后重新登录
```

### 3. 内存不足
```bash
# 症状: Out of memory, 程序崩溃
# 解决方案:
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### 4. 网络连接问题
```bash
# 症状: Connection refused, Timeout
# 解决方案:
sudo ufw allow 8080
echo "nameserver 8.8.8.8" | sudo tee -a /etc/resolv.conf
```

### 5. DrissionPage问题
```bash
# 症状: DrissionPage相关错误
# 解决方案:
pip3 uninstall DrissionPage
pip3 install DrissionPage==4.0.5.6
```

## 🔧 快速诊断命令

```bash
# 1. 运行快速测试
python3 test_ubuntu_simple.py

# 2. 运行详细诊断
python3 ubuntu_fix.py

# 3. 检查Chrome
google-chrome --version
which google-chrome

# 4. 检查Python包
pip3 list | grep -E "(DrissionPage|flask|websocket)"

# 5. 检查系统资源
free -h
df -h
```

## 🚀 推荐启动方式

```bash
# Ubuntu优化版（推荐）
python3 btc_price_monitor_ubuntu.py

# 如果优化版有问题，使用标准版
python3 btc_price_monitor.py
```

## 📞 仍然有问题？

1. 保存错误日志: `python3 btc_price_monitor_ubuntu.py 2>&1 | tee error.log`
2. 运行诊断: `python3 ubuntu_fix.py > diagnosis.txt`
3. 提供系统信息: `uname -a && lsb_release -a`
