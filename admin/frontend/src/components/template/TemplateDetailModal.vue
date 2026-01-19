<template>
  <n-modal
    :show="visible"
    preset="card"
    title="模版详情"
    style="max-width: 800px; width: 90vw"
    :closable="true"
    :mask-closable="true"
    @update:show="$emit('update:visible', $event)"
  >
    <div v-if="loading" class="flex items-center justify-center py-8">
      <n-spin size="medium" />
    </div>

    <div v-else-if="templateData" class="space-y-6">
      <!-- 基本信息 -->
      <div class="rounded-lg bg-gray-50 p-4">
        <h3 class="mb-4 flex items-center text-lg font-semibold">
          <TheIcon icon="material-symbols:info-outline" :size="20" class="mr-2" />
          基本信息
        </h3>

        <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div>
            <label class="mb-1 block text-sm font-medium text-gray-700">模版ID</label>
            <div class="border rounded bg-white p-2 text-sm font-mono">
              {{ templateData.templateID }}
            </div>
          </div>

          <div>
            <label class="mb-1 block text-sm font-medium text-gray-700">别名</label>
            <div class="border rounded bg-white p-2 text-sm">
              {{ templateData.aliases?.join(', ') || '-' }}
            </div>
          </div>

          <div>
            <label class="mb-1 block text-sm font-medium text-gray-700">CPU核心数</label>
            <div class="border rounded bg-white p-2 text-sm">{{ templateData.cpuCount }} 核</div>
          </div>

          <div>
            <label class="mb-1 block text-sm font-medium text-gray-700">内存</label>
            <div class="border rounded bg-white p-2 text-sm">{{ templateData.memoryMB }} MB</div>
          </div>

          <div>
            <label class="mb-1 block text-sm font-medium text-gray-700">可见性</label>
            <n-tag :type="templateData.public ? 'success' : 'warning'" size="small">
              <TheIcon
                :icon="templateData.public ? 'material-symbols:lock-open' : 'material-symbols:lock'"
                :size="12"
                class="mr-1"
              />
              {{ templateData.public ? '公开' : '私有' }}
            </n-tag>
          </div>

          <div>
            <label class="mb-1 block text-sm font-medium text-gray-700">构建状态</label>
            <n-tag :type="getBuildStatusType(templateData.buildStatus)" size="small">
              <TheIcon
                :icon="getBuildStatusIcon(templateData.buildStatus)"
                :size="12"
                class="mr-1"
              />
              {{ getBuildStatusText(templateData.buildStatus) }}
            </n-tag>
          </div>
        </div>
      </div>

      <!-- 统计信息 -->
      <div class="rounded-lg bg-blue-50 p-4">
        <h3 class="mb-4 flex items-center text-lg font-semibold">
          <TheIcon icon="material-symbols:analytics-outline" :size="20" class="mr-2" />
          使用统计
        </h3>

        <div class="grid grid-cols-1 gap-4 md:grid-cols-3">
          <div class="text-center">
            <div class="text-2xl font-bold text-blue-600">{{ templateData.spawnCount || 0 }}</div>
            <div class="text-sm text-gray-600">启动次数</div>
          </div>

          <div class="text-center">
            <div class="text-2xl font-bold text-green-600">{{ templateData.buildCount || 0 }}</div>
            <div class="text-sm text-gray-600">构建次数</div>
          </div>

          <div class="text-center">
            <div class="text-2xl font-bold text-purple-600">
              {{ templateData.lastSpawnedAt ? getTimeAgo(templateData.lastSpawnedAt) : '-' }}
            </div>
            <div class="text-sm text-gray-600">最后使用</div>
          </div>
        </div>
      </div>

      <!-- 构建历史和日志 -->
      <div class="rounded-lg bg-gray-50 p-4">
        <h3 class="mb-4 flex items-center text-lg font-semibold">
          <TheIcon icon="material-symbols:history" :size="20" class="mr-2" />
          构建信息
        </h3>

        <div class="space-y-4">
          <div>
            <label class="mb-2 block text-sm font-medium text-gray-700">当前构建ID</label>
            <div class="border rounded bg-white p-2 text-sm font-mono">
              {{ templateData.buildID || '-' }}
            </div>
          </div>

          <div>
            <label class="mb-2 block text-sm font-medium text-gray-700">创建时间</label>
            <div class="border rounded bg-white p-2 text-sm">
              {{ templateData.createdAt ? formatDate(templateData.createdAt) : '-' }}
            </div>
          </div>

          <div>
            <label class="mb-2 block text-sm font-medium text-gray-700">更新时间</label>
            <div class="border rounded bg-white p-2 text-sm">
              {{ templateData.updatedAt ? formatDate(templateData.updatedAt) : '-' }}
            </div>
          </div>

          <div v-if="templateData.createdBy">
            <label class="mb-2 block text-sm font-medium text-gray-700">创建者</label>
            <div class="border rounded bg-white p-2 text-sm">
              {{ templateData.createdBy.email || templateData.createdBy.id }}
            </div>
          </div>
        </div>
      </div>

      <!-- 实时构建日志 (如果正在构建) -->
      <div v-if="isBuilding" class="rounded-lg bg-yellow-50 p-4">
        <h3 class="mb-4 flex items-center text-lg font-semibold">
          <TheIcon icon="material-symbols:build" :size="20" class="mr-2" />
          构建日志
          <n-spin size="small" class="ml-2" />
        </h3>

        <div class="max-h-60 overflow-y-auto rounded bg-black p-4 text-sm font-mono text-green-400">
          <div v-for="(log, index) in buildLogs" :key="index" class="whitespace-pre-wrap">
            {{ log }}
          </div>
          <div v-if="buildLogs.length === 0" class="text-gray-500">等待构建日志...</div>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="flex justify-between">
        <div>
          <n-button
            v-if="isBuilding"
            type="warning"
            size="small"
            :loading="refreshing"
            @click="refreshBuildStatus"
          >
            <TheIcon icon="material-symbols:refresh" :size="16" class="mr-2" />
            刷新状态
          </n-button>
        </div>

        <n-button @click="handleClose"> 关闭 </n-button>
      </div>
    </template>
  </n-modal>
