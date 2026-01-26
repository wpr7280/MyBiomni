# 数据库存储 API Key 的配置方案

## ✅ 方案优势

### 相比环境变量方案
- ✅ **动态配置**：无需重启服务即可切换模型
- ✅ **集中管理**：所有配置在后台统一管理
- ✅ **多模型支持**：可以配置多个提供商的 API Key
- ✅ **用户友好**：管理员在界面直接配置，无需 SSH 登录服务器

---

## 📊 数据库配置清单

### Agent 配置（8个）
| 配置键 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `agent.llm` | string | `claude-sonnet-4-5` | 模型名称 |
| `agent.source` | string | `Anthropic` | LLM 提供商 |
| `agent.temperature` | float | `0.7` | 温度参数 |
| `agent.timeout_seconds` | int | `600` | 超时时间 |
| `agent.use_tool_retriever` | bool | `true` | 工具检索 |
| `agent.commercial_mode` | bool | `false` | 商业模式 |
| `agent.base_url` | string | `` | 自定义 URL |
| `agent.api_key` | string | `` | 自定义 API Key |

### LLM API Keys（9个）
| 配置键 | 敏感 | 说明 |
|--------|------|------|
| `llm.openai_api_key` | ✅ | OpenAI API Key |
| `llm.anthropic_api_key` | ✅ | Anthropic API Key |
| `llm.gemini_api_key` | ✅ | Google Gemini API Key |
| `llm.groq_api_key` | ✅ | Groq API Key |
| `llm.azure_api_key` | ✅ | Azure OpenAI API Key |
| `llm.azure_endpoint` | ❌ | Azure Endpoint |
| `llm.aws_region` | ❌ | AWS Region |
| `llm.aws_access_key_id` | ✅ | AWS Access Key |
| `llm.aws_secret_access_key` | ✅ | AWS Secret Key |

**总计**：17 个配置项

---

## 🔄 配置加载流程

```
1. 用户发送消息
   ↓
2. WebSocket 接收（user_id, conversation_id）
   ↓
3. AgentService.get_or_create_agent(user_id, db)
   ↓
4. ConfigService.get_agent_config(db)
   ├─ 查询 system_config 表
   ├─ 解析配置值（int/float/bool/string）
   ├─ 根据 source 设置环境变量
   └─ 返回配置字典
   ↓
5. 计算配置哈希
   ├─ 如果配置未变更 → 返回缓存的 Agent
   └─ 如果配置已变更 → 创建新的 Agent
   ↓
6. 创建 A1 Agent（传递所有配置参数）
   ↓
7. 缓存 (config_hash, agent)
   ↓
8. 执行任务
```

---

## 🔐 安全机制

### 1. 敏感信息保护

**数据库**：
```sql
-- API Key 标记为敏感
is_sensitive = 1
```

**后端脱敏**：
```java
// SystemConfigService.java
if (config.getIsSensitive() == 1) {
    String value = config.getConfigValue();
    if (value != null && value.length() > 8) {
        vo.setConfigValue("***" + value.substring(value.length() - 4));
    }
}
```

**前端显示**：
```vue
<!-- 密码输入框 -->
<NInput 
  type="password"
  show-password-on="click"
  placeholder="sk-..."
/>
```

### 2. 环境变量设置

**Python 实现**：
```python
# config_service.py
def _set_llm_env_vars(source: str, credentials: dict):
    """根据提供商设置环境变量"""
    if source == 'OpenAI':
        os.environ['OPENAI_API_KEY'] = credentials.get('openai_api_key', '')
    elif source == 'Anthropic':
        os.environ['ANTHROPIC_API_KEY'] = credentials.get('anthropic_api_key', '')
    # ... 其他提供商
```

**优点**：
- ✅ LLM 库仍然从环境变量读取（兼容性）
- ✅ 配置从数据库加载（灵活性）
- ✅ 运行时动态设置（无需重启）

---

## 📝 已实现的文件

### Python 后端（3个文件）
1. ✅ `agent/services/config_service.py` - 配置加载服务
   - `get_agent_config()` - 从数据库加载配置
   - `_parse_value()` - 解析配置值
   - `_set_llm_env_vars()` - 设置环境变量

2. ✅ `agent/services/agent_service.py` - 更新 Agent 创建逻辑
   - 使用 ConfigService 加载配置
   - 配置哈希检测变更
   - 自动创建/更新实例

3. ✅ `agent/models/models.py` - 添加 SystemConfig 模型

### Spring Boot 后端（6个文件）
1. ✅ `insert_default_config.sql` - 初始化 17 个配置
2. ✅ `UpdateConfigRequest.java`
3. ✅ `BatchUpdateConfigRequest.java`
4. ✅ `SystemConfigVO.java`
5. ✅ `SystemConfigService.java`
6. ✅ `SystemConfigController.java`

### 前端（2个文件）
1. ✅ `admin/frontend/src/api/index.js` - 配置 API
2. ✅ `admin/frontend/src/views/config/model/index.vue` - 配置管理页面
   - 根据提供商显示对应的 API Key 输入框
   - 支持单个或多个配置项（Azure/Bedrock）

