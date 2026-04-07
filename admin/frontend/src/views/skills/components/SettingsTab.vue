<script setup>
import { ref } from 'vue'
import { NButton, NSpace, NSwitch, NPopconfirm, NCard, NIcon, NAlert } from 'naive-ui'
import { useMessage } from 'naive-ui'
import { useI18n } from 'vue-i18n'
import api from '@/api'

const { t } = useI18n()
const props = defineProps({ skill: { type: Object, required: true } })
const emit = defineEmits(['deleted', 'updated'])
const message = useMessage()
const toggling = ref(false)
const deleting = ref(false)

async function toggleEnabled() {
  toggling.value = true
  try {
    if (props.skill.enabled) {
      await api.disableSkill(props.skill.id)
      message.success(t('views.skills.message_disable_success'))
    } else {
      await api.enableSkill(props.skill.id)
      message.success(t('views.skills.message_enable_success'))
    }
    emit('updated')
  } catch (e) { message.error(t('views.skills.settings_operation_failed')) }
  finally { toggling.value = false }
}

async function handleDelete() {
  deleting.value = true
  try {
    const res = await api.deleteSkill(props.skill.id)
    if (res.code === 200) { message.success(t('views.skills.settings_deleted')); emit('deleted') }
    else message.error(res.msg || t('views.skills.message_save_failed'))
  } catch (e) { message.error(t('views.skills.message_save_failed')) }
  finally { deleting.value = false }
}
</script>

<template>
  <div class="settings-tab">
    <NCard class="setting-card" :title="t('views.skills.settings_enable_status')">
      <div class="setting-row">
        <div class="setting-info">
          <div class="setting-label">{{ skill.enabled ? t('views.skills.settings_currently_enabled') : t('views.skills.settings_currently_disabled') }}</div>
          <div class="setting-desc">{{ t('views.skills.settings_enable_desc') }}</div>
        </div>
        <NSwitch :value="skill.enabled" :loading="toggling" @update:value="toggleEnabled" />
      </div>
    </NCard>

    <NCard class="setting-card danger-card" :title="t('views.skills.settings_danger_zone')">
      <NAlert type="warning" style="margin-bottom: 16px;">
        {{ t('views.skills.settings_delete_warning') }}
      </NAlert>
      <NPopconfirm @positive-click="handleDelete">
        <template #trigger>
          <NButton type="error" :loading="deleting">
            <template #icon>
              <NIcon><svg viewBox="0 0 24 24"><path fill="currentColor" d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg></NIcon>
            </template>
            {{ t('views.skills.settings_delete_button') }}
          </NButton>
        </template>
        {{ t('views.skills.settings_delete_confirm', { name: skill.display_name || skill.name }) }}
      </NPopconfirm>
    </NCard>
  </div>
</template>

<style scoped>
.settings-tab { padding: 16px 0; max-width: 700px; }
.setting-card { margin-bottom: 20px; border-radius: 10px; }
.setting-card :deep(.n-card-header) { padding: 14px 20px; font-size: 15px; }
.setting-row { display: flex; justify-content: space-between; align-items: center; }
.setting-label { font-size: 14px; font-weight: 500; color: #333; }
.setting-desc { font-size: 12px; color: #999; margin-top: 4px; }
.danger-card { border-color: #fde2e2; }
.danger-card :deep(.n-card-header) { color: #d03050; }
</style>
