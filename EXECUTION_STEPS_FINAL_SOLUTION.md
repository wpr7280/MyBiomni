# Execution Steps 最终解决方案

## 🎯 目标

将 Agent 的执行过程**详细展示**，包括所有思考、代码执行和输出结果。

## ✅ 实现的功能

### 1. 智能内容拆分

**Reasoning 拆分（4 级策略）**：
1. 按段落拆分（`\n\n`）
2. 如果段落太少（≤2）且内容长（>600字符），按行拆分
3. 如果单个段落太长（>800字符），按 600 字符拆分
4. 如果段落太多（>20），合并小段落（每 400 字符）

**Result 拆分（2 级策略）**：
1. 按分隔符拆分（`===` 或 `---` 且长度>30）
2. 如果块太少（≤3）且内容长（>1500字符），按 600 字符拆分

### 2. 详细的步骤命名

- 单个内容：`🤔 Reasoning`, `📋 Observation`
- 多个内容：`🤔 Thinking 1/5`, `📋 Output 3/8`

### 3. 完整的标签支持

- ✅ `<execute>` - 代码执行
- ✅ `<observe>` - 执行结果（A1 使用）
- ✅ `<observation>` - 执行结果（备用）
- ✅ `<solution>` - 最终答案

### 4. 调试日志使用 stderr

所有调试日志输出到 stderr，不污染执行结果。

## 📊 预期效果

### 修复前（12 个步骤）
```
Step 1: 🤔 Reasoning - "How do different..."
Step 2: 🤔 Reasoning - "I'll help you... (整个计划，600字符)"
Step 3: 🛠️ Executing - 代码
Step 4: 📋 Observation - "PERTURBATION EFFECTS... (所有输出，5000字符)"
Step 5: 🤔 Reasoning - "Now let me..."
...
```

### 修复后（40-60 个步骤）
```
Step 1: 🤔 Reasoning - "How do different..."
Step 2: 🤔 Thinking 1/4 - "I'll help you explore..."
Step 3: 🤔 Thinking 2/4 - "## Plan"
Step 4: 🤔 Thinking 3/4 - "1. [ ] Understand..."
Step 5: 🤔 Thinking 4/4 - "Let me start by..."
Step 6: 🛠️ Executing PYTHON code - print("PERTURBATION...")
Step 7: 📋 Output 1/8 - "================"
Step 8: 📋 Output 2/8 - "PERTURBATION EFFECTS..."
Step 9: 📋 Output 3/8 - "1. TYPES OF PERTURBATIONS..."
Step 10: 📋 Output 4/8 - "Genetic Perturbations..."
Step 11: 📋 Output 5/8 - "Chemical Perturbations..."
Step 12: 📋 Output 6/8 - "Environmental Perturbations..."
Step 13: 📋 Output 7/8 - "2. MEASUREMENT APPROACHES..."
Step 14: 📋 Output 8/8 - "3. KEY CONCEPTS..."
Step 15: 🤔 Thinking 1/2 - "Now let me demonstrate..."
Step 16: 🤔 Thinking 2/2 - "I'll create visualizations..."
Step 17: 🛠️ Executing PYTHON code - import pandas...
Step 18: 📋 Output 1/6 - "Loading DepMap datasets..."
Step 19: 📋 Output 2/6 - "CRISPR Gene Effect data..."
Step 20: 📋 Output 3/6 - "Gene Expression data..."
...
Step 40-60: 更多详细步骤
```

## 🔧 拆分策略详解

### Reasoning 拆分逻辑

```python
# 1. 按段落拆分
paragraphs = content.split('\n\n')

# 2. 如果段落太少（≤2）且内容长（>600），按行拆分
if len(paragraphs) <= 2 and len(content) > 600:
    paragraphs = content.split('\n')

# 3. 如果单个段落太长（>800），按 600 字符拆分
if len(paragraphs) == 1 and len(paragraphs[0]) > 800:
    paragraphs = [text[i:i+600] for i in range(0, len(text), 600)]

# 4. 如果段落太多（>20），合并小段落
if len(paragraphs) > 20:
    # 每 400 字符合并为一个块
    merged = []
    temp = []
    temp_len = 0
    for para in paragraphs:
        temp.append(para)
        temp_len += len(para)
        if temp_len > 400:
            merged.append('\n\n'.join(temp))
            temp = []
            temp_len = 0
    paragraphs = merged
```

### Result 拆分逻辑

```python
# 1. 按分隔符拆分（=== 或 --- 且长度>30）
for line in output_lines:
    if (line.strip().startswith('===') and len(line.strip()) > 30) or \
       (line.strip().startswith('---') and len(line.strip()) > 30):
        # 保存当前块，开始新块
        ...

# 2. 如果块太少（≤3）且内容长（>1500），按 600 字符拆分
if len(output_blocks) <= 3 and len(tool_output) > 1500:
    new_blocks = []
    for block in output_blocks:
        if len(block) > 800:
            for i in range(0, len(block), 600):
                new_blocks.append(block[i:i+600])
    output_blocks = new_blocks
```

## 🧪 测试验证

重启服务后，发送测试查询：

```bash
cd agent
./stop.sh
./start.sh

# 查看步骤保存日志
tail -f logs/latest.err | grep "Saved.*step"
```

应该看到：
```
✓ Saved reasoning step 1: How do different...
   📦 拆分为 4 个思考块
✓ Saved reasoning step 2 (1/4): I'll help you...
✓ Saved reasoning step 3 (2/4): ## Plan...
✓ Saved reasoning step 4 (3/4): 1. [ ] Understand...
✓ Saved reasoning step 5 (4/4): Let me start...
✓ Saved tool_call step 6: python code (3840 chars)
✓ Updated tool_call step 6 to success
   📦 拆分为 8 个输出块
✓ Saved result step 7 (1/8): ================...
✓ Saved result step 8 (2/8): PERTURBATION EFFECTS...
✓ Saved result step 9 (3/8): 1. TYPES OF...
✓ Saved result step 10 (4/8): Genetic Perturbations...
...
```

## 📊 预期步骤数量

对于一个典型的 Agent 执行（如 log21 的查询）：
- 6-7 个 AI 轮次
- 每个轮次包含：
  - 1-5 个 thinking 块
  - 1 个 tool_call
  - 3-10 个 output 块
- **总共 40-80 个步骤**（而不是 12 个）

## 🎨 前端显示优化

步骤数量增加后，前端已经支持：
- ✅ 折叠/展开（Collapse 组件）
- ✅ 步骤编号和图标
- ✅ 代码语法高亮
- ✅ Markdown 渲染
- ✅ 图片显示

## 📝 相关文件

- `agent/services/callback.py` - 核心修改（智能拆分）
- `agent/biomni/agent/a1.py` - pretty_print(printout=False)
- `client/frontend/src/components/ExecutionPanel.tsx` - 前端显示
- `agent/start.sh` - 启动脚本
- `agent/LOGGING_GUIDE.md` - 日志管理指南

## 🚀 立即测试

```bash
cd agent
./stop.sh
./start.sh
```

然后在前端发送查询，应该能看到 40-80 个详细的执行步骤！
