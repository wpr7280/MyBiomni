# MyBiomni AMI 构建技术方案（Plan 3 — 最终合并版）

最后更新：2026-02-08

---

## 0. 三条硬规则

1. **前端永远同源**：浏览器只访问 `http(s)://<IP>/...`，不暴露后端端口，不需要按实例重编译前端。
2. **配置只在首启生成**：所有密码/密钥在第一次启动时生成，写入单一 `biomni.env`，服务通过 systemd `EnvironmentFile=` 注入。
3. **AMI 中零敏感信息**：制作 AMI 前必须清理所有已生成的 env、凭据、日志、bash_history、私钥。

---

## 1. 目标架构（All-in-One 单实例）

### 1.1 组件与端口

| 组件 | 监听地址 | 端口 | 对外 |
|------|---------|------|------|
| Nginx | 0.0.0.0 | 80/443 | ✅ 唯一入口 |
| Admin Backend (Spring Boot) | 127.0.0.1 | 9999 | ❌ |
| Agent (FastAPI) | 127.0.0.1 | 8000 | ❌ |
| MySQL 8.0 | 127.0.0.1 | 3306 | ❌ |
| Redis 7.x | 127.0.0.1 | 6379 | ❌ |

安全组：Inbound 仅 80、443、22（建议限源 IP）；Outbound 全开（Agent 需访问外部 LLM API）。

### 1.2 Nginx 路由

| 外部路径 | 目标 | 说明 |
|----------|------|------|
| `/` | `/opt/biomni/client-frontend/` | 用户端 React 静态文件 |
| `/admin/` | `/opt/biomni/admin-frontend/` | 管理后台 Vue 静态文件 |
| `/api/` | `proxy http://127.0.0.1:9999/api/` | Spring Boot API |
| `/ws/` | `proxy http://127.0.0.1:8000/ws/` | Agent WebSocket |
| `/agent-api/` | `proxy http://127.0.0.1:8000/api/` | Agent REST（上传等） |

Nginx 配置为固定文件，内部端口不变，不需要模板渲染。

### 1.3 没有域名怎么办

默认不依赖域名，直接用 Public IP 访问：
- 管理后台：`http://<public-ip>/admin/`
- 用户端：`http://<public-ip>/`
- WebSocket：前端基于 `window.location` 自动推导 `ws://<public-ip>/ws/...`

Public IP 会变的问题：
- 测试/临时：接受 IP 变化，需要时查看控制台。
- 生产（推荐）：绑定 Elastic IP (EIP)。

HTTPS：
- 没有域名时先用 HTTP（公共 CA 不为裸 IP 签证书）。
- 客户自带域名时：`sudo apt install certbot python3-certbot-nginx && sudo certbot --nginx -d your-domain.com`
- 或在 ALB/CloudFront 前终止 TLS，实例仍提供 HTTP。

---

## 2. 现状：必须处理的硬编码与敏感信息

### 2.1 Admin Backend (Spring Boot)

**文件：`application-local.properties` / `application-prod.properties`**

| 配置项 | 当前值 | 问题 |
|--------|--------|------|
| `spring.datasource.mysql.password` | `qusuyinqing@xjtu28` | 硬编码明文密码 |
| `spring.datasource.mysql.username` | `root` | 应使用专用用户 |
| `jwt.secret` | `mySecretKeyForJWT...` | 硬编码，所有实例共享 |
| `spring.data.redis.host` | `redis.service.consul` (prod) | AMI 需改为 localhost |
| `spring.mail.*` | 飞书 SMTP 凭证 `u2DFNPzhVlK9P437` | 硬编码邮箱密码 |
| `spring.datasource.mysql.driver-class-name` | `com.mysql.jdbc.Driver` | MySQL 5.x 旧驱动，8.0 应为 `com.mysql.cj.jdbc.Driver` |
| `server.port` | 9999 / 19999 | AMI 统一 9999 |

### 2.2 Agent (FastAPI)

**文件：`agent/.env` / `agent/core/config.py`**

| 配置项 | 当前值 | 问题 |
|--------|--------|------|
| `JWT_SECRET_KEY` | 与 Spring Boot 相同硬编码值 | 需动态生成，两端同步 |
| `DATABASE_URL` | `root:qusuyinqing%40xjtu28@localhost:3306/biomni` | 硬编码密码 |
| `USE_MOCK_AGENT` | `true` | AMI 必须 `false` |
| `CORS_ORIGINS` | `localhost:3001,3000` | AMI 需设为 `127.0.0.1` + `PUBLIC_IP` |
| `SPRING_BOOT_URL` | `http://localhost:8083` | 端口应为 9999 |

### 2.3 前端

| 文件 | 配置项 | 问题 |
|------|--------|------|
| `client/frontend/src/api/client.ts` | `baseURL` 默认 `http://localhost:8083` | 需改为同源空字符串 |
| `client/frontend/src/hooks/useWebSocket.ts` | `wsUrl` 默认 `ws://localhost:8000` | 需改为同源推导 |
| `client/frontend/src/api/agentClient.ts` | `baseURL` 默认 `http://localhost:8000` | 需改为同源 |
| `admin/frontend/.env.production` | `VITE_API_BASE_URL=http://your-domain.com:8080/api` | 需改为 `/api` |
| `admin/frontend/src/utils/http/infra-client.js` | 硬编码 `https://api.e2b.9527.tech` | 需通过 env 配置或移除 |

### 2.4 数据库初始化

| 文件 | 问题 |
|------|------|
| `init.sql` 默认管理员 | BCrypt hash 固定，所有实例相同 |
| `init.sql` 无 `force_password_change` | 首次登录不强制改密 |

### 2.5 必须从 AMI 中排除的敏感文件

| 文件 | 原因 |
|------|------|
| `biomni.pem` (根目录) | SSH 私钥 |
| `admin/frontend/src/biomni.pem` | SSH 私钥副本 |
| `.git/` | Git 历史可能包含密码提交记录 |
| `admin/backend/deploy.sh` | 包含服务器 IP `39.103.178.214` |
| `admin/backend/logs/` | 开发环境日志 |
| `agent/.env` | 包含明文数据库密码 |
| `docker-compose.yml` | 包含明文密码 |
| `README.md` | 包含服务器 IP 和部署命令 |

---

## 3. 配置注入方案：单一 `biomni.env`

### 3.1 设计原则

- **能用 env 覆盖就不用模板**：Spring Boot relaxed binding 天然支持环境变量覆盖 properties；Agent 的 Pydantic Settings 天然支持 env。
- **单一配置源**：所有服务共享 `/opt/biomni/config/biomni.env`，systemd 通过 `EnvironmentFile=` 注入。
- **不用 sed 替换**：避免特殊字符转义问题。
- **Nginx 固定配置**：内部端口不变，不需要渲染。

### 3.2 `biomni.env` 结构

```bash
# /opt/biomni/config/biomni.env  (chmod 600, owned by biomni)
# 由 first-boot.sh 生成，不要手动编辑

# ---- MySQL ----
BIOMNI_DB_HOST=127.0.0.1
BIOMNI_DB_PORT=3306
BIOMNI_DB_NAME=biomni
BIOMNI_DB_USER=biomni
BIOMNI_DB_PASSWORD=<hex-48-chars>
MYSQL_ROOT_PASSWORD=<hex-48-chars>

# ---- JWT (Spring Boot + Agent 共享) ----
BIOMNI_JWT_SECRET=<hex-64-chars>

# ---- Redis ----
BIOMNI_REDIS_PASSWORD=<hex-48-chars>

# ---- Spring Boot env override (relaxed binding) ----
SPRING_PROFILES_ACTIVE=ami
SERVER_PORT=9999
SPRING_DATASOURCE_MYSQL_JDBC_URL=jdbc:mysql://127.0.0.1:3306/biomni?useUnicode=true&characterEncoding=utf8&useSSL=false&serverTimezone=GMT%2B8
SPRING_DATASOURCE_MYSQL_USERNAME=biomni
SPRING_DATASOURCE_MYSQL_PASSWORD=<same as BIOMNI_DB_PASSWORD>
SPRING_DATASOURCE_MYSQL_DRIVER_CLASS_NAME=com.mysql.cj.jdbc.Driver
JWT_SECRET=<same as BIOMNI_JWT_SECRET>
JWT_EXPIRATION=86400000
SPRING_DATA_REDIS_HOST=127.0.0.1
SPRING_DATA_REDIS_PORT=6379
SPRING_DATA_REDIS_PASSWORD=<same as BIOMNI_REDIS_PASSWORD>

# ---- Agent env ----
JWT_SECRET_KEY=<same as BIOMNI_JWT_SECRET>
JWT_ALGORITHM=HS512
DATABASE_URL=mysql+pymysql://biomni:<BIOMNI_DB_PASSWORD>@127.0.0.1:3306/biomni
USE_MOCK_AGENT=false
AGENT_DATA_PATH=/opt/biomni/data
AGENT_UPLOAD_DATA_PATH=/opt/biomni/upload
CORS_ORIGINS=["http://127.0.0.1","http://<PUBLIC_IP>"]
SPRING_BOOT_URL=http://127.0.0.1:9999
```

