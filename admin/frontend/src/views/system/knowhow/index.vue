<script setup>
import { NCard, NIcon } from 'naive-ui'
import CommonPage from '@/components/page/CommonPage.vue'
</script>

<template>
  <CommonPage :show-header="false">
    <div class="page-container">
      <NCard class="page-card" title="文档管理">
        <template #header-extra>
          <NIcon size="20" color="#18a058">
            <svg viewBox="0 0 24 24">
              <path fill="currentColor" d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/>
            </svg>
          </NIcon>
        </template>
        <div style="padding: 40px; text-align: center; color: #999;">
          <p style="font-size: 16px;">文档管理功能开发中...</p>
          <p style="font-size: 14px; margin-top: 8px;">管理员可以创建、编辑和管理 Know-How 文档</p>
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
