<template>
  <n-modal v-model:show="visible" :mask-closable="false" preset="card" :title="modalTitle" class="w-full max-w-7xl" style="width: 90vw; max-width: 1200px; min-height: 650px; max-height: 90vh;">
    <n-tabs type="line" animated @update:value="handleTabChange">
      <!-- 信息 & 日志 -->
      <n-tab-pane name="info" :tab="$t('sandboxs.tab_info_logs')">
        <!-- 基本信息区域 -->
        <div class="mb-6">
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <div class="bg-gray-50 p-4 rounded-lg">
              <h4 style="font-size: 14px; font-weight: 500; color: #374151; margin-bottom: 12px;">{{ $t('sandboxs.label_basic_info') }}</h4>
              <div class="space-y-2">
                <div class="flex justify-between">
                  <span style="font-size: 13px; color: #6b7280;">{{ $t('sandboxs.label_sandbox_id') }}:</span>
                  <span style="font-size: 13px; font-family: monospace;">{{ sandbox?.sandboxID }}</span>
                </div>
                <div class="flex justify-between">
                  <span style="font-size: 13px; color: #6b7280;">{{ $t('sandboxs.label_client_id') }}:</span>
                  <span style="font-size: 13px; font-family: monospace;">{{ sandbox?.clientID }}</span>
                </div>
                <div class="flex justify-between">
                  <span style="font-size: 13px; color: #6b7280;">{{ $t('sandboxs.label_template') }}:</span>
                  <span style="font-size: 13px;">{{ templateName }}</span>
                </div>
                <div class="flex justify-between">
                  <span style="font-size: 13px; color: #6b7280;">{{ $t('sandboxs.label_alias') }}:</span>
                  <span style="font-size: 13px;">{{ sandbox?.alias || '-' }}</span>
                </div>
              </div>
            </div>

            <div class="bg-gray-50 p-4 rounded-lg">
              <h4 style="font-size: 14px; font-weight: 500; color: #374151; margin-bottom: 12px;">{{ $t('sandboxs.label_resources') }}</h4>
              <div class="space-y-2">
                <div class="flex justify-between">
                  <span style="font-size: 13px; color: #6b7280;">{{ $t('sandboxs.label_cpu_count') }}:</span>
                  <span style="font-size: 13px;">{{ sandbox?.cpuCount }} {{ $t('sandboxs.text_cores') }}</span>
                </div>
                <div class="flex justify-between">
                  <span style="font-size: 13px; color: #6b7280;">{{ $t('sandboxs.label_memory') }}:</span>
                  <span style="font-size: 13px;">{{ sandbox?.memoryMB }} {{ $t('sandboxs.text_mb') }}</span>
                </div>
              </div>
            </div>

            <div class="bg-gray-50 p-4 rounded-lg">
              <h4 style="font-size: 14px; font-weight: 500; color: #374151; margin-bottom: 12px;">{{ $t('sandboxs.label_time_info') }}</h4>
              <div class="space-y-2">
                <div class="flex justify-between">
                  <span style="font-size: 13px; color: #6b7280;">{{ $t('sandboxs.label_started_at') }}:</span>
                  <span style="font-size: 13px;">{{ formatDateTime(sandbox?.startedAt) }}</span>
                </div>
                <div class="flex justify-between">
                  <span style="font-size: 13px; color: #6b7280;">{{ $t('sandboxs.label_end_at') }}:</span>
                  <span style="font-size: 13px;">{{ formatDateTime(sandbox?.endAt) }}</span>
                </div>
              </div>
            </div>

            <div class="bg-gray-50 p-4 rounded-lg">
              <h4 style="font-size: 14px; font-weight: 500; color: #374151; margin-bottom: 12px;">{{ $t('sandboxs.label_metadata') }}</h4>
              <n-code :code="metadataString" language="json" style="font-size: 11px;" />
            </div>
          </div>


        </div>

        <!-- 日志区域 -->
        <div class="space-y-4">
          <div class="flex justify-between items-center">
            <h4 style="font-size: 14px; font-weight: 500;">{{ $t('sandboxs.label_logs') }}</h4>
            <div class="flex gap-2">
              <n-input-number
                v-model:value="logLimit"
                :min="100"
                :max="5000"
                :step="100"
                size="small"
                style="width: 120px"
                :placeholder="$t('sandboxs.placeholder_log_limit')"
              />
              <n-button type="primary" size="small" :loading="logsLoading" @click="fetchLogs">
                <template #icon>
                  <TheIcon icon="material-symbols:refresh" />
                </template>
                {{ $t('sandboxs.button_refresh_logs') }}
              </n-button>
            </div>
          </div>
          <div 
            class="bg-black p-4 rounded-lg font-mono overflow-y-auto" 
            style="height: 400px; overflow-y: auto; color: #4ade80; font-size: 12px;"
          >
            <div v-if="logsLoading" style="text-align: center; padding: 16px 0;">
              <n-spin size="small" />
              <span style="margin-left: 8px;">{{ $t('sandboxs.text_loading_logs') }}...</span>
            </div>
            <div v-else-if="logs.length === 0" style="text-align: center; padding: 16px 0; color: #6b7280;">
              {{ $t('sandboxs.text_no_logs') }}
            </div>
            <div v-else>
              <div v-for="(log, index) in logs" :key="index" style="margin-bottom: 8px;">
                <span style="color: #9ca3af;">[{{ formatDateTime(log.timestamp) }}]</span>
                <span style="margin-left: 8px;">{{ log.line }}</span>
              </div>
            </div>
          </div>
        </div>
      </n-tab-pane>

      <!-- 指标 -->
      <n-tab-pane name="metrics" :tab="$t('sandboxs.tab_metrics')">
        <div class="space-y-6">
          <div class="flex justify-between items-center">
            <h4 style="font-size: 14px; font-weight: 500;">{{ $t('sandboxs.label_metrics') }}</h4>
            <n-button type="primary" size="small" :loading="metricsLoading" @click="fetchMetrics">
              <template #icon>
                <TheIcon icon="material-symbols:refresh" />
              </template>
              {{ $t('sandboxs.button_refresh_metrics') }}
            </n-button>
          </div>

          <!-- 加载状态 -->
          <div v-if="metricsLoading" style="text-align: center; padding: 32px 0;">
            <n-spin size="medium" />
            <div style="margin-top: 8px; font-size: 14px; color: #6b7280;">{{ $t('sandboxs.text_loading_metrics') }}...</div>
          </div>

          <!-- 无数据状态 -->
          <div v-else-if="metrics.length === 0" style="text-align: center; padding: 32px 0; color: #6b7280;">
            {{ $t('sandboxs.text_no_metrics') }}
          </div>

          <!-- 有数据时显示内容 -->
          <div v-else class="space-y-4">
            <!-- 最新指标卡片 -->
            <div v-if="latestMetric" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div class="bg-blue-50 p-4 rounded-lg">
                <div class="flex items-center justify-between">
                  <div>
                    <p style="font-size: 14px; color: #4b5563;">{{ $t('sandboxs.label_cpu_usage') }}</p>
                    <p style="font-size: 24px; font-weight: 700; color: #2563eb;">{{ latestMetric.cpuUsedPct.toFixed(1) }}%</p>
                  </div>
                  <TheIcon icon="material-symbols:memory" style="color: #3b82f6;" :size="24" />
                </div>
              </div>

              <div class="bg-green-50 p-4 rounded-lg">
                <div class="flex items-center justify-between">
                  <div>
                    <p style="font-size: 14px; color: #4b5563;">{{ $t('sandboxs.label_memory_usage') }}</p>
                    <p style="font-size: 24px; font-weight: 700; color: #16a34a;">{{ ((latestMetric.memUsedMiB / latestMetric.memTotalMiB) * 100).toFixed(1) }}%</p>
                  </div>
                  <TheIcon icon="material-symbols:storage" style="color: #22c55e;" :size="24" />
                </div>
              </div>

              <div class="bg-purple-50 p-4 rounded-lg">
                <div class="flex items-center justify-between">
                  <div>
                    <p style="font-size: 14px; color: #4b5563;">{{ $t('sandboxs.label_memory_used') }}</p>
                    <p style="font-size: 24px; font-weight: 700; color: #9333ea;">{{ latestMetric.memUsedMiB }} MB</p>
                  </div>
                  <TheIcon icon="material-symbols:memory-alt" style="color: #a855f7;" :size="24" />
                </div>
              </div>

              <div class="bg-orange-50 p-4 rounded-lg">
                <div class="flex items-center justify-between">
                  <div>
                    <p style="font-size: 14px; color: #4b5563;">{{ $t('sandboxs.label_memory_total') }}</p>
                    <p style="font-size: 24px; font-weight: 700; color: #ea580c;">{{ latestMetric.memTotalMiB }} MB</p>
                  </div>
                  <TheIcon icon="material-symbols:hard-drive-2" style="color: #f97316;" :size="24" />
                </div>
              </div>
            </div>

            <!-- 指标历史图表 -->
            <div class="bg-gray-50 p-4 rounded-lg">
              <h5 style="font-size: 14px; font-weight: 500; margin-bottom: 12px;">{{ $t('sandboxs.label_metrics_history') }}</h5>
              <div ref="chartContainer" style="width: 100%; height: 400px;"></div>
            </div>

            <!-- 指标历史表格 - 暂时隐藏 -->
            <!-- <div class="bg-gray-50 p-4 rounded-lg">
              <h5 style="font-size: 14px; font-weight: 500; margin-bottom: 12px;">{{ $t('sandboxs.label_metrics_table') }}</h5>
              <n-data-table 
                :columns="metricsColumns" 
                :data="metrics" 
                size="small" 
                :max-height="300"
                :bordered="false"
                :single-line="false"
              />
            </div> -->
          </div>


        </div>
      </n-tab-pane>
    </n-tabs>



    <template #action>
      <n-button @click="handleClose">{{ $t('common.close') }}</n-button>
    </template>
  </n-modal>
