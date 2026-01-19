<template>
  <CommonPage show-footer title="团队管理">
    <template #action>
      <n-button type="primary" @click="showCreateTeamModal = true">
        <TheIcon icon="material-symbols:add" :size="18" class="mr-2" />
        创建团队
      </n-button>
    </template>

    <div v-if="teamStore.currentTeam" class="space-y-6">
      <n-card class="h-fit">
        <div class="space-y-6">
          <div class="flex items-center gap-3">
            <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-gray-100 dark:bg-gray-700">
              <TheIcon icon="material-symbols:info" :size="20" class="text-gray-600 dark:text-gray-300" />
            </div>
            <div>
              <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Team Details</h2>
              <p class="text-sm text-gray-500">Manage your team's basic information and settings.</p>
            </div>
          </div>

          <n-divider class="!my-0" />

          <div class="grid grid-cols-1 gap-6 md:grid-cols-2">
            <div class="space-y-4">
              <h3 class="text-base font-semibold text-gray-900 dark:text-gray-100">Team Name</h3>
              <p class="text-sm text-gray-500">Change your team name to display on your invoices and receipts.</p>
              <div class="flex items-center gap-3">
                <n-input
                  v-model:value="teamNameInput"
                  :placeholder="teamStore.currentTeam.name"
                  size="medium"
                  class="flex-1"
                />
                <n-button
                  type="primary"
                  size="medium"
                  :loading="updatingTeamName"
                  @click="handleUpdateTeamName"
                >
                  SAVE
                </n-button>
              </div>
              <p class="text-sm text-gray-500">
                Seen as - <span class="text-blue-500">{{ teamStore.currentTeam.slug }}'s Team</span>
              </p>
            </div>

            <div class="space-y-4">
              <h3 class="text-base font-semibold text-gray-900 dark:text-gray-100">Information</h3>
              <p class="text-sm text-gray-500">Additional information about this team.</p>
              <div class="space-y-3">
                <div class="flex items-center gap-3">
                  <n-tag type="warning" size="small">E-Mail</n-tag>
                  <span class="text-sm text-gray-800 dark:text-gray-200">{{ teamStore.currentTeam.email }}</span>
                  <n-button text size="small" @click="copyToClipboard(teamStore.currentTeam.email)">
                    <TheIcon icon="material-symbols:content-copy" :size="14" />
                  </n-button>
                </div>

                <div class="flex items-center gap-3">
                  <n-tag type="info" size="small">Team ID</n-tag>
                  <span class="text-sm font-mono text-gray-800 dark:text-gray-200">{{ teamStore.currentTeam.id.slice(0, 20) }}...</span>
                  <n-button text size="small" @click="copyToClipboard(teamStore.currentTeam.id)">
                    <TheIcon icon="material-symbols:content-copy" :size="14" />
                  </n-button>
                </div>

                <div class="flex items-center gap-3">
                  <n-tag type="success" size="small">Tier</n-tag>
                  <span class="text-sm text-gray-800 dark:text-gray-200">{{ getTeamTierText(teamStore.currentTeam.tier) }}</span>
                </div>

                <div class="flex items-center gap-3">
                  <n-tag type="default" size="small">Status</n-tag>
                  <span class="text-sm text-gray-800 dark:text-gray-200">{{ getTeamStatusText(teamStore.currentTeam) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </n-card>

      <n-card>
        <div class="space-y-5">
          <div class="flex items-center gap-3">
            <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-gray-100 dark:bg-gray-700">
              <TheIcon icon="material-symbols:group" :size="20" class="text-gray-600 dark:text-gray-300" />
            </div>
            <div>
              <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Team Members</h2>
              <p class="text-sm text-gray-500">Manage your team members and their roles.</p>
            </div>
          </div>

          <n-divider class="!my-0" />

          <div class="space-y-3">
            <h3 class="text-base font-semibold text-gray-900 dark:text-gray-100">Invite New Member</h3>
            <p class="text-sm text-gray-500">Enter the email address of the member you want to invite.</p>
            <div class="flex items-center gap-3 max-w-lg">
              <n-input
                v-model:value="inviteEmail"
                placeholder="member@acme.com"
                size="medium"
                class="flex-1"
                @keyup.enter="handleInviteMember"
              />
              <n-button
                type="primary"
                size="medium"
                :loading="invitingMember"
                :disabled="!inviteEmail"
                @click="handleInviteMember"
              >
                ADD MEMBER
              </n-button>
            </div>
          </div>

          <n-divider class="!my-0" />

          <div class="space-y-4">
            <h3 class="text-base font-semibold text-gray-900 dark:text-gray-100">Current Members</h3>
            <div class="grid grid-cols-12 gap-4 border-b border-gray-200 dark:border-gray-700 pb-2">
              <div class="col-span-4">
                <h4 class="text-xs font-medium text-gray-500 uppercase tracking-wider">NAME</h4>
              </div>
              <div class="col-span-4">
                <h4 class="text-xs font-medium text-gray-500 uppercase tracking-wider">E-MAIL</h4>
              </div>
              <div class="col-span-2">
                <h4 class="text-xs font-medium text-gray-500 uppercase tracking-wider">ROLE</h4>
              </div>
              <div class="col-span-2">
                <h4 class="text-xs font-medium text-gray-500 uppercase tracking-wider">ADDED BY</h4>
              </div>
            </div>

            <div v-if="membersLoading" class="flex items-center justify-center py-8">
              <n-spin size="medium" />
              <span class="ml-3 text-sm text-gray-500">Loading members...</span>
            </div>

            <div v-else-if="teamStore.teamMembers.length > 0" class="space-y-2">
              <div
                v-for="member in teamStore.teamMembers"
                :key="member.userId"
                class="grid grid-cols-12 gap-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-800 rounded-lg px-2 transition-colors duration-200"
              >
                <div class="col-span-4 flex items-center gap-3">
                  <n-avatar
                    :src="member.avatar"
                    :size="32"
                    round
                    class="bg-green-500 text-white font-medium"
                  >
                    {{ member.name?.charAt(0)?.toUpperCase() || 'U' }}
                  </n-avatar>
                  <div>
                    <div class="text-sm font-medium text-gray-900 dark:text-gray-100">
                      {{ member.name || 'You' }}
                    </div>
                  </div>
                </div>

                <div class="col-span-4 flex items-center">
                  <span class="text-sm text-gray-600 dark:text-gray-400">{{ member.email }}</span>
                </div>

                <div class="col-span-2 flex items-center">
                  <n-tag
                    :type="getRoleTagType(member.role)"
                    size="small"
                  >
                    {{ getRoleName(member.role) }}
                  </n-tag>
                </div>

                <div class="col-span-2 flex items-center">
                  <span class="text-sm text-gray-600 dark:text-gray-400">{{ member.addByName || member.addBy || '-' }}</span>
                </div>
              </div>
            </div>

            <div v-else class="text-center py-8">
              <n-empty description="No team members yet" />
            </div>
          </div>
        </div>
      </n-card>
    </div>

    <div v-else class="text-center py-12">
      <div v-if="teamStore.loading" class="space-y-4">
        <n-spin size="large" />
        <p class="text-base text-gray-500">Loading team information...</p>
      </div>
      <div v-else-if="teamStore.error" class="space-y-4">
        <n-result status="error" title="Failed to load" :description="teamStore.error">
          <template #extra>
            <n-button type="primary" @click="fetchData"> Reload </n-button>
          </template>
        </n-result>
      </div>
      <div v-else class="space-y-4">
        <n-empty description="Please select a team first">
          <template #extra>
            <n-button type="primary" @click="showCreateTeamModal = true">
              Create your first team
            </n-button>
          </template>
        </n-empty>
      </div>
    </div>

    <CreateTeamModal v-model:visible="showCreateTeamModal" @success="handleTeamCreated" />
  </CommonPage>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import { useTeamStore } from '@/store'
import CommonPage from '@/components/page/CommonPage.vue'
import TheIcon from '@/components/icon/TheIcon.vue'
import CreateTeamModal from '@/components/team/CreateTeamModal.vue'

defineOptions({ name: '团队管理' })

const message = useMessage()
const teamStore = useTeamStore()

// 弹窗状态
const showCreateTeamModal = ref(false)

// 团队名称编辑
const teamNameInput = ref('')
const updatingTeamName = ref(false)

// 成员邀请
const inviteEmail = ref('')
const invitingMember = ref(false)

// 成员加载状态
const membersLoading = ref(false)

// 获取数据
const fetchData = async () => {
  await teamStore.fetchTeams()
  if (teamStore.currentTeam) {
    await fetchMembers()
  }
}

// 获取成员列表
const fetchMembers = async () => {
  membersLoading.value = true
  try {
    await teamStore.fetchTeamMembers()
  } finally {
    membersLoading.value = false
  }
}

// 更新团队名称
const handleUpdateTeamName = async () => {
  if (!teamNameInput.value.trim()) {
    message.warning('请输入团队名称')
    return
  }

  updatingTeamName.value = true
  try {
    const result = await teamStore.updateTeam(teamStore.currentTeam.id, {
      name: teamNameInput.value.trim(),
    })

    if (result.success) {
      message.success('团队名称更新成功')
      teamNameInput.value = ''
    } else {
      message.error(result.message || '更新团队名称失败')
    }
  } catch (error) {
    message.error('更新团队名称失败: ' + (error.message || '未知错误'))
  } finally {
    updatingTeamName.value = false
  }
}

// 邀请成员
const handleInviteMember = async () => {
  if (!inviteEmail.value.trim()) {
    message.warning('请输入邮箱地址')
    return
  }

  invitingMember.value = true
  try {
    const result = await teamStore.inviteMember({
      email: inviteEmail.value.trim(),
    })

    if (result.success) {
      message.success('成员邀请成功')
      inviteEmail.value = ''
      await fetchMembers()
    } else {
      message.error(result.message || '邀请成员失败')
    }
  } catch (error) {
    message.error('邀请成员失败: ' + (error.message || '未知错误'))
  } finally {
    invitingMember.value = false
  }
}

// 处理团队创建成功
const handleTeamCreated = () => {
  message.success('团队创建成功')
  fetchData()
}

// 复制到剪贴板
const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text)
    message.success('已复制到剪贴板')
  } catch (error) {
    message.error('复制失败')
  }
}

