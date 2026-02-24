# AMI 构建操作清单

按顺序执行，每完成一项打勾 ✅

## 开发机操作

### 代码修改
- [x] Client Frontend - client.ts baseURL 改为空字符串
- [x] Client Frontend - useWebSocket.ts WS 地址同源推导
- [x] Client Frontend - agentClient.ts baseURL 改为空字符串
- [x] Client Frontend - upload.ts 路径改为 /agent-api/upload
- [x] Client Frontend - 新增 .env.production
- [x] Admin Frontend - .env.production 更新
- [x] Admin Frontend - router/index.js 支持 VITE_PUBLIC_PATH
- [x] Admin Frontend - infra-client.js 移除硬编码 URL
- [x] Spring Boot - application-local.properties 敏感值改为 env
- [x] Spring Boot - application-prod.properties 敏感值改为 env
- [x] Spring Boot - 新增 application-ami.properties
- [x] Spring Boot - pom.xml 添加 finalName
- [x] Agent - config.py CORS 默认值改为 127.0.0.1
- [x] Agent - main.py reload=False

### 构建产物
- [ ] Client Frontend: `cd client/frontend && npm install && npm run build`
- [ ] Admin Frontend: `cd admin/frontend && pnpm install && pnpm run build`
- [ ] Spring Boot JAR: `cd admin/backend && mvn clean package -DskipTests`
- [ ] 验证 JAR 名称: `target/biomni-admin.jar` 存在
- [ ] 验证前端无 sourcemap: 检查 dist/ 中无 .map 文件

### 安全检查
- [ ] 确认 client/frontend/dist/ 不包含 .map 文件
- [ ] 确认 admin/frontend/dist/ 不包含 .map 文件
- [ ] 确认 biomni-admin.jar 不包含明文密码（反编译检查）
- [ ] 确认没有 .pem 文件在构建产物中
- [ ] 确认没有 .env 文件在构建产物中

## EC2 Golden Instance 操作

### 系统准备
- [ ] 启动 Ubuntu 22.04 t3.xlarge (100GB gp3)
- [ ] 安全组配置: 22/80/443 inbound
- [ ] 更新系统: `sudo apt update && sudo apt upgrade -y`
- [ ] 安装 MySQL 8.0: `sudo apt install -y mysql-server-8.0`
- [ ] 安装 Redis: `sudo apt install -y redis-server`
- [ ] 安装 Nginx: `sudo apt install -y nginx`
- [ ] 安装 Java 17: `sudo apt install -y openjdk-17-jdk-headless`
- [ ] 安装 Python 3.11: `sudo apt install -y python3.11 python3.11-venv`
- [ ] 安装工具: `sudo apt install -y apache2-utils fail2ban ufw`

### 用户和目录
- [ ] 创建 biomni 用户: `sudo useradd -r -m -d /opt/biomni -s /usr/sbin/nologin biomni`
- [ ] 创建目录结构: `sudo mkdir -p /opt/biomni/{admin-backend,admin-frontend,client-frontend,agent,config,scripts,sql,logs,data,upload}`
- [ ] 设置所有权: `sudo chown -R biomni:biomni /opt/biomni`