</template>

<script setup>
import { ref, computed, watch, h, onMounted, nextTick } from 'vue'
import { useMessage } from 'naive-ui'
import { useI18n } from 'vue-i18n'
import * as echarts from 'echarts'
import api from '@/api'
import TheIcon from '@/components/icon/TheIcon.vue'

defineOptions({ name: 'SandboxDetailModal' })

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  sandboxId: {
    type: String,
    default: ''
  },
  templates: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:visible', 'refresh'])

const { t: $t } = useI18n()
const message = useMessage()

// 响应式数据
const sandbox = ref(null)
const logs = ref([])
const metrics = ref([])
const loading = ref(false)
const logsLoading = ref(false)
const metricsLoading = ref(false)

// 日志相关
const logLimit = ref(1000)

// 图表相关
const chartContainer = ref(null)
let chart = null

// 计算属性
const visible = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val)
})

const modalTitle = computed(() => {
  return sandbox.value 
    ? `${$t('sandboxs.modal_title_detail')} - ${sandbox.value.sandboxID}`
    : $t('sandboxs.modal_title_detail')
})

const templateName = computed(() => {
  if (!sandbox.value?.templateID) return '-'
  const template = props.templates.find(t => t.templateID === sandbox.value.templateID)
  return template?.aliases?.[0] || template?.templateID || sandbox.value.templateID
})

