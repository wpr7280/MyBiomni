# WarpHelix AMI 构建状态

**最后更新**: 2026-02-08

## ✅ 已完成的工作

### 1. 代码修改（按 Plan 3 第 4 节）

#### Client Frontend (React)
- ✅ `client.ts` - baseURL 改为空字符串（同源）
- ✅ `useWebSocket.ts` - WebSocket 地址同源推导
- ✅ `agentClient.ts` - baseURL 改为空字符串
- ✅ `upload.ts` - 上传路径改为 `/agent-api/upload`
- ✅ 新增 `.env.production` - 所有 VITE 变量留空

#### Admin Frontend (Vue)
- ✅ `.env.production` - 更新为 `/api` 和 `/admin/`
- ✅ `router/index.js` - base 读取 `VITE_PUBLIC_PATH`
- ✅ `infra-client.js` - 移除硬编码 `https://api.e2b.9527.tech`

#### Spring Boot Backend
- ✅ `application-local.properties` - 敏感值改为 env 占位符
- ✅ `application-prod.properties` - 敏感值改为 env 占位符
- ✅ 新增 `application-ami.properties` - AMI profile
- ✅ `pom.xml` - 添加 `<finalName>biomni-admin</finalName>`
- ✅ MySQL driver 更新为 `com.mysql.cj.jdbc.Driver`

#### Agent (FastAPI)
- ✅ `config.py` - CORS 默认值改为 `["http://127.0.0.1"]`
- ✅ `main.py` - `reload=False`（生产环境）

### 2. AMI 构建文件（ami-build/ 目录）

#### 脚本 (scripts/)
- ✅ `first-boot.sh` - 首次启动初始化（密码生成、数据库初始化、CORS 配置）
- ✅ `health-check.sh` - 健康检查（服务、端口、HTTP 端点、资源）
- ✅ `pre-ami-cleanup.sh` - AMI 制作前清理
- ✅ `backup.sh` - 数据库备份

#### Systemd 服务 (systemd/)
- ✅ `biomni-firstboot.service` - 首次启动 oneshot
- ✅ `biomni-admin.service` - Spring Boot 服务
- ✅ `biomni-agent.service` - Agent 服务

#### 配置文件 (config/)
- ✅ `nginx-biomni.conf` - Nginx 反向代理配置
- ✅ `logrotate-biomni` - 日志轮转配置

#### SQL (sql/)
- ✅ `init.sql` - 数据库初始化（从 admin/backend/data/init/mysql/ 复制）

#### 文档
- ✅ `README.md` - 使用说明
- ✅ `CHECKLIST.md` - 详细操作清单

## 📋 下一步操作

### Phase A: 本地构建（开发机）

```bash
# 1. 构建 Client Frontend
cd client/frontend
npm install
npm run build
# 验证: dist/ 目录存在，无 .map 文件

# 2. 构建 Admin Frontend
cd admin/frontend
pnpm install
pnpm run build
# 验证: dist/ 目录存在，无 .map 文件

# 3. 构建 Spring Boot JAR
cd admin/backend
mvn clean package -DskipTests
# 验证: target/biomni-admin.jar 存在

# 4. 打包发布包（可选，或直接在 EC2 上传）
mkdir -p release/{admin-backend,admin-frontend,client-frontend,agent}
cp target/biomni-admin.jar release/admin-backend/
cp -r ../admin/frontend/dist/* release/admin-frontend/
cp -r ../client/frontend/dist/* release/client-frontend/
cp -r ../../agent release/
tar -czf biomni-release.tar.gz release/
```

### Phase B: EC2 Golden Instance 部署

参考 `ami-build/README.md` 和 `ami-build/CHECKLIST.md`

关键步骤：
1. 启动 Ubuntu 22.04 t3.xlarge
2. 安装依赖（MySQL 8.0, Redis, Nginx, Java 17, Python 3.11）
3. 创建 biomni 用户和目录
4. 上传构建产物
5. 部署 systemd 服务和 Nginx 配置
6. 安装 Agent Python 依赖
7. 安全加固
8. 测试 first-boot.sh
9. 清理并创建 AMI

## 🔍 关键设计决策（已实现）

1. **CORS 配置** - first-boot.sh 自动将 PUBLIC_IP 加入 CORS_ORIGINS
2. **密码生成** - 使用 `openssl rand -hex`（无需 URL encode）
3. **BCrypt** - 使用 `htpasswd` 生成（不依赖 Python bcrypt）
4. **前端同源** - 所有 API/WS 请求通过 Nginx 代理，不暴露后端端口
5. **配置注入** - 单一 `biomni.env`，systemd 通过 EnvironmentFile 注入
6. **强制改密** - 默认管理员 `force_password_change=1`
7. **Agent workers** - 保持 `workers=1`（WebSocket 兼容性）
8. **健康检查端点** - Admin: `/health/alive`, Agent: `/health`

## ⚠️ 重要注意事项

1. **Cython 编译**（可选）
   - 需要在目标平台（Ubuntu 22.04 + Python 3.11 + x86_64）上执行
   - 参考 Plan 3 第 7.2 节
   - 如果遇到问题，可回退到 PyInstaller 或直接部署源码（开发阶段）

2. **pip install -e 问题**
   - Cython 编译后不要用 `pip install -e .`
   - 依靠 systemd `WorkingDirectory` 让 Python 找到包
   - 只需 `pip install -r requirements-api.txt` 安装第三方依赖

3. **CORS 必须包含 PUBLIC_IP**
   - 浏览器 Origin header 是 `http://<public-ip>`
   - FastAPI CORSMiddleware 会校验，否则 preflight 失败
   - first-boot.sh 已自动处理

4. **客户绑定域名后**
   - 需要手动编辑 `/opt/biomni/config/biomni.env`
   - 在 `CORS_ORIGINS` 中加入新的 origin（如 `https://your-domain.com`）
   - 重启 Agent 服务: `sudo systemctl restart biomni-agent`

## 📚 参考文档

- **完整技术方案**: `other/docs/AMI_BUILD_PLAN_3.md` (1639 行)
- **使用说明**: `ami-build/README.md`
- **操作清单**: `ami-build/CHECKLIST.md`
- **Plan 1**: `other/docs/AMI_BUILD_TECHNICAL_PLAN.md`
- **Plan 2**: `other/docs/AMI_BUILD_PLAN_2.md`

## 🎯 当前状态

- [x] 代码修改完成
- [x] AMI 构建文件创建完成
- [ ] 本地构建前端和 JAR
- [ ] EC2 Golden Instance 部署
- [ ] 测试验证
- [ ] 创建 AMI
- [ ] 回归测试
- [ ] AWS Marketplace 提交

---

**准备就绪，可以开始本地构建和 EC2 部署！**