### 3.3 密码生成策略

使用 hex 字符集 `[0-9a-f]`，天然不需要 URL encode，不会被 sed/shell 转义：

```bash
BIOMNI_DB_PASSWORD="$(openssl rand -hex 24)"       # 48 chars
MYSQL_ROOT_PASSWORD="$(openssl rand -hex 24)"       # 48 chars
BIOMNI_JWT_SECRET="$(openssl rand -hex 32)"         # 64 chars
BIOMNI_REDIS_PASSWORD="$(openssl rand -hex 24)"     # 48 chars
ADMIN_PASSWORD="$(openssl rand -base64 18 | tr -d '=+/')"  # 用户可读的初始密码
```


---

## 4. 代码修改清单（按模块）

### 4.1 Spring Boot（Admin Backend）

#### 4.1.1 清理 properties 中的明文敏感项

`application-local.properties` 和 `application-prod.properties` 中的敏感值改为 env 占位，避免被打进 JAR：

```properties
spring.datasource.mysql.password=${SPRING_DATASOURCE_MYSQL_PASSWORD:}
jwt.secret=${JWT_SECRET:}
spring.mail.password=${SPRING_MAIL_PASSWORD:}
```

同时将 driver 从 `com.mysql.jdbc.Driver` 更新为 `com.mysql.cj.jdbc.Driver`（MySQL 8.0 要求）。

#### 4.1.2 新增 `application-ami.properties`

路径：`admin/backend/src/main/resources/application-ami.properties`

只写非敏感默认值，敏感项全部由 `biomni.env` 中的环境变量覆盖（Spring Boot relaxed binding）：

```properties
server.port=${SERVER_PORT:9999}
spring.datasource.mysql.driver-class-name=com.mysql.cj.jdbc.Driver
spring.datasource.mysql.hikari.minimum-idle=5
spring.datasource.mysql.hikari.maximum-pool-size=20
mybatis.mapper-locations=classpath:mapper/*.xml
mybatis.configuration.map-underscore-to-camel-case=true
server.servlet.session.timeout=120m
spring.jackson.serialization.write-dates-as-timestamps=true
logging.level.com.qusu.mybiomni=info
spring.servlet.multipart.max-file-size=20MB
spring.servlet.multipart.max-request-size=20MB
spring.jpa.hibernate.ddl-auto=validate
spring.jpa.show-sql=false
jwt.expiration=${JWT_EXPIRATION:86400000}
spring.cache.type=redis
spring.cache.redis.time-to-live=3600000
spring.cache.redis.cache-null-values=false
spring.cache.redis.use-key-prefix=true
```

systemd 启动时通过 `SPRING_PROFILES_ACTIVE=ami` 激活此 profile，所有密码/密钥由 env 注入，不需要 sed 替换。

#### 4.1.3 修改 `pom.xml` 统一 JAR 名

当前 artifactId 是 `my-biomni`，默认产物名 `my-biomni-0.0.1-SNAPSHOT.jar`。在 `<build>` 中添加：

```xml
<build>
    <finalName>biomni-admin</finalName>
    ...
</build>
```

统一为 `biomni-admin.jar`，方便 systemd 和运维脚本引用。

### 4.2 Agent（FastAPI）

#### 4.2.1 `main.py` 关闭热重载

当前代码：

```python
uvicorn.run(
    "api.app:app",
    host="0.0.0.0",
    port=8000,
    reload=True,      # ← 开发模式
    log_level="info"
)
```

AMI 版本必须改为：

```python
uvicorn.run(
    "api.app:app",
    host="0.0.0.0",
    port=8000,
    reload=False,      # 生产环境关闭热重载
    log_level="info"
)
```

或者更好的做法——systemd 直接用命令行启动，不走 `main.py`：

```bash
ExecStart=/opt/biomni/agent/venv/bin/uvicorn api.app:app --host 127.0.0.1 --port 8000 --log-level info
```

> ⚠️ 保持 `workers=1`。当前 `ConnectionManager` 使用内存字典存储 WebSocket 连接，多 worker 下不共享状态。

#### 4.2.2 CORS 配置

`agent/core/config.py` 中 `CORS_ORIGINS` 默认值改为 `["http://127.0.0.1"]`，AMI 中由 `biomni.env` 覆盖。

> ⚠️ **必须在 first-boot 时把 PUBLIC_IP 加入 CORS_ORIGINS**。虽然请求经过 Nginx 代理到 127.0.0.1，但浏览器发送的 `Origin` header 仍然是 `http://<public-ip>`。FastAPI 的 CORSMiddleware 会校验 Origin，如果不在允许列表中，preflight 请求会被拒绝（影响文件上传等 POST 请求）。WebSocket 升级不受 CORS 限制，但 REST API 会被挡。
>
> 如果客户后续绑定了域名或配置了 HTTPS，需要手动编辑 `biomni.env` 中的 `CORS_ORIGINS` 加入新的 origin（如 `https://your-domain.com`），然后重启 Agent 服务。

### 4.3 Client Frontend（React）

#### 4.3.1 `client.ts` — API baseURL 同源

当前：
```typescript
baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8083',
```

改为：
```typescript
baseURL: import.meta.env.VITE_API_URL || '',
```

空字符串 = 同源。请求路径本身是 `/api/...`，会走 Nginx → Spring Boot。

> 注意：不要用 `window.location.origin`，空字符串更简洁且 axios 默认行为就是同源。

#### 4.3.2 `useWebSocket.ts` — WebSocket 同源推导

当前：
```typescript
const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';
const url = `${wsUrl}/ws/chat/${conversationId}?token=...`;
```

改为：
```typescript
const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const wsUrl = import.meta.env.VITE_WS_URL || `${protocol}//${window.location.host}`;
const url = `${wsUrl}/ws/chat/${conversationId}?token=...`;
```

这样无论 HTTP 还是 HTTPS，WebSocket 地址都自动推导，不需要硬编码。

#### 4.3.3 `agentClient.ts` — Agent API 同源

当前：
```typescript
baseURL: import.meta.env.VITE_AGENT_API_URL || 'http://localhost:8000',
```

改为：
```typescript
baseURL: import.meta.env.VITE_AGENT_API_URL || '',
```

#### 4.3.4 `upload.ts` — 上传路径改为 `/agent-api/`

当前：
```typescript
const response = await agentApiClient.post('/api/upload', formData, ...);
```

改为：
```typescript
const response = await agentApiClient.post('/agent-api/upload', formData, ...);
```

原因：FastAPI 的上传路由前缀是 `/api`，Spring Boot 也用 `/api`。对外通过 Nginx 用 `/agent-api/` 区分，避免冲突。

#### 4.3.5 新增 `.env.production`

```bash
# client/frontend/.env.production
VITE_API_URL=
VITE_WS_URL=
VITE_AGENT_API_URL=
```

留空 = 同源，由 Nginx 代理。只有特殊部署才需要覆盖。

### 4.4 Admin Frontend（Vue）

#### 4.4.1 `.env.production` 统一

```bash
# admin/frontend/.env.production
VITE_PUBLIC_PATH=/admin/
VITE_USE_PROXY=false
VITE_BASE_API=/api
VITE_TITLE=Biomni Admin
VITE_USE_HASH=false
VITE_INFRA_API_URL=
```

`VITE_BASE_API=/api` 确保 axios 请求走相对路径 → Nginx → Spring Boot。

#### 4.4.2 路由 base 支持 `/admin`

`admin/frontend/src/router/index.js` 中 base 改为读取 `VITE_PUBLIC_PATH`：

```javascript
const base = import.meta.env.VITE_PUBLIC_PATH || '/'
history: isHash ? createWebHashHistory(base) : createWebHistory(base),
```

确保 Nginx 为 `/admin/` 配置 `try_files ... /admin/index.html;`。

#### 4.4.3 `infra-client.js` 清理

移除硬编码的 `https://api.e2b.9527.tech`，改为从 `VITE_INFRA_API_URL` 读取。同时清理注释中的 API Key 和 Supabase Token（敏感信息泄露风险）。