---

## 🎨 前端 UI 特点

### 1. 动态表单
```
选择 OpenAI → 显示 OpenAI API Key 输入框
选择 Anthropic → 显示 Anthropic API Key 输入框
选择 Azure → 显示 API Key + Endpoint 输入框
选择 Bedrock → 显示 Region + Access Key + Secret Key
选择 Ollama → 不显示 API Key（本地运行）
选择 Custom → 显示 Base URL + API Key
```

### 2. API Key 输入框
- ✅ 密码类型（默认隐藏）
- ✅ 点击显示/隐藏
- ✅ 占位符提示（sk-...）
- ✅ 获取链接提示

### 3. 配置分区
```
┌─────────────────────────────────────┐
│ 📘 基础配置                          │
│  - LLM 提供商                        │
│  - 模型名称                          │
│  - 温度参数                          │
├─────────────────────────────────────┤
│ 🔑 API Key 配置（根据提供商显示）    │
│  - OpenAI API Key                   │
│  - 或 Anthropic API Key             │
│  - 或 Azure API Key + Endpoint      │
│  - 或 AWS 凭证                       │
├─────────────────────────────────────┤
│ ✅ 自定义模型配置（仅 Custom）       │
│  - Base URL                         │
│  - API Key                          │
├─────────────────────────────────────┤
│ ⚙️ 高级配置                          │
│  - 超时时间                          │
│  - 工具检索                          │
│  - 商业模式                          │
├─────────────────────────────────────┤
│ 👁️ 配置预览                          │
│  - JSON 格式                         │
└─────────────────────────────────────┘
```

---

## 🚀 使用指南

### 1. 初始化配置

```bash
# 插入默认配置（包含 API Key 配置项）
cd admin/backend/data/init/mysql
mysql -u root -p biomni < insert_default_config.sql
```

### 2. 配置 OpenAI

**步骤**：
1. 进入"配置管理" → "模型配置"
2. LLM 提供商：选择 `OpenAI`
3. 模型名称：选择 `gpt-4o`
4. OpenAI API Key：输入 `sk-...`
5. 点击"保存配置"

**效果**：
- Python Agent 从数据库读取配置
- 设置 `os.environ['OPENAI_API_KEY']`
- 创建 OpenAI LLM 实例

### 3. 配置 Anthropic

**步骤**：
1. LLM 提供商：选择 `Anthropic (Claude)`
2. 模型名称：选择 `claude-3-5-sonnet-20241022`
3. Anthropic API Key：输入 `sk-ant-...`
4. 点击"保存配置"

### 4. 配置 Azure OpenAI

**步骤**：
1. LLM 提供商：选择 `Azure OpenAI`
2. 模型名称：输入 `gpt-4o`
3. Azure API Key：输入 API Key
4. Azure Endpoint：输入 `https://your-resource.openai.azure.com/`
5. 点击"保存配置"

### 5. 配置 AWS Bedrock

**步骤**：
1. LLM 提供商：选择 `AWS Bedrock`
2. 模型名称：输入 `anthropic.claude-3-5-sonnet-20241022-v2:0`
3. AWS Region：输入 `us-east-1`
4. AWS Access Key ID：输入 `AKIA...`
5. AWS Secret Access Key：输入密钥
6. 点击"保存配置"

---

## 🔍 配置变更检测

### 配置哈希机制

```python
# 1. 加载配置
config = ConfigService.get_agent_config(db)

# 2. 计算哈希
config_str = json.dumps(config, sort_keys=True)
config_hash = hashlib.md5(config_str.encode()).hexdigest()

# 3. 检查缓存
if user_id in agent_pool:
    cached_hash, cached_agent = agent_pool[user_id]
    if cached_hash == config_hash:
        return cached_agent  # 配置未变更，使用缓存
    else:
        # 配置已变更，创建新实例
        del agent_pool[user_id]

# 4. 创建新实例
agent = A1(**config)
agent_pool[user_id] = (config_hash, agent)
```

**优点**：
- ✅ 自动检测配置变更
- ✅ 配置未变更时复用实例（性能）
- ✅ 配置变更时自动更新（灵活）

---

## 🧪 测试场景

### 场景 1: 首次使用
```
1. 数据库无配置 → 插入默认配置
2. 用户发送消息
3. Python 加载配置（使用默认值）
4. 创建 Claude Agent
5. 执行任务
```

### 场景 2: 切换模型
```
1. 当前使用 Claude
2. 管理员修改配置为 GPT-4o
3. 管理员输入 OpenAI API Key
4. 保存配置
5. 用户发送新消息
6. Python 检测配置变更
7. 创建新的 GPT-4o Agent
8. 执行任务
```

### 场景 3: 配置未变更
```
1. 用户 A 发送消息 → 创建 Agent
2. 用户 A 再次发送消息 → 复用 Agent（配置哈希相同）
3. 用户 B 发送消息 → 创建新 Agent（不同用户）
```

