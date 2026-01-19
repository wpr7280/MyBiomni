<script setup>
import { NCard, NIcon } from 'naive-ui'
import CommonPage from '@/components/page/CommonPage.vue'
</script>

<template>
  <CommonPage :show-header="false">
    <div class="page-container">
      <NCard class="page-card" title="对话记录">
        <template #header-extra>
          <NIcon size="20" color="#18a058">
            <svg viewBox="0 0 24 24">
              <path fill="currentColor" d="M13 3a9 9 0 0 0-9 9H1l3.89 3.89l.07.14L9 12H6c0-3.87 3.13-7 7-7s7 3.13 7 7s-3.13 7-7 7c-1.93 0-3.68-.79-4.94-2.06l-1.42 1.42A8.954 8.954 0 0 0 13 21a9 9 0 0 0 0-18zm-1 5v5l4.28 2.54l.72-1.21l-3.5-2.08V8H12z"/>
            </svg>
          </NIcon>
        </template>
        <div style="padding: 40px; text-align: center; color: #999;">
          <p style="font-size: 16px;">对话记录功能开发中...</p>
          <p style="font-size: 14px; margin-top: 8px;">管理员可以查看所有用户的对话记录</p>
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
