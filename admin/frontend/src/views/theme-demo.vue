<template>
  <AppPage title="主题配色方案演示">
    <div class="theme-demo">
      <!-- 主色调展示 -->
      <div class="color-section">
        <h2 class="section-title">主色调系统</h2>
        <div class="color-grid">
          <div class="color-item">
            <div class="color-block primary-500"></div>
            <div class="color-info">
              <span class="color-name">主色</span>
              <span class="color-value">#1C9CEB</span>
            </div>
          </div>
          <div class="color-item">
            <div class="color-block primary-400"></div>
            <div class="color-info">
              <span class="color-name">浅色</span>
              <span class="color-value">#4DB5FF</span>
            </div>
          </div>
          <div class="color-item">
            <div class="color-block primary-600"></div>
            <div class="color-info">
              <span class="color-name">深色</span>
              <span class="color-value">#0F7BC7</span>
            </div>
          </div>
          <div class="color-item">
            <div class="color-block primary-50"></div>
            <div class="color-info">
              <span class="color-name">超浅色</span>
              <span class="color-value">#E6F4FF</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 辅助色展示 -->
      <div class="color-section">
        <h2 class="section-title">辅助色系统</h2>
        <div class="color-grid">
          <div class="color-item">
            <div class="color-block success-500"></div>
            <div class="color-info">
              <span class="color-name">成功色</span>
              <span class="color-value">#52C41A</span>
            </div>
          </div>
          <div class="color-item">
            <div class="color-block warning-500"></div>
            <div class="color-info">
              <span class="color-name">警告色</span>
              <span class="color-value">#FAAD14</span>
            </div>
          </div>
          <div class="color-item">
            <div class="color-block error-500"></div>
            <div class="color-info">
              <span class="color-name">错误色</span>
              <span class="color-value">#FF4D4F</span>
            </div>
          </div>
          <div class="color-item">
            <div class="color-block info-500"></div>
            <div class="color-info">
              <span class="color-name">信息色</span>
              <span class="color-value">#1890FF</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 组件展示 -->
      <div class="component-section">
        <h2 class="section-title">组件样式展示</h2>
        
        <!-- 按钮展示 -->
        <div class="component-group">
          <h3 class="group-title">按钮</h3>
          <div class="button-group">
            <n-button type="primary">主要按钮</n-button>
            <n-button type="success">成功按钮</n-button>
            <n-button type="warning">警告按钮</n-button>
            <n-button type="error">错误按钮</n-button>
            <n-button type="info">信息按钮</n-button>
          </div>
        </div>

        <!-- 卡片展示 -->
        <div class="component-group">
          <h3 class="group-title">卡片</h3>
          <div class="card-group">
            <n-card title="示例卡片" class="demo-card">
              <p>这是一个使用新配色方案的卡片组件。</p>
              <template #footer>
                <n-button type="primary" size="small">操作</n-button>
              </template>
            </n-card>
          </div>
        </div>

        <!-- 输入框展示 -->
        <div class="component-group">
          <h3 class="group-title">输入框</h3>
          <div class="input-group">
            <n-input placeholder="请输入内容" />
            <n-input placeholder="聚焦状态" class="mt-3" />
          </div>
        </div>

        <!-- 标签页展示 -->
        <div class="component-group">
          <h3 class="group-title">标签页</h3>
          <n-tabs type="line" animated>
            <n-tab-pane name="tab1" tab="标签页1">
              <p>这是第一个标签页的内容。</p>
            </n-tab-pane>
            <n-tab-pane name="tab2" tab="标签页2">
              <p>这是第二个标签页的内容。</p>
            </n-tab-pane>
            <n-tab-pane name="tab3" tab="标签页3">
              <p>这是第三个标签页的内容。</p>
            </n-tab-pane>
          </n-tabs>
        </div>

        <!-- 进度条展示 -->
        <div class="component-group">
          <h3 class="group-title">进度条</h3>
          <div class="progress-group">
            <n-progress type="line" :percentage="75" />
            <n-progress type="circle" :percentage="60" class="mt-3" />
          </div>
        </div>

        <!-- 消息展示 -->
        <div class="component-group">
          <h3 class="group-title">消息提示</h3>
          <div class="message-group">
            <n-button @click="showMessage('success')" type="success" size="small">成功消息</n-button>
            <n-button @click="showMessage('warning')" type="warning" size="small" class="ml-2">警告消息</n-button>
            <n-button @click="showMessage('error')" type="error" size="small" class="ml-2">错误消息</n-button>
            <n-button @click="showMessage('info')" type="info" size="small" class="ml-2">信息消息</n-button>
          </div>
        </div>
      </div>
    </div>
  </AppPage>
</template>

<script setup>
import { useMessage } from 'naive-ui'

const $message = useMessage()

function showMessage(type) {
  const messages = {
    success: '操作成功！',
    warning: '请注意这个警告！',
    error: '发生了一个错误！',
    info: '这是一条信息提示！'
  }
  
  $message[type](messages[type])
}
</script>

<style scoped>
.theme-demo {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.section-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-color-primary);
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid var(--primary-color);
}

.color-section {
  margin-bottom: 40px;
}

.color-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.color-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  border-radius: 8px;
  background: white;
  box-shadow: var(--shadow-1);
  transition: all 0.3s ease;
}

.color-item:hover {
  box-shadow: var(--shadow-2);
  transform: translateY(-2px);
}

.color-block {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  border: 2px solid var(--border-color);
}

.color-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.color-name {
  font-weight: 600;
  color: var(--text-color-primary);
}

.color-value {
  font-size: 12px;
  color: var(--text-color-secondary);
  font-family: 'Monaco', 'Menlo', monospace;
}

/* 颜色块样式 */
.primary-500 { background-color: var(--primary-color); }
.primary-400 { background-color: var(--primary-color-hover); }
.primary-600 { background-color: var(--primary-color-pressed); }
.primary-50 { background-color: var(--primary-color-suppl); }

.success-500 { background-color: var(--success-color); }
.warning-500 { background-color: var(--warning-color); }
.error-500 { background-color: var(--error-color); }
.info-500 { background-color: var(--info-color); }

/* 组件展示样式 */
.component-section {
  margin-top: 40px;
}

.component-group {
  margin-bottom: 30px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: var(--shadow-1);
}

.group-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-color-primary);
  margin-bottom: 15px;
}

.button-group {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.card-group {
  max-width: 400px;
}

.demo-card {
  transition: all 0.3s ease;
}

.demo-card:hover {
  box-shadow: var(--shadow-3);
}

.input-group {
  max-width: 300px;
}

.progress-group {
  max-width: 400px;
}

.message-group {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .theme-demo {
    padding: 10px;
  }
  
  .color-grid {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 15px;
  }
  
  .color-item {
    padding: 10px;
  }
  
  .color-block {
    width: 50px;
    height: 50px;
  }
  
  .button-group {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .message-group {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style> 