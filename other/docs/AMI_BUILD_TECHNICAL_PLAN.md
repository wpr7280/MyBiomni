# Biomni AMI 构建技术方案 — AWS Marketplace 上架

## 1. 项目现状分析

### 1.1 组件清单

| 组件 | 技术栈 | 端口 | 说明 |
|------|--------|------|------|
| Admin Backend | Spring Boot 3.4.5 + Java 17 | 9999(local) / 19999(prod) | 管理后台 API |
| Admin Frontend | Vue 3 + Naive UI + Vite 4 | 3100 (PM2 serve) | 管理后台前端 |
| Agent | Python 3.11 + FastAPI + Biomni A1 | 8000 | WebSocket 问答 + 文件上传 |
| Client Frontend | React 18 + Ant Design + Vite 5 | 3001 (dev) / 静态部署 | 用户端 |
| MySQL | 5.7 (docker-compose) / 8.0 (目标) | 3306 | 数据库 |
| Redis | 7.2-alpine | 6379 | 缓存 + Session |
| Nginx | — | 80/443 | 反向代理 |

### 1.2 当前硬编码 / 敏感信息清单

以下是散落在各配置文件中需要在 AMI 构建时统一处理的变量：

#### ① admin/backend — Spring Boot 配置

**文件: `application-local.properties` / `application-prod.properties`**

| 配置项 | 当前值 | 问题 |
|--------|--------|------|
| `spring.datasource.mysql.password` | `qusuyinqing@xjtu28` | 硬编码明文密码 |
| `spring.datasource.mysql.username` | `root` | 应使用专用用户 |
| `spring.datasource.mysql.jdbc-url` | `127.0.0.1:3306` | OK (本地) |
| `jwt.secret` | `mySecretKeyForJWT...` | 硬编码，所有实例共享同一密钥 |
| `spring.data.redis.host` | `127.0.0.1` / `redis.service.consul` | prod 用了 Consul，AMI 需改为 localhost |
| `spring.mail.*` | 飞书 SMTP 凭证 | 硬编码邮箱密码 |
| `server.port` | `9999` / `19999` | AMI 统一为一个端口 |

#### ② agent — Python 配置

**文件: `.env`**

| 配置项 | 当前值 | 问题 |
|--------|--------|------|
| `JWT_SECRET_KEY` | 与 Spring Boot 相同 | 需动态生成，两端同步 |
| `DATABASE_URL` | `root:qusuyinqing%40xjtu28@localhost:3306/biomni` | 硬编码密码 |
| `USE_MOCK_AGENT` | `true` | AMI 应为 `false` |
| `CORS_ORIGINS` | `localhost:3001,3000` | AMI 需动态设置为实例 IP |

**文件: `core/config.py` (Settings)**

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `SPRING_BOOT_URL` | `http://localhost:8083` | 端口需与 AMI 统一 |
| `CORS_ORIGINS` | `localhost` | 需动态替换 |

#### ③ 前端环境变量

**Admin Frontend (`admin/frontend/.env.production`)**

| 配置项 | 当前值 | 问题 |
|--------|--------|------|
| `VITE_BASE_URL` | `/admin` | OK |
| `VITE_API_BASE_URL` | `http://your-domain.com:8080/api` | 占位符，需构建时替换 |

**Client Frontend (`client/frontend/.env.production`)**

| 配置项 | 当前值 | 问题 |
|--------|--------|------|
| `VITE_API_URL` | `https://api.biomni.com` | 硬编码域名 |
| `VITE_WS_URL` | `wss://api.biomni.com` | 硬编码域名 |

#### ④ 数据库初始化

**文件: `init.sql`**

| 内容 | 问题 |
|------|------|
| 默认管理员密码 | BCrypt hash 硬编码，所有实例相同 |
| 默认配额 | OK |

#### ⑤ docker-compose.yml

| 配置项 | 当前值 | 问题 |
|--------|--------|------|
| `MYSQL_ROOT_PASSWORD` | `qusuyinqing@xjtu28` | 硬编码 |
| MySQL 版本 | 5.7 | AMI 建议升级到 8.0 |

#### ⑥ Admin Frontend — Infra API 硬编码

**文件: `admin/frontend/src/utils/http/infra-client.js`**

| 配置项 | 当前值 | 问题 |
|--------|--------|------|
| `baseURL` | `https://api.e2b.9527.tech` | 硬编码第三方 API 地址，AMI 中需通过 `VITE_INFRA_API_URL` 环境变量配置或移除 |

> 注意：infra-client.js 中还有注释掉的 API Key 和 Supabase Token，虽然已注释但仍属于敏感信息泄露风险，AMI 构建前应清理。

#### ⑦ 其他敏感文件

| 文件 | 问题 |
|------|------|
| `biomni.pem` (项目根目录) | SSH 私钥，绝对不能打包进 AMI |
| `admin/frontend/src/biomni.pem` | 同上，前端目录中也有一份 |
| `README.md` | 包含服务器 IP `44.222.116.143` 和 rsync 部署命令 |
| `admin/backend/deploy.sh` | 包含服务器 IP `39.103.178.214` |
| `admin/backend/logs/` | 开发日志，不应打包 |

---

## 2. AMI 架构设计

### 2.1 目标架构 (All-in-One 单实例)

```
EC2 Instance (推荐 t3.xlarge / m5.xlarge)
│
├── Nginx (80/443)
│   ├── /           → /opt/biomni/client-frontend/   (React 静态文件)
│   ├── /admin      → /opt/biomni/admin-frontend/    (Vue 静态文件)
│   ├── /api/       → proxy http://127.0.0.1:9999    (Spring Boot)
│   ├── /ws/        → proxy http://127.0.0.1:8000    (Agent WebSocket)
│   └── /agent-api/ → proxy http://127.0.0.1:8000    (Agent REST)
│
├── MySQL 8.0 (systemd, 127.0.0.1:3306)
├── Redis 7.x (systemd, 127.0.0.1:6379)
├── Spring Boot JAR (systemd, 127.0.0.1:9999)
├── Python Agent (systemd, 127.0.0.1:8000)
│
└── /opt/biomni/
    ├── admin-backend/    biomni-admin.jar
    ├── admin-frontend/   dist 静态文件
    ├── client-frontend/  dist 静态文件
    ├── agent/            编译后的 Agent
    ├── config/           统一配置目录
    ├── scripts/          运维脚本
    ├── sql/              数据库初始化
    ├── logs/             日志目录
    └── data/             Agent 数据目录
```

### 2.2 端口规划 (AMI 内部)

| 服务 | 端口 | 对外暴露 |
|------|------|----------|
| Nginx | 80 / 443 | ✅ 唯一对外端口 |
| Spring Boot | 9999 | ❌ 仅 localhost |
| Agent (FastAPI) | 8000 | ❌ 仅 localhost |
| MySQL | 3306 | ❌ 仅 localhost |
| Redis | 6379 | ❌ 仅 localhost |

---

## 3. 变量生成与统一替换方案

### 3.1 需要动态生成的变量

AMI 首次启动时，由 `first-boot.sh` 脚本自动生成以下变量：

```bash
# ========== 自动生成的变量 ==========

# MySQL
MYSQL_ROOT_PASSWORD=$(openssl rand -base64 32 | tr -d '=/+' | head -c 32)
MYSQL_BIOMNI_PASSWORD=$(openssl rand -base64 32 | tr -d '=/+' | head -c 32)
MYSQL_BIOMNI_USER="biomni"
MYSQL_BIOMNI_DB="biomni"

# JWT (Spring Boot 和 Agent 共享)
JWT_SECRET=$(openssl rand -base64 64 | tr -d '=/+' | head -c 64)

# 默认管理员
ADMIN_DEFAULT_PASSWORD=$(openssl rand -base64 16 | tr -d '=/+' | head -c 16)

# Redis
REDIS_PASSWORD=$(openssl rand -base64 32 | tr -d '=/+' | head -c 32)

# 实例信息 (使用 IMDSv2，AWS Marketplace 要求)
TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 300")
INSTANCE_ID=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/instance-id)
PUBLIC_IP=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/public-ipv4 || echo "127.0.0.1")
PRIVATE_IP=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/local-ipv4)
```

