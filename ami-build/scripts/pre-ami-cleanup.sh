#!/bin/bash
# ============================================================
# Pre-AMI Cleanup Script
# 在创建 AMI 快照之前执行，清理所有敏感信息和临时文件
# ============================================================

set -e
echo "=== Pre-AMI Cleanup ==="

# 停止应用服务
echo "Stopping application services..."
sudo systemctl stop biomni-admin biomni-agent nginx || true

# 停止并清理 docker 容器和数据
echo "Stopping and cleaning docker containers..."
cd /opt/biomni/docker
docker compose down -v || true

# 删除初始化标记
echo "Removing initialization marker..."
sudo rm -f /opt/biomni/.initialized

# 删除生成的配置和凭据
echo "Removing generated configs and credentials..."
sudo rm -f /opt/biomni/config/biomni.env
sudo rm -f /opt/biomni/docker/.env
sudo rm -f /home/ubuntu/biomni-credentials.txt

# 清理日志
echo "Cleaning logs..."
sudo rm -rf /opt/biomni/logs/*
sudo rm -rf /var/log/*.log 2>/dev/null || true
sudo journalctl --vacuum-time=1s

# 清理临时文件
echo "Cleaning temporary files..."
sudo rm -rf /tmp/* /var/tmp/* 2>/dev/null || true

# 清理 SSH host keys
echo "Cleaning SSH host keys..."
sudo rm -f /etc/ssh/ssh_host_*

# 清理 bash history
echo "Cleaning bash history..."
sudo rm -f /root/.bash_history /home/ubuntu/.bash_history
history -c

# 清理 cloud-init
echo "Cleaning cloud-init..."
sudo cloud-init clean --logs

# 清理包管理缓存
echo "Cleaning package cache..."
sudo apt-get clean

echo ""
echo "=== Cleanup complete. Ready to create AMI. ==="
