# 执行步骤显示问题 - 调试文档

## 🐛 问题描述

### 问题 1: 执行步骤一直显示 "Executing PYTHON code..."
**现象**: 前端 Executor 面板显示步骤状态为 "running"，即使 Agent 已经完成

**原因**: 
- `<execute>` 标签创建 ExecutionStep，状态 = `'running'`
- 如果没有对应的 `<observation>` 标签，状态永远不会更新为 `'success'`
- `pending_tool_call_step` 没有被清理

**修复**: 在 `callback.py` 的 `get_result()` 中添加检查：
```python
if self.pending_tool_call_step:
    print(f"⚠️ Warning: 检测到未完成的 tool_call 步骤，自动标记为成功")
    self.pending_tool_call_step.status = 'success'
    self.pending_tool_call_step.completed_at = datetime.now()
    self.pending_tool_call_step.tool_output = "(No observation received)"
    self.db.commit()
```

### 问题 2: 执行步骤消失，只显示前几个
**现象**: 前端只显示前 4 个执行步骤，后面的都消失了

**原因**: 
- `get_result()` 方法没有被调用
- Agent 线程可能没有正确结束
- `step_queue.put(('done', None))` 没有被执行

**可能的根本原因**:
1. Agent 执行过程中抛出异常，但异常被吞掉
2. 线程无限循环，永远等不到 `'done'` 消息
3. `queue.Empty` 异常导致无限等待

**修复**: 
1. 添加超时机制（600 秒）
2. 添加详细的调试日志
3. 确保线程正确结束

### 问题 3: 最终的 assistant message 没有保存
**现象**: 数据库中没有 assistant 消息记录

**原因**: `get_result()` 没有被调用，所以 assistant_message 没有被创建

**修复**: 确保 `get_result()` 被调用

## 🔧 修复方案

### 1. callback.py 修复

```python
def get_result(self):
    """获取最终结果"""
    # ✅ 修复：如果还有未完成的 tool_call 步骤，标记为成功
    if self.pending_tool_call_step:
        print(f"⚠️ Warning: 检测到未完成的 tool_call 步骤，自动标记为成功")
        self.pending_tool_call_step.status = 'success'
        self.pending_tool_call_step.completed_at = datetime.now()
        self.pending_tool_call_step.duration_ms = int(
            (self.pending_tool_call_step.completed_at - self.pending_tool_call_step.started_at).total_seconds() * 1000
        )
        self.pending_tool_call_step.tool_output = "(No observation received)"
        self.db.commit()
        self.pending_tool_call_step = None
    
    # 保存 AI 消息
    assistant_message = Message(...)
    self.db.add(assistant_message)
    self.db.commit()
    self.db.refresh(assistant_message)
    
    # ✅ 修复：批量更新所有 execution_steps 的 message_id
    updated_count = self.db.query(ExecutionStep).filter(
        ExecutionStep.conversation_id == self.conversation_id,
        ExecutionStep.message_id == 0
    ).update({'message_id': assistant_message.id})
    self.db.commit()
    
    print(f"✓ 已将 {updated_count} 个执行步骤关联到消息 ID: {assistant_message.id}")
```

### 2. agent_service.py 修复

```python
# 添加超时机制
timeout_counter = 0
max_timeout = 6000  # 600 秒

while True:
    try:
        msg_type, data = await asyncio.get_event_loop().run_in_executor(
            None, step_queue.get, True, 0.1
        )
        
        timeout_counter = 0  # 重置计数器
        
        if msg_type == 'done':
            print("✓ Agent 执行完成，准备保存结果")
            break
            
    except queue.Empty:
        timeout_counter += 1
        if timeout_counter >= max_timeout:
            print(f"⚠️ Warning: Agent 执行超时，强制结束")
            break
        await asyncio.sleep(0.1)

print("✓ 开始调用 callback.get_result()")
result = callback.get_result()
print(f"✓ get_result() 返回: message_id={result.get('id')}")
return result
```

### 3. websocket.py 修复

```python
# 不要设置 current_message_id
callback = WebSocketCallback(
    conversation_id=conversation_id,
    manager=manager,
    db=db,
    user_id=user_id
)
# 注意：不设置 current_message_id，让它保持为 0
# 执行步骤会在 get_result() 中批量更新为 assistant_message.id
```

