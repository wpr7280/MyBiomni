# 配额功能快速参考

## 🚀 5分钟快速启动

```bash
# 1. 创建配额表
cd admin/backend/data
mysql -u root -p biomni < ../../create_quota_table.sql

# 2. 启动 Python Agent
cd agent
export USE_MOCK_AGENT=true
python main.py

# 3. 启动前端
cd client/frontend
npm run dev:mock

# 4. 访问
open http://localhost:3001
```

---

## 📊 关键数据

| 项目 | 值 |
|------|-----|
| 默认配额 | 1,000,000 tokens |
| Mock Agent 单次消耗 | ~1,055 tokens |
| 可用次数 | ~948 次 |
| 配额表名 | `user_quotas` |
| 外键关联 | `admin.id` |

---

## 🔍 快速查询

### 查看所有用户配额
```sql
SELECT 
    u.id,
    u.email,
    q.total_token_limit,
    q.total_token_used,
    (q.total_token_limit - q.total_token_used) as remaining,
    ROUND((q.total_token_used / q.total_token_limit) * 100, 2) as usage_percent
FROM admin u
LEFT JOIN user_quotas q ON u.id = q.user_id;
```

### 查看配额不足的用户
```sql
SELECT 
    u.email,
    q.total_token_used,
    q.total_token_limit
FROM admin u
JOIN user_quotas q ON u.id = q.user_id
WHERE q.total_token_used >= q.total_token_limit;
```

### 重置用户配额
```sql
UPDATE user_quotas 
SET total_token_used = 0, updated_at = NOW()
WHERE user_id = 1;
```

### 增加用户配额
```sql
UPDATE user_quotas 
SET total_token_limit = 2000000, updated_at = NOW()
WHERE user_id = 1;
```

---

## 📁 关键文件位置

### Python 后端
```
agent/
├── api/websocket.py          # 配额检查
├── services/callback.py      # Token 统计 + 配额更新
├── services/agent_service.py # 传递 usage
├── services/mock_agent.py    # Mock token usage
├── models/models.py          # UserQuota 模型
└── create_quota_table.sql    # 数据库脚本
```

### 前端（待实现）
```
client/frontend/src/
├── api/quota.ts              # 配额 API（待创建）
├── components/ChatWindow.tsx # 显示配额（待修改）
└── hooks/useWebSocket.ts     # 处理配额不足（待修改）
```

### 文档
```
├── QUOTA_IMPLEMENTATION_STATUS.md  # 实现状态
├── NEXT_STEPS.md                   # 下一步工作
├── SESSION_CHANGES.md              # 本次修改
├── COMPLETION_SUMMARY.md           # 完成总结
├── QUOTA_FLOW_DIAGRAM.md           # 流程图
└── QUICK_REFERENCE.md              # 本文件
```

---

## 🐛 常见问题

### Q1: 配额表创建失败
```bash
# 检查数据库连接
mysql -u root -p biomni -e "SHOW TABLES;"

# 检查 admin 表是否存在
mysql -u root -p biomni -e "DESC admin;"

# 手动创建（如果脚本失败）
mysql -u root -p biomni < agent/create_quota_table.sql
```

### Q2: Token 统计为 0
```python
# 检查 Mock Agent 是否返回 usage
# agent/services/mock_agent.py
yield {
    'output': "...",
    'usage': {'input_tokens': 50, 'output_tokens': 30}  # 必须有这个
}
```

### Q3: 配额不更新
```python
# 检查 callback.py 中的更新逻辑
def get_result(self):
    # 确保这段代码被执行
    quota = self.db.query(UserQuota).filter(UserQuota.user_id == self.user_id).first()
    if quota:
        quota.total_token_used += (self.total_input_tokens + self.total_output_tokens)
        self.db.commit()
```

### Q4: 前端不显示配额
```typescript
// 1. 检查 API 是否返回配额信息
// 2. 检查 ChatWindow 是否调用 loadQuota()
// 3. 检查浏览器控制台错误
```

---

## 🧪 测试命令

