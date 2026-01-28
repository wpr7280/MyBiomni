# Execution Steps 详细显示方案

## 🎯 目标

将 Agent 的执行过程**详细展示**出来，包括：
- 每一段思考过程
- 每一次代码执行
- 每一段执行结果
- 所有生成的图片

## 🔧 实现方案

### 1. 拆分长内容为多个步骤

**Reasoning 内容拆分**：
```python
# 按段落拆分（双换行符）
paragraphs = content.split('\n\n')

# 如果段落太少，按单换行符拆分
if len(paragraphs) <= 2 and len(content) > 500:
    paragraphs = content.split('\n')

# 如果还是只有一个段落但很长，按长度拆分
if len(paragraphs) == 1 and len(paragraphs[0]) > 1000:
    # 按 800 字符拆分
    paragraphs = [text[i:i+800] for i in range(0, len(text), 800)]

# 为每个段落创建一个步骤
for i, para in enumerate(paragraphs):
    step_name = f'🤔 Thinking {i+1}/{len(paragraphs)}'
    # 保存步骤...
```

**Result 内容拆分**：
```python
# 按分隔符拆分（=== 或 ---）
output_blocks = []
current_block = []

for line in output_lines:
    if line.strip().startswith('===') or line.strip().startswith('---'):
        if current_block:
            output_blocks.append('\n'.join(current_block))
            current_block = []
        current_block.append(line)
    else:
        current_block.append(line)

# 如果没有分隔符，按长度拆分
if len(output_blocks) == 1 and len(tool_output) > 2000:
    output_blocks = [tool_output[i:i+1000] for i in range(0, len(tool_output), 1000)]

# 为每个块创建一个步骤
for i, block in enumerate(output_blocks):
    step_name = f'📋 Output {i+1}/{len(output_blocks)}'
    # 保存步骤...
```

### 2. 预期效果

**修复前（12 个步骤）**：
```
Step 1: 🤔 Reasoning - "How do different..."
Step 2: 🤔 Reasoning - "I'll help you... (整个计划)"
Step 3: 🛠️ Executing - 代码
Step 4: 📋 Observation - "PERTURBATION EFFECTS... (所有输出)"
Step 5: 🤔 Reasoning - "Now let me..."
...
```

**修复后（30+ 个步骤）**：
```
Step 1: 🤔 Reasoning - "How do different..."
Step 2: 🤔 Thinking 1/3 - "I'll help you explore..."
Step 3: 🤔 Thinking 2/3 - "## Plan"
Step 4: 🤔 Thinking 3/3 - "Let me start by..."
Step 5: 🛠️ Executing - 代码
Step 6: 📋 Output 1/5 - "PERTURBATION EFFECTS..."
Step 7: 📋 Output 2/5 - "1. TYPES OF PERTURBATIONS..."
Step 8: 📋 Output 3/5 - "Genetic Perturbations..."
Step 9: 📋 Output 4/5 - "Chemical Perturbations..."
Step 10: 📋 Output 5/5 - "Environmental Perturbations..."
Step 11: 🤔 Thinking 1/2 - "Now let me demonstrate..."
Step 12: 🤔 Thinking 2/2 - "I'll create visualizations..."
Step 13: 🛠️ Executing - 更多代码
Step 14: 📋 Output 1/3 - "Simulation complete..."
Step 15: 📋 Output 2/3 - "Results: ..."
Step 16: 📋 Output 3/3 - "Visualization saved..."
...
```

### 3. 拆分策略

**Reasoning 拆分**：
1. 优先按双换行符（段落）拆分
2. 如果段落太少，按单换行符拆分
3. 如果还是太长，按 800 字符拆分
4. 每个段落 = 1 个步骤

**Result 拆分**：
1. 优先按分隔符（`===`, `---`）拆分
2. 如果没有分隔符，按 1000 字符拆分
3. 每个块 = 1 个步骤
4. 图片只在最后一个块显示

### 4. 步骤命名

- 单个内容：`🤔 Reasoning`, `📋 Observation`
- 多个内容：`🤔 Thinking 1/3`, `📋 Output 2/5`

### 5. 优势

✅ **更详细**：每个逻辑块都是独立步骤
✅ **更清晰**：用户可以看到完整的执行过程
✅ **更易读**：每个步骤内容适中，不会太长
✅ **更直观**：步骤数量增加，进度更明显

## 📊 预期步骤数量

对于一个典型的 Agent 执行：
- 6-7 个 AI 轮次
- 每个轮次包含 2-5 个逻辑块
- **总共 30-50 个步骤**（而不是 12 个）

## 🧪 测试

重启服务后，发送相同的查询，应该看到：
- 步骤数量显著增加（30+）
- 每个步骤内容适中（不会太长）
- 步骤名称清晰（Thinking 1/3, Output 2/5）
- 完整的执行过程展示

## 📝 相关文件

- `agent/services/callback.py` - 已修改（拆分长内容）
- `client/frontend/src/components/ExecutionPanel.tsx` - 前端显示（已优化）