---

## 5. 数据库初始化与默认管理员

### 5.1 初始化策略

AMI 内置 `init.sql`（来自仓库），但不在制作 AMI 时执行，而在 first-boot 时执行：

1. 安装并启动 MySQL
2. 生成 `MYSQL_ROOT_PASSWORD`、`BIOMNI_DB_PASSWORD`
3. 配置 root 密码，创建业务用户 `biomni`
4. 执行 `init.sql` 完成建库建表与默认数据
5. 生成随机 `ADMIN_PASSWORD`，用 bcrypt 写回 admin 表
6. 设置 `force_password_change=1`，强制首次登录改密

### 5.2 BCrypt 生成方式

使用 `apache2-utils` 的 `htpasswd`，不依赖 Python bcrypt 库：

```bash
# 安装（AMI 预装）
sudo apt install -y apache2-utils

# 生成 bcrypt hash
ADMIN_BCRYPT="$(htpasswd -bnBC 10 "" "${ADMIN_PASSWORD}" | tr -d ':\n')"

# 写回数据库
mysql -u root -p"${MYSQL_ROOT_PASSWORD}" biomni -e \
  "UPDATE admin SET password='${ADMIN_BCRYPT}', force_password_change=1 WHERE id=1;"
```

### 5.3 SQL 文件处理

将 `init.sql` 直接使用（包含 CREATE TABLE + 默认 INSERT），first-boot 执行后再 UPDATE 密码。不需要拆分为 schema + seed 模板，更简单：

```bash
# 1. 执行原始 init.sql（包含固定 bcrypt hash 的默认管理员）
mysql -u biomni -p"${BIOMNI_DB_PASSWORD}" biomni < /opt/biomni/sql/init.sql

# 2. 用随机密码覆盖默认管理员密码 + 强制改密
ADMIN_BCRYPT="$(htpasswd -bnBC 10 "" "${ADMIN_PASSWORD}" | tr -d ':\n')"
mysql -u biomni -p"${BIOMNI_DB_PASSWORD}" biomni -e \
  "UPDATE admin SET password='${ADMIN_BCRYPT}', force_password_change=1 WHERE id=1;"
```

---

## 6. `first-boot.sh` 完整脚本

```bash
#!/bin/bash
# ============================================================
# Biomni First Boot Initialization Script
# 仅在首次启动时执行，完成密码生成、配置写入、数据库初始化
# ============================================================

set -euo pipefail

LOCK_FILE="/opt/biomni/.initialized"
LOG_FILE="/opt/biomni/logs/first-boot.log"
CONFIG_DIR="/opt/biomni/config"
SQL_DIR="/opt/biomni/sql"
CRED_FILE="/home/ubuntu/biomni-credentials.txt"

# 幂等：已初始化则跳过
if [ -f "$LOCK_FILE" ]; then
    echo "Biomni already initialized. Skipping."
    exit 0
fi

mkdir -p /opt/biomni/logs
exec > >(tee -a "$LOG_FILE") 2>&1
echo "=========================================="
echo "Biomni First Boot — $(date)"
echo "=========================================="

# ------------------------------------------
# 1. 生成随机密码和密钥（hex，无需 URL encode）
# ------------------------------------------
echo "[1/7] Generating secrets..."

BIOMNI_DB_PASSWORD="$(openssl rand -hex 24)"
MYSQL_ROOT_PASSWORD="$(openssl rand -hex 24)"
BIOMNI_JWT_SECRET="$(openssl rand -hex 32)"
BIOMNI_REDIS_PASSWORD="$(openssl rand -hex 24)"
ADMIN_PASSWORD="$(openssl rand -base64 18 | tr -d '=+/')"

# IMDSv2 获取实例信息
TOKEN=$(curl -sf -X PUT "http://169.254.169.254/latest/api/token" \
  -H "X-aws-ec2-metadata-token-ttl-seconds: 300" --connect-timeout 3 || echo "")
if [ -n "$TOKEN" ]; then
    INSTANCE_ID=$(curl -sf -H "X-aws-ec2-metadata-token: $TOKEN" \
      http://169.254.169.254/latest/meta-data/instance-id || echo "unknown")
    PUBLIC_IP=$(curl -sf -H "X-aws-ec2-metadata-token: $TOKEN" \
      http://169.254.169.254/latest/meta-data/public-ipv4 || echo "127.0.0.1")
else
    INSTANCE_ID="unknown"
    PUBLIC_IP="127.0.0.1"
fi

echo "  Instance: $INSTANCE_ID | Public IP: $PUBLIC_IP"

# ------------------------------------------
# 2. 写入 biomni.env（单一配置源）
# ------------------------------------------
echo "[2/7] Writing biomni.env..."

cat > ${CONFIG_DIR}/biomni.env <<EOF
# Generated by first-boot.sh at $(date)
# DO NOT EDIT MANUALLY

# ---- MySQL ----
BIOMNI_DB_HOST=127.0.0.1
BIOMNI_DB_PORT=3306
BIOMNI_DB_NAME=biomni
BIOMNI_DB_USER=biomni
BIOMNI_DB_PASSWORD=${BIOMNI_DB_PASSWORD}
MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}

# ---- JWT (Spring Boot + Agent 共享) ----
BIOMNI_JWT_SECRET=${BIOMNI_JWT_SECRET}

# ---- Redis ----
BIOMNI_REDIS_PASSWORD=${BIOMNI_REDIS_PASSWORD}

# ---- Spring Boot env override (relaxed binding) ----
SPRING_PROFILES_ACTIVE=ami
SERVER_PORT=9999
SPRING_DATASOURCE_MYSQL_JDBC_URL=jdbc:mysql://127.0.0.1:3306/biomni?useUnicode=true&characterEncoding=utf8&useSSL=false&serverTimezone=GMT%2B8
SPRING_DATASOURCE_MYSQL_USERNAME=biomni
SPRING_DATASOURCE_MYSQL_PASSWORD=${BIOMNI_DB_PASSWORD}
SPRING_DATASOURCE_MYSQL_DRIVER_CLASS_NAME=com.mysql.cj.jdbc.Driver
JWT_SECRET=${BIOMNI_JWT_SECRET}
JWT_EXPIRATION=86400000
SPRING_DATA_REDIS_HOST=127.0.0.1
SPRING_DATA_REDIS_PORT=6379
SPRING_DATA_REDIS_PASSWORD=${BIOMNI_REDIS_PASSWORD}

# ---- Agent env ----
JWT_SECRET_KEY=${BIOMNI_JWT_SECRET}
JWT_ALGORITHM=HS512
DATABASE_URL=mysql+pymysql://biomni:${BIOMNI_DB_PASSWORD}@127.0.0.1:3306/biomni
USE_MOCK_AGENT=false
AGENT_DATA_PATH=/opt/biomni/data
AGENT_UPLOAD_DATA_PATH=/opt/biomni/upload
CORS_ORIGINS=["http://127.0.0.1","http://${PUBLIC_IP}"]
SPRING_BOOT_URL=http://127.0.0.1:9999
EOF

chown biomni:biomni ${CONFIG_DIR}/biomni.env
chmod 600 ${CONFIG_DIR}/biomni.env

# ------------------------------------------
# 3. 初始化 MySQL
# ------------------------------------------
echo "[3/7] Configuring MySQL..."

sudo mysql -u root <<EOSQL
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '${MYSQL_ROOT_PASSWORD}';
CREATE DATABASE IF NOT EXISTS biomni CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'biomni'@'localhost' IDENTIFIED WITH mysql_native_password BY '${BIOMNI_DB_PASSWORD}';
GRANT ALL PRIVILEGES ON biomni.* TO 'biomni'@'localhost';
FLUSH PRIVILEGES;
EOSQL

# 执行建表 SQL
mysql -u biomni -p"${BIOMNI_DB_PASSWORD}" biomni < ${SQL_DIR}/init.sql

# 随机化管理员密码 + 强制改密
ADMIN_BCRYPT="$(htpasswd -bnBC 10 "" "${ADMIN_PASSWORD}" | tr -d ':\n')"
mysql -u biomni -p"${BIOMNI_DB_PASSWORD}" biomni -e \
  "UPDATE admin SET password='${ADMIN_BCRYPT}', force_password_change=1 WHERE id=1;"

echo "  MySQL initialized with random admin password."

# ------------------------------------------
# 4. 配置 Redis
# ------------------------------------------
echo "[4/7] Configuring Redis..."

sudo sed -i "s/^# requirepass .*/requirepass ${BIOMNI_REDIS_PASSWORD}/" /etc/redis/redis.conf
sudo sed -i "s/^requirepass .*/requirepass ${BIOMNI_REDIS_PASSWORD}/" /etc/redis/redis.conf
sudo sed -i "s/^bind .*/bind 127.0.0.1/" /etc/redis/redis.conf
sudo systemctl restart redis-server

# ------------------------------------------
# 5. 配置 Nginx
# ------------------------------------------
echo "[5/7] Configuring Nginx..."

sudo ln -sf /etc/nginx/sites-available/biomni /etc/nginx/sites-enabled/biomni
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# ------------------------------------------
# 6. 启动服务
# ------------------------------------------
echo "[6/7] Starting services..."

sudo systemctl enable biomni-admin biomni-agent
sudo systemctl start biomni-admin
sleep 5
sudo systemctl start biomni-agent

# ------------------------------------------
# 7. 输出凭据
# ------------------------------------------
echo "[7/7] Saving credentials..."

cat > ${CRED_FILE} <<EOF
============================================================
  Biomni Installation Credentials
  Generated: $(date)
  Instance:  ${INSTANCE_ID}
============================================================

  Admin Portal:   http://${PUBLIC_IP}/admin/
  Client Portal:  http://${PUBLIC_IP}/

  Admin Username: admin
  Admin Email:    admin@biomni.com
  Admin Password: ${ADMIN_PASSWORD}

  MySQL Root Password:   ${MYSQL_ROOT_PASSWORD}
  MySQL Biomni Password: ${BIOMNI_DB_PASSWORD}
  JWT Secret:            ${BIOMNI_JWT_SECRET}
  Redis Password:        ${BIOMNI_REDIS_PASSWORD}

  IMPORTANT:
    1. 请立即登录管理后台修改默认密码
    2. 在管理后台 > 系统配置 中设置 LLM API Key
    3. 建议绑定 Elastic IP 获得固定访问地址
    4. 建议配置 HTTPS (Let's Encrypt)

============================================================
EOF

chmod 600 ${CRED_FILE}
chown ubuntu:ubuntu ${CRED_FILE}

# 标记已初始化
touch ${LOCK_FILE}

echo ""
echo "=========================================="
echo "  ✅ Biomni initialization completed!"
echo "  📄 Credentials: ${CRED_FILE}"
echo "=========================================="
```

