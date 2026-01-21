# 模型配置功能实现总结

## ✅ 已完成功能

### 1. 后端实现

#### 1.1 数据初始化
**文件**: `admin/backend/data/init/mysql/insert_default_config.sql`

**默认配置**:
```sql
agent.llm = 'claude-sonnet-4-5'
agent.source = 'Anthropic'
agent.temperature = '0.7'
agent.timeout_seconds = '600'
agent.use_tool_retriever = 'true'
agent.commercial_mode = 'false'
agent.base_url = ''
agent.api_key = ''
```

#### 1.2 Request 类
- `UpdateConfigRequest.java` - 单个配置更新
- `BatchUpdateConfigRequest.java` - 批量配置更新

#### 1.3 Response 类
- `SystemConfigVO.java` - 配置响应对象（支持敏感信息脱敏）

#### 1.4 Service 层
**文件**: `SystemConfigService.java`

**方法**:
- `getAgentConfigs()` - 获取所有 Agent 配置
- `getConfig()` - 获取单个配置
- `updateConfig()` - 更新单个配置（带验证）
- `batchUpdateConfigs()` - 批量更新配置
- `resetToDefault()` - 重置为默认值
- `validateConfigValue()` - 配置值验证

**验证规则**:
- `agent.source`: 必须是 8 种提供商之一
- `agent.temperature`: 0-2 之间
- `agent.timeout_seconds`: 60-3600 秒
- `agent.use_tool_retriever`: true/false
- `agent.commercial_mode`: true/false

#### 1.5 Controller 层
**文件**: `SystemConfigController.java`

**接口**:
- `POST /api/config/list` - 获取配置列表
- `POST /api/config/update` - 更新单个配置
- `POST /api/config/batch-update` - 批量更新配置
- `POST /api/config/reset` - 重置为默认值

---

### 2. 前端实现

#### 2.1 API 接口
**文件**: `admin/frontend/src/api/index.js`

**新增接口**:
```javascript
getConfigList: () => request.post('/config/list', {})
updateConfig: (data = {}) => request.post('/config/update', data)
batchUpdateConfig: (data = {}) => request.post('/config/batch-update', data)
resetConfig: () => request.post('/config/reset', {})
```

#### 2.2 配置管理页面
**文件**: `admin/frontend/src/views/config/model/index.vue`

**功能特点**:
1. **智能提供商选择**
   - 8 种 LLM 提供商下拉选择
   - 根据提供商显示推荐模型
   - 一键选择推荐模型

2. **动态表单**
   - 选择 Custom 提供商时显示 Base URL 和 API Key
   - 其他提供商隐藏自定义配置

3. **环境变量提示**
   - 根据提供商显示所需环境变量
   - Ollama 提示无需 API Key

4. **配置验证**
   - 温度参数：0-2，步长 0.1
   - 超时时间：60-3600 秒，步长 60
   - 开关组件：工具检索、商业模式

5. **配置预览**
   - 实时显示 JSON 格式配置
   - 敏感信息脱敏显示

6. **操作按钮**
   - 保存配置（带加载状态）
   - 重置为默认值（带确认）

---

## 🎨 UI 设计特点

### 1. 分区设计
```
┌─────────────────────────────────────────┐
│ 📘 基础配置                              │
│  - LLM 提供商                            │
│  - 模型名称（带推荐模型快捷按钮）         │
│  - 温度参数                              │
│  - 环境变量提示                          │
├─────────────────────────────────────────┤
│ ✅ 自定义模型配置（仅 Custom 显示）      │
│  - Base URL                             │
│  - API Key（密码输入框）                 │
├─────────────────────────────────────────┤
│ ⚙️ 高级配置                              │
│  - 超时时间                              │
│  - 工具检索（开关）                      │
│  - 商业模式（开关）                      │
├─────────────────────────────────────────┤
│ 👁️ 配置预览                              │
│  - JSON 格式显示                         │
│  - 实时更新                              │
└─────────────────────────────────────────┘
```

