# MyBiomni AMI 上架 AWS Marketplace：构建/参数化/首启初始化 技术方案（Plan v2）

最后更新：2026-02-08  
仓库范围：`admin/backend`（Java/Spring Boot）、`admin/frontend`（Vue/Vite）、`agent`（FastAPI/WebSocket）、`client/frontend`（React/Vite）、`admin/backend/data/init/mysql/init.sql`（数据模型）

> 本文目标：把 MyBiomni 做成 **AWS Marketplace AMI（单机 All‑in‑One）**，实现客户启动 EC2 后自动初始化即可用，并确保 AMI 中**不包含任何固定明文敏感信息**（DB 密码/JWT Secret/邮箱密码/SSH key 等）。

---

## 0. 结论先行：AMI 产品的三条硬规则

1. **前端永远同源**：浏览器只访问 `http(s)://<实例域名或IP>/...`，不暴露后端/agent 端口，不需要按实例重编译前端。  
2. **配置只在首启生成**：所有密码/密钥/连接串在第一次启动时生成并落到 `/opt/biomni/config/biomni.env`，服务通过 systemd 注入。  
3. **制作 AMI 前必须清理**：AMI 镜像里不能残留任何已生成的 `biomni.env`、初始化哨兵、日志、bash_history、构建时临时文件。

---

## 1. 目标架构（All‑in‑One，推荐作为 Marketplace 首发形态）

### 1.1 组件与端口（内部）

| 组件 | 监听地址 | 端口 | 对外暴露 |
|---|---:|---:|---|
| Nginx | 0.0.0.0 | 80/443 | ✅（唯一入口） |
| Admin Backend（Spring Boot） | 127.0.0.1 | 9999 | ❌ |
| Agent（FastAPI） | 127.0.0.1 | 8000 | ❌ |
| MySQL 8.0 | 127.0.0.1 | 3306 | ❌ |
| Redis（可选） | 127.0.0.1 | 6379 | ❌ |

安全组建议：
- Inbound：`80`（必需），`443`（可选），`22`（可选且建议限制办公公网 IP）
- Outbound：默认允许（Agent 需要访问外部 LLM/工具时必须）

### 1.2 Nginx 路由规划（外部）

| 外部路径 | 目标 | 说明 |
|---|---|---|
| `/` | `/opt/biomni/client-frontend/` | 用户端 React 静态资源 |
| `/admin/` | `/opt/biomni/admin-frontend/` | 管理后台 Vue 静态资源 |
| `/api/` | `http://127.0.0.1:9999/api/` | Spring Boot API（注意保留 `/api` 前缀） |
| `/ws/` | `http://127.0.0.1:8000/ws/` | Agent WebSocket（FastAPI 路由前缀就是 `/ws`） |
| `/agent-api/` | `http://127.0.0.1:8000/api/` | Agent 上传等 REST（FastAPI 路由前缀是 `/api`，对外用 `/agent-api` 避免冲突） |

---

## 1.3 没有域名怎么办？（直接用 IP 访问）

结论：**可以完全用 IP**。本方案默认不依赖域名：前端、API、WebSocket、上传均按“同源相对路径”设计，用户直接访问 `http://<public-ip>/` 即可。

### 1) 默认用 HTTP + Public IP

- 访问地址（客户侧）：
  - 管理后台：`http://<public-ip>/admin/`
  - 用户端：`http://<public-ip>/`
- WebSocket：前端基于 `window.location` 自动推导 `ws://<public-ip>/ws/...`（Nginx 代理到 `127.0.0.1:8000`），不需要域名。

### 2) Public IP 会变怎么办？

EC2 的 Public IPv4 在**停止/启动**后可能变化（除非绑定 Elastic IP）。

建议在客户文档里写清两种选项：
- **测试/临时使用**：接受 IP 变化，需要时在控制台查看新的 Public IP。
- **生产/稳定访问（推荐）**：客户创建并绑定 **Elastic IP (EIP)**，以后用固定 IP 访问。

### 3) 没有域名怎么上 HTTPS？

