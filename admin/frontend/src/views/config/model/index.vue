<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { NCard, NForm, NFormItem, NInput, NSelect, NSwitch, NButton, NAlert, NIcon, NSpace, NPopconfirm, NInputNumber, NSpin } from 'naive-ui'
import CommonPage from '@/components/page/CommonPage.vue'
import { useMessage } from 'naive-ui'
import { useI18n } from 'vue-i18n'
import api from '@/api'

const { t } = useI18n()
const message = useMessage()
const loading = ref(false)
const saving = ref(false)

// 配置表单
const configForm = ref({
  'agent.llm': 'claude-sonnet-4-5',
  'agent.source': 'Anthropic',
  'agent.temperature': '0.7',
  'agent.max_tokens': '8192',
  'agent.timeout_seconds': '600',
  'agent.use_tool_retriever': 'true',
  'agent.commercial_mode': 'false',
  'agent.base_url': '',
  'agent.api_key': '',
  // LLM API Keys
  'llm.openai_api_key': '',
  'llm.anthropic_api_key': '',
  'llm.gemini_api_key': '',
  'llm.groq_api_key': '',
  'llm.azure_api_key': '',
  'llm.azure_endpoint': '',
  'llm.aws_region': 'us-east-1',
  'llm.aws_access_key_id': '',
  'llm.aws_secret_access_key': '',
  'llm.aws_bearer_token': ''
})

// LLM 提供商选项
const sourceOptions = [
  { label: 'OpenAI', value: 'OpenAI' },
  { label: 'Anthropic (Claude)', value: 'Anthropic' },
  { label: 'Ollama (本地)', value: 'Ollama' },
  { label: 'Google Gemini', value: 'Gemini' },
  { label: 'Groq', value: 'Groq' },
  { label: 'AWS Bedrock', value: 'Bedrock' },
  { label: 'Azure OpenAI', value: 'AzureOpenAI' },
  { label: '通义千问 (DashScope)', value: 'DashScope' },
  { label: '自定义模型', value: 'Custom' }
]

// 根据提供商显示推荐模型
const recommendedModels = computed(() => {
  const source = configForm.value['agent.source']
  const models = {
    'OpenAI': ['gpt-4o', 'gpt-4-turbo', 'gpt-4', 'gpt-3.5-turbo'],
    'Anthropic': ['claude-3-5-sonnet-20241022', 'claude-3-opus-20240229', 'claude-3-sonnet-20240229', 'claude-sonnet-4-5'],
    'Ollama': ['llama3.1:70b', 'llama3.1:8b', 'mistral', 'qwen2.5:72b', 'deepseek-r1:70b'],
    'Gemini': ['gemini-2.0-flash-exp', 'gemini-1.5-pro', 'gemini-1.5-flash'],
    'Groq': ['llama-3.3-70b-versatile', 'mixtral-8x7b-32768', 'llama-3.1-70b-versatile'],
    'Bedrock': ['anthropic.claude-3-5-sonnet-20241022-v2:0', 'anthropic.claude-3-opus-20240229-v1:0'],
    'AzureOpenAI': ['gpt-4o', 'gpt-4-turbo', 'gpt-35-turbo'],
    'DashScope': ['qwen-max', 'qwen-plus', 'qwen-turbo', 'qwen-long', 'qwen2.5-72b-instruct', 'qwen2.5-32b-instruct', 'qwen2.5-14b-instruct'],
    'Custom': []
  }
  return models[source] || []
})

// 是否显示自定义模型配置
const showCustomConfig = computed(() => {
  return configForm.value['agent.source'] === 'Custom'
})

