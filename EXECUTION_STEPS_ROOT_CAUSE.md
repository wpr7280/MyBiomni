# 🔍 Execution Steps 问题根本原因分析

## 问题追踪过程

### 第一次发现（log19）
- 只保存了部分步骤
- 步骤顺序跳跃（1, 4, 5...）
- 缺少 `<observe>` 内容

### 第二次发现（log20）
- 支持了 `<observe>` 标签
- 但调试日志出现在 result 的 toolOutput 中
- 仍然缺少很多步骤

### 第三次发现（log21 + agent_20260128_083106.out）
- 调试日志改用 stderr 了
- 但调试日志仍然出现在输出中
- 问题：不是 callback 的问题，是 A1 Agent 本身的输出！

## 🎯 根本原因

**A1 Agent 的 `go_stream()` 方法调用 `pretty_print(message)`，默认会输出到 stdout。**

### 调用链：

```
1. A1.go_stream(prompt)
   ↓
2. for s in self.app.stream(...):
   ↓
3. out = pretty_print(message)  # ← 这里输出到 stdout！
   ↓
4. yield {"output": out}
   ↓
5. callback.process_step(output)
   ↓
6. 检测到分隔符和标签，保存步骤
   ↓
7. 但是 pretty_print 的输出也被 run_python_repl() 捕获
   ↓
8. 这些输出又被当作新的 output 处理
   ↓
9. 递归处理，步骤混乱
```

### pretty_print() 的问题：

```python
def pretty_print(message, printout=True):
    # ... 格式化消息 ...
    if printout:
        print(f"{title}")  # ← 输出到 stdout！
    return title
```

当 `printout=True`（默认值）时，会输出：
```
================================== Ai Message ==================================

I'll help you explore...
<execute>
...
</execute>
```

这些输出被 `run_python_repl()` 捕获，成为执行结果的一部分，然后又被 callback 处理。

## ✅ 完整解决方案

### 修复 1：A1 Agent 不输出到 stdout

**文件**: `agent/biomni/agent/a1.py`

```python
# 修改 go_stream() 方法
out = pretty_print(message, printout=False)  # 🔴 关键：不打印
```

### 修复 2：Callback 调试日志使用 stderr

**文件**: `agent/services/callback.py`

```python
import sys

# 所有调试日志使用 stderr
print(f"✓ Saved reasoning step {self.step_order}", file=sys.stderr)
```

### 修复 3：支持两种标签

```python
# 同时支持 <observe> 和 <observation>
observe_match = re.search(r'<observe>(.*?)</observe>', output, re.DOTALL)
observation_match = re.search(r'<observation>(.*?)</observation>', output, re.DOTALL)
```

### 修复 4：启动命令捕获 stderr

```bash
# 使用启动脚本（推荐）
./start.sh

# 或手动启动
nohup python main.py > log.out 2> log.err &
```

## 📊 预期效果

### 修复前：
```
Step 1: reasoning - "How do different..."
Step 2: reasoning - "I'll help you..."
Step 3: tool_call - python code
Step 4: result - "============================================================
                  📝 Processing output (length: 25963)  ← 调试日志污染！
                  ..."
```

### 修复后：
```
Step 1: reasoning - "How do different..."
Step 2: reasoning - "I'll help you..."
Step 3: tool_call - python code
Step 4: result - "PERTURBATION EFFECTS ON PROTEIN EXPRESSION  ← 干净的输出
                  ..."
Step 5: reasoning - "Now let me demonstrate..."
Step 6: tool_call - python code
Step 7: result - "Simulation complete..."
... (更多步骤)
```

## 🧪 验证方法

### 1. 重启服务

```bash
cd agent
./stop.sh
./start.sh
```

### 2. 查看日志

```bash
# 查看调试日志（stderr）
tail -f logs/latest.err | grep "Saved.*step"

# 应该看到：
# ✓ Saved reasoning step 1: How do different...
# ✓ Saved reasoning step 2: I'll help you...
# ✓ Saved tool_call step 3: python code (3840 chars)
# ✓ Updated tool_call step 3 to success
# ✓ Saved result step 4: PERTURBATION EFFECTS...  ← 无调试日志！
# ✓ Saved reasoning step 5: Now let me...
# ...
```

### 3. 检查数据库

```sql
SELECT step_order, step_type, 
       LEFT(tool_output, 100) as output_preview
FROM execution_steps 
WHERE conversation_id = (SELECT MAX(id) FROM conversations)
ORDER BY step_order;
```

应该看到：
- 连续的步骤顺序（1, 2, 3, 4, 5...）
- 干净的输出内容（无 "Processing output" 等调试信息）
- 完整的步骤类型（reasoning, tool_call, result）

## 📝 修改的文件

1. ✅ `agent/biomni/agent/a1.py` - 关键修复
2. ✅ `agent/services/callback.py` - 调试日志改 stderr
3. ✅ `client/frontend/src/components/ExecutionPanel.tsx` - 前端优化
4. ✅ `agent/start.sh` - 启动脚本
5. ✅ `agent/stop.sh` - 停止脚本
6. ✅ `agent/LOGGING_GUIDE.md` - 日志管理指南

## 🚀 下一步

重启服务后，应该能看到完整的执行步骤，无调试日志污染。
