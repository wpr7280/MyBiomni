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
    title: 'Token配额',
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
          }, { default: () => '配额' }),
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
    message.error('加载失败')
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
      message.error('操作失败')
    }
  })
}

// 删除用户
async function deleteUser(id) {
  try {
    await api.deleteUser({ userId: id })
    message.success('删除成功')
    loadUsers()
  } catch (error) {
    message.error('删除失败')
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
    message.success('配额更新成功')
    showQuotaModal.value = false
    loadUsers()
  } catch (error) {
    message.error('配额更新失败')
  }
}

// 重置配额
async function resetQuota() {
  try {
    await api.resetQuota({
      userId: quotaForm.value.userId
    })
    message.success('配额已重置')
    quotaForm.value.totalTokenUsed = 0
    loadUsers()
  } catch (error) {
    message.error('重置失败')
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
            placeholder="搜索用户..."
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
          :data="users"
          :loading="loading"
          :pagination="pagination"
          :bordered="false"
          @update:page="handlePageChange"
          style="margin-top: 16px;"
        >
          <template #empty>
            <NEmpty description="暂无用户" />
          </template>
        </NDataTable>
      </NCard>

      <!-- 用户编辑弹窗 -->
      <NModal
        v-model:show="showUserModal"
        preset="card"
        :title="userForm.id ? '编辑用户' : '创建用户'"
        style="max-width: 600px;"
      >
        <!-- 默认密码提示 -->
        <n-alert 
          v-if="!userForm.id" 
          type="info" 
          title="默认密码"
          style="margin-bottom: 16px;"
        >
          新用户的默认密码为：<strong>Password&123</strong>
          <br/>
          用户首次登录时需要修改密码。
        </n-alert>

        <NForm
          ref="userFormRef"
          :model="userForm"
          label-placement="left"
          label-width="100"
        >
          <NFormItem label="用户名" path="username" :rule="{ required: true, message: '请输入用户名' }">
            <NInput v-model:value="userForm.username" placeholder="请输入用户名" />
          </NFormItem>
          <NFormItem label="邮箱" path="email" :rule="{ required: true, type: 'email', message: '请输入有效的邮箱' }">
            <NInput v-model:value="userForm.email" placeholder="请输入邮箱" />
          </NFormItem>
          <NFormItem v-if="!userForm.id" label="密码" path="password">
            <NInput 
              v-model:value="userForm.password" 
              type="password" 
              placeholder="留空使用默认密码 Password&123"
              clearable
            />
          </NFormItem>
          <NFormItem label="真实姓名" path="realName">
            <NInput v-model:value="userForm.realName" placeholder="请输入真实姓名" />
          </NFormItem>
          <NFormItem label="角色" path="role">
            <NSelect v-model:value="userForm.role" :options="roleOptions" />
          </NFormItem>
          <NFormItem label="状态" path="status">
            <NSelect v-model:value="userForm.status" :options="statusOptions" />
          </NFormItem>
        </NForm>
        <template #footer>
          <div style="display: flex; justify-content: flex-end; gap: 12px;">
            <NButton @click="showUserModal = false">取消</NButton>
            <NButton type="primary" @click="saveUser">保存</NButton>
          </div>
        </template>
      </NModal>

      <!-- 配额管理弹窗 -->
      <NModal
        v-model:show="showQuotaModal"
        preset="card"
        title="配额管理"
        style="max-width: 600px;"
      >
        <NAlert type="info" style="margin-bottom: 16px;">
          管理用户 <strong>{{ quotaForm.username }}</strong> 的 Token 配额
        </NAlert>

        <NForm
          ref="quotaFormRef"
          :model="quotaForm"
          label-placement="left"
          label-width="120"
        >
          <NFormItem label="总配额 (Tokens)">
            <NInput 
              v-model:value="quotaForm.totalTokenLimit" 
              type="number"
              :min="0"
              :step="100000"
              placeholder="请输入总配额"
            />
          </NFormItem>
          <NFormItem label="已使用 (Tokens)">
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
                  <NButton type="warning" ghost>重置</NButton>
                </template>
                确定要重置已使用量为 0 吗？
              </NPopconfirm>
            </div>
          </NFormItem>
          <NFormItem label="剩余 (Tokens)">
            <NInput 
              :value="(quotaForm.totalTokenLimit - quotaForm.totalTokenUsed).toLocaleString()" 
              disabled
            />
          </NFormItem>
          <NFormItem label="使用率">
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
            <NButton @click="showQuotaModal = false">取消</NButton>
            <NButton type="primary" @click="saveQuota">保存</NButton>
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
