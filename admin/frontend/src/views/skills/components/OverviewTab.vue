<script setup>
import { ref, watch } from 'vue'
import { NForm, NFormItem, NInput, NButton, NSpace, NTag, NDynamicTags } from 'naive-ui'
import { useMessage } from 'naive-ui'
import { useI18n } from 'vue-i18n'
import api from '@/api'

const { t } = useI18n()
const props = defineProps({ skill: { type: Object, required: true } })
const emit = defineEmits(['updated'])
const message = useMessage()
const editing = ref(false)
const saving = ref(false)
const form = ref({})

function resetForm() {
  form.value = {
    display_name: props.skill.display_name || '',
    description: props.skill.description || '',
    version: props.skill.version || '0.1.0',
    category: props.skill.category || '',
    authors: props.skill.authors || [],
    license: props.skill.license || '',
    triggers: props.skill.triggers || [],
  }
}

watch(() => props.skill, resetForm, { immediate: true })
function startEdit() { resetForm(); editing.value = true }
function cancelEdit() { editing.value = false; resetForm() }

async function saveEdit() {
  saving.value = true
  try {
    const res = await api.updateSkill(props.skill.id, form.value)
    if (res.code === 200) { message.success(t('views.skills.message_save_success')); editing.value = false; emit('updated') }
    else message.error(res.msg || t('views.skills.message_save_failed'))
  } catch (e) { message.error(t('views.skills.message_save_failed')) }
  finally { saving.value = false }
}
</script>

<template>
  <div class="overview-tab">
    <div class="tab-toolbar">
      <NSpace v-if="!editing">
        <NButton type="primary" size="small" @click="startEdit">{{ t('views.skills.button_edit') }}</NButton>
      </NSpace>
      <NSpace v-else>
        <NButton size="small" @click="cancelEdit">{{ t('views.skills.button_cancel') }}</NButton>
        <NButton type="primary" size="small" :loading="saving" @click="saveEdit">{{ t('views.skills.button_save') }}</NButton>
      </NSpace>
    </div>

    <div v-if="!editing" class="info-grid">
      <div class="info-item">
        <div class="info-label">{{ t('views.skills.overview_skill_id') }}</div>
        <div class="info-value mono">{{ skill.name }}</div>
      </div>
      <div class="info-item">
        <div class="info-label">{{ t('views.skills.overview_display_name') }}</div>
        <div class="info-value">{{ skill.display_name || '-' }}</div>
      </div>
      <div class="info-item">
        <div class="info-label">{{ t('views.skills.overview_category') }}</div>
        <div class="info-value">
          <NTag v-if="skill.category" size="small" :bordered="false" type="success">{{ skill.category }}</NTag>
          <span v-else>-</span>
        </div>
      </div>
      <div class="info-item">
        <div class="info-label">{{ t('views.skills.overview_version') }}</div>
        <div class="info-value">{{ skill.version || '-' }}</div>
      </div>
      <div class="info-item full">
        <div class="info-label">{{ t('views.skills.overview_description') }}</div>
        <div class="info-value">{{ skill.description || '-' }}</div>
      </div>
      <div class="info-item">
        <div class="info-label">{{ t('views.skills.overview_authors') }}</div>
        <div class="info-value">
          <NSpace v-if="skill.authors && skill.authors.length" size="small">
            <NTag v-for="a in skill.authors" :key="a" size="small" :bordered="false">{{ a }}</NTag>
          </NSpace>
          <span v-else>-</span>
        </div>
      </div>
      <div class="info-item">
        <div class="info-label">{{ t('views.skills.overview_license') }}</div>
        <div class="info-value">{{ skill.license || '-' }}</div>
      </div>
      <div class="info-item full">
        <div class="info-label">{{ t('views.skills.overview_triggers') }}</div>
        <div class="info-value">
          <NSpace v-if="skill.triggers && skill.triggers.length" size="small">
            <NTag v-for="tr in skill.triggers" :key="tr" size="small" :bordered="false" type="info">{{ tr }}</NTag>
          </NSpace>
          <span v-else>-</span>
        </div>
      </div>
      <div class="info-item full" v-if="skill.dependencies && Object.keys(skill.dependencies).length">
        <div class="info-label">{{ t('views.skills.overview_dependencies') }}</div>
        <div class="info-value">
          <NSpace size="small">
            <NTag v-for="(ver, dep) in skill.dependencies" :key="dep" size="small" :bordered="false">{{ dep }}: {{ ver }}</NTag>
          </NSpace>
        </div>
      </div>
    </div>

    <NForm v-else :model="form" label-placement="left" label-width="100" style="max-width: 700px;">
      <NFormItem :label="t('views.skills.overview_display_name')">
        <NInput v-model:value="form.display_name" :placeholder="t('views.skills.placeholder_display_name')" />
      </NFormItem>
      <NFormItem :label="t('views.skills.overview_category')">
        <NInput v-model:value="form.category" :placeholder="t('views.skills.placeholder_category')" />
      </NFormItem>
      <NFormItem :label="t('views.skills.overview_version')">
        <NInput v-model:value="form.version" :placeholder="t('views.skills.placeholder_version')" />
      </NFormItem>
      <NFormItem :label="t('views.skills.overview_description')">
        <NInput v-model:value="form.description" type="textarea" :rows="3" :placeholder="t('views.skills.placeholder_description')" />
      </NFormItem>
      <NFormItem :label="t('views.skills.overview_authors')">
        <NDynamicTags v-model:value="form.authors" />
      </NFormItem>
      <NFormItem :label="t('views.skills.overview_license')">
        <NInput v-model:value="form.license" :placeholder="t('views.skills.placeholder_license')" />
      </NFormItem>
      <NFormItem :label="t('views.skills.overview_triggers')">
        <NDynamicTags v-model:value="form.triggers" />
      </NFormItem>
    </NForm>
  </div>
</template>

<style scoped>
.overview-tab { padding: 16px 0; }
.tab-toolbar { display: flex; justify-content: flex-end; margin-bottom: 20px; }
.info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.info-item { padding: 12px 16px; background: #fafafa; border-radius: 8px; }
.info-item.full { grid-column: 1 / -1; }
.info-label { font-size: 12px; color: #999; margin-bottom: 4px; }
.info-value { font-size: 14px; color: #333; word-break: break-all; }
.info-value.mono { font-family: 'Monaco', 'Menlo', monospace; }
@media (max-width: 768px) { .info-grid { grid-template-columns: 1fr; } }
</style>
