<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NButton, NCard, NSpace, NIcon, NTag, NSpin, NInput, NModal } from 'naive-ui'
import { useMessage } from 'naive-ui'
import { useI18n } from 'vue-i18n'
import { marked } from 'marked'
import CommonPage from '@/components/page/CommonPage.vue'
import api from '@/api'

marked.setOptions({ breaks: true, gfm: true })

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const message = useMessage()
const docId = computed(() => route.params.id)
const loading = ref(false)
const saving = ref(false)
const editing = ref(false)
const doc = ref(null)
const editContent = ref('')
const showDelete = ref(false)
const deleting = ref(false)

const previewHtml = computed(() => editContent.value ? marked(editContent.value) : `<p style="color:#999;">${t('views.knowhow.text_preview')}</p>`)
const readHtml = computed(() => doc.value?.content ? marked(doc.value.content) : `<p style="color:#999;">${t('views.knowhow.text_no_content')}</p>`)

async function loadDoc() {
  loading.value = true
  try {
    const res = await api.getKnowHowDetail(docId.value)
    if (res.code === 200) doc.value = res.data
  } catch (e) {
    message.error(t('views.knowhow.message_load_failed'))
  } finally {
    loading.value = false
  }
}

function startEdit() { editContent.value = doc.value?.content || ''; editing.value = true }
function cancelEdit() { editing.value = false }

async function saveContent() {
  saving.value = true
  try {
    const res = await api.updateKnowHow(docId.value, { content: editContent.value })
    if (res.code === 200) { doc.value = res.data; editing.value = false; message.success(t('views.knowhow.message_save_success')) }
    else message.error(res.message || t('views.knowhow.message_save_failed'))
  } catch (e) { message.error(t('views.knowhow.message_save_failed')) }
  finally { saving.value = false }
}

async function doDelete() {
  deleting.value = true
  try {
    const res = await api.deleteKnowHow(docId.value)
    if (res.code === 200) { message.success(t('views.knowhow.message_delete_success')); router.push('/knowhow') }
    else message.error(res.message || t('views.knowhow.message_delete_failed'))
  } catch (e) { message.error(t('views.knowhow.message_delete_failed')) }
  finally { deleting.value = false; showDelete.value = false }
}

function goBack() { router.push('/knowhow') }
onMounted(() => { loadDoc() })
</script>

<template>
  <CommonPage>
    <div class="detail-page">
      <NSpin :show="loading">
        <div v-if="doc">
          <div class="detail-header">
            <div class="header-left">
              <NButton text @click="goBack" style="font-size: 24px; margin-right: 8px;">←</NButton>
              <div class="header-info">
                <div class="header-title">
                  📚 {{ doc.name }}
                  <NTag v-if="doc.version" size="small" :bordered="false" type="info">v{{ doc.version }}</NTag>
                </div>
                <div class="header-meta">
                  <span class="meta-id">{{ doc.id }}</span>
                  <span v-if="doc.authors">👤 {{ doc.authors }}</span>
                  <span v-if="doc.license">📜 {{ doc.license }}</span>
                  <span v-if="doc.last_updated">🕐 {{ doc.last_updated }}</span>
                  <NTag v-if="doc.commercial_use && doc.commercial_use.includes('✅')" size="tiny" :bordered="false" type="success">{{ t('views.knowhow.label_commercial') }}</NTag>
                </div>
              </div>
            </div>
            <NSpace>
              <NButton v-if="!editing" type="primary" @click="startEdit">{{ t('views.knowhow.button_edit') }}</NButton>
              <template v-else>
                <NButton @click="cancelEdit">{{ t('views.knowhow.button_cancel') }}</NButton>
                <NButton type="primary" :loading="saving" @click="saveContent">{{ t('views.knowhow.button_save') }}</NButton>
              </template>
              <NButton type="error" ghost @click="showDelete = true">{{ t('views.knowhow.button_delete') }}</NButton>
            </NSpace>
          </div>

          <div v-if="doc.description && !editing" class="desc-bar">{{ doc.description }}</div>

          <div v-if="doc.resources && doc.resources.length > 0 && !editing" class="resources-bar">
            <span class="resources-label">📎 {{ t('views.knowhow.label_resources') }}：</span>
            <NTag v-for="r in doc.resources" :key="r" size="small" :bordered="false" style="margin-right: 4px;">{{ r }}</NTag>
          </div>

          <NCard class="content-card">
            <div v-if="!editing" class="markdown-body" v-html="readHtml" />
            <div v-else class="editor-layout">
              <div class="editor-pane">
                <div class="pane-title">{{ t('views.knowhow.text_markdown_edit') }}</div>
                <textarea v-model="editContent" class="md-textarea" :placeholder="t('views.knowhow.text_placeholder_md')" />
              </div>
              <div class="preview-pane">
                <div class="pane-title">{{ t('views.knowhow.text_preview') }}</div>
                <div class="markdown-body" v-html="previewHtml" />
              </div>
            </div>
          </NCard>
        </div>

        <div v-else-if="!loading" style="padding: 60px; text-align: center;">
          <p style="color: #999;">{{ t('views.knowhow.text_not_found') }}</p>
          <NButton type="primary" style="margin-top: 16px;" @click="goBack">{{ t('views.knowhow.button_back') }}</NButton>
        </div>
      </NSpin>

      <NModal v-model:show="showDelete" preset="dialog" type="warning"
        :title="t('views.knowhow.modal_title_delete')"
        :content="t('views.knowhow.modal_text_delete')"
        positive-text="OK" negative-text="Cancel"
        :positive-button-props="{ type: 'error', loading: deleting }"
        @positive-click="doDelete"
      />
    </div>
  </CommonPage>