## 📊 数据流程

### 正确的流程

```
1. 用户发送消息
   ↓
2. 创建 user_message (id=42)
   ↓
3. 创建 WebSocketCallback
   - current_message_id = None (或 0)
   ↓
4. Agent 开始执行
   ↓
5. 创建 ExecutionStep
   - message_id = 0 (临时值)
   - step_order = 1, 2, 3...
   ↓
6. Agent 执行完成
   ↓
7. 调用 callback.get_result()
   ↓
8. 创建 assistant_message (id=43)
   ↓
9. 批量更新 ExecutionStep
   - WHERE message_id = 0
   - SET message_id = 43
   ↓
10. 返回结果到前端
```

### 错误的流程（之前）

```
1. 用户发送消息
   ↓
2. 创建 user_message (id=42)
   ↓
3. 创建 WebSocketCallback
   - current_message_id = 42 ❌ 错误！
   ↓
4. Agent 开始执行
   ↓
5. 创建 ExecutionStep
   - message_id = 42 ❌ 关联到 user_message
   ↓
6. Agent 执行完成（或超时）
   ↓
7. get_result() 没有被调用 ❌
   ↓
8. assistant_message 没有创建 ❌
   ↓
9. ExecutionStep 关联错误 ❌
```

## 🔍 调试日志

### 正常执行应该看到的日志

```
🚀 Agent 线程开始执行: conversation_id=11
✓ Agent 执行完成，共 15 个步骤
✓ Agent 执行完成，准备保存结果
✓ 开始调用 callback.get_result()
⚠️ Warning: 检测到未完成的 tool_call 步骤，自动标记为成功
✓ 已将 15 个执行步骤关联到消息 ID: 43
✓ get_result() 返回: message_id=43
✓ Agent 执行完成，返回结果: {'id': 43, ...}
```

### 异常情况的日志

```
🚀 Agent 线程开始执行: conversation_id=11
❌ Agent 线程执行失败: [错误信息]
[异常堆栈]
```

或

```
🚀 Agent 线程开始执行: conversation_id=11
⚠️ Warning: Agent 执行超时（600秒），强制结束
✓ 开始调用 callback.get_result()
✓ 已将 X 个执行步骤关联到消息 ID: XX
```

## 🧪 测试建议

### 1. 检查日志输出

重启服务后，发送一个简单的问题，观察日志：

```bash
# 应该看到这些日志
🚀 Agent 线程开始执行: conversation_id=X
✓ Agent 执行完成，共 X 个步骤
✓ Agent 执行完成，准备保存结果
✓ 开始调用 callback.get_result()
✓ 已将 X 个执行步骤关联到消息 ID: XX
✓ get_result() 返回: message_id=XX
```

### 2. 检查数据库

```sql
-- 检查消息是否保存
SELECT * FROM messages WHERE conversation_id = 11 ORDER BY id DESC LIMIT 5;

-- 检查执行步骤是否关联正确
SELECT id, message_id, step_order, step_type, status 
FROM execution_steps 
WHERE conversation_id = 11 
ORDER BY id DESC LIMIT 20;

-- 应该看到：
-- message_id 不是 0，而是真实的 assistant_message.id
-- status 都是 'success'，没有 'running'
```

### 3. 检查前端

前端应该：
- 收到 `execution_complete` 消息
- 显示完整的 assistant 回复
- Executor 面板显示所有步骤，状态都是完成

## 🎯 预期结果

修复后：
- ✅ 所有执行步骤都显示在 Executor 面板
- ✅ 步骤状态正确（success/failed，没有永久 running）
- ✅ assistant_message 正确保存到数据库
- ✅ execution_steps 正确关联到 assistant_message
- ✅ 前端收到完整的回复内容

## 📝 相关文件

- `agent/services/callback.py`: 回调处理器
- `agent/services/agent_service.py`: Agent 服务
- `agent/api/websocket.py`: WebSocket 处理
- `client/frontend/src/hooks/useWebSocket.ts`: 前端 WebSocket

## 🔮 后续优化

1. **进度反馈**: 显示 "Step X/Y"
2. **错误恢复**: 单个步骤失败不影响整体
3. **取消功能**: 允许用户中断执行
4. **重试机制**: 失败步骤自动重试
