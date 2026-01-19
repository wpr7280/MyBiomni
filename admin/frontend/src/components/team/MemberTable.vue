<template>
  <div class="member-table">
    <!-- 表格头部操作 -->
    <div class="mb-4 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <h3 class="text-lg font-semibold">团队成员</h3>
        <n-tag type="info" size="medium">{{ members.length }} 个成员</n-tag>
      </div>

      <div class="flex items-center gap-3">
        <n-input
          v-model:value="searchKeyword"
          placeholder="搜索成员..."
          size="medium"
          clearable
          style="width: 200px"
        >
          <template #prefix>
            <TheIcon icon="material-symbols:search" :size="16" />
          </template>
        </n-input>

        <n-button type="primary" :disabled="!canManageMembers" @click="$emit('invite')">
          <template #icon>
            <TheIcon icon="material-symbols:person-add" :size="16" />
          </template>
          邀请成员
        </n-button>
      </div>
    </div>

    <!-- 成员表格 -->
    <n-data-table
      :columns="columns"
      :data="filteredMembers"
      :loading="loading"
      :pagination="pagination"
      :row-key="(row) => row.userId"
      size="medium"
      flex-height
      style="height: 400px"
    />
  </div>
</template>

<script setup>
import { ref, computed, h } from 'vue'
import { NTag, NButton, NAvatar, NPopconfirm, NTooltip } from 'naive-ui'
import { useUserStore } from '@/store'
import TheIcon from '@/components/icon/TheIcon.vue'

const props = defineProps({
  members: {
    type: Array,
    default: () => [],
  },
  loading: {
    type: Boolean,
    default: false,
  },
  canManageMembers: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['invite', 'removeMember', 'updateRole'])

const userStore = useUserStore()
const searchKeyword = ref('')

// 分页配置
const pagination = {
  pageSize: 10,
  showSizePicker: true,
  pageSizes: [10, 20, 50],
  showQuickJumper: true,
}

// 过滤后的成员列表
const filteredMembers = computed(() => {
  if (!searchKeyword.value) return props.members

  const keyword = searchKeyword.value.toLowerCase()
  return props.members.filter(
    (member) =>
      member.name?.toLowerCase().includes(keyword) || member.email?.toLowerCase().includes(keyword)
  )
})

// 角色标签类型映射
const getRoleTagType = (role) => {
  const typeMap = {
    owner: 'error',
    admin: 'warning',
    member: 'info',
  }
  return typeMap[role] || 'default'
}

// 角色名称映射
const getRoleName = (role) => {
  const nameMap = {
    owner: '所有者',
    admin: '管理员',
    member: '成员',
  }
  return nameMap[role] || role
}

// 表格列配置
const columns = computed(() => [
  {
    title: '成员',
    key: 'member',
    width: 250,
    render: (row) => {
      return h('div', { class: 'flex items-center gap-3' }, [
        h(
          NAvatar,
          {
            src: row.avatar,
            size: 32,
            round: true,
          },
          {
            default: () => row.name?.charAt(0)?.toUpperCase() || 'U',
          }
        ),
        h('div', { class: 'flex flex-col' }, [
          h(
            'div',
            { class: 'font-medium text-gray-900 dark:text-gray-100' },
            row.name || '未知用户'
          ),
          h('div', { class: 'text-sm text-gray-500' }, row.email || ''),
        ]),
      ])
    },
  },
  {
    title: '角色',
    key: 'role',
    width: 120,
    render: (row) => {
      return h(
        NTag,
        {
          type: getRoleTagType(row.role),
          size: 'small',
        },
        {
          default: () => getRoleName(row.role),
        }
      )
    },
  },
  {
    title: '加入时间',
    key: 'joinedAt',
    width: 150,
    render: (row) => {
      return formatDate(row.joinedAt)
    },
  },
  {
    title: '添加者',
    key: 'addBy',
    width: 120,
    render: (row) => {
      return row.addByName || row.addBy || '-'
    },
  },
  {
    title: '操作',
    key: 'actions',
    width: 120,
    render: (row) => {
      const actions = []

      // 不能操作自己
      if (row.userId === userStore.userId) {
        return h('span', { class: 'text-gray-400' }, '当前用户')
      }

      // 不能操作所有者
      if (row.role === 'owner') {
        return h('span', { class: 'text-gray-400' }, '所有者')
      }

      // 只有管理员和所有者可以操作其他成员
      if (props.canManageMembers) {
        // 角色变更按钮
        if (row.role !== 'owner') {
          actions.push(
            h(
              NTooltip,
              {},
              {
                trigger: () =>
                  h(
                    NButton,
                    {
                      size: 'small',
                      quaternary: true,
                      onClick: () => handleRoleChange(row),
                    },
                    {
                      icon: () =>
                        h(TheIcon, { icon: 'material-symbols:admin-panel-settings', size: 14 }),
                    }
                  ),
                default: () => '变更角色',
              }
            )
          )
        }

        // 移除成员按钮
        actions.push(
          h(
            NPopconfirm,
            {
              onPositiveClick: () => handleRemoveMember(row),
            },
            {
              trigger: () =>
                h(
                  NButton,
                  {
                    size: 'small',
                    quaternary: true,
                    type: 'error',
                  },
                  {
                    icon: () => h(TheIcon, { icon: 'material-symbols:person-remove', size: 14 }),
                  }
                ),
              default: () => `确定要移除成员 ${row.name} 吗？`,
            }
          )
        )
      }

      return h('div', { class: 'flex items-center gap-1' }, actions)
    },
  },
])

// 处理角色变更
const handleRoleChange = (member) => {
  // 这里可以弹出角色选择对话框，暂时简化为切换管理员/成员
  const newRole = member.role === 'admin' ? 'member' : 'admin'
  emit('updateRole', member.userId, newRole)
}

// 处理移除成员
const handleRemoveMember = (member) => {
  emit('removeMember', member.userId)
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '-'
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
    })
  } catch (error) {
    return dateString
  }
}
</script>

<style scoped>
.member-table {
  background: white;
  border-radius: 8px;
  padding: 16px;
}

:deep(.n-data-table-th) {
  font-weight: 600;
}

:deep(.n-data-table-td) {
  border-bottom: 1px solid #f0f0f0;
}
</style>
