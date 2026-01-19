<script setup>
import { NCard, NIcon } from 'naive-ui'
import CommonPage from '@/components/page/CommonPage.vue'
</script>

<template>
  <CommonPage :show-header="false">
    <div class="page-container">
      <NCard class="page-card" title="系统设置">
        <template #header-extra>
          <NIcon size="20" color="#18a058">
            <svg viewBox="0 0 24 24">
              <path fill="currentColor" d="M19.14 12.94c.04-.3.06-.61.06-.94c0-.32-.02-.64-.07-.94l2.03-1.58a.49.49 0 0 0 .12-.61l-1.92-3.32a.488.488 0 0 0-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54a.484.484 0 0 0-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.05.3-.09.63-.09.94s.02.64.07.94l-2.03 1.58a.49.49 0 0 0-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6s3.6 1.62 3.6 3.6s-1.62 3.6-3.6 3.6z"/>
            </svg>
          </NIcon>
        </template>
        <div style="padding: 40px; text-align: center; color: #999;">
          <p style="font-size: 16px;">系统设置功能开发中...</p>
          <p style="font-size: 14px; margin-top: 8px;">配置系统参数、并发任务数、会话超时等</p>
        </div>
      </NCard>
    </div>
  </CommonPage>
</template>

<style scoped>
.page-container {
  padding: 20px 24px;
}

.page-card {
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.page-card :deep(.n-card-header) {
  padding: 16px 24px;
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
  border-bottom: 1px solid #f0f0f0;
}
</style>