### 6.1 注册为 systemd oneshot

```ini
# /etc/systemd/system/biomni-firstboot.service
[Unit]
Description=Biomni First Boot Initialization
After=network-online.target mysql.service redis-server.service
Wants=network-online.target
ConditionPathExists=!/opt/biomni/.initialized

[Service]
Type=oneshot
ExecStart=/opt/biomni/scripts/first-boot.sh
RemainAfterExit=yes
StandardOutput=journal+console

[Install]
WantedBy=multi-user.target
```

```bash
sudo chmod +x /opt/biomni/scripts/first-boot.sh
sudo systemctl enable biomni-firstboot.service
```


---

## 7. 源码保护

### 7.1 总体原则

AMI 会交付到客户 AWS 账号，客户对 EC2 拥有 root 权限，无法做到绝对不可逆。目标是：**不交付可读源码**，只交付运行所需构建产物，并用编译/混淆提高逆向门槛。

### 7.2 Python Agent — Cython 编译（推荐）

将 `.py` 编译为 C 扩展 `.so` 文件，无法直接阅读源码，反编译难度极高。

```bash
cd agent

# 1. 安装 Cython
pip install cython setuptools

# 2. 创建编译脚本 setup_cython.py
cat > setup_cython.py << 'PYEOF'
from setuptools import setup, find_packages
from Cython.Build import cythonize
import glob

py_files = []
for directory in ['api', 'core', 'services', 'models']:
    py_files.extend(glob.glob(f'{directory}/**/*.py', recursive=True))
py_files.extend(glob.glob('biomni/**/*.py', recursive=True))

# 保留 __init__.py（维持包结构）和 main.py（入口）
py_files = [f for f in py_files if '__init__' not in f and f != 'main.py']

print(f"将编译 {len(py_files)} 个文件:")
for f in py_files:
    print(f"  {f}")

setup(
    ext_modules=cythonize(
        py_files,
        compiler_directives={'language_level': "3"},
        nthreads=4,
    ),
    packages=find_packages(),
)
PYEOF

# 3. 编译（必须在目标平台 Ubuntu 22.04 + Python 3.11 + x86_64 上执行）
python setup_cython.py build_ext --inplace

# 4. 删除 .py 源文件，只保留 .so 和 __init__.py
find biomni api core services models -name "*.py" ! -name "__init__.py" -delete
find . -name "*.c" -delete  # 删除中间 C 文件

# 5. 验证
python -c "from biomni.agent import A1; print('OK')"
```

编译后目录结构示例：
```
agent/
├── main.py                                        # 保留（入口，内容很少）
├── biomni/
│   ├── __init__.py
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── a1.cpython-311-x86_64-linux-gnu.so     # 核心算法，已保护
│   │   └── react.cpython-311-x86_64-linux-gnu.so
│   ├── tool/
│   │   ├── *.so
│   │   ├── schema_db/*.pkl                         # 数据文件保留
│   │   └── tool_description/*.so
│   └── ...
├── api/
│   ├── __init__.py
│   └── *.so
├── core/
│   ├── __init__.py
│   └── *.so
└── services/
    ├── __init__.py
    └── *.so
```

> ⚠️ Cython 编译的 `.so` 依赖特定 Python 版本（如 cpython-311）。AMI 中安装的 Python 版本必须与编译时一致。建议在 EC2 上编译，或用 Docker：
> ```bash
> docker run --rm -v $(pwd):/app -w /app python:3.11 bash -c \
>   "pip install cython && python setup_cython.py build_ext --inplace"
> ```

> ⚠️ **Cython 编译后不要用 `pip install -e .`（editable install）**。editable install 依赖源码目录中的 `.py` 文件，删除后会 import 失败。正确做法是依靠 systemd 的 `WorkingDirectory` 让 Python 在 CWD 找到包，不需要 pip install 包本身。只需 `pip install -r requirements-api.txt` 安装第三方依赖即可。

**落地建议**：Cython 方案需要在目标 OS（Ubuntu 22.04 + Python 3.11 + x86_64）上实际验证编译和运行。biomni 的依赖链较复杂（含 C 扩展、数据文件、动态 import 等），建议：
1. 先在 EC2 Golden Instance 上尝试 Cython 编译 + 运行全流程
2. 如果遇到兼容性问题（如某些模块动态 import 失败、`.pkl` 数据文件路径问题），可回退到 **PyInstaller 方案**

