<script setup>
import { ref, onMounted } from 'vue'
import { NButton, NCard, NSpace, NInput, NDataTable, NPopconfirm, NTag, NIcon, NEmpty } from 'naive-ui'
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
const conversations = ref([])
const pagination = ref({
  page: 1,
  pageSize: 20,
  itemCount: 0,
})

// 表格列定义
const columns = [
  {
    title: () => t('views.conversations.label_title'),
    key: 'title',
    ellipsis: { tooltip: true },
  },
  {
    title: () => t('views.conversations.label_status'),
    key: 'status',
    width: 100,
    render: (row) => {
      const statusMap = {
        active: { type: 'info', text: '进行中' },
        completed: { type: 'success', text: '已完成' },
        failed: { type: 'error', text: '失败' },
        cancelled: { type: 'warning', text: '已取消' },
      }
      const status = statusMap[row.status] || { type: 'default', text: row.status }
      return h(NTag, { type: status.type, size: 'small' }, { default: () => status.text })
    }
  },
  {
    title: () => t('views.conversations.label_message_count'),
    key: 'messageCount',
    width: 100,
  },
  {
    title: () => t('views.conversations.label_tokens'),
    key: 'totalTokens',
    width: 120,
  },
  {
    title: () => t('views.conversations.label_created_at'),
    key: 'createdAt',
    width: 180,
    render: (row) => row.createdAt ? new Date(row.createdAt).toLocaleString() : '-'
  },
  {
    title: () => t('views.conversations.label_actions'),
    key: 'actions',
    width: 180,
    render: (row) => {
      return h(NSpace, {}, {
        default: () => [
          h(NButton, {
            size: 'small',
            type: 'primary',
            ghost: true,
            onClick: () => viewDetail(row.id)
          }, { default: () => t('views.conversations.button_view_detail') }),
          h(NPopconfirm, {
            onPositiveClick: () => deleteConversation(row.id)
          }, {
            default: () => t('views.conversations.message_delete_confirm'),
            trigger: () => h(NButton, {
              size: 'small',
              type: 'error',
              ghost: true
            }, { default: () => t('views.conversations.button_delete') })
          })
        ]
      })
    }
  }
]

// 加载对话列表
async function loadConversations() {
  loading.value = true
  try {
    const res = await api.getConversations({
      page: pagination.value.page,
      pageSize: pagination.value.pageSize,
      keyword: searchKeyword.value
    })
    if (res.code === 200) {
      conversations.value = res.data.items || []
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
  loadConversations()
}

// 查看详情
function viewDetail(id) {
  router.push(`/conversations/${id}`)
}

// 删除对话
async function deleteConversation(id) {
  try {
    const res = await api.deleteConversation(id)
    if (res.code === 200) {
      message.success(t('views.conversations.message_delete_success'))
      loadConversations()
    }
  } catch (error) {
    message.error('删除失败')
  }
}

// 创建对话
function createConversation() {
  router.push('/conversations/create')
}

// 分页变化
function handlePageChange(page) {
  pagination.value.page = page
  loadConversations()
}

onMounted(() => {
  loadConversations()
})
</script>

<template>
  <CommonPage :show-header="false">
    <div class="conversations-container">
      <NCard class="conversations-card" :title="t('views.conversations.label_my_conversations')">
        <template #header-extra>
          <NButton type="primary" @click="createConversation">
            <template #icon>
              <NIcon>
                <svg viewBox="0 0 24 24">
                  <path fill="currentColor" d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
                </svg>
              </NIcon>
            </template>
            {{ t('views.conversations.button_create_conversation') }}
          </NButton>
        </template>

        <div class="search-bar">
          <NInput
            v-model:value="searchKeyword"
            :placeholder="t('views.conversations.placeholder_search')"
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
          :data="conversations"
          :loading="loading"
          :pagination="pagination"
          :bordered="false"
          @update:page="handlePageChange"
          style="margin-top: 16px;"
        >
          <template #empty>
            <NEmpty description="暂无对话记录" />
          </template>
        </NDataTable>
      </NCard>
    </div>
  </CommonPage>
</template>

<style scoped>
.conversations-container {
  padding: 20px 24px;
}

.conversations-card {
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.conversations-card :deep(.n-card-header) {
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
  .conversations-container {
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