### 3.2 配置文件模板化

将所有配置文件改为模板，使用占位符 `__VARIABLE_NAME__`，首次启动时用 `sed` 替换。

#### 模板文件清单

**① `/opt/biomni/config/application-ami.properties.tpl`**

```properties
server.port=9999

# MySQL
spring.datasource.mysql.jdbc-url=jdbc:mysql://127.0.0.1:3306/__MYSQL_DB__?useUnicode=true&characterEncoding=utf8&useSSL=false&serverTimezone=GMT%2B8
spring.datasource.mysql.username=__MYSQL_USER__
spring.datasource.mysql.password=__MYSQL_PASSWORD__
spring.datasource.mysql.driver-class-name=com.mysql.cj.jdbc.Driver
spring.datasource.mysql.hikari.minimum-idle=5
spring.datasource.mysql.hikari.maximum-pool-size=20

# MyBatis
mybatis.mapper-locations=classpath:mapper/*.xml
mybatis.configuration.map-underscore-to-camel-case=true
server.servlet.session.timeout=120m
spring.jackson.serialization.write-dates-as-timestamps=true

# Logging
logging.level.com.qusu.mybiomni=info

# Upload
spring.servlet.multipart.max-file-size=20MB
spring.servlet.multipart.max-request-size=20MB

# JPA
spring.jpa.hibernate.ddl-auto=validate
spring.jpa.show-sql=false

# JWT
jwt.secret=__JWT_SECRET__
jwt.expiration=86400000

# Redis
spring.data.redis.host=127.0.0.1
spring.data.redis.port=6379
spring.data.redis.password=__REDIS_PASSWORD__
spring.data.redis.database=1
spring.data.redis.timeout=5000ms
spring.data.redis.lettuce.pool.max-active=20
spring.data.redis.lettuce.pool.max-idle=10
spring.data.redis.lettuce.pool.min-idle=5

# Spring Cache
spring.cache.type=redis
spring.cache.redis.time-to-live=3600000
spring.cache.redis.cache-null-values=false
spring.cache.redis.use-key-prefix=true

# Mail (用户可在管理后台配置，此处留空)
# spring.mail.host=
# spring.mail.port=
# spring.mail.username=
# spring.mail.password=
```

**② `/opt/biomni/config/agent.env.tpl`**

```bash
# JWT 配置（与 Spring Boot 共享）
JWT_SECRET_KEY=__JWT_SECRET__
JWT_ALGORITHM=HS512

# Spring Boot API
SPRING_BOOT_URL=http://127.0.0.1:9999
INTERNAL_SECRET=__INTERNAL_SECRET__

# 数据库
DATABASE_URL=mysql+pymysql://__MYSQL_USER__:__MYSQL_PASSWORD_URLENCODED__@127.0.0.1:3306/__MYSQL_DB__

# Agent 配置
AGENT_DATA_PATH=/opt/biomni/data
AGENT_UPLOAD_DATA_PATH=/opt/biomni/upload
DEFAULT_LLM=claude-sonnet-4-5
DEFAULT_TEMPERATURE=0.7

# 生产模式
USE_MOCK_AGENT=false

# CORS (Nginx 代理后，Agent 只接受本地请求)
CORS_ORIGINS=["http://127.0.0.1","http://__PUBLIC_IP__"]
```

**③ `/opt/biomni/config/nginx-biomni.conf.tpl`**