// 根据提供商显示对应的 API Key 配置
const apiKeyConfig = computed(() => {
  const source = configForm.value['agent.source']
  
  const configs = {
    'OpenAI': {
      key: 'llm.openai_api_key',
      label: 'OpenAI API Key',
      placeholder: 'sk-...',
      hint: t('views.config.model.text_openai_hint')
    },
    'Anthropic': {
      key: 'llm.anthropic_api_key',
      label: 'Anthropic API Key',
      placeholder: 'sk-ant-...',
      hint: t('views.config.model.text_anthropic_hint')
    },
    'Gemini': {
      key: 'llm.gemini_api_key',
      label: 'Google Gemini API Key',
      placeholder: 'AI...',
      hint: t('views.config.model.text_gemini_hint')
    },
    'Groq': {
      key: 'llm.groq_api_key',
      label: 'Groq API Key',
      placeholder: 'gsk_...',
      hint: t('views.config.model.text_groq_hint')
    },
    'AzureOpenAI': {
      keys: ['llm.azure_api_key', 'llm.azure_endpoint'],
      labels: ['Azure API Key', 'Azure Endpoint'],
      placeholders: ['...', 'https://your-resource.openai.azure.com/'],
      hint: t('views.config.model.text_azure_hint')
    },
    'Bedrock': {
      keys: ['llm.aws_region', 'llm.aws_bearer_token'],
      labels: ['AWS Region', 'AWS Bearer Token'],
      placeholders: ['us-east-1', 'Bearer Token...'],
      hint: t('views.config.model.text_bedrock_hint')
    },
    'DashScope': {
      key: 'llm.dashscope_api_key',
      label: 'DashScope API Key',
      placeholder: 'sk-...',
      hint: t('views.config.model.text_dashscope_hint')
    }
  }
  
  return configs[source] || null
})

// 加载配置
async function loadConfigs() {
  loading.value = true
  try {
    const res = await api.getConfigList()
      
    if (res.code === 200 && res.data) {
      res.data.forEach(config => {
        configForm.value[config.configKey] = config.configValue || ''
      })
      // 确保温度参数是数字类型
      if (configForm.value['agent.temperature']) {
        configForm.value['agent.temperature'] = parseFloat(configForm.value['agent.temperature'])
      }
      // 确保 max_tokens 是数字类型
      if (configForm.value['agent.max_tokens']) {
        configForm.value['agent.max_tokens'] = parseInt(configForm.value['agent.max_tokens'])
      }
      // 确保超时时间是数字类型
      if (configForm.value['agent.timeout_seconds']) {
        configForm.value['agent.timeout_seconds'] = parseInt(configForm.value['agent.timeout_seconds'])
      }
    }
  } catch (error) {
    message.error(t('views.config.model.message_load_failed'))
  } finally {
    loading.value = false
  }
}

// 保存配置
async function saveConfigs() {
  saving.value = true
  try {
    // 转换数字类型为字符串
    const configsToSave = { ...configForm.value }
    configsToSave['agent.temperature'] = String(configsToSave['agent.temperature'])
    configsToSave['agent.max_tokens'] = String(configsToSave['agent.max_tokens'])
    configsToSave['agent.timeout_seconds'] = String(configsToSave['agent.timeout_seconds'])
    
    await api.batchUpdateConfig({ configs: configsToSave })
    message.success(t('views.config.model.message_save_success'))
  } catch (error) {
    message.error(t('views.config.model.message_save_failed') + ': ' + (error.message || ''))
  } finally {
    saving.value = false
  }
}

// 当提供商变更时，清空自定义配置
watch(() => configForm.value['agent.source'], (newSource, oldSource) => {
  if (oldSource === 'Custom' && newSource !== 'Custom') {
    configForm.value['agent.base_url'] = ''
    configForm.value['agent.api_key'] = ''
  }
})

onMounted(() => {
  loadConfigs()
})

</script>

