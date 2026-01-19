<template>
  <div class="side-footer" :class="{ 'side-footer--collapsed': appStore.collapsed }">
    <!-- 分割线 -->
    <div class="footer-divider"></div>
    
    <!-- 折叠状态：只显示图标 -->
    <div v-if="appStore.collapsed" class="footer-collapsed">
      <div class="footer-item" @click="handleContact">
        <n-tooltip placement="right" trigger="hover">
          <template #trigger>
            <div class="footer-icon">
              <n-icon size="18" color="var(--text-color-secondary)">
                <svg viewBox="0 0 24 24">
                  <path fill="currentColor" d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5l-8-5V6l8 5l8-5v2z"/>
                </svg>
              </n-icon>
            </div>
          </template>
          {{ $t('footer.contact_us') }}
        </n-tooltip>
      </div>
      
      <div class="footer-item" @click="handlePrivacy">
        <n-tooltip placement="right" trigger="hover">
          <template #trigger>
            <div class="footer-icon">
              <n-icon size="18" color="var(--text-color-secondary)">
                <svg viewBox="0 0 24 24">
                  <path fill="currentColor" d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12c5.16-1.26 9-6.45 9-12V5l-9-4zm0 10.99h7c-.53 4.12-3.28 7.79-7 8.94V12H5V6.3l7-3.11v8.8z"/>
                </svg>
              </n-icon>
            </div>
          </template>
          {{ $t('footer.privacy_policy') }}
        </n-tooltip>
      </div>
      
      <div class="footer-item" @click="handleTerms">
        <n-tooltip placement="right" trigger="hover">
          <template #trigger>
            <div class="footer-icon">
              <n-icon size="18" color="var(--text-color-secondary)">
                <svg viewBox="0 0 24 24">
                  <path fill="currentColor" d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/>
                </svg>
              </n-icon>
            </div>
          </template>
          {{ $t('footer.user_agreement') }}
        </n-tooltip>
      </div>
    </div>
    
    <!-- 展开状态：显示完整内容 -->
    <div v-else class="footer-expanded">
      <!-- 联系我们 -->
      <div class="footer-section">
        <div class="footer-title">{{ $t('footer.contact_us') }}</div>
        <div class="footer-links">
          <a href="mailto:contact-us@agentnest.cn" class="footer-link">
            <n-icon size="14" class="footer-link-icon">
              <svg viewBox="0 0 24 24">
                <path fill="currentColor" d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5l-8-5V6l8 5l8-5v2z"/>
              </svg>
            </n-icon>
            contact-us@agentnest.cn
          </a>
        </div>
      </div>
      
      <!-- 法律信息 -->
      <div class="footer-section">
        <div class="footer-title">{{ $t('footer.legal_info') }}</div>
        <div class="footer-links">
          <a href="/static/privacy.html" target="_blank" class="footer-link">
            <n-icon size="14" class="footer-link-icon">
              <svg viewBox="0 0 24 24">
                <path fill="currentColor" d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12c5.16-1.26 9-6.45 9-12V5l-9-4zm0 10.99h7c-.53 4.12-3.28 7.79-7 8.94V12H5V6.3l7-3.11v8.8z"/>
              </svg>
            </n-icon>
            {{ $t('footer.privacy_policy') }}
          </a>
          <a href="/static/terms.html" target="_blank" class="footer-link">
            <n-icon size="14" class="footer-link-icon">
              <svg viewBox="0 0 24 24">
                <path fill="currentColor" d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/>
              </svg>
            </n-icon>
            {{ $t('footer.user_agreement') }}
          </a>
        </div>
      </div>
      
      <!-- 备案信息 -->
      <div class="footer-section">
        <div class="footer-title">{{ $t('footer.icp_info') }}</div>
        <div class="footer-text">
          <a href="https://beian.miit.gov.cn/" target="_blank" class="footer-link">
            {{ $t('footer.icp_number') }}
          </a>
        </div>
      </div>
      
      <!-- 版权信息 -->
      <div class="footer-section">
        <div class="footer-copyright">
          {{ $t('footer.copyright') }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAppStore } from '@/store'

const appStore = useAppStore()

// 处理联系我们
function handleContact() {
  window.open('mailto:contact-us@agentnest.cn')
}

// 处理隐私政策
function handlePrivacy() {
  window.open('/static/privacy.html', '_blank')
}

// 处理用户协议
function handleTerms() {
  window.open('/static/terms.html', '_blank')
}
</script>

<style lang="scss" scoped>
.side-footer {
  position: relative;
  background: var(--n-color);
  border-top: 1px solid var(--n-border-color);
  transition: all 0.3s ease;
  flex-shrink: 0; // 防止footer被压缩
  
  &--collapsed {
    padding: 8px 0;
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
  gap: 8px;
  padding: 8px 0;
}

.footer-item {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 6px;
  cursor: pointer;
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
}

.footer-section {
  margin-bottom: 16px;
  
  &:last-child {
    margin-bottom: 0;
  }
}

.footer-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-color-secondary);
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.footer-links {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.footer-link {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--text-color-secondary);
  text-decoration: none;
  transition: all 0.2s ease;
  padding: 4px 0;
  
  &:hover {
    color: var(--primary-color);
    text-decoration: none;
  }
}

.footer-link-icon {
  flex-shrink: 0;
}

.footer-text {
  font-size: 12px;
  color: var(--text-color-secondary);
  line-height: 1.4;
}

.footer-copyright {
  font-size: 11px;
  color: var(--text-color-tertiary);
  text-align: center;
  padding: 8px 0 0 0;
  border-top: 1px solid var(--n-border-color);
  margin-top: 12px;
}

// 响应式设计
@media (max-width: 768px) {
  .footer-expanded {
    padding: 12px;
  }
  
  .footer-section {
    margin-bottom: 12px;
  }
  
  .footer-title {
    font-size: 11px;
  }
  
  .footer-link {
    font-size: 11px;
  }
  
  .footer-copyright {
    font-size: 10px;
  }
}

// Dark模式适配
:deep(.dark) {
  .side-footer {
    background: var(--n-color);
    border-top-color: var(--n-border-color);
  }
  
  .footer-divider {
    background: var(--n-border-color);
  }
  
  .footer-item:hover {
    background: var(--n-item-color-hover);
  }
  
  .footer-title {
    color: var(--text-color-secondary);
  }
  
  .footer-link {
    color: var(--text-color-secondary);
    
    &:hover {
      color: var(--primary-color);
    }
  }
  
  .footer-text {
    color: var(--text-color-secondary);
  }
  
  .footer-copyright {
    color: var(--text-color-tertiary);
    border-top-color: var(--n-border-color);
  }
}
</style> 