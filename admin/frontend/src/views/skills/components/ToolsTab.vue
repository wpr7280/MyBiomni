<script setup>
import { ref, onMounted } from 'vue'
import { NCard, NButton, NIcon, NSpace, NEmpty, NSpin, NInput, NCollapse, NCollapseItem, NTag } from 'naive-ui'
import { useMessage } from 'naive-ui'
import { useI18n } from 'vue-i18n'
import api from '@/api'

const { t } = useI18n()
const props = defineProps({
  skillId: { type: String, required: true },
})

const message = useMessage()
const loading = ref(false)
const tools = ref([])
const editingTool = ref(null)
const editForm = ref({})
const saving = ref(false)

async function loadTools() {
  loading.value = true
  try {
    const res = await api.getSkillTools(props.skillId)
    if (res.code === 200) tools.value = res.data || []
  } catch (e) {
    message.error(t('views.skills.message_load_tools_failed'))
  } finally {
    loading.value = false
  }
}

function startEditTool(tool) {
  editingTool.value = tool.name
  editForm.value = {
    description: tool.description || '',
    parameters: JSON.stringify(tool.parameters || {}, null, 2),
  }
}

function cancelEdit() { editingTool.value = null }

async function saveTool(tool) {
  saving.value = true
  try {
    let params
    try { params = JSON.parse(editForm.value.parameters) }
    catch { message.error(t('views.skills.message_json_error')); saving.value = false; return }
    const res = await api.updateSkillTool(props.skillId, tool.name, {
      description: editForm.value.description,
      parameters: params,
    })
    if (res.code === 200) { message.success(t('views.skills.message_save_success')); editingTool.value = null; await loadTools() }
    else message.error(res.msg || t('views.skills.message_save_failed'))
  } catch (e) { message.error(t('views.skills.message_save_failed')) }
  finally { saving.value = false }
}

onMounted(() => { loadTools() })
</script>

<template>
  <div class="tools-tab">
    <NSpin :show="loading">
      <NEmpty v-if="tools.length === 0 && !loading" :description="t('views.skills.text_no_tools')" />
      <NCollapse v-else arrow-placement="left">
        <NCollapseItem v-for="tool in tools" :key="tool.name" :name="tool.name">
          <template #header>
            <div class="tool-header">
              <NIcon size="16" color="#18a058">
                <svg viewBox="0 0 24 24"><path fill="currentColor" d="M22.7 19l-9.1-9.1c.9-2.3.4-5-1.5-6.9c-2-2-5-2.4-7.4-1.3L9 6 6 9L1.6 4.7C.4 7.1.9 10.1 2.9 12.1c1.9 1.9 4.6 2.4 6.9 1.5l9.1 9.1c.4.4 1 .4 1.4 0l2.3-2.3c.5-.4.5-1.1.1-1.4z"/></svg>
              </NIcon>
              <span class="tool-name">{{ tool.name }}</span>
              <NTag v-if="tool.type" size="tiny" :bordered="false" type="info">{{ tool.type }}</NTag>
            </div>
          </template>
          <template #header-extra>
            <NButton v-if="editingTool !== tool.name" size="tiny" @click.stop="startEditTool(tool)">{{ t('views.skills.button_edit') }}</NButton>
          </template>
          <div class="tool-content">
            <template v-if="editingTool !== tool.name">
              <div class="tool-field">
                <div class="field-label">{{ t('views.skills.tool_label_description') }}</div>
                <div class="field-value">{{ tool.description || '-' }}</div>
              </div>
              <div class="tool-field">
                <div class="field-label">{{ t('views.skills.tool_label_parameters') }}</div>
                <pre class="json-preview">{{ JSON.stringify(tool.parameters || {}, null, 2) }}</pre>
              </div>
            </template>
            <template v-else>
              <div class="tool-field">
                <div class="field-label">{{ t('views.skills.tool_label_description') }}</div>
                <NInput v-model:value="editForm.description" type="textarea" :rows="2" :placeholder="t('views.skills.tool_placeholder_description')" />
              </div>
              <div class="tool-field">
                <div class="field-label">{{ t('views.skills.tool_label_parameters_json') }}</div>
                <NInput v-model:value="editForm.parameters" type="textarea" :rows="10" :placeholder="t('views.skills.tool_placeholder_parameters')" style="font-family: 'Monaco', 'Menlo', monospace; font-size: 13px;" />
              </div>
              <NSpace style="margin-top: 12px;">
                <NButton size="small" @click="cancelEdit">{{ t('views.skills.button_cancel') }}</NButton>
                <NButton type="primary" size="small" :loading="saving" @click="saveTool(tool)">{{ t('views.skills.button_save') }}</NButton>
              </NSpace>
            </template>
          </div>
        </NCollapseItem>
      </NCollapse>
    </NSpin>
  </div>
</template>

<style scoped>
.tools-tab { padding: 16px 0; }
.tool-header { display: flex; align-items: center; gap: 8px; }
.tool-name { font-weight: 600; font-family: 'Monaco', 'Menlo', monospace; font-size: 14px; }
.tool-content { padding: 8px 0; }
.tool-field { margin-bottom: 16px; }
.field-label { font-size: 12px; color: #999; margin-bottom: 6px; }
.field-value { font-size: 14px; color: #333; }
.json-preview { background: #f5f7fa; border: 1px solid #e8e8e8; border-radius: 6px; padding: 12px; font-family: 'Monaco', 'Menlo', monospace; font-size: 13px; line-height: 1.5; overflow-x: auto; margin: 0; }
</style>