- 通常公共 CA 不为“裸 IP”签发浏览器信任证书，因此**没有域名时建议先用 HTTP**。
- 若客户强制要加密传输，常见路线：
  - 客户自带域名 + 证书（最通用）
  - 或在客户的 ALB / CloudFront 前终止 TLS（你的实例仍然只提供 HTTP）
  - 或自签证书（浏览器会提示不受信任，不推荐面向公网用户）

---

## 2. 现状与风险点（基于当前代码）

### 2.1 必须“变量化/去明文”的配置

#### Admin Backend（Spring Boot）
文件：
- `admin/backend/src/main/resources/application-local.properties`
- `admin/backend/src/main/resources/application-prod.properties`

必须处理：
- `spring.datasource.mysql.*`：从 env 注入（避免 jar 内出现固定账号/密码）
- `jwt.secret`：从 env 注入（首启生成，与 Agent 共享）
- `spring.data.redis.host`：AMI 默认 localhost（prod 里当前是 consul 域名，不适用于 AMI 单机）
- `spring.mail.*`：**不要写死**；建议改为 `${SPRING_MAIL_PASSWORD:}` 或迁移到系统配置/Secrets Manager

#### Agent（FastAPI）
文件：`agent/core/config.py`（Pydantic Settings）

必须处理：
- `JWT_SECRET_KEY` / `JWT_ALGORITHM`：与 Spring Boot 一致
- `DATABASE_URL`：首启脚本生成（建议使用不需要 URL encode 的密码字符集）
- `USE_MOCK_AGENT=false`：AMI 必须关闭
- `AGENT_DATA_PATH` / `AGENT_UPLOAD_DATA_PATH`：固定到 `/opt/biomni/*`

#### 前端（Vite）
目标：生产构建后的静态文件**不包含任何实例 IP/域名**，运行时自动同源访问。

必须处理：
- `client/frontend`：API baseURL 不要默认 `localhost:8083`
- WebSocket：不要默认 `ws://localhost:8000`
- 上传：建议改为 `/agent-api/upload`（详见 4.3）
- `admin/frontend`：生产环境实际使用 `VITE_BASE_API`、`VITE_PUBLIC_PATH`；需要保证 `/admin/` 部署可用

### 2.2 数据库初始化的“默认管理员密码”问题

文件：`admin/backend/data/init/mysql/init.sql`

当前行为：
- 插入默认 admin，bcrypt hash 固定（所有实例相同）  

AMI 要求：
- 首启必须生成随机管理员初始密码，并写回数据库，同时设置 `force_password_change=1`。

### 2.3 外部依赖提示（需要明确可配置）

`admin/frontend/src/utils/http/infra-client.js` 默认会使用 `VITE_INFRA_API_URL || 'https://api.e2b.9527.tech'`。  
如果 Marketplace 产品不希望默认依赖该外部服务，建议：
- 在文档中明确说明用途/数据流向；并提供配置项 `VITE_INFRA_API_URL`
- 或在 Marketplace 版本中关闭该功能入口（按业务选择）

---

## 3. 统一变量生成与注入（核心方案）

### 3.1 单一配置中心：`/opt/biomni/config/biomni.env`

原则：**所有服务只吃一个 env 文件**，由首启脚本生成；systemd 通过 `EnvironmentFile=` 注入。

建议变量集（示例结构，不包含真实值）：