### 7.2.1 备选方案：PyInstaller（保护更强，但体积更大）

如果 Cython 方案在实际验证中遇到问题，PyInstaller 是更稳妥的选择：

```bash
cd agent
pip install pyinstaller

pyinstaller --onedir \
  --hidden-import=biomni \
  --hidden-import=biomni.agent \
  --hidden-import=biomni.tool \
  --hidden-import=biomni.know_how \
  --hidden-import=biomni.model \
  --add-data "biomni/know_how:biomni/know_how" \
  --add-data "biomni/tool/schema_db:biomni/tool/schema_db" \
  --add-data "biomni/tool/protocols:biomni/tool/protocols" \
  --add-data "biomni/tool/tool_description:biomni/tool/tool_description" \
  --name biomni-agent \
  main.py

# 产物在 dist/biomni-agent/ 目录下
```

PyInstaller 优点：完全看不到 Python 源码，不依赖系统 Python 版本。
缺点：产物体积大（200-500MB）、启动稍慢、hidden-import 需要逐个排查。

使用 PyInstaller 时，systemd service 改为：
```ini
ExecStart=/opt/biomni/agent/dist/biomni-agent/biomni-agent
```

> **推荐策略**：先尝试 Cython，验证通过则用 Cython（体积小、启动快）；验证不通过则用 PyInstaller（更稳妥）。两者都配合文件权限加固（7.5 节）。

### 7.3 Spring Boot — ProGuard 混淆（可选）

JAR 本身是编译后的 .class 字节码，但可用 `jd-gui` 反编译。ProGuard 混淆后类名/方法名变为 a/b/c，大幅增加逆向难度。

在 `pom.xml` 中添加 ProGuard 插件：

```xml
<plugin>
    <groupId>com.github.wvengen</groupId>
    <artifactId>proguard-maven-plugin</artifactId>
    <version>2.6.0</version>
    <executions>
        <execution>
            <phase>package</phase>
            <goals><goal>proguard</goal></goals>
        </execution>
    </executions>
    <configuration>
        <obfuscate>true</obfuscate>
        <injar>${project.build.finalName}.jar</injar>
        <outjar>${project.build.finalName}-obf.jar</outjar>
        <options>
            <option>-keep public class com.qusu.mybiomni.MyBiomniApplication { *; }</option>
            <option>-keep @org.springframework.stereotype.* class *</option>
            <option>-keep @org.springframework.web.bind.annotation.RestController class *</option>
            <option>-keepclassmembers class * {
                @org.springframework.beans.factory.annotation.Autowired *;
                @org.springframework.beans.factory.annotation.Value *;
                @org.springframework.web.bind.annotation.* *;
            }</option>
            <option>-keep class com.qusu.mybiomni.model.** { *; }</option>
            <option>-keep class com.qusu.mybiomni.controller.**.* { *; }</option>
            <option>-keepclassmembers class * {
                public ** get*();
                public void set*(***);
            }</option>
        </options>
    </configuration>
</plugin>
```

> ProGuard 与 Spring Boot 兼容性需要仔细调试。初期可以先不混淆，用原始 JAR 上架，后续迭代加入。

### 7.4 前端

前端最终在浏览器侧可见，无法真正隐藏。做到以下即可：
- 只交付 `dist/`，不交付源码
- 生产构建关闭 sourcemap（不生成 `*.map`）
- 开启压缩/混淆（terser），降低可读性

### 7.5 文件权限加固

```bash
# Agent 目录：只有 biomni 用户可读写执行
sudo chown -R biomni:biomni /opt/biomni/agent
sudo chmod -R 750 /opt/biomni/agent
find /opt/biomni/agent -name "*.so" -exec chmod 550 {} \;

# Spring Boot JAR：只有 biomni 用户可读
sudo chown biomni:biomni /opt/biomni/admin-backend/biomni-admin.jar
sudo chmod 500 /opt/biomni/admin-backend/biomni-admin.jar

# 配置文件：只有 biomni 用户可读（包含密码）
sudo chmod 600 /opt/biomni/config/biomni.env

# ubuntu 用户无法读取 agent 目录内容
sudo -u ubuntu ls /opt/biomni/agent/biomni/ 2>&1 | grep -q "Permission denied" && echo "✅ OK"
```


---

## 8. AMI 构建流程（6 阶段）

### Phase A：本地构建发布包

#### A.1 修改前端代码支持同源

按第 4 节修改 `client.ts`、`useWebSocket.ts`、`agentClient.ts`、`upload.ts`、admin `.env.production` 等。

#### A.2 构建前端产物

```bash
# Client Frontend
cd client/frontend
cat > .env.production << 'EOF'
VITE_API_URL=
VITE_WS_URL=
VITE_AGENT_API_URL=
EOF
npm install && npm run build
# 产物：client/frontend/dist/

# Admin Frontend
cd admin/frontend
cat > .env.production << 'EOF'
VITE_PUBLIC_PATH=/admin/
VITE_USE_PROXY=false
VITE_BASE_API=/api
VITE_TITLE=Biomni Admin
VITE_USE_HASH=false
VITE_INFRA_API_URL=
EOF
pnpm install && pnpm run build
# 产物：admin/frontend/dist/
```

#### A.3 构建 Spring Boot JAR

```bash
cd admin/backend
# 确保 pom.xml 已添加 <finalName>biomni-admin</finalName>
mvn clean package -DskipTests
# 产物：target/biomni-admin.jar
```

#### A.4 编译 Python Agent（Cython）

在目标平台（Ubuntu 22.04 + Python 3.11 + x86_64）上执行，见第 7.2 节。

#### A.5 打包发布包

```bash
mkdir -p release/{admin-backend,admin-frontend,client-frontend,agent,sql,scripts,config}

# 复制产物
cp admin/backend/target/biomni-admin.jar release/admin-backend/
cp -r client/frontend/dist/* release/client-frontend/
cp -r admin/frontend/dist/* release/admin-frontend/

# Agent（Cython 编译后）
cp -r agent/ release/agent/
rm -rf release/agent/{__pycache__,.env,logs/,data/,*.c,setup_cython.py,build/,.git}
find release/agent -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
find release/agent -name "*.pyc" -delete

# SQL
cp admin/backend/data/init/mysql/init.sql release/sql/

# 脚本和配置（需要提前准备）
cp scripts/first-boot.sh release/scripts/
cp scripts/health-check.sh release/scripts/
cp scripts/pre-ami-cleanup.sh release/scripts/
cp config/nginx-biomni.conf release/config/

# !! 安全检查
echo "=== 检查残留 .py 文件（除 __init__.py 和 main.py）==="
find release/agent -name "*.py" ! -name "__init__.py" ! -name "main.py"

echo "=== 检查敏感文件 ==="
find release -name "*.pem" -o -name ".git" -o -name "deploy.sh" \
  -o -name ".env" -o -name "docker-compose.yml" -o -name "*.map"
# 输出应为空

tar -czf biomni-release.tar.gz release/
```

### Phase B：EC2 Golden Instance 预装

#### B.1 启动基础 EC2

```bash
aws ec2 run-instances \
  --image-id ami-0c7217cdde317cfec \
  --instance-type t3.xlarge \
  --key-name your-key \
  --security-group-ids sg-xxx \
  --block-device-mappings '[{"DeviceName":"/dev/sda1","Ebs":{"VolumeSize":100,"VolumeType":"gp3"}}]'
```

#### B.2 安装系统依赖

```bash
sudo apt update && sudo apt upgrade -y

# 基础工具
sudo apt install -y curl wget vim htop unzip jq apache2-utils

# MySQL 8.0
sudo apt install -y mysql-server-8.0
sudo systemctl enable mysql

# Redis
sudo apt install -y redis-server
sudo systemctl enable redis-server

# Java 17
sudo apt install -y openjdk-17-jdk-headless

# Python 3.11
sudo apt install -y python3.11 python3.11-venv python3-pip

# Nginx
sudo apt install -y nginx
sudo systemctl enable nginx

# 安全工具
sudo apt install -y fail2ban ufw unattended-upgrades
```

