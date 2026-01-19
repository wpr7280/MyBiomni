<script setup>
import { ref, onMounted, h } from 'vue'
import { NButton, NCard, NInput, NDataTable, NPopconfirm, NTag, NIcon, NEmpty, NSpace, NModal, NForm, NFormItem, NSelect } from 'naive-ui'
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
    width: 200,
    render: (row) => {
      return h(NSpace, { size: 4 }, {
        default: () => [
          h(NButton, {
            size: 'small',
            type: 'primary',
            ghost: true,
            onClick: () => editUser(row)
          }, { default: () => t('views.system.users.button_edit') }),
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
    password: '',
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
          <NFormItem v-if="!userForm.id" label="密码" path="password" :rule="{ required: true, message: '请输入密码' }">
            <NInput v-model:value="userForm.password" type="password" placeholder="请输入密码" />
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