<template>
  <CommonPage :show-header="false">
    <div class="config-container">
      <NSpin :show="loading">
        <NCard class="config-card" :title="t('views.config.model.label_model_config')">
          <template #header-extra>
            <NButton type="primary" :loading="saving" @click="saveConfigs">
              <template #icon>
                <NIcon>
                  <svg viewBox="0 0 24 24">
                    <path fill="currentColor" d="M17 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14c1.1 0 2-.9 2-2V7l-4-4zm2 16H5V5h11.17L19 7.83V19zm-7-7c-1.66 0-3 1.34-3 3s1.34 3 3 3s3-1.34 3-3s-1.34-3-3-3zM6 6h9v4H6z"/>
                  </svg>
                </NIcon>
              </template>
              {{ t('views.config.model.button_save') }}
            </NButton>
          </template>

          <!-- 提示信息 -->
          <NAlert type="info" style="margin-bottom: 24px;">
            <template #icon>
              <NIcon size="20">
                <svg viewBox="0 0 24 24">
                  <path fill="currentColor" d="M11 7h2v2h-2zm0 4h2v6h-2zm1-9C6.48 2 2 6.48 2 12s4.48 10 10 10s10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8s8 3.59 8 8s-3.59 8-8 8z"/>
                </svg>
              </NIcon>
            </template>
            {{ t('views.config.model.alert_config_notice') }}
          </NAlert>

          <NForm label-placement="left" label-width="140" style="max-width: 800px;">
            <!-- 基础配置 -->
            <div class="config-section">
              <div class="section-title">
                <NIcon size="18" color="#1890ff">
                  <svg viewBox="0 0 24 24">
                    <path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10s10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3s-3-1.34-3-3s1.34-3 3-3zm0 14.2a7.2 7.2 0 0 1-6-3.22c.03-1.99 4-3.08 6-3.08c1.99 0 5.97 1.09 6 3.08a7.2 7.2 0 0 1-6 3.22z"/>
                  </svg>
                </NIcon>
                <span>{{ t('views.config.model.section_basic') }}</span>
              </div>

              <NFormItem :label="t('views.config.model.label_llm_provider')">
                <NSelect 
                  v-model:value="configForm['agent.source']" 
                  :options="sourceOptions"
                  :placeholder="t('views.config.model.placeholder_provider')"
                />
              </NFormItem>

              <NFormItem :label="t('views.config.model.label_model_name')">
                <div style="width: 100%;">
                  <NInput 
                    v-model:value="configForm['agent.llm']" 
                    :placeholder="t('views.config.model.placeholder_model')"
                  />
                  <div v-if="recommendedModels.length > 0" style="margin-top: 8px;">
                    <div style="font-size: 12px; color: #999; margin-bottom: 4px;">{{ t('views.config.model.text_recommended_models') }}</div>
                    <NSpace size="small">
                      <NButton
                        v-for="model in recommendedModels"
                        :key="model"
                        size="tiny"
                        secondary
                        @click="configForm['agent.llm'] = model"
                      >
                        {{ model }}
                      </NButton>
                    </NSpace>
                  </div>
                </div>
              </NFormItem>

              <NFormItem :label="t('views.config.model.label_temperature')">
                <div style="display: flex; align-items: center; gap: 12px; width: 100%;">
                  <NInputNumber 
                    v-model:value="configForm['agent.temperature']" 
                    :min="0"
                    :max="2"
                    :step="0.1"
                    :precision="1"
                    :default-value="0.7"
                    style="flex: 1;"
                  />
                  <span style="font-size: 12px; color: #999;">{{ t('views.config.model.text_temperature_hint') }}</span>
                </div>
              </NFormItem>

              <NFormItem :label="t('views.config.model.label_max_tokens')">
                <div style="display: flex; align-items: center; gap: 12px; width: 100%;">
                  <NInputNumber 
                    v-model:value="configForm['agent.max_tokens']" 
                    :min="1024"
                    :max="200000"
                    :step="1024"
                    :default-value="8192"
                    style="flex: 1;"
                  />
                  <span style="font-size: 12px; color: #999;">{{ t('views.config.model.text_max_tokens_hint') }}</span>
                </div>
              </NFormItem>
            </div>

            <!-- API Key 配置（根据提供商显示） -->
            <div v-if="apiKeyConfig && !showCustomConfig" class="config-section">
              <div class="section-title">
                <NIcon size="18" color="#52c41a">
                  <svg viewBox="0 0 24 24">
                    <path fill="currentColor" d="M12.65 10A5.99 5.99 0 0 0 7 6c-3.31 0-6 2.69-6 6s2.69 6 6 6a5.99 5.99 0 0 0 5.65-4H17v4h4v-4h2v-4H12.65zM7 14c-1.1 0-2-.9-2-2s.9-2 2-2s2 .9 2 2s-.9 2-2 2z"/>
                  </svg>
                </NIcon>
                <span>{{ t('views.config.model.section_api_key') }}</span>
              </div>

              <!-- 单个 API Key -->
              <template v-if="apiKeyConfig.key">
                <NFormItem :label="apiKeyConfig.label">
                  <div style="width: 100%;">
                    <NInput 
                      v-model:value="configForm[apiKeyConfig.key]"
                      type="password"
                      show-password-on="click"
                      :placeholder="apiKeyConfig.placeholder"
                    />
                    <div style="font-size: 12px; color: #999; margin-top: 4px;">
                      {{ apiKeyConfig.hint }}
                    </div>
                  </div>
                </NFormItem>
              </template>

              <!-- Bedrock 分组显示 -->
              <template v-else-if="apiKeyConfig.groups">
                <div v-for="(group, groupIndex) in apiKeyConfig.groups" :key="groupIndex" style="margin-bottom: 20px;">
                  <div style="font-size: 13px; font-weight: 600; color: #595959; margin-bottom: 12px; padding: 8px 12px; background: #f5f7fa; border-radius: 6px;">
                    {{ group.title }}
                  </div>
                  <NFormItem 
                    v-for="(key, index) in group.keys" 
                    :key="key"
                    :label="group.labels[index]"
                  >
                    <div style="width: 100%;">
                      <NInput 
                        v-model:value="configForm[key]"
                        :type="key.includes('secret') || key.includes('key') || key.includes('token') ? 'password' : 'text'"
                        :show-password-on="key.includes('secret') || key.includes('key') || key.includes('token') ? 'click' : undefined"
                        :placeholder="group.placeholders[index]"
                      />
                    </div>
                  </NFormItem>
                </div>
                <div style="font-size: 12px; color: #999; margin-top: -12px; margin-bottom: 12px;">
                  {{ apiKeyConfig.hint }}
                </div>
              </template>

              <!-- 其他多配置项（Azure） -->
              <template v-else-if="apiKeyConfig.keys">
                <NFormItem 
                  v-for="(key, index) in apiKeyConfig.keys" 
                  :key="key"
                  :label="apiKeyConfig.labels[index]"
                >
                  <div style="width: 100%;">
                    <NInput 
                      v-model:value="configForm[key]"
                      :type="key.includes('secret') || key.includes('key') ? 'password' : 'text'"
                      :show-password-on="key.includes('secret') || key.includes('key') ? 'click' : undefined"
                      :placeholder="apiKeyConfig.placeholders[index]"
                    />
                  </div>
                </NFormItem>
                <div style="font-size: 12px; color: #999; margin-top: -12px; margin-bottom: 12px;">
                  {{ apiKeyConfig.hint }}
                </div>
              </template>
            </div>

            <!-- 自定义模型配置 -->
            <div v-if="showCustomConfig" class="config-section">
              <div class="section-title">
                <NIcon size="18" color="#52c41a">
                  <svg viewBox="0 0 24 24">
                    <path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10s10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5l1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                  </svg>
                </NIcon>
                <span>{{ t('views.config.model.section_custom') }}</span>
              </div>

              <NFormItem :label="t('views.config.model.label_base_url')">
                <NInput 
                  v-model:value="configForm['agent.base_url']" 
                  :placeholder="t('views.config.model.placeholder_base_url')"
                />
              </NFormItem>

              <NFormItem :label="t('views.config.model.label_api_key')">
                <NInput 
                  v-model:value="configForm['agent.api_key']"
                  type="password"
                  show-password-on="click"
                  :placeholder="t('views.config.model.placeholder_api_key')"
                />
              </NFormItem>
            </div>

            <!-- 高级配置 -->
            <div class="config-section">
              <div class="section-title">
                <NIcon size="18" color="#faad14">
                  <svg viewBox="0 0 24 24">
                    <path fill="currentColor" d="M19.14 12.94c.04-.3.06-.61.06-.94c0-.32-.02-.64-.07-.94l2.03-1.58a.49.49 0 0 0 .12-.61l-1.92-3.32a.488.488 0 0 0-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54a.484.484 0 0 0-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.05.3-.09.63-.09.94s.02.64.07.94l-2.03 1.58a.49.49 0 0 0-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6s3.6 1.62 3.6 3.6s-1.62 3.6-3.6 3.6z"/>
                  </svg>
                </NIcon>
                <span>{{ t('views.config.model.section_advanced') }}</span>
              </div>

              <NFormItem :label="t('views.config.model.label_timeout')">
                <div style="display: flex; align-items: center; gap: 12px; width: 100%;">
                  <NInputNumber 
                    v-model:value="configForm['agent.timeout_seconds']" 
                    :min="60"
                    :max="3600"
                    :step="60"
                    style="flex: 1;"
                  />
                  <span style="font-size: 12px; color: #999;">{{ t('views.config.model.text_timeout_hint') }}</span>
                </div>
              </NFormItem>

              <NFormItem :label="t('views.config.model.label_tool_retriever')">
                <div style="display: flex; align-items: center; gap: 12px;">
                  <NSwitch 
                    :value="configForm['agent.use_tool_retriever'] === 'true'"
                    @update:value="val => configForm['agent.use_tool_retriever'] = val ? 'true' : 'false'"
                  />
                  <span style="font-size: 12px; color: #666;">
                    {{ t('views.config.model.text_tool_retriever_hint') }}
                  </span>
                </div>
              </NFormItem>
            </div>

            <!-- 配置预览 -->
            <div class="config-section">
              <div class="section-title">
                <NIcon size="18" color="#722ed1">
                  <svg viewBox="0 0 24 24">
                    <path fill="currentColor" d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5s5 2.24 5 5s-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3s3-1.34 3-3s-1.34-3-3-3z"/>
                  </svg>
                </NIcon>
                <span>{{ t('views.config.model.section_preview') }}</span>
              </div>

              <div class="config-preview">
                <pre>{{ JSON.stringify({
                  llm: configForm['agent.llm'],
                  source: configForm['agent.source'],
                  temperature: parseFloat(configForm['agent.temperature']),
                  max_tokens: parseInt(configForm['agent.max_tokens']),
                  timeout_seconds: parseInt(configForm['agent.timeout_seconds']),
                  use_tool_retriever: configForm['agent.use_tool_retriever'] === 'true',
                  commercial_mode: configForm['agent.commercial_mode'] === 'true',
                  ...(showCustomConfig ? {
                    base_url: configForm['agent.base_url'],
                    api_key: configForm['agent.api_key'] ? '***' : ''
                  } : {})
                }, null, 2) }}</pre>
              </div>
            </div>
          </NForm>
        </NCard>
      </NSpin>
    </div>
  </CommonPage>
</template>

<style scoped>
.config-container {
  padding: 20px 24px;
}

.config-card {
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.config-card :deep(.n-card-header) {
  padding: 16px 24px;
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
  border-bottom: 1px solid #f0f0f0;
}

.config-section {
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid #f0f0f0;
}

.config-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #262626;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 2px solid #f0f0f0;
}

.config-preview {
  background: #f5f7fa;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  padding: 16px;
  font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
  font-size: 13px;
  line-height: 1.6;
  color: #262626;
  overflow-x: auto;
}

.config-preview pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-all;
}

@media (max-width: 768px) {
  .config-container {
    padding: 12px 16px;
  }
  
  .config-card :deep(.n-form) {
    max-width: none !important;
  }
}
</style>
