<script setup>
import { ref, onMounted, h } from 'vue'
import { NCard, NIcon, NSwitch, NButton, NAlert, NTable, NTag, NSpace, NSpin } from 'naive-ui'
import CommonPage from '@/components/page/CommonPage.vue'
import { useMessage } from 'naive-ui'
import { useI18n } from 'vue-i18n'
import api from '@/api'

const { t } = useI18n()
const message = useMessage()
const loading = ref(false)
const saving = ref(false)
const commercialMode = ref(false)

// 数据集许可证信息
const datasetLicenses = [
  { name: 'COSMIC', license: '需要商业许可证', commercial: '❌ 需要授权', risk: '高' },
  { name: 'BindingDB', license: 'Custom (非商业)', commercial: '❌ 需要授权', risk: '高' },
  { name: 'Broad Repurposing Hub', license: 'CC BY 4.0', commercial: '✅ 允许', risk: '低' },
  { name: 'DDInter', license: 'CC BY-NC-SA 4.0', commercial: '❌ 仅非商业', risk: '高' },
  { name: 'DisGeNET', license: 'CC BY-NC-SA 4.0', commercial: '❌ 仅非商业', risk: '高' },
  { name: 'Enamine', license: 'Proprietary', commercial: '❌ 需要授权', risk: '高' },
  { name: 'Gene Ontology', license: 'CC BY 4.0', commercial: '✅ 允许', risk: '低' },
  { name: 'GTEx', license: 'dbGaP 受控访问', commercial: '⚠️ 需要授权', risk: '中' },
  { name: 'Human Protein Atlas', license: 'CC BY-SA 3.0', commercial: '✅ 允许', risk: '低' },
  { name: 'MSigDB', license: 'Custom', commercial: '❌ 需要授权', risk: '高' },
  { name: 'OMIM', license: 'Custom', commercial: '❌ 需要授权', risk: '高' },
  { name: 'BioGRID', license: 'OSL 3.0', commercial: '✅ 允许', risk: '低' },
  { name: 'DepMap', license: 'CC BY 4.0', commercial: '✅ 允许', risk: '低' },
  { name: 'Genebass', license: 'ODC-By v1.0', commercial: '✅ 允许', risk: '低' },
  { name: 'GWAS Catalog', license: 'Apache 2.0', commercial: '✅ 允许', risk: '低' },
  { name: 'HPO', license: 'Custom (免费)', commercial: '✅ 允许', risk: '低' },
  { name: 'McPAS-TCR', license: 'CC BY-NC-SA 4.0', commercial: '❌ 仅非商业', risk: '高' },
  { name: 'miRDB', license: 'Custom (非商业)', commercial: '❌ 仅非商业', risk: '高' },
  { name: 'miRTarBase', license: 'CC BY-NC 4.0', commercial: '❌ 仅非商业', risk: '高' }
]

const columns = [
  { title: () => t('views.config.commercial.table_column_dataset'), key: 'name', width: 200 },
  { title: () => t('views.config.commercial.table_column_license'), key: 'license', width: 200 },
  { 
    title: () => t('views.config.commercial.table_column_commercial'), 
    key: 'commercial',
    width: 150,
    render: (row) => {
      const type = row.commercial.includes('✅') ? 'success' : row.commercial.includes('⚠️') ? 'warning' : 'error'
      return h(NTag, { type, size: 'small' }, { default: () => row.commercial })
    }
  },
  { 
    title: () => t('views.config.commercial.table_column_risk'), 
    key: 'risk',
    width: 100,
    render: (row) => {
      const typeMap = { '低': 'success', '中': 'warning', '高': 'error' }
      const textMap = { 
        '低': t('views.config.commercial.text_risk_low'), 
        '中': t('views.config.commercial.text_risk_medium'), 
        '高': t('views.config.commercial.text_risk_high') 
      }
      return h(NTag, { type: typeMap[row.risk], size: 'small' }, { default: () => textMap[row.risk] })
    }
  }
]

// 加载配置
async function loadConfig() {
  loading.value = true
  try {
    const res = await api.getConfigList()
    if (res.code === 200 && res.data) {
      const config = res.data.find(c => c.configKey === 'agent.commercial_mode')
      if (config) {
        commercialMode.value = config.configValue === 'true'
      }
    }
  } catch (error) {
    message.error(t('views.config.commercial.message_load_failed'))
  } finally {
    loading.value = false
  }
}

