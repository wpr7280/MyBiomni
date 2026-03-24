# WarpHelix Agent 应用 API 接口文档

## 1. 接口概述

### 1.1 基本信息
- **Base URL**: `https://api.warphelix.com`
- **协议**: HTTPS
- **数据格式**: JSON
- **字符编码**: UTF-8
- **API 版本**: v1

### 1.2 通用响应格式

#### 成功响应
```json
{
  "code": 200,
  "message": "success",
  "data": {
    // 业务数据
  },
  "timestamp": 1705564800000
}
```

#### 错误响应
```json
{
  "code": 400,
  "message": "参数错误",
  "error": "用户名不能为空",
  "timestamp": 1705564800000
}
```

### 1.3 HTTP 状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 429 | 请求过于频繁 |
| 500 | 服务器内部错误 |

### 1.4 认证方式

使用 JWT Token 进行认证，在请求头中携带：

```
Authorization: Bearer <token>
```

---

## 2. Admin 管理端接口

### 2.1 认证接口

#### 2.1.1 管理员登录

**接口**: `POST /api/admin/auth/login`

**请求参数**:
```json
{
  "username": "admin",
  "password": "password123"
}
```

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expiresIn": 7200,
    "forcePasswordChange": true,
    "admin": {
      "id": 1,
      "username": "admin",
      "email": "admin@warphelix.com",
      "realName": "系统管理员",
      "role": "super_admin",
      "avatar": "https://..."
    }
  }
}
```

**说明**: 
- 如果 `forcePasswordChange` 为 `true`，前端需要强制跳转到修改密码页面
- 首次登录时，只能访问修改密码和登出接口

#### 2.1.2 强制修改密码

**接口**: `POST /api/admin/auth/change-password`

**请求参数**:
```json
{
  "oldPassword": "initial_random_password",
  "newPassword": "new_secure_password"
}
```

**响应**:
```json
{
  "code": 200,
  "message": "密码修改成功，请重新登录"
}
```

**说明**:
- 新密码必须满足强度要求：至少8位，包含大小写字母、数字
- 修改成功后需要重新登录

#### 2.1.3 刷新 Token

**接口**: `POST /api/admin/auth/refresh`

**请求头**:
```
Authorization: Bearer <refreshToken>
```

**响应**:
```json
{
  "code": 200,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expiresIn": 7200
  }
}
```

#### 2.1.4 登出

**接口**: `POST /api/admin/auth/logout`

**响应**:
```json
{
  "code": 200,
  "message": "登出成功"
}
```

### 2.2 用户管理接口

#### 2.2.1 用户列表

**接口**: `GET /api/admin/users`

**查询参数**:
- `page`: 页码 (默认: 1)
- `pageSize`: 每页数量 (默认: 20)
- `keyword`: 搜索关键词 (用户名/邮箱)
- `status`: 状态筛选 (0-禁用, 1-启用)
- `startDate`: 开始日期
- `endDate`: 结束日期

**响应**:
```json
{
  "code": 200,
  "data": {
    "total": 100,
    "page": 1,
    "pageSize": 20,
    "items": [
      {
        "id": 1,
        "username": "user001",
        "email": "user001@example.com",
        "phone": "13800138000",
        "realName": "张三",
        "status": 1,
        "emailVerified": true,
        "phoneVerified": true,
        "registerSource": "email",
        "lastLoginAt": "2025-01-18T10:30:00Z",
        "createdAt": "2025-01-01T00:00:00Z"
      }
    ]
  }
}
```

#### 2.2.2 用户详情

**接口**: `GET /api/admin/users/{id}`

**响应**:
```json
{
  "code": 200,
  "data": {
    "id": 1,
    "username": "user001",
    "email": "user001@example.com",
    "phone": "13800138000",
    "realName": "张三",
    "avatar": "https://...",
    "status": 1,
    "emailVerified": true,
    "phoneVerified": true,
    "registerSource": "email",
    "lastLoginAt": "2025-01-18T10:30:00Z",
    "lastLoginIp": "192.168.1.100",
    "createdAt": "2025-01-01T00:00:00Z",
    "quota": {
      "dailyConversationLimit": 10,
      "monthlyConversationLimit": 300,
      "dailyTokenLimit": 100000,
      "monthlyTokenLimit": 3000000,
      "concurrentTaskLimit": 3
    },
    "usage": {
      "dailyConversationUsed": 5,
      "monthlyConversationUsed": 120,
      "dailyTokenUsed": 45000,
      "monthlyTokenUsed": 1200000
    }
  }
}
```

#### 2.2.3 创建用户

**接口**: `POST /api/admin/users`

**请求参数**:
```json
{
  "username": "user002",
  "password": "password123",
  "email": "user002@example.com",
  "phone": "13800138001",
  "realName": "李四",
  "quotaTemplateId": 1
}
```

**响应**:
```json
{
  "code": 201,
  "message": "创建成功",
  "data": {
    "id": 2,
    "username": "user002",
    "initialPassword": "password123"
  }
}
```

**说明**:
- 用户账号由管理员创建，不支持自助注册
- 创建时可以指定初始密码，或由系统随机生成
- 建议用户首次登录后修改密码

#### 2.2.4 更新用户

**接口**: `PUT /api/admin/users/{id}`

**请求参数**:
```json
{
  "email": "newemail@example.com",
  "phone": "13900139000",
  "realName": "李四",
  "status": 1
}
```

#### 2.2.5 删除用户

**接口**: `DELETE /api/admin/users/{id}`

**响应**:
```json
{
  "code": 200,
  "message": "删除成功"
}
```

#### 2.2.6 重置密码

**接口**: `POST /api/admin/users/{id}/reset-password`

**请求参数**:
```json
{
  "newPassword": "newpassword123"
}
```

### 2.3 配置管理接口

#### 2.3.1 获取系统配置

**接口**: `GET /api/admin/config/system`

**响应**:
```json
{
  "code": 200,
  "data": {
    "dataPath": "./data",
    "useToolRetriever": true,
    "maxConcurrentTasks": 100,
    "sessionTimeout": 30,
    "defaultUserQuota": {
      "dailyConversationLimit": 10,
      "monthlyConversationLimit": 300
    }
  }
}
```

**说明**: 不再包含 `enableRegistration` 配置项，用户账号统一由管理员创建

#### 2.3.2 更新系统配置

**接口**: `PUT /api/admin/config/system`

**请求参数**:
```json
{
  "maxConcurrentTasks": 150,
  "sessionTimeout": 60
}
```

**说明**: 移除了 `enableRegistration` 配置项

#### 2.3.3 获取模型配置

**接口**: `GET /api/admin/config/model`

**响应**:
```json
{
  "code": 200,
  "data": {
    "llm": "claude-sonnet-4-5",
    "source": "Anthropic",
    "temperature": 0.7,
    "timeoutSeconds": 600,
    "baseUrl": null,
    "apiKey": "***" // 脱敏显示
  }
}
```

#### 2.3.4 更新模型配置

**接口**: `PUT /api/admin/config/model`

**请求参数**:
```json
{
  "llm": "gpt-4",
  "source": "OpenAI",
  "temperature": 0.8,
  "timeoutSeconds": 900
}
```

#### 2.3.5 测试模型连接

**接口**: `POST /api/admin/config/model/test`

**请求参数**:
```json
{
  "llm": "gpt-4",
  "source": "OpenAI",
  "baseUrl": "https://api.openai.com/v1",
  "apiKey": "sk-..."
}
```

**响应**:
```json
{
  "code": 200,
  "data": {
    "success": true,
    "message": "连接成功",
    "responseTime": 1250
  }
}
```

#### 2.3.6 获取商用模式配置

**接口**: `GET /api/admin/config/commercial`

**响应**:
```json
{
  "code": 200,
  "data": {
    "enabled": false,
    "description": "商用模式将排除非商用许可的数据集和工具"
  }
}
```

#### 2.3.7 更新商用模式配置

**接口**: `PUT /api/admin/config/commercial`

**请求参数**:
```json
{
  "enabled": true
}
```

### 2.4 配额管理接口

#### 2.4.1 配额模板列表

**接口**: `GET /api/admin/quota/templates`

**响应**:
```json
{
  "code": 200,
  "data": [
    {
      "id": 1,
      "templateName": "免费版",
      "description": "新用户默认配额",
      "dailyConversationLimit": 10,
      "monthlyConversationLimit": 300,
      "dailyTokenLimit": 100000,
      "monthlyTokenLimit": 3000000,
      "concurrentTaskLimit": 3,
      "storageLimitMb": 1024,
      "isDefault": true,
      "status": 1
    }
  ]
}
```

#### 2.4.2 创建配额模板

**接口**: `POST /api/admin/quota/templates`

**请求参数**:
```json
{
  "templateName": "高级版",
  "description": "高级用户配额",
  "dailyConversationLimit": 100,
  "monthlyConversationLimit": 3000,
  "dailyTokenLimit": 1000000,
  "monthlyTokenLimit": 30000000,
  "concurrentTaskLimit": 10,
  "storageLimitMb": 10240
}
```

#### 2.4.3 设置用户配额

**接口**: `PUT /api/admin/users/{id}/quota`

**请求参数**:
```json
{
  "templateId": 2,
  "effectiveFrom": "2025-01-18T00:00:00Z",
  "effectiveUntil": "2025-12-31T23:59:59Z"
}
```

#### 2.4.4 查看配额使用情况

**接口**: `GET /api/admin/users/{id}/quota/usage`

**查询参数**:
- `startDate`: 开始日期
- `endDate`: 结束日期

**响应**:
```json
{
  "code": 200,
  "data": {
    "userId": 1,
    "quota": {
      "dailyConversationLimit": 10,
      "monthlyConversationLimit": 300,
      "dailyTokenLimit": 100000,
      "monthlyTokenLimit": 3000000
    },
    "usage": {
      "today": {
        "conversationUsed": 5,
        "tokenUsed": 45000
      },
      "thisMonth": {
        "conversationUsed": 120,
        "tokenUsed": 1200000
      }
    },
    "history": [
      {
        "date": "2025-01-18",
        "conversationUsed": 5,
        "tokenUsed": 45000
      }
    ]
  }
}
```

#### 2.4.5 重置配额

**接口**: `POST /api/admin/quota/reset`

**请求参数**:
```json
{
  "userIds": [1, 2, 3],
  "resetType": "daily" // daily, monthly
}
```

### 2.5 对话管理接口

#### 2.5.1 对话列表

**接口**: `GET /api/admin/conversations`

**查询参数**:
- `page`: 页码
- `pageSize`: 每页数量
- `userId`: 用户ID筛选
- `status`: 状态筛选 (active, completed, failed, cancelled)
- `keyword`: 关键词搜索
- `startDate`: 开始日期
- `endDate`: 结束日期

**响应**:
```json
{
  "code": 200,
  "data": {
    "total": 500,
    "page": 1,
    "pageSize": 20,
    "items": [
      {
        "id": 1,
        "userId": 1,
        "username": "user001",
        "title": "分析单细胞数据",
        "status": "completed",
        "modelName": "claude-sonnet-4-5",
        "messageCount": 10,
        "totalTokens": 25000,
        "totalDurationMs": 45000,
        "createdAt": "2025-01-18T10:00:00Z",
        "lastMessageAt": "2025-01-18T10:15:00Z"
      }
    ]
  }
}
```

#### 2.5.2 对话详情

**接口**: `GET /api/admin/conversations/{id}`

**响应**:
```json
{
  "code": 200,
  "data": {
    "id": 1,
    "userId": 1,
    "username": "user001",
    "title": "分析单细胞数据",
    "status": "completed",
    "modelName": "claude-sonnet-4-5",
    "modelSource": "Anthropic",
    "messageCount": 10,
    "totalTokens": 25000,
    "totalDurationMs": 45000,
    "createdAt": "2025-01-18T10:00:00Z",
    "messages": [
      {
        "id": 1,
        "role": "user",
        "content": "请帮我分析这个单细胞数据",
        "contentType": "text",
        "tokens": 15,
        "createdAt": "2025-01-18T10:00:00Z"
      },
      {
        "id": 2,
        "role": "assistant",
        "content": "好的，我会帮你分析...",
        "contentType": "markdown",
        "tokens": 150,
        "createdAt": "2025-01-18T10:00:30Z"
      }
    ],
    "executionSteps": [
      {
        "id": 1,
        "stepOrder": 1,
        "stepType": "tool_call",
        "stepName": "数据加载",
        "toolName": "load_scanpy_data",
        "toolInput": "{\"path\": \"data.h5ad\"}",
        "toolOutput": "Successfully loaded 5000 cells",
        "status": "success",
        "durationMs": 2000,
        "startedAt": "2025-01-18T10:00:30Z",
        "completedAt": "2025-01-18T10:00:32Z"
      }
    ]
  }
}
```

#### 2.5.3 对话统计

**接口**: `GET /api/admin/conversations/stats`

**查询参数**:
- `startDate`: 开始日期
- `endDate`: 结束日期

**响应**:
```json
{
  "code": 200,
  "data": {
    "totalConversations": 1000,
    "activeConversations": 50,
    "completedConversations": 900,
    "failedConversations": 50,
    "totalTokens": 50000000,
    "avgDurationMs": 35000,
    "dailyStats": [
      {
        "date": "2025-01-18",
        "count": 100,
        "tokens": 2500000
      }
    ]
  }
}
```

#### 2.5.4 导出对话

**接口**: `POST /api/admin/conversations/export`

**请求参数**:
```json
{
  "conversationIds": [1, 2, 3],
  "format": "json" // json, csv, pdf
}
```

**响应**:
```json
{
  "code": 200,
  "data": {
    "downloadUrl": "https://files.warphelix.com/exports/conversations_20250118.zip",
    "expiresAt": "2025-01-19T00:00:00Z"
  }
}
```

### 2.6 Know-How 文档管理接口

#### 2.6.1 文档列表

**接口**: `GET /api/admin/knowhow`

**查询参数**:
- `page`: 页码
- `pageSize`: 每页数量
- `keyword`: 搜索关键词
- `category`: 分类筛选
- `tags`: 标签筛选 (逗号分隔)
- `status`: 状态 (0-禁用, 1-启用, 2-草稿)
- `commercialUse`: 商用许可 (0-不允许, 1-允许)

**响应**:
```json
{
  "code": 200,
  "data": {
    "total": 50,
    "items": [
      {
        "id": 1,
        "docId": "single_cell_annotation",
        "title": "Single Cell RNA-seq Cell Type Annotation",
        "shortDescription": "Best practices for annotating cell types...",
        "category": "数据分析",
        "tags": "single-cell,annotation,RNA-seq",
        "authors": "Luecken, M.D. et al.",
        "license": "CC BY 4.0",
        "commercialUse": 1,
        "status": 1,
        "priority": 10,
        "viewCount": 1500,
        "usageCount": 300,
        "createdAt": "2025-01-01T00:00:00Z",
        "updatedAt": "2025-01-15T00:00:00Z"
      }
    ]
  }
}
```

#### 2.6.2 文档详情

**接口**: `GET /api/admin/knowhow/{id}`

**响应**:
```json
{
  "code": 200,
  "data": {
    "id": 1,
    "docId": "single_cell_annotation",
    "title": "Single Cell RNA-seq Cell Type Annotation",
    "shortDescription": "Best practices for annotating cell types...",
    "content": "# Single Cell RNA-seq Cell Type Annotation\n\n...",
    "contentWithoutMetadata": "Cell type annotation is...",
    "category": "数据分析",
    "tags": "single-cell,annotation,RNA-seq",
    "authors": "Luecken, M.D. et al.",
    "affiliations": "Helmholtz Munich, Wellcome Sanger Institute",
    "version": "1.0",
    "lastUpdated": "2025-01-15",
    "license": "CC BY 4.0",
    "commercialUse": 1,
    "sourceUrl": "https://www.sc-best-practices.org/...",
    "citation": "Luecken, M.D., Theis, F.J. et al. (2023)...",
    "status": 1,
    "priority": 10,
    "viewCount": 1500,
    "usageCount": 300,
    "filePath": "/know_how/single_cell_annotation.md",
    "createdAt": "2025-01-01T00:00:00Z",
    "updatedAt": "2025-01-15T00:00:00Z"
  }
}
```

**说明**:
- `category`: 单个分类字符串
- `tags`: 逗号分隔的标签字符串

#### 2.6.3 创建文档

**接口**: `POST /api/admin/knowhow`

**请求参数**:
```json
{
  "docId": "crispr_screen_design",
  "title": "CRISPR Screen Design Guide",
  "shortDescription": "Best practices for designing CRISPR screens",
  "content": "# CRISPR Screen Design Guide\n\n...",
  "category": "实验技术",
  "tags": "crispr,screen,design",
  "authors": "John Doe, Jane Smith",
  "affiliations": "Stanford University",
  "version": "1.0",
  "license": "CC BY 4.0",
  "commercialUse": 1,
  "sourceUrl": "https://...",
  "status": 1,
  "priority": 5
}
```

**说明**:
- `category`: 从预定义分类中选择
- `tags`: 逗号分隔的标签字符串

#### 2.6.4 更新文档

**接口**: `PUT /api/admin/knowhow/{id}`

**请求参数**: 同创建文档

#### 2.6.5 删除文档

**接口**: `DELETE /api/admin/knowhow/{id}`

#### 2.6.6 修改文档状态

**接口**: `PUT /api/admin/knowhow/{id}/status`

**请求参数**:
```json
{
  "status": 1 // 0-禁用, 1-启用, 2-草稿
}
```

---

## 3. Client 用户端接口

### 3.1 认证接口

#### 3.1.1 用户登录

**接口**: `POST /api/client/auth/login`

**请求参数**:
```json
{
  "username": "user001",
  "password": "password123"
}
```

**响应**:
```json
{
  "code": 200,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expiresIn": 7200,
    "user": {
      "id": 1,
      "username": "user001",
      "email": "user001@example.com",
      "realName": "张三",
      "avatar": "https://..."
    }
  }
}
```

**说明**: 
- 用户账号由管理员在后台创建
- 不提供自助注册功能

#### 3.1.2 第三方登录 (可选)

**接口**: `POST /api/client/auth/oauth/{provider}`

**路径参数**:
- `provider`: google, github

**请求参数**:
```json
{
  "code": "oauth_authorization_code"
}
```

### 3.2 个人中心接口

#### 3.2.1 获取个人信息

**接口**: `GET /api/client/user/profile`

**响应**:
```json
{
  "code": 200,
  "data": {
    "id": 1,
    "username": "user001",
    "email": "user001@example.com",
    "phone": "13800138000",
    "realName": "张三",
    "avatar": "https://...",
    "emailVerified": true,
    "phoneVerified": true,
    "registerSource": "email",
    "createdAt": "2025-01-01T00:00:00Z"
  }
}
```

#### 3.2.2 更新个人信息

**接口**: `PUT /api/client/user/profile`

**请求参数**:
```json
{
  "realName": "张三",
  "avatar": "https://..."
}
```

#### 3.2.3 修改密码

**接口**: `PUT /api/client/user/password`

**请求参数**:
```json
{
  "oldPassword": "oldpassword123",
  "newPassword": "newpassword123"
}
```

#### 3.2.4 查看配额

**接口**: `GET /api/client/user/quota`

**响应**:
```json
{
  "code": 200,
  "data": {
    "quota": {
      "dailyConversationLimit": 10,
      "monthlyConversationLimit": 300,
      "dailyTokenLimit": 100000,
      "monthlyTokenLimit": 3000000,
      "concurrentTaskLimit": 3,
      "storageLimitMb": 1024
    },
    "usage": {
      "today": {
        "conversationUsed": 5,
        "conversationRemaining": 5,
        "tokenUsed": 45000,
        "tokenRemaining": 55000
      },
      "thisMonth": {
        "conversationUsed": 120,
        "conversationRemaining": 180,
        "tokenUsed": 1200000,
        "tokenRemaining": 1800000
      },
      "storageUsedMb": 256
    }
  }
}
```

### 3.3 对话管理接口

#### 3.3.1 对话列表

**接口**: `GET /api/client/conversations`

**查询参数**:
- `page`: 页码
- `pageSize`: 每页数量
- `keyword`: 搜索关键词
- `status`: 状态筛选
- `isFavorite`: 是否收藏

**响应**:
```json
{
  "code": 200,
  "data": {
    "total": 50,
    "items": [
      {
        "id": 1,
        "title": "分析单细胞数据",
        "status": "completed",
        "messageCount": 10,
        "isFavorite": false,
        "isPinned": false,
        "createdAt": "2025-01-18T10:00:00Z",
        "lastMessageAt": "2025-01-18T10:15:00Z"
      }
    ]
  }
}
```

#### 3.3.2 创建对话

**接口**: `POST /api/client/conversations`

**请求参数**:
```json
{
  "title": "新对话",
  "initialMessage": "请帮我分析这个数据"
}
```

**响应**:
```json
{
  "code": 201,
  "data": {
    "id": 2,
    "title": "新对话",
    "status": "active"
  }
}
```

#### 3.3.3 对话详情

**接口**: `GET /api/client/conversations/{id}`

**响应**:
```json
{
  "code": 200,
  "data": {
    "id": 1,
    "title": "分析单细胞数据",
    "status": "completed",
    "modelName": "claude-sonnet-4-5",
    "messageCount": 10,
    "totalTokens": 25000,
    "isFavorite": false,
    "isPinned": false,
    "createdAt": "2025-01-18T10:00:00Z",
    "messages": [
      {
        "id": 1,
        "role": "user",
        "content": "请帮我分析这个单细胞数据",
        "contentType": "text",
        "createdAt": "2025-01-18T10:00:00Z"
      }
    ]
  }
}
```

#### 3.3.4 发送消息

**接口**: `POST /api/client/conversations/{id}/messages`

**请求参数**:
```json
{
  "content": "请继续分析",
  "attachments": [
    {
      "type": "file",
      "url": "https://..."
    }
  ]
}
```

**响应**:
```json
{
  "code": 201,
  "data": {
    "messageId": 11,
    "taskId": "task_123456"
  }
}
```

#### 3.3.5 更新对话

**接口**: `PUT /api/client/conversations/{id}`

**请求参数**:
```json
{
  "title": "新标题"
}
```

#### 3.3.6 删除对话

**接口**: `DELETE /api/client/conversations/{id}`

#### 3.3.7 收藏对话

**接口**: `PUT /api/client/conversations/{id}/favorite`

**请求参数**:
```json
{
  "isFavorite": true
}
```

#### 3.3.8 获取执行状态

**接口**: `GET /api/client/conversations/{id}/execution`

**响应**:
```json
{
  "code": 200,
  "data": {
    "status": "running",
    "currentStep": "数据分析",
    "progress": 60,
    "startedAt": "2025-01-18T10:00:00Z"
  }
}
```

#### 3.3.9 获取执行步骤

**接口**: `GET /api/client/conversations/{id}/steps`

**响应**:
```json
{
  "code": 200,
  "data": [
    {
      "id": 1,
      "stepOrder": 1,
      "stepType": "tool_call",
      "stepName": "数据加载",
      "toolName": "load_scanpy_data",
      "status": "success",
      "durationMs": 2000,
      "startedAt": "2025-01-18T10:00:30Z",
      "completedAt": "2025-01-18T10:00:32Z"
    }
  ]
}
```

#### 3.3.10 取消执行

**接口**: `POST /api/client/conversations/{id}/cancel`

**响应**:
```json
{
  "code": 200,
  "message": "任务已取消"
}
```

#### 3.3.11 导出结果

**接口**: `POST /api/client/conversations/{id}/export`

**请求参数**:
```json
{
  "format": "pdf" // pdf, markdown, json
}
```

**响应**:
```json
{
  "code": 200,
  "data": {
    "downloadUrl": "https://files.warphelix.com/exports/conversation_1.pdf",
    "expiresAt": "2025-01-19T00:00:00Z"
  }
}
```

#### 3.3.12 提交反馈

**接口**: `POST /api/client/conversations/{id}/feedback`

**请求参数**:
```json
{
  "rating": 5,
  "comment": "非常有帮助"
}
```

### 3.4 Know-How 浏览接口

#### 3.4.1 文档列表

**接口**: `GET /api/client/knowhow`

**查询参数**:
- `page`: 页码
- `pageSize`: 每页数量
- `keyword`: 搜索关键词
- `category`: 分类筛选
- `tags`: 标签筛选 (逗号分隔)

**响应**:
```json
{
  "code": 200,
  "data": {
    "total": 50,
    "items": [
      {
        "id": 1,
        "docId": "single_cell_annotation",
        "title": "Single Cell RNA-seq Cell Type Annotation",
        "shortDescription": "Best practices for annotating cell types...",
        "category": "数据分析",
        "tags": "single-cell,annotation",
        "authors": "Luecken, M.D. et al.",
        "viewCount": 1500
      }
    ]
  }
}
```

#### 3.4.2 文档详情

**接口**: `GET /api/client/knowhow/{id}`

**响应**: 同管理端文档详情接口

---

## 4. WebSocket 接口

### 4.1 对话实时通信

**连接**: `wss://api.warphelix.com/ws/conversations/{conversationId}`