```nginx
server {
    listen 80;
    server_name _;

    client_max_body_size 20M;

    # Client Frontend (用户端)
    location / {
        root /opt/biomni/client-frontend;
        try_files $uri $uri/ /index.html;
    }

    # Admin Frontend (管理后台)
    location /admin {
        alias /opt/biomni/admin-frontend;
        try_files $uri $uri/ /admin/index.html;
    }

    # Admin Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:9999/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
    }

    # Agent REST API (文件上传等)
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

### 3.3 前端构建时变量注入

前端是静态文件，API 地址需要在构建时确定。AMI 中有两种策略：

#### 策略 A: 使用相对路径 (推荐)

修改前端代码，让 API 请求使用相对路径，由 Nginx 统一代理：

**Client Frontend `.env.production` 改为：**
```bash
VITE_API_URL=
VITE_WS_URL=
VITE_AGENT_API_URL=
```

**对应前端代码修改 — `client/frontend/src/api/client.ts`：**
```typescript
// 如果 VITE_API_URL 为空，使用当前域名 + /api
const API_URL = import.meta.env.VITE_API_URL || `${window.location.origin}/api`;
```

**对应前端代码修改 — `client/frontend/src/hooks/useWebSocket.ts`：**
```typescript
// WebSocket 地址自动推导
const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const WS_URL = import.meta.env.VITE_WS_URL || `${protocol}//${window.location.host}/ws`;
```

**Admin Frontend `.env.production` 改为：**
```bash
VITE_BASE_URL=/admin
VITE_API_BASE_URL=/api
VITE_APP_TITLE=Biomni Admin
```

这样前端构建一次即可，不需要根据实例 IP 重新构建。

#### 策略 B: 首次启动时重新构建 (备选)

如果无法修改前端代码使用相对路径，则在 first-boot 时：
```bash
# 替换前端环境变量并重新构建
cd /opt/biomni/src/client-frontend
sed -i "s|VITE_API_URL=.*|VITE_API_URL=http://${PUBLIC_IP}|" .env.production
sed -i "s|VITE_WS_URL=.*|VITE_WS_URL=ws://${PUBLIC_IP}/ws|" .env.production
npm run build
cp -r dist/* /opt/biomni/client-frontend/
```

> ⚠️ 策略 B 需要在 AMI 中保留 node_modules 和源码，增加镜像体积且暴露源码，不推荐。

---

## 4. 代码修改清单

### 4.1 必须修改的文件

#### ① 新增 `application-ami.properties`

```
admin/backend/src/main/resources/application-ami.properties
```

内容见 3.2 节模板。AMI 中 Spring Boot 启动参数改为 `--spring.profiles.active=ami`。

#### ② 修改 Client Frontend API 地址逻辑

**文件: `client/frontend/src/api/client.ts`**
- 改为支持空 `VITE_API_URL` 时使用 `window.location.origin`

**文件: `client/frontend/src/hooks/useWebSocket.ts`**
- 改为支持空 `VITE_WS_URL` 时自动推导 WebSocket 地址

**文件: `client/frontend/src/api/agentClient.ts`**
- 同理，Agent API 地址改为相对路径

#### ③ 修改 Admin Frontend API 地址逻辑

**文件: `admin/frontend/src/api/index.js`**
- 确保 production 模式下使用相对路径 `/api`

#### ④ 修改 Agent CORS 配置

**文件: `agent/core/config.py`**
```python
# CORS — 支持从环境变量读取，默认允许本地
CORS_ORIGINS: list = ["http://127.0.0.1"]
```

#### ⑤ 修改 Admin Frontend Infra Client

**文件: `admin/frontend/src/utils/http/infra-client.js`**
- 移除硬编码的 `https://api.e2b.9527.tech`
- 改为从 `VITE_INFRA_API_URL` 环境变量读取，或在 AMI 中不使用此功能时移除
- 清理注释中的 API Key 和 Token

#### ⑥ 修改 Client Frontend upload.ts

**文件: `client/frontend/src/api/upload.ts`**
- 当前使用 `agentApiClient`（baseURL 为 `VITE_AGENT_API_URL`）
- 确保 `agentClient.ts` 的 fallback 改为 `window.location.origin + '/agent-api'`（对应 Nginx 的 `/agent-api/` 路由）

#### ⑦ Spring Boot pom.xml 添加 finalName

**文件: `admin/backend/pom.xml`**
- 在 `<build>` 中添加 `<finalName>biomni-admin</finalName>`
- 当前 artifactId 是 `my-biomni`，默认产物名 `my-biomni-0.0.1-SNAPSHOT.jar`
- 统一为 `biomni-admin.jar` 方便 systemd 和脚本引用

#### ⑧ 新增 `.env.production` for Client Frontend

```bash
# client/frontend/.env.production
VITE_API_URL=
VITE_WS_URL=
VITE_AGENT_API_URL=
```

空值 = 使用相对路径，由 Nginx 代理。

### 4.2 新增文件清单

| 文件 | 位置 (AMI 内) | 说明 |
|------|---------------|------|
| `first-boot.sh` | `/opt/biomni/scripts/first-boot.sh` | 首次启动初始化 |
| `health-check.sh` | `/opt/biomni/scripts/health-check.sh` | 健康检查 |
| `biomni-admin.service` | `/etc/systemd/system/` | Spring Boot 服务 |
| `biomni-agent.service` | `/etc/systemd/system/` | Agent 服务 |
| `application-ami.properties.tpl` | `/opt/biomni/config/` | Spring Boot 配置模板 |
| `agent.env.tpl` | `/opt/biomni/config/` | Agent 配置模板 |
| `nginx-biomni.conf.tpl` | `/opt/biomni/config/` | Nginx 配置模板 |
| `schema.sql` | `/opt/biomni/sql/` | 纯建表 SQL (不含 INSERT) |
| `seed.sql.tpl` | `/opt/biomni/sql/` | 初始数据模板 (含密码占位符) |

---

## 5. AMI 构建操作流程

### Phase 1: 本地准备 (开发机)

#### Step 1.1: 修改前端代码支持相对路径

```bash
# === Client Frontend ===
# 修改 client/frontend/src/api/client.ts
# 将 baseURL 改为动态推导：
#   const baseURL = import.meta.env.VITE_API_URL || window.location.origin;

# 修改 client/frontend/src/hooks/useWebSocket.ts
# 将 WS 地址改为动态推导：
#   const proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
#   const wsUrl = import.meta.env.VITE_WS_URL || `${proto}//${location.host}/ws`;

# 修改 client/frontend/src/api/agentClient.ts
# Agent API 同理改为相对路径

# === Admin Frontend ===
# 确认 admin/frontend/src/api/index.js 在 production 下使用 /api
```

#### Step 1.2: 构建前端产物

```bash
# Client Frontend
cd client/frontend
cat > .env.production << 'EOF'
VITE_API_URL=
VITE_WS_URL=
VITE_AGENT_API_URL=
EOF
npm install
npm run build
# 产物在 client/frontend/dist/

# Admin Frontend
cd admin/frontend
cat > .env.production << 'EOF'
VITE_BASE_URL=/admin
VITE_API_BASE_URL=/api
VITE_APP_TITLE=Biomni Admin
VITE_PUBLIC_PATH=/admin/
EOF
pnpm install
pnpm run build
# 产物在 admin/frontend/dist/
```

#### Step 1.3: 构建 Spring Boot JAR (含混淆)

```bash
cd admin/backend

# 注意: pom.xml 中 artifactId 是 my-biomni，版本 0.0.1-SNAPSHOT
# 默认产物名为 my-biomni-0.0.1-SNAPSHOT.jar
# 建议在 pom.xml 的 <build> 中添加 <finalName>biomni-admin</finalName> 统一命名
mvn clean package -DskipTests

# 产物: target/biomni-admin.jar (如果配置了 finalName)
# 或者: target/my-biomni-0.0.1-SNAPSHOT.jar (默认)
```

> ⚠️ 当前 `deploy.sh` 中引用的 JAR 名是 `biomni-backend-0.0.1-SNAPSHOT.jar`，
> 而 pom.xml 的 artifactId 是 `my-biomni`，实际产物名为 `my-biomni-0.0.1-SNAPSHOT.jar`。
> 需要统一，建议在 pom.xml 中添加 `<finalName>biomni-admin</finalName>`。

**Spring Boot JAR 混淆 (ProGuard)**

Spring Boot 的 JAR 本身已经是编译后的 .class 字节码，但可以用 `jd-gui` 等工具反编译。
加 ProGuard 混淆后，类名、方法名、字段名全部变成 a/b/c，大幅增加逆向难度。

在 `pom.xml` 中添加 ProGuard 插件：

```xml
<build>
    <finalName>biomni-admin</finalName>
    <plugins>
        <!-- ProGuard 混淆 -->
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
                    <!-- 保留 Spring Boot 入口 -->
                    <option>-keep public class com.qusu.mybiomni.MyBiomniApplication { *; }</option>
                    <!-- 保留 Spring 注解相关 -->
                    <option>-keepclassmembers class * {
                        @org.springframework.beans.factory.annotation.Autowired *;
                        @org.springframework.beans.factory.annotation.Value *;
                        @org.springframework.web.bind.annotation.* *;
                    }</option>
                    <!-- 保留 Controller/Service/Repository -->
                    <option>-keep @org.springframework.stereotype.Controller class *</option>
                    <option>-keep @org.springframework.stereotype.Service class *</option>
                    <option>-keep @org.springframework.stereotype.Repository class *</option>
                    <option>-keep @org.springframework.web.bind.annotation.RestController class *</option>
                    <!-- 保留实体类 (MyBatis/JPA 需要) -->
                    <option>-keep class com.qusu.mybiomni.model.** { *; }</option>
                    <option>-keep class com.qusu.mybiomni.controller.**.* { *; }</option>
                    <!-- 保留 Lombok 生成的方法 -->
                    <option>-keepclassmembers class * {
                        public ** get*();
                        public void set*(***);
                    }</option>
                </options>
            </configuration>
        </plugin>
    </plugins>
</build>
```

> 注意：ProGuard 与 Spring Boot 的兼容性需要仔细调试。如果混淆后启动报错，
> 逐步添加 `-keep` 规则。初期可以先不混淆，用原始 JAR 上架，后续迭代加入。

#### Step 1.4: 打包 Python Agent (源码保护)

Python Agent 是核心知识产权，必须保护。推荐 Cython 编译方案：

**方案 A: Cython 编译为 .so (推荐，平衡保护与兼容性)**

将 `.py` 编译为 C 扩展 `.so` 文件，无法直接阅读源码，反编译难度极高。

```bash
cd agent

# 1. 安装 Cython
pip install cython setuptools

# 2. 创建编译脚本 setup_cython.py
cat > setup_cython.py << 'PYEOF'
from setuptools import setup, find_packages
from Cython.Build import cythonize
import os
import glob

# 收集所有需要编译的 .py 文件
py_files = []
# 编译 api/, core/, services/, models/ 目录 (你的业务代码)
for directory in ['api', 'core', 'services', 'models']:
    py_files.extend(glob.glob(f'{directory}/**/*.py', recursive=True))

# 编译 biomni/ 核心包 (最重要的保护对象)
py_files.extend(glob.glob('biomni/**/*.py', recursive=True))

# 排除 __init__.py (保留以维持包结构)
py_files = [f for f in py_files if '__init__' not in f]
# 排除 main.py (入口文件保留)
py_files = [f for f in py_files if f != 'main.py']

print(f"将编译 {len(py_files)} 个文件:")
for f in py_files:
    print(f"  {f}")

setup(
    ext_modules=cythonize(
        py_files,
        compiler_directives={
            'language_level': "3",
            'boundscheck': False,
            'wraparound': False,
        },
        nthreads=4,
    ),
    packages=find_packages(),
)
PYEOF

# 3. 编译 (需要在目标平台 Linux x86_64 上执行，或交叉编译)
python setup_cython.py build_ext --inplace

