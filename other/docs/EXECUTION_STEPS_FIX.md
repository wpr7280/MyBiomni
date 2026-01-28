# Execution Steps 显示问题修复

## 🔴 关键发现

**A1 Agent 使用 `<observe>` 标签，不是 `<observation>`！**

从 log20 可以看到：
```
<observe>
The function executed and returned literature search results...
</observe>
```

这是导致大量步骤丢失的根本原因。

## 问题描述

在 Executor Panel 中，Agent 的执行步骤显示不完整：
- 数据库中保存的步骤少于实际执行的步骤
- 步骤顺序跳跃（如从 1 跳到 4）
- 许多中间步骤丢失（如 "Starting analysis..." 等）
- **只保存了 2 个 reasoning 步骤，其他 `<observe>` 内容全部丢失**

## 根本原因

1. **标签不匹配**：代码中只检测 `<observation>`，但 A1 实际输出的是 `<observe>`
2. **Callback 处理不完整**：只处理带有特定标签的内容，忽略了大量的推理文本
3. **内容过滤过严**：`on_reasoning()` 方法过滤掉了太多有用的内容
4. **步骤计数问题**：某些情况下 `step_order` 没有正确递增
5. **Conversation 更新缺少日志**：无法确认是否正确更新

## 修复方案

### 1. 改进 `process_step()` 方法

**文件**: `agent/services/callback.py`

**关键修复**：
- ✅ **同时支持 `<observe>` 和 `<observation>` 标签**
- ✅ 清理输出时移除更多干扰内容
- ✅ 即使没有特定标签，也保存有意义的推理内容
- ✅ 添加详细的调试日志

```python
async def process_step(self, output: str, usage: dict = None):
    # 清理输出
    output = output.replace('================================== Ai Message ==================================', '')
    output = output.replace('================================ Human Message =================================', '')
    output = output.strip()
    
    if not output:
        return
    
    print(f"\n{'='*60}")
    print(f"📝 Processing output (length: {len(output)})")
    print(f"   First 200 chars: {output[:200]}...")
    print(f"{'='*60}")
    
    # 提取标签前的思考内容
    tag_positions = []
    for tag in ["<execute>", "<solution>", "<observe>", "<observation>", "<function_calls>"]:
        pos = output.find(tag)
        if pos != -1:
            tag_positions.append(pos)
    
    # 如果有标签，提取标签前的思考内容
    if tag_positions:
        first_tag_pos = min(tag_positions)
        thinking = output[:first_tag_pos].strip()
        if thinking and len(thinking) > 10:
            print(f"   ✓ 检测到 thinking 内容")
            self.step_order += 1
            await self.on_reasoning(thinking)
    elif len(output) > 10:
        print(f"   ✓ 无标签，作为 reasoning 处理")
        self.step_order += 1
        await self.on_reasoning(output)
    
    # 检查 <execute> 标签
    execute_match = re.search(r'<execute>(.*?)</execute>', output, re.DOTALL)
    if execute_match:
        print("   ✓ 检测到 <execute> 标签")
        self.step_order += 1
        # ... 处理代码
    
    # 🔴 关键修复：同时检查 <observe> 和 <observation>
    observe_match = re.search(r'<observe>(.*?)</observe>', output, re.DOTALL)
    if observe_match:
        print("   ✓ 检测到 <observe> 标签")
        observation = observe_match.group(1).strip()
        await self.on_tool_result(observation)
    
    observation_match = re.search(r'<observation>(.*?)</observation>', output, re.DOTALL)
    if observation_match:
        print("   ✓ 检测到 <observation> 标签")
        observation = observation_match.group(1).strip()
        await self.on_tool_result(observation)
```

### 2. 改进 `on_reasoning()` 方法

**改进点**:
- 更彻底地清理内容
- 添加详细的调试日志
- 限制内容长度（最多 5000 字符）

```python
async def on_reasoning(self, content: str):
    # 清理内容
    content = content.replace('================================== Ai Message ==================================', '')
    content = content.replace('================================ Human Message =================================', '')
    content = content.replace('<function_calls>', '')
    content = content.replace('</function_calls>', '')
    content = content.strip()
    
    if not content or len(content) < 5:
        return
    
    # 限制内容长度
    if len(content) > 5000:
        content = content[:5000] + "\n... (truncated)"
    
    # 保存到数据库
    step = ExecutionStep(...)
    self.db.add(step)
    self.db.commit()
    
    print(f"✓ Saved reasoning step {self.step_order}: {content[:100]}...")
```

### 3. 改进 `on_tool_result()` 方法

**改进点**:
- 添加调试日志
- 限制输出长度（避免数据库溢出）

```python
async def on_tool_result(self, tool_output: str):
    # 更新之前的 tool_call 步骤
    if self.pending_tool_call_step:
        self.pending_tool_call_step.status = 'success'
        self.pending_tool_call_step.completed_at = datetime.now()
        self.db.commit()
        print(f"✓ Updated tool_call step {self.pending_tool_call_step.step_order} to success")
    
    # 限制输出长度
    if len(tool_output) > 5000:
        tool_output = tool_output[:5000] + "\n... (truncated)"
    
    # 创建 result 步骤
    self.step_order += 1
    step = ExecutionStep(...)
    self.db.add(step)
    self.db.commit()
    
    print(f"✓ Saved result step {self.step_order}: {tool_output[:100]}...")
```

### 4. 改进 `get_result()` 方法

**改进点**:
- 添加详细的调试日志
- 确保 conversation 被正确更新

