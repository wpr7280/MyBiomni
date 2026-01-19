<template>
  <n-modal
    :show="visible"
    preset="card"
    title="新建模版"
    style="max-width: 900px; width: 95vw"
    :closable="!isBuilding"
    :mask-closable="false"
    @update:show="$emit('update:visible', $event)"
  >
    <!-- 步骤指示器 -->
    <div class="mb-6">
      <n-steps :current="currentStep" :status="getStepStatus()">
        <n-step title="基本信息" description="填写模版基本配置" />
        <n-step title="Dockerfile" description="编写或上传Dockerfile" />
        <n-step title="构建监控" description="监控构建进度" />
      </n-steps>
    </div>

    <!-- 步骤1: 基本信息 -->
    <div v-if="currentStep === 1" class="space-y-6">
      <n-form
        ref="basicFormRef"
        :model="formData"
        :rules="basicFormRules"
        label-placement="left"
        label-width="120"
        require-mark-placement="right-hanging"
      >
        <div class="grid grid-cols-1 gap-6 md:grid-cols-2">
          <div class="space-y-4">
            <n-form-item label="模版别名" path="alias">
              <n-input
                v-model:value="formData.alias"
                placeholder="为模版设置一个易记的别名"
                clearable
              />
            </n-form-item>

            <n-form-item label="CPU核心数" path="cpuCount">
              <n-input-number
                v-model:value="formData.cpuCount"
                :min="1"
                :max="16"
                :step="1"
                placeholder="CPU核心数"
                style="width: 100%"
              >
                <template #suffix>
                  <span class="text-gray-500">核</span>
                </template>
              </n-input-number>
            </n-form-item>

            <n-form-item label="内存大小" path="memoryMB">
              <n-input-number
                v-model:value="formData.memoryMB"
                :min="512"
                :max="32768"
                :step="512"
                placeholder="内存大小"
                style="width: 100%"
              >
                <template #suffix>
                  <span class="text-gray-500">MB</span>
                </template>
              </n-input-number>
            </n-form-item>
          </div>

          <div class="space-y-4">
            <n-form-item label="启动命令" path="startCmd">
              <n-input
                v-model:value="formData.startCmd"
                placeholder="/root/.jupyter/start-up.sh"
                clearable
              />
            </n-form-item>

            <n-form-item label="就绪检查" path="readyCmd">
              <n-input
                v-model:value="formData.readyCmd"
                placeholder="用于检查服务是否就绪的命令"
                clearable
              />
            </n-form-item>
          </div>
        </div>

        <!-- 预设配置 -->
        <div class="mt-6">
          <n-divider title-placement="left">快速配置</n-divider>
          <div class="grid grid-cols-1 gap-4 md:grid-cols-3">
            <n-card
              class="cursor-pointer transition-shadow hover:shadow-md"
              @click="applyPreset('basic')"
            >
              <div class="text-center">
                <TheIcon icon="material-symbols:memory" :size="24" class="mb-2 text-blue-500" />
                <div class="font-medium">基础配置</div>
                <div class="text-sm text-gray-500">1核心 1GB内存</div>
              </div>
            </n-card>

            <n-card
              class="cursor-pointer transition-shadow hover:shadow-md"
              @click="applyPreset('standard')"
            >
              <div class="text-center">
                <TheIcon icon="material-symbols:settings" :size="24" class="mb-2 text-green-500" />
                <div class="font-medium">标准配置</div>
                <div class="text-sm text-gray-500">4核心 4GB内存</div>
              </div>
            </n-card>

            <n-card
              class="cursor-pointer transition-shadow hover:shadow-md"
              @click="applyPreset('performance')"
            >
              <div class="text-center">
                <TheIcon
                  icon="material-symbols:rocket-launch"
                  :size="24"
                  class="mb-2 text-orange-500"
                />
                <div class="font-medium">高性能配置</div>
                <div class="text-sm text-gray-500">8核心 8GB内存</div>
              </div>
            </n-card>
          </div>
        </div>
      </n-form>
    </div>

    <!-- 步骤2: Dockerfile编辑 -->
    <div v-if="currentStep === 2" class="space-y-4">
      <div class="flex items-center justify-between">
        <h3 class="text-lg font-semibold">Dockerfile内容</h3>
        <div class="flex gap-2">
          <n-button size="small" @click="loadDockerfileTemplate">
            <TheIcon icon="material-symbols:file-copy" :size="16" class="mr-1" />
            加载模板
          </n-button>
          <n-upload
            :show-file-list="false"
            accept=".dockerfile,Dockerfile"
            @before-upload="handleDockerfileUpload"
          >
            <n-button size="small">
              <TheIcon icon="material-symbols:upload" :size="16" class="mr-1" />
              上传文件
            </n-button>
          </n-upload>
        </div>
      </div>

      <n-form-item path="dockerfile">
        <div class="w-full">
          <n-input
            v-model:value="formData.dockerfile"
            type="textarea"
            placeholder="请输入Dockerfile内容..."
            :rows="20"
            :spellcheck="false"
            style="font-family: 'Courier New', monospace"
            show-count
          />

          <!-- Dockerfile语法提示 -->
          <div class="mt-2 rounded bg-gray-50 p-3 text-sm">
            <div class="mb-2 font-medium">Dockerfile 语法提示：</div>
            <div class="grid grid-cols-1 gap-2 text-xs md:grid-cols-2">
              <div><code>FROM</code> - 基础镜像</div>
              <div><code>RUN</code> - 执行命令</div>
              <div><code>COPY</code> - 复制文件</div>
              <div><code>WORKDIR</code> - 工作目录</div>
              <div><code>EXPOSE</code> - 暴露端口</div>
              <div><code>CMD</code> - 启动命令</div>
            </div>
          </div>
        </div>
      </n-form-item>
    </div>

    <!-- 步骤3: 构建监控 -->
    <div v-if="currentStep === 3" class="space-y-6">
      <!-- 构建状态概览 -->
      <div class="rounded-lg bg-gray-50 p-4">
        <div class="mb-4 flex items-center justify-between">
          <h3 class="flex items-center text-lg font-semibold">
            <TheIcon icon="material-symbols:build" :size="20" class="mr-2" />
            构建状态
          </h3>
          <n-tag :type="getBuildStatusType(buildStatus)" size="medium">
            <TheIcon :icon="getBuildStatusIcon(buildStatus)" :size="14" class="mr-1" />
            {{ getBuildStatusText(buildStatus) }}
          </n-tag>
        </div>

        <div class="grid grid-cols-1 gap-4 text-sm md:grid-cols-2">
          <div>
            <label class="font-medium text-gray-700">模版ID:</label>
            <div class="mt-1 font-mono">{{ createdTemplate?.templateID || '-' }}</div>
          </div>
          <div>
            <label class="font-medium text-gray-700">构建ID:</label>
            <div class="mt-1 font-mono">{{ createdTemplate?.buildID || '-' }}</div>
          </div>
        </div>

        <!-- 构建进度 -->
        <div v-if="isBuilding" class="mt-4">
          <div class="mb-2 flex items-center gap-2">
            <n-spin size="small" />
            <span class="text-sm">构建进行中...</span>
          </div>
          <n-progress type="line" :percentage="buildProgress" :show-indicator="true" processing />
        </div>
      </div>

      <!-- 构建日志 -->
      <div class="rounded-lg bg-black p-4 text-green-400">
        <div class="mb-2 flex items-center justify-between">
          <h4 class="font-medium">构建日志</h4>
          <n-button size="tiny" quaternary :disabled="isBuilding" @click="clearLogs">
            清空日志
          </n-button>
        </div>

        <div
          ref="logContainer"
          class="max-h-80 overflow-y-auto whitespace-pre-wrap text-sm font-mono"
        >
          <div v-for="(log, index) in buildLogs" :key="index">
            {{ log }}
          </div>
          <div v-if="buildLogs.length === 0" class="text-gray-500">等待构建日志输出...</div>
        </div>
      </div>

      <!-- 构建结果 -->
      <div
        v-if="buildStatus === 'ready'"
        class="border border-green-200 rounded-lg bg-green-50 p-4"
      >
        <div class="flex items-center text-green-800">
          <TheIcon icon="material-symbols:check-circle" :size="20" class="mr-2" />
          <span class="font-medium">构建成功！</span>
        </div>
        <p class="mt-2 text-sm text-green-700">模版已成功创建并构建完成，可以开始使用了。</p>
      </div>

      <div v-if="buildStatus === 'error'" class="border border-red-200 rounded-lg bg-red-50 p-4">
        <div class="flex items-center text-red-800">
          <TheIcon icon="material-symbols:error" :size="20" class="mr-2" />
          <span class="font-medium">构建失败</span>
        </div>
        <p class="mt-2 text-sm text-red-700">
          构建过程中发生错误，请检查Dockerfile内容或联系管理员。
        </p>
      </div>
    </div>

    <!-- 底部操作按钮 -->
    <template #footer>
      <div class="flex justify-between">
        <div>
          <n-button v-if="currentStep > 1 && !isBuilding" @click="previousStep"> 上一步 </n-button>
        </div>

        <div class="flex gap-3">
          <n-button :disabled="isBuilding" @click="handleCancel">
            {{ isBuilding ? '构建中...' : '取消' }}
          </n-button>

          <n-button v-if="currentStep < 3" type="primary" :loading="stepLoading" @click="nextStep">
            {{ currentStep === 2 ? '开始构建' : '下一步' }}
          </n-button>

          <n-button
            v-if="currentStep === 3 && buildStatus === 'ready'"
            type="primary"
            @click="handleComplete"
          >
            完成
          </n-button>

          <n-button
            v-if="currentStep === 3 && buildStatus === 'error'"
            type="warning"
            :loading="retryLoading"
            @click="retryBuild"
          >
            重新构建
          </n-button>
        </div>
      </div>
    </template>
  </n-modal>
