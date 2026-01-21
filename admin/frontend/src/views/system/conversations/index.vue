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
  { label: '全部', value: null },
  { label: '活跃', value: 'active' },
  { label: '已归档', value: 'archived' }
]

// 表格列定义
const columns = [
  {
    title: '对话ID',
    key: 'id',
    width: 80,
  },
  {
    title: '用户',
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
    title: '对话标题',
    key: 'title',
    ellipsis: {
      tooltip: true
    }
  },
  {
    title: '状态',
    key: 'status',
    width: 100,
    render: (row) => {
      return h(NTag, {
        type: row.status === 'active' ? 'success' : 'default',
        size: 'small'
      }, {
        default: () => row.status === 'active' ? '活跃' : '已归档'
      })
    }
  },
  {
    title: '消息数',
    key: 'messageCount',
    width: 100,
    render: (row) => row.messageCount || 0
  },
  {
    title: 'Tokens',
    key: 'totalTokens',
    width: 100,
    render: (row) => {
      const tokens = row.totalTokens || 0
      return h('span', {}, `${(tokens / 1000).toFixed(1)}K`)
    }
  },
  {
    title: '最后消息',
    key: 'lastMessageAt',
    width: 180,
    render: (row) => row.lastMessageAt ? new Date(row.lastMessageAt).toLocaleString() : '-'
  },
  {
    title: '创建时间',
    key: 'createdAt',
    width: 180,
    render: (row) => row.createdAt ? new Date(row.createdAt).toLocaleString() : '-'
  },
  {
    title: '操作',
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
          }, { default: () => '详情' }),
          h(NPopconfirm, {
            onPositiveClick: () => deleteConversation(row.id)
          }, {
            default: () => '确定要删除这个对话吗？',
            trigger: () => h(NButton, {
              size: 'small',
              type: 'error',
              ghost: true
            }, { default: () => '删除' })
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
    message.error('加载失败')
  } finally {
    loading.value = false
  }
}

// 删除对话
async function deleteConversation(id) {
  try {
    await api.deleteAdminConversation({ conversationId: id })
    message.success('删除成功')
    loadConversations()
  } catch (error) {
    message.error('删除失败')
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
    message.error('加载详情失败')
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
      <NCard class="conversations-card" title="对话记录管理">
        <template #header-extra>
          <div style="display: flex; align-items: center; gap: 8px;">
            <NIcon size="20" color="#18a058">
              <svg viewBox="0 0 24 24">
                <path fill="currentColor" d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/>
              </svg>
            </NIcon>
            <span style="font-size: 14px; color: #666;">
              共 {{ pagination.itemCount }} 条对话记录
            </span>
          </div>
        </template>

        <!-- 搜索栏 -->
        <div class="search-bar">
          <NInput
            v-model:value="searchKeyword"
            placeholder="搜索对话标题..."
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
            placeholder="状态"
            clearable
            style="width: 150px;"
          />
          
          <NDatePicker
            v-model:value="dateRange"
            type="daterange"
            clearable
            placeholder="选择日期范围"
            style="width: 280px;"
          />
          
          <NButton type="primary" @click="handleSearch">
            搜索
          </NButton>
          
          <NButton @click="handleReset">
            重置
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
            <NEmpty description="暂无对话记录" />
          </template>
        </NDataTable>
      </NCard>

      <!-- 对话详情弹窗 -->
      <NModal
        v-model:show="showDetailModal"
        preset="card"
        title="对话详情"
        style="width: 90%; max-width: 1200px;"
        :segmented="{ content: true }"
      >
        <NSpin :show="detailLoading">
          <div v-if="conversationDetail" style="min-height: 400px;">
            <!-- 对话基本信息 -->
            <div style="padding: 16px; background: #f8f9fa; border-radius: 8px; margin-bottom: 20px;">
              <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px;">
                <div>
                  <div style="font-size: 12px; color: #999; margin-bottom: 4px;">对话标题</div>
                  <div style="font-weight: 600;">{{ conversationDetail.title }}</div>
                </div>
                <div>
                  <div style="font-size: 12px; color: #999; margin-bottom: 4px;">用户</div>
                  <div>{{ conversationDetail.username }} ({{ conversationDetail.userEmail }})</div>
                </div>
                <div>
                  <div style="font-size: 12px; color: #999; margin-bottom: 4px;">消息数</div>
                  <div>{{ conversationDetail.messageCount }} 条</div>
                </div>
                <div>
                  <div style="font-size: 12px; color: #999; margin-bottom: 4px;">Token 使用</div>
                  <div>{{ ((conversationDetail.totalTokens || 0) / 1000).toFixed(1) }}K</div>
                </div>
                <div>
                  <div style="font-size: 12px; color: #999; margin-bottom: 4px;">创建时间</div>
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
                          {{ msg.role === 'user' ? '用户' : 'AI 助手' }}
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
              <NEmpty v-else description="暂无消息" />
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
