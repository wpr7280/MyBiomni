# WarpHelix AMI 构建文件

本目录包含构建 AWS Marketplace AMI 所需的所有脚本和配置文件。

## 目录结构

```
ami-build/
├── scripts/              # 运维脚本
│   ├── first-boot.sh     # 首次启动初始化（自动生成密码、配置数据库）
│   ├── health-check.sh   # 健康检查
│   ├── pre-ami-cleanup.sh # AMI 制作前清理
│   └── backup.sh         # 数据库备份
├── systemd/              # Systemd 服务文件
│   ├── biomni-firstboot.service  # 首次启动服务
│   ├── biomni-admin.service      # Spring Boot 服务
│   └── biomni-agent.service      # Agent 服务
├── config/               # 配置文件
│   ├── nginx-biomni.conf         # Nginx 配置
│   └── logrotate-biomni          # 日志轮转配置
├── sql/                  # 数据库初始化
│   └── init.sql          # 建表 + 默认数据
└── README.md             # 本文件
```

## 使用流程

### Phase A: 本地构建（开发机）

1. **修改代码**（已完成）
   - 前端改为同源访问
   - Spring Boot 敏感值改为环境变量
   - Agent 关闭 reload

2. **构建前端产物**
   ```bash
   # Client Frontend
   cd client/frontend
   npm install && npm run build
   
   # Admin Frontend
   cd admin/frontend
   pnpm install && pnpm run build
   ```

3. **构建 Spring Boot JAR**
   ```bash
   cd admin/backend
   mvn clean package -DskipTests
   # 产物: target/biomni-admin.jar
   ```

4. **（可选）Cython 编译 Agent**
   - 在目标平台（Ubuntu 22.04 + Python 3.11）上执行
   - 参考 Plan 3 第 7.2 节

### Phase B: EC2 Golden Instance 部署

1. **启动 EC2**
   - Ubuntu 22.04 LTS
   - t3.xlarge 或更大
   - 100GB gp3 EBS

2. **安装依赖**
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install -y mysql-server-8.0 redis-server nginx \
     openjdk-17-jdk-headless python3.11 python3.11-venv \
     apache2-utils fail2ban ufw
   ```

3. **创建用户和目录**
   ```bash
   sudo useradd -r -m -d /opt/biomni -s /usr/sbin/nologin biomni
   sudo mkdir -p /opt/biomni/{admin-backend,admin-frontend,client-frontend}
   sudo mkdir -p /opt/biomni/{agent,config,scripts,sql,logs,data,upload}
   ```

4. **上传文件**
   - 前端 dist → `/opt/biomni/{admin,client}-frontend/`
   - Spring Boot JAR → `/opt/biomni/admin-backend/biomni-admin.jar`
   - Agent 代码 → `/opt/biomni/agent/`
   - 本目录所有文件 → `/opt/biomni/`

5. **部署配置**
   ```bash
   # Systemd 服务
   sudo cp systemd/*.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable biomni-firstboot biomni-admin biomni-agent
   
   # Nginx
   sudo cp config/nginx-biomni.conf /etc/nginx/sites-available/biomni
   sudo ln -sf /etc/nginx/sites-available/biomni /etc/nginx/sites-enabled/
   sudo rm -f /etc/nginx/sites-enabled/default
   
   # Logrotate
   sudo cp config/logrotate-biomni /etc/logrotate.d/biomni
   
   # 脚本权限
   sudo chmod +x scripts/*.sh
   ```

6. **安装 Agent 依赖**
   ```bash
   sudo -u biomni python3.11 -m venv /opt/biomni/agent/venv
   sudo -u biomni /opt/biomni/agent/venv/bin/pip install -r /opt/biomni/agent/requirements-api.txt
   ```

7. **设置权限**
   ```bash
   sudo chown -R biomni:biomni /opt/biomni
   sudo chmod 750 /opt/biomni/agent
   sudo chmod 500 /opt/biomni/admin-backend/biomni-admin.jar
   ```

### Phase C: 测试

```bash
# 手动执行 first-boot（测试）
sudo /opt/biomni/scripts/first-boot.sh

# 查看凭据
cat ~/biomni-credentials.txt

# 健康检查
/opt/biomni/scripts/health-check.sh

# 浏览器访问
# http://<public-ip>/admin/
# http://<public-ip>/
```

### Phase D: 创建 AMI

```bash
# 1. 清理
sudo /opt/biomni/scripts/pre-ami-cleanup.sh

# 2. 停止实例并创建 AMI
aws ec2 create-image \
  --instance-id i-xxxxxxxxx \
  --name "WarpHelix-v1.0.0-$(date +%Y%m%d)" \
  --description "WarpHelix AI-Powered Biomedical Assistant"

# 3. 测试新 AMI
# 启动新实例，验证 first-boot 自动执行
```

## 关键注意事项

1. **CORS 配置**：first-boot.sh 会自动将 PUBLIC_IP 加入 CORS_ORIGINS
2. **密码安全**：所有密码在首次启动时随机生成（hex 字符集）
3. **强制改密**：默认管理员首次登录必须修改密码
4. **源码保护**：Agent 建议用 Cython 编译为 .so 文件
5. **健康检查端点**：
   - Admin: `/health/alive`
   - Agent: `/health`

## 故障排查

```bash
# 查看服务状态
sudo systemctl status biomni-admin biomni-agent

# 查看日志
sudo journalctl -u biomni-admin -f
sudo journalctl -u biomni-agent -f
tail -f /opt/biomni/logs/*.log

# 重启服务
sudo systemctl restart biomni-admin biomni-agent

# 检查端口
sudo ss -tlnp | grep -E '(9999|8000|3306|6379|80)'
```

## 参考文档

- 完整技术方案：`other/docs/AMI_BUILD_PLAN_3.md`
- 操作 Checklist：Plan 3 第 14 节