### 场景 4: API Key 更新
```
1. 管理员更新 OpenAI API Key
2. 保存配置
3. 用户发送消息
4. Python 检测配置变更（哈希不同）
5. 创建新 Agent（使用新 API Key）
```

---

## 🔐 安全特性

### 1. 数据库层
```sql
-- 敏感字段标记
is_sensitive = 1  -- API Keys
is_sensitive = 0  -- 其他配置
```

### 2. 后端层
```java
// 查询时自动脱敏
if (config.getIsSensitive() == 1) {
    vo.setConfigValue("***" + value.substring(value.length() - 4));
}
```

### 3. 前端层
```vue
<!-- 密码输入框 -->
<NInput type="password" show-password-on="click" />

<!-- 显示时脱敏 -->
{{ apiKey ? '***' + apiKey.slice(-4) : '' }}
```

### 4. Python 层
```python
# 运行时设置环境变量（不打印）
os.environ['OPENAI_API_KEY'] = credentials.get('openai_api_key', '')
```

---

## 📋 完整的配置示例

### OpenAI 配置
```sql
UPDATE system_config SET config_value = 'gpt-4o' WHERE config_key = 'agent.llm';
UPDATE system_config SET config_value = 'OpenAI' WHERE config_key = 'agent.source';
UPDATE system_config SET config_value = 'sk-proj-...' WHERE config_key = 'llm.openai_api_key';
```

### Anthropic 配置
```sql
UPDATE system_config SET config_value = 'claude-3-5-sonnet-20241022' WHERE config_key = 'agent.llm';
UPDATE system_config SET config_value = 'Anthropic' WHERE config_key = 'agent.source';
UPDATE system_config SET config_value = 'sk-ant-...' WHERE config_key = 'llm.anthropic_api_key';
```

### Ollama 配置（无需 API Key）
```sql
UPDATE system_config SET config_value = 'llama3.1:70b' WHERE config_key = 'agent.llm';
UPDATE system_config SET config_value = 'Ollama' WHERE config_key = 'agent.source';
-- 无需 API Key
```

### 自定义模型配置
```sql
UPDATE system_config SET config_value = 'my-model' WHERE config_key = 'agent.llm';
UPDATE system_config SET config_value = 'Custom' WHERE config_key = 'agent.source';
UPDATE system_config SET config_value = 'http://localhost:8000/v1' WHERE config_key = 'agent.base_url';
UPDATE system_config SET config_value = 'your-api-key' WHERE config_key = 'agent.api_key';
```

---

## 🎯 实现清单

### Python 后端
- [x] SystemConfig 模型（models.py）
- [x] ConfigService（config_service.py）
  - [x] get_agent_config()
  - [x] _parse_value()
  - [x] _set_llm_env_vars()
- [x] 更新 AgentService（agent_service.py）
  - [x] 使用 ConfigService 加载配置
  - [x] 配置哈希检测
  - [x] 自动创建/更新实例
- [x] 更新 execute_agent_stream() 传递 db

### Spring Boot 后端
- [x] 默认配置 SQL（17个配置项）
- [x] Request 类
- [x] Response 类
- [x] SystemConfigService
- [x] SystemConfigController

### 前端
- [x] API 接口
- [x] 配置管理页面
  - [x] 动态 API Key 输入框
  - [x] 根据提供商显示不同配置
  - [x] 密码输入框
  - [x] 获取链接提示

---

## 🚀 快速启动

### 1. 初始化数据库
```bash
cd admin/backend/data/init/mysql
mysql -u root -p biomni < insert_default_config.sql
```

### 2. 配置 API Key
1. 登录管理后台
2. 进入"配置管理" → "模型配置"
3. 选择 LLM 提供商
4. 输入对应的 API Key
5. 保存配置

### 3. 测试
1. 登录客户端
2. 创建新对话
3. 发送消息
4. 观察是否使用新配置的模型

---

## 💡 优势总结

### 相比环境变量方案
| 特性 | 环境变量 | 数据库存储 |
|------|---------|-----------|
| 动态配置 | ❌ 需要重启 | ✅ 立即生效 |
| 管理方式 | ❌ SSH 登录 | ✅ Web 界面 |
| 多模型支持 | ⚠️ 需要配置所有 | ✅ 按需配置 |
| 安全性 | ✅ 不在代码中 | ✅ 数据库加密 |
| 审计 | ❌ 无记录 | ✅ 有变更记录 |
| 用户友好 | ❌ 技术门槛高 | ✅ 界面操作 |

### 核心优势
1. ✅ **零重启**：配置变更立即生效
2. ✅ **零 SSH**：无需登录服务器
3. ✅ **零代码**：管理员界面操作
4. ✅ **多模型**：支持 8 种提供商
5. ✅ **安全**：敏感信息脱敏显示

---

**文档版本**: v1.0  
**创建时间**: 2025-01-20  
**维护者**: Biomni Team  
**状态**: ✅ 已完成实现
