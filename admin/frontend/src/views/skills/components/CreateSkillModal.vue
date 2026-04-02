<script setup>
import { ref, watch } from 'vue'
import { NModal, NForm, NFormItem, NInput, NSelect, NButton, NSpace } from 'naive-ui'
import { useMessage } from 'naive-ui'
import api from '@/api'

const props = defineProps({
  show: Boolean,
  categories: { type: Array, default: () => [] },
})

const emit = defineEmits(['update:show', 'created'])

const message = useMessage()
const submitting = ref(false)
const formRef = ref(null)

const form = ref({
  name: '',
  display_name: '',
  category: '',
  description: '',
})

const rules = {
  name: [
    { required: true, message: '请输入 Skill 标识', trigger: 'blur' },
    { pattern: /^[a-z][a-z0-9_-]*$/, message: '只允许小写字母、数字、下划线、短横线，以字母开头', trigger: 'blur' },
  ],
  display_name: [{ required: true, message: '请输入显示名称', trigger: 'blur' }],
  category: [{ required: true, message: '请选择或输入分类', trigger: 'blur' }],
}

const categoryOptions = ref([])

watch(
  () => props.categories,
  (cats) => {
    categoryOptions.value = (cats || []).map(c => ({ label: c, value: c }))
  },
  { immediate: true }
)

watch(
  () => props.show,
  (val) => {
    if (val) {
      form.value = { name: '', display_name: '', category: '', description: '' }
    }
  }
)

async function handleSubmit() {
  try {
    await formRef.value?.validate()
  } catch {
    return
  }
  submitting.value = true
  try {
    const res = await api.createSkill(form.value)
    if (res.code === 200) {
      message.success('Skill 创建成功')
      emit('created', res.data)
    } else {
      message.error(res.msg || '创建失败')
    }
  } catch (e) {
    message.error('创建失败：' + (e.message || ''))
  } finally {
    submitting.value = false
  }
}

function handleClose() {
  emit('update:show', false)
}
</script>

<template>
  <NModal
    :show="show"
    preset="card"
    title="新建 Skill"
    style="width: 520px;"
    :mask-closable="false"
    @close="handleClose"
    @mask-click="handleClose"
  >
    <NForm ref="formRef" :model="form" :rules="rules" label-placement="left" label-width="100">
      <NFormItem label="Skill 标识" path="name">
        <NInput v-model:value="form.name" placeholder="如 web_search、data_analysis" />
      </NFormItem>
      <NFormItem label="显示名称" path="display_name">
        <NInput v-model:value="form.display_name" placeholder="如 网页搜索、数据分析" />
      </NFormItem>
      <NFormItem label="分类" path="category">
        <NSelect
          v-model:value="form.category"
          :options="categoryOptions"
          filterable
          tag
          placeholder="选择或输入分类"
        />
      </NFormItem>
      <NFormItem label="描述">
        <NInput
          v-model:value="form.description"
          type="textarea"
          :rows="3"
          placeholder="Skill 功能描述"
        />
      </NFormItem>
    </NForm>
    <template #footer>
      <NSpace justify="end">
        <NButton @click="handleClose">取消</NButton>
        <NButton type="primary" :loading="submitting" @click="handleSubmit">创建</NButton>
      </NSpace>
    </template>
  </NModal>
</template>
