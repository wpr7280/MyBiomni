<script setup>
import { ref, onMounted, computed } from 'vue'
import { NButton, NSpace, NSpin, NIcon } from 'naive-ui'
import { useMessage } from 'naive-ui'
import { useI18n } from 'vue-i18n'
import { marked } from 'marked'
import api from '@/api'

marked.setOptions({ breaks: true, gfm: true })

const { t } = useI18n()
const props = defineProps({
  skillId: { type: String, required: true },
})

const message = useMessage()
const loading = ref(false)
const saving = ref(false)
const editing = ref(false)
const content = ref('')
const editContent = ref('')

const renderedHtml = computed(() => content.value ? marked(content.value) : `<p style="color:#999;">${t('views.skills.text_no_howto')}</p>`)
const previewHtml = computed(() => editContent.value ? marked(editContent.value) : `<p style="color:#999;">${t('views.skills.text_preview')}</p>`)

async function loadHowTo() {
  loading.value = true
  try {
    const res = await api.getSkillHowTo(props.skillId)
    if (res.code === 200) content.value = res.data?.content || ''
  } catch (e) {
    content.value = ''
  } finally {
    loading.value = false
  }
}

function startEdit() { editContent.value = content.value; editing.value = true }
function cancelEdit() { editing.value = false }

async function saveHowTo() {
  saving.value = true
  try {
    const res = await api.updateSkillHowTo(props.skillId, { content: editContent.value })
    if (res.code === 200) { content.value = editContent.value; editing.value = false; message.success(t('views.skills.message_save_success')) }
    else message.error(res.msg || t('views.skills.message_save_failed'))
  } catch (e) { message.error(t('views.skills.message_save_failed')) }
  finally { saving.value = false }
}

onMounted(() => { loadHowTo() })
</script>

<template>
  <div class="howto-tab">
    <div class="tab-toolbar">
      <NSpace v-if="!editing">
        <NButton type="primary" size="small" @click="startEdit">
          <template #icon>
            <NIcon><svg viewBox="0 0 24 24"><path fill="currentColor" d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04a.996.996 0 0 0 0-1.41l-2.34-2.34a.996.996 0 0 0-1.41 0l-1.83 1.83l3.75 3.75l1.83-1.83z"/></svg></NIcon>
          </template>
          {{ t('views.skills.button_edit') }}
        </NButton>
      </NSpace>
      <NSpace v-else>
        <NButton size="small" @click="cancelEdit">{{ t('views.skills.button_cancel') }}</NButton>
        <NButton type="primary" size="small" :loading="saving" @click="saveHowTo">{{ t('views.skills.button_save') }}</NButton>
      </NSpace>
    </div>

    <NSpin :show="loading">
      <div v-if="!editing" class="markdown-body" v-html="renderedHtml" />
      <div v-else class="editor-layout">
        <div class="editor-pane">
          <div class="pane-title">{{ t('views.skills.text_markdown_edit') }}</div>
          <textarea v-model="editContent" class="md-textarea" placeholder="Markdown..." />
        </div>
        <div class="preview-pane">
          <div class="pane-title">{{ t('views.skills.text_preview') }}</div>
          <div class="markdown-body" v-html="previewHtml" />
        </div>
      </div>
    </NSpin>
  </div>
</template>

<style scoped>
.howto-tab { padding: 16px 0; }
.tab-toolbar { display: flex; justify-content: flex-end; margin-bottom: 16px; }
.editor-layout { display: flex; gap: 16px; min-height: 500px; }
.editor-pane, .preview-pane { flex: 1; display: flex; flex-direction: column; border: 1px solid #e8e8e8; border-radius: 8px; overflow: hidden; }
.pane-title { padding: 8px 12px; font-size: 12px; font-weight: 600; color: #666; background: #fafafa; border-bottom: 1px solid #e8e8e8; }
.md-textarea { flex: 1; border: none; outline: none; resize: none; padding: 16px; font-size: 14px; font-family: 'Monaco', 'Menlo', 'Consolas', monospace; line-height: 1.6; background: #fff; }
.markdown-body { padding: 16px; font-size: 14px; line-height: 1.8; color: #333; overflow-y: auto; flex: 1; }
.markdown-body :deep(h1) { font-size: 24px; margin: 16px 0 8px; font-weight: 600; }
.markdown-body :deep(h2) { font-size: 20px; margin: 14px 0 8px; font-weight: 600; }
.markdown-body :deep(h3) { font-size: 16px; margin: 12px 0 6px; font-weight: 600; }
.markdown-body :deep(pre) { background: #f5f7fa; padding: 12px; border-radius: 6px; overflow-x: auto; margin: 8px 0; }
.markdown-body :deep(code) { background: #f0f0f0; padding: 2px 6px; border-radius: 3px; font-size: 13px; font-family: 'Monaco', 'Menlo', monospace; }
.markdown-body :deep(pre code) { background: none; padding: 0; }
.markdown-body :deep(li) { margin-left: 20px; list-style: disc; }
.markdown-body :deep(hr) { border: none; border-top: 1px solid #e8e8e8; margin: 16px 0; }
.markdown-body :deep(a) { color: #18a058; text-decoration: none; }
.markdown-body :deep(a:hover) { text-decoration: underline; }
.markdown-body :deep(table) { border-collapse: collapse; width: 100%; margin: 12px 0; }
.markdown-body :deep(th), .markdown-body :deep(td) { border: 1px solid #ddd; padding: 8px 12px; text-align: left; font-size: 13px; }
.markdown-body :deep(th) { background: #f5f7fa; font-weight: 600; }
@media (max-width: 768px) { .editor-layout { flex-direction: column; } }
</style>