### 上传文件
- [ ] 上传 client/frontend/dist/* → /opt/biomni/client-frontend/
- [ ] 上传 admin/frontend/dist/* → /opt/biomni/admin-frontend/
- [ ] 上传 biomni-admin.jar → /opt/biomni/admin-backend/
- [ ] 上传 agent/ 目录 → /opt/biomni/agent/
- [ ] 上传 ami-build/scripts/* → /opt/biomni/scripts/
- [ ] 上传 ami-build/sql/init.sql → /opt/biomni/sql/
- [ ] 上传 ami-build/systemd/* → /tmp/
- [ ] 上传 ami-build/config/* → /tmp/

### 部署配置
- [ ] 部署 systemd 服务: `sudo cp /tmp/*.service /etc/systemd/system/`
- [ ] 重载 systemd: `sudo systemctl daemon-reload`
- [ ] 启用服务: `sudo systemctl enable biomni-firstboot biomni-admin biomni-agent`
- [ ] 部署 Nginx 配置: `sudo cp /tmp/nginx-biomni.conf /etc/nginx/sites-available/biomni`
- [ ] 创建软链接: `sudo ln -sf /etc/nginx/sites-available/biomni /etc/nginx/sites-enabled/`
- [ ] 删除默认站点: `sudo rm -f /etc/nginx/sites-enabled/default`
- [ ] 测试 Nginx: `sudo nginx -t`
- [ ] 部署 logrotate: `sudo cp /tmp/logrotate-biomni /etc/logrotate.d/biomni`
- [ ] 脚本权限: `sudo chmod +x /opt/biomni/scripts/*.sh`

### Agent 依赖
- [ ] 创建 venv: `sudo -u biomni python3.11 -m venv /opt/biomni/agent/venv`
- [ ] 升级 pip: `sudo -u biomni /opt/biomni/agent/venv/bin/pip install --upgrade pip`
- [ ] 安装依赖: `sudo -u biomni /opt/biomni/agent/venv/bin/pip install -r /opt/biomni/agent/requirements-api.txt`
- [ ] 验证 import: `sudo -u biomni /opt/biomni/agent/venv/bin/python -c "from biomni.agent import A1; print('OK')"`

### 安全加固
- [ ] 防火墙: `sudo ufw allow 22/tcp && sudo ufw allow 80/tcp && sudo ufw allow 443/tcp && sudo ufw --force enable`
- [ ] SSH 加固: 禁用密码登录和 root 登录
- [ ] 启用 fail2ban: `sudo systemctl enable fail2ban && sudo systemctl start fail2ban`
- [ ] 自动更新: `sudo dpkg-reconfigure -plow unattended-upgrades`
- [ ] Agent 权限: `sudo chmod 750 /opt/biomni/agent`
- [ ] JAR 权限: `sudo chmod 500 /opt/biomni/admin-backend/biomni-admin.jar`
- [ ] Config 权限: `sudo chmod 600 /opt/biomni/config/*.env` (first-boot 后)

### 测试
- [ ] 手动执行 first-boot: `sudo /opt/biomni/scripts/first-boot.sh`
- [ ] 查看凭据: `cat ~/biomni-credentials.txt`
- [ ] 健康检查: `/opt/biomni/scripts/health-check.sh` (全部通过)
- [ ] 浏览器访问管理后台: `http://<ip>/admin/`
- [ ] 用默认密码登录成功
- [ ] 强制改密提示正常
- [ ] 浏览器访问用户端: `http://<ip>/`
- [ ] 配置 LLM API Key
- [ ] 创建对话测试
- [ ] WebSocket 连接正常
- [ ] 文件上传功能正常
- [ ] 外部扫描端口: 9999/8000/3306/6379 不可达
- [ ] 重启实例: `sudo reboot`
- [ ] 重启后服务自动恢复

## AMI 制作

### 清理
- [ ] 执行清理脚本: `sudo /opt/biomni/scripts/pre-ami-cleanup.sh`
- [ ] 验证 biomni.env 已删除: `ls /opt/biomni/config/biomni.env` (不存在)
- [ ] 验证 .initialized 已删除: `ls /opt/biomni/.initialized` (不存在)
- [ ] 验证凭据已删除: `ls ~/biomni-credentials.txt` (不存在)
- [ ] 验证日志已清空: `ls /opt/biomni/logs/` (空目录)
- [ ] 验证 bash history 已清空

### 创建 AMI
- [ ] 停止实例（可选，--no-reboot 可跳过）
- [ ] 创建 AMI: `aws ec2 create-image --instance-id i-xxx --name "Biomni-v1.0.0-YYYYMMDD"`
- [ ] 等待 AMI 可用: `aws ec2 wait image-available --image-ids ami-xxx`
- [ ] 记录 AMI ID: _______________

## 回归验证

### 新实例测试
- [ ] 从新 AMI 启动实例
- [ ] 等待 3-5 分钟（first-boot 执行）
- [ ] SSH 登录查看 MOTD
- [ ] 查看凭据: `cat ~/biomni-credentials.txt` (存在且密码随机)
- [ ] 健康检查: `/opt/biomni/scripts/health-check.sh` (全部通过)
- [ ] 管理后台可访问
- [ ] 用户端可访问
- [ ] 默认密码可登录
- [ ] 首次登录强制改密
- [ ] 配置 LLM Key 后可对话
- [ ] WebSocket 正常
- [ ] 文件上传正常
- [ ] 端口安全（外部不可达）
- [ ] 重启后服务恢复

### 多次启动验证
- [ ] 启动第二个实例，密码与第一个不同
- [ ] 启动第三个实例，密码与前两个不同

## AWS Marketplace 提交

- [ ] 准备产品描述和截图
- [ ] 准备使用文档
- [ ] 提交 AMI ID 到 Marketplace
- [ ] 等待安全扫描通过
- [ ] 发布产品

---

**完成日期**: _______________
**AMI ID**: _______________
**测试实例 IP**: _______________