#### B.3 创建用户和目录

```bash
sudo useradd -r -m -d /opt/biomni -s /usr/sbin/nologin biomni
sudo mkdir -p /opt/biomni/{admin-backend,admin-frontend,client-frontend}
sudo mkdir -p /opt/biomni/{agent,config,scripts,sql,logs,data,upload,backups}
sudo chown -R biomni:biomni /opt/biomni
```

#### B.4 上传并部署

```bash
scp biomni-release.tar.gz ubuntu@<EC2_IP>:/tmp/
# 在 EC2 上
cd /tmp && tar -xzf biomni-release.tar.gz
sudo cp -r release/* /opt/biomni/
sudo chown -R biomni:biomni /opt/biomni
```

#### B.5 安装 Agent Python 依赖

```bash
sudo -u biomni python3.11 -m venv /opt/biomni/agent/venv
sudo -u biomni /opt/biomni/agent/venv/bin/pip install --upgrade pip
sudo -u biomni /opt/biomni/agent/venv/bin/pip install -r /opt/biomni/agent/requirements-api.txt
```

> ⚠️ **不要用 `pip install -e .`（editable install）**。Cython 编译后 `.py` 源文件已删除，editable install 依赖源码目录中的 `.py` 文件，会导致 import 失败。正确做法是依靠 systemd 的 `WorkingDirectory=/opt/biomni/agent` 让 Python 自动在当前目录找到包（uvicorn 启动时 CWD 就是 agent 目录），或者用 `pip install .`（非 editable，会把 `.so` 复制到 site-packages）。
>
> 如果选择 `pip install .`（非 editable），需要确保 `pyproject.toml` / `setup.py` 正确声明了包，且 Cython 编译后的 `.so` 文件能被 setuptools 识别。**推荐更简单的方案：不 install，直接靠 WorkingDirectory + PYTHONPATH。**
>
> 在 systemd service 中已经设置了 `WorkingDirectory=/opt/biomni/agent`，uvicorn 启动时会自动将 CWD 加入 `sys.path`，因此 `from biomni.agent import A1` 等 import 可以正常工作。

#### B.6 部署 Systemd 服务

**`/etc/systemd/system/biomni-admin.service`**

```ini
[Unit]
Description=Biomni Admin Backend (Spring Boot)
After=network.target mysql.service redis-server.service
Requires=mysql.service

[Service]
Type=simple
User=biomni
Group=biomni
WorkingDirectory=/opt/biomni/admin-backend
EnvironmentFile=/opt/biomni/config/biomni.env
ExecStart=/usr/bin/java -Xms512m -Xmx1g \
  -jar /opt/biomni/admin-backend/biomni-admin.jar
Restart=always
RestartSec=10
StandardOutput=append:/opt/biomni/logs/admin-backend.log
StandardError=append:/opt/biomni/logs/admin-backend-error.log

[Install]
WantedBy=multi-user.target
```

> 注意：不需要 `--spring.profiles.active=ami` 命令行参数，因为 `biomni.env` 中已有 `SPRING_PROFILES_ACTIVE=ami`，Spring Boot 会自动读取。

**`/etc/systemd/system/biomni-agent.service`**

```ini
[Unit]
Description=Biomni AI Agent (FastAPI)
After=network.target mysql.service redis-server.service
Requires=mysql.service

[Service]
Type=simple
User=biomni
Group=biomni
WorkingDirectory=/opt/biomni/agent
EnvironmentFile=/opt/biomni/config/biomni.env
ExecStart=/opt/biomni/agent/venv/bin/uvicorn api.app:app \
  --host 127.0.0.1 --port 8000 --log-level info
Restart=always
RestartSec=10
Environment="PYTHONUNBUFFERED=1"
StandardOutput=append:/opt/biomni/logs/agent.log
StandardError=append:/opt/biomni/logs/agent-error.log

[Install]
WantedBy=multi-user.target
```

#### B.7 部署 Nginx 配置

```nginx
# /etc/nginx/sites-available/biomni
server {
    listen 80;
    server_name _;
    client_max_body_size 20M;

    # 用户端
    location / {
        root /opt/biomni/client-frontend;
        try_files $uri $uri/ /index.html;
    }

    # 管理后台
    location /admin/ {
        alias /opt/biomni/admin-frontend/;
        try_files $uri $uri/ /admin/index.html;
    }

    # Spring Boot API
    location /api/ {
        proxy_pass http://127.0.0.1:9999/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
    }

    # Agent REST（上传等）
    location /agent-api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 300s;
    }

    # Agent WebSocket
    location /ws/ {
        proxy_pass http://127.0.0.1:8000/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 3600s;
        proxy_send_timeout 3600s;
    }
}
```

```bash
sudo ln -sf /etc/nginx/sites-available/biomni /etc/nginx/sites-enabled/biomni
sudo rm -f /etc/nginx/sites-enabled/default
```

### Phase C：安全加固

```bash
# 防火墙
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

# SSH 加固
sudo sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl restart sshd

# Fail2Ban
sudo systemctl enable fail2ban && sudo systemctl start fail2ban

# 自动安全更新
sudo dpkg-reconfigure -plow unattended-upgrades

# 文件权限（见 7.5 节）
sudo chown -R biomni:biomni /opt/biomni/agent
sudo chmod -R 750 /opt/biomni/agent
sudo chmod 500 /opt/biomni/admin-backend/biomni-admin.jar
```

### Phase D：自测

手动执行 `first-boot.sh`，验证完整流程：

```bash
sudo /opt/biomni/scripts/first-boot.sh
cat ~/biomni-credentials.txt

# 验证
curl -sf http://127.0.0.1:9999/health/alive && echo "✅ Admin Backend OK"
curl -sf http://127.0.0.1:8000/health && echo "✅ Agent OK"
curl -sf http://127.0.0.1/ | head -1 && echo "✅ Client Frontend OK"
curl -sf http://127.0.0.1/admin/ | head -1 && echo "✅ Admin Frontend OK"
```

浏览器验证：登录管理后台、配置 LLM Key、创建对话、WebSocket 收发、上传附件。

### Phase E：制作 AMI 前清理

```bash
#!/bin/bash
# /opt/biomni/scripts/pre-ami-cleanup.sh

set -e
echo "=== Pre-AMI Cleanup ==="

# 停止服务
sudo systemctl stop biomni-admin biomni-agent nginx mysql redis-server

# 删除初始化标记（让新实例重新执行 first-boot）
sudo rm -f /opt/biomni/.initialized

# 删除生成的配置和凭据
sudo rm -f /opt/biomni/config/biomni.env
sudo rm -f /home/ubuntu/biomni-credentials.txt

# 清理 MySQL 数据（first-boot 会重新初始化）
sudo rm -rf /var/lib/mysql/*
sudo mysqld --initialize-insecure --user=mysql

# 清理 Redis 数据
sudo rm -f /var/lib/redis/dump.rdb /var/lib/redis/appendonly.aof

# 清理日志
sudo rm -rf /opt/biomni/logs/*
sudo rm -rf /var/log/*.log
sudo journalctl --vacuum-time=1s

# 清理临时文件
sudo rm -rf /tmp/* /var/tmp/*

# 清理 SSH host keys（新实例自动重新生成）
sudo rm -f /etc/ssh/ssh_host_*

# 清理 bash history
sudo rm -f /root/.bash_history /home/ubuntu/.bash_history
history -c

# 清理 cloud-init
sudo cloud-init clean --logs

echo "=== Cleanup complete. Ready to create AMI. ==="
```

### Phase F：创建 AMI

```bash
# 1. 执行清理
sudo /opt/biomni/scripts/pre-ami-cleanup.sh

# 2. 创建 AMI
aws ec2 create-image \
  --instance-id i-xxxxxxxxxxxxxxxxx \
  --name "Biomni-v1.0.0-$(date +%Y%m%d)" \
  --description "Biomni AI-Powered Biomedical Assistant" \
  --no-reboot

# 3. 等待完成
aws ec2 wait image-available --image-ids ami-xxxxxxxxx

# 4. 共享给 AWS Marketplace 账户
aws ec2 modify-image-attribute \
  --image-id ami-xxxxxxxxx \
  --launch-permission "Add=[{UserId=679593333241}]"
```

