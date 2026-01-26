# Biomni Agent 配置管理方案

## 📋 目录
1. [A1 Agent 可配置参数](#1-a1-agent-可配置参数)
2. [模型配置详解](#2-模型配置详解)
3. [配置传递方案](#3-配置传递方案)
4. [配置同步机制](#4-配置同步机制)
5. [数据库设计](#5-数据库设计)
6. [实现方案](#6-实现方案)

---

## 1. A1 Agent 可配置参数

### 1.1 核心参数（来自 `biomni/agent/a1.py`）

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `path` | str | `"./data"` | 数据存储路径 |
| `llm` | str | `"claude-sonnet-4-5"` | LLM 模型名称 |
| `source` | SourceType | `None` (自动检测) | LLM 提供商 |
| `use_tool_retriever` | bool | `True` | 是否使用工具检索 |
| `timeout_seconds` | int | `600` | 代码执行超时时间（秒） |
| `base_url` | str | `None` | 自定义模型服务 URL |
| `api_key` | str | `None` | 自定义模型 API Key |
| `commercial_mode` | bool | `False` | 商业模式（排除非商业数据集） |
| `expected_data_lake_files` | list | `None` | 预期的数据湖文件 |

### 1.2 BiomniConfig 参数（来自 `biomni/config.py`）

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `path` | str | `"./data"` | 数据路径 |
| `timeout_seconds` | int | `600` | 超时时间 |
| `llm` | str | `"claude-sonnet-4-5"` | LLM 模型 |
| `temperature` | float | `0.7` | 温度参数 |
| `use_tool_retriever` | bool | `True` | 工具检索 |
| `commercial_mode` | bool | `False` | 商业模式 |
| `base_url` | str | `None` | 自定义 URL |
| `api_key` | str | `None` | 自定义 API Key |
| `source` | str | `None` | LLM 来源 |
| `protocols_io_access_token` | str | `None` | Protocols.io Token |

---

## 2. 模型配置详解

### 2.1 支持的 LLM 提供商（来自 `biomni/llm.py`）

| 提供商 | Source 值 | 必需参数 | 可选参数 | 环境变量 |
|--------|-----------|----------|----------|----------|
| **OpenAI** | `"OpenAI"` | `model` | `temperature`, `stop_sequences` | `OPENAI_API_KEY` |
| **Azure OpenAI** | `"AzureOpenAI"` | `model` | `temperature` | `OPENAI_API_KEY`, `OPENAI_ENDPOINT` |
| **Anthropic** | `"Anthropic"` | `model` | `temperature`, `stop_sequences` | `ANTHROPIC_API_KEY` |
| **Google Gemini** | `"Gemini"` | `model` | `temperature`, `stop_sequences` | `GEMINI_API_KEY` |
| **Groq** | `"Groq"` | `model` | `temperature`, `stop_sequences` | `GROQ_API_KEY` |
| **Ollama** | `"Ollama"` | `model` | `temperature` | - |
| **AWS Bedrock** | `"Bedrock"` | `model` | `temperature`, `stop_sequences` | `AWS_REGION` |
| **Custom** | `"Custom"` | `model`, `base_url`, `api_key` | `temperature`, `stop_sequences` | - |

### 2.2 常用模型示例

#### OpenAI
```python
{
    "llm": "gpt-4o",
    "source": "OpenAI",
    "temperature": 0.7
}
# 需要环境变量: OPENAI_API_KEY
```

#### Anthropic (Claude)
```python
{
    "llm": "claude-3-5-sonnet-20241022",
    "source": "Anthropic",
    "temperature": 0.7
}
# 需要环境变量: ANTHROPIC_API_KEY
```

#### Ollama (本地)
```python
{
    "llm": "llama3.1:70b",
    "source": "Ollama",
    "temperature": 0.7
}
# 无需 API Key
```

#### 自定义模型服务
```python
{
    "llm": "my-custom-model",
    "source": "Custom",
    "base_url": "http://localhost:8000/v1",
    "api_key": "your-api-key",
    "temperature": 0.7
}
```

### 2.3 Source 自动检测规则

如果不指定 `source`，系统会根据 `llm` 名称自动检测：

| 模型名称前缀 | 自动检测为 |
|-------------|-----------|
| `claude-` | Anthropic |
| `gpt-` | OpenAI |
| `azure-` | AzureOpenAI |
| `gemini-` | Gemini |
| `groq` | Groq |
| `anthropic.claude-` | Bedrock |
| `llama`, `mistral`, `qwen` 等 | Ollama |
| 包含 `/` | Ollama |

---

## 3. 配置传递方案

### 3.1 当前实现（agent_service.py）

```python
class AgentService:
    @staticmethod
    def get_or_create_agent(user_id: int, config: dict = None):
        if user_id not in agent_pool:
            agent_pool[user_id] = A1(
                path=config.get('data_path', './data') if config else './data',
                llm=config.get('llm', 'claude-sonnet-4-5') if config else 'claude-sonnet-4-5',
            )
        return agent_pool[user_id]
```

**问题**：
- ❌ 只传递了 `path` 和 `llm` 两个参数
- ❌ 没有传递 `source`, `temperature`, `base_url`, `api_key` 等
- ❌ 配置是硬编码的，无法动态调整

### 3.2 改进方案

```python
class AgentService:
    @staticmethod
    def get_or_create_agent(user_id: int, config: dict = None):
        """获取或创建 Agent 实例
        
        Args:
            user_id: 用户ID
            config: 配置字典，包含：
                - llm: 模型名称
                - source: LLM 提供商
                - temperature: 温度参数
                - base_url: 自定义模型 URL
                - api_key: 自定义模型 API Key
                - path: 数据路径
                - timeout_seconds: 超时时间
                - use_tool_retriever: 是否使用工具检索
                - commercial_mode: 商业模式
        """
        if user_id not in agent_pool:
            # 从配置中提取参数
            agent_config = {
                'path': config.get('path', './data'),
                'llm': config.get('llm', 'claude-sonnet-4-5'),
                'source': config.get('source'),
                'temperature': config.get('temperature', 0.7),
                'base_url': config.get('base_url'),
                'api_key': config.get('api_key'),
                'timeout_seconds': config.get('timeout_seconds', 600),
                'use_tool_retriever': config.get('use_tool_retriever', True),
                'commercial_mode': config.get('commercial_mode', False)
            } if config else {}
            
            agent_pool[user_id] = A1(**agent_config)
        
        return agent_pool[user_id]
```

---

## 4. 配置同步机制

### 4.1 配置来源优先级

```
用户级配置 > 系统级配置 > 默认配置
```

### 4.2 配置存储方案

#### 方案 A：数据库存储（推荐）

**优点**：
- ✅ 持久化存储
- ✅ 支持多实例部署
- ✅ 便于管理和审计
- ✅ 支持用户级和系统级配置

**缺点**：
- ⚠️ 需要数据库查询
- ⚠️ 配置变更需要重启 Agent

#### 方案 B：配置文件存储

**优点**：
- ✅ 简单直接
- ✅ 便于版本控制

**缺点**：
- ❌ 不支持多实例
- ❌ 不支持用户级配置
- ❌ 配置变更需要重启服务

#### 方案 C：混合方案（推荐）

**系统级配置**：存储在数据库
**用户级配置**：存储在数据库
**默认配置**：存储在代码中（BiomniConfig）

### 4.3 配置更新流程

```
1. 管理员在后台修改配置
   ↓
2. Spring Boot 保存到数据库
   ↓
3. Python Agent 定期轮询或接收通知
   ↓
4. 清除 agent_pool 中的旧实例
   ↓
5. 下次请求时使用新配置创建实例
```

---

## 5. 数据库设计

### 5.1 系统配置表

```sql
CREATE TABLE `system_config` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '配置ID',
  `config_key` VARCHAR(100) NOT NULL COMMENT '配置键',
  `config_value` VARCHAR(10000) COMMENT '配置值',
  `config_type` VARCHAR(20) NOT NULL DEFAULT 'string' COMMENT '配置类型: string, int, float, bool, json',
  `description` VARCHAR(500) COMMENT '配置说明',
  `is_sensitive` INT NOT NULL DEFAULT 0 COMMENT '是否敏感: 0-否, 1-是',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_config_key` (`config_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统配置表';
```

**配置示例**：
```sql
INSERT INTO system_config (config_key, config_value, config_type, description) VALUES
('agent.llm', 'claude-sonnet-4-5', 'string', 'LLM 模型名称'),
('agent.source', 'Anthropic', 'string', 'LLM 提供商'),
('agent.temperature', '0.7', 'float', '温度参数'),
('agent.timeout_seconds', '600', 'int', '超时时间（秒）'),
('agent.use_tool_retriever', 'true', 'bool', '是否使用工具检索'),
('agent.commercial_mode', 'false', 'bool', '商业模式');
```

### 5.2 用户配置表（可选）

```sql
CREATE TABLE `user_config` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '配置ID',
  `user_id` INT NOT NULL COMMENT '用户ID',
  `config_key` VARCHAR(100) NOT NULL COMMENT '配置键',
  `config_value` TEXT COMMENT '配置值',
  `config_type` VARCHAR(20) NOT NULL DEFAULT 'string' COMMENT '配置类型',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_user_config` (`user_id`, `config_key`),
  CONSTRAINT `fk_user_config_user` FOREIGN KEY (`user_id`) REFERENCES `admin` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户配置表';
```

---

## 6. 实现方案

### 6.1 配置加载流程

```
WebSocket 连接
   ↓
获取 user_id
   ↓
加载配置（优先级）:
   1. 查询 user_config 表（用户级）
   2. 查询 system_config 表（系统级）
   3. 使用 BiomniConfig 默认值
   ↓
创建/获取 Agent 实例
   ↓
执行任务
```

### 6.2 Python 实现

#### 6.2.1 配置服务（新建）

```python
# agent/services/config_service.py

from sqlalchemy.orm import Session
from models.models import SystemConfig, UserConfig
from biomni.config import BiomniConfig

class ConfigService:
    """配置管理服务"""
    
    @staticmethod
    def get_agent_config(db: Session, user_id: int = None) -> dict:
        """获取 Agent 配置
        
        优先级：用户配置 > 系统配置 > 默认配置
        """
        config = {}
        
        # 1. 加载默认配置
        default_config = BiomniConfig()
        config = default_config.to_dict()
        
        # 2. 加载系统配置
        system_configs = db.query(SystemConfig).filter(
            SystemConfig.config_key.like('agent.%')
        ).all()
        
        for sc in system_configs:
            key = sc.config_key.replace('agent.', '')
            value = ConfigService._parse_config_value(sc.config_value, sc.config_type)
            config[key] = value
        
        # 3. 加载用户配置（如果指定了 user_id）
        if user_id:
            user_configs = db.query(UserConfig).filter(
                UserConfig.user_id == user_id,
                UserConfig.config_key.like('agent.%')
            ).all()
            
            for uc in user_configs:
                key = uc.config_key.replace('agent.', '')
                value = ConfigService._parse_config_value(uc.config_value, uc.config_type)
                config[key] = value
        
        return config
    
    @staticmethod
    def _parse_config_value(value: str, config_type: str):
        """解析配置值"""
        if config_type == 'int':
            return int(value)
        elif config_type == 'float':
            return float(value)
        elif config_type == 'bool':
            return value.lower() in ('true', '1', 'yes')
        elif config_type == 'json':
            import json
            return json.loads(value)
        else:
            return value
```


#### 6.2.2 更新 agent_service.py

```python
# agent/services/agent_service.py

from services.config_service import ConfigService

class AgentService:
    
    @staticmethod
    def get_or_create_agent(user_id: int, db: Session):
        """获取或创建 Agent 实例"""
        if USE_MOCK_AGENT:
            # Mock Agent 不需要配置
            if user_id not in agent_pool:
                agent_pool[user_id] = MockAgentAsync(
                    path='./data',
                    llm='claude-sonnet-4-5'
                )
            return agent_pool[user_id]
        
        # 加载配置
        config = ConfigService.get_agent_config(db, user_id)
        
        # 检查配置是否变更
        config_key = f"config_{user_id}"
        if config_key in agent_pool:
            old_config, agent = agent_pool[config_key]
            if old_config == config:
                # 配置未变更，返回现有实例
                return agent
            else:
                # 配置已变更，删除旧实例
                del agent_pool[config_key]
        
        # 创建新实例
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
        
        # 缓存配置和实例
        agent_pool[config_key] = (config, agent)
        
        return agent
```

#### 6.2.3 更新 websocket.py

```python
# agent/api/websocket.py

async def handle_agent_execution(...):
    # 执行 Agent（流式）
    result = await AgentService.execute_agent_stream(
        conversation_id=conversation_id,
        user_id=user_id,
        query=content,
        callback=callback,
        db=db  # 传递 db 以加载配置
    )
```

---

## 7. Spring Boot 后端实现

### 7.1 数据模型

```java
// SystemConfigDO.java
@Data
public class SystemConfigDO {
    private Integer id;
    private String configKey;
    private String configValue;
    private String configType;  // string, int, float, bool, json
    private String description;
    private Integer isSensitive;  // 0-否, 1-是
    private Date createdAt;
    private Date updatedAt;
}
```

### 7.2 Service 层

```java
// SystemConfigService.java
@Service
public class SystemConfigService {
    
    @Autowired
    private SystemConfigDAO systemConfigDAO;
    
    /**
     * 获取所有 Agent 配置
     */
    public List<SystemConfigDO> getAgentConfigs() {
        SystemConfigDOExample example = new SystemConfigDOExample();
        example.createCriteria().andConfigKeyLike("agent.%");
        return systemConfigDAO.selectByExample(example);
    }
    
    /**
     * 更新配置
     */
    @Transactional
    public void updateConfig(String configKey, String configValue) {
        SystemConfigDOExample example = new SystemConfigDOExample();
        example.createCriteria().andConfigKeyEqualTo(configKey);
        
        List<SystemConfigDO> configs = systemConfigDAO.selectByExample(example);
        
        if (configs.isEmpty()) {
            // 创建新配置
            SystemConfigDO config = new SystemConfigDO();
            config.setConfigKey(configKey);
            config.setConfigValue(configValue);
            config.setConfigType("string");
            config.setCreatedAt(new Date());
            config.setUpdatedAt(new Date());
            systemConfigDAO.insert(config);
        } else {
            // 更新现有配置
            SystemConfigDO config = configs.get(0);
            config.setConfigValue(configValue);
            config.setUpdatedAt(new Date());
            systemConfigDAO.updateByPrimaryKeySelective(config);
        }
        
        // 通知 Python Agent 配置已更新
        notifyConfigChange(configKey);
    }
    
    /**
     * 通知配置变更
     */
    private void notifyConfigChange(String configKey) {
        // 方案 1: 通过 Redis 发布消息
        // redisTemplate.convertAndSend("config:update", configKey);
        
        // 方案 2: 通过 HTTP 调用 Python Agent
        // restTemplate.post("http://localhost:8000/api/config/reload", ...);
        
        // 方案 3: 设置标志位，Python 定期轮询
        // 暂时不实现，Python 每次创建 Agent 时都会重新加载配置
    }
}
```

### 7.3 Controller 层

```java
// SystemConfigController.java
@RestController
@RequestMapping("/api/config")
@RequireRole("admin")
public class SystemConfigController {
    
    @Autowired
    private SystemConfigService systemConfigService;
    
    /**
     * 获取 Agent 配置列表
     */
    @PostMapping("/list")
    public BaseResult<List<SystemConfigVO>> getConfigList() {
        try {
            List<SystemConfigDO> configs = systemConfigService.getAgentConfigs();
            List<SystemConfigVO> vos = configs.stream()
                .map(this::convertToVO)
                .collect(Collectors.toList());
            return BaseResult.success(vos);
        } catch (Exception e) {
            return BaseResult.error(e.getMessage());
        }
    }
    
    /**
     * 更新配置
     */
    @PostMapping("/update")
    public BaseResult<Void> updateConfig(@RequestBody UpdateConfigRequest request) {
        try {
            systemConfigService.updateConfig(
                request.getConfigKey(), 
                request.getConfigValue()
            );
            return BaseResult.success(null);
        } catch (Exception e) {
            return BaseResult.error(e.getMessage());
        }
    }
}
```

---

## 8. 配置同步方案对比

### 方案 1: 实时通知（Redis Pub/Sub）

**流程**：
```
Spring Boot 更新配置
   ↓
发布 Redis 消息
   ↓
Python Agent 订阅消息
   ↓
清除 agent_pool
   ↓
下次请求使用新配置
```

**优点**：
- ✅ 实时同步
- ✅ 支持多实例

**缺点**：
- ❌ 需要 Redis
- ❌ 增加复杂度

### 方案 2: 定期轮询

**流程**：
```
Python Agent 每 60 秒查询数据库
   ↓
检查配置是否变更
   ↓
如果变更，清除 agent_pool
   ↓
下次请求使用新配置
```

**优点**：
- ✅ 简单
- ✅ 无需额外组件

**缺点**：
- ❌ 延迟（最多 60 秒）
- ❌ 数据库查询开销

### 方案 3: 按需加载（推荐）

**流程**：
```
每次创建 Agent 时
   ↓
查询数据库获取最新配置
   ↓
检查 agent_pool 中的配置
   ↓
如果配置变更，创建新实例
   ↓
否则返回现有实例
```

**优点**：
- ✅ 简单可靠
- ✅ 配置变更立即生效
- ✅ 无需额外组件

**缺点**：
- ⚠️ 每次请求都查询数据库（可以用缓存优化）

---

## 9. 前端管理界面

### 9.1 配置管理页面

**路径**: `/config/model`

**功能**：
- 查看所有 Agent 配置
- 编辑配置值
- 测试配置（发送测试消息）
- 重置为默认值

### 9.2 配置项分组

#### 基础配置
- LLM 模型名称
- LLM 提供商
- 温度参数

#### 高级配置
- 超时时间
- 工具检索开关
- 商业模式开关

#### 自定义模型配置
- Base URL
- API Key
- Source

### 9.3 UI 设计

```
┌────────────────────────────────────────────────┐
│              Agent 配置管理                     │
├────────────────────────────────────────────────┤
│                                                │
│  基础配置                                       │
│  ┌──────────────────────────────────────────┐ │
│  │ LLM 模型:  [claude-sonnet-4-5        ▼] │ │
│  │ 提供商:    [Anthropic                ▼] │ │
│  │ 温度:      [0.7                        ] │ │
│  └──────────────────────────────────────────┘ │
│                                                │
│  高级配置                                       │
│  ┌──────────────────────────────────────────┐ │
│  │ 超时时间:  [600] 秒                       │ │
│  │ 工具检索:  [✓] 启用                       │ │
│  │ 商业模式:  [ ] 启用                       │ │
│  └──────────────────────────────────────────┘ │
│                                                │
│  自定义模型（可选）                             │
│  ┌──────────────────────────────────────────┐ │
│  │ Base URL:  [http://localhost:8000/v1   ] │ │
│  │ API Key:   [********************       ] │ │
│  └──────────────────────────────────────────┘ │
│                                                │
│  [测试配置]  [保存]  [重置为默认值]             │
└────────────────────────────────────────────────┘
```

---

## 10. 配置变更通知方案

### 10.1 简单方案（推荐）

**实现**：
- Python Agent 每次创建实例时查询数据库
- 比较配置是否变更
- 如果变更，创建新实例

**优点**：
- ✅ 简单可靠
- ✅ 无需额外组件
- ✅ 配置立即生效

**缺点**：
- ⚠️ 每次查询数据库（可以用缓存）

### 10.2 Redis 方案（高级）

**实现**：
```python
# Python Agent 订阅 Redis
import redis

redis_client = redis.Redis(host='localhost', port=6379)
pubsub = redis_client.pubsub()
pubsub.subscribe('config:update')

# 后台线程监听
def config_listener():
    for message in pubsub.listen():
        if message['type'] == 'message':
            config_key = message['data']
            # 清除 agent_pool
            agent_pool.clear()
            print(f"配置已更新: {config_key}")
```

**优点**：
- ✅ 实时通知
- ✅ 支持多实例

**缺点**：
- ❌ 需要 Redis
- ❌ 增加复杂度

### 10.3 HTTP 回调方案

**实现**：
```java
// Spring Boot 更新配置后
restTemplate.post("http://localhost:8000/api/config/reload", configKey);
```

```python
# Python Agent 提供接口
@router.post("/api/config/reload")
async def reload_config(config_key: str):
    # 清除 agent_pool
    agent_pool.clear()
    return {"status": "ok"}
```

**优点**：
- ✅ 实时通知
- ✅ 无需 Redis

**缺点**：
- ⚠️ 需要 Python Agent 提供接口
- ⚠️ 多实例需要逐个通知

---

## 11. 推荐方案总结

### 11.1 配置存储
- ✅ 使用数据库存储（system_config 表）
- ✅ 支持用户级配置（user_config 表，可选）
- ✅ 代码中保留默认配置（BiomniConfig）

### 11.2 配置加载
- ✅ 每次创建 Agent 时查询数据库
- ✅ 优先级：用户配置 > 系统配置 > 默认配置
- ✅ 配置变更时清除旧实例

### 11.3 配置同步
- ✅ 按需加载（简单方案）
- ⚠️ 可选：添加 Redis 通知（高级方案）

### 11.4 前端管理
- ✅ 配置管理页面（/config/model）
- ✅ 支持编辑、测试、重置
- ✅ 敏感信息脱敏显示

---

## 12. 实现步骤

### 阶段 1: 数据库和基础功能（1小时）
1. 创建 `system_config` 表
2. 插入默认配置
3. 创建 Python 配置服务（ConfigService）
4. 更新 agent_service.py 使用配置

### 阶段 2: Spring Boot 后端（1小时）
1. 创建 SystemConfigDO 和 DAO
2. 创建 SystemConfigService
3. 创建 SystemConfigController
4. 实现配置 CRUD 接口

### 阶段 3: 前端管理界面（1.5小时）
1. 创建配置管理页面
2. 实现配置列表显示
3. 实现配置编辑功能
4. 实现测试和重置功能

### 阶段 4: 配置同步（可选，1小时）
1. 实现 Redis 通知（如果需要）
2. 或实现 HTTP 回调
3. 或使用按需加载（无需额外工作）

**总计**: 3.5 - 4.5 小时

---

## 13. 配置示例

### 13.1 OpenAI GPT-4

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

**环境变量**：
```bash
OPENAI_API_KEY=sk-...
```

### 13.2 Anthropic Claude

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

**环境变量**：
```bash
ANTHROPIC_API_KEY=sk-ant-...
```

### 13.3 Ollama 本地模型

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

**无需 API Key**

### 13.4 自定义模型服务

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

## 14. 安全考虑

### 14.1 敏感信息保护

**API Key 存储**：
- ✅ 不存储在数据库（使用环境变量）
- ✅ 前端显示时脱敏（`sk-***...1234`）
- ✅ 只有管理员可以查看和修改

**自定义模型 API Key**：
- ⚠️ 如果需要存储在数据库，必须加密
- ✅ 使用 `is_sensitive` 标记
- ✅ 前端显示时脱敏

### 14.2 配置验证

**后端验证**：
```java
// 验证 LLM 模型名称
if (!isValidLLMModel(configValue)) {
    throw new RuntimeException("无效的 LLM 模型名称");
}

// 验证 Source
if (!Arrays.asList("OpenAI", "Anthropic", "Ollama", ...).contains(configValue)) {
    throw new RuntimeException("无效的 LLM 提供商");
}

// 验证 Temperature
float temp = Float.parseFloat(configValue);
if (temp < 0 || temp > 2) {
    throw new RuntimeException("温度参数必须在 0-2 之间");
}
```

**Python 验证**：
```python
# 在创建 Agent 前验证配置
def validate_config(config: dict):
    # 验证 temperature
    if 'temperature' in config:
        temp = config['temperature']
        if not (0 <= temp <= 2):
            raise ValueError("Temperature must be between 0 and 2")
    
    # 验证 source
    if 'source' in config:
        valid_sources = ['OpenAI', 'Anthropic', 'Ollama', 'Gemini', 'Groq', 'Bedrock', 'Custom']
        if config['source'] not in valid_sources:
            raise ValueError(f"Invalid source: {config['source']}")
    
    # 验证 Custom 模型必需参数
    if config.get('source') == 'Custom':
        if not config.get('base_url'):
            raise ValueError("base_url is required for Custom source")
```

---

## 15. 测试方案

### 15.1 配置加载测试

```python
# 测试默认配置
config = ConfigService.get_agent_config(db, user_id=None)
assert config['llm'] == 'claude-sonnet-4-5'

# 测试系统配置覆盖
# 在数据库中设置 agent.llm = 'gpt-4o'
config = ConfigService.get_agent_config(db, user_id=None)
assert config['llm'] == 'gpt-4o'

# 测试用户配置覆盖
# 在数据库中设置用户1的 agent.llm = 'llama3.1:70b'
config = ConfigService.get_agent_config(db, user_id=1)
assert config['llm'] == 'llama3.1:70b'
```

### 15.2 配置变更测试

```python
# 1. 创建 Agent（使用配置 A）
agent1 = AgentService.get_or_create_agent(user_id=1, db=db)

# 2. 更新配置（配置 B）
systemConfigService.updateConfig('agent.llm', 'gpt-4o')

# 3. 再次获取 Agent（应该使用配置 B）
agent2 = AgentService.get_or_create_agent(user_id=1, db=db)

# 4. 验证是新实例
assert agent1 is not agent2
```

### 15.3 模型切换测试

```bash
# 测试不同模型
# 1. OpenAI
curl -X POST http://localhost:8083/api/config/update \
  -d '{"configKey": "agent.llm", "configValue": "gpt-4o"}'

# 2. Anthropic
curl -X POST http://localhost:8083/api/config/update \
  -d '{"configKey": "agent.llm", "configValue": "claude-3-5-sonnet-20241022"}'

# 3. Ollama
curl -X POST http://localhost:8083/api/config/update \
  -d '{"configKey": "agent.llm", "configValue": "llama3.1:70b"}'
```

---

## 16. 总结

### 核心设计原则
1. ✅ **简单优先**：使用按需加载，避免过度设计
2. ✅ **安全第一**：敏感信息不存储在数据库
3. ✅ **灵活扩展**：支持系统级和用户级配置
4. ✅ **向后兼容**：保持现有代码可用

### 推荐实现顺序
1. **阶段 1**：数据库 + Python 配置服务（核心）
2. **阶段 2**：Spring Boot 后端 API（管理）
3. **阶段 3**：前端管理界面（可视化）
4. **阶段 4**：配置同步优化（可选）

### 预期效果
- ✅ 管理员可以在后台动态调整 LLM 模型
- ✅ 支持多种 LLM 提供商（OpenAI、Anthropic、Ollama 等）
- ✅ 配置变更立即生效（下次请求）
- ✅ 支持用户级配置（可选）
- ✅ 安全可靠，易于维护

---

**文档版本**: v1.0  
**创建时间**: 2025-01-20  
**维护者**: Biomni Team  
**状态**: 方案设计，待评审
