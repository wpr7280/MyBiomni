# 模型配置快速参考

## 🎯 常用模型配置

### OpenAI GPT-4
```json
{
  "llm": "gpt-4o",
  "source": "OpenAI",
  "temperature": 0.7
}
```
**环境变量**: `OPENAI_API_KEY=sk-...`

### Anthropic Claude
```json
{
  "llm": "claude-3-5-sonnet-20241022",
  "source": "Anthropic",
  "temperature": 0.7
}
```
**环境变量**: `ANTHROPIC_API_KEY=sk-ant-...`

### Ollama (本地)
```json
{
  "llm": "llama3.1:70b",
  "source": "Ollama",
  "temperature": 0.7
}
```
**无需 API Key**

### Google Gemini
```json
{
  "llm": "gemini-2.0-flash-exp",
  "source": "Gemini",
  "temperature": 0.7
}
```
**环境变量**: `GEMINI_API_KEY=...`

### Groq
```json
{
  "llm": "llama-3.3-70b-versatile",
  "source": "Groq",
  "temperature": 0.7
}
```
**环境变量**: `GROQ_API_KEY=...`

### 自定义模型
```json
{
  "llm": "my-model",
  "source": "Custom",
  "base_url": "http://localhost:8000/v1",
  "api_key": "your-key",
  "temperature": 0.7
}
```

---

## 📊 参数说明

| 参数 | 必需 | 类型 | 说明 | 示例 |
|------|------|------|------|------|
| `llm` | ✅ | string | 模型名称 | `"gpt-4o"` |
| `source` | ⚠️ | string | LLM 提供商（可自动检测） | `"OpenAI"` |
| `temperature` | ❌ | float | 温度参数 (0-2) | `0.7` |
| `base_url` | ⚠️ | string | 自定义模型 URL（Custom 必需） | `"http://..."` |
| `api_key` | ⚠️ | string | 自定义模型 Key（Custom 必需） | `"sk-..."` |
| `timeout_seconds` | ❌ | int | 超时时间（秒） | `600` |
| `use_tool_retriever` | ❌ | bool | 工具检索 | `true` |
| `commercial_mode` | ❌ | bool | 商业模式 | `false` |

---

## 🔑 环境变量

### OpenAI
```bash
OPENAI_API_KEY=sk-...
```

### Azure OpenAI
```bash
OPENAI_API_KEY=...
OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
```

### Anthropic
```bash
ANTHROPIC_API_KEY=sk-ant-...
```

### Gemini
```bash
GEMINI_API_KEY=...
```

### Groq
```bash
GROQ_API_KEY=...
```

### AWS Bedrock
```bash
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
```

---

## 🎨 前端配置界面设计

### 模型选择器
```
LLM 提供商: [下拉选择]
├─ OpenAI
│  └─ 模型: gpt-4o, gpt-4-turbo, gpt-3.5-turbo
├─ Anthropic
│  └─ 模型: claude-3-5-sonnet, claude-3-opus, claude-3-haiku
├─ Ollama
│  └─ 模型: llama3.1:70b, mistral, qwen
├─ Gemini
│  └─ 模型: gemini-2.0-flash-exp, gemini-1.5-pro
├─ Groq
│  └─ 模型: llama-3.3-70b-versatile, mixtral-8x7b
└─ Custom
   └─ 需要填写: base_url, api_key
```

### 配置表单
```
┌─────────────────────────────────────┐
│ LLM 提供商: [Anthropic         ▼]  │
│ 模型名称:   [claude-sonnet-4-5   ]  │
│ 温度参数:   [0.7] (0-2)            │
│ 超时时间:   [600] 秒               │
│ 工具检索:   [✓] 启用               │
│ 商业模式:   [ ] 启用               │
└─────────────────────────────────────┘

自定义模型配置（仅 Custom 提供商）
┌─────────────────────────────────────┐
│ Base URL:   [http://localhost:8000/v1] │
│ API Key:    [********************]  │
└─────────────────────────────────────┘

[测试配置] [保存] [重置]
```

---

## 🧪 配置测试

### 测试 OpenAI
```bash
# 1. 设置配置
POST /api/config/update
{
  "configKey": "agent.llm",
  "configValue": "gpt-4o"
}

# 2. 发送测试消息
# 观察是否使用 GPT-4o 响应
```

### 测试配置切换
```bash
# 1. 使用 Claude
agent.llm = "claude-sonnet-4-5"

# 2. 发送消息，记录响应风格

# 3. 切换到 GPT-4
agent.llm = "gpt-4o"

# 4. 发送相同消息，对比响应
```

---

## 📝 配置最佳实践

### 1. 生产环境
```json
{
  "agent.llm": "claude-3-5-sonnet-20241022",
  "agent.source": "Anthropic",
  "agent.temperature": 0.7,
  "agent.timeout_seconds": 600,
  "agent.use_tool_retriever": true,
  "agent.commercial_mode": true
}
```

### 2. 开发环境
```json
{
  "agent.llm": "llama3.1:70b",
  "agent.source": "Ollama",
  "agent.temperature": 0.7,
  "agent.timeout_seconds": 300,
  "agent.use_tool_retriever": false,
  "agent.commercial_mode": false
}
```

### 3. 测试环境
```json
{
  "agent.llm": "gpt-3.5-turbo",
  "agent.source": "OpenAI",
  "agent.temperature": 0.5,
  "agent.timeout_seconds": 180,
  "agent.use_tool_retriever": true,
  "agent.commercial_mode": false
}
```

---

**文档版本**: v1.0  
**创建时间**: 2025-01-20  
**用途**: 快速查找模型配置参数
