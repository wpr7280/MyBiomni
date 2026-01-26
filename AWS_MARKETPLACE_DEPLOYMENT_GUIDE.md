# Biomni AWS Marketplace AMI 部署指南

## 目录
1. [AMI 镜像准备](#1-ami-镜像准备)
2. [代码保护策略](#2-代码保护策略)
3. [AWS Marketplace 发布流程](#3-aws-marketplace-发布流程)
4. [定价和许可策略](#4-定价和许可策略)
5. [安全和合规](#5-安全和合规)
6. [用户体验优化](#6-用户体验优化)

---

## 1. AMI 镜像准备

### 1.1 基础架构设计

**推荐架构：单实例 All-in-One**
```
EC2 Instance (推荐 t3.xlarge 或更高)
├── MySQL 8.0 (本地安装)
├── Python Agent (FastAPI)
├── Spring Boot Backend (管理后台)
├── Vue.js Frontend (管理前端)
├── React Frontend (用户客户端)
└── Nginx (反向代理)
```

**或者：分离式架构**
```
EC2 Instance + RDS MySQL
├── Python Agent
├── Spring Boot Backend
├── Vue.js Frontend
└── React Frontend
```

### 1.2 AMI 构建步骤

#### Step 1: 启动基础 EC2 实例
```bash
# 选择基础镜像
- Ubuntu 22.04 LTS (推荐)
- Amazon Linux 2023
- 实例类型: t3.xlarge (4 vCPU, 16GB RAM)
```

#### Step 2: 安装系统依赖
```bash
#!/bin/bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装基础工具
sudo apt install -y curl wget git vim htop

# 安装 Docker 和 Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# 安装 MySQL 8.0
sudo apt install -y mysql-server-8.0

# 安装 Python 3.11
sudo apt install -y python3.11 python3.11-venv python3-pip

# 安装 Java 17 (for Spring Boot)
sudo apt install -y openjdk-17-jdk

# 安装 Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# 安装 Nginx
sudo apt install -y nginx
```

#### Step 3: 部署应用（编译后的版本）

**重要：不要包含源代码！**

```bash
# 创建应用目录
sudo mkdir -p /opt/biomni/{agent,admin-backend,admin-frontend,client-frontend}

# 部署 Python Agent (编译为 .pyc 或使用 PyInstaller)
# 详见代码保护部分

# 部署 Spring Boot (JAR 文件)
sudo cp admin-backend/target/biomni-admin-*.jar /opt/biomni/admin-backend/

# 部署前端（构建后的静态文件）
sudo cp -r admin-frontend/dist/* /opt/biomni/admin-frontend/
sudo cp -r client-frontend/dist/* /opt/biomni/client-frontend/
```

#### Step 4: 配置 Systemd 服务

**Python Agent Service**
```ini
# /etc/systemd/system/biomni-agent.service
[Unit]
Description=Biomni AI Agent
After=network.target mysql.service

[Service]
Type=simple
User=biomni
WorkingDirectory=/opt/biomni/agent
ExecStart=/opt/biomni/agent/biomni-agent
Restart=always
RestartSec=10
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
```

**Spring Boot Backend Service**
```ini
# /etc/systemd/system/biomni-admin.service
[Unit]
Description=Biomni Admin Backend
After=network.target mysql.service

[Service]
Type=simple
User=biomni
WorkingDirectory=/opt/biomni/admin-backend
ExecStart=/usr/bin/java -jar biomni-admin.jar
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Step 5: 配置 Nginx

```nginx
# /etc/nginx/sites-available/biomni
server {
    listen 80;
    server_name _;

    # Admin Frontend
    location /admin {
        alias /opt/biomni/admin-frontend;
        try_files $uri $uri/ /admin/index.html;
    }

    # Client Frontend
    location / {
        root /opt/biomni/client-frontend;
        try_files $uri $uri/ /index.html;
    }

    # Admin Backend API
    location /api/admin {
        proxy_pass http://localhost:8083;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Agent API
    location /api/agent {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # WebSocket
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

#### Step 6: 初始化脚本

```bash
#!/bin/bash
# /opt/biomni/scripts/first-boot.sh

# 生成随机密码
MYSQL_ROOT_PASSWORD=$(openssl rand -base64 32)
ADMIN_PASSWORD=$(openssl rand -base64 16)

# 配置 MySQL
mysql -u root <<EOF
ALTER USER 'root'@'localhost' IDENTIFIED BY '${MYSQL_ROOT_PASSWORD}';
CREATE DATABASE biomni CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'biomni'@'localhost' IDENTIFIED BY '${MYSQL_ROOT_PASSWORD}';
GRANT ALL PRIVILEGES ON biomni.* TO 'biomni'@'localhost';
FLUSH PRIVILEGES;
EOF

# 导入数据库结构
mysql -u biomni -p${MYSQL_ROOT_PASSWORD} biomni < /opt/biomni/sql/schema.sql

# 创建默认管理员
mysql -u biomni -p${MYSQL_ROOT_PASSWORD} biomni <<EOF
INSERT INTO admin (username, email, password, role, status) 
VALUES ('admin', 'admin@biomni.com', '${ADMIN_PASSWORD}', 'super_admin', 1);
EOF

# 保存凭据到文件
cat > /home/ubuntu/biomni-credentials.txt <<EOF
===========================================
Biomni Installation Credentials
===========================================

MySQL Root Password: ${MYSQL_ROOT_PASSWORD}
Admin Username: admin
Admin Password: ${ADMIN_PASSWORD}

Admin Portal: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)/admin
Client Portal: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)

IMPORTANT: Please change these passwords immediately after first login!
===========================================
EOF

chmod 600 /home/ubuntu/biomni-credentials.txt

# 启动服务
systemctl enable biomni-agent biomni-admin nginx
systemctl start biomni-agent biomni-admin nginx

echo "Biomni installation completed!"
```

#### Step 7: 清理和优化

```bash
# 清理敏感信息
sudo rm -rf /root/.bash_history /home/ubuntu/.bash_history
sudo rm -rf /var/log/*.log
sudo rm -rf /tmp/*

# 清理源代码（如果有）
sudo rm -rf /opt/biomni/src

# 清理包管理器缓存
sudo apt clean
sudo apt autoclean

# 清理 SSH keys
sudo rm -rf /etc/ssh/ssh_host_*
sudo rm -rf /home/ubuntu/.ssh/authorized_keys

# 停止服务（AMI 创建前）
sudo systemctl stop biomni-agent biomni-admin nginx mysql
```

#### Step 8: 创建 AMI

```bash
# 在 AWS Console 或使用 CLI
aws ec2 create-image \
  --instance-id i-1234567890abcdef0 \
  --name "Biomni-v1.0.0-$(date +%Y%m%d)" \
  --description "Biomni AI-Powered Biomedical Assistant" \
  --no-reboot
```

---

## 2. 代码保护策略

### 2.1 Python 代码保护

#### 方案 1: PyInstaller 打包（推荐）
```bash
# 安装 PyInstaller
pip install pyinstaller

# 打包为单个可执行文件
pyinstaller --onefile \
  --hidden-import=biomni \
  --add-data "biomni/know_how:biomni/know_how" \
  --name biomni-agent \
  agent/main.py

# 结果：dist/biomni-agent (二进制文件，无法反编译)
```

**优点：**
- 完全编译为二进制，无法轻易反编译
- 包含所有依赖，部署简单
- 性能好

**缺点：**
- 文件较大
- 需要针对不同平台编译

#### 方案 2: Cython 编译
```bash
# 安装 Cython
pip install cython

# 编译 Python 代码为 C 扩展
# setup.py
from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize(
        "biomni/**/*.py",
        compiler_directives={'language_level': "3"}
    )
)

# 编译
python setup.py build_ext --inplace

# 删除 .py 文件，只保留 .so 文件
find biomni -name "*.py" -delete
```

**优点：**
- 编译为 C 扩展，难以反编译
- 性能提升
- 文件较小

**缺点：**
- 需要编译环境
- 调试困难

#### 方案 3: 代码混淆 + PyArmor
```bash
# 安装 PyArmor
pip install pyarmor

# 混淆代码
pyarmor obfuscate --recursive \
  --output dist/biomni \
  agent/main.py

# 结果：混淆后的 .py 文件，运行时解密
```

**优点：**
- 保持 Python 格式
- 加密保护
- 可以设置过期时间

**缺点：**
- 仍然是 Python 字节码，有被破解风险
- 性能略有下降

### 2.2 Java 代码保护

#### 方案 1: ProGuard 混淆（推荐）
```xml
<!-- pom.xml -->
<plugin>
    <groupId>com.github.wvengen</groupId>
    <artifactId>proguard-maven-plugin</artifactId>
    <version>2.6.0</version>
    <executions>
        <execution>
            <phase>package</phase>
            <goals>
                <goal>proguard</goal>
            </goals>
        </execution>
    </executions>
    <configuration>
        <obfuscate>true</obfuscate>
        <options>
            <option>-keep public class com.qusu.mybiomni.Application { *; }</option>
            <option>-keepclassmembers class * { @org.springframework.beans.factory.annotation.Autowired *; }</option>
        </options>
    </configuration>
</plugin>
```

#### 方案 2: 商业加密工具
- **Excelsior JET**: 编译为原生代码
- **JObfuscator**: 商业级混淆
- **Allatori**: 字符串加密 + 流程混淆

### 2.3 前端代码保护

#### 方案 1: 代码混淆 + 压缩
```javascript
// vite.config.js / vue.config.js
export default {
  build: {
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
      },
      mangle: {
        toplevel: true,
      },
      format: {
        comments: false,
      },
    },
  },
}
```

#### 方案 2: 代码分割 + 动态加载
```javascript
// 关键业务逻辑动态加载
const criticalModule = await import(/* webpackChunkName: "critical" */ './critical.js');
```

#### 方案 3: WebAssembly
```javascript
// 将核心算法编译为 WASM
import init, { process_data } from './biomni_core.wasm';
```

### 2.4 数据库和配置保护

```bash
# 加密配置文件
# 使用 AWS Secrets Manager 或 Parameter Store

# application.properties
spring.datasource.password=${AWS_SECRET:biomni-db-password}

# 环境变量
export BIOMNI_DB_PASSWORD=$(aws secretsmanager get-secret-value \
  --secret-id biomni-db-password \
  --query SecretString \
  --output text)
```

### 2.5 许可证验证机制

```python
# license_validator.py
import hashlib
import hmac
from datetime import datetime

class LicenseValidator:
    def __init__(self):
        self.secret_key = self._get_hardware_id()
    
    def _get_hardware_id(self):
        """获取硬件指纹"""
        # EC2 Instance ID
        import requests
        instance_id = requests.get(
            'http://169.254.169.254/latest/meta-data/instance-id',
            timeout=1
        ).text
        return instance_id
    
    def validate_license(self, license_key):
        """验证许可证"""
        # 检查许可证格式
        # 验证签名
        # 检查过期时间
        # 验证硬件绑定
        pass
    
    def check_online_activation(self):
        """在线激活验证"""
        # 定期向许可服务器验证
        pass
```

### 2.6 运行时保护

```python
# 反调试检测
import sys
import os

def anti_debug():
    """检测调试器"""
    if sys.gettrace() is not None:
        print("Debugger detected!")
        sys.exit(1)
    
    # 检查环境变量
    if 'PYTHONDEBUG' in os.environ:
        sys.exit(1)

# 完整性检查
import hashlib

def verify_integrity():
    """验证文件完整性"""
    expected_hash = "..."  # 预计算的哈希值
    actual_hash = hashlib.sha256(open(__file__, 'rb').read()).hexdigest()
    if expected_hash != actual_hash:
        sys.exit(1)
```

---

## 3. AWS Marketplace 发布流程

### 3.1 准备工作

1. **注册 AWS Marketplace 卖家账户**
   - 访问 https://aws.amazon.com/marketplace/management/
   - 完成卖家注册
   - 提供税务信息（W-9 或 W-8）
   - 设置银行账户

2. **准备产品信息**
   - 产品名称：Biomni - AI-Powered Biomedical Assistant
   - 简短描述（160 字符）
   - 详细描述（Markdown 格式）
   - 产品 Logo（120x120 px）
   - 截图（至少 3 张）
   - 演示视频（可选）
   - 产品文档 URL

3. **准备技术文档**
   - 安装指南
   - 用户手册
   - API 文档
   - 故障排除指南
   - 安全最佳实践

### 3.2 AMI 提交流程

#### Step 1: 创建产品列表
```
AWS Marketplace Management Portal
→ Products
→ Server
→ Create Server Product
```

#### Step 2: 填写产品信息
```yaml
Product Title: Biomni - AI-Powered Biomedical Assistant
Short Description: |
  Universal biomedical AI agent providing intelligent data analysis,
  literature search, and experimental design support for researchers.

Long Description: |
  Biomni is a comprehensive SaaS platform that combines cutting-edge AI
  technology with biomedical domain expertise...

Categories:
  - Machine Learning & AI
  - Healthcare & Life Sciences
  - Developer Tools

Keywords:
  - Biomedical AI
  - Research Assistant
  - Data Analysis
  - Literature Search
```

#### Step 3: 上传 AMI
```bash
# 1. 共享 AMI 到 AWS Marketplace 账户
aws ec2 modify-image-attribute \
  --image-id ami-xxxxx \
  --launch-permission "Add=[{UserId=679593333241}]"

# 2. 在 Marketplace Portal 中扫描 AMI
# AWS 会自动扫描安全漏洞和合规性

# 3. 等待扫描结果（通常 1-2 小时）
```

#### Step 4: 配置定价
```yaml
Pricing Model: Hourly with Annual
Hourly Rates:
  - t3.xlarge: $0.50/hour (+ EC2 cost)
  - t3.2xlarge: $1.00/hour (+ EC2 cost)

Annual Contract:
  - Standard: $5,000/year
  - Professional: $15,000/year
  - Enterprise: $50,000/year

Free Trial: 14 days
```

#### Step 5: 设置支持信息
```yaml
Support Channels:
  - Email: support@biomni.com
  - Documentation: https://docs.biomni.com
  - Community Forum: https://community.biomni.com

Support Tiers:
  - Community (Free): Email support, 48h response
  - Professional: Priority email, 24h response
  - Enterprise: 24/7 phone + email, 4h response
```

#### Step 6: 提交审核
```
Review all information
→ Submit for Review
→ Wait for AWS approval (5-10 business days)
```

### 3.3 审核要点

AWS 会检查：
- ✅ AMI 安全扫描（无高危漏洞）
- ✅ 产品描述准确性
- ✅ 定价合理性
- ✅ 支持渠道可用性
- ✅ 文档完整性
- ✅ 许可证合规性

---

## 4. 定价和许可策略

### 4.1 定价模型

#### 模型 1: 按使用量计费（推荐）
```
基础费用: $0.50/hour
+ EC2 实例费用
+ 按 Token 使用量额外收费: $0.01/1000 tokens
```

#### 模型 2: 订阅制
```
Starter: $99/month
  - 1M tokens/month
  - 5 users
  - Community support

Professional: $499/month
  - 10M tokens/month
  - 25 users
  - Priority support

Enterprise: $2,999/month
  - Unlimited tokens
  - Unlimited users
  - 24/7 support
  - Custom deployment
```

#### 模型 3: 混合模式
```
基础订阅: $199/month
+ 超出部分按量计费: $0.01/1000 tokens
```

### 4.2 许可证类型

```python
# license_types.py
class LicenseType(Enum):
    TRIAL = "trial"           # 14天试用
    STARTER = "starter"       # 基础版
    PROFESSIONAL = "pro"      # 专业版
    ENTERPRISE = "enterprise" # 企业版
    ACADEMIC = "academic"     # 学术版（非商业）

class LicenseFeatures:
    TRIAL = {
        "duration_days": 14,
        "max_users": 2,
        "max_tokens_per_month": 100000,
        "support_level": "community",
    }
    
    PROFESSIONAL = {
        "duration_days": 365,
        "max_users": 25,
        "max_tokens_per_month": 10000000,
        "support_level": "priority",
        "custom_models": True,
    }
```

---

## 5. 安全和合规

### 5.1 安全加固

```bash
# 1. 防火墙配置
sudo ufw enable
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS

# 2. SSH 加固
sudo sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo sed -i 's/#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config

# 3. 自动安全更新
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades

# 4. 入侵检测
sudo apt install -y fail2ban
sudo systemctl enable fail2ban
```

### 5.2 合规性

#### HIPAA 合规（如果处理医疗数据）
- ✅ 数据加密（传输和静态）
- ✅ 访问控制和审计日志
- ✅ 数据备份和恢复
- ✅ 业务连续性计划

#### GDPR 合规
- ✅ 数据隐私声明
- ✅ 用户数据导出功能
- ✅ 数据删除功能
- ✅ Cookie 同意机制

### 5.3 监控和日志

```yaml
# CloudWatch 集成
Metrics:
  - CPU Utilization
  - Memory Usage
  - Disk I/O
  - Network Traffic
  - Application Errors

Logs:
  - Application Logs → CloudWatch Logs
  - Access Logs → S3
  - Audit Logs → CloudWatch Logs (encrypted)

Alarms:
  - High CPU (> 80%)
  - High Memory (> 90%)
  - Application Errors (> 10/min)
  - Disk Space (> 85%)
```

---

## 6. 用户体验优化

### 6.1 首次启动体验

```bash
# /etc/motd (Message of the Day)
cat > /etc/motd <<'EOF'
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   🧬 Welcome to Biomni - AI-Powered Biomedical Assistant ║
║                                                           ║
║   Quick Start:                                            ║
║   1. View credentials: cat ~/biomni-credentials.txt       ║
║   2. Access Admin Portal: http://YOUR_IP/admin           ║
║   3. Access Client Portal: http://YOUR_IP                ║
║                                                           ║
║   Documentation: https://docs.biomni.com                  ║
║   Support: support@biomni.com                             ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
EOF
```

### 6.2 健康检查脚本

```bash
#!/bin/bash
# /opt/biomni/scripts/health-check.sh

echo "Biomni Health Check"
echo "==================="

# Check services
services=("biomni-agent" "biomni-admin" "nginx" "mysql")
for service in "${services[@]}"; do
    if systemctl is-active --quiet $service; then
        echo "✓ $service is running"
    else
        echo "✗ $service is NOT running"
    fi
done

# Check ports
ports=(80 8000 8083 3306)
for port in "${ports[@]}"; do
    if netstat -tuln | grep -q ":$port "; then
        echo "✓ Port $port is listening"
    else
        echo "✗ Port $port is NOT listening"
    fi
done

# Check disk space
df -h | grep -E '^/dev/' | awk '{print "Disk: " $1 " - Used: " $5}'

# Check memory
free -h | grep Mem | awk '{print "Memory: Used " $3 " / Total " $2}'
```

### 6.3 自动备份

```bash
#!/bin/bash
# /opt/biomni/scripts/backup.sh

BACKUP_DIR="/opt/biomni/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup database
mysqldump -u biomni -p${MYSQL_PASSWORD} biomni > ${BACKUP_DIR}/biomni_${DATE}.sql

# Backup configuration
tar -czf ${BACKUP_DIR}/config_${DATE}.tar.gz /opt/biomni/config

# Upload to S3 (optional)
aws s3 cp ${BACKUP_DIR}/biomni_${DATE}.sql s3://biomni-backups/

# Keep only last 7 days
find ${BACKUP_DIR} -name "*.sql" -mtime +7 -delete
```

---

## 7. 发布后运营

### 7.1 监控指标

```yaml
Business Metrics:
  - New Installations/day
  - Active Users
  - Token Usage
  - Conversion Rate (Trial → Paid)
  - Churn Rate
  - MRR (Monthly Recurring Revenue)

Technical Metrics:
  - Uptime (Target: 99.9%)
  - Response Time (Target: < 200ms)
  - Error Rate (Target: < 0.1%)
  - API Success Rate (Target: > 99%)
```

### 7.2 更新策略

```bash
# 版本更新流程
1. 创建新 AMI 版本
2. 在 Marketplace 中发布新版本
3. 通知现有用户
4. 提供升级脚本

# /opt/biomni/scripts/upgrade.sh
#!/bin/bash
echo "Upgrading Biomni to version $NEW_VERSION"
# 下载新版本
# 备份当前版本
# 停止服务
# 替换文件
# 迁移数据库
# 启动服务
```

### 7.3 客户支持

```yaml
Support Channels:
  - Email: support@biomni.com
  - Slack Community: biomni.slack.com
  - GitHub Issues: github.com/biomni/issues
  - Documentation: docs.biomni.com
  - Video Tutorials: youtube.com/biomni

Response SLA:
  - Critical (P0): 1 hour
  - High (P1): 4 hours
  - Medium (P2): 24 hours
  - Low (P3): 48 hours
```

---

## 8. 成本估算

### 8.1 AWS 成本

```
EC2 Instance (t3.xlarge):
  - On-Demand: $0.1664/hour = ~$120/month
  - Reserved (1 year): ~$85/month
  - Spot: ~$50/month

Storage (100GB EBS):
  - $10/month

Data Transfer:
  - First 1GB: Free
  - Next 10TB: $0.09/GB

Total Monthly Cost: ~$100-150/instance
```

### 8.2 收入预测

```
Scenario 1: Conservative
  - 10 customers @ $499/month = $4,990/month
  - Costs: $1,500/month (10 instances)
  - Profit: $3,490/month

Scenario 2: Moderate
  - 50 customers @ $499/month = $24,950/month
  - Costs: $7,500/month (50 instances)
  - Profit: $17,450/month

Scenario 3: Optimistic
  - 200 customers @ $499/month = $99,800/month
  - Costs: $30,000/month (200 instances)
  - Profit: $69,800/month
```

---

## 9. 检查清单

### 发布前检查

- [ ] AMI 已完成安全扫描
- [ ] 所有源代码已移除
- [ ] 代码已混淆/编译
- [ ] 许可证验证机制已实现
- [ ] 首次启动脚本已测试
- [ ] 健康检查脚本正常工作
- [ ] 文档已完成
- [ ] 定价策略已确定
- [ ] 支持渠道已建立
- [ ] 备份机制已配置
- [ ] 监控已设置
- [ ] 合规性已审查

### 发布后检查

- [ ] 监控新安装
- [ ] 收集用户反馈
- [ ] 跟踪错误和问题
- [ ] 定期更新 AMI
- [ ] 响应支持请求
- [ ] 分析使用数据
- [ ] 优化成本
- [ ] 改进文档

---

## 10. 参考资源

- [AWS Marketplace Seller Guide](https://docs.aws.amazon.com/marketplace/latest/userguide/)
- [AMI Best Practices](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AMIs.html)
- [AWS Marketplace Security](https://docs.aws.amazon.com/marketplace/latest/userguide/product-and-ami-policies.html)
- [PyInstaller Documentation](https://pyinstaller.org/)
- [ProGuard Manual](https://www.guardsquare.com/manual/home)

---

**最后更新**: 2025-01-21  
**版本**: 1.0  
**作者**: Biomni Team
