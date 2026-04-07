<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { NButton, NCard, NSpace, NInput, NIcon, NTag, NEmpty, NSpin, NModal, NForm, NFormItem, NGrid, NGi } from 'naive-ui'
import { useMessage } from 'naive-ui'
import { useI18n } from 'vue-i18n'
import CommonPage from '@/components/page/CommonPage.vue'
import api from '@/api'

const { t } = useI18n()
const router = useRouter()
const message = useMessage()
const loading = ref(false)
const searchText = ref('')
const documents = ref([])
const showCreate = ref(false)
const creating = ref(false)
const createForm = ref({
  id: '',
  name: '',
  description: '',
  authors: '',
  version: '1.0',
  license: 'CC BY 4.0',
  commercial_use: '✅ Allowed',
})

const filteredDocs = computed(() => {
  if (!searchText.value) return documents.value
  const s = searchText.value.toLowerCase()
  return documents.value.filter(d =>
    d.name.toLowerCase().includes(s) ||
    d.description.toLowerCase().includes(s) ||
    d.id.toLowerCase().includes(s)
  )
})

async function loadDocuments() {
  loading.value = true
  try {
    const res = await api.getKnowHowList()
    if (res.code === 200) {
      documents.value = res.data || []
    }
  } catch (e) {
    message.error(t('views.knowhow.message_load_failed'))
  } finally {
    loading.value = false
  }
}

function goDetail(doc) {
  router.push(`/knowhow/${doc.id}`)
}

function openCreate() {
  createForm.value = {
    id: '',
    name: '',
    description: '',
    authors: '',
    version: '1.0',
    license: 'CC BY 4.0',
    commercial_use: '✅ Allowed',
  }
  showCreate.value = true
}

async function doCreate() {
  if (!createForm.value.id || !createForm.value.name) {
    message.warning(t('views.knowhow.message_id_name_required'))
    return
  }
  creating.value = true
  try {
    const res = await api.createKnowHow(createForm.value)
    if (res.code === 200) {
      message.success(t('views.knowhow.message_create_success'))
      showCreate.value = false
      await loadDocuments()
      router.push(`/knowhow/${createForm.value.id}`)
    } else {
      message.error(res.message || t('views.knowhow.message_create_failed'))
    }
  } catch (e) {
    message.error(e?.response?.data?.detail || t('views.knowhow.message_create_failed'))
  } finally {
    creating.value = false
  }
}

onMounted(() => {
  loadDocuments()
})
</script>

