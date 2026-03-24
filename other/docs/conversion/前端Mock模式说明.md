# 前端 Mock 模式说明

## 1. 概述

为了方便前端开发和测试，我们添加了完整的 Mock 数据支持。在 Mock 模式下，前端可以独立运行，不需要后端服务。

---

## 2. 启动 Mock 模式

### 方式 1：使用 Mock 命令（推荐）

```bash
cd client/frontend
npm install
npm run dev:mock
```

### 方式 2：修改环境变量

编辑 `.env.development`：
```env
VITE_USE_MOCK=true
```

然后启动：
```bash
npm run dev
```

---

## 3. Mock 数据

### 3.1 测试账号

| 邮箱 | 密码 | 角色 | 说明 |
|------|------|------|------|
| user@warphelix.com | user123 | user | 普通用户 |
| admin@warphelix.com | admin123 | super_admin | 超级管理员 |

### 3.2 预置对话

系统预置了 3 个对话，包含完整的历史消息：

1. **蛋白质结构分析**
   - 4 条消息
   - 包含 Markdown 格式回答
   - 包含代码示例

2. **基因测序数据处理**
   - 2 条消息
   - 质量控制相关内容

3. **单细胞分析流程**
   - 2 条消息
   - scRNA-seq 流程说明

### 3.3 Mock WebSocket

发送消息后会自动模拟 Agent 执行过程：

```
1. 执行开始 (300ms 延迟)
   ↓
2. 步骤 1: 分析用户问题 (500ms)
   ↓
3. 步骤 2: 搜索相关知识 (1200ms)
   - 显示工具调用详情
   - 显示工具输出
   ↓
4. 步骤 3: 生成回答 (2000ms)
   - 显示工具调用详情
   ↓
5. 执行完成
   - 返回 Assistant 消息
```

---

## 4. Mock 功能清单

### 4.1 已实现的功能

✅ **认证功能**
- 登录（邮箱 + 密码验证）
- 获取当前用户信息
- 登出

✅ **对话管理**
- 获取对话列表（3 个预置对话）
- 创建新对话
- 获取对话详情
- 删除对话

✅ **消息管理**
- 获取历史消息
- 发送消息
- 消息自动保存到内存

✅ **WebSocket 通信**
- 模拟连接建立
- 模拟 Agent 执行
- 实时推送执行步骤
- 返回执行结果

### 4.2 Mock 特点

- 🎭 **真实的延迟**：模拟网络请求延迟
- 📊 **完整的数据**：包含所有必要字段
- 🔄 **状态管理**：支持增删改查操作
- 💾 **内存存储**：数据在内存中保持（刷新重置）

---

## 5. 文件结构

```
client/frontend/
├── src/
│   ├── mock/
│   │   ├── data.ts          # Mock 数据定义
│   │   ├── api.ts           # Mock API 实现
│   │   ├── websocket.ts     # Mock WebSocket 实现
│   │   └── README.md        # Mock 使用说明
│   ├── api/
│   │   ├── auth.ts          # 认证 API（支持 Mock）
│   │   └── conversation.ts  # 对话 API（支持 Mock）
│   └── hooks/
│       └── useWebSocket.ts  # WebSocket Hook（支持 Mock）
├── .env.development         # 开发环境变量
├── .env.mock                # Mock 环境变量
└── package.json             # 添加了 dev:mock 命令
```

---

## 6. 切换模式

### 6.1 从 Mock 切换到真实 API

**步骤 1：修改环境变量**

编辑 `.env.development`：
```env
VITE_USE_MOCK=false
VITE_API_URL=http://localhost:8083
VITE_WS_URL=ws://localhost:8000
```

**步骤 2：启动后端服务**

```bash
# Spring Boot
cd admin/backend
./mvnw spring-boot:run

# Python Agent
cd agent
python main.py
```

**步骤 3：重启前端**

```bash
npm run dev
```

### 6.2 从真实 API 切换到 Mock

```bash
# 直接使用 Mock 命令
npm run dev:mock
```

---

## 7. 开发流程建议

### 阶段 1：前端开发（1-2 周）

✅ **使用 Mock 模式**
- 快速开发 UI 组件
- 测试交互逻辑
- 完善用户体验
- 不依赖后端进度

### 阶段 2：后端开发（1-2 周）

✅ **并行开发**
- 前端继续使用 Mock
- 后端开发 API 接口
- 互不阻塞

### 阶段 3：联调测试（3-5 天）

✅ **切换到真实 API**
- 关闭 Mock 模式
- 前后端联调
- 修复接口问题
- 数据格式对齐

### 阶段 4：集成测试（2-3 天）

✅ **完整测试**
- 功能测试
- 性能测试
- 安全测试

---

## 8. Mock 数据维护

### 8.1 添加新的 Mock 对话

编辑 `src/mock/data.ts`：

```typescript
export const mockConversations: Conversation[] = [
  // 添加新对话
  {
    id: 4,
    title: '新的对话主题',
    status: 'active',
    messageCount: 0,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  // ...
];
```

### 8.2 添加新的 Mock 消息

```typescript
export const mockMessages: Record<number, Message[]> = {
  4: [  // 对话 ID
    {
      id: 9,
      conversationId: 4,
      role: 'user',
      content: '你的问题',
      createdAt: new Date().toISOString(),
    },
    // ...
  ],
};
```

### 8.3 自定义 Mock 响应

编辑 `src/mock/websocket.ts` 中的 `generateMockResponse` 方法。

---

## 9. 优势总结

### 9.1 开发效率

✅ **前端独立开发**
- 不需要等待后端接口
- 快速迭代 UI
- 及时发现问题

✅ **并行开发**
- 前后端同时开发
- 提高整体效率

### 9.2 测试便利

✅ **快速测试**
- 无需启动后端服务
- 快速验证功能
- 方便演示

✅ **数据可控**
- Mock 数据可以自定义
- 测试各种场景
- 边界情况测试

### 9.3 团队协作

✅ **降低依赖**
- 前端不依赖后端进度
- 后端不受前端影响
- 提高团队效率

---

## 10. 注意事项

### 10.1 数据持久化

⚠️ Mock 数据保存在内存中，刷新页面会重置

### 10.2 WebSocket 限制

⚠️ Mock WebSocket 只模拟了基本功能，不支持所有 WebSocket 特性

### 10.3 生产环境

⚠️ 生产环境必须关闭 Mock 模式（`VITE_USE_MOCK=false`）

---

**文档版本**: v1.0  
**创建日期**: 2025-01-20  
**维护者**: WarpHelix Team
