# A1 Agent 配置指南

## A1 初始化参数

A1 Agent 的 `__init__` 方法接受以下参数：

```python
A1(
    path: str | None = None,                    # 数据路径
    llm: str | None = None,                     # LLM 模型名称
    source: SourceType | None = None,           # LLM 提供商
    use_tool_retriever: bool | None = None,     # 是否使用工具检索
    timeout_seconds: int | None = None,         # 代码执行超时时间
    base_url: str | None = None,                # 自定义模型服务 URL
    api_key: str | None = None,                 # API 密钥
    commercial_mode: bool | None = None,        # 商业模式
    expected_data_lake_files: list | None = None # 预期数据湖文件
)
```

## 参数详解

### 1. path (数据路径)
- **类型**: `str | None`
- **默认值**: 从 `default_config.path` 读取
- **说明**: Agent 数据存储路径，包括数据湖、基准测试等
- **示例**: `'./data'`, `'/home/user/biomni_data'`

### 2. llm (LLM 模型)
- **类型**: `str | None`
- **默认值**: 从 `default_config.llm` 读取
- **说明**: 使用的 LLM 模型名称
- **常用值**:
  - `'claude-sonnet-4-5'` (Anthropic Claude)
  - `'gpt-4'`, `'gpt-4-turbo'` (OpenAI)
  - `'gemini-pro'` (Google Gemini)
  - `'llama3'` (Ollama 本地模型)

### 3. source (LLM 提供商)
- **类型**: `SourceType | None`
- **默认值**: 从 `default_config.source` 读取
- **说明**: LLM 服务提供商
- **可选值**:
  - `"Anthropic"` - Claude 模型
  - `"OpenAI"` - GPT 模型
  - `"AzureOpenAI"` - Azure OpenAI 服务
  - `"Ollama"` - 本地 Ollama 服务
  - `"Gemini"` - Google Gemini
  - `"Bedrock"` - AWS Bedrock
  - `"Custom"` - 自定义模型服务

### 4. use_tool_retriever (工具检索)
- **类型**: `bool | None`
- **默认值**: 从 `default_config.use_tool_retriever` 读取
- **说明**: 是否启用工具检索功能（根据查询自动选择相关工具）
- **推荐**: `True` (提高效率和准确性)

### 5. timeout_seconds (超时时间)
- **类型**: `int | None`
- **默认值**: 从 `default_config.timeout_seconds` 读取
- **说明**: 代码执行的超时时间（秒）
- **推荐**: `600` (10分钟)

### 6. base_url (自定义服务 URL)
- **类型**: `str | None`
- **默认值**: 从 `default_config.base_url` 读取
- **说明**: 自定义模型服务的基础 URL
- **使用场景**: 
  - 使用自部署的模型服务
  - 使用代理服务
- **示例**: `'http://localhost:8000/v1'`

### 7. api_key (API 密钥)
- **类型**: `str | None`
- **默认值**: 从 `default_config.api_key` 读取
- **说明**: LLM 服务的 API 密钥
- **注意**: 
  - 优先从环境变量读取（如 `ANTHROPIC_API_KEY`）
  - 如果使用自定义服务，可能不需要

### 8. commercial_mode (商业模式)
- **类型**: `bool | None`
- **默认值**: 从 `default_config.commercial_mode` 读取
- **说明**: 是否启用商业模式（排除非商业许可的数据集）
- **值**:
  - `True`: 只使用商业许可的数据集
  - `False`: 使用所有数据集（包括学术用途）

### 9. expected_data_lake_files (数据湖文件)
- **类型**: `list | None`
- **默认值**: `None`
- **说明**: 预期的数据湖文件列表
- **值**:
  - `None`: 自动下载所有数据湖文件
  - `[]`: 跳过数据湖下载
  - `['file1.csv', 'file2.pkl']`: 只下载指定文件

---

## Temperature 配置

**重要**: `temperature` 参数**不是** A1 的直接参数！

Temperature 通过 `default_config` 配置，有两种方式：

### 方式一：修改 agent/biomni/config.py

```python
from biomni.config import default_config

# 在创建 A1 之前修改
default_config.temperature = 0.7

agent = A1(llm='claude-sonnet-4-5')
```

### 方式二：通过环境变量

在 `.env` 文件中设置：
```bash
TEMPERATURE=0.7
```

---

## 配置示例

### 示例 1: 使用 Anthropic Claude（默认）

```python
agent = A1(
    path='./data',
    llm='claude-sonnet-4-5',
    source='Anthropic',
    use_tool_retriever=True,
    timeout_seconds=600,
    commercial_mode=False
)
```

### 示例 2: 使用 OpenAI GPT-4

```python
agent = A1(
    path='./data',
    llm='gpt-4-turbo',
    source='OpenAI',
    api_key='sk-...',  # 或通过环境变量 OPENAI_API_KEY
    use_tool_retriever=True,
    timeout_seconds=600
)
```

### 示例 3: 使用本地 Ollama

```python
agent = A1(
    path='./data',
    llm='llama3',
    source='Ollama',
    base_url='http://localhost:11434',
    use_tool_retriever=True,
    timeout_seconds=600
)
```

### 示例 4: 使用自定义模型服务

```python
agent = A1(
    path='./data',
    llm='custom-model',
    source='Custom',
    base_url='http://your-server:8000/v1',
    api_key='your-api-key',
    use_tool_retriever=True,
    timeout_seconds=600
)
```

### 示例 5: 商业模式（排除非商业数据）

```python
agent = A1(
    path='./data',
    llm='claude-sonnet-4-5',
    source='Anthropic',
    commercial_mode=True,  # 只使用商业许可的数据集
    use_tool_retriever=True
)
```

---

## 在 SaaS 系统中的配置

在你的 `agent_service.py` 中，配置从数据库读取：

```python
# 从数据库加载配置
config = ConfigService.get_agent_config(db)

# 创建 Agent（只传递 A1 支持的参数）
agent = A1(
    path=config.get('path', './data'),
    llm=config.get('llm', 'claude-sonnet-4-5'),
    source=config.get('source'),
    use_tool_retriever=config.get('use_tool_retriever', True),
    timeout_seconds=config.get('timeout_seconds', 600),
    base_url=config.get('base_url'),
    api_key=config.get('api_key'),
    commercial_mode=config.get('commercial_mode', False),
    expected_data_lake_files=None
)
```

---

## 常见问题

### Q: 如何设置 temperature？
A: Temperature 不是 A1 的参数，需要通过 `default_config` 或环境变量设置。

### Q: 如何使用自己的模型？
A: 设置 `source='Custom'` 和 `base_url`，确保你的服务兼容 OpenAI API 格式。

### Q: 数据湖文件很大，如何跳过下载？
A: 设置 `expected_data_lake_files=[]`。

### Q: 如何知道我的配置是否正确？
A: A1 初始化时会打印配置信息，检查控制台输出。

---

## 环境变量配置

在 `.env` 文件中可以设置：

```bash
# LLM 配置
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...

# Agent 配置
TEMPERATURE=0.7
TIMEOUT_SECONDS=600
USE_TOOL_RETRIEVER=true
COMMERCIAL_MODE=false

# 自定义服务
CUSTOM_BASE_URL=http://localhost:8000/v1
CUSTOM_API_KEY=your-key
```

---

## 参考

- A1 源码: `agent/biomni/agent/a1.py`
- 配置文件: `agent/biomni/config.py`
- 服务集成: `agent/services/agent_service.py`
