<script setup>
import { ref, onMounted, h } from 'vue'
import { NCard, NIcon, NSwitch, NButton, NAlert, NTable, NTag, NSpace, NSpin } from 'naive-ui'
import CommonPage from '@/components/page/CommonPage.vue'
import { useMessage } from 'naive-ui'
import api from '@/api'

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
  { title: '数据集', key: 'name', width: 200 },
  { title: '许可证', key: 'license', width: 200 },
  { 
    title: '商业使用', 
    key: 'commercial',
    width: 150,
    render: (row) => {
      const type = row.commercial.includes('✅') ? 'success' : row.commercial.includes('⚠️') ? 'warning' : 'error'
      return h(NTag, { type, size: 'small' }, { default: () => row.commercial })
    }
  },
  { 
    title: '风险等级', 
    key: 'risk',
    width: 100,
    render: (row) => {
      const typeMap = { '低': 'success', '中': 'warning', '高': 'error' }
      return h(NTag, { type: typeMap[row.risk], size: 'small' }, { default: () => row.risk })
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
    message.error('加载配置失败')
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
    message.success('配置保存成功')
  } catch (error) {
    message.error('保存失败')
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
        <NCard class="commercial-card" title="商业模式配置">
          <template #header-extra>
            <NButton type="primary" :loading="saving" @click="saveConfig">
              <template #icon>
                <NIcon>
                  <svg viewBox="0 0 24 24">
                    <path fill="currentColor" d="M17 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14c1.1 0 2-.9 2-2V7l-4-4zm2 16H5V5h11.17L19 7.83V19zm-7-7c-1.66 0-3 1.34-3 3s1.34 3 3 3s3-1.34 3-3s-1.34-3-3-3zM6 6h9v4H6z"/>
                  </svg>
                </NIcon>
              </template>
              保存配置
            </NButton>
          </template>

          <!-- 风险警告 -->
          <NAlert type="error" title="⚠️ 重要法律声明" style="margin-bottom: 24px;">
            <div style="line-height: 1.8;">
              <p style="margin-bottom: 12px; font-weight: 600;">
                在启用或禁用商业模式前，请仔细阅读以下内容：
              </p>
              <ul style="margin: 0 0 12px 20px;">
                <li>部分数据集仅授权用于<strong>非商业用途</strong>（学术研究、教育等）</li>
                <li>在商业环境中使用这些数据集可能<strong>违反许可协议</strong></li>
                <li>违反许可协议可能导致<strong>法律责任和经济损失</strong></li>
                <li>启用商业模式后，系统将<strong>自动排除</strong>非商业授权的数据集</li>
              </ul>
              <p style="margin-top: 12px; padding: 12px; background: #fff1f0; border-left: 3px solid #ff4d4f; font-weight: 600;">
                ⚠️ 使用风险由您自行承担。建议在使用前咨询法律顾问，确保符合所有适用的许可协议。
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
                  商业模式
                </div>
                <div style="font-size: 13px; color: #666;">
                  启用后仅使用商业授权的数据集，自动排除非商业数据集
                </div>
              </div>
              <NSwitch 
                v-model:value="commercialMode"
                size="large"
              >
                <template #checked>已启用</template>
                <template #unchecked>已禁用</template>
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
              <strong>商业模式已启用</strong><br/>
              系统将仅使用具有商业授权的数据集（{{ datasetLicenses.filter(d => d.commercial.includes('✅')).length }} 个可用）
            </div>
            <div v-else>
              <strong>学术模式（默认）</strong><br/>
              系统将使用所有数据集（{{ datasetLicenses.length }} 个），包括仅限非商业使用的数据集
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
              数据集许可证信息
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
              📚 商业模式说明
            </div>
            <div style="font-size: 13px; line-height: 1.8; color: #595959;">
              <p style="margin-bottom: 8px;">
                <strong>商业模式启用时：</strong>
              </p>
              <ul style="margin: 0 0 12px 20px;">
                <li>系统自动排除标记为"仅非商业"的数据集</li>
                <li>仅使用明确允许商业使用的数据集</li>
                <li>降低许可证合规风险</li>
                <li>可能影响某些功能的可用性</li>
              </ul>
              
              <p style="margin-bottom: 8px;">
                <strong>商业模式禁用时（学术模式）：</strong>
              </p>
              <ul style="margin: 0 0 12px 20px;">
                <li>可以使用所有数据集</li>
                <li>适用于学术研究、教育等非商业场景</li>
                <li>功能完整，数据集最全</li>
                <li>不适用于商业产品或服务</li>
              </ul>

              <p style="margin-top: 16px; padding: 12px; background: #fff; border-radius: 4px; border: 1px solid #d9d9d9;">
                <strong>⚖️ 法律建议：</strong>
                在商业环境中使用 Biomni 前，请咨询法律顾问，审查所有相关数据集的许可协议，确保合规使用。
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