### 2. 交互优化
- ✅ 推荐模型快捷按钮（点击自动填充）
- ✅ 环境变量提示（根据提供商动态显示）
- ✅ 配置预览（实时显示 JSON）
- ✅ 敏感信息保护（API Key 脱敏）
- ✅ 表单验证（范围限制）
- ✅ 加载状态反馈
- ✅ 操作确认（重置前确认）

### 3. 响应式设计
- ✅ 移动端适配
- ✅ 表单宽度自适应
- ✅ 按钮布局优化

---

## 📊 支持的 LLM 提供商

| 提供商 | 推荐模型 | 环境变量 |
|--------|---------|----------|
| **OpenAI** | gpt-4o, gpt-4-turbo, gpt-3.5-turbo | OPENAI_API_KEY |
| **Anthropic** | claude-3-5-sonnet, claude-sonnet-4-5 | ANTHROPIC_API_KEY |
| **Ollama** | llama3.1:70b, mistral, qwen2.5:72b | 无需 API Key |
| **Gemini** | gemini-2.0-flash-exp, gemini-1.5-pro | GEMINI_API_KEY |
| **Groq** | llama-3.3-70b-versatile, mixtral-8x7b | GROQ_API_KEY |
| **Bedrock** | anthropic.claude-3-5-sonnet | AWS_REGION, AWS_ACCESS_KEY_ID |
| **Azure OpenAI** | gpt-4o, gpt-35-turbo | OPENAI_API_KEY, OPENAI_ENDPOINT |
| **Custom** | 自定义 | 在页面配置 Base URL 和 API Key |

---

## 🚀 使用指南

### 1. 初始化配置

```bash
# 插入默认配置到数据库
cd admin/backend/data/init/mysql
mysql -u root -p biomni < insert_default_config.sql
```

### 2. 访问配置页面

1. 登录管理后台
2. 进入"配置管理" → "模型配置"
3. 查看当前配置

### 3. 修改配置

#### 切换到 OpenAI GPT-4
1. LLM 提供商：选择 `OpenAI`
2. 模型名称：点击推荐模型 `gpt-4o` 或手动输入
3. 温度参数：保持 `0.7` 或调整
4. 点击"保存配置"

#### 切换到 Ollama 本地模型
1. LLM 提供商：选择 `Ollama (本地)`
2. 模型名称：点击 `llama3.1:70b` 或输入其他模型
3. 环境变量提示：显示"无需 API Key（本地运行）"
4. 点击"保存配置"

#### 使用自定义模型
1. LLM 提供商：选择 `自定义模型`
2. 模型名称：输入模型名称
3. Base URL：输入 `http://localhost:8000/v1`
4. API Key：输入自定义 API Key
5. 点击"保存配置"

### 4. 重置配置

1. 点击"重置为默认值"按钮
2. 确认操作
3. 配置恢复为 Claude Sonnet 4.5

---

## 🔍 配置验证

### 后端验证规则

```java
// 1. LLM 提供商验证
validSources = ["OpenAI", "AzureOpenAI", "Anthropic", "Ollama", "Gemini", "Groq", "Bedrock", "Custom"]

// 2. 温度参数验证
0 <= temperature <= 2

// 3. 超时时间验证
60 <= timeout_seconds <= 3600

// 4. 布尔值验证
use_tool_retriever, commercial_mode ∈ {"true", "false"}
```

### 前端验证

```javascript
// 1. 温度参数
<NInputNumber :min="0" :max="2" :step="0.1" />

// 2. 超时时间
<NInputNumber :min="60" :max="3600" :step="60" />

// 3. 必填项
configKey: required
```

---

## 📝 配置示例

### OpenAI GPT-4
```json
{
  "agent.llm": "gpt-4o",
  "agent.source": "OpenAI",
  "agent.temperature": "0.7",
  "agent.timeout_seconds": "600",
  "agent.use_tool_retriever": "true",
  "agent.commercial_mode": "false"
}
```