# 4. 删除 .py 源文件，只保留 .so 和 __init__.py
find biomni api core services models -name "*.py" ! -name "__init__.py" -delete
find . -name "*.c" -delete  # 删除 Cython 生成的中间 C 文件

# 5. 验证
python -c "from biomni.agent import A1; print('OK')"
```

编译后的目录结构：
```
agent/
├── main.py                          # 保留 (入口，内容很少)
├── api/
│   ├── __init__.py                  # 保留
│   ├── app.cpython-311-x86_64-linux-gnu.so    # 编译后
│   ├── websocket.cpython-311-x86_64-linux-gnu.so
│   └── upload.cpython-311-x86_64-linux-gnu.so
├── biomni/
│   ├── __init__.py
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── a1.cpython-311-x86_64-linux-gnu.so  # 核心算法，已保护
│   │   ├── react.cpython-311-x86_64-linux-gnu.so
│   │   └── ...
│   ├── tool/
│   │   ├── *.so                     # 所有工具编译后
│   │   ├── schema_db/*.pkl          # 数据文件保留
│   │   └── tool_description/*.so
│   └── ...
├── core/
│   ├── __init__.py
│   └── *.so
├── services/
│   ├── __init__.py
│   └── *.so
└── models/
    ├── __init__.py
    └── *.so
```

> ⚠️ Cython 编译必须在与 AMI 相同的平台上执行 (Ubuntu 22.04 + Python 3.11 + x86_64)。
> 建议在 EC2 上编译，或使用 Docker: `docker run --rm -v $(pwd):/app -w /app python:3.11 bash -c "pip install cython && python setup_cython.py build_ext --inplace"`

**方案 B: PyInstaller 打包为单个二进制 (最强保护，但调试困难)**

```bash
cd agent
pip install pyinstaller

pyinstaller --onefile \
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
# 产物: dist/biomni-agent (单个二进制，约 200-500MB)
```

PyInstaller 产物是一个自解压二进制，运行时解压到临时目录。
优点是完全看不到 Python 源码；缺点是文件大、启动慢、依赖问题多（biomni 的依赖链很复杂）。

**方案 C: 源码部署 (开发阶段，不推荐上架)**

```bash
# 直接将 agent/ 目录复制到 AMI，创建 venv
# 用户 SSH 进去就能看到所有 .py 文件
# 仅适合内部测试，不适合 Marketplace
```

**推荐策略：Cython (方案 A) + 文件权限加固**

即使用了 Cython，也要配合文件权限：
```bash
# AMI 中设置 agent 目录权限
sudo chown -R biomni:biomni /opt/biomni/agent
sudo chmod -R 750 /opt/biomni/agent
# ubuntu 用户无法读取 agent 目录内容
# 只有 biomni 服务用户可以执行
```

#### Step 1.5: 准备 SQL 文件

将 `init.sql` 拆分为两个文件：

**`schema.sql`** — 纯建表，不含任何 INSERT：
```sql
-- 从 init.sql 中提取所有 CREATE TABLE 语句
-- 移除 INSERT INTO admin ... 和 INSERT INTO user_quotas ...
```

**`seed.sql.tpl`** — 初始数据模板：
```sql
-- 插入默认管理员 (密码由 first-boot.sh 生成 BCrypt hash 后替换)
INSERT INTO `admin` (`username`, `password`, `email`, `real_name`, `role`, `status`)
VALUES ('admin', '__ADMIN_PASSWORD_HASH__', 'admin@biomni.com', '系统管理员', 'admin', 1);

-- 插入默认配额
INSERT INTO `user_quotas` (`user_id`, `total_token_limit`, `total_token_used`)
VALUES (1, 1000000, 0);
```

#### Step 1.6: 准备部署包

```bash
# 创建部署包目录
mkdir -p biomni-ami-package/{admin-backend,admin-frontend,client-frontend}
mkdir -p biomni-ami-package/{agent,config,scripts,sql}

# 复制产物
cp admin/backend/target/biomni-admin.jar biomni-ami-package/admin-backend/
cp -r client/frontend/dist/* biomni-ami-package/client-frontend/
cp -r admin/frontend/dist/* biomni-ami-package/admin-frontend/

# Agent (Cython 编译后)
cp -r agent/ biomni-ami-package/agent/
# 清理不需要的文件
rm -rf biomni-ami-package/agent/{__pycache__,.env,logs/,data/,*.c,setup_cython.py,build/}
find biomni-ami-package/agent -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
find biomni-ami-package/agent -name "*.pyc" -delete

# !! 关键检查: 确认没有 .py 源文件泄露 (除了 __init__.py 和 main.py)
echo "=== 检查残留 .py 文件 ==="
find biomni-ami-package/agent -name "*.py" ! -name "__init__.py" ! -name "main.py"
# 如果输出不为空，说明有遗漏，需要删除或编译

# 配置模板
cp config-templates/* biomni-ami-package/config/

# SQL
cp sql/schema.sql biomni-ami-package/sql/
cp sql/seed.sql.tpl biomni-ami-package/sql/

# 脚本
cp scripts/* biomni-ami-package/scripts/

# !! 最终安全检查: 确认没有敏感文件
echo "=== 检查敏感文件 ==="
find biomni-ami-package -name "*.pem" -o -name ".git" -o -name "deploy.sh" \
  -o -name ".env" ! -name ".env.tpl" -o -name "docker-compose.yml"
# 输出应为空

# 打包
tar -czf biomni-ami-package.tar.gz biomni-ami-package/
```

---

### Phase 2: EC2 实例准备

#### Step 2.1: 启动基础 EC2

```bash
# AWS Console 或 CLI
aws ec2 run-instances \
  --image-id ami-0c7217cdde317cfec \  # Ubuntu 22.04 LTS
  --instance-type t3.xlarge \
  --key-name your-key \
  --security-group-ids sg-xxx \
  --block-device-mappings '[{"DeviceName":"/dev/sda1","Ebs":{"VolumeSize":100,"VolumeType":"gp3"}}]' \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=biomni-ami-builder}]'

# 安全组开放: 22(SSH), 80(HTTP), 443(HTTPS)
```

#### Step 2.2: 安装系统依赖

```bash
#!/bin/bash
# install-deps.sh

set -e

# 更新系统
sudo apt update && sudo apt upgrade -y

# 基础工具
sudo apt install -y curl wget vim htop unzip jq

# MySQL 8.0
sudo apt install -y mysql-server-8.0
sudo systemctl enable mysql
sudo systemctl start mysql

# Redis 7.x
sudo apt install -y redis-server
sudo systemctl enable redis-server

# Java 17
sudo apt install -y openjdk-17-jdk-headless

# Python 3.11 + venv + pip
sudo apt install -y python3.11 python3.11-venv python3-pip

# Node.js 20 (仅在需要策略 B 重新构建前端时安装)
# curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
# sudo apt install -y nodejs

# Nginx
sudo apt install -y nginx
sudo systemctl enable nginx

# PM2 (如果前端用 PM2 serve)
# sudo npm install -g pm2

# 安全工具
sudo apt install -y fail2ban ufw unattended-upgrades
```

#### Step 2.3: 创建系统用户和目录

```bash
# 创建 biomni 系统用户 (无登录 shell)
sudo useradd -r -m -d /opt/biomni -s /usr/sbin/nologin biomni

# 创建目录结构
sudo mkdir -p /opt/biomni/{admin-backend,admin-frontend,client-frontend}
sudo mkdir -p /opt/biomni/{agent,config,scripts,sql,logs,data,upload,backups}

# 设置权限
sudo chown -R biomni:biomni /opt/biomni
```

#### Step 2.4: 上传部署包并解压

```bash
# 从开发机上传
scp biomni-ami-package.tar.gz ubuntu@<EC2_IP>:/tmp/

# 在 EC2 上解压
cd /tmp
tar -xzf biomni-ami-package.tar.gz
sudo cp -r biomni-ami-package/* /opt/biomni/
sudo chown -R biomni:biomni /opt/biomni
```

#### Step 2.5: 安装 Python Agent 依赖

```bash
# 创建 venv
sudo -u biomni python3.11 -m venv /opt/biomni/agent/venv

# 安装依赖
sudo -u biomni /opt/biomni/agent/venv/bin/pip install --upgrade pip
sudo -u biomni /opt/biomni/agent/venv/bin/pip install -r /opt/biomni/agent/requirements-api.txt

# 安装 biomni 包本身 (Cython 编译后的 .so 文件仍需要 setup.py/pyproject.toml 注册包)
sudo -u biomni /opt/biomni/agent/venv/bin/pip install -e /opt/biomni/agent/

# 安装 BCrypt 工具 (用于 first-boot 生成密码 hash)
sudo -u biomni /opt/biomni/agent/venv/bin/pip install bcrypt

# 验证 Agent 可以正常 import
sudo -u biomni /opt/biomni/agent/venv/bin/python -c "from biomni.agent import A1; print('✅ Agent import OK')"
```

> 注意：Cython 编译的 .so 文件依赖特定的 Python 版本 (如 cpython-311)。
> AMI 中安装的 Python 版本必须与编译时一致。

#### Step 2.6: 配置 Systemd 服务

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
ExecStart=/usr/bin/java -Xms512m -Xmx1g \
  -jar /opt/biomni/admin-backend/biomni-admin.jar \
  --spring.profiles.active=ami \
  --spring.config.additional-location=file:/opt/biomni/config/application-ami.properties
Restart=always
RestartSec=10
StandardOutput=append:/opt/biomni/logs/admin-backend.log
StandardError=append:/opt/biomni/logs/admin-backend-error.log

[Install]
WantedBy=multi-user.target
```

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
EnvironmentFile=/opt/biomni/config/agent.env
ExecStart=/opt/biomni/agent/venv/bin/python main.py
Restart=always
RestartSec=10
Environment="PYTHONUNBUFFERED=1"
StandardOutput=append:/opt/biomni/logs/agent.log
StandardError=append:/opt/biomni/logs/agent-error.log

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
```

#### Step 2.7: 配置 Redis 密码

```bash
# Redis 配置模板 — first-boot 时替换密码
sudo tee /opt/biomni/config/redis.conf.tpl > /dev/null << 'EOF'
bind 127.0.0.1
port 6379
requirepass __REDIS_PASSWORD__
appendonly yes
maxmemory 512mb
maxmemory-policy allkeys-lru
EOF
```

---

### Phase 3: 编写 first-boot.sh (核心脚本)

这是 AMI 最关键的脚本，用户启动实例后自动执行一次，完成所有初始化。

**`/opt/biomni/scripts/first-boot.sh`**

```bash
#!/bin/bash
# ============================================================
# Biomni First Boot Initialization Script
# 仅在首次启动时执行，完成密码生成、配置替换、数据库初始化
# ============================================================

set -e

LOCK_FILE="/opt/biomni/.initialized"
LOG_FILE="/opt/biomni/logs/first-boot.log"
CONFIG_DIR="/opt/biomni/config"
SQL_DIR="/opt/biomni/sql"
CRED_FILE="/home/ubuntu/biomni-credentials.txt"

# 如果已初始化，跳过
if [ -f "$LOCK_FILE" ]; then
    echo "Biomni already initialized. Skipping first-boot."
    exit 0
fi

exec > >(tee -a "$LOG_FILE") 2>&1
echo "=========================================="
echo "Biomni First Boot - $(date)"
echo "=========================================="

# ------------------------------------------
# 1. 生成随机密码和密钥
# ------------------------------------------
echo "[1/8] Generating secrets..."

MYSQL_ROOT_PASSWORD=$(openssl rand -base64 32 | tr -d '=/+' | head -c 32)
MYSQL_BIOMNI_PASSWORD=$(openssl rand -base64 32 | tr -d '=/+' | head -c 32)
MYSQL_BIOMNI_USER="biomni"
MYSQL_BIOMNI_DB="biomni"
JWT_SECRET=$(openssl rand -base64 64 | tr -d '=/+' | head -c 64)
INTERNAL_SECRET=$(openssl rand -base64 32 | tr -d '=/+' | head -c 32)
REDIS_PASSWORD=$(openssl rand -base64 32 | tr -d '=/+' | head -c 32)
ADMIN_DEFAULT_PASSWORD=$(openssl rand -base64 12 | tr -d '=/+' | head -c 12)

# URL-encode MySQL 密码 (用于 Python SQLAlchemy 连接串)
MYSQL_BIOMNI_PASSWORD_URLENCODED=$(python3 -c "import urllib.parse; print(urllib.parse.quote('${MYSQL_BIOMNI_PASSWORD}'))")

# 获取实例信息 (使用 IMDSv2，AWS Marketplace 要求)
TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 300" --connect-timeout 3 || echo "")
if [ -n "$TOKEN" ]; then
    INSTANCE_ID=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/instance-id || echo "unknown")
    PUBLIC_IP=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/public-ipv4 || echo "127.0.0.1")
    PRIVATE_IP=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/local-ipv4 || echo "127.0.0.1")
else
    INSTANCE_ID="unknown"
    PUBLIC_IP="127.0.0.1"
    PRIVATE_IP="127.0.0.1"
fi

echo "  Instance ID: $INSTANCE_ID"
echo "  Public IP:   $PUBLIC_IP"
echo "  Private IP:  $PRIVATE_IP"

# ------------------------------------------
# 2. 配置 MySQL
# ------------------------------------------
echo "[2/8] Configuring MySQL..."

# 设置 root 密码并创建 biomni 用户
sudo mysql -u root <<EOSQL
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '${MYSQL_ROOT_PASSWORD}';
CREATE DATABASE IF NOT EXISTS ${MYSQL_BIOMNI_DB} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '${MYSQL_BIOMNI_USER}'@'localhost' IDENTIFIED BY '${MYSQL_BIOMNI_PASSWORD}';
GRANT ALL PRIVILEGES ON ${MYSQL_BIOMNI_DB}.* TO '${MYSQL_BIOMNI_USER}'@'localhost';
FLUSH PRIVILEGES;
EOSQL

# 导入表结构
mysql -u ${MYSQL_BIOMNI_USER} -p"${MYSQL_BIOMNI_PASSWORD}" ${MYSQL_BIOMNI_DB} < ${SQL_DIR}/schema.sql

# 生成管理员密码的 BCrypt hash
ADMIN_PASSWORD_HASH=$(/opt/biomni/agent/venv/bin/python3 -c "
import bcrypt
password = '${ADMIN_DEFAULT_PASSWORD}'.encode('utf-8')
hashed = bcrypt.hashpw(password, bcrypt.gensalt(rounds=10))
print(hashed.decode('utf-8'))
")

# 替换 seed.sql 中的占位符并执行
sed "s|__ADMIN_PASSWORD_HASH__|${ADMIN_PASSWORD_HASH}|g" \
    ${SQL_DIR}/seed.sql.tpl > /tmp/seed.sql
mysql -u ${MYSQL_BIOMNI_USER} -p"${MYSQL_BIOMNI_PASSWORD}" ${MYSQL_BIOMNI_DB} < /tmp/seed.sql
rm -f /tmp/seed.sql

echo "  MySQL configured successfully."

# ------------------------------------------
# 3. 配置 Redis
# ------------------------------------------
echo "[3/8] Configuring Redis..."

sed "s|__REDIS_PASSWORD__|${REDIS_PASSWORD}|g" \
    ${CONFIG_DIR}/redis.conf.tpl > /tmp/redis-biomni.conf
sudo cp /tmp/redis-biomni.conf /etc/redis/redis.conf
rm -f /tmp/redis-biomni.conf
sudo systemctl restart redis-server

echo "  Redis configured with password."

# ------------------------------------------
# 4. 生成 Spring Boot 配置
# ------------------------------------------
echo "[4/8] Generating Spring Boot configuration..."

sed -e "s|__MYSQL_DB__|${MYSQL_BIOMNI_DB}|g" \
    -e "s|__MYSQL_USER__|${MYSQL_BIOMNI_USER}|g" \
    -e "s|__MYSQL_PASSWORD__|${MYSQL_BIOMNI_PASSWORD}|g" \
    -e "s|__JWT_SECRET__|${JWT_SECRET}|g" \
    -e "s|__REDIS_PASSWORD__|${REDIS_PASSWORD}|g" \
    ${CONFIG_DIR}/application-ami.properties.tpl \
    > ${CONFIG_DIR}/application-ami.properties

chown biomni:biomni ${CONFIG_DIR}/application-ami.properties
chmod 600 ${CONFIG_DIR}/application-ami.properties

echo "  Spring Boot config generated."
```

```bash
# ------------------------------------------
# 5. 生成 Agent 配置
# ------------------------------------------
echo "[5/8] Generating Agent configuration..."

sed -e "s|__JWT_SECRET__|${JWT_SECRET}|g" \
    -e "s|__INTERNAL_SECRET__|${INTERNAL_SECRET}|g" \
    -e "s|__MYSQL_USER__|${MYSQL_BIOMNI_USER}|g" \
    -e "s|__MYSQL_PASSWORD_URLENCODED__|${MYSQL_BIOMNI_PASSWORD_URLENCODED}|g" \
    -e "s|__MYSQL_DB__|${MYSQL_BIOMNI_DB}|g" \
    -e "s|__PUBLIC_IP__|${PUBLIC_IP}|g" \
    ${CONFIG_DIR}/agent.env.tpl \
    > ${CONFIG_DIR}/agent.env

chown biomni:biomni ${CONFIG_DIR}/agent.env
chmod 600 ${CONFIG_DIR}/agent.env

echo "  Agent config generated."

# ------------------------------------------
# 6. 配置 Nginx
# ------------------------------------------
echo "[6/8] Configuring Nginx..."

# 直接使用模板 (Nginx 配置中无需替换变量，全部用 localhost)
sudo cp ${CONFIG_DIR}/nginx-biomni.conf.tpl /etc/nginx/sites-available/biomni
sudo ln -sf /etc/nginx/sites-available/biomni /etc/nginx/sites-enabled/biomni
sudo rm -f /etc/nginx/sites-enabled/default

# 测试 Nginx 配置
sudo nginx -t
sudo systemctl restart nginx

echo "  Nginx configured."

# ------------------------------------------
# 7. 启动所有服务
# ------------------------------------------
echo "[7/8] Starting services..."

sudo systemctl enable biomni-admin biomni-agent
sudo systemctl start biomni-admin
sleep 5
sudo systemctl start biomni-agent

echo "  Services started."

# ------------------------------------------
# 8. 保存凭据并完成
# ------------------------------------------
echo "[8/8] Saving credentials..."

cat > ${CRED_FILE} <<EOF
============================================================
  Biomni Installation Credentials
  Generated: $(date)
  Instance:  ${INSTANCE_ID}
============================================================

MySQL Root Password:    ${MYSQL_ROOT_PASSWORD}
MySQL Biomni User:      ${MYSQL_BIOMNI_USER}
MySQL Biomni Password:  ${MYSQL_BIOMNI_PASSWORD}

Admin Portal:   http://${PUBLIC_IP}/admin
Admin Username: admin
Admin Email:    admin@biomni.com
Admin Password: ${ADMIN_DEFAULT_PASSWORD}

Client Portal:  http://${PUBLIC_IP}/

JWT Secret:     ${JWT_SECRET}
Redis Password: ${REDIS_PASSWORD}

IMPORTANT:
  1. 请立即登录管理后台修改默认密码
  2. 在管理后台 > 系统配置 中设置 LLM API Key
  3. 建议配置 HTTPS (Let's Encrypt)

============================================================
EOF

chmod 600 ${CRED_FILE}
chown ubuntu:ubuntu ${CRED_FILE}

# 标记已初始化
touch ${LOCK_FILE}

echo ""
echo "=========================================="
echo "  Biomni initialization completed!"
echo "  Credentials saved to: ${CRED_FILE}"
echo "=========================================="
```

#### 注册为 cloud-init 首次启动任务

```bash
# /etc/cloud/cloud.cfg.d/99-biomni.cfg
runcmd:
  - /opt/biomni/scripts/first-boot.sh
```

或者使用 systemd oneshot service：

```ini
# /etc/systemd/system/biomni-first-boot.service
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
sudo systemctl enable biomni-first-boot.service
```

---

### Phase 4: 安全加固与清理

#### Step 4.1: 防火墙

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw --force enable
```

#### Step 4.2: SSH 加固

```bash
sudo sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl restart sshd
```

#### Step 4.3: 自动安全更新

```bash
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

#### Step 4.4: Fail2Ban

```bash
sudo apt install -y fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

#### Step 4.5: MySQL 安全加固

```bash
# 禁止远程 root 登录 (first-boot 中已处理)
# 删除匿名用户和测试数据库
sudo mysql -u root -p"${MYSQL_ROOT_PASSWORD}" <<EOSQL
DELETE FROM mysql.user WHERE User='';
DROP DATABASE IF EXISTS test;
DELETE FROM mysql.db WHERE Db='test' OR Db='test\\_%';
FLUSH PRIVILEGES;
EOSQL
```

#### Step 4.5.1: 源码保护 — 文件权限加固

```bash
# Agent 目录: 只有 biomni 用户可读写执行，ubuntu 用户无法查看
sudo chown -R biomni:biomni /opt/biomni/agent
sudo chmod -R 750 /opt/biomni/agent
# .so 文件设为只读+可执行
find /opt/biomni/agent -name "*.so" -exec chmod 550 {} \;

# Spring Boot JAR: 只有 biomni 用户可读
sudo chown biomni:biomni /opt/biomni/admin-backend/biomni-admin.jar
sudo chmod 500 /opt/biomni/admin-backend/biomni-admin.jar

# 配置文件: 只有 biomni 用户可读 (包含密码)
sudo chmod 600 /opt/biomni/config/*.properties /opt/biomni/config/*.env 2>/dev/null || true
# 模板文件可以稍宽松
sudo chmod 640 /opt/biomni/config/*.tpl

# 凭据文件: 只有 ubuntu 用户可读
# (在 first-boot.sh 中已设置 chmod 600)

# 验证: ubuntu 用户无法读取 agent 源码
sudo -u ubuntu ls /opt/biomni/agent/biomni/ 2>&1 | grep -q "Permission denied" && echo "✅ 权限正确" || echo "❌ 权限有问题"
```

#### Step 4.6: 设置 MOTD (登录欢迎信息)

```bash
sudo tee /etc/motd > /dev/null << 'EOF'

  ╔═══════════════════════════════════════════════════════╗
  ║  🧬 Biomni - AI-Powered Biomedical Assistant         ║
  ╠═══════════════════════════════════════════════════════╣
  ║                                                       ║
  ║  Quick Start:                                         ║
  ║    cat ~/biomni-credentials.txt                       ║
  ║                                                       ║
  ║  Admin Portal:  http://<PUBLIC_IP>/admin              ║
  ║  Client Portal: http://<PUBLIC_IP>/                   ║
  ║                                                       ║
  ║  Health Check:  /opt/biomni/scripts/health-check.sh   ║
  ║  View Logs:     journalctl -u biomni-admin -f         ║
  ║                 journalctl -u biomni-agent -f         ║
  ║                                                       ║
  ║  Docs: https://docs.biomni.com                        ║
  ╚═══════════════════════════════════════════════════════╝

EOF
```

#### Step 4.7: AMI 创建前清理

```bash
#!/bin/bash
# /opt/biomni/scripts/pre-ami-cleanup.sh
# 在创建 AMI 快照之前执行

set -e

echo "=== Pre-AMI Cleanup ==="

# 1. 停止所有服务
sudo systemctl stop biomni-admin biomni-agent nginx mysql redis-server

# 2. 删除初始化标记 (让新实例重新执行 first-boot)
sudo rm -f /opt/biomni/.initialized

# 3. 删除生成的配置文件 (保留模板)
sudo rm -f /opt/biomni/config/application-ami.properties
sudo rm -f /opt/biomni/config/agent.env
sudo rm -f /home/ubuntu/biomni-credentials.txt

# 4. 清理 MySQL 数据 (first-boot 会重新初始化)
sudo rm -rf /var/lib/mysql/*
sudo mysqld --initialize-insecure --user=mysql

# 5. 清理 Redis 数据
sudo rm -f /var/lib/redis/dump.rdb /var/lib/redis/appendonly.aof

# 6. 清理日志
sudo rm -rf /opt/biomni/logs/*
sudo rm -rf /var/log/*.log /var/log/**/*.log
sudo journalctl --vacuum-time=1s

