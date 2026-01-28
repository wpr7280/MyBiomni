# Callback 改进文档

## 🎯 改进目标

让 WebSocket callback 的逻辑完全匹配 A1 Gradio 的渲染逻辑，提供更好的执行步骤展示。

## 📊 改进对比

### 之前的问题

1. ❌ `<execute>` 和 `<observation>` 配对关系不清晰
2. ❌ 代码内容没有显示在前端（只显示 "Executing PYTHON code"）
3. ❌ 创建了多余的 `result` 步骤
4. ❌ 状态更新逻辑复杂

### 改进后的逻辑

1. ✅ 清晰的 `<execute>` → `<observation>` 配对
2. ✅ 代码内容通过 `toolInput` 传递到前端
3. ✅ `<observation>` 直接更新 `<execute>` 步骤的输出
4. ✅ 简化的状态管理

## 🔧 核心改进

### 1. 统一变量命名

```python
# 之前
self.pending_tool_call_step = None

# 现在
self.pending_code_execution_step = None  # 更清晰的命名
```

### 2. 改进 `on_tool_result()` 逻辑

```python
async def on_tool_result(self, tool_output: str):
    """工具结果 - 显示执行结果"""
    # 更新之前的代码执行步骤
    if self.pending_code_execution_step:
        self.pending_code_execution_step.status = 'success'
        self.pending_code_execution_step.tool_output = tool_output  # ✅ 设置输出
        self.pending_code_execution_step.completed_at = datetime.now()
        self.pending_code_execution_step.duration_ms = ...
        self.db.commit()
        
        # ✅ 推送更新（不是新步骤）
        await self.manager.send_message(str(self.conversation_id), {
            'type': 'execution_step_update',  # ✅ 更新类型
            'step': {
                'id': self.pending_code_execution_step.id,
                'toolOutput': tool_output,  # ✅ 添加输出
                'status': 'success',
                'completedAt': ...,
                'durationMs': ...
            }
        })
        
        self.pending_code_execution_step = None
    
    # ✅ 检测图片并单独推送
    images = self._extract_images_from_output(tool_output)
    if images:
        await self.manager.send_message(str(self.conversation_id), {
            'type': 'images_detected',
            'images': images
        })
```

### 3. 前端需要处理新的消息类型

```typescript
// useWebSocket.ts 需要添加
case 'execution_step_update':
    // 更新现有步骤
    setExecutionSteps(prev => prev.map(step => 
        step.id === data.step.id 
            ? { ...step, ...data.step }
            : step
    ));
    break;

case 'images_detected':
    // 处理图片数据
    // 可以显示在最后一个步骤中
    break;
```

## 📋 执行流程对比

### A1 Gradio 流程

```
1. Reasoning → 显示思考过程
2. <execute> → 显示代码（status: pending）
3. <observation> → 更新代码步骤（status: done），显示输出
4. 检测图片 → 显示图片预览
5. <solution> → 显示最终答案
```

### 改进后的 WebSocket 流程

```
1. Reasoning → 创建 reasoning 步骤
2. <execute> → 创建 tool_call 步骤（status: running，包含代码）
3. <observation> → 更新 tool_call 步骤（status: success，添加输出）
4. 检测图片 → 推送图片数据
5. <solution> → 设置 final_content
```

## 🎨 前端展示效果

### 执行步骤展示

```
🤔 Reasoning
  [思考内容...]
  
🛠️ Executing PYTHON code
  ```python
  import pandas as pd
  print("Hello")
  ```
  
  Output:
  ```
  Hello
  ```
  
  Duration: 1250 ms
  
🖼️ Generated Images
  [图片预览]
```

## 🔍 调试信息

### 正常执行应该看到的日志

```
✓ 检测到图片: ./data/plot.png
✓ 检测到完整的 <solution> 标签
✓ 已将 5 个执行步骤关联到消息 ID: 50
```

### 异常情况的日志

```
⚠️ Warning: 检测到未完成的代码执行步骤，自动标记为成功
✓ 已将 5 个执行步骤关联到消息 ID: 50
```

## 📊 数据库结构

### execution_steps 表

```sql
-- 示例数据
id | conversation_id | message_id | step_order | step_type | step_name | tool_input | tool_output | status
1  | 10              | 50         | 1          | reasoning | 🤔 Reasoning | NULL | [思考内容] | success
2  | 10              | 50         | 2          | tool_call | 🛠️ Executing PYTHON code | {"code": "..."} | [输出] | success
3  | 10              | 50         | 3          | reasoning | 🤔 Reasoning | NULL | [思考内容] | success
4  | 10              | 50         | 4          | tool_call | 🛠️ Executing PYTHON code | {"code": "..."} | [输出] | success
```

## ✅ 改进总结

1. **统一变量命名**：`pending_code_execution_step` 更清晰
2. **简化步骤创建**：`<observation>` 不创建新步骤，而是更新现有步骤
3. **改进状态管理**：`running` → `success` 的转换更清晰
4. **图片处理优化**：单独推送图片数据，不创建额外步骤
5. **前端消息类型**：添加 `execution_step_update` 和 `images_detected`

## 🚀 下一步

前端需要更新 `useWebSocket.ts` 以处理新的消息类型：
- `execution_step_update`: 更新现有步骤
- `images_detected`: 处理图片数据

这样就能完全匹配 A1 Gradio 的展示效果了！