</template>

<script setup>
import { ref, computed, watch, onUnmounted } from 'vue'
import { useMessage } from 'naive-ui'
import api from '@/api'
import TheIcon from '@/components/icon/TheIcon.vue'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false,
  },
  templateData: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['update:visible', 'build-status-changed'])

const message = useMessage()
const loading = ref(false)
const refreshing = ref(false)
const buildLogs = ref([])
const pollTimer = ref(null)

// 计算属性
const isBuilding = computed(() => {
  return (
    props.templateData?.buildStatus === 'building' || props.templateData?.buildStatus === 'waiting'
  )
})

// 监听模态框显示状态
watch(
  () => props.visible,
  (newVal) => {
    if (newVal && props.templateData) {
      startBuildStatusPolling()
    } else {
      stopBuildStatusPolling()
    }
  }
)

// 监听模版数据变化
watch(
  () => props.templateData,
  (newVal) => {
    if (newVal && props.visible) {
      startBuildStatusPolling()
    }
  }
)

// 构建状态相关方法
const getBuildStatusType = (status) => {
  const statusMap = {
    ready: 'success',
    building: 'warning',
    waiting: 'info',
    error: 'error',
  }
  return statusMap[status] || 'default'
}

const getBuildStatusIcon = (status) => {
  const iconMap = {
    ready: 'material-symbols:check-circle',
    building: 'material-symbols:build',
    waiting: 'material-symbols:hourglass-empty',
    error: 'material-symbols:error',
  }
  return iconMap[status] || 'material-symbols:help'
}

const getBuildStatusText = (status) => {
  const textMap = {
    ready: '构建完成',
    building: '构建中',
    waiting: '等待构建',
    error: '构建失败',
  }
  return textMap[status] || '未知状态'
}

// 时间格式化
const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

const getTimeAgo = (dateStr) => {
  const now = new Date()
  const past = new Date(dateStr)
  const diffMs = now - past
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

  if (diffDays === 0) {
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
    if (diffHours === 0) {
      const diffMinutes = Math.floor(diffMs / (1000 * 60))
      return `${diffMinutes}分钟前`
    }
    return `${diffHours}小时前`
  } else if (diffDays < 30) {
    return `${diffDays}天前`
  } else {
    return formatDate(dateStr)
  }
}

// 构建状态轮询
const startBuildStatusPolling = () => {
  stopBuildStatusPolling()

  if (!isBuilding.value || !props.templateData?.templateID || !props.templateData?.buildID) {
    return
  }

  const poll = async () => {
    try {
      const status = await api.getTemplateBuildStatus(
        props.templateData.templateID,
        props.templateData.buildID,
        buildLogs.value.length
      )

      // 更新构建日志
      if (status.logs && status.logs.length > 0) {
        buildLogs.value.push(...status.logs)
      }

      // 如果构建完成，停止轮询
      if (status.status === 'ready' || status.status === 'error') {
        stopBuildStatusPolling()
        // 可以触发父组件刷新数据
        emit('build-status-changed', status)
      }
    } catch (error) {
      console.error('获取构建状态失败:', error)
    }
  }

  // 立即执行一次
  poll()

  // 每3秒轮询一次
  pollTimer.value = setInterval(poll, 3000)
}

const stopBuildStatusPolling = () => {
  if (pollTimer.value) {
    clearInterval(pollTimer.value)
    pollTimer.value = null
  }
}

const refreshBuildStatus = async () => {
  if (!props.templateData?.templateID || !props.templateData?.buildID) return

  refreshing.value = true
  try {
    const status = await api.getTemplateBuildStatus(
      props.templateData.templateID,
      props.templateData.buildID,
      0 // 重新获取所有日志
    )

    buildLogs.value = status.logs || []
    message.success('状态已刷新')
  } catch (error) {
    message.error('刷新失败')
    console.error(error)
  } finally {
    refreshing.value = false
  }
}

const handleClose = () => {
  emit('update:visible', false)
  stopBuildStatusPolling()
  buildLogs.value = []
}

// 组件卸载时清理定时器
onUnmounted(() => {
  stopBuildStatusPolling()
})
</script>