### Anthropic Claude
```json
{
  "agent.llm": "claude-3-5-sonnet-20241022",
  "agent.source": "Anthropic",
  "agent.temperature": "0.7",
  "agent.timeout_seconds": "600",
  "agent.use_tool_retriever": "true",
  "agent.commercial_mode": "false"
}
```

### Ollama 本地
```json
{
  "agent.llm": "llama3.1:70b",
  "agent.source": "Ollama",
  "agent.temperature": "0.7",
  "agent.timeout_seconds": "600",
  "agent.use_tool_retriever": "true",
  "agent.commercial_mode": "false"
}
```

### 自定义模型
```json
{
  "agent.llm": "my-custom-model",
  "agent.source": "Custom",
  "agent.base_url": "http://localhost:8000/v1",
  "agent.api_key": "your-api-key",
  "agent.temperature": "0.7",
  "agent.timeout_seconds": "600",
  "agent.use_tool_retriever": "true",
  "agent.commercial_mode": "false"
}
```

---

## 🔐 安全特性

### 1. 敏感信息保护
- ✅ API Key 标记为敏感（`is_sensitive = 1`）
- ✅ 前端显示时脱敏（`***1234`）
- ✅ 密码输入框（点击显示）

### 2. 权限控制
- ✅ 仅管理员可访问（`@RequireRole("admin")`）
- ✅ 所有接口都需要管理员权限

### 3. 配置验证
- ✅ 后端验证（Service 层）
- ✅ 前端验证（表单组件）
- ✅ 错误提示友好

---

## 🧪 测试清单

### 功能测试
- [ ] 加载配置列表
- [ ] 切换 LLM 提供商
- [ ] 选择推荐模型
- [ ] 修改温度参数
- [ ] 修改超时时间
- [ ] 切换工具检索
- [ ] 切换商业模式
- [ ] 配置自定义模型
- [ ] 保存配置
- [ ] 重置为默认值

### 验证测试
- [ ] 温度参数范围验证（0-2）
- [ ] 超时时间范围验证（60-3600）
- [ ] 无效提供商验证
- [ ] 必填项验证

### 安全测试
- [ ] 非管理员无法访问
- [ ] API Key 脱敏显示
- [ ] 敏感信息不泄露

---

## 📁 创建的文件清单

### 后端（6个文件）
1. `insert_default_config.sql` - 默认配置初始化
2. `UpdateConfigRequest.java` - 单个更新请求
3. `BatchUpdateConfigRequest.java` - 批量更新请求
4. `SystemConfigVO.java` - 配置响应对象
5. `SystemConfigService.java` - 配置服务
6. `SystemConfigController.java` - 配置接口

### 前端（2个文件）
1. `admin/frontend/src/api/index.js` - 添加配置 API
2. `admin/frontend/src/views/config/model/index.vue` - 配置管理页面

---

## 🎯 下一步：Python Agent 集成

### 需要实现的功能

#### 1. 配置服务（Python）
**文件**: `agent/services/config_service.py`

```python
from sqlalchemy.orm import Session
from models.models import SystemConfig

class ConfigService:
    @staticmethod
    def get_agent_config(db: Session) -> dict:
        """从数据库加载 Agent 配置"""
        configs = db.query(SystemConfig).filter(
            SystemConfig.config_key.like('agent.%')
        ).all()
        
        config = {}
        for c in configs:
            key = c.config_key.replace('agent.', '')
            value = ConfigService._parse_value(c.config_value, c.config_type)
            config[key] = value
        
        return config
    
    @staticmethod
    def _parse_value(value: str, config_type: str):
        if config_type == 'int':
            return int(value)
        elif config_type == 'float':
            return float(value)
        elif config_type == 'bool':
            return value.lower() == 'true'
        else:
            return value
```

#### 2. 更新 agent_service.py

