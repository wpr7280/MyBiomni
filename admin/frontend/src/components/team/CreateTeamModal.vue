<template>
  <n-modal
    :show="visible"
    preset="card"
    :title="$t('teams.button_create_team')"
    style="max-width: 500px; width: 90vw"
    :closable="!loading"
    :mask-closable="false"
    @update:show="$emit('update:visible', $event)"
  >
    <n-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-placement="left"
      label-width="80"
      require-mark-placement="right-hanging"
    >
      <n-form-item :label="$t('teams.label_team_name')" path="name">
        <n-input
          v-model:value="formData.name"
          :placeholder="$t('teams.placeholder_team_name')"
          clearable
          :disabled="loading"
          maxlength="50"
          show-count
        />
      </n-form-item>
    </n-form>

    <template #footer>
      <div class="flex justify-end gap-3">
        <n-button :disabled="loading" @click="handleCancel">{{ $t('teams.button_cancel') }}</n-button>
        <n-button type="primary" :loading="loading" @click="handleSubmit">{{ $t('teams.button_create_team') }}</n-button>
      </div>
    </template>
  </n-modal>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { useMessage } from 'naive-ui'
import { useI18n } from 'vue-i18n'
import { useTeamStore } from '@/store'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:visible', 'success'])

const { t: $t } = useI18n()
const message = useMessage()
const teamStore = useTeamStore()
const formRef = ref(null)
const loading = ref(false)

// 表单数据
const formData = reactive({
  name: '',
})

// 表单验证规则
const formRules = {
  name: [
    { required: true, message: $t('teams.message_team_name_required') },
    { min: 2, max: 50, message: '团队名称长度为2-50个字符' },
  ],
}

// 监听弹窗显示状态，重置表单
watch(
  () => props.visible,
  (newVal) => {
    if (newVal) {
      resetForm()
    }
  }
)

// 重置表单
const resetForm = () => {
  formData.name = ''
  formRef.value?.restoreValidation()
}

// 处理提交
const handleSubmit = async () => {
  try {
    await formRef.value?.validate()
  } catch (error) {
    return
  }

  loading.value = true

  try {
    const result = await teamStore.createTeam({
      name: formData.name,
    })

    if (result.success) {
      message.success($t('teams.message_team_created'))
      emit('success', result.data)
      emit('update:visible', false)
    } else {
      message.error(result.message || $t('teams.message_team_create_failed'))
    }
  } catch (error) {
    message.error($t('teams.message_team_create_failed') + ': ' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

// 处理取消
const handleCancel = () => {
  emit('update:visible', false)
}
</script>

<style scoped>
:deep(.n-form-item-label) {
  font-weight: 500;
}
</style>
