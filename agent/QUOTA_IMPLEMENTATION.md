# 配额功能实现说明

## ✅ 已完成的修改

### 1. 数据模型
- ✅ `models/models.py` - 添加 `UserQuota` 模型

### 2. 回调处理器
- ✅ `services/callback.py` - 添加 `user_id` 参数
- ✅ `services/callback.py` - `get_result()` 中更新配额

### 3. WebSocket 服务
- ⏳ `api/websocket.py` - 需要添加配额检查
- ⏳ `api/websocket.py` - 传递 `user_id` 给 callback

---

## 📋 待完成的修改

### 1. websocket.py

在 `handle_agent_execution` 函数开头添加配额检查：

```python
# 1. 检查配额
from models.models import UserQuota

quota = db.query(UserQuota).filter(UserQuota.user_id == user_id).first()

if not quota:
    quota = UserQuota(user_id=user_id)
    db.add(quota)
    db.commit()

if quota.total_token_used >= quota.total_token_limit:
    await manager.send_message(str(conversation_id), {
        'type': 'quota_exceeded',
        'error': f'Token 配额已用完'
    })
    return
```

在创建 callback 时传递 `user_id`：

```python
callback = WebSocketCallback(
    conversation_id=conversation_id,
    manager=manager,
    db=db,
    user_id=user_id  # 添加这个参数
)
```

---

## 🗄️ 数据库初始化

执行 SQL 脚本：

```bash
mysql -u root -p biomni_app < agent/create_quota_table.sql
```

---

## 🧪 测试

### 1. 创建测试用户配额

```sql
INSERT INTO user_quotas (user_id, total_token_limit, total_token_used)
VALUES (1, 10000, 0);  -- 用户 1，配额 1 万 Token
```

### 2. 测试配额检查

发送消息，观察：
- Token 累加
- 配额不足时的提示

### 3. 查看配额使用

```sql
SELECT 
    u.id,
    u.username,
    u.email,
    q.total_token_limit,
    q.total_token_used,
    (q.total_token_limit - q.total_token_used) as remaining
FROM admin u
LEFT JOIN user_quotas q ON u.id = q.user_id;
```

---

## 📊 前端展示

底部显示配额：

```typescript
<Tag color="blue">
  Token: {quota.totalTokenUsed.toLocaleString()} / {quota.totalTokenLimit.toLocaleString()}
</Tag>
```

---

**文档版本**: v1.0  
**创建时间**: 2025-01-20  
**维护者**: Biomni Team