```python
from services.config_service import ConfigService

class AgentService:
    @staticmethod
    def get_or_create_agent(user_id: int, db: Session):
        # 加载配置
        config = ConfigService.get_agent_config(db)
        
        # 创建 Agent
        agent = A1(
            path=config.get('path', './data'),
            llm=config.get('llm', 'claude-sonnet-4-5'),
            source=config.get('source'),
            temperature=config.get('temperature', 0.7),
            base_url=config.get('base_url'),
            api_key=config.get('api_key'),
            timeout_seconds=config.get('timeout_seconds', 600),
            use_tool_retriever=config.get('use_tool_retriever', True),
            commercial_mode=config.get('commercial_mode', False)
        )
        
        return agent
```

#### 3. 数据库模型

```python
# agent/models/models.py

class SystemConfig(Base):
    __tablename__ = 'system_config'
    
    id = Column(Integer, primary_key=True)
    config_key = Column(String(100), nullable=False, unique=True)
    config_value = Column(Text)
    config_type = Column(String(20), nullable=False, default='string')
    description = Column(String(500))
    is_sensitive = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now)
```

---

## 🔄 配置生效流程

```
1. 管理员在后台修改配置
   ↓
2. Spring Boot 保存到 system_config 表
   ↓
3. 用户发送新消息
   ↓
4. Python Agent 从数据库加载配置
   ↓
5. 创建新的 Agent 实例（使用新配置）
   ↓
6. 执行任务
```

**注意**：
- ✅ 配置变更对新对话立即生效
- ✅ 现有对话继续使用旧配置（Agent 实例已创建）
- ✅ 如需强制更新，可以清空 `agent_pool`

---

## 💡 使用场景

### 场景 1: 切换到更快的模型
**需求**: 降低成本，使用更快的模型

**操作**:
1. LLM 提供商：`OpenAI`
2. 模型名称：`gpt-3.5-turbo`
3. 保存配置

### 场景 2: 使用本地模型
**需求**: 数据隐私，使用本地 Ollama

**操作**:
1. LLM 提供商：`Ollama (本地)`
2. 模型名称：`llama3.1:70b`
3. 保存配置

### 场景 3: 测试新模型
**需求**: 测试自定义模型服务

**操作**:
1. LLM 提供商：`自定义模型`
2. 模型名称：`my-test-model`
3. Base URL：`http://localhost:8000/v1`
4. API Key：`test-key`
5. 保存配置

### 场景 4: 生产环境优化
**需求**: 提高准确性，使用最强模型

**操作**:
1. LLM 提供商：`Anthropic`
2. 模型名称：`claude-3-5-sonnet-20241022`
3. 温度参数：`0.5`（更确定性）
4. 超时时间：`900`（15分钟）
5. 商业模式：`启用`
6. 保存配置

---

## 📈 后续优化建议

### 1. 配置历史
- [ ] 记录配置变更历史
- [ ] 支持回滚到历史配置
- [ ] 显示变更人和时间

### 2. 配置测试
- [ ] 添加"测试配置"按钮
- [ ] 发送测试消息验证配置
- [ ] 显示测试结果

### 3. 配置模板
- [ ] 预设配置模板（开发/测试/生产）
- [ ] 一键切换模板
- [ ] 自定义模板

### 4. 用户级配置
- [ ] 支持为特定用户设置不同配置
- [ ] 配置优先级：用户 > 系统 > 默认

---

## ✅ 完成清单

### 后端
- [x] 默认配置 SQL
- [x] Request 类
- [x] Response 类
- [x] Service 层（含验证）
- [x] Controller 层
- [x] 代码编译通过

### 前端
- [x] API 接口定义
- [x] 配置管理页面
- [x] 智能提供商选择
- [x] 推荐模型快捷按钮
- [x] 动态表单（Custom 配置）
- [x] 环境变量提示
- [x] 配置预览
- [x] 保存和重置功能

### Python Agent
- [ ] 配置服务（待实现）
- [ ] 更新 agent_service.py（待实现）
- [ ] 数据库模型（待实现）

---

**文档版本**: v1.0  
**创建时间**: 2025-01-20  
**维护者**: Biomni Team  
**状态**: ✅ 后端和前端已完成，待 Python 集成