---

## 9. 健康检查脚本

**`/opt/biomni/scripts/health-check.sh`**

```bash
#!/bin/bash
# Biomni Health Check Script

echo "╔══════════════════════════════════════╗"
echo "║     Biomni Health Check Report       ║"
echo "╚══════════════════════════════════════╝"
echo ""

PASS=0
FAIL=0

check() {
    local name=$1
    local result=$2
    if [ "$result" = "0" ]; then
        echo "  ✅ $name"
        ((PASS++))
    else
        echo "  ❌ $name"
        ((FAIL++))
    fi
}

echo "── Services ──"
systemctl is-active --quiet mysql;          check "MySQL" $?
systemctl is-active --quiet redis-server;   check "Redis" $?
systemctl is-active --quiet biomni-admin;   check "Admin Backend" $?
systemctl is-active --quiet biomni-agent;   check "Agent" $?
systemctl is-active --quiet nginx;          check "Nginx" $?

echo ""
echo "── Ports ──"
ss -tlnp | grep -q ':3306 ';  check "MySQL (3306)" $?
ss -tlnp | grep -q ':6379 ';  check "Redis (6379)" $?
ss -tlnp | grep -q ':9999 ';  check "Admin Backend (9999)" $?
ss -tlnp | grep -q ':8000 ';  check "Agent (8000)" $?
ss -tlnp | grep -q ':80 ';    check "Nginx (80)" $?

echo ""
echo "── HTTP Endpoints ──"
curl -sf http://127.0.0.1:9999/health/alive > /dev/null 2>&1; check "Admin /health/alive" $?
curl -sf http://127.0.0.1:8000/health > /dev/null 2>&1;       check "Agent /health" $?
curl -sf http://127.0.0.1/ > /dev/null 2>&1;                  check "Client Frontend" $?
curl -sf http://127.0.0.1/admin/ > /dev/null 2>&1;            check "Admin Frontend" $?

echo ""
echo "── Resources ──"
DISK_USAGE=$(df / --output=pcent | tail -1 | tr -d ' %')
MEM_USAGE=$(free | awk '/Mem:/{printf "%.0f", $3/$2*100}')
echo "  Disk: ${DISK_USAGE}% used"
echo "  Memory: ${MEM_USAGE}% used"
[ "$DISK_USAGE" -lt 85 ]; check "Disk < 85%" $?
[ "$MEM_USAGE" -lt 90 ];  check "Memory < 90%" $?

echo ""
echo "══════════════════════════════════════"
echo "  Result: ${PASS} passed, ${FAIL} failed"
echo "══════════════════════════════════════"

exit $FAIL
```

---

## 10. 运维脚本

### 10.1 日志轮转

**`/etc/logrotate.d/biomni`**

```
/opt/biomni/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 biomni biomni
    sharedscripts
    postrotate
        systemctl reload biomni-admin 2>/dev/null || true
        systemctl reload biomni-agent 2>/dev/null || true
    endscript
}
```

### 10.2 数据库备份

**`/opt/biomni/scripts/backup.sh`**

```bash
#!/bin/bash
set -e

BACKUP_DIR="/opt/biomni/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/biomni_${DATE}.sql.gz"

# 从 biomni.env 读取密码
source /opt/biomni/config/biomni.env

mkdir -p ${BACKUP_DIR}

mysqldump -u biomni -p"${BIOMNI_DB_PASSWORD}" biomni | gzip > ${BACKUP_FILE}

# 保留最近 30 天的备份
find ${BACKUP_DIR} -name "*.sql.gz" -mtime +30 -delete

echo "Backup saved: ${BACKUP_FILE} ($(du -h ${BACKUP_FILE} | cut -f1))"
```

建议添加 crontab 每日自动备份：
```bash
echo "0 3 * * * /opt/biomni/scripts/backup.sh >> /opt/biomni/logs/backup.log 2>&1" | sudo crontab -u biomni -
```

### 10.3 升级脚本

**`/opt/biomni/scripts/upgrade.sh`**

```bash
#!/bin/bash
set -e

VERSION=$1
if [ -z "$VERSION" ]; then
    echo "Usage: upgrade.sh <version>"
    echo "Example: upgrade.sh 1.1.0"
    exit 1
fi

S3_BUCKET="biomni-releases"
echo "Upgrading Biomni to v${VERSION}..."

# 1. 备份
/opt/biomni/scripts/backup.sh

# 2. 下载新版本
aws s3 cp s3://${S3_BUCKET}/v${VERSION}/biomni-admin.jar /tmp/
aws s3 cp s3://${S3_BUCKET}/v${VERSION}/admin-frontend.tar.gz /tmp/
aws s3 cp s3://${S3_BUCKET}/v${VERSION}/client-frontend.tar.gz /tmp/

# 3. 停止服务
sudo systemctl stop biomni-admin biomni-agent

# 4. 替换文件
sudo cp /tmp/biomni-admin.jar /opt/biomni/admin-backend/
sudo tar -xzf /tmp/admin-frontend.tar.gz -C /opt/biomni/admin-frontend/ --strip-components=1
sudo tar -xzf /tmp/client-frontend.tar.gz -C /opt/biomni/client-frontend/ --strip-components=1
sudo chown -R biomni:biomni /opt/biomni/{admin-backend,admin-frontend,client-frontend}

# 5. 数据库迁移（如有）
MIGRATION="/tmp/migration-v${VERSION}.sql"
if aws s3 cp s3://${S3_BUCKET}/v${VERSION}/migration.sql ${MIGRATION} 2>/dev/null; then
    source /opt/biomni/config/biomni.env
    mysql -u biomni -p"${BIOMNI_DB_PASSWORD}" biomni < ${MIGRATION}
    echo "Database migration applied."
fi

# 6. 重启服务
sudo systemctl start biomni-admin biomni-agent

echo "✅ Upgrade to v${VERSION} complete!"
```

### 10.4 MOTD（登录欢迎信息）

```bash
sudo tee /etc/motd > /dev/null << 'EOF'

  ╔═══════════════════════════════════════════════════════╗
  ║  🧬 Biomni — AI-Powered Biomedical Assistant         ║
  ╠═══════════════════════════════════════════════════════╣
  ║                                                       ║
  ║  Quick Start:                                         ║
  ║    cat ~/biomni-credentials.txt                       ║
  ║                                                       ║
  ║  Admin Portal:  http://<PUBLIC_IP>/admin/             ║
  ║  Client Portal: http://<PUBLIC_IP>/                   ║
  ║                                                       ║
  ║  Health Check:  /opt/biomni/scripts/health-check.sh   ║
  ║  View Logs:     journalctl -u biomni-admin -f         ║
  ║                 journalctl -u biomni-agent -f         ║
  ║                                                       ║
  ╚═══════════════════════════════════════════════════════╝

EOF
```

---

## 11. AWS Marketplace 上架要点

### 11.1 卖家资质

- 注册 AWS Marketplace 卖家账号
- 完成收款/税务信息配置
- 准备产品描述、截图、支持渠道、使用文档

### 11.2 定价策略

首发建议 **BYOL（Bring Your Own License）或免费**，跑通闭环后再接入付费：
- 免费版：客户自带 LLM API Key，不收取软件费用
- 付费版（后续）：接入 AWS Marketplace Metering/Entitlement API

### 11.3 安全扫描常见卡点

Marketplace 提交 AMI 后会进行自动安全扫描，常见被拒原因：

| 问题 | 解决方案 |
|------|----------|
| 多余端口对外开放 | 仅开放 80/443/22，其余 bind 127.0.0.1 |
| 弱口令/固定默认密码 | first-boot 随机生成，`force_password_change=1` |
| AMI 内残留 credentials | pre-ami-cleanup.sh 清理 |
| 残留 `.env`/日志/私钥 | 同上 |
| 系统软件包漏洞 | `apt upgrade -y` + `unattended-upgrades` |
| SSH 允许密码登录 | `PasswordAuthentication no` |
| SSH 允许 root 登录 | `PermitRootLogin no` |
| 未使用 IMDSv2 | first-boot.sh 中使用 token-based metadata |

