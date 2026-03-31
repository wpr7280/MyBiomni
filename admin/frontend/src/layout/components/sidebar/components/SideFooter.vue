<template>
  <div class="side-footer" :class="{ 'side-footer--collapsed': appStore.collapsed }">
    <!-- 分割线 -->
    <div class="footer-divider"></div>
    
    <!-- 折叠状态：只显示图标 -->
    <div v-if="appStore.collapsed" class="footer-collapsed">
      <div class="footer-item">
        <n-tooltip placement="right" trigger="hover">
          <template #trigger>
            <div class="footer-icon">
              <n-icon size="18" color="var(--text-color-secondary)">
                <svg viewBox="0 0 24 24">
                  <path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                </svg>
              </n-icon>
            </div>
          </template>
          WarpHelix
        </n-tooltip>
      </div>
    </div>
    
    <!-- 展开状态：显示版权信息 -->
    <div v-else class="footer-expanded">
      <div class="footer-copyright">
        {{ $t('footer.copyright') }}
      </div>
      
      <!-- 链接 -->
      <div class="footer-links">
        <a href="/static/privacy.html" target="_blank" class="footer-link">
          {{ $t('footer.privacy_policy') }}
        </a>
        <span class="footer-separator">|</span>
        <a href="/static/terms.html" target="_blank" class="footer-link">
          {{ $t('footer.user_agreement') }}
        </a>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAppStore } from '@/store'

const appStore = useAppStore()
</script>

<style lang="scss" scoped>
.side-footer {
  position: relative;
  background: var(--n-color);
  border-top: 1px solid var(--n-border-color);
  transition: all 0.3s ease;
  flex-shrink: 0;
  
  &--collapsed {
    padding: 12px 0;
  }
}

.footer-divider {
  height: 1px;
  background: var(--n-border-color);
  margin: 0;
}

// 折叠状态样式
.footer-collapsed {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 0;
}

.footer-item {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 6px;
  transition: all 0.2s ease;
  
  &:hover {
    background: var(--n-item-color-hover);
    
    .footer-icon {
      color: var(--primary-color) !important;
    }
  }
}

.footer-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s ease;
}

// 展开状态样式
.footer-expanded {
  padding: 16px;
  text-align: center;
}

.footer-copyright {
  font-size: 11px;
  color: var(--text-color-tertiary);
  margin-bottom: 8px;
  line-height: 1.4;
}

.footer-links {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 11px;
}

.footer-link {
  color: var(--text-color-secondary);
  text-decoration: none;
  transition: color 0.2s ease;
  
  &:hover {
    color: var(--primary-color);
  }
}

.footer-separator {
  color: var(--text-color-tertiary);
}
</style>