// 保存配置
async function saveConfig() {
  saving.value = true
  try {
    await api.updateConfig({
      configKey: 'agent.commercial_mode',
      configValue: commercialMode.value ? 'true' : 'false'
    })
    message.success(t('views.config.commercial.message_save_success'))
  } catch (error) {
    message.error(t('views.config.commercial.message_save_failed'))
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadConfig()
})

</script>

<template>
  <CommonPage :show-header="false">
    <div class="commercial-container">
      <NSpin :show="loading">
        <NCard class="commercial-card" :title="t('views.config.commercial.label_commercial_mode')">
          <template #header-extra>
            <NButton type="primary" :loading="saving" @click="saveConfig">
              <template #icon>
                <NIcon>
                  <svg viewBox="0 0 24 24">
                    <path fill="currentColor" d="M17 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14c1.1 0 2-.9 2-2V7l-4-4zm2 16H5V5h11.17L19 7.83V19zm-7-7c-1.66 0-3 1.34-3 3s1.34 3 3 3s3-1.34 3-3s-1.34-3-3-3zM6 6h9v4H6z"/>
                  </svg>
                </NIcon>
              </template>
              {{ t('views.config.commercial.button_save') }}
            </NButton>
          </template>

          <!-- 风险警告 -->
          <NAlert type="error" :title="t('views.config.commercial.alert_legal_title')" style="margin-bottom: 24px;">
            <div style="line-height: 1.8;">
              <p style="margin-bottom: 12px; font-weight: 600;">
                {{ t('views.config.commercial.alert_legal_intro') }}
              </p>
              <ul style="margin: 0 0 12px 20px;">
                <li v-html="t('views.config.commercial.alert_legal_item_1')"></li>
                <li v-html="t('views.config.commercial.alert_legal_item_2')"></li>
                <li v-html="t('views.config.commercial.alert_legal_item_3')"></li>
                <li v-html="t('views.config.commercial.alert_legal_item_4')"></li>
              </ul>
              <p style="margin-top: 12px; padding: 12px; background: #fff1f0; border-left: 3px solid #ff4d4f; font-weight: 600;">
                {{ t('views.config.commercial.alert_legal_risk') }}
              </p>
            </div>
          </NAlert>

          <!-- 商业模式开关 -->
          <div style="padding: 24px; background: #fafafa; border-radius: 8px; margin-bottom: 24px;">
            <div style="display: flex; align-items: center; justify-content: space-between;">
              <div>
                <div style="font-size: 16px; font-weight: 600; margin-bottom: 8px;">
                  <NIcon size="20" color="#1890ff" style="vertical-align: middle; margin-right: 8px;">
                    <svg viewBox="0 0 24 24">
                      <path fill="currentColor" d="M20 6h-2.18c.11-.31.18-.65.18-1a2.996 2.996 0 0 0-5.5-1.65l-.5.67l-.5-.68C10.96 2.54 10.05 2 9 2C7.34 2 6 3.34 6 5c0 .35.07.69.18 1H4c-1.11 0-1.99.89-1.99 2L2 19c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V8c0-1.11-.89-2-2-2zm-5-2c.55 0 1 .45 1 1s-.45 1-1 1s-1-.45-1-1s.45-1 1-1zM9 4c.55 0 1 .45 1 1s-.45 1-1 1s-1-.45-1-1s.45-1 1-1zm11 15H4v-2h16v2zm0-5H4V8h5.08L7 10.83L8.62 12L12 7.4l3.38 4.6L17 10.83L14.92 8H20v6z"/>
                    </svg>
                  </NIcon>
                  {{ t('views.config.commercial.label_switch') }}
                </div>
                <div style="font-size: 13px; color: #666;">
                  {{ t('views.config.commercial.text_switch_desc') }}
                </div>
              </div>
              <NSwitch 
                v-model:value="commercialMode"
                size="large"
              >
                <template #checked>{{ t('views.config.commercial.text_switch_enabled') }}</template>
                <template #unchecked>{{ t('views.config.commercial.text_switch_disabled') }}</template>
              </NSwitch>
            </div>
          </div>

          <!-- 当前状态说明 -->
          <NAlert 
            :type="commercialMode ? 'success' : 'info'" 
            style="margin-bottom: 24px;"
          >
            <template #icon>
              <NIcon size="18">
                <svg viewBox="0 0 24 24">
                  <path fill="currentColor" d="M11 7h2v2h-2zm0 4h2v6h-2zm1-9C6.48 2 2 6.48 2 12s4.48 10 10 10s10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8s8 3.59 8 8s-3.59 8-8 8z"/>
                </svg>
              </NIcon>
            </template>
            <div v-if="commercialMode">
              <strong>{{ t('views.config.commercial.text_mode_enabled_title') }}</strong><br/>
              {{ t('views.config.commercial.text_mode_enabled_desc', { count: datasetLicenses.filter(d => d.commercial.includes('✅')).length }) }}
            </div>
            <div v-else>
              <strong>{{ t('views.config.commercial.text_mode_disabled_title') }}</strong><br/>
              {{ t('views.config.commercial.text_mode_disabled_desc', { count: datasetLicenses.length }) }}
            </div>
          </NAlert>

          <!-- 数据集许可证列表 -->
          <div style="margin-top: 32px;">
            <div style="font-size: 16px; font-weight: 600; margin-bottom: 16px; display: flex; align-items: center; gap: 8px;">
              <NIcon size="18" color="#722ed1">
                <svg viewBox="0 0 24 24">
                  <path fill="currentColor" d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/>
                </svg>
              </NIcon>
              {{ t('views.config.commercial.section_dataset_title') }}
            </div>
            
            <NTable 
              :columns="columns" 
              :data="datasetLicenses"
              :bordered="true"
              :single-line="false"
              size="small"
              style="margin-bottom: 24px;"
            />
          </div>

          <!-- 说明文档 -->
          <div style="margin-top: 32px; padding: 20px; background: #f5f7fa; border-radius: 8px; border-left: 4px solid #1890ff;">
            <div style="font-size: 14px; font-weight: 600; margin-bottom: 12px; color: #262626;">
              {{ t('views.config.commercial.section_explanation_title') }}
            </div>
            <div style="font-size: 13px; line-height: 1.8; color: #595959;">
              <p style="margin-bottom: 8px;">
                <strong>{{ t('views.config.commercial.text_when_enabled_title') }}</strong>
              </p>
              <ul style="margin: 0 0 12px 20px;">
                <li>{{ t('views.config.commercial.text_when_enabled_1') }}</li>
                <li>{{ t('views.config.commercial.text_when_enabled_2') }}</li>
                <li>{{ t('views.config.commercial.text_when_enabled_3') }}</li>
                <li>{{ t('views.config.commercial.text_when_enabled_4') }}</li>
              </ul>
              
              <p style="margin-bottom: 8px;">
                <strong>{{ t('views.config.commercial.text_when_disabled_title') }}</strong>
              </p>
              <ul style="margin: 0 0 12px 20px;">
                <li>{{ t('views.config.commercial.text_when_disabled_1') }}</li>
                <li>{{ t('views.config.commercial.text_when_disabled_2') }}</li>
                <li>{{ t('views.config.commercial.text_when_disabled_3') }}</li>
                <li>{{ t('views.config.commercial.text_when_disabled_4') }}</li>
              </ul>

              <p style="margin-top: 16px; padding: 12px; background: #fff; border-radius: 4px; border: 1px solid #d9d9d9;">
                <strong>{{ t('views.config.commercial.text_legal_advice_title') }}</strong>
                {{ t('views.config.commercial.text_legal_advice_content') }}
              </p>
            </div>
          </div>
        </NCard>
      </NSpin>
    </div>
  </CommonPage>
</template>

<style scoped>
.commercial-container {
  padding: 20px 24px;
}

.commercial-card {
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.commercial-card :deep(.n-card-header) {
  padding: 16px 24px;
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
  border-bottom: 1px solid #f0f0f0;
}

@media (max-width: 768px) {
  .commercial-container {
    padding: 12px 16px;
  }
}
</style>