// 获取团队套餐文本
const getTeamTierText = (tier) => {
  const tierMap = {
    base_v1: 'Basic',
    pro_v1: 'Professional',
    enterprise_v1: 'Enterprise',
  }
  return tierMap[tier] || tier
}

// 获取团队状态文本
const getTeamStatusText = (team) => {
  if (team.isBanned) return 'Banned'
  if (team.isBlocked) return 'Blocked'
  return 'Active'
}

// 获取角色标签类型
const getRoleTagType = (role) => {
  const typeMap = {
    owner: 'error',
    admin: 'warning',
    member: 'info',
  }
  return typeMap[role] || 'default'
}

// 获取角色名称
const getRoleName = (role) => {
  const nameMap = {
    owner: 'Owner',
    admin: 'Admin',
    member: 'Member',
  }
  return nameMap[role] || role
}

// 组件挂载时初始化
onMounted(async () => {
  await fetchData()
})
</script>

<style scoped>
:deep(.n-card) {
  border-radius: 8px;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
}

:deep(.n-card-header) {
  padding: 20px 20px 0 20px;
  border-bottom: none;
}

:deep(.n-card__content) {
  padding: 20px;
}

:deep(.n-input) {
  border-radius: 6px;
}

:deep(.n-button) {
  border-radius: 6px;
  font-weight: 500;
}

:deep(.n-tag) {
  border-radius: 4px;
  font-weight: 500;
}

.grid {
  display: grid;
}

.grid-cols-1 {
  grid-template-columns: repeat(1, minmax(0, 1fr));
}

.grid-cols-12 {
  grid-template-columns: repeat(12, minmax(0, 1fr));
}

.col-span-2 {
  grid-column: span 2 / span 2;
}

.col-span-4 {
  grid-column: span 4 / span 4;
}

@media (min-width: 768px) {
  .md\:grid-cols-2 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>