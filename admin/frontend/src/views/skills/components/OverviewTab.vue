<script setup>
import { ref, watch } from 'vue'
import { NForm, NFormItem, NInput, NButton, NSpace, NTag, NDynamicTags } from 'naive-ui'
import { useMessage } from 'naive-ui'
import api from '@/api'

const props = defineProps({
  skill: { type: Object, required: true },
})

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

function startEdit() {
  resetForm()
  editing.value = true
}

function cancelEdit() {
  editing.value = false
  resetForm()
}

async function saveEdit() {
  saving.value = true
  try {
    const res = await api.updateSkill(props.skill.id, form.value)
    if (res.code === 200) {
      message.success('保存成功')
      editing.value = false
      emit('updated')
    } else {
      message.error(res.msg || '保存失败')
    }
  } catch (e) {
    message.error('保存失败')
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="overview-tab">
    <div class="tab-toolbar">
      <NSpace v-if="!editing">
        <NButton type="primary" size="small" @click="startEdit">编辑</NButton>
      </NSpace>
      <NSpace v-else>
        <NButton size="small" @click="cancelEdit">取消</NButton>
        <NButton type="primary" size="small" :loading="saving" @click="saveEdit">保存</NButton>
      </NSpace>
    </div>

    <!-- 只读模式 -->
    <div v-if="!editing" class="info-grid">
      <div class="info-item">
        <div class="info-label">Skill 标识</div>
        <div class="info-value mono">{{ skill.name }}</div>
      </div>
      <div class="info-item">
        <div class="info-label">显示名称</div>
        <div class="info-value">{{ skill.display_name || '-' }}</div>
      </div>
      <div class="info-item">
        <div class="info-label">分类</div>
        <div class="info-value">
          <NTag v-if="skill.category" size="small" :bordered="false" type="success">{{ skill.category }}</NTag>
          <span v-else>-</span>
        </div>
      </div>
      <div class="info-item">
        <div class="info-label">版本</div>
        <div class="info-value">{{ skill.version || '-' }}</div>
      </div>
      <div class="info-item full">
        <div class="info-label">描述</div>
        <div class="info-value">{{ skill.description || '-' }}</div>
      </div>
      <div class="info-item">
        <div class="info-label">作者</div>
        <div class="info-value">
          <NSpace v-if="skill.authors && skill.authors.length" size="small">
            <NTag v-for="a in skill.authors" :key="a" size="small" :bordered="false">{{ a }}</NTag>
          </NSpace>
          <span v-else>-</span>
        </div>
      </div>
      <div class="info-item">
        <div class="info-label">许可证</div>
        <div class="info-value">{{ skill.license || '-' }}</div>
      </div>
      <div class="info-item full">
        <div class="info-label">触发条件</div>
        <div class="info-value">
          <NSpace v-if="skill.triggers && skill.triggers.length" size="small">
            <NTag v-for="t in skill.triggers" :key="t" size="small" :bordered="false" type="info">{{ t }}</NTag>
          </NSpace>
          <span v-else>-</span>
        </div>
      </div>
      <div class="info-item full" v-if="skill.dependencies && Object.keys(skill.dependencies).length">
        <div class="info-label">依赖</div>
        <div class="info-value">
          <NSpace size="small">
            <NTag v-for="(ver, dep) in skill.dependencies" :key="dep" size="small" :bordered="false">{{ dep }}: {{ ver }}</NTag>
          </NSpace>
        </div>
      </div>
    </div>

    <!-- 编辑模式 -->
    <NForm v-else :model="form" label-placement="left" label-width="100" style="max-width: 700px;">
      <NFormItem label="显示名称">
        <NInput v-model:value="form.display_name" placeholder="显示名称" />
      </NFormItem>
      <NFormItem label="分类">
        <NInput v-model:value="form.category" placeholder="分类" />
      </NFormItem>
      <NFormItem label="版本">
        <NInput v-model:value="form.version" placeholder="如 0.1.0" />
      </NFormItem>
      <NFormItem label="描述">
        <NInput v-model:value="form.description" type="textarea" :rows="3" placeholder="Skill 功能描述" />
      </NFormItem>
      <NFormItem label="作者">
        <NDynamicTags v-model:value="form.authors" />
      </NFormItem>
      <NFormItem label="许可证">
        <NInput v-model:value="form.license" placeholder="如 MIT" />
      </NFormItem>
      <NFormItem label="触发条件">
        <NDynamicTags v-model:value="form.triggers" />
      </NFormItem>
    </NForm>
  </div>
</template>

<style scoped>
.overview-tab {
  padding: 16px 0;
}

.tab-toolbar {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 20px;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.info-item {
  padding: 12px 16px;
  background: #fafafa;
  border-radius: 8px;
}

.info-item.full {
  grid-column: 1 / -1;
}

.info-label {
  font-size: 12px;
  color: #999;
  margin-bottom: 4px;
}

.info-value {
  font-size: 14px;
  color: #333;
  word-break: break-all;
}

.info-value.mono {
  font-family: 'Monaco', 'Menlo', monospace;
}

@media (max-width: 768px) {
  .info-grid {
    grid-template-columns: 1fr;
  }
}
</style>
