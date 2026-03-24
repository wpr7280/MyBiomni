# 客户端 API 接口文档

## 1. 接口概述

### 1.1 基础信息

| 项目 | 说明 |
|------|------|
| **Base URL** | `http://localhost:8083` (开发环境) |
| **认证方式** | JWT Token (Bearer) |
| **数据格式** | JSON |
| **字符编码** | UTF-8 |

### 1.2 统一响应格式

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

**状态码说明**：
- `200`: 成功
- `400`: 请求参数错误
- `401`: 未授权（Token 无效或过期）
- `403`: 权限不足
- `404`: 资源不存在
- `500`: 服务器内部错误

---

## 2. 认证接口

### 2.1 用户登录

**接口**: `POST /api/auth/login`

**请求参数**:
```json
{
  "email": "user@example.com",
  "password": "password"
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "userId": "1",
    "email": "user@example.com",
    "username": "user123",
    "role": "user",
    "forcePasswordChange": false
  }
}
```

**TypeScript 类型**:
```typescript
interface LoginRequest {
  email: string;
  password: string;
}

interface LoginResponse {
  token: string;
  userId: string;
  email: string;
  username: string;
  role: string;
  forcePasswordChange: boolean;
}

interface User {
  id: number;
  username: string;
  email: string;
  role: string;
  realName?: string;
  avatar?: string;
}
```

---

### 2.2 获取当前用户信息

**接口**: `GET /api/auth/me`

**请求头**:
```
Authorization: Bearer {token}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "userId": "1",
    "email": "user@example.com",
    "username": "user123",
    "role": "user",
    "forcePasswordChange": false
  }
}
```

---

### 2.3 用户登出

**接口**: `POST /api/auth/logout`

**请求头**:
```
Authorization: Bearer {token}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "登出成功",
  "data": null
}
```

---

## 3. 对话管理接口

### 3.1 获取对话列表

**接口**: `GET /api/conversations`

**请求参数**:
| 参数 | 类型 | 必填 | 说明 | 默认值 |
|------|------|------|------|--------|
| page | int | 否 | 页码 | 1 |
| size | int | 否 | 每页数量 | 20 |

**请求示例**:
```
GET /api/conversations?page=1&size=20
```

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "title": "关于蛋白质结构的问题",
      "status": "active",
      "messageCount": 5,
      "lastMessageAt": "2025-01-20T10:30:00",
      "createdAt": "2025-01-20T09:00:00",
      "updatedAt": "2025-01-20T10:30:00"
    },
    {
      "id": 2,
      "title": "基因测序分析",
      "status": "completed",
      "messageCount": 10,
      "lastMessageAt": "2025-01-19T15:20:00",
      "createdAt": "2025-01-19T14:00:00",
      "updatedAt": "2025-01-19T15:20:00"
    }
  ]
}
```

**TypeScript 类型**:
```typescript
interface Conversation {
  id: number;
  title: string;
  status: 'active' | 'completed' | 'failed' | 'cancelled';
  messageCount: number;
  lastMessageAt?: string;
  createdAt: string;
  updatedAt: string;
}
```

---

### 3.2 创建新对话

**接口**: `POST /api/conversations`

**请求参数**:
```json
{
  "title": "新对话"
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "创建成功",
  "data": {
    "id": 3,
    "title": "新对话",
    "status": "active",
    "messageCount": 0,
    "createdAt": "2025-01-20T11:00:00",
    "updatedAt": "2025-01-20T11:00:00"
  }
}
```

---

### 3.3 获取对话详情

**接口**: `GET /api/conversations/{id}`

**路径参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 对话ID |

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "title": "关于蛋白质结构的问题",
    "status": "active",
    "messageCount": 5,
    "totalTokens": 1500,
    "totalDurationMs": 5000,
    "lastMessageAt": "2025-01-20T10:30:00",
    "createdAt": "2025-01-20T09:00:00",
    "updatedAt": "2025-01-20T10:30:00"
  }
}
```

---

### 3.4 删除对话

**接口**: `DELETE /api/conversations/{id}`

**路径参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 对话ID |

**响应示例**:
```json
{
  "code": 200,
  "message": "删除成功",
  "data": null
}
```

---

## 4. 消息管理接口

### 4.1 获取对话消息

**接口**: `GET /api/conversations/{conversationId}/messages`

**路径参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| conversationId | int | 对话ID |