</template>

<style scoped>
.detail-page { padding: 20px 24px; }
.detail-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; }
.header-left { display: flex; align-items: flex-start; gap: 8px; }
.header-info { margin-top: 2px; }
.header-title { display: flex; align-items: center; gap: 8px; font-size: 20px; font-weight: 600; color: #262626; }
.header-meta { display: flex; align-items: center; gap: 12px; margin-top: 6px; font-size: 13px; color: #999; }
.meta-id { font-family: 'Monaco', 'Menlo', monospace; background: #f0f0f0; padding: 1px 6px; border-radius: 4px; font-size: 12px; }
.desc-bar { padding: 12px 16px; background: #f9fafb; border-radius: 8px; font-size: 14px; color: #555; margin-bottom: 12px; line-height: 1.5; }
.resources-bar { padding: 8px 16px; background: #fffbe6; border-radius: 8px; font-size: 13px; margin-bottom: 12px; display: flex; align-items: center; flex-wrap: wrap; gap: 4px; }
.resources-label { color: #666; margin-right: 4px; }
.content-card { border-radius: 12px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06); }
.editor-layout { display: flex; gap: 16px; min-height: 600px; }
.editor-pane, .preview-pane { flex: 1; display: flex; flex-direction: column; border: 1px solid #e8e8e8; border-radius: 8px; overflow: hidden; }
.pane-title { padding: 8px 12px; font-size: 12px; font-weight: 600; color: #666; background: #fafafa; border-bottom: 1px solid #e8e8e8; }
.md-textarea { flex: 1; border: none; outline: none; resize: none; padding: 16px; font-size: 14px; font-family: 'Monaco', 'Menlo', 'Consolas', monospace; line-height: 1.6; background: #fff; }
.markdown-body { padding: 20px; font-size: 14px; line-height: 1.8; color: #333; overflow-y: auto; flex: 1; }
.markdown-body :deep(h1) { font-size: 24px; margin: 16px 0 8px; font-weight: 600; }
.markdown-body :deep(h2) { font-size: 20px; margin: 14px 0 8px; font-weight: 600; border-bottom: 1px solid #eee; padding-bottom: 4px; }
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
.markdown-body :deep(tr:nth-child(even)) { background: #fafafa; }
.markdown-body :deep(blockquote) { border-left: 4px solid #18a058; margin: 12px 0; padding: 8px 16px; color: #666; background: #f9fafb; }
.markdown-body :deep(ul), .markdown-body :deep(ol) { padding-left: 24px; margin: 8px 0; }
@media (max-width: 768px) { .editor-layout { flex-direction: column; } }
</style>