```bash
# /opt/biomni/config/biomni.env (0600)

# --- internal ports ---
BIOMNI_BACKEND_PORT=9999
BIOMNI_AGENT_PORT=8000

# --- mysql ---
BIOMNI_DB_HOST=127.0.0.1
BIOMNI_DB_PORT=3306
BIOMNI_DB_NAME=biomni
BIOMNI_DB_USER=biomni
BIOMNI_DB_PASSWORD=...generated...
MYSQL_ROOT_PASSWORD=...generated...

# --- jwt shared ---
BIOMNI_JWT_ALG=HS512
BIOMNI_JWT_SECRET=...generated...

# --- spring boot env override（relaxed binding）---
SPRING_PROFILES_ACTIVE=ami
SERVER_PORT=9999
SPRING_DATASOURCE_MYSQL_JDBC_URL=jdbc:mysql://127.0.0.1:3306/biomni?useUnicode=true&characterEncoding=utf8&useSSL=false&serverTimezone=GMT%2B8
SPRING_DATASOURCE_MYSQL_USERNAME=biomni
SPRING_DATASOURCE_MYSQL_PASSWORD=...same as BIOMNI_DB_PASSWORD...
JWT_SECRET=...same as BIOMNI_JWT_SECRET...
SPRING_DATA_REDIS_HOST=127.0.0.1
SPRING_DATA_REDIS_PORT=6379

# --- agent ---
JWT_SECRET_KEY=...same as BIOMNI_JWT_SECRET...
JWT_ALGORITHM=HS512
DATABASE_URL=mysql+pymysql://biomni:...@127.0.0.1:3306/biomni
USE_MOCK_AGENT=false
AGENT_DATA_PATH=/opt/biomni/data
AGENT_UPLOAD_DATA_PATH=/opt/biomni/upload
```

> 为什么这样设计：  
> - Spring Boot 不需要再做 `sed` 替换 properties，直接由 env 覆盖（更稳）。  
> - Agent 的 Pydantic Settings 天生支持 env。  
> - Nginx 配置可固定使用 `127.0.0.1:9999/8000`，不需要模板渲染（最省心）。

### 3.2 密钥/密码生成策略（避免 URL encode & sed 转义）

推荐 DB 密码使用 hex，只包含 `[0-9a-f]`，方便拼 `DATABASE_URL`：

```bash
BIOMNI_DB_PASSWORD="$(openssl rand -hex 24)"
MYSQL_ROOT_PASSWORD="$(openssl rand -hex 24)"
BIOMNI_JWT_SECRET="$(openssl rand -hex 32)"
ADMIN_PASSWORD="$(openssl rand -base64 18 | tr -d '=+/')"
```

### 3.3 “统一替换”怎么做（建议优先级）

1) **能用 env 覆盖就不用模板**（Spring/Agent）  
2) Nginx 采用**固定配置文件**（内部端口固定即可）  
3) 仅在需要动态域名/TLS 时才做模板渲染（`envsubst`），避免 `sed` 大面积替换

---

## 4. 代码/配置需要怎么改（按模块给出落点）

### 4.1 Spring Boot（Admin Backend）

#### 4.1.1 清理明文敏感配置（必须）

把 `application-local.properties`、`application-prod.properties` 中的敏感项改为 env 占位或删除，避免被打进 jar：

```properties
spring.datasource.mysql.password=${SPRING_DATASOURCE_MYSQL_PASSWORD:}
jwt.secret=${JWT_SECRET:}
spring.mail.password=${SPRING_MAIL_PASSWORD:}
```

同时建议把 driver 从 `com.mysql.jdbc.Driver` 更新为 `com.mysql.cj.jdbc.Driver`（与 MySQL Connector/J 8 一致）。

#### 4.1.2 增加 AMI profile（推荐）

新增：`admin/backend/src/main/resources/application-ami.properties`  
只写“非敏感默认值”，敏感继续由 env 覆盖：

```properties
server.port=${SERVER_PORT:9999}
spring.datasource.mysql.driver-class-name=com.mysql.cj.jdbc.Driver
```

systemd 通过 `SPRING_PROFILES_ACTIVE=ami` 启动即可。

### 4.2 Agent（FastAPI）

#### 4.2.1 生产启动方式（必须）

AMI 内不要用 `reload=True`。建议 systemd：

```bash
uvicorn api.app:app --host 127.0.0.1 --port 8000 --log-level info
```

#### 4.2.2 LLM Key/Provider 的配置方式说明（建议写进客户文档）

Agent 在 `agent/services/config_service.py` 会从 DB 的 `system_config` 表读取：
- `agent.*`（如 `agent.source`、`agent.llm` 等）
- `llm.*`（如 `llm.anthropic_api_key`、`llm.openai_api_key` 等）

