<script setup>
import { NCard, NIcon } from 'naive-ui'
import CommonPage from '@/components/page/CommonPage.vue'
</script>

<template>
  <CommonPage :show-header="false">
    <div class="page-container">
      <NCard class="page-card" title="配额管理">
        <template #header-extra>
          <NIcon size="20" color="#18a058">
            <svg viewBox="0 0 24 24">
              <path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10s10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
            </svg>
          </NIcon>
        </template>
        <div style="padding: 40px; text-align: center; color: #999;">
          <p style="font-size: 16px;">配额管理功能开发中...</p>
          <p style="font-size: 14px; margin-top: 8px;">敬请期待</p>
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