**请求参数**:
| 参数 | 类型 | 必填 | 说明 | 默认值 |
|------|------|------|------|--------|
| page | int | 否 | 页码 | 1 |
| size | int | 否 | 每页数量 | 50 |

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "conversationId": 1,
      "role": "user",
      "content": "什么是蛋白质的二级结构？",
      "contentType": "text",
      "tokens": 15,
      "createdAt": "2025-01-20T09:00:00"
    },
    {
      "id": 2,
      "conversationId": 1,
      "role": "assistant",
      "content": "蛋白质的二级结构是指...",
      "contentType": "markdown",
      "tokens": 150,
      "inputTokens": 15,
      "outputTokens": 135,
      "createdAt": "2025-01-20T09:00:30"
    }
  ]
}
```

**TypeScript 类型**:
```typescript
interface Message {
  id: number;
  conversationId: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  contentType?: 'text' | 'markdown' | 'code';
  tokens?: number;
  inputTokens?: number;
  outputTokens?: number;
  createdAt: string;
}
```

---

### 4.2 发送消息

**接口**: `POST /api/conversations/{conversationId}/messages`

**路径参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| conversationId | int | 对话ID |

**请求参数**:
```json
{
  "content": "什么是蛋白质的二级结构？"
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "发送成功",
  "data": {
    "id": 1,
    "conversationId": 1,
    "role": "user",
    "content": "什么是蛋白质的二级结构？",
    "contentType": "text",
    "createdAt": "2025-01-20T09:00:00"
  }
}
```

**说明**:
- 此接口只保存用户消息到数据库并检查配额
- 实际的 Agent 执行通过 WebSocket 进行
- 前端需要在调用此接口后，通过 WebSocket 发送消息给 Python Agent

---

## 5. WebSocket 接口

### 5.1 连接

**端点**: `ws://localhost:8000/ws/chat/{conversationId}`

**连接参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| conversationId | int | 是 | 对话ID（路径参数） |
| token | string | 是 | JWT Token（查询参数） |

**连接示例**:
```javascript
const token = localStorage.getItem('token');
const ws = new WebSocket(
  `ws://localhost:8000/ws/chat/123?token=${encodeURIComponent(token)}`
);
```

---

### 5.2 发送消息

**客户端 → 服务器**:
```json
{
  "type": "send_message",
  "content": "什么是蛋白质的二级结构？"
}
```

---

### 5.3 接收消息

#### 5.3.1 执行开始

**服务器 → 客户端**:
```json
{
  "type": "execution_start",
  "message_id": 1
}
```

#### 5.3.2 执行步骤

**服务器 → 客户端**:
```json
{
  "type": "execution_step",
  "step": {
    "id": 1,
    "conversationId": 1,
    "messageId": 2,
    "stepOrder": 1,
    "stepType": "tool_call",
    "stepName": "搜索文献",
    "toolName": "search_papers",
    "toolInput": {
      "query": "protein secondary structure",
      "limit": 5
    },
    "toolOutput": "找到 5 篇相关文献...",
    "status": "success",
    "durationMs": 1200,
    "startedAt": "2025-01-20T09:00:01",
    "completedAt": "2025-01-20T09:00:02"
  }
}
```

**TypeScript 类型**:
```typescript
interface ExecutionStep {
  id: number;
  conversationId: number;
  messageId: number;
  stepOrder: number;
  stepType: 'reasoning' | 'tool_call' | 'result';
  stepName?: string;
  toolName?: string;
  toolInput?: any;
  toolOutput?: string;
  status: 'running' | 'success' | 'failed';
  errorMessage?: string;
  durationMs: number;
  startedAt: string;
  completedAt?: string;
}
```

#### 5.3.3 执行完成

**服务器 → 客户端**:
```json
{
  "type": "execution_complete",
  "message": {
    "id": 2,
    "conversationId": 1,
    "role": "assistant",
    "content": "蛋白质的二级结构是指...",
    "contentType": "markdown",
    "tokens": 150,
    "inputTokens": 15,
    "outputTokens": 135,
    "createdAt": "2025-01-20T09:00:30"
  }
}
```

#### 5.3.4 执行错误

**服务器 → 客户端**:
```json
{
  "type": "execution_error",
  "error": "配额不足"
}
```

---

## 6. 内部 API（供 Python Agent 调用）

### 6.1 更新配额

**接口**: `POST /api/internal/quota/update`

**请求头**:
```
X-Internal-Secret: your-internal-api-secret
```

**请求参数**:
```json
{
  "user_id": 1,
  "tokens": 1500,
  "conversation_count": 1,
  "duration_ms": 5000
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "更新成功",
  "data": null
}
```

---

## 7. 错误码说明

### 7.1 通用错误码

| 错误码 | 说明 | 处理方式 |
|--------|------|----------|
| 200 | 成功 | - |
| 400 | 请求参数错误 | 检查请求参数 |
| 401 | 未授权 | 重新登录 |
| 403 | 权限不足 | 检查用户权限 |
| 404 | 资源不存在 | 检查资源ID |
| 500 | 服务器错误 | 联系管理员 |

### 7.2 业务错误码

| 错误码 | 说明 |
|--------|------|
| 1001 | 用户名或密码错误 |
| 1002 | Token 无效或过期 |
| 1003 | 配额不足 |
| 1004 | 对话不存在 |
| 1005 | 权限不足 |

---

## 8. 前端调用示例

### 8.1 登录

```typescript
import { authApi } from '@/api/auth';
import { useAuthStore } from '@/store/authStore';