```python
def get_result(self):
    print(f"📊 get_result() 开始: conversation_id={self.conversation_id}")
    
    # 保存 AI 消息
    assistant_message = Message(...)
    self.db.add(assistant_message)
    self.db.commit()
    print(f"✓ 保存 assistant message: id={assistant_message.id}")
    
    # 更新配额
    quota = self.db.query(UserQuota).filter(...).first()
    if quota:
        old_used = quota.total_token_used
        quota.total_token_used += (self.total_input_tokens + self.total_output_tokens)
        self.db.commit()
        print(f"✓ 更新配额: {old_used} → {quota.total_token_used}")
    
    # 更新对话
    conversation = self.db.query(Conversation).get(self.conversation_id)
    if conversation:
        old_count = conversation.message_count
        conversation.message_count += 1
        conversation.total_tokens += assistant_message.tokens
        conversation.total_duration_ms += self.total_duration_ms
        conversation.last_message_at = datetime.now()
        conversation.updated_at = datetime.now()
        self.db.commit()
        
        print(f"✓ 更新 conversation:")
        print(f"  - message_count: {old_count} → {conversation.message_count}")
        print(f"  - total_tokens: {conversation.total_tokens}")
    else:
        print(f"⚠️ Warning: Conversation {self.conversation_id} not found!")
```

### 3. 改进前端显示

**文件**: `client/frontend/src/components/ExecutionPanel.tsx`

**改进点**:
- 清理 Markdown 内容中的干扰文本
- 移除多余的分隔符和标签
- 添加步骤名称格式化函数

```typescript
const renderStepContent = (step: ExecutionStep) => {
  if (step.stepType === 'reasoning' && step.toolOutput) {
    // 清理内容
    let content = step.toolOutput;
    
    // 移除多余的分隔符
    content = content.replace(/={50,}/g, '');
    content = content.replace(/Ai Message/g, '');
    content = content.replace(/Human Message/g, '');
    
    // 移除 function_calls 标签
    content = content.replace(/<\/?function_calls>/g, '');
    
    // 清理多余的空行
    content = content.replace(/\n{3,}/g, '\n\n');
    content = content.trim();
    
    if (!content) return null;
    
    return <ReactMarkdown>{content}</ReactMarkdown>;
  }
};

// 格式化步骤名称
const formatStepName = (step: ExecutionStep) => {
  if (step.stepName) {
    return step.stepName;
  }
  
  switch (step.stepType) {
    case 'reasoning':
      return '🤔 Thinking';
    case 'tool_call':
      return '🛠️ Executing';
    case 'result':
      return '📋 Result';
    default:
      return step.stepType;
  }
};
```

## 测试验证

### 运行测试脚本

```bash
cd agent
python test_callback.py
```

预期输出：
```
🧪 开始测试 WebSocketCallback
================================================================================
测试输出 1/5
================================================================================
📝 Processing output (length: 523)
   First 200 chars: I'll help you explore how different perturbations...
   ✓ 检测到 thinking 内容
✓ Saved reasoning step 1: I'll help you explore...
   ✓ 检测到 <execute> 标签
✓ Saved tool_call step 2: python code (234 chars)

================================================================================
测试输出 2/5
================================================================================
📝 Processing output (length: 98)
   First 200 chars: <observe>The function executed...
   ✓ 检测到 <observe> 标签
✓ Updated tool_call step 2 to success
✓ Saved result step 3: The function executed...

... (更多步骤)

✅ 测试完成
总步骤数: 10
✓ 步骤数正常
```

### 实际测试

修复后，应该能看到：

1. **完整的步骤序列**：
   - Step 1: 🤔 Thinking - "I'll help you explore..."
   - Step 2: 🛠️ Executing PYTHON code - query_pubmed(...)
   - Step 3: 📋 Observation - "The function executed..."
   - Step 4: 🤔 Thinking - "Now let me query databases..."
   - Step 5: 🛠️ Executing PYTHON code - query_kegg(...)
   - Step 6: 📋 Observation - "KEGG query returned..."
   - ...

2. **正确的步骤顺序**：1, 2, 3, 4, 5... 连续递增

3. **清晰的内容显示**：
   - 推理内容格式化良好
   - 代码高亮显示
   - 结果清晰可读

4. **Conversation 正确更新**：
   - message_count 增加
   - total_tokens 累计
   - last_message_at 更新

### 查看日志验证

重启服务后，日志应该显示：
```
✓ Saved reasoning step 1: I'll help you explore...
✓ Saved tool_call step 2: python code (234 chars)
✓ Updated tool_call step 2 to success
✓ Saved result step 3: The function executed...
✓ Saved reasoning step 4: Now let me query...
✓ Saved tool_call step 5: python code (189 chars)
✓ Updated tool_call step 5 to success
✓ Saved result step 6: KEGG query returned...
...
✓ 更新 conversation:
  - message_count: 2 → 3
  - total_tokens: 1234 → 2456
```

## 后续优化建议

1. **步骤分组**：将相关步骤（如 tool_call + result）分组显示
2. **可折叠内容**：长内容默认折叠，点击展开
3. **实时更新**：步骤执行时实时显示进度
4. **错误处理**：更好地显示错误步骤
5. **性能优化**：大量步骤时使用虚拟滚动

## 相关文件

- `agent/services/callback.py` - Callback 处理逻辑
- `agent/services/agent_service.py` - Agent 执行服务
- `client/frontend/src/components/ExecutionPanel.tsx` - 前端显示组件
- `agent/api/websocket.py` - WebSocket 通信
