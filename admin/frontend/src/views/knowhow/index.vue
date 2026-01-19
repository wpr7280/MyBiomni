<script setup>
import { ref, onMounted, h } from 'vue'
import { NButton, NCard, NInput, NDataTable, NTag, NIcon, NEmpty, NSpace } from 'naive-ui'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import CommonPage from '@/components/page/CommonPage.vue'
import { useMessage } from 'naive-ui'
import api from '@/api'

const { t } = useI18n()
const router = useRouter()
const message = useMessage()

const loading = ref(false)
const searchKeyword = ref('')
const documents = ref([])
const pagination = ref({
  page: 1,
  pageSize: 20,
  itemCount: 0,
})

// 表格列定义
const columns = [
  {
    title: () => t('views.knowhow.label_title'),
    key: 'title',
    ellipsis: { tooltip: true },
  },
  {
    title: () => t('views.knowhow.label_category'),
    key: 'category',
    width: 120,
    render: (row) => row.category || '-'
  },
  {
    title: () => t('views.knowhow.label_tags'),
    key: 'tags',
    width: 200,
    render: (row) => {
      if (!row.tags) return '-'
      const tagList = row.tags.split(',').slice(0, 3)
      return h(NSpace, { size: 4 }, {
        default: () => tagList.map(tag => 
          h(NTag, { size: 'small', type: 'info' }, { default: () => tag.trim() })
        )
      })
    }
  },
  {
    title: () => t('views.knowhow.label_commercial_use'),
    key: 'commercialUse',
    width: 100,
    render: (row) => {
      return h(NTag, {
        type: row.commercialUse === 1 ? 'success' : 'warning',
        size: 'small'
      }, {
        default: () => row.commercialUse === 1 
          ? t('views.knowhow.text_allowed') 
          : t('views.knowhow.text_not_allowed')
      })
    }
  },
  {
    title: () => t('views.knowhow.label_author'),
    key: 'authors',
    width: 150,
    ellipsis: { tooltip: true },
    render: (row) => row.authors || '-'
  },
  {
    title: () => t('views.conversations.label_actions'),
    key: 'actions',
    width: 120,
    render: (row) => {
      return h(NButton, {
        size: 'small',
        type: 'primary',
        ghost: true,
        onClick: () => viewDetail(row.id)
      }, { default: () => t('views.knowhow.button_view_detail') })
    }
  }
]

// 加载文档列表
async function loadDocuments() {
  loading.value = true
  try {
    const res = await api.getKnowHowList({
      page: pagination.value.page,
      pageSize: pagination.value.pageSize,
      keyword: searchKeyword.value
    })
    if (res.code === 200) {
      documents.value = res.data.items || []
      pagination.value.itemCount = res.data.total || 0
    }
  } catch (error) {
    message.error('加载失败')
  } finally {
    loading.value = false
  }
}

// 搜索
function handleSearch() {
  pagination.value.page = 1
  loadDocuments()
}

// 查看详情
function viewDetail(id) {
  router.push(`/knowhow/${id}`)
}

// 分页变化
function handlePageChange(page) {
  pagination.value.page = page
  loadDocuments()
}

onMounted(() => {
  loadDocuments()
})
</script>

<template>
  <CommonPage :show-header="false">
    <div class="knowhow-container">
      <NCard class="knowhow-card" :title="t('views.knowhow.label_knowhow')">
        <template #header-extra>
          <NIcon size="20" color="#18a058">
            <svg viewBox="0 0 24 24">
              <path fill="currentColor" d="M18 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zM6 4h5v8l-2.5-1.5L6 12V4z"/>
            </svg>
          </NIcon>
        </template>

        <div class="search-bar">
          <NInput
            v-model:value="searchKeyword"
            :placeholder="t('views.knowhow.placeholder_search')"
            clearable
            @keyup.enter="handleSearch"
            style="max-width: 400px;"
          >
            <template #prefix>
              <NIcon>
                <svg viewBox="0 0 24 24">
                  <path fill="currentColor" d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5A6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5S14 7.01 14 9.5S11.99 14 9.5 14z"/>
                </svg>
              </NIcon>
            </template>
          </NInput>
          <NButton type="primary" @click="handleSearch" style="margin-left: 12px;">
            搜索
          </NButton>
        </div>

        <NDataTable
          :columns="columns"
          :data="documents"
          :loading="loading"
          :pagination="pagination"
          :bordered="false"
          @update:page="handlePageChange"
          style="margin-top: 16px;"
        >
          <template #empty>
            <NEmpty description="暂无文档" />
          </template>
        </NDataTable>
      </NCard>
    </div>
  </CommonPage>
</template>

<style scoped>
.knowhow-container {
  padding: 20px 24px;
}

.knowhow-card {
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.knowhow-card :deep(.n-card-header) {
  padding: 16px 24px;
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
  border-bottom: 1px solid #f0f0f0;
}

.search-bar {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

@media (max-width: 768px) {
  .knowhow-container {
    padding: 12px 16px;
  }
  
  .search-bar {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }
  
  .search-bar .n-input {
    max-width: none !important;
  }
  
  .search-bar .n-button {
    margin-left: 0 !important;
  }
}
</style>
