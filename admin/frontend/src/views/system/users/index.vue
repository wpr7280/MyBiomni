<script setup>
import { ref, onMounted, h } from 'vue'
import { NButton, NCard, NInput, NDataTable, NPopconfirm, NTag, NIcon, NEmpty, NSpace, NModal, NForm, NFormItem, NSelect, NAlert } from 'naive-ui'
import { useI18n } from 'vue-i18n'
import CommonPage from '@/components/page/CommonPage.vue'
import { useMessage } from 'naive-ui'
import api from '@/api'

const { t } = useI18n()
const message = useMessage()

const loading = ref(false)
const searchKeyword = ref('')
const users = ref([])
const pagination = ref({
  page: 1,
  pageSize: 20,
  itemCount: 0,
})

// 用户弹窗
const showUserModal = ref(false)
const userFormRef = ref(null)
const userForm = ref({
  id: null,
  username: '',
  email: '',
  password: '',
  realName: '',
  role: 'user',
  status: 1
})

// 配额弹窗
const showQuotaModal = ref(false)
const quotaFormRef = ref(null)
const quotaForm = ref({
  userId: null,
  username: '',
  totalTokenLimit: 1000000,
  totalTokenUsed: 0
})

const roleOptions = [
  { label: t('views.system.users.role_admin'), value: 'admin' },
  { label: t('views.system.users.role_user'), value: 'user' }
]

const statusOptions = [
  { label: t('views.system.users.status_active'), value: 1 },
  { label: t('views.system.users.status_disabled'), value: 0 }
]

// 表格列定义
const columns = [
  {
    title: () => t('views.system.users.label_username'),
    key: 'username',
  },
  {
    title: () => t('views.system.users.label_email'),
    key: 'email',
  },
  {
    title: () => t('views.system.users.label_role'),
    key: 'role',
    width: 100,
    render: (row) => {
      return h(NTag, {
        type: row.role === 'admin' ? 'success' : 'info',
        size: 'small'
      }, {
        default: () => row.role === 'admin' 
          ? t('views.system.users.role_admin')
          : t('views.system.users.role_user')
      })
    }
  },
  {
    title: () => t('views.system.users.label_token_quota'),
    key: 'quota',
    width: 140,
    render: (row) => {
      const limit = row.totalTokenLimit || 1000000
      const used = row.totalTokenUsed || 0
      const percent = (used / limit * 100).toFixed(1)
      return h('div', { style: 'font-size: 12px;' }, [
        h('div', { style: 'margin-bottom: 2px;' }, `${(used / 1000).toFixed(0)}K / ${(limit / 1000).toFixed(0)}K`),
        h('div', { 
          style: `color: ${percent > 80 ? '#d03050' : percent > 50 ? '#f0a020' : '#18a058'};` 
        }, `${percent}%`)
      ])
    }
  },
  {
    title: () => t('views.system.users.label_status'),
    key: 'status',
    width: 100,
    render: (row) => {
      return h(NTag, {
        type: row.status === 1 ? 'success' : 'error',
        size: 'small'
      }, {
        default: () => row.status === 1
          ? t('views.system.users.status_active')
          : t('views.system.users.status_disabled')
      })
    }
  },
  {
    title: () => t('views.system.users.label_created_at'),
    key: 'createdAt',
    width: 180,
    render: (row) => row.createdAt ? new Date(row.createdAt).toLocaleString() : '-'
  },
  {
    title: () => t('views.conversations.label_actions'),
    key: 'actions',
    width: 260,
    render: (row) => {
      return h(NSpace, { size: 4 }, {
        default: () => [
          h(NButton, {
            size: 'small',
            type: 'primary',
            ghost: true,
            onClick: () => editUser(row)
          }, { default: () => t('views.system.users.button_edit') }),
          h(NButton, {
            size: 'small',
            type: 'info',
            ghost: true,
            onClick: () => manageQuota(row)
          }, { default: () => t('views.system.users.button_quota') }),
          h(NPopconfirm, {
            onPositiveClick: () => deleteUser(row.id)
          }, {
            default: () => t('views.system.users.message_delete_confirm'),
            trigger: () => h(NButton, {
              size: 'small',
              type: 'error',
              ghost: true
            }, { default: () => t('views.system.users.button_delete') })
          })
        ]
      })
    }
  }
]

// 加载用户列表
async function loadUsers() {
  loading.value = true
  try {
    const res = await api.getUserList({
      currentPage: pagination.value.page,
      pageSize: pagination.value.pageSize,
      keyword: searchKeyword.value
    })
    if (res.code === 200) {
      users.value = res.data || []
      pagination.value.itemCount = res.totalCount || 0
    }
  } catch (error) {
    message.error(t('views.system.users.message_load_failed'))
  } finally {
    loading.value = false
  }
}