const metadataString = computed(() => {
  return JSON.stringify(sandbox.value?.metadata || {}, null, 2)
})

const latestMetric = computed(() => {
  return metrics.value.length > 0 ? metrics.value[metrics.value.length - 1] : null
})

// 指标表格列
const metricsColumns = computed(() => [
  {
    title: $t('sandboxs.label_timestamp'),
    key: 'timestamp',
    render: (row) => formatDateTime(row.timestamp),
    width: 180
  },
  {
    title: $t('sandboxs.label_cpu_usage'),
    key: 'cpuUsedPct',
    render: (row) => `${row.cpuUsedPct.toFixed(2)}%`,
    width: 120
  },
  {
    title: $t('sandboxs.label_memory_used'),
    key: 'memUsedMiB',
    render: (row) => `${row.memUsedMiB} MB`,
    width: 120
  },
  {
    title: $t('sandboxs.label_memory_total'),
    key: 'memTotalMiB',
    render: (row) => `${row.memTotalMiB} MB`,
    width: 120
  },
  {
    title: $t('sandboxs.label_memory_usage'),
    key: 'memUsage',
    render: (row) => `${((row.memUsedMiB / row.memTotalMiB) * 100).toFixed(1)}%`,
    width: 120
  }
])

// 方法
const formatDateTime = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
  })
}

const fetchSandboxDetail = async () => {
  if (!props.sandboxId) return
  
  loading.value = true
  try {
    sandbox.value = await api.getSandboxById(props.sandboxId)
  } catch (error) {
    console.error('获取沙箱详情失败:', error)
    message.error($t('sandboxs.message_get_detail_failed'))
  } finally {
    loading.value = false
  }
}

const fetchLogs = async () => {
  if (!props.sandboxId) return
  
  logsLoading.value = true
  try {
    const result = await api.getSandboxLogs(props.sandboxId, {
      limit: logLimit.value
    })
    logs.value = result.logs || []
  } catch (error) {
    console.error('获取日志失败:', error)
    message.error($t('sandboxs.message_get_logs_failed'))
  } finally {
    logsLoading.value = false
  }
}

