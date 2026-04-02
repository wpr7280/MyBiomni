<script setup>
import { ref } from 'vue'
import { NButton, NSpace, NSwitch, NPopconfirm, NCard, NIcon, NAlert } from 'naive-ui'
import { useMessage } from 'naive-ui'
import api from '@/api'

const props = defineProps({
  skill: { type: Object, required: true },
})

const emit = defineEmits(['deleted', 'updated'])

const message = useMessage()
const toggling = ref(false)
const deleting = ref(false)

async function toggleEnabled() {
  toggling.value = true
  try {
    if (props.skill.enabled) {
      await api.disableSkill(props.skill.id)
      message.success('已禁用')
    } else {
      await api.enableSkill(props.skill.id)
      message.success('已启用')
    }
    emit('updated')
  } catch (e) {
    message.error('操作失败')
  } finally {
    toggling.value = false
  }
}

async function handleDelete() {
  deleting.value = true
  try {
    const res = await api.deleteSkill(props.skill.id)
    if (res.code === 200) {
      message.success('Skill 已删除')
      emit('deleted')
    } else {
      message.error(res.msg || '删除失败')
    }
  } catch (e) {
    message.error('删除失败')
  } finally {
    deleting.value = false
  }
}
</script>

<template>
  <div class="settings-tab">
    <!-- 启用/禁用 -->
    <NCard class="setting-card" title="启用状态">
      <div class="setting-row">
        <div class="setting-info">
          <div class="setting-label">{{ skill.enabled ? '当前已启用' : '当前已禁用' }}</div>
          <div class="setting-desc">启用后，该 Skill 的工具将对 Agent 可用</div>
        </div>
        <NSwitch
          :value="skill.enabled"
          :loading="toggling"
          @update:value="toggleEnabled"
        />
      </div>
    </NCard>

    <!-- 危险操作 -->
    <NCard class="setting-card danger-card" title="危险操作">
      <NAlert type="warning" style="margin-bottom: 16px;">
        删除 Skill 是不可逆操作，所有关联的工具定义和 How-To 文档都将被移除。
      </NAlert>
      <NPopconfirm
        @positive-click="handleDelete"
      >
        <template #trigger>
          <NButton type="error" :loading="deleting">
            <template #icon>
              <NIcon>
                <svg viewBox="0 0 24 24"><path fill="currentColor" d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg>
              </NIcon>
            </template>
            删除此 Skill
          </NButton>
        </template>
        确定要删除 <strong>{{ skill.display_name || skill.name }}</strong> 吗？此操作不可撤销。
      </NPopconfirm>
    </NCard>
  </div>
</template>

<style scoped>
.settings-tab {
  padding: 16px 0;
  max-width: 700px;
}

.setting-card {
  margin-bottom: 20px;
  border-radius: 10px;
}

.setting-card :deep(.n-card-header) {
  padding: 14px 20px;
  font-size: 15px;
}

.setting-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.setting-label {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.setting-desc {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

.danger-card {
  border-color: #fde2e2;
}

.danger-card :deep(.n-card-header) {
  color: #d03050;
}
</style>