// 创建用户
function createUser() {
  userForm.value = {
    id: null,
    username: '',
    email: '',
    password: '',  // 留空，让用户看到提示
    realName: '',
    role: 'user',
    status: 1
  }
  showUserModal.value = true
}

// 编辑用户
function editUser(user) {
  userForm.value = {
    id: user.id,
    username: user.username,
    email: user.email,
    password: '',
    realName: user.realName,
    role: user.role,
    status: user.status
  }
  showUserModal.value = true
}

// 保存用户
async function saveUser() {
  userFormRef.value?.validate(async (errors) => {
    if (errors) return
    
    try {
      if (userForm.value.id) {
        await api.updateUser({
          userId: userForm.value.id,
          ...userForm.value
        })
      } else {
        await api.createUser(userForm.value)
      }
      message.success(t('views.system.users.message_create_success'))
      showUserModal.value = false
      loadUsers()
    } catch (error) {
      message.error(t('views.system.users.message_operation_failed'))
    }
  })
}

// 删除用户
async function deleteUser(id) {
  try {
    await api.deleteUser({ userId: id })
    message.success(t('views.system.users.message_delete_success'))
    loadUsers()
  } catch (error) {
    message.error(t('views.system.users.message_operation_failed'))
  }
}

// 管理配额
function manageQuota(user) {
  quotaForm.value = {
    userId: user.id,
    username: user.username,
    totalTokenLimit: user.totalTokenLimit || 1000000,
    totalTokenUsed: user.totalTokenUsed || 0
  }
  showQuotaModal.value = true
}

// 保存配额
async function saveQuota() {
  try {
    await api.updateQuota({
      userId: quotaForm.value.userId,
      totalTokenLimit: quotaForm.value.totalTokenLimit
    })
    message.success(t('views.system.users.message_quota_update_success'))
    showQuotaModal.value = false
    loadUsers()
  } catch (error) {
    message.error(t('views.system.users.message_quota_update_failed'))
  }
}

// 重置配额
async function resetQuota() {
  try {
    await api.resetQuota({
      userId: quotaForm.value.userId
    })
    message.success(t('views.system.users.message_quota_reset_success'))
    quotaForm.value.totalTokenUsed = 0
    loadUsers()
  } catch (error) {
    message.error(t('views.system.users.message_quota_reset_failed'))
  }
}

function handleSearch() {
  pagination.value.page = 1
  loadUsers()
}

function handlePageChange(page) {
  pagination.value.page = page
  loadUsers()
}

onMounted(() => {
  loadUsers()
})
</script>