### 测试配额检查
```bash
# 1. 设置用户配额为 1000（测试用）
mysql -u root -p biomni -e "UPDATE user_quotas SET total_token_limit = 1000 WHERE user_id = 1;"

# 2. 发送消息（会失败，因为 1055 > 1000）

# 3. 恢复配额
mysql -u root -p biomni -e "UPDATE user_quotas SET total_token_limit = 1000000 WHERE user_id = 1;"
```

### 测试 Token 统计
```bash
# 1. 重置配额
mysql -u root -p biomni -e "UPDATE user_quotas SET total_token_used = 0 WHERE user_id = 1;"

# 2. 发送 1 条消息

# 3. 查看使用量（应该约 1055）
mysql -u root -p biomni -e "SELECT total_token_used FROM user_quotas WHERE user_id = 1;"
```

---

## 📊 监控指标

### 配额使用率
```sql
SELECT 
    AVG((total_token_used / total_token_limit) * 100) as avg_usage_percent,
    MAX((total_token_used / total_token_limit) * 100) as max_usage_percent,
    COUNT(CASE WHEN total_token_used >= total_token_limit THEN 1 END) as users_exceeded
FROM user_quotas;
```

### Top 10 用户（按使用量）
```sql
SELECT 
    u.email,
    q.total_token_used,
    q.total_token_limit,
    ROUND((q.total_token_used / q.total_token_limit) * 100, 2) as usage_percent
FROM admin u
JOIN user_quotas q ON u.id = q.user_id
ORDER BY q.total_token_used DESC
LIMIT 10;
```

### 每日 Token 消耗
```sql
SELECT 
    DATE(m.created_at) as date,
    SUM(m.tokens) as total_tokens,
    COUNT(*) as message_count
FROM messages m
WHERE m.role = 'assistant'
GROUP BY DATE(m.created_at)
ORDER BY date DESC
LIMIT 30;
```

---

## 🔧 调试技巧

### 1. 查看 Python 日志
```bash
# 实时查看
tail -f agent/logs/info.*.log

# 查看错误
tail -f agent/logs/error.*.log

# 搜索配额相关日志
grep -i "quota" agent/logs/*.log
```

### 2. 查看 WebSocket 消息
```javascript
// 浏览器控制台
// 1. 打开开发者工具 (F12)
// 2. 切换到 Network 标签
// 3. 筛选 WS (WebSocket)
// 4. 查看消息内容
```

### 3. 数据库调试
```sql
-- 查看最近的消息
SELECT * FROM messages ORDER BY created_at DESC LIMIT 10;

-- 查看最近的执行步骤
SELECT * FROM execution_steps ORDER BY created_at DESC LIMIT 10;

-- 查看配额变化
SELECT * FROM user_quotas ORDER BY updated_at DESC;
```

---

## 🎯 性能基准

### Mock Agent
- 单次对话时间: ~5 秒
- Token 消耗: ~1055
- 执行步骤: 6 个
- 数据库操作: ~10 次

### 真实 A1 Agent（预估）
- 单次对话时间: 10-30 秒
- Token 消耗: 1000-5000
- 执行步骤: 5-20 个
- 数据库操作: ~20-50 次

---

## 📞 获取帮助

### 文档
1. `QUOTA_IMPLEMENTATION_STATUS.md` - 详细实现状态
2. `NEXT_STEPS.md` - 操作指南
3. `QUOTA_FLOW_DIAGRAM.md` - 流程图

### 代码位置
- 配额检查: `agent/api/websocket.py:50-70`
- Token 统计: `agent/services/callback.py:20-30`
- 配额更新: `agent/services/callback.py:150-160`

### 数据库
- 配额表: `user_quotas`
- 创建脚本: `agent/create_quota_table.sql`

---

## ✅ 检查清单

### 部署前
- [ ] 配额表已创建
- [ ] 所有用户有默认配额
- [ ] Python 服务正常启动
- [ ] 前端可以连接 WebSocket

### 功能测试
- [ ] 可以发送消息
- [ ] Token 正确统计
- [ ] 配额正确更新
- [ ] 配额不足时拒绝

### 性能测试
- [ ] 单次对话 < 10 秒
- [ ] 数据库查询 < 100ms
- [ ] WebSocket 延迟 < 50ms

---

**最后更新**: 2025-01-20  
**版本**: v1.0  
**状态**: ✅ 核心功能已完成