<template>
  <CommonPage>
    <div class="knowhow-page">
      <!-- Header -->
      <div class="page-header">
        <div class="header-left">
          <h2 class="page-title">📚 {{ t('views.knowhow.title_page') }}</h2>
          <span class="doc-count">{{ t('views.knowhow.text_doc_count', { count: filteredDocs.length }) }}</span>
        </div>
        <NSpace>
          <NInput
            v-model:value="searchText"
            :placeholder="t('views.knowhow.placeholder_search')"
            clearable
            style="width: 240px;"
          >
            <template #prefix>
              <NIcon size="16">
                <svg viewBox="0 0 24 24"><path fill="currentColor" d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5A6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5S14 7.01 14 9.5S11.99 14 9.5 14z"/></svg>
              </NIcon>
            </template>
          </NInput>
          <NButton type="primary" @click="openCreate">
            {{ t('views.knowhow.button_create') }}
          </NButton>
        </NSpace>
      </div>

      <!-- Content -->
      <NSpin :show="loading">
        <NEmpty v-if="filteredDocs.length === 0 && !loading" :description="t('views.knowhow.text_no_docs')" />
        <NGrid v-else :cols="1" :x-gap="16" :y-gap="16">
          <NGi v-for="doc in filteredDocs" :key="doc.id">
            <NCard hoverable class="doc-card" @click="goDetail(doc)">
              <div class="doc-card-content">
                <div class="doc-main">
                  <div class="doc-title">
                    <span>{{ doc.name }}</span>
                    <NTag v-if="doc.version" size="tiny" :bordered="false" type="info" style="margin-left: 8px;">
                      v{{ doc.version }}
                    </NTag>
                    <NTag v-if="doc.commercial_use && doc.commercial_use.includes('✅')" size="tiny" :bordered="false" type="success" style="margin-left: 4px;">
                      {{ t('views.knowhow.label_commercial') }}
                    </NTag>
                  </div>
                  <div class="doc-desc">{{ doc.description || t('views.knowhow.text_no_description') }}</div>
                  <div class="doc-meta">
                    <span v-if="doc.authors" class="meta-item">👤 {{ doc.authors }}</span>
                    <span v-if="doc.license" class="meta-item">📜 {{ doc.license }}</span>
                    <span v-if="doc.last_updated" class="meta-item">🕐 {{ doc.last_updated }}</span>
                    <span class="meta-item id-badge">{{ doc.id }}</span>
                  </div>
                </div>
                <div class="doc-arrow">→</div>
              </div>
            </NCard>
          </NGi>
        </NGrid>
      </NSpin>

      <!-- Create Modal -->
      <NModal
        v-model:show="showCreate"
        preset="dialog"
        :title="t('views.knowhow.modal_title_create')"
        positive-text="OK"
        negative-text="Cancel"
        :positive-button-props="{ loading: creating }"
        @positive-click="doCreate"
        style="width: 560px;"
      >
        <NForm label-placement="left" label-width="80">
          <NFormItem :label="t('views.knowhow.label_id')" required>
            <NInput v-model:value="createForm.id" :placeholder="t('views.knowhow.placeholder_id')" />
          </NFormItem>
          <NFormItem :label="t('views.knowhow.label_name')" required>
            <NInput v-model:value="createForm.name" :placeholder="t('views.knowhow.placeholder_name')" />
          </NFormItem>
          <NFormItem :label="t('views.knowhow.label_description')">
            <NInput v-model:value="createForm.description" type="textarea" :rows="2" :placeholder="t('views.knowhow.placeholder_description')" />
          </NFormItem>
          <NFormItem :label="t('views.knowhow.label_authors')">
            <NInput v-model:value="createForm.authors" :placeholder="t('views.knowhow.placeholder_authors')" />
          </NFormItem>
          <NFormItem :label="t('views.knowhow.label_version')">
            <NInput v-model:value="createForm.version" :placeholder="t('views.knowhow.placeholder_version')" />
          </NFormItem>
          <NFormItem :label="t('views.knowhow.label_license')">
            <NInput v-model:value="createForm.license" :placeholder="t('views.knowhow.placeholder_license')" />
          </NFormItem>
        </NForm>
      </NModal>
    </div>
  </CommonPage>
</template>

<style scoped>
.knowhow-page { padding: 20px 24px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.header-left { display: flex; align-items: baseline; gap: 12px; }
.page-title { font-size: 20px; font-weight: 600; margin: 0; }
.doc-count { font-size: 13px; color: #999; }
.doc-card { cursor: pointer; border-radius: 10px; transition: box-shadow 0.2s; }
.doc-card:hover { box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); }
.doc-card-content { display: flex; justify-content: space-between; align-items: center; }
.doc-main { flex: 1; }
.doc-title { font-size: 16px; font-weight: 600; color: #262626; display: flex; align-items: center; }
.doc-desc { font-size: 14px; color: #666; margin-top: 6px; line-height: 1.5; }
.doc-meta { display: flex; align-items: center; gap: 16px; margin-top: 8px; font-size: 12px; color: #999; }
.id-badge { font-family: 'Monaco', 'Menlo', monospace; background: #f0f0f0; padding: 1px 6px; border-radius: 4px; }
.doc-arrow { font-size: 20px; color: #ccc; margin-left: 16px; }
</style>