管理后台已有接口：
- `POST /api/config/reset` 写入默认 `agent.*`（不含 key）
- `POST /api/config/update` / `batch-update` 写入 key
- `POST /api/config/status` 检查当前 provider 是否已配 key

Marketplace 客户体验建议：
1) 首启生成管理员密码  
2) 管理员登录 `/admin/`  
3) 在“系统配置”页选择 provider 并填 API Key  
4) 再开始对话使用 Agent

### 4.3 Client Frontend（React）

目标：生产构建产物不写死任何域名/IP，全部同源。

#### 4.3.1 API baseURL 同源（必须）

修改：`client/frontend/src/api/client.ts`  
把默认 `baseURL` 改为同源空字符串：

```ts
baseURL: import.meta.env.VITE_API_URL || '',
```

（请求路径本身是 `'/api/...'`，会走 Nginx → Spring Boot）

#### 4.3.2 WebSocket 同源推导（必须）

修改：`client/frontend/src/hooks/useWebSocket.ts`  
用页面协议推导 `ws/wss`：

```ts
const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const wsUrl = import.meta.env.VITE_WS_URL || `${protocol}//${window.location.host}`;
```

当前拼接逻辑是 `${wsUrl}/ws/chat/...`，与 Nginx `/ws/` 代理匹配。

#### 4.3.3 上传路径改为 `/agent-api`（强烈推荐）

修改：
- `client/frontend/src/api/agentClient.ts`：默认 `baseURL` 同源
- `client/frontend/src/api/upload.ts`：把上传路径改成 `/agent-api/upload`

原因：FastAPI upload 前缀是 `/api`，而 Spring 也用 `/api`；对外用 `/agent-api` 更清晰、也更不容易误配。

#### 4.3.4 `.env.production` 约定（建议）

新增/调整：`client/frontend/.env.production`

```env
VITE_API_URL=
VITE_WS_URL=
VITE_AGENT_API_URL=
```

留空表示同源；只有特殊部署才需要覆盖。

### 4.4 Admin Frontend（Vue）

#### 4.4.1 生产环境变量统一（必须）

Admin 前端 axios baseURL 读取的是 `VITE_BASE_API`（见 `admin/frontend/src/utils/http/index.js`）。

建议 `admin/frontend/.env.production`：

```env
VITE_PUBLIC_PATH=/admin/
VITE_USE_PROXY=false
VITE_BASE_API=/api
VITE_TITLE=WarpHelix Admin
VITE_USE_HASH=false
VITE_INFRA_API_URL=
```

#### 4.4.2 路由 base 支持 /admin（推荐）

修改：`admin/frontend/src/router/index.js`  
把 base 写死 `'/'` 改为读取 `VITE_PUBLIC_PATH`：

```js
const base = import.meta.env.VITE_PUBLIC_PATH || '/'
history: isHash ? createWebHashHistory(base) : createWebHistory(base),
```

并确保 Nginx 为 `/admin/` 配置 `try_files ... /admin/index.html;`。

---

## 5. 数据库初始化与默认管理员“首启随机化”

### 5.1 初始化策略

AMI 内置 `init.sql`（来自仓库 `admin/backend/data/init/mysql/init.sql`），但**不在制作 AMI 时执行**，而在实例首次启动时执行：

1) 安装并启动 MySQL  
2) 生成 `MYSQL_ROOT_PASSWORD`、`BIOMNI_DB_PASSWORD`  
3) 配置 root 密码，创建业务用户 `biomni`  
4) 执行 `init.sql` 完成建库建表与默认数据  
5) 生成 `ADMIN_PASSWORD`，用 bcrypt 写回 admin 表，同时设置 `force_password_change=1`

### 5.2 bcrypt 生成推荐方式（避免引入 Java 工具）

使用 `apache2-utils` 的 `htpasswd`：

```bash
ADMIN_BCRYPT="$(htpasswd -bnBC 10 "" "${ADMIN_PASSWORD}" | tr -d ':\n')"
mysql -u root -p"${MYSQL_ROOT_PASSWORD}" biomni -e \
  "UPDATE admin SET password='${ADMIN_BCRYPT}', force_password_change=1 WHERE id=1;"