</template>

<script setup>
import { ref, reactive, computed, watch, nextTick, onUnmounted } from 'vue'
import { useMessage } from 'naive-ui'
import api from '@/api'
import TheIcon from '@/components/icon/TheIcon.vue'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:visible', 'success'])

const message = useMessage()
const basicFormRef = ref(null)
const logContainer = ref(null)

// 表单数据
const formData = reactive({
  alias: '',
  dockerfile: '',
  startCmd: '', // 启动命令默认为空，可选
  readyCmd: '',
  cpuCount: 4,
  memoryMB: 4096,
})

// 步骤状态
const currentStep = ref(1)
const stepLoading = ref(false)
const retryLoading = ref(false)

// 构建状态
const buildStatus = ref('')
const buildProgress = ref(0)
const buildLogs = ref([])
const createdTemplate = ref(null)
const pollTimer = ref(null)

// 计算属性
const isBuilding = computed(() => {
  return buildStatus.value === 'building' || buildStatus.value === 'waiting'
})

// 表单验证规则
const basicFormRules = {
  alias: [{ required: true, message: '请输入模版别名' }],
  cpuCount: [
    { required: true, message: '请输入CPU核心数' },
    { type: 'number', min: 1, max: 16, message: 'CPU核心数范围1-16' },
  ],
  memoryMB: [
    { required: true, message: '请输入内存大小' },
    { type: 'number', min: 512, max: 32768, message: '内存大小范围512MB-32GB' },
  ],
  // startCmd 不再是必填字段，根据API文档它是可选的
}

