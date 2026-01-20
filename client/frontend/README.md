# Biomni Client Frontend

基于 React + TypeScript + Ant Design X 的 AI 对话客户端。

## 技术栈

- **React 18** - 前端框架
- **TypeScript** - 类型系统
- **Ant Design X** - AI 对话组件
- **Ant Design** - UI 组件库
- **Vite** - 构建工具
- **Zustand** - 状态管理
- **React Router** - 路由管理
- **Axios** - HTTP 客户端

## 项目结构

```
src/
├── api/                    # API 接口
│   ├── client.ts          # Axios 配置
│   ├── auth.ts            # 认证 API
│   └── conversation.ts    # 对话 API
├── components/            # 组件
│   ├── ChatWindow.tsx     # 对话窗口（双栏布局）
│   └── ExecutionPanel.tsx # Agent 执行过程面板
├── hooks/                 # 自定义 Hooks
│   └── useWebSocket.ts    # WebSocket Hook
├── pages/                 # 页面
│   ├── Login.tsx          # 登录页
│   ├── SSOLogin.tsx       # SSO 登录页
│   └── ChatLayout.tsx     # 对话布局页
├── store/                 # 状态管理
│   └── authStore.ts       # 认证状态
├── types/                 # 类型定义
│   └── index.ts           # 全局类型
├── App.tsx                # 应用入口
└── main.tsx               # 主文件
```

## 功能特性

### 1. 用户认证
- ✅ 用户名密码登录
- ✅ SSO 单点登录（从 Admin 前端跳转）
- ✅ JWT Token 认证
- ✅ 自动 Token 刷新

### 2. 对话功能
- ✅ 对话列表（左侧边栏）
- ✅ 创建/删除对话
- ✅ 双栏对话窗口
  - 左侧：问答区域
  - 右侧：Agent 执行过程
- ✅ 实时消息推送（WebSocket）
- ✅ 历史消息加载

### 3. Agent 执行可视化
- ✅ 实时显示执行步骤
- ✅ 工具调用详情
- ✅ 代码执行结果
- ✅ 执行时长统计

## 开发指南

### 安装依赖

```bash
cd client/frontend
npm install
# 或
pnpm install
```

### 启动开发服务器

**方式 1：Mock 模式（推荐，不需要后端）**

```bash
npm run dev:mock
```

访问 http://localhost:3001

测试账号：
- 邮箱: `user@biomni.com`
- 密码: `user123`

**方式 2：真实 API 模式**

```bash
npm run dev
```

需要先启动后端服务：
- Spring Boot: http://localhost:8083
- Python Agent: http://localhost:8000

### 构建生产版本

```bash
npm run build
```

### 预览生产版本

```bash
npm run preview
```

## 环境变量

### 开发环境 (.env.development)

```env
VITE_API_URL=http://localhost:8083
VITE_WS_URL=ws://localhost:8000
```

### 生产环境 (.env.production)

```env
VITE_API_URL=https://api.biomni.com
VITE_WS_URL=wss://api.biomni.com
```

## 核心组件说明

### ChatLayout

对话布局页面，包含：
- 左侧对话列表（使用 Ant Design X Conversations 组件）
- 右侧对话窗口

### ChatWindow

对话窗口组件，双栏布局：
- 左侧：问答区域（使用 Ant Design X Bubble + Sender）
- 右侧：Agent 执行过程面板

### ExecutionPanel

Agent 执行过程可视化面板，显示：
- 执行步骤时间线
- 工具调用详情
- 代码执行结果
- 错误信息

### useWebSocket Hook

WebSocket 连接管理：
- 自动连接/重连
- 消息接收和发送
- 执行状态管理

## API 接口

### 认证接口

```typescript
// 登录
POST /api/auth/login
{
  "username": "user",
  "password": "password"
}

// 获取当前用户
GET /api/auth/me
```

### 对话接口

```typescript
// 获取对话列表
GET /api/conversations?page=1&size=20

// 创建对话
POST /api/conversations
{
  "title": "新对话"
}

// 获取消息
GET /api/conversations/{id}/messages

// 发送消息
POST /api/conversations/{id}/messages
{
  "content": "你好"
}
```

### WebSocket 接口

```typescript
// 连接
ws://localhost:8000/ws/chat/{conversationId}?token={jwt_token}

// 发送消息
{
  "type": "send_message",
  "content": "你好"
}

// 接收消息
{
  "type": "execution_start" | "execution_step" | "execution_complete" | "execution_error",
  "step": {...},
  "message": {...}
}
```

## SSO 单点登录

从 Admin 前端跳转到 Client 前端：

```typescript
// Admin 前端
const token = localStorage.getItem('token');
window.open(`http://localhost:3001/auth/sso?token=${token}`, '_blank');
```

Client 前端会自动：
1. 从 URL 获取 Token
2. 验证 Token 有效性
3. 保存到 localStorage
4. 清除 URL 中的 Token
5. 跳转到首页

## 注意事项

### 1. CORS 配置

开发环境需要配置 Spring Boot 和 Python Agent 的 CORS：

```java
// Spring Boot
config.addAllowedOrigin("http://localhost:3001");
```

```python
# Python Agent
allow_origins=["http://localhost:3001"]
```

### 2. WebSocket 连接

- 确保 Python Agent 服务已启动
- Token 必须有效
- 连接断开会自动重连（5秒后）

### 3. Token 管理

- Token 保存在 localStorage
- 401 错误会自动跳转到登录页
- SSO 登录后会立即清除 URL 中的 Token

## 部署

### Docker 部署

```dockerfile
# Dockerfile
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Nginx 配置

```nginx
server {
    listen 80;
    server_name localhost;
    
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }
}
```

## 开发计划

- [x] 基础项目结构
- [x] 用户认证（登录、SSO）
- [x] 对话列表
- [x] 对话窗口（双栏布局）
- [x] WebSocket 实时通信
- [x] Agent 执行过程可视化
- [ ] 文件上传功能
- [ ] Markdown 渲染优化
- [ ] 代码高亮优化
- [ ] 对话搜索
- [ ] 对话导出
- [ ] 用户设置

## 许可证

MIT