<template>
  <CommonPage :show-header="false">
    <div class="users-container">
      <NCard class="users-card" :title="t('views.system.users.label_user_management')">
        <template #header-extra>
          <NButton type="primary" @click="createUser">
            <template #icon>
              <NIcon>
                <svg viewBox="0 0 24 24">
                  <path fill="currentColor" d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
                </svg>
              </NIcon>
            </template>
            {{ t('views.system.users.button_create_user') }}
          </NButton>
        </template>

        <div class="search-bar">
          <NInput
            v-model:value="searchKeyword"
            :placeholder="t('views.system.users.placeholder_search')"
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
            {{ t('views.system.users.button_search') }}
          </NButton>
        </div>

        <NDataTable
          :columns="columns"
          :data="users"
          :loading="loading"
          :pagination="pagination"
          :bordered="false"
          @update:page="handlePageChange"
          style="margin-top: 16px;"
        >
          <template #empty>
            <NEmpty :description="t('views.system.users.text_no_users')" />
          </template>
        </NDataTable>
      </NCard>

      <!-- 用户编辑弹窗 -->
      <NModal
        v-model:show="showUserModal"
        preset="card"
        :title="userForm.id ? t('views.system.users.modal_title_edit') : t('views.system.users.modal_title_create')"
        style="max-width: 600px;"
      >
        <!-- 默认密码提示 -->
        <n-alert 
          v-if="!userForm.id" 
          type="info" 
          :title="t('views.system.users.alert_default_password_title')"
          style="margin-bottom: 16px;"
        >
          <div v-html="t('views.system.users.alert_default_password_content')"></div>
        </n-alert>

        <NForm
          ref="userFormRef"
          :model="userForm"
          label-placement="left"
          label-width="100"
        >
          <NFormItem :label="t('views.system.users.label_username')" path="username" :rule="{ required: true, message: t('views.system.users.message_username_required') }">
            <NInput v-model:value="userForm.username" :placeholder="t('views.system.users.placeholder_username')" />
          </NFormItem>
          <NFormItem :label="t('views.system.users.label_email')" path="email" :rule="{ required: true, type: 'email', message: t('views.system.users.message_email_required') }">
            <NInput v-model:value="userForm.email" :placeholder="t('views.system.users.placeholder_email')" />
          </NFormItem>
          <NFormItem v-if="!userForm.id" :label="t('views.system.users.label_password')" path="password">
            <NInput 
              v-model:value="userForm.password" 
              type="password" 
              :placeholder="t('views.system.users.placeholder_password')"
              clearable
            />
          </NFormItem>
          <NFormItem :label="t('views.system.users.label_real_name')" path="realName">
            <NInput v-model:value="userForm.realName" :placeholder="t('views.system.users.placeholder_real_name')" />
          </NFormItem>
          <NFormItem :label="t('views.system.users.label_role')" path="role">
            <NSelect v-model:value="userForm.role" :options="roleOptions" />
          </NFormItem>
          <NFormItem :label="t('views.system.users.label_status')" path="status">
            <NSelect v-model:value="userForm.status" :options="statusOptions" />
          </NFormItem>
        </NForm>
        <template #footer>
          <div style="display: flex; justify-content: flex-end; gap: 12px;">
            <NButton @click="showUserModal = false">{{ t('views.system.users.button_cancel') }}</NButton>
            <NButton type="primary" @click="saveUser">{{ t('views.system.users.button_save') }}</NButton>
          </div>
        </template>
      </NModal>

      <!-- 配额管理弹窗 -->
      <NModal
        v-model:show="showQuotaModal"
        preset="card"
        :title="t('views.system.users.modal_title_quota')"
        style="max-width: 600px;"
      >
        <NAlert type="info" style="margin-bottom: 16px;">
          <div v-html="t('views.system.users.alert_quota_user', { username: quotaForm.username })"></div>
        </NAlert>

        <NForm
          ref="quotaFormRef"
          :model="quotaForm"
          label-placement="left"
          label-width="120"
        >
          <NFormItem :label="t('views.system.users.label_total_quota')">
            <NInput 
              v-model:value="quotaForm.totalTokenLimit" 
              type="number"
              :min="0"
              :step="100000"
              :placeholder="t('views.system.users.placeholder_total_quota')"
            />
          </NFormItem>
          <NFormItem :label="t('views.system.users.label_used_quota')">
            <div style="display: flex; align-items: center; gap: 12px; width: 100%;">
              <NInput 
                :value="quotaForm.totalTokenUsed.toLocaleString()" 
                disabled
                style="flex: 1;"
              />
              <NPopconfirm
                @positive-click="resetQuota"
              >
                <template #trigger>
                  <NButton type="warning" ghost>{{ t('views.system.users.button_reset') }}</NButton>
                </template>
                {{ t('views.system.users.message_reset_confirm') }}
              </NPopconfirm>
            </div>
          </NFormItem>
          <NFormItem :label="t('views.system.users.label_remaining_quota')">
            <NInput 
              :value="(quotaForm.totalTokenLimit - quotaForm.totalTokenUsed).toLocaleString()" 
              disabled
            />
          </NFormItem>
          <NFormItem :label="t('views.system.users.label_usage_rate')">
            <div style="display: flex; align-items: center; gap: 12px;">
              <div style="flex: 1; height: 20px; background: #f0f0f0; border-radius: 10px; overflow: hidden;">
                <div 
                  :style="{
                    width: `${Math.min(100, (quotaForm.totalTokenUsed / quotaForm.totalTokenLimit * 100))}%`,
                    height: '100%',
                    background: (quotaForm.totalTokenUsed / quotaForm.totalTokenLimit * 100) > 80 
                      ? 'linear-gradient(90deg, #d03050, #ff6b6b)' 
                      : (quotaForm.totalTokenUsed / quotaForm.totalTokenLimit * 100) > 50
                        ? 'linear-gradient(90deg, #f0a020, #ffc107)'
                        : 'linear-gradient(90deg, #18a058, #36ad6a)',
                    transition: 'width 0.3s ease'
                  }"
                />
              </div>
              <span style="min-width: 60px; text-align: right; font-weight: 600;">
                {{ ((quotaForm.totalTokenUsed / quotaForm.totalTokenLimit * 100) || 0).toFixed(1) }}%
              </span>
            </div>
          </NFormItem>
        </NForm>

        <template #footer>
          <div style="display: flex; justify-content: flex-end; gap: 12px;">
            <NButton @click="showQuotaModal = false">{{ t('views.system.users.button_cancel') }}</NButton>
            <NButton type="primary" @click="saveQuota">{{ t('views.system.users.button_save') }}</NButton>
          </div>
        </template>
      </NModal>
    </div>
  </CommonPage>
</template>

<style scoped>
.users-container {
  padding: 20px 24px;
}

.users-card {
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.users-card :deep(.n-card-header) {
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
  .users-container {
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