// 监听弹窗显示状态
watch(
  () => props.visible,
  (newVal) => {
    if (newVal) {
      resetForm()
    } else {
      stopBuildStatusPolling()
    }
  }
)

// 重置表单
const resetForm = () => {
  currentStep.value = 1
  buildStatus.value = ''
  buildProgress.value = 0
  buildLogs.value = []
  createdTemplate.value = null
  stopBuildStatusPolling()

  Object.assign(formData, {
    alias: '',
    dockerfile: '',
    startCmd: '', // 启动命令默认为空
    readyCmd: '',
    cpuCount: 4,
    memoryMB: 4096,
  })
}

// 步骤控制
const getStepStatus = () => {
  if (currentStep.value === 3) {
    if (buildStatus.value === 'ready') return 'finish'
    if (buildStatus.value === 'error') return 'error'
    if (isBuilding.value) return 'process'
  }
  return 'process'
}

const nextStep = async () => {
  if (currentStep.value === 1) {
    // 验证基本信息
    try {
      await basicFormRef.value?.validate()
    } catch (error) {
      return
    }
  }

  if (currentStep.value === 2) {
    // 验证Dockerfile并开始构建
    if (!formData.dockerfile.trim()) {
      message.error('请输入Dockerfile内容')
      return
    }

    await startBuild()
    return
  }

  currentStep.value++
}

const previousStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--
  }
}

