<template>
  <n-modal
    :show="visible"
    preset="card"
    title="邀请团队成员"
    style="max-width: 600px; width: 90vw"
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
      <n-form-item label="邮箱地址" path="email">
        <n-input
          v-model:value="formData.email"
          placeholder="请输入邀请成员的邮箱地址"
          clearable
          :disabled="loading"
        />
      </n-form-item>

      <n-form-item label="角色" path="role">
        <n-select
          v-model:value="formData.role"
          :options="roleOptions"
          placeholder="选择成员角色"
          :disabled="loading"
        />
      </n-form-item>

      <n-form-item label="邀请消息" path="message">
        <n-input
          v-model:value="formData.message"
          type="textarea"
          placeholder="可选：添加邀请消息"
          :rows="3"
          :disabled="loading"
          maxlength="500"
          show-count
        />
      </n-form-item>
    </n-form>

    <template #footer>
      <div class="flex justify-end gap-3">
        <n-button :disabled="loading" @click="handleCancel"> 取消 </n-button>
        <n-button type="primary" :loading="loading" @click="handleSubmit"> 发送邀请 </n-button>
      </div>
    </template>
  </n-modal>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { useMessage } from 'naive-ui'
import { useTeamStore } from '@/store'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:visible', 'success'])

const message = useMessage()
const teamStore = useTeamStore()
const formRef = ref(null)
const loading = ref(false)

// 表单数据
const formData = reactive({
  email: '',
  role: 'member',
  message: '',
})

// 角色选项
const roleOptions = [
  { label: '成员', value: 'member' },
  { label: '管理员', value: 'admin' },
]

// 表单验证规则
const formRules = {
  email: [
    { required: true, message: '请输入邮箱地址' },
    { type: 'email', message: '请输入有效的邮箱地址' },
  ],
  role: [{ required: true, message: '请选择角色' }],
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
  formData.email = ''
  formData.role = 'member'
  formData.message = ''
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
    const result = await teamStore.inviteMember({
      email: formData.email,
      role: formData.role,
      message: formData.message,
    })

    if (result.success) {
      message.success('邀请发送成功')
      emit('success', result.data)
      emit('update:visible', false)
    } else {
      message.error(result.message || '发送邀请失败')
    }
  } catch (error) {
    message.error('发送邀请失败: ' + (error.message || '未知错误'))
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