# 7. 清理临时文件
sudo rm -rf /tmp/* /var/tmp/*

# 8. 清理 SSH host keys (新实例会自动重新生成)
sudo rm -f /etc/ssh/ssh_host_*

# 9. 清理 bash history
sudo rm -f /root/.bash_history /home/ubuntu/.bash_history
history -c

# 10. 清理 cloud-init (让新实例重新执行)
sudo cloud-init clean --logs

echo "=== Cleanup complete. Ready to create AMI. ==="
```

---

### Phase 5: 创建 AMI

```bash
# 1. 执行清理脚本
sudo /opt/biomni/scripts/pre-ami-cleanup.sh

# 2. 在 AWS Console 或 CLI 创建 AMI
aws ec2 create-image \
  --instance-id i-xxxxxxxxxxxxxxxxx \
  --name "Biomni-v1.0.0-$(date +%Y%m%d)" \
  --description "Biomni AI-Powered Biomedical Assistant - All-in-One AMI" \
  --no-reboot \
  --tag-specifications \
    'ResourceType=image,Tags=[{Key=Product,Value=Biomni},{Key=Version,Value=1.0.0}]'

# 3. 等待 AMI 创建完成
aws ec2 wait image-available --image-ids ami-xxxxxxxxx

# 4. 共享给 AWS Marketplace 账户
aws ec2 modify-image-attribute \
  --image-id ami-xxxxxxxxx \
  --launch-permission "Add=[{UserId=679593333241}]"
```

---

### Phase 6: 测试验证

#### Step 6.1: 从 AMI 启动新实例测试

```bash
# 启动测试实例
aws ec2 run-instances \
  --image-id ami-xxxxxxxxx \
  --instance-type t3.xlarge \
  --key-name your-test-key \
  --security-group-ids sg-xxx

# 等待实例启动 + first-boot 完成 (约 3-5 分钟)
```

#### Step 6.2: 验证清单

```
□ SSH 登录后看到 MOTD 欢迎信息
□ ~/biomni-credentials.txt 存在且包含随机密码
□ 每次启动实例密码都不同 (验证随机性)
□ http://<IP>/admin 可访问管理后台
□ http://<IP>/ 可访问用户端
□ 管理后台可用默认密码登录
□ 管理后台 > 系统配置 可设置 LLM API Key
□ 设置 API Key 后，用户端可正常对话
□ WebSocket 连接正常
□ 文件上传功能正常
□ MySQL 仅监听 127.0.0.1
□ Redis 仅监听 127.0.0.1 且有密码
□ 外部无法直接访问 9999/8000/3306/6379 端口
□ health-check.sh 所有检查通过
□ 服务重启后自动恢复 (kill 进程后 systemd 自动拉起)
□ 实例 reboot 后所有服务自动启动
```

---

## 6. 变量替换总览表

| 占位符 | 生成方式 | 使用位置 |
|--------|----------|----------|
| `__MYSQL_ROOT_PASSWORD__` | `openssl rand` | MySQL root 用户 |
| `__MYSQL_USER__` | 固定 `biomni` | Spring Boot, Agent |
| `__MYSQL_PASSWORD__` | `openssl rand` | Spring Boot properties |
| `__MYSQL_PASSWORD_URLENCODED__` | Python urllib.parse.quote | Agent .env (SQLAlchemy URL) |
| `__MYSQL_DB__` | 固定 `biomni` | Spring Boot, Agent, SQL |
| `__JWT_SECRET__` | `openssl rand -base64 64` | Spring Boot, Agent (共享) |
| `__INTERNAL_SECRET__` | `openssl rand` | Agent 内部 API 认证 |
| `__REDIS_PASSWORD__` | `openssl rand` | Spring Boot, Redis, Agent |
| `__ADMIN_PASSWORD_HASH__` | BCrypt(随机密码) | seed.sql → MySQL |
| `__PUBLIC_IP__` | EC2 metadata API | Agent CORS, 凭据文件 |

---

## 7. 需要注意的关键问题

### 7.1 JWT Secret 同步

Spring Boot 和 Python Agent 必须使用完全相同的 JWT Secret，否则用户在客户端登录后 WebSocket 连接会认证失败。

- Spring Boot: `jwt.secret` in `application-ami.properties`
- Agent: `JWT_SECRET_KEY` in `agent.env`
- 算法: 两端都使用 `HS512`

### 7.2 前端 API 地址

AMI 中前端通过 Nginx 反向代理访问后端，所有 API 请求使用相对路径：

```
前端请求 /api/xxx  →  Nginx proxy_pass  →  Spring Boot :9999
前端请求 /ws/xxx   →  Nginx proxy_pass  →  Agent :8000
前端请求 /agent-api/xxx → Nginx proxy_pass → Agent :8000
```

这要求前端代码中不能硬编码 `http://xxx:9999` 这样的绝对地址。

### 7.3 Agent main.py 中的 reload 参数

当前 `agent/main.py` 中 uvicorn 启动参数 `reload=True`，生产环境必须改为 `reload=False`：

```python
# agent/main.py — AMI 版本
uvicorn.run(
    "api.app:app",
    host="0.0.0.0",
    port=8000,
    reload=False,  # 生产环境关闭热重载
    log_level="info",
    workers=2       # 可选: 多 worker
)
```

### 7.4 Spring Boot 端口统一

当前 local 用 9999，prod 用 19999。AMI profile 统一使用 `9999`，Nginx 代理到此端口。

### 7.5 MySQL 版本

当前 docker-compose 用的是 MySQL 5.7，AMI 中直接安装 MySQL 8.0。需确认 SQL 语法兼容性（当前 init.sql 语法兼容 8.0）。

### 7.6 数据持久化

AMI 实例的 EBS 卷默认在实例终止时删除。建议用户：
- 使用 EBS 快照定期备份
- 或将数据库迁移到 RDS

### 7.7 HTTPS 配置

AMI 默认只配置 HTTP (80)。用户如需 HTTPS，需要：
1. 绑定域名
2. 安装 certbot: `sudo apt install certbot python3-certbot-nginx`
3. 申请证书: `sudo certbot --nginx -d your-domain.com`

可在 first-boot 后提示用户操作。

### 7.8 敏感文件清理

以下文件绝对不能出现在 AMI 中：

| 文件 | 原因 |
|------|------|
| `biomni.pem` (根目录) | SSH 私钥 |
| `admin/frontend/src/biomni.pem` | SSH 私钥副本 |
| `.git/` | Git 历史可能包含密码提交记录 |
| `admin/backend/deploy.sh` | 包含服务器 IP |
| `admin/backend/logs/` | 开发环境日志 |
| `agent/.env` | 包含明文数据库密码 |
| `docker-compose.yml` | 包含明文密码 |
| `README.md` | 包含服务器 IP 和部署命令 |

在 Step 1.6 打包部署包时，确保这些文件不被包含。

### 7.9 Agent 多 Worker 与 WebSocket 兼容性

`agent/main.py` 中如果设置 `workers=2`，WebSocket 连接可能会路由到不同 worker 导致状态丢失。
当前 `ConnectionManager` 使用内存字典存储连接，多 worker 下不共享。

建议 AMI 中保持 `workers=1`，或后续改用 Redis pub/sub 做 WebSocket 广播。

### 7.10 Admin Frontend 的 VITE_BASE_API 路径

当前 `admin/frontend/src/utils/http/index.js` 中：
```javascript
export const request = createAxios({
  baseURL: import.meta.env.VITE_BASE_API,
})
```

`VITE_BASE_API` 在 `.env.development` 中设置为 `http://127.0.0.1:9999/api`（绝对路径）。
AMI 的 `.env.production` 中需设置为 `/api`（相对路径），由 Nginx 代理。

### 7.11 Spring Boot JDBC Driver 类名

当前 `application-prod.properties` 中使用的是：
```
spring.datasource.mysql.driver-class-name=com.mysql.jdbc.Driver
```
这是 MySQL 5.x 的旧驱动类名。MySQL 8.0 应使用：
```
spring.datasource.mysql.driver-class-name=com.mysql.cj.jdbc.Driver
```
AMI 模板中已修正为 `com.mysql.cj.jdbc.Driver`。

---

## 8. 健康检查脚本

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
curl -sf http://127.0.0.1:8000/health > /dev/null 2>&1; check "Agent /health" $?
curl -sf http://127.0.0.1:9999/health/alive > /dev/null 2>&1; check "Admin /health/alive" $?
curl -sf http://127.0.0.1/ > /dev/null 2>&1; check "Client Frontend" $?

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

## 9. 日志轮转配置

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

---

## 10. 升级方案

当需要发布新版本 AMI 时：

### 10.1 全新 AMI (推荐)

重复 Phase 1-5，创建新版本 AMI。用户需要迁移数据：

```bash
# 旧实例导出
mysqldump -u biomni -p biomni > biomni-backup.sql
scp biomni-backup.sql user@new-instance:/tmp/

# 新实例导入 (first-boot 完成后)
mysql -u biomni -p biomni < /tmp/biomni-backup.sql
```

### 10.2 原地升级脚本 (可选)

提供 `/opt/biomni/scripts/upgrade.sh`，用户在现有实例上执行：

```bash
#!/bin/bash
# upgrade.sh — 从 S3 下载新版本并替换

set -e
VERSION=$1
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
sudo tar -xzf /tmp/admin-frontend.tar.gz -C /opt/biomni/admin-frontend/
sudo tar -xzf /tmp/client-frontend.tar.gz -C /opt/biomni/client-frontend/

# 5. 数据库迁移 (如有)
# mysql -u biomni -p biomni < /opt/biomni/sql/migration-v${VERSION}.sql

# 6. 重启服务
sudo systemctl start biomni-admin biomni-agent

echo "Upgrade to v${VERSION} complete!"
```

---

## 11. 完整文件清单 (AMI 内)

```
/opt/biomni/
├── admin-backend/
│   └── biomni-admin.jar
├── admin-frontend/
│   ├── index.html
│   └── assets/...
├── client-frontend/
│   ├── index.html
│   └── assets/...
├── agent/
│   ├── main.py
│   ├── api/
│   ├── biomni/
│   ├── core/
│   ├── models/
│   ├── services/
│   ├── requirements-api.txt
│   └── venv/
├── config/
│   ├── application-ami.properties.tpl   # 模板
│   ├── application-ami.properties       # first-boot 生成 (AMI 中不存在)
│   ├── agent.env.tpl                    # 模板
│   ├── agent.env                        # first-boot 生成 (AMI 中不存在)
│   ├── nginx-biomni.conf.tpl            # Nginx 模板
│   └── redis.conf.tpl                   # Redis 模板
├── scripts/
│   ├── first-boot.sh
│   ├── health-check.sh
│   ├── backup.sh
│   ├── upgrade.sh
│   └── pre-ami-cleanup.sh
├── sql/
│   ├── schema.sql                       # 纯建表
│   └── seed.sql.tpl                     # 初始数据模板
├── data/                                # Agent 运行数据
├── upload/                              # 用户上传文件
├── logs/                                # 统一日志目录
└── backups/                             # 数据库备份

/etc/systemd/system/
├── biomni-admin.service
├── biomni-agent.service
└── biomni-first-boot.service

/etc/nginx/sites-available/
└── biomni

/etc/logrotate.d/
└── biomni
```

---

## 12. 操作 Checklist (按顺序执行)

### 开发机操作
- [ ] 修改 Client Frontend `client.ts` 支持相对路径 API 地址
- [ ] 修改 Client Frontend `useWebSocket.ts` 支持相对路径 WS 地址
- [ ] 修改 Client Frontend `agentClient.ts` 支持相对路径 Agent API 地址
- [ ] 修改 Admin Frontend `.env.production` 设置 `VITE_BASE_API=/api`
- [ ] 修改 Admin Frontend `infra-client.js` 移除硬编码 URL 和注释中的 Token
- [ ] 修改 Agent `main.py` 关闭 reload，设置 workers=1
- [ ] 修改 `pom.xml` 添加 `<finalName>biomni-admin</finalName>`
- [ ] 新增 `application-ami.properties` Spring Boot profile (使用 `com.mysql.cj.jdbc.Driver`)
- [ ] 将 `init.sql` 拆分为 `schema.sql` + `seed.sql.tpl`
- [ ] 编写配置模板文件 (`.tpl`)
- [ ] 编写 `first-boot.sh` (使用 IMDSv2 获取 metadata)
- [ ] 编写 `health-check.sh` (Admin 端点为 `/health/alive`)
- [ ] 编写 systemd service 文件
- [ ] 编写 Nginx 配置模板
- [ ] 构建 Client Frontend dist
- [ ] 构建 Admin Frontend dist
- [ ] 构建 Spring Boot JAR
- [ ] 确认部署包中不包含 `.pem`、`.git`、`.env`、`deploy.sh`、`logs/` 等敏感文件
- [ ] 打包部署包 `biomni-ami-package.tar.gz`

### EC2 操作
- [ ] 启动 Ubuntu 22.04 t3.xlarge 实例
- [ ] 安装系统依赖 (MySQL 8.0, Redis, Java 17, Python 3.11, Nginx)
- [ ] 创建 biomni 用户和目录结构
- [ ] 上传并解压部署包
- [ ] 安装 Python Agent 依赖 (venv + pip)
- [ ] 部署 systemd service 文件
- [ ] 配置防火墙 (ufw)
- [ ] 配置 SSH 加固
- [ ] 配置 fail2ban
- [ ] 配置自动安全更新
- [ ] 配置日志轮转
- [ ] 设置 MOTD
- [ ] 手动测试 first-boot.sh (验证完整流程)
- [ ] 执行 pre-ami-cleanup.sh
- [ ] 创建 AMI 快照

### 验证操作
- [ ] 从 AMI 启动全新实例
- [ ] 验证 first-boot 自动执行
- [ ] 验证凭据文件生成
- [ ] 验证管理后台可登录 (`http://<IP>/admin`)
- [ ] 验证用户端可访问 (`http://<IP>/`)
- [ ] 验证 LLM 配置后可对话 (WebSocket 正常)
- [ ] 验证文件上传功能正常 (通过 `/agent-api/` 路由)
- [ ] 验证端口安全 (外部扫描 9999/8000/3306/6379 不可达)
- [ ] 验证 reboot 后所有服务自动恢复
- [ ] 多次启动验证密码随机性
- [ ] 验证 AMI 中无 `.pem`、`.git`、明文密码等敏感文件
- [ ] 验证 `/health/alive` (Admin) 和 `/health` (Agent) 端点正常

---

**文档版本**: 1.0
**最后更新**: 2026-02-08
**作者**: Biomni Team