### 11.4 提交流程

1. 在 AWS Marketplace Management Portal 创建产品
2. 填写产品信息（名称、描述、分类、截图、支持信息）
3. 提交 AMI ID
4. 等待安全扫描通过（通常 1-3 个工作日）
5. 审核通过后发布

---

## 12. 客户使用流程

客户从 Marketplace 订阅后的完整体验：

1. **启动实例**：从 Marketplace 选择 Biomni AMI，选择机型（推荐 `t3.xlarge` 起步），配置安全组（80/443/22），启动
2. **等待初始化**：1-3 分钟，first-boot 自动完成密码生成、数据库初始化、服务启动
3. **获取凭据**：SSH 登录，执行 `cat ~/biomni-credentials.txt` 获取初始管理员密码
4. **访问管理后台**：浏览器打开 `http://<public-ip>/admin/`，用初始密码登录
5. **首次改密**：系统强制要求修改默认密码（`force_password_change=1`）
6. **配置 LLM**：在管理后台 > 系统配置中选择 LLM Provider 并填入 API Key
7. **开始使用**：访问 `http://<public-ip>/` 进入用户端，开始对话

### 后续建议（写入客户文档）

- 绑定 Elastic IP 获得固定访问地址
- 配置域名 + HTTPS：`sudo apt install certbot python3-certbot-nginx && sudo certbot --nginx -d your-domain.com`
- 定期备份：`/opt/biomni/scripts/backup.sh`
- 健康检查：`/opt/biomni/scripts/health-check.sh`

---

## 13. AMI 文件清单

```
/opt/biomni/
├── admin-backend/
│   └── biomni-admin.jar                    # Spring Boot JAR
├── admin-frontend/                         # Vue dist 静态文件
│   ├── index.html
│   └── assets/...
├── client-frontend/                        # React dist 静态文件
│   ├── index.html
│   └── assets/...
├── agent/                                  # Python Agent（Cython 编译后）
│   ├── main.py                             # 入口（保留）
│   ├── biomni/                             # 核心包（.so 文件）
│   ├── api/                                # API 层（.so 文件）
│   ├── core/                               # 配置层（.so 文件）
│   ├── services/                           # 服务层（.so 文件）
│   ├── models/                             # 模型层（.so 文件）
│   ├── requirements-api.txt
│   ├── pyproject.toml
│   └── venv/                               # Python 虚拟环境
├── config/
│   └── biomni.env                          # ← first-boot 生成（AMI 中不存在）
├── scripts/
│   ├── first-boot.sh                       # 首次启动初始化
│   ├── health-check.sh                     # 健康检查
│   ├── backup.sh                           # 数据库备份
│   ├── upgrade.sh                          # 版本升级
│   └── pre-ami-cleanup.sh                  # AMI 制作前清理
├── sql/
│   └── init.sql                            # 建表 + 默认数据
├── data/                                   # Agent 运行数据
├── upload/                                 # 用户上传文件
├── logs/                                   # 统一日志目录
└── backups/                                # 数据库备份

/etc/systemd/system/
├── biomni-firstboot.service                # 首次启动 oneshot
├── biomni-admin.service                    # Spring Boot 服务
└── biomni-agent.service                    # Agent 服务

/etc/nginx/sites-available/
└── biomni                                  # Nginx 配置（固定文件）

/etc/logrotate.d/
└── biomni                                  # 日志轮转配置
```

---

## 14. 操作 Checklist

### 开发机

- [ ] 修改 `client/frontend/src/api/client.ts` — baseURL 改为空字符串
- [ ] 修改 `client/frontend/src/hooks/useWebSocket.ts` — WS 地址同源推导
- [ ] 修改 `client/frontend/src/api/agentClient.ts` — baseURL 改为空字符串
- [ ] 修改 `client/frontend/src/api/upload.ts` — 上传路径改为 `/agent-api/upload`
- [ ] 新增 `client/frontend/.env.production` — 三个 VITE 变量留空
- [ ] 修改 `admin/frontend/.env.production` — `VITE_BASE_API=/api`
- [ ] 修改 `admin/frontend/src/router/index.js` — base 读取 `VITE_PUBLIC_PATH`
- [ ] 清理 `admin/frontend/src/utils/http/infra-client.js` — 移除硬编码 URL 和注释中的 Token
- [ ] 清理 `application-local.properties` / `application-prod.properties` — 敏感值改为 env 占位
- [ ] 新增 `application-ami.properties` — 非敏感默认值
- [ ] 修改 `pom.xml` — 添加 `<finalName>biomni-admin</finalName>`
- [ ] 修改 `agent/main.py` — `reload=False`（或 systemd 直接用 uvicorn 命令）
- [ ] 修改 `agent/core/config.py` — CORS 默认值改为 `["http://127.0.0.1"]`
- [ ] 编写 `first-boot.sh`（IMDSv2 + hex 密码 + htpasswd bcrypt + force_password_change）
- [ ] 编写 `health-check.sh`（Admin 端点 `/health/alive`，Agent 端点 `/health`）
- [ ] 编写 `pre-ami-cleanup.sh`
- [ ] 编写 `backup.sh`、`upgrade.sh`
- [ ] 编写 Nginx 配置文件
- [ ] 编写 systemd service 文件（biomni-admin、biomni-agent、biomni-firstboot）
- [ ] 构建 Client Frontend dist（确认无 sourcemap）
- [ ] 构建 Admin Frontend dist（确认无 sourcemap）
- [ ] 构建 Spring Boot JAR（可选 ProGuard 混淆）
- [ ] Cython 编译 Agent（在目标平台执行）
- [ ] 打包发布包，确认不包含 `.pem`、`.git`、`.env`、`deploy.sh`、`logs/`、`node_modules/`、`*.map`

### EC2 Golden Instance

- [ ] 启动 Ubuntu 22.04 t3.xlarge（100GB gp3）
- [ ] 安装依赖：MySQL 8.0、Redis、Java 17、Python 3.11、Nginx、apache2-utils
- [ ] 创建 biomni 用户和目录结构
- [ ] 上传并解压发布包
- [ ] 安装 Agent Python 依赖（venv + pip）
- [ ] 部署 systemd service 文件
- [ ] 部署 Nginx 配置
- [ ] 配置防火墙（ufw：80/443/22）
- [ ] SSH 加固（禁密码登录、禁 root 登录）
- [ ] 启用 fail2ban
- [ ] 启用自动安全更新
- [ ] 配置日志轮转
- [ ] 设置文件权限（agent 750、JAR 500、config 600）
- [ ] 设置 MOTD
- [ ] 手动执行 first-boot.sh 验证完整流程
- [ ] 浏览器验证：管理后台登录、LLM 配置、用户端对话、WebSocket、文件上传
- [ ] 执行 pre-ami-cleanup.sh
- [ ] 创建 AMI 快照

### 回归验证（用新 AMI 启动干净实例）

- [ ] first-boot 自动执行成功
- [ ] `~/biomni-credentials.txt` 存在且包含随机密码
- [ ] 多次启动验证密码随机性
- [ ] `http://<IP>/admin/` 可访问，默认密码可登录
- [ ] 首次登录强制改密
- [ ] `http://<IP>/` 可访问用户端
- [ ] 配置 LLM Key 后可正常对话（WebSocket 正常）
- [ ] 文件上传功能正常（通过 `/agent-api/` 路由）
- [ ] 外部扫描 9999/8000/3306/6379 端口不可达
- [ ] `health-check.sh` 全部通过
- [ ] 服务被 kill 后 systemd 自动拉起
- [ ] 实例 reboot 后所有服务自动恢复
- [ ] AMI 中无 `.pem`、`.git`、明文密码等敏感文件
- [ ] `/health/alive`（Admin）和 `/health`（Agent）端点正常

---

**文档版本**: 3.0（Plan 1 + Plan 2 合并最终版）
**最后更新**: 2026-02-08
**作者**: Biomni Team
