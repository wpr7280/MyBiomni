# 配额功能实现状态

## ✅ 已完成

### 1. 数据库设计
- ✅ 创建了 `user_quotas` 表（独立表，避免影响 admin 表缓存）
- ✅ SQL 脚本：`agent/create_quota_table.sql`
- ✅ 字段：user_id, total_token_limit, total_token_used

### 2. Python 后端实现

#### 2.1 数据模型
- ✅ `agent/models/models.py` - 添加了 `UserQuota` 模型

#### 2.2 配额检查
- ✅ `agent/api/websocket.py` - WebSocket 接收消息时检查配额
- ✅ 配额不足时返回 `quota_exceeded` 消息
- ✅ 自动创建默认配额（100万 Token）

#### 2.3 Token 统计
- ✅ `agent/services/callback.py` - 累计 input_tokens 和 output_tokens
- ✅ `agent/services/mock_agent.py` - Mock Agent 返回 usage 信息
- ✅ `agent/services/agent_service.py` - 传递 usage 到 callback

#### 2.4 配额更新
- ✅ `agent/services/callback.py` - 执行完成后更新 `user_quotas` 表
- ✅ 更新 `total_token_used` 字段

### 3. 前端修复
- ✅ 修复了附件上传的 TypeScript 类型错误
- ✅ 修复了示例问题点击事件（添加类型断言）

---

## 🔄 待完成

### 1. 数据库初始化
```bash
# 需要执行 SQL 创建表
mysql -u root -p biomni < agent/create_quota_table.sql
```

### 2. 前端配额显示

#### 2.1 获取配额信息
需要在前端调用 API 获取用户配额：

```typescript
// client/frontend/src/api/auth.ts
export interface QuotaInfo {
  totalTokenLimit: number;
  totalTokenUsed: number;
  remaining: number;
}

export const authApi = {
  async getQuota(): Promise<QuotaInfo> {
    const response = await apiClient.get('/api/auth/me');
    const user = response.data.data;
    return {
      totalTokenLimit: user.totalTokenLimit || 1000000,
      totalTokenUsed: user.totalTokenUsed || 0,
      remaining: (user.totalTokenLimit || 1000000) - (user.totalTokenUsed || 0)
    };
  }
};
```

#### 2.2 显示配额
更新 `client/frontend/src/components/ChatWindow.tsx`：

```typescript
// 当前显示（Mock 数据）
<Tag color="processing">📊 Weekly: 45/50</Tag>
<Tag color="success">📅 Tokens: 2025-06-02</Tag>

// 改为真实配额
<Tag color={quota.remaining > 100000 ? 'success' : 'warning'}>
  📊 Token: {quota.totalTokenUsed.toLocaleString()} / {quota.totalTokenLimit.toLocaleString()}
</Tag>
```

#### 2.3 处理配额不足
在 `useWebSocket.ts` 中处理 `quota_exceeded` 消息：

```typescript
if (data.type === 'quota_exceeded') {
  message.error('Token 配额已用完，请联系管理员');
  setIsExecuting(false);
}
```

### 3. Spring Boot 后端（可选）

#### 3.1 用户信息 API
更新 `/api/auth/me` 返回配额信息：

```java
// AdminUserController.java
@GetMapping("/me")
public BaseResult<UserVO> getCurrentUser(@AuthenticationPrincipal AdminVO currentUser) {
    // 查询 user_quotas 表
    UserQuota quota = userQuotaMapper.selectByUserId(currentUser.getId());
    
    UserVO user = new UserVO();
    user.setId(currentUser.getId());
    user.setEmail(currentUser.getEmail());
    user.setTotalTokenLimit(quota != null ? quota.getTotalTokenLimit() : 1000000);
    user.setTotalTokenUsed(quota != null ? quota.getTotalTokenUsed() : 0);
    
    return BaseResult.success(user);
}
```

#### 3.2 配额管理 API（管理员）
```java
// QuotaController.java
@PostMapping("/api/admin/quota/update")
public BaseResult<Void> updateQuota(@RequestBody UpdateQuotaRequest request) {
    // 更新用户配额
    userQuotaService.updateQuota(request.getUserId(), request.getTotalTokenLimit());
    return BaseResult.success(null);
}

@PostMapping("/api/admin/quota/reset")
public BaseResult<Void> resetQuota(@RequestBody ResetQuotaRequest request) {
    // 重置已使用量
    userQuotaService.resetUsage(request.getUserId());
    return BaseResult.success(null);
}
```

### 4. 管理后台（可选）

#### 4.1 用户列表显示配额
在 `admin/frontend/src/views/system/users/index.vue` 中添加列：

```vue
<el-table-column label="Token 配额" width="120">
  <template #default="{ row }">
    {{ row.totalTokenLimit?.toLocaleString() }}
  </template>
</el-table-column>

<el-table-column label="已使用" width="120">
  <template #default="{ row }">
    {{ row.totalTokenUsed?.toLocaleString() }}
  </template>
</el-table-column>

<el-table-column label="使用率" width="100">
  <template #default="{ row }">
    <el-tag :type="getUsageType(row)">
      {{ ((row.totalTokenUsed / row.totalTokenLimit) * 100).toFixed(1) }}%
    </el-tag>
  </template>
</el-table-column>
```

#### 4.2 编辑配额
在用户编辑对话框中添加配额字段：

```vue
<el-form-item label="Token 配额">
  <el-input-number v-model="form.totalTokenLimit" :min="0" :step="100000" />
</el-form-item>

<el-form-item>
  <el-button @click="resetQuota">重置使用量</el-button>
</el-form-item>
```

---

## 📊 实现进度

| 模块 | 状态 | 完成度 |
|------|------|--------|
| 数据库设计 | ✅ 完成 | 100% |
| Python 配额检查 | ✅ 完成 | 100% |
| Python Token 统计 | ✅ 完成 | 100% |
| Python 配额更新 | ✅ 完成 | 100% |
| 前端 TypeScript 修复 | ✅ 完成 | 100% |
| 数据库初始化 | ⏳ 待执行 | 0% |
| 前端配额显示 | ⏳ 待实现 | 0% |
| Spring Boot API | ⏳ 可选 | 0% |
| 管理后台 | ⏳ 可选 | 0% |

**总体进度**: 60% （核心功能已完成）

---

## 🚀 快速测试

### 1. 创建配额表
```bash
cd admin/backend/data
mysql -u root -p biomni < ../../create_quota_table.sql
```

### 2. 启动 Python Agent
```bash
cd agent
export USE_MOCK_AGENT=true
python main.py
```

### 3. 启动前端
```bash
cd client/frontend
npm run dev:mock
```

### 4. 测试配额
1. 登录系统
2. 发送多条消息
3. 观察 Token 累计（Mock Agent 每次约 690 tokens）
4. 当达到配额限制时，会收到 `quota_exceeded` 错误

---

## 📝 注意事项

### Token 统计准确性
- ✅ Mock Agent：返回模拟的 token 数量
- ⚠️ 真实 A1 Agent：需要从 LLM response 中提取 `usage_metadata`
- 💡 建议：在 `biomni/agent/a1.py` 中添加 token 统计

### 配额表独立性
- ✅ 使用独立的 `user_quotas` 表
- ✅ 不影响 `admin` 表的缓存
- ✅ 便于后续扩展（每日限制、并发限制等）

### 性能优化
- 当前实现：每次执行后更新配额（同步）
- 可选优化：使用 Redis 缓存配额，定期同步到数据库

---

**文档版本**: v1.0  
**创建时间**: 2025-01-20  
**维护者**: Biomni Team  
**状态**: 核心功能已完成，待前端集成