async function login() {
  try {
    const { token, user } = await authApi.login({
      email: 'user@example.com',
      password: 'password'
    });
    
    // 保存到状态管理
    useAuthStore.getState().setAuth(token, user);
    
    // 跳转到首页
    navigate('/');
  } catch (error) {
    message.error(error.message);
  }
}
```

### 8.2 获取对话列表

```typescript
import { conversationApi } from '@/api/conversation';

async function loadConversations() {
  try {
    const conversations = await conversationApi.getConversations(1, 20);
    setConversations(conversations);
  } catch (error) {
    message.error(error.message);
  }
}
```

### 8.3 发送消息（REST + WebSocket）

```typescript
import { conversationApi } from '@/api/conversation';
import { useWebSocket } from '@/hooks/useWebSocket';

async function sendMessage(content: string) {
  try {
    // 1. 调用 REST API 保存消息和检查配额
    await conversationApi.sendMessage(conversationId, content);
    
    // 2. 通过 WebSocket 发送给 Python Agent 执行
    const { sendMessage } = useWebSocket(conversationId);
    sendMessage(content);
  } catch (error) {
    message.error(error.message);
  }
}
```

### 8.4 WebSocket 连接

```typescript
import { useWebSocket } from '@/hooks/useWebSocket';

function ChatWindow({ conversationId }: { conversationId: number }) {
  const { messages, executionSteps, isExecuting, sendMessage } = 
    useWebSocket(conversationId);
  
  return (
    <div>
      {messages.map(msg => (
        <Bubble key={msg.id} content={msg.content} />
      ))}
      
      <ExecutionPanel steps={executionSteps} />
      
      <Sender onSubmit={sendMessage} loading={isExecuting} />
    </div>
  );
}
```

---

## 9. 测试数据

### 9.1 测试账号

| 邮箱 | 密码 | 角色 | 说明 |
|------|------|------|------|
| admin@warphelix.com | admin123 | super_admin | 超级管理员 |
| user1@warphelix.com | user123 | user | 普通用户 |
| user2@warphelix.com | user123 | user | 普通用户 |

### 9.2 测试对话

```json
{
  "id": 1,
  "title": "测试对话",
  "status": "active",
  "messageCount": 2
}
```

### 9.3 测试消息

```json
[
  {
    "id": 1,
    "role": "user",
    "content": "你好"
  },
  {
    "id": 2,
    "role": "assistant",
    "content": "你好！我是 Biomni AI 助手，有什么可以帮助你的吗？"
  }
]
```

---

## 10. 注意事项

### 10.1 Token 管理

- Token 保存在 localStorage
- 每次请求自动添加到 Authorization 头
- 401 错误自动跳转到登录页
- Token 有效期 7 天

### 10.2 CORS 配置

开发环境需要配置后端 CORS：

```java
// Spring Boot
config.addAllowedOrigin("http://localhost:3001");
```

```python
# Python Agent
allow_origins=["http://localhost:3001"]
```

### 10.3 WebSocket 连接

- 确保 Python Agent 服务已启动
- Token 必须有效
- 连接断开会自动重连（5秒后）
- 一个对话只能有一个 WebSocket 连接

### 10.4 配额限制

- 每日对话次数限制
- 每日 Token 使用限制
- 并发任务限制
- 配额不足时会返回错误

---

**文档版本**: v1.0  
**创建日期**: 2025-01-20  
**维护者**: WarpHelix Team
