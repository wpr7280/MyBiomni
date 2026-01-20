# Mock 数据使用说明

## 1. 启用 Mock 模式

### 方式 1：使用 Mock 环境变量文件

```bash
# 启动 Mock 模式
npm run dev:mock

# 或者手动指定
vite --mode mock
```

### 方式 2：修改 .env.development

```env
# .env.development
VITE_USE_MOCK=true
VITE_API_URL=http://localhost:8083
VITE_WS_URL=ws://localhost:8000
```

然后正常启动：
```bash
npm run dev
```

---

## 2. Mock 数据说明

### 2.1 Mock 用户

| 邮箱 | 密码 | 角色 | 用户名 |
|------|------|------|--------|
| admin@biomni.com | admin123 | super_admin | admin |
| user@biomni.com | user123 | user | user |

### 2.2 Mock 对话

系统预置了 3 个对话：
1. **蛋白质结构分析** - 包含 4 条消息
2. **基因测序数据处理** - 包含 2 条消息
3. **单细胞分析流程** - 包含 2 条消息

### 2.3 Mock WebSocket

Mock WebSocket 会模拟真实的 Agent 执行过程：
- ✅ 执行开始通知
- ✅ 3 个执行步骤（分析问题、搜索知识、生成回答）
- ✅ 执行完成通知
- ✅ 自动生成回答内容

---

## 3. Mock 功能

### 3.1 已实现的 Mock 功能

✅ **认证功能**
- 登录（邮箱 + 密码）
- 获取当前用户信息
- 登出

✅ **对话管理**
- 获取对话列表
- 创建新对话
- 获取对话详情
- 删除对话

✅ **消息管理**
- 获取历史消息
- 发送消息

✅ **WebSocket 通信**
- 模拟 Agent 执行
- 实时推送执行步骤
- 返回执行结果

### 3.2 Mock 数据特点

- 🎭 **真实的延迟**：模拟网络请求延迟（300-2000ms）
- 📊 **完整的数据**：包含所有必要字段
- 🔄 **状态管理**：支持增删改查操作
- 💾 **持久化**：数据在内存中保持（刷新页面会重置）

---

## 4. 使用示例

### 4.1 登录测试

```typescript
// 使用 Mock 账号登录
邮箱: user@biomni.com
密码: user123
```

### 4.2 对话测试

1. 登录后自动加载 3 个预置对话
2. 点击对话查看历史消息
3. 点击"新建对话"创建新对话
4. 发送消息测试 WebSocket 通信

### 4.3 Agent 执行测试

发送消息后，会看到：
1. 执行开始提示
2. 3 个执行步骤依次显示
3. 最终回答显示在左侧

---

## 5. 切换到真实 API

### 5.1 修改环境变量

```env
# .env.development
VITE_USE_MOCK=false  # 关闭 Mock
VITE_API_URL=http://localhost:8083
VITE_WS_URL=ws://localhost:8000
```

### 5.2 重启开发服务器

```bash
npm run dev
```

现在会连接真实的后端服务。

---

## 6. Mock 文件说明

### 6.1 文件结构

```
src/mock/
├── data.ts          # Mock 数据定义
├── api.ts           # Mock API 实现
├── websocket.ts     # Mock WebSocket 实现
└── README.md        # 使用说明
```

### 6.2 核心文件

**data.ts**
- Mock 用户数据
- Mock 对话数据
- Mock 消息数据
- 工具函数（delay、generateToken）

**api.ts**
- Mock API 实现
- 模拟网络延迟
- 数据增删改查

**websocket.ts**
- Mock WebSocket 类
- 模拟 Agent 执行
- 自动生成执行步骤

---

## 7. 注意事项

### 7.1 数据持久化

Mock 数据保存在内存中，刷新页面会重置。如果需要持久化，可以：
- 使用 localStorage 保存
- 使用 IndexedDB
- 使用 Mock Service Worker (MSW)

### 7.2 WebSocket 限制

Mock WebSocket 不是真正的 WebSocket，只是模拟了基本行为：
- ✅ 支持 send/close 方法
- ✅ 支持 addEventListener
- ✅ 模拟 readyState
- ❌ 不支持二进制数据
- ❌ 不支持所有 WebSocket 特性

### 7.3 切换提示

在 Mock 模式下，控制台会显示：
```
🎭 Mock 模式已启用
```

---

## 8. 开发建议

### 8.1 开发流程

1. **前端开发阶段**：使用 Mock 模式
   - 快速开发 UI
   - 测试交互逻辑
   - 不依赖后端

2. **联调阶段**：关闭 Mock 模式
   - 连接真实后端
   - 测试接口对接
   - 修复问题

3. **生产环境**：自动关闭 Mock
   - 生产构建不包含 Mock 代码

### 8.2 最佳实践

- ✅ Mock 数据尽量真实
- ✅ 模拟真实的网络延迟
- ✅ 包含错误场景测试
- ✅ 及时更新 Mock 数据

---

**创建时间**: 2025-01-20  
**维护者**: Biomni Team
