<template>
  <n-dropdown
    :options="dropdownOptions"
    trigger="click"
    placement="bottom-start"
    :show-arrow="true"
    @select="handleSelect"
  >
    <n-button quaternary size="medium" class="team-switcher-btn" :loading="teamStore.loading">
      <template #icon>
        <n-avatar
          v-if="teamStore.currentTeam?.logo"
          :src="teamStore.currentTeam.logo"
          :size="20"
          round
        />
        <TheIcon v-else icon="material-symbols:group" :size="20" />
      </template>
      <span class="ml-2">{{ teamStore.currentTeamName }}</span>
      <TheIcon icon="material-symbols:keyboard-arrow-down" :size="16" class="ml-1" />
    </n-button>
  </n-dropdown>

  <!-- 创建团队弹窗 -->
  <CreateTeamModal v-model:visible="showCreateModal" @success="handleTeamCreated" />
</template>

<script setup>
import { ref, computed, onMounted, h } from 'vue'
import { useMessage } from 'naive-ui'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useTeamStore } from '@/store'
import TheIcon from '@/components/icon/TheIcon.vue'
import CreateTeamModal from './CreateTeamModal.vue'

const { t: $t } = useI18n()
const message = useMessage()
const router = useRouter()
const teamStore = useTeamStore()
const showCreateModal = ref(false)

// 下拉菜单选项
const dropdownOptions = computed(() => {
  const options = []

  // 团队列表
  if (teamStore.teams.length > 0) {
    options.push({
      type: 'group',
      label: $t('teams.text_my_teams'),
      key: 'teams',
      children: teamStore.teams.map((team) => ({
        label: team.name,
        key: `team-${team.id}`,
        icon: () =>
          team.logo
            ? h('n-avatar', { src: team.logo, size: 16, round: true })
            : h(TheIcon, { icon: 'material-symbols:group', size: 16 }),
        props: {
          class: teamStore.currentTeam?.id === team.id ? 'bg-primary-50 text-primary-600' : '',
        },
      })),
    })
  }

  // 分隔线
  if (options.length > 0) {
    options.push({ type: 'divider', key: 'divider' })
  }

  // 创建团队选项
  options.push({
    label: $t('teams.text_create_new_team'),
    key: 'create-team',
    icon: () => h(TheIcon, { icon: 'material-symbols:add', size: 16 }),
    props: {
      class: 'text-primary-600',
    },
  })

  return options
})

// 处理选择
const handleSelect = async (key) => {
  if (key === 'create-team') {
    showCreateModal.value = true
    return
  }

  if (key.startsWith('team-')) {
    const teamId = key.replace('team-', '')
    const success = await teamStore.switchTeam(teamId)
    if (success) {
      message.success(`${$t('teams.message_switch_to_team')}: ${teamStore.currentTeamName}`)
      
      // 刷新当前页面数据
      await refreshCurrentPage()
    } else {
      message.error($t('teams.message_switch_team_failed'))
    }
  }
}

// 刷新当前页面
const refreshCurrentPage = async () => {
  try {
    // 延迟一下让切换消息显示完成
    setTimeout(() => {
      // 使用router.go(0)刷新当前页面，这会重新加载当前路由
      router.go(0)
    }, 500)
  } catch (error) {
    console.error('页面刷新失败:', error)
    // 如果路由跳转失败，使用强制刷新
    window.location.reload()
  }
}

// 处理团队创建成功
const handleTeamCreated = () => {
  message.success($t('teams.message_team_created'))
  teamStore.fetchTeams() // 重新获取团队列表
}

// 组件挂载时初始化
onMounted(async () => {
  // 从本地存储加载当前团队
  teamStore.loadCurrentTeamFromStorage()
  // 获取团队列表
  await teamStore.fetchTeams()
  console.log('团队列表:', teamStore.teams)
  console.log('当前团队:', teamStore.currentTeam)
})
</script>

<style scoped>
.team-switcher-btn {
  min-width: 120px;
  justify-content: flex-start;
}

:deep(.n-button__content) {
  display: flex;
  align-items: center;
  width: 100%;
}
</style>
 