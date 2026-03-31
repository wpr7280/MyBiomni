# 快速启动指南

## 🚀 5 分钟快速体验

### 1. 安装依赖

```bash
cd client/frontend
npm install
```

### 2. 启动 Mock 模式

```bash
npm run dev:mock
```

### 3. 访问应用

打开浏览器访问：http://localhost:3001

### 4. 登录测试

使用以下账号登录：

**普通用户**
- 邮箱: `user@warphelix.com`
- 密码: `user123`

**管理员**
- 邮箱: `admin@warphelix.com`
- 密码: `admin123`

### 5. 体验功能

✅ **对话列表**
- 查看 3 个预置对话
- 点击对话查看历史消息

✅ **创建对话**
- 点击"新建对话"按钮
- 输入对话标题

✅ **发送消息**
- 在输入框输入消息
- 点击发送或按 Enter
- 观察右侧 Agent 执行过程

✅ **删除对话**
- 右键点击对话
- 选择"删除"

---

## 📋 Mock 数据说明

### 预置对话

1. **蛋白质结构分析** - 包含 4 条消息
2. **基因测序数据处理** - 包含 2 条消息
3. **单细胞分析流程** - 包含 2 条消息

### Mock WebSocket

发送消息后会自动模拟 Agent 执行：
1. 执行开始（300ms 延迟）
2. 分析问题（500ms）
3. 搜索知识库（1200ms）
4. 生成回答（2000ms）
5. 执行完成

---

## 🔧 切换到真实 API

### 1. 修改环境变量

编辑 `.env.development`：

```env
VITE_USE_MOCK=false
VITE_API_URL=http://localhost:8083
VITE_WS_URL=ws://localhost:8000
```

### 2. 启动后端服务

```bash
# 启动 Spring Boot
cd admin/backend
./mvnw spring-boot:run

# 启动 Python Agent
cd agent
python main.py
```

### 3. 重启前端

```bash
npm run dev
```

---

## 🎯 开发建议

### 前端开发阶段

✅ 使用 Mock 模式
- 快速开发 UI
- 测试交互逻辑
- 不依赖后端

### 联调阶段

✅ 切换到真实 API
- 测试接口对接
- 验证数据格式
- 修复问题

### 生产环境

✅ 自动使用真实 API
- Mock 代码不会打包到生产版本

---

## 📝 常见问题

### Q1: Mock 模式下数据会保存吗？

不会。Mock 数据保存在内存中，刷新页面会重置。

### Q2: 如何添加更多 Mock 数据？

编辑 `src/mock/data.ts` 文件，添加更多对话和消息。

### Q3: Mock WebSocket 支持所有功能吗？

支持基本功能，但不是真正的 WebSocket。如果需要测试复杂场景，建议使用真实 API。

### Q4: 如何判断当前是否在 Mock 模式？

打开浏览器控制台，如果看到 `🎭 Mock 模式已启用`，说明在 Mock 模式。

---

**创建时间**: 2025-01-20  
**维护者**: WarpHelix Team
