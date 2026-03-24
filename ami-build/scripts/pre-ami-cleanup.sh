#!/bin/bash
# ============================================================
# Pre-AMI Cleanup Script
# 在创建 AMI 快照之前执行，清理所有敏感信息和临时文件
# ============================================================

set -e
echo "=== Pre-AMI Cleanup ==="

# 停止应用服务
echo "Stopping application services..."
sudo systemctl stop biomni-admin biomni-agent || true

# 删除初始化标记
echo "Removing initialization marker..."
sudo rm -f /opt/biomni/.initialized

# 删除生成的配置和凭据
echo "Removing generated configs and credentials..."
sudo rm -f /opt/biomni/config/biomni.env
sudo rm -f /home/ubuntu/biomni-credentials.txt

# Reset MySQL root to auth_socket so first-boot can use sudo mysql
echo "Resetting MySQL root to auth_socket..."
# Use debian-sys-maint to reset root (it always has a password in /etc/mysql/debian.cnf)
DEBIAN_PW=$(sudo grep -m1 'password' /etc/mysql/debian.cnf | awk '{print $3}')
mysql -u debian-sys-maint -p"${DEBIAN_PW}" -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH auth_socket;" 2>/dev/null || true
mysql -u debian-sys-maint -p"${DEBIAN_PW}" -e "DROP USER IF EXISTS 'biomni'@'localhost';" 2>/dev/null || true
mysql -u debian-sys-maint -p"${DEBIAN_PW}" -e "FLUSH PRIVILEGES;" 2>/dev/null || true
echo "  MySQL root reset to auth_socket."

# 清空 biomni 数据库（保留结构，清除用户数据）
echo "Cleaning biomni database user data..."
mysql -u debian-sys-maint -p"${DEBIAN_PW}" biomni -e "
DELETE FROM execution_steps;
DELETE FROM messages;
DELETE FROM attachments;
DELETE FROM conversations;
DELETE FROM user_quotas;
DELETE FROM system_config WHERE config_key LIKE '%api_key%' OR config_key LIKE '%secret%' OR config_key LIKE '%token%' OR config_key LIKE '%password%' OR config_key IN ('agent.base_url', 'llm.azure_endpoint');
DELETE FROM admin;
" 2>/dev/null || true
echo "  Database user data cleaned."

# 确保 firstboot 服务已 enable
echo "Ensuring firstboot service is enabled..."
sudo cp /opt/biomni/systemd/biomni-firstboot.service /etc/systemd/system/ 2>/dev/null || true
sudo cp /opt/biomni/systemd/biomni-admin.service /etc/systemd/system/ 2>/dev/null || true
sudo cp /opt/biomni/systemd/biomni-agent.service /etc/systemd/system/ 2>/dev/null || true
sudo systemctl daemon-reload
sudo systemctl enable biomni-firstboot biomni-admin biomni-agent

# 清理上传文件
echo "Cleaning upload data..."
sudo rm -rf /opt/biomni/upload/* 2>/dev/null || true
sudo rm -rf /opt/biomni/data/user_uploads/* 2>/dev/null || true

# 清理日志
echo "Cleaning logs..."
sudo rm -rf /opt/biomni/logs/*
sudo rm -rf /var/log/*.log 2>/dev/null || true
sudo journalctl --vacuum-time=1s

# 清理临时文件
echo "Cleaning temporary files..."
sudo rm -rf /tmp/* /var/tmp/* 2>/dev/null || true

# 清理 SSH host keys (会在下次启动时重新生成)
echo "Cleaning SSH host keys..."
sudo rm -f /etc/ssh/ssh_host_*

# 清理 bash history
echo "Cleaning bash history..."
sudo rm -f /root/.bash_history /home/ubuntu/.bash_history
history -c

# 清理 cloud-init (让新实例重新初始化)
echo "Cleaning cloud-init..."
sudo cloud-init clean --logs

# 清理包管理缓存
echo "Cleaning package cache..."
sudo apt-get clean

echo ""
echo "=== Cleanup complete. Ready to create AMI. ==="
echo "=== IMPORTANT: Verify biomni-firstboot is enabled: ==="
sudo systemctl is-enabled biomni-firstboot
