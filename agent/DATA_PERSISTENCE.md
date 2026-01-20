# Python Agent 数据持久化说明

## 数据保存流程

### 1. 用户消息（Spring Boot 保存）

```
前端发送消息
    ↓
Spring Boot MessageController.sendMessage()
    ↓
保存到 messages 表
    role = 'user'
    content = 用户输入
    tokens = 估算值
```

**已实现**: ✅ Spring Boot 的 MessageService

---

### 2. 执行步骤（Python Agent 保存）

```
Agent 执行过程中
    ↓
callback.on_tool_call()
    ↓
保存到 execution_steps 表
    step_type = 'tool_call'
    tool_name = 工具名称
    tool_input = 工具输入
    status = 'running'
    ↓
callback.on_tool_result()
    ↓
更新 execution_steps 表
    tool_output = 工具输出
    status = 'success'
    duration_ms = 执行时长
```

**已实现**: ✅ callback.py 中的 on_tool_call() 和 on_tool_result()

---

### 3. AI 消息（Python Agent 保存）

```
Agent 执行完成
    ↓
callback.get_result()
    ↓
保存到 messages 表
    role = 'assistant'
    content = AI 回答
    tokens = 总 Token
    input_tokens = 输入 Token
    output_tokens = 输出 Token
    ↓
更新 conversations 表
    message_count += 1
    total_tokens += tokens
    total_duration_ms += duration
    last_message_at = NOW()
```

**已实现**: ✅ callback.py 中的 get_result()

---

## 完整数据流

```
┌─────────────────────────────────────────────────────────┐
│  1. 用户发送消息                                         │
│     ↓                                                    │
│  2. Spring Boot 保存用户消息                            │
│     INSERT INTO messages (role='user', ...)             │
│     ↓                                                    │
│  3. WebSocket 发送给 Python Agent                       │
│     ↓                                                    │
│  4. Python Agent 执行                                   │
│     ├─ 步骤1: 保存执行步骤                              │
│     │  INSERT INTO execution_steps (...)                │
│     │  推送到前端                                        │
│     ├─ 步骤2: 更新执行结果                              │
│     │  UPDATE execution_steps SET tool_output=...       │
│     │  推送到前端                                        │
│     └─ 步骤3: ...                                       │
│     ↓                                                    │
│  5. Agent 执行完成                                      │
│     ├─ 保存 AI 消息                                     │
│     │  INSERT INTO messages (role='assistant', ...)     │
│     └─ 更新对话统计                                     │
│        UPDATE conversations SET                         │
│          message_count += 1,                            │
│          total_tokens += tokens,                        │
│          total_duration_ms += duration                  │
│     ↓                                                    │
│  6. 推送 AI 消息到前端                                  │
└─────────────────────────────────────────────────────────┘
```

---

## 数据库表更新

### messages 表

| 操作 | 时机 | 负责方 |
|------|------|--------|
| 插入用户消息 | 用户发送时 | Spring Boot |
| 插入 AI 消息 | Agent 完成时 | Python Agent |

### execution_steps 表

| 操作 | 时机 | 负责方 |
|------|------|--------|
| 插入步骤 | 工具调用时 | Python Agent |
| 更新步骤 | 工具完成时 | Python Agent |

### conversations 表

| 操作 | 时机 | 负责方 |
|------|------|--------|
| 更新统计（用户消息） | 用户发送时 | Spring Boot |
| 更新统计（AI 消息） | Agent 完成时 | Python Agent |

---

## 代码确认

### ✅ 用户消息保存（Spring Boot）

```java
// MessageService.java
@Transactional
public MessageVO sendMessage(Integer conversationId, Integer userId, String content) {
    // 创建用户消息
    MessageDO message = new MessageDO();
    message.setConversationId(conversationId);
    message.setRole("user");
    message.setContent(content);
    // ...
    messageDAO.insert(message);  // ✅ 保存到数据库
    
    // 更新对话统计
    conversation.setMessageCount(conversation.getMessageCount() + 1);
    conversationDAO.updateByPrimaryKey(conversation);  // ✅ 更新统计
    
    return convertToVO(message);
}
```

### ✅ 执行步骤保存（Python Agent）

```python
# services/callback.py
async def on_tool_call(self, tool_name: str, tool_input: dict):
    step = ExecutionStep(...)
    self.db.add(step)
    self.db.commit()  # ✅ 保存到数据库
    
    # 推送到前端
    await self.manager.send_message(...)  # ✅ 实时推送

async def on_tool_result(self, tool_output: str):
    step.tool_output = tool_output
    step.status = 'success'
    self.db.commit()  # ✅ 更新数据库
    
    # 推送到前端
    await self.manager.send_message(...)  # ✅ 实时推送
```

### ✅ AI 消息保存（Python Agent）

```python
# services/callback.py
def get_result(self):
    # 保存 AI 消息
    assistant_message = Message(...)
    self.db.add(assistant_message)
    self.db.commit()  # ✅ 保存到数据库
    
    # 更新对话统计
    conversation.message_count += 1
    conversation.total_tokens += tokens
    self.db.commit()  # ✅ 更新统计
    
    return {...}  # 返回给前端
```

---

## ✅ 总结

所有数据都会保存到数据库：

1. ✅ **用户消息** - Spring Boot 保存
2. ✅ **执行步骤** - Python Agent 保存（每个步骤）
3. ✅ **AI 消息** - Python Agent 保存
4. ✅ **对话统计** - 两边都会更新

数据持久化逻辑已完整实现！🎉

---

**文档版本**: v1.0  
**创建时间**: 2025-01-20  
**维护者**: Biomni Team
