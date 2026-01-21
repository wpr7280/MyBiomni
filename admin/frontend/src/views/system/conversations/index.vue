<script setup>
import { ref, onMounted, h } from 'vue'
import { NButton, NCard, NInput, NDataTable, NPopconfirm, NTag, NIcon, NEmpty, NSpace, NDatePicker, NSelect, NModal, NSpin, NScrollbar } from 'naive-ui'
import { useI18n } from 'vue-i18n'
import CommonPage from '@/components/page/CommonPage.vue'
import { useMessage } from 'naive-ui'
import api from '@/api'

const { t } = useI18n()
const message = useMessage()

const loading = ref(false)
const searchKeyword = ref('')
const searchUserId = ref(null)
const searchStatus = ref(null)
const dateRange = ref(null)
const conversations = ref([])
const pagination = ref({
  page: 1,
  pageSize: 20,
  itemCount: 0,
})

// 详情弹窗
const showDetailModal = ref(false)
const detailLoading = ref(false)
const conversationDetail = ref(null)

const statusOptions = [
  { label: t('views.system.conversations.status_all'), value: null },
  { label: t('views.system.conversations.status_active'), value: 'active' },
  { label: t('views.system.conversations.status_archived'), value: 'archived' }
]

// 表格列定义
const columns = [
  {
    title: () => t('views.system.conversations.label_conversation_id'),
    key: 'id',
    width: 80,
  },
  {
    title: () => t('views.system.conversations.label_user'),
    key: 'user',
    width: 200,
    render: (row) => {
      return h('div', { style: 'font-size: 12px;' }, [
        h('div', { style: 'font-weight: 600; margin-bottom: 2px;' }, row.username || '-'),
        h('div', { style: 'color: #999;' }, row.userEmail || '-')
      ])
    }
  },
  {
    title: () => t('views.system.conversations.label_title'),
    key: 'title',
    ellipsis: {
      tooltip: true
    }
  },
  {
    title: () => t('views.system.conversations.label_status'),
    key: 'status',
    width: 100,
    render: (row) => {
      return h(NTag, {
        type: row.status === 'active' ? 'success' : 'default',
        size: 'small'
      }, {
        default: () => row.status === 'active' ? t('views.system.conversations.status_active') : t('views.system.conversations.status_archived')
      })
    }
  },
  {
    title: () => t('views.system.conversations.label_message_count'),
    key: 'messageCount',
    width: 100,
    render: (row) => row.messageCount || 0
  },
  {
    title: () => t('views.system.conversations.label_tokens'),
    key: 'totalTokens',
    width: 100,
    render: (row) => {
      const tokens = row.totalTokens || 0
      return h('span', {}, `${(tokens / 1000).toFixed(1)}K`)
    }
  },
  {
    title: () => t('views.system.conversations.label_last_message'),
    key: 'lastMessageAt',
    width: 180,
    render: (row) => row.lastMessageAt ? new Date(row.lastMessageAt).toLocaleString() : '-'
  },
  {
    title: () => t('views.system.conversations.label_created_at'),
    key: 'createdAt',
    width: 180,
    render: (row) => row.createdAt ? new Date(row.createdAt).toLocaleString() : '-'
  },
  {
    title: () => t('views.system.conversations.label_actions'),
    key: 'actions',
    width: 180,
    fixed: 'right',
    render: (row) => {
      return h(NSpace, { size: 4 }, {
        default: () => [
          h(NButton, {
            size: 'small',
            type: 'primary',
            ghost: true,
            onClick: () => viewDetail(row.id)
          }, { default: () => t('views.system.conversations.button_detail') }),
          h(NPopconfirm, {
            onPositiveClick: () => deleteConversation(row.id)
          }, {
            default: () => t('views.system.conversations.message_delete_confirm'),
            trigger: () => h(NButton, {
              size: 'small',
              type: 'error',
              ghost: true
            }, { default: () => t('views.system.conversations.button_delete') })
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
    const params = {
      currentPage: pagination.value.page,
      pageSize: pagination.value.pageSize,
      keyword: searchKeyword.value || undefined,
      userId: searchUserId.value || undefined,
      status: searchStatus.value || undefined
    }
    
    // 添加日期范围
    if (dateRange.value && dateRange.value.length === 2) {
      params.startDate = new Date(dateRange.value[0]).toISOString().split('T')[0]
      params.endDate = new Date(dateRange.value[1]).toISOString().split('T')[0]
    }
    
    const res = await api.getAdminConversationList(params)
    if (res.code === 200) {
      conversations.value = res.data || []
      pagination.value.itemCount = res.totalCount || 0
    }
  } catch (error) {
    message.error(t('views.system.conversations.message_load_failed'))
  } finally {
    loading.value = false
  }
}

// 删除对话
async function deleteConversation(id) {
  try {
    await api.deleteAdminConversation({ conversationId: id })
    message.success(t('views.system.conversations.message_delete_success'))
    loadConversations()
  } catch (error) {
    message.error(t('views.system.conversations.message_delete_failed'))
  }
}

// 查看详情
async function viewDetail(id) {
  showDetailModal.value = true
  detailLoading.value = true
  conversationDetail.value = null
  
  try {
    const res = await api.getAdminConversationDetail({ conversationId: id })
    if (res.code === 200) {
      conversationDetail.value = res.data
    }
  } catch (error) {
    message.error(t('views.system.conversations.message_detail_load_failed'))
  } finally {
    detailLoading.value = false
  }
}

function handleSearch() {
  pagination.value.page = 1
  loadConversations()
}

function handleReset() {
  searchKeyword.value = ''
  searchUserId.value = null
  searchStatus.value = null
  dateRange.value = null
  pagination.value.page = 1
  loadConversations()
}

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
      <NCard class="conversations-card" :title="t('views.system.conversations.label_conversation_management')">
        <template #header-extra>
          <div style="display: flex; align-items: center; gap: 8px;">
            <NIcon size="20" color="#18a058">
              <svg viewBox="0 0 24 24">
                <path fill="currentColor" d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/>
              </svg>
            </NIcon>
            <span style="font-size: 14px; color: #666;">
              {{ t('views.system.conversations.text_total_records', { count: pagination.itemCount }) }}
            </span>
          </div>
        </template>

        <!-- 搜索栏 -->
        <div class="search-bar">
          <NInput
            v-model:value="searchKeyword"
            :placeholder="t('views.system.conversations.placeholder_search')"
            clearable
            @keyup.enter="handleSearch"
            style="max-width: 300px;"
          >
            <template #prefix>
              <NIcon>
                <svg viewBox="0 0 24 24">
                  <path fill="currentColor" d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5A6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5S14 7.01 14 9.5S11.99 14 9.5 14z"/>
                </svg>
              </NIcon>
            </template>
          </NInput>
          
          <NSelect
            v-model:value="searchStatus"
            :options="statusOptions"
            :placeholder="t('views.system.conversations.placeholder_status')"
            clearable
            style="width: 150px;"
          />
          
          <NDatePicker
            v-model:value="dateRange"
            type="daterange"
            clearable
            :placeholder="t('views.system.conversations.placeholder_date_range')"
            style="width: 280px;"
          />
          
          <NButton type="primary" @click="handleSearch">
            {{ t('views.system.conversations.button_search') }}
          </NButton>
          
          <NButton @click="handleReset">
            {{ t('views.system.conversations.button_reset') }}
          </NButton>
        </div>

        <!-- 数据表格 -->
        <NDataTable
          :columns="columns"
          :data="conversations"
          :loading="loading"
          :pagination="pagination"
          :bordered="false"
          :scroll-x="1400"
          @update:page="handlePageChange"
          style="margin-top: 16px;"
        >
          <template #empty>
            <NEmpty :description="t('views.system.conversations.text_no_records')" />
          </template>
        </NDataTable>
      </NCard>

      <!-- 对话详情弹窗 -->
      <NModal
        v-model:show="showDetailModal"
        preset="card"
        :title="t('views.system.conversations.modal_title_detail')"
        style="width: 90%; max-width: 1200px;"
        :segmented="{ content: true }"
      >
        <NSpin :show="detailLoading">
          <div v-if="conversationDetail" style="min-height: 400px;">
            <!-- 对话基本信息 -->
            <div style="padding: 16px; background: #f8f9fa; border-radius: 8px; margin-bottom: 20px;">
              <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px;">
                <div>
                  <div style="font-size: 12px; color: #999; margin-bottom: 4px;">{{ t('views.system.conversations.detail_label_title') }}</div>
                  <div style="font-weight: 600;">{{ conversationDetail.title }}</div>
                </div>
                <div>
                  <div style="font-size: 12px; color: #999; margin-bottom: 4px;">{{ t('views.system.conversations.detail_label_user') }}</div>
                  <div>{{ conversationDetail.username }} ({{ conversationDetail.userEmail }})</div>
                </div>
                <div>
                  <div style="font-size: 12px; color: #999; margin-bottom: 4px;">{{ t('views.system.conversations.detail_label_message_count') }}</div>
                  <div>{{ conversationDetail.messageCount }} {{ t('views.system.conversations.detail_text_messages') }}</div>
                </div>
                <div>
                  <div style="font-size: 12px; color: #999; margin-bottom: 4px;">{{ t('views.system.conversations.detail_label_token_usage') }}</div>
                  <div>{{ ((conversationDetail.totalTokens || 0) / 1000).toFixed(1) }}K</div>
                </div>
                <div>
                  <div style="font-size: 12px; color: #999; margin-bottom: 4px;">{{ t('views.system.conversations.detail_label_created_at') }}</div>
                  <div>{{ new Date(conversationDetail.createdAt).toLocaleString() }}</div>
                </div>
              </div>
            </div>

            <!-- 消息列表 -->
            <div style="max-height: 600px; overflow-y: auto;">
              <div v-if="conversationDetail.messages && conversationDetail.messages.length > 0">
                <div
                  v-for="(msg, index) in conversationDetail.messages"
                  :key="msg.id"
                  style="margin-bottom: 20px;"
                >
                  <div style="display: flex; align-items: flex-start; gap: 12px;">
                    <!-- 头像 -->
                    <div
                      :style="{
                        width: '36px',
                        height: '36px',
                        borderRadius: '50%',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: '18px',
                        flexShrink: 0,
                        background: msg.role === 'user' ? '#52c41a' : '#1890ff'
                      }"
                    >
                      {{ msg.role === 'user' ? '👤' : '🤖' }}
                    </div>

                    <!-- 消息内容 -->
                    <div style="flex: 1; min-width: 0;">
                      <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                        <span style="font-weight: 600; font-size: 14px;">
                          {{ msg.role === 'user' ? t('views.system.conversations.text_user_message') : t('views.system.conversations.text_ai_message') }}
                        </span>
                        <span style="font-size: 12px; color: #999;">
                          {{ new Date(msg.createdAt).toLocaleString() }}
                        </span>
                        <NTag v-if="msg.tokens" size="small" type="info">
                          {{ msg.tokens }} tokens
                        </NTag>
                      </div>
                      <div
                        :style="{
                          padding: '12px 16px',
                          borderRadius: '8px',
                          background: msg.role === 'user' ? '#f0f0f0' : '#e6f7ff',
                          whiteSpace: 'pre-wrap',
                          wordBreak: 'break-word',
                          lineHeight: '1.6'
                        }"
                      >
                        {{ msg.content }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <NEmpty v-else :description="t('views.system.conversations.text_no_messages')" />
            </div>
          </div>
        </NSpin>
      </NModal>
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
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

@media (max-width: 768px) {
  .conversations-container {
    padding: 12px 16px;
  }
  
  .search-bar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-bar .n-input,
  .search-bar .n-select,
  .search-bar .n-date-picker {
    max-width: none !important;
    width: 100% !important;
  }
}
</style>
