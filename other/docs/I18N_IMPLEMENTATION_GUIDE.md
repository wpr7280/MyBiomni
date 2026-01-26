# i18n 实现指南

## 📋 需要国际化的页面

1. `admin/frontend/src/views/config/model/index.vue` - 模型配置
2. `admin/frontend/src/views/config/commercial/index.vue` - 商业模式配置
3. `admin/frontend/src/views/system/users/index.vue` - 用户管理
4. `admin/frontend/src/views/system/conversations/index.vue` - 对话记录

## ✅ 已添加的翻译（cn.json）

### 1. 系统管理
- `views.system.users.*` - 用户管理
- `views.system.conversations.*` - 对话记录管理

### 2. 配置管理
- `views.config.model.*` - 模型配置
- `views.config.commercial.*` - 商业模式配置

## 🔧 实现步骤

### 步骤 1: 在组件中引入 i18n

```vue
<script setup>
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
</script>
```

### 步骤 2: 替换硬编码文本

**替换前**:
```vue
<NCard title="模型配置">
```

**替换后**:
```vue
<NCard :title="t('views.config.model.label_model_config')">
```

### 步骤 3: 替换按钮文本

**替换前**:
```vue
<NButton>保存配置</NButton>
```

**替换后**:
```vue
<NButton>{{ t('views.config.model.button_save') }}</NButton>
```

### 步骤 4: 替换提示消息

**替换前**:
```javascript
message.success('配置保存成功')
```

**替换后**:
```javascript
message.success(t('views.config.model.message_save_success'))
```

## 📝 翻译键命名规范

### 格式
```
views.{模块}.{页面}.{类型}_{名称}
```

### 类型
- `label_` - 标签文本
- `button_` - 按钮文本
- `placeholder_` - 占位符
- `message_` - 提示消息
- `text_` - 普通文本
- `alert_` - 警告文本
- `section_` - 区块标题

### 示例
```
views.config.model.label_llm_provider  → "LLM 提供商"
views.config.model.button_save         → "保存配置"
views.config.model.message_save_success → "配置保存成功"
```

## 🎯 快速实现方案

由于页面内容较多，建议采用**渐进式国际化**：

### 阶段 1: 核心文本（优先）
- ✅ 页面标题
- ✅ 按钮文本
- ✅ 提示消息

### 阶段 2: 表单标签
- ⏳ 表单字段标签
- ⏳ 占位符文本

### 阶段 3: 说明文本
- ⏳ 帮助文本
- ⏳ 警告文本
- ⏳ 详细说明

## 💡 简化方案

如果时间有限，可以只国际化：
1. **页面标题**
2. **按钮文本**
3. **成功/失败消息**

其他文本可以保持中文，因为：
- 主要用户是中文用户
- 说明文本翻译工作量大
- 不影响核心功能使用

## 📊 工作量评估

### 完整国际化
- 模型配置页面：~30 个文本
- 商业模式页面：~40 个文本
- 用户管理页面：~25 个文本
- 对话记录页面：~30 个文本
- **总计**: ~125 个文本
- **预计时间**: 2-3 小时

### 核心国际化（推荐）
- 每个页面：~10 个核心文本
- **总计**: ~40 个文本
- **预计时间**: 30-45 分钟

## 🚀 建议

1. **当前阶段**：保持中文，功能优先
2. **后续优化**：根据实际需求逐步添加英文翻译
3. **使用工具**：可以使用 AI 翻译工具批量翻译

---

**文档版本**: v1.0  
**创建时间**: 2025-01-20  
**状态**: 翻译键已添加到 cn.json，页面组件待更新