```

---

## 6. First‑boot 自动化（幂等 + IMDSv2 + 输出凭据）

### 6.1 触发方式（推荐）

使用 systemd oneshot：
- `biomni-firstboot.service`（开机运行一次）
- `/opt/biomni/scripts/first-boot.sh`
- 哨兵：`/opt/biomni/.initialized`

### 6.2 `first-boot.sh` 关键步骤（建议顺序）

1) IMDSv2 获取实例信息（可选：仅用于输出访问 URL；不参与配置渲染也可以）  
2) 生成变量并写入 `/opt/biomni/config/biomni.env`（0600）  
3) 初始化 MySQL（建议业务用户使用 `mysql_native_password` 以兼容 `pymysql`）  
4) 执行 `init.sql`  
5) 随机化管理员密码 + 强制改密  
6) 启用并启动 `biomni-admin`、`biomni-agent`、`nginx`  
7) 写入 `/home/ubuntu/biomni-credentials.txt`（0600），并提示客户立刻改密  
8) 写入哨兵文件，确保幂等

> 注意：AMI 制作阶段一定要保证 **不预生成** `biomni.env`、不写入 `.initialized`。

---

## 7. AMI 构建流程（建议可重复、可审计）

> 推荐：先手工跑通一轮，再固化为 Packer 或 EC2 Image Builder。

### Phase A：构建发布包（不含源码）

建议发布包结构（示例）：

```
release/
├── admin-backend/biomni-admin.jar
├── admin-frontend/           (dist)
├── client-frontend/          (dist)
├── agent/                    (venv + 代码 或 pyinstaller 二进制)
├── sql/init.sql
├── nginx/biomni.conf
├── systemd/*.service
└── scripts/first-boot.sh
```

关键要求：
- 不要把 `node_modules/`、`.env`、日志、私钥文件打包
- 如要做代码保护：Agent 可考虑 PyInstaller；Java 可做混淆（可选）

---

## 7.1 不暴露源代码：交付策略与可达边界

### 结论（现实边界）

- AMI 会交付到客户 AWS 账号，客户对 EC2 拥有 root 权限；**你无法做到绝对不可逆**。
- 你能做到的是：**不交付可读源码仓库**（不包含 `.git`、`.py`、`.java/.ts/.vue` 等），只交付运行所需构建产物，并用混淆/打包提高逆向门槛。

### 交付策略：只放 Release Artifacts，不放 Repo

AMI 的 `/opt/biomni/` 仅包含：
- Spring Boot：`*.jar`（可选：混淆后的 jar）
- 前端：`dist/` 静态文件（禁用 sourcemap，避免 `*.map`）
- Agent：
  - **优先方案**：PyInstaller 产物（可执行文件/目录模式），AMI 内不保留 `.py`
  - 备选方案：venv + `.pyc`（删除 `.py`；仍可能被还原，保护弱于 PyInstaller）
- SQL：`init.sql`（schema + 初始数据；不包含任何客户专属密码）
- 运维：systemd unit、nginx conf、first-boot 脚本

### 组件级建议

1) Agent（Python）
- 推荐：在 Ubuntu 22.04 环境用 PyInstaller 打包，AMI 内只保留二进制与必要资源。
- 注意：PyInstaller 体积更大，需在 Golden Instance 验证启动、依赖与性能。

2) Admin Backend（Java）
- 最小化：只放 `jar`，不放 `src/`、不放 Maven 缓存与构建产物目录。
- 加强（可选）：ProGuard/R8 混淆；需要额外配置 keep 规则以避免 Spring 反射相关问题。

3) 前端（Vue/React）
- 前端最终会在浏览器侧可见，无法真正隐藏；建议做到：
  - 只交付 `dist/`
  - 生产构建关闭 sourcemap（不生成 `*.map`）
  - 开启压缩/混淆（terser），降低可读性

### AMI 制作前的“源码/敏感残留”排查清单（强制）

在 Golden Instance 上创建 AMI 前，至少确保不存在：
- 源码仓库与依赖：`.git/`、`src/`、`node_modules/`、开发用 `.env`
- 私钥与部署脚本：`*.pem`、含固定 IP/账号的部署脚本与日志
- 首启生成物：`/opt/biomni/config/biomni.env`、`/opt/biomni/.initialized`、`/home/ubuntu/biomni-credentials.txt`
- 历史与日志：`~/.bash_history`、可能包含 token/密码的日志文件

### Phase B：Golden Instance 预装依赖 + 放置发布包

操作要点：
- OS 推荐 Ubuntu 22.04 LTS
- 安装：Nginx、Java17、Python3.11、MySQL8、（可选）Redis、apache2-utils
- 目录：全部落到 `/opt/biomni/*`
- systemd：放置并 enable（但不要运行 first-boot 造成写入 env）
- Nginx：放置配置并 enable（可先不启动）

### Phase C：自测（必须）

建议自测项：
- `curl http://127.0.0.1:9999/health/alive`
- `curl http://127.0.0.1:8000/health`
- 浏览器访问：`/`、`/admin/`
- 登录、创建对话、WebSocket 收发、上传附件

### Phase D：制作 AMI 前清理（必须）

必须清理：
- `/opt/biomni/config/biomni.env`
- `/opt/biomni/.initialized`
- first-boot 生成的 credentials 文件（如存在）
- shell history、临时文件、构建缓存
- 如果曾启动过服务，清理日志中可能包含的 token/密码

建议清理：
- 包管理缓存
- 旧的 SSH host keys（让实例启动时重新生成）

### Phase E：创建 AMI + 回归验证

1) 停止服务  
2) Create image（命名建议包含版本号 + 日期）  
3) 用新 AMI 启动一台“干净实例”做回归，确保 first‑boot 正常运行

---

## 8. AWS Marketplace 上架流程要点（AMI）

> 具体控制台 UI 会变，这里给“必经环节清单”。

1) 卖家资质与收款/税务信息  
2) 产品资料（描述、截图、支持渠道、使用文档）  
3) 提交 AMI 并通过安全扫描  
4) 定价/许可策略：
   - 首发建议先 BYOL/免费，跑通闭环
   - 后续如做付费，再接入 entitlement/metering（专项）

Marketplace 扫描常见卡点（要提前防雷）：
- 多余端口对外开放
- 弱口令/固定默认密码
- AMI 内残留 `.env`/credentials/logs/私钥
- 系统软件包漏洞（需要升级）

---

## 9. 客户侧使用流程（建议写成“客户版部署指南”）

1) 从 Marketplace 启动实例（选择合适机型，如 `t3.xlarge` 起步）  
2) 等待 1–3 分钟 first‑boot 完成  
3) SSH 登录查看 `/home/ubuntu/biomni-credentials.txt` 获取初始管理员密码  
4) 访问：
   - 管理后台：`http://<public-ip>/admin/`
   - 用户端：`http://<public-ip>/`
5) 首次登录强制改密  
6) 在“系统配置”中配置 LLM provider 与 API Key（`/api/config/status` 应显示配置正常）  
7) 开始对话使用 Agent（WebSocket & 上传都走同源 Nginx）

---

## 10. 交付物清单（建议）

AMI 内建议包含以下文件（模板/固定配置皆可）：
- `/opt/biomni/scripts/first-boot.sh`
- `/etc/systemd/system/biomni-firstboot.service`
- `/etc/systemd/system/biomni-admin.service`
- `/etc/systemd/system/biomni-agent.service`
- `/etc/nginx/sites-available/biomni.conf`（并 link 到 `sites-enabled`）
- `/opt/biomni/sql/init.sql`

---

## 11. 下一步（建议按顺序落地）

1) 先把前端做成同源（client：API/WS/Upload；admin：/admin base + /api base）  
2) 清理后端 properties 的明文敏感项（jar 内不能出现固定 secret）  
3) 写 first‑boot 并做幂等（失败可重跑）  
4) Golden Instance 跑通 → 清理 → 出 AMI → 新实例回归  
5) 固化为 Packer / Image Builder → Marketplace 上架
