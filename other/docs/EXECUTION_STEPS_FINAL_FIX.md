# Execution Steps 最终修复方案

## 🔴 发现的真正问题

### 问题：A1 Agent 的 `pretty_print()` 输出到 stdout

从代码追踪发现：
1. `A1.go_stream()` 调用 `pretty_print(message)` 
2. `pretty_print()` 默认会 `print(f"{title}")` 输出到 stdout
3. 这些输出包含 "================================== Ai Message ==================================" 等分隔符
4. 这些输出被 `run_python_repl()` 捕获，成为执行结果的一部分
5. Callback 处理这些"执行结果"时，又检测到分隔符和标签，导致递归处理

**结果**：调试信息污染执行结果，步骤被重复处理或丢失。

## ✅ 最终修复

### 修复 1：A1 Agent 不输出到 stdout

**文件**: `agent/biomni/agent/a1.py`

```python
# ❌ 原代码：会输出到 stdout
out = pretty_print(message)

# ✅ 修复：不输出，只返回格式化字符串
out = pretty_print(message, printout=False)
```

### 修复 2：Callback 调试日志使用 stderr

**文件**: `agent/services/callback.py`

所有调试日志改用 `print(..., file=sys.stderr)`：
- `process_step()` - 所有调试日志
- `on_reasoning()` - 保存日志
- `on_tool_call()` - 保存日志
- `on_tool_result()` - 更新和保存日志
- `get_result()` - 所有更新日志
- `_extract_images_from_output()` - 图片检测日志

### 修复 3：支持 `<observe>` 标签

```python
# 同时支持两种标签
observe_match = re.search(r'<observe>(.*?)</observe>', output, re.DOTALL)
if observe_match:
    observation = observe_match.group(1).strip()
    await self.on_tool_result(observation)

observation_match = re.search(r'<observation>(.*?)</observation>', output, re.DOTALL)
if observation_match:
    observation = observation_match.group(1).strip()
    await self.on_tool_result(observation)
```

## 📊 预期效果

### 修复前（log21）：
```
✓ Saved reasoning step 1: How do different perturbations...
✓ Saved reasoning step 2: I'll help you explore...
✓ Saved tool_call step 3: python code (3840 chars)
✓ Saved result step 4: ============================================================  # ❌ 包含调试日志！
                       📝 Processing output (length: 25963)
                       ...
```

### 修复后（预期）：
```
✓ Saved reasoning step 1: How do different perturbations...
✓ Saved reasoning step 2: I'll help you explore...
✓ Saved tool_call step 3: python code (3840 chars)
✓ Updated tool_call step 3 to success
✓ Saved result step 4: ================================================================================  # ✅ 只有实际输出
                       PERTURBATION EFFECTS ON PROTEIN EXPRESSION
                       ...
✓ Saved reasoning step 5: Now let me demonstrate...
✓ Saved tool_call step 6: python code (2345 chars)
✓ Updated tool_call step 6 to success
✓ Saved result step 7: Loaded DepMap datasets...
...
```

## 🧪 测试验证

### 1. 重启服务

```bash
cd agent
python main.py
```

### 2. 发送测试消息

在前端发送任意消息，观察后端日志（stderr）：

```bash
# 查看 stderr 日志
tail -f logs/error.log | grep "Saved.*step"
```

应该看到：
- 所有步骤都有保存日志
- 步骤顺序连续（1, 2, 3, 4...）
- 没有调试日志污染

### 3. 检查数据库

```sql
SELECT step_order, step_type, step_name, 
       LEFT(tool_output, 100) as output_preview
FROM execution_steps 
WHERE conversation_id = (SELECT MAX(id) FROM conversations)
ORDER BY step_order;
```

应该看到：
- 连续的步骤顺序
- 清晰的输出内容（无调试日志）
- 完整的步骤类型（reasoning, tool_call, result）

### 4. 检查前端显示

Execution Panel 应该显示：
- ✅ 完整的步骤列表（15+ 个步骤）
- ✅ 清晰的内容（无 "Processing output" 等调试信息）
- ✅ 正确的步骤类型图标
- ✅ 图片正确显示（如果有）

## 🎯 关键改进点

1. **stderr vs stdout**：
   - stdout：被 `run_python_repl()` 捕获，成为执行结果的一部分
   - stderr：不被捕获，只在日志中显示

2. **避免递归处理**：
   - 调试日志不再污染执行结果
   - 不会被当作新的输出再次处理

3. **清晰的日志**：
   - 所有调试信息在 stderr 中
   - 所有执行结果在 stdout 中（被正确捕获）

## 📝 相关文件

- `agent/services/callback.py` - 已修复（所有 print 使用 stderr）
- `client/frontend/src/components/ExecutionPanel.tsx` - 前端显示（已优化）
- `other/docs/EXECUTION_STEPS_COMPLETE_FIX.md` - 完整修复文档
- `other/docs/EXECUTION_STEPS_QUICK_FIX.md` - 快速修复指南
- `EXECUTION_STEPS_FIX_SUMMARY.md` - 修复摘要

## 🚀 下一步

重启服务后测试，应该能看到完整的执行步骤，无调试日志污染。
