# 需要添加的 i18n 翻译

## cn.json 需要添加的键

```json
"views": {
  "config": {
    "model": {
      // ... 现有的键 ...
      
      // 区块标题
      "section_api_key": "API Key 配置",
      "section_custom": "自定义模型配置",
      "section_advanced": "高级配置",
      "section_preview": "配置预览",
      
      // 表单标签
      "label_llm_provider": "LLM 提供商",
      "label_model_name": "模型名称",
      "label_temperature": "温度参数",
      "label_timeout": "超时时间（秒）",
      "label_tool_retriever": "工具检索",
      "label_base_url": "Base URL",
      "label_api_key": "API Key",
      
      // 占位符
      "placeholder_provider": "选择 LLM 提供商",
      "placeholder_model": "输入模型名称",
      "placeholder_base_url": "http://localhost:8000/v1",
      "placeholder_api_key": "输入自定义模型的 API Key",
      
      // 提示文本
      "text_recommended": "推荐模型：",
      "text_temp_hint": "0-2，越高越随机",
      "text_timeout_hint": "60-3600秒",
      "text_retriever_hint": "启用后会根据问题自动选择相关工具",
      
      // Bedrock 认证方式
      "text_auth_method_1": "方式 1: Access Key 认证",
      "text_auth_method_2": "方式 2: Bearer Token 认证",
      "text_bedrock_hint": "从 AWS IAM 获取。Region 必填，然后选择 Access Key 或 Bearer Token 认证",
      
      // Azure
      "text_azure_hint": "从 Azure Portal 获取",
      
      // 其他提供商
      "text_openai_hint": "从 https://platform.openai.com/api-keys 获取",
      "text_anthropic_hint": "从 https://console.anthropic.com/settings/keys 获取",
      "text_gemini_hint": "从 https://aistudio.google.com/app/apikey 获取",
      "text_groq_hint": "从 https://console.groq.com/keys 获取"
    }
  }
}
```

## en.json 对应的英文翻译

```json
"views": {
  "config": {
    "model": {
      // Sections
      "section_api_key": "API Key Configuration",
      "section_custom": "Custom Model Configuration",
      "section_advanced": "Advanced Configuration",
      "section_preview": "Configuration Preview",
      
      // Labels
      "label_llm_provider": "LLM Provider",
      "label_model_name": "Model Name",
      "label_temperature": "Temperature",
      "label_timeout": "Timeout (seconds)",
      "label_tool_retriever": "Tool Retriever",
      "label_base_url": "Base URL",
      "label_api_key": "API Key",
      
      // Placeholders
      "placeholder_provider": "Select LLM Provider",
      "placeholder_model": "Enter model name",
      "placeholder_base_url": "http://localhost:8000/v1",
      "placeholder_api_key": "Enter custom model API Key",
      
      // Hints
      "text_recommended": "Recommended models:",
      "text_temp_hint": "0-2, higher is more random",
      "text_timeout_hint": "60-3600 seconds",
      "text_retriever_hint": "Automatically select relevant tools based on the question",
      
      // Bedrock auth methods
      "text_auth_method_1": "Method 1: Access Key Authentication",
      "text_auth_method_2": "Method 2: Bearer Token Authentication",
      "text_bedrock_hint": "Get from AWS IAM. Region is required, then choose Access Key or Bearer Token authentication",
      
      // Azure
      "text_azure_hint": "Get from Azure Portal",
      
      // Other providers
      "text_openai_hint": "Get from https://platform.openai.com/api-keys",
      "text_anthropic_hint": "Get from https://console.anthropic.com/settings/keys",
      "text_gemini_hint": "Get from https://aistudio.google.com/app/apikey",
      "text_groq_hint": "Get from https://console.groq.com/keys"
    }
  }
}
```

## Vue 组件需要修改的地方

### 1. apiKeyConfig computed 属性

将所有硬编码文本改为 `t()` 函数调用。

### 2. 模板中的硬编码文本

- "基础配置" → `{{ t('views.config.model.section_basic') }}`
- "API Key 配置" → `{{ t('views.config.model.section_api_key') }}`
- "推荐模型：" → `{{ t('views.config.model.text_recommended') }}`
- 等等...

---

**注意**: 由于修改较多，建议分步进行：
1. 先添加所有翻译键到 cn.json 和 en.json
2. 然后逐个替换 Vue 组件中的硬编码文本
3. 测试每个修改确保正常工作

**预计工作量**: 1-1.5 小时
