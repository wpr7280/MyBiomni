# 配额功能流程图

## 📊 完整流程图

```
┌─────────────────────────────────────────────────────────────────┐
│                         用户发送消息                              │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│  WebSocket 接收消息 (api/websocket.py)                          │
│  - 验证 JWT Token                                                │
│  - 获取 user_id                                                  │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│  检查配额 (user_quotas 表)                                       │
│  - 查询 total_token_limit                                        │
│  - 查询 total_token_used                                         │
│  - 如果没有记录，创建默认配额（100万）                            │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
              ┌───────┴───────┐
              │               │
              ▼               ▼
    ┌─────────────┐   ┌─────────────┐
    │ 配额不足？   │   │ 配额充足？   │
    │ used >= limit│   │ used < limit │
    └──────┬──────┘   └──────┬──────┘
           │                 │
           ▼                 ▼
    ┌─────────────┐   ┌─────────────────────────────────┐
    │ 返回错误     │   │ 保存用户消息到 messages 表      │
    │ quota_exceeded│  │ - role: user                    │
    │             │   │ - content: 用户输入              │
    └─────────────┘   │ - tokens: 估算值                 │
                      └──────┬──────────────────────────┘
                             │
                             ▼
                      ┌─────────────────────────────────┐
                      │ 创建 WebSocketCallback          │
                      │ - conversation_id               │
                      │ - user_id                       │
                      │ - current_message_id            │
                      └──────┬──────────────────────────┘
                             │
                             ▼
                      ┌─────────────────────────────────┐
                      │ 执行 Agent (agent_service.py)   │
                      │ - Mock Agent 或真实 A1          │
                      │ - 流式输出                       │
                      └──────┬──────────────────────────┘
                             │
                             ▼
                      ┌─────────────────────────────────┐
                      │ 处理每个步骤 (callback.py)       │
                      │                                 │
                      │ 步骤 1: 思考                     │
                      │ - 累计 tokens (50 + 30)         │
                      │ - 保存 execution_step (reasoning)│
                      │                                 │
                      │ 步骤 2: 执行代码                 │
                      │ - 累计 tokens (80 + 60)         │
                      │ - 保存 execution_step (tool_call)│
                      │                                 │
                      │ 步骤 3: 观察结果                 │
                      │ - 累计 tokens (100 + 40)        │
                      │ - 保存 execution_step (result)  │
                      │                                 │
                      │ ... (更多步骤)                   │
                      │                                 │
                      │ 步骤 N: 最终答案                 │
                      │ - 累计 tokens (200 + 150)       │
                      │ - 提取 <solution> 内容          │
                      └──────┬──────────────────────────┘
                             │
                             ▼
                      ┌─────────────────────────────────┐
                      │ 保存 AI 消息 (callback.get_result)│
                      │ - role: assistant               │
                      │ - content: 最终答案              │
                      │ - input_tokens: 累计值           │
                      │ - output_tokens: 累计值          │
                      └──────┬──────────────────────────┘
                             │
                             ▼
                      ┌─────────────────────────────────┐
                      │ 更新配额 (user_quotas 表)        │
                      │ total_token_used +=              │
                      │   (input_tokens + output_tokens) │
                      └──────┬──────────────────────────┘
                             │
                             ▼
                      ┌─────────────────────────────────┐
                      │ 更新对话统计 (conversations 表)  │
                      │ - message_count += 2            │
                      │ - total_tokens += tokens        │
                      │ - last_message_at = now         │
                      └──────┬──────────────────────────┘
                             │
                             ▼
                      ┌─────────────────────────────────┐
                      │ 返回结果给前端                   │
                      │ - type: execution_complete      │
                      │ - message: AI 消息对象           │
                      └─────────────────────────────────┘
```

---

## 🔍 关键节点详解

### 1. 配额检查（WebSocket 层）

```python
# agent/api/websocket.py

quota = db.query(UserQuota).filter(UserQuota.user_id == user_id).first()

if not quota:
    # 创建默认配额
    quota = UserQuota(
        user_id=user_id, 
        total_token_limit=1000000, 
        total_token_used=0
    )
    db.add(quota)
    db.commit()

if quota.total_token_used >= quota.total_token_limit:
    # 配额不足
    await manager.send_message(str(conversation_id), {
        'type': 'quota_exceeded',
        'error': f'Token 配额已用完（{quota.total_token_used:,}/{quota.total_token_limit:,}）'
    })
    return
```

### 2. Token 统计（Callback 层）

```python
# agent/services/callback.py

async def process_step(self, output: str, usage: dict = None):
    # 累计 Token
    if usage:
        self.total_input_tokens += usage.get('input_tokens', 0)
        self.total_output_tokens += usage.get('output_tokens', 0)
    
    # 处理步骤...
```

### 3. 配额更新（Callback 层）

```python
# agent/services/callback.py

def get_result(self):
    # 保存 AI 消息
    assistant_message = Message(...)
    db.add(assistant_message)
    db.commit()
    
    # 更新配额
    quota = db.query(UserQuota).filter(UserQuota.user_id == self.user_id).first()
    if quota:
        quota.total_token_used += (self.total_input_tokens + self.total_output_tokens)
        quota.updated_at = datetime.now()
        db.commit()
```