const fetchMetrics = async () => {
  if (!props.sandboxId) return
  
  metricsLoading.value = true
  try {
    const result = await api.getSandboxMetrics(props.sandboxId)
    metrics.value = Array.isArray(result) ? result : []
    
    // 获取数据后，等待DOM更新完成再处理图表
    await nextTick()
    
    // 延迟一点时间确保加载状态结束，DOM重新渲染完成
    setTimeout(() => {
      if (metrics.value.length > 0) {
        // 重新初始化图表
        if (chart) {
          chart.dispose()
          chart = null
        }
        initChart()
        updateChart()
      }
    }, 100)
  } catch (error) {
    console.error('获取指标失败:', error)
    message.error($t('sandboxs.message_get_metrics_failed'))
    // 清空数据
    metrics.value = []
  } finally {
    metricsLoading.value = false
  }
}



const handleClose = () => {
  visible.value = false
}

// 处理标签页切换
const handleTabChange = (tabName) => {
  if (tabName === 'metrics') {
    // 每次切换到 metrics 标签时都重新初始化图表
    nextTick(() => {
      // 先清理现有图表
      if (chart) {
        chart.dispose()
        chart = null
      }
      
      // 延迟一点时间确保DOM渲染完成，然后重新初始化
      setTimeout(() => {
        if (metrics.value.length > 0) {
          initChart()
          updateChart()
        }
      }, 100)
    })
  }
}

// 初始化图表
const initChart = () => {
  if (!chartContainer.value) {
    return
  }
  
  try {
    chart = echarts.init(chartContainer.value)
    
    const option = {
      title: {
        text: $t('sandboxs.label_metrics_chart'),
        left: 'center',
        textStyle: {
          fontSize: 14,
          fontWeight: 500
        }
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross'
        },
        formatter: function (params) {
          if (!params || params.length === 0) return ''
          const time = new Date(params[0].axisValue).toLocaleString('zh-CN', { hour12: false })
          let result = `<div style="font-size: 12px;">${time}</div>`
          params.forEach(param => {
            result += `<div style="margin-top: 4px;">
              <span style="color: ${param.color};">●</span> 
              ${param.seriesName}: ${param.value}%
            </div>`
          })
          return result
        }
      },
      legend: {
        data: [$t('sandboxs.label_cpu_usage'), $t('sandboxs.label_memory_usage')],
        bottom: 0
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '15%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: [],
        axisLabel: {
          formatter: function (value) {
            return new Date(value).toLocaleTimeString('zh-CN', { hour12: false })
          }
        }
      },
      yAxis: {
        type: 'value',
        name: '使用率 (%)',
        axisLabel: {
          formatter: '{value}%'
        },
        min: 0
      },
      series: [
        {
          name: $t('sandboxs.label_cpu_usage'),
          type: 'line',
          data: [],
          smooth: true,
          lineStyle: {
            color: '#3b82f6'
          },
          itemStyle: {
            color: '#3b82f6'
          }
        },
        {
          name: $t('sandboxs.label_memory_usage'),
          type: 'line',
          data: [],
          smooth: true,
          lineStyle: {
            color: '#22c55e'
          },
          itemStyle: {
            color: '#22c55e'
          }
        }
      ]
    }
    
    chart.setOption(option)
  } catch (error) {
    console.error('图表初始化失败:', error)
  }
}

// 更新图表数据
const updateChart = () => {
  if (!metrics.value.length || !chart) {
    return
  }
  
  try {
    const timestamps = metrics.value.map(m => m.timestamp)
    const cpuData = metrics.value.map(m => parseFloat(m.cpuUsedPct.toFixed(2)))
    const memoryData = metrics.value.map(m => parseFloat(((m.memUsedMiB / m.memTotalMiB) * 100).toFixed(2)))
    
    const updateOption = {
      xAxis: {
        data: timestamps
      },
      series: [
        {
          data: cpuData
        },
        {
          data: memoryData
        }
      ]
    }
    
    chart.setOption(updateOption)
  } catch (error) {
    console.error('更新图表数据失败:', error)
  }
}

// 监听器
watch(() => props.visible, async (newVal) => {
  if (newVal && props.sandboxId) {
    fetchSandboxDetail()
    fetchLogs()
    fetchMetrics()
  }
})

watch(() => props.sandboxId, (newVal) => {
  if (newVal && props.visible) {
    fetchSandboxDetail()
    fetchLogs()
    fetchMetrics()
  }
})

// 组件挂载时添加窗口大小变化监听器
onMounted(() => {
  window.addEventListener('resize', () => {
    if (chart) {
      chart.resize()
    }
  })
})

// 在模态框关闭时清理图表
watch(() => props.visible, (newVal) => {
  if (!newVal) {
    if (chart) {
      chart.dispose()
      chart = null
    }
  }
})
</script> 