// 预设配置
const applyPreset = (preset) => {
  const presets = {
    basic: { cpuCount: 1, memoryMB: 1024 },
    standard: { cpuCount: 4, memoryMB: 4096 },
    performance: { cpuCount: 8, memoryMB: 8192 },
  }

  if (presets[preset]) {
    Object.assign(formData, presets[preset])
    message.success(
      `已应用${preset === 'basic' ? '基础' : preset === 'standard' ? '标准' : '高性能'}配置`
    )
  }
}

// Dockerfile相关
const loadDockerfileTemplate = () => {
  const template = `# Make sure to use this base image
FROM e2bdev/code-interpreter:latest 

# Install some Python packages
RUN pip install cowsay 
`

  formData.dockerfile = template
  message.success('已加载Dockerfile模板')
}

const handleDockerfileUpload = (file) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    formData.dockerfile = e.target.result
    message.success('Dockerfile文件已加载')
  }
  reader.readAsText(file.file)
  return false // 阻止默认上传行为
}

// 构建相关
const startBuild = async () => {
  stepLoading.value = true

  try {
    // 第一步：创建模版
    message.loading('正在创建模版...', { duration: 0, key: 'create' })

    const template = await api.createTemplate({
      dockerfile: formData.dockerfile,
      alias: formData.alias,
      startCmd: formData.startCmd,
      readyCmd: formData.readyCmd,
      cpuCount: formData.cpuCount,
      memoryMB: formData.memoryMB,
    })

    createdTemplate.value = template
    message.destroyAll()
    message.success('模版创建成功')

    // 第二步：触发构建
    message.loading('正在启动构建...', { duration: 0, key: 'build' })

    await api.startTemplateBuild(template.templateID, template.buildID)

    message.destroyAll()
    message.success('构建已启动')

    // 第三步：进入监控步骤
    currentStep.value = 3
    buildStatus.value = 'building'
    buildProgress.value = 10

    // 开始轮询构建状态
    startBuildStatusPolling()
  } catch (error) {
    message.destroyAll()
    message.error('创建失败: ' + (error.message || '未知错误'))
    console.error('创建模版失败:', error)
  } finally {
    stepLoading.value = false
  }
}

const retryBuild = async () => {
  if (!createdTemplate.value) return

  retryLoading.value = true

  try {
    buildStatus.value = 'building'
    buildProgress.value = 10
    buildLogs.value = []

    await api.startTemplateBuild(createdTemplate.value.templateID, createdTemplate.value.buildID)
    message.success('重新构建已启动')

    startBuildStatusPolling()
  } catch (error) {
    message.error('重新构建失败: ' + (error.message || '未知错误'))
    buildStatus.value = 'error'
  } finally {
    retryLoading.value = false
  }
}

// 构建状态轮询
const startBuildStatusPolling = () => {
  stopBuildStatusPolling()

  const poll = async () => {
    if (!createdTemplate.value) return

    try {
      const status = await api.getTemplateBuildStatus(
        createdTemplate.value.templateID,
        createdTemplate.value.buildID,
        buildLogs.value.length
      )

      buildStatus.value = status.status

      // 更新进度
      if (status.status === 'building') {
        buildProgress.value = Math.min(buildProgress.value + 5, 90)
      } else if (status.status === 'ready') {
        buildProgress.value = 100
      }

      // 更新构建日志
      if (status.logs && status.logs.length > 0) {
        buildLogs.value.push(...status.logs)
        // 滚动到底部
        nextTick(() => {
          if (logContainer.value) {
            logContainer.value.scrollTop = logContainer.value.scrollHeight
          }
        })
      }

      // 如果构建完成，停止轮询
      if (status.status === 'ready' || status.status === 'error') {
        stopBuildStatusPolling()

        if (status.status === 'ready') {
          message.success('模版构建成功！')
        } else {
          message.error('模版构建失败')
        }
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

// 状态显示辅助函数
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
  return textMap[status] || '准备中'
}

// 操作处理
const clearLogs = () => {
  buildLogs.value = []
}

const handleCancel = () => {
  emit('update:visible', false)
}

const handleComplete = () => {
  emit('success', createdTemplate.value)
  emit('update:visible', false)
}

// 组件卸载时清理
onUnmounted(() => {
  stopBuildStatusPolling()
})
</script>

<style scoped>
:deep(.n-input__textarea-el) {
  font-family: 'Courier New', monospace !important;
}
</style>