---

## 📊 数据流图

```
┌──────────────┐
│   前端       │
│ (React)      │
└──────┬───────┘
       │ WebSocket
       │ ws://localhost:8000/ws/chat/{conversation_id}?token=xxx
       ▼
┌──────────────────────────────────────────────────────────┐
│                    Python Agent 服务                      │
│                                                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │ WebSocket   │→ │ Agent       │→ │ Callback    │     │
│  │ Handler     │  │ Service     │  │ Handler     │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
│         │                │                │              │
│         ▼                ▼                ▼              │
│  ┌──────────────────────────────────────────────┐      │
│  │            MySQL 数据库                       │      │
│  │  - user_quotas (配额表)                       │      │
│  │  - conversations (对话表)                     │      │
│  │  - messages (消息表)                          │      │
│  │  - execution_steps (执行步骤表)               │      │
│  └──────────────────────────────────────────────┘      │
└──────────────────────────────────────────────────────────┘
```

---

## 🔢 Token 计算示例

### Mock Agent 单次对话

| 步骤 | Input Tokens | Output Tokens | 小计 |
|------|--------------|---------------|------|
| 1. 思考 | 50 | 30 | 80 |
| 2. 执行代码 | 80 | 60 | 140 |
| 3. 观察结果 | 100 | 40 | 140 |
| 4. 再次执行 | 120 | 50 | 170 |
| 5. 观察结果 | 140 | 35 | 175 |
| 6. 最终答案 | 200 | 150 | 350 |
| **总计** | **690** | **365** | **1055** |

### 配额消耗计算

```
默认配额: 1,000,000 tokens
单次对话: 1,055 tokens
可用次数: 1,000,000 / 1,055 ≈ 948 次

示例：
- 第 1 次对话后: 999,945 tokens 剩余
- 第 100 次对话后: 894,500 tokens 剩余
- 第 500 次对话后: 472,500 tokens 剩余
- 第 948 次对话后: 560 tokens 剩余（不足一次）
- 第 949 次对话: 配额不足，拒绝执行
```

---

## 🎯 配额状态机

```
┌─────────────┐
│  初始状态    │
│ (无配额记录) │
└──────┬──────┘
       │ 首次发送消息
       ▼
┌─────────────────────┐
│  创建默认配额        │
│ limit: 1,000,000    │
│ used: 0             │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  正常使用状态        │
│ used < limit        │
│ (可以发送消息)       │
└──────┬──────────────┘
       │ 每次对话 +1055 tokens
       │
       ▼
┌─────────────────────┐
│  接近限制状态        │
│ used > limit * 0.9  │
│ (建议显示警告)       │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  配额用完状态        │
│ used >= limit       │
│ (拒绝发送消息)       │
└─────────────────────┘
       │
       │ 管理员重置或增加配额
       ▼
┌─────────────────────┐
│  恢复正常状态        │
│ used < limit        │
└─────────────────────┘
```

---

## 🔐 安全检查点

### 1. 认证检查
```
WebSocket 连接 → 验证 JWT Token → 获取 user_id
```

### 2. 配额检查
```
接收消息 → 查询 user_quotas → 检查 used < limit
```

### 3. 权限检查
```
操作对话 → 验证 conversation.user_id == current_user_id
```

### 4. 数据隔离
```
每个用户只能访问自己的：
- conversations
- messages
- execution_steps
- user_quotas
```

---

## 📈 性能优化建议

### 当前实现
```
每次发送消息:
1. 查询 user_quotas (1 次 SELECT)
2. 保存用户消息 (1 次 INSERT)
3. 执行 Agent (N 次 LLM 调用)
4. 保存执行步骤 (M 次 INSERT)
5. 保存 AI 消息 (1 次 INSERT)
6. 更新配额 (1 次 UPDATE)
7. 更新对话统计 (1 次 UPDATE)

总计: 2 SELECT + (M+2) INSERT + 2 UPDATE
```

### 优化方案（可选）
```
使用 Redis 缓存:
1. 配额信息缓存 (减少 SELECT)
2. 批量更新配额 (减少 UPDATE)
3. 异步更新统计 (提高响应速度)

预期提升: 响应时间减少 30-50%
```

---

## 🧪 测试场景

### 场景 1: 正常使用
```
1. 用户登录
2. 发送消息 "分析基因表达"
3. Agent 执行（约 5 秒）
4. 返回结果
5. 配额更新: used += 1055
```

### 场景 2: 配额不足
```
1. 用户已使用 999,500 tokens
2. 发送消息（需要 1055 tokens）
3. 配额检查失败
4. 返回 quota_exceeded 错误
5. 前端显示提示
```

### 场景 3: 首次使用
```
1. 新用户登录
2. user_quotas 表无记录
3. 自动创建默认配额（100万）
4. 正常执行
```

### 场景 4: 并发请求
```
1. 用户同时发送 2 条消息
2. 两个请求都检查配额（可能都通过）
3. 执行完成后分别更新配额
4. 最终 used 正确累计
```

---

**文档版本**: v1.0  
**创建时间**: 2025-01-20  
**用途**: 帮助理解配额功能的完整流程