**认证**: 连接时携带 token
```
wss://api.warphelix.com/ws/conversations/1?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 4.2 消息类型

#### 4.2.1 新消息

```json
{
  "type": "message",
  "data": {
    "id": 2,
    "role": "assistant",
    "content": "正在分析数据...",
    "contentType": "text",
    "createdAt": "2025-01-18T10:00:30Z"
  }
}
```

#### 4.2.2 执行步骤更新

```json
{
  "type": "execution_step",
  "data": {
    "id": 1,
    "stepOrder": 1,
    "stepType": "tool_call",
    "stepName": "数据加载",
    "toolName": "load_scanpy_data",
    "status": "running",
    "startedAt": "2025-01-18T10:00:30Z"
  }
}
```

#### 4.2.3 执行完成

```json
{
  "type": "execution_complete",
  "data": {
    "status": "success",
    "totalDurationMs": 45000,
    "totalTokens": 25000
  }
}
```

#### 4.2.4 错误通知

```json
{
  "type": "error",
  "data": {
    "code": "EXECUTION_ERROR",
    "message": "执行失败: 数据文件不存在"
  }
}
```

---

## 5. 错误码说明

| 错误码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 / Token 无效 |
| 403 | 禁止访问 / 权限不足 |
| 404 | 资源不存在 |
| 409 | 资源冲突 (如用户名已存在) |
| 429 | 请求过于频繁 / 配额不足 |
| 500 | 服务器内部错误 |
| 503 | 服务暂时不可用 |

### 业务错误码

| 错误码 | 说明 |
|--------|------|
| 10001 | 用户名或密码错误 |
| 10002 | 用户不存在 |
| 10003 | 用户已被禁用 |
| 10004 | 用户名已存在 |
| 10005 | 邮箱已被使用 |
| 20001 | 配额不足 |
| 20002 | 超过并发限制 |
| 20003 | 存储空间不足 |
| 30001 | 对话不存在 |
| 30002 | 对话已结束 |
| 30003 | 任务执行失败 |
| 40001 | 文档不存在 |
| 40002 | 文档已被禁用 |

---

## 6. 限流规则

### 6.1 接口限流

| 接口类型 | 限制 |
|---------|------|
| 登录接口 | 5次/分钟 |
| 发送验证码 | 1次/分钟, 10次/小时 |
| 创建对话 | 根据配额限制 |
| 发送消息 | 10次/分钟 |
| 文件上传 | 5次/分钟 |
| 其他接口 | 100次/分钟 |

### 6.2 限流响应

```json
{
  "code": 429,
  "message": "请求过于频繁，请稍后再试",
  "data": {
    "retryAfter": 60
  }
}
```

---

## 7. 分页规范

### 7.1 请求参数
- `page`: 页码，从 1 开始
- `pageSize`: 每页数量，默认 20，最大 100

### 7.2 响应格式
```json
{
  "code": 200,
  "data": {
    "total": 100,
    "page": 1,
    "pageSize": 20,
    "totalPages": 5,
    "items": []
  }
}
```

---

## 8. 文件上传

### 8.1 上传接口

**接口**: `POST /api/client/files/upload`

**请求**: `multipart/form-data`
- `file`: 文件
- `folder`: 文件夹 (可选)

**响应**:
```json
{
  "code": 200,
  "data": {
    "fileId": "file_123456",
    "fileName": "data.csv",
    "fileSize": 1024000,
    "fileUrl": "https://files.warphelix.com/uploads/file_123456.csv",
    "uploadedAt": "2025-01-18T10:00:00Z"
  }
}
```

### 8.2 文件限制
- 单文件大小: 最大 100MB
- 支持格式: `.csv`, `.xlsx`, `.h5ad`, `.pdf`, `.png`, `.jpg`
- 总存储空间: 根据用户配额

---

**文档版本**: v1.0  
**最后更新**: 2025-01-18  
**维护者**: WarpHelix Team
