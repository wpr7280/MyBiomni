<script setup>
import SideLogo from './components/SideLogo.vue'
import SideMenu from './components/SideMenu.vue'
import SideFooter from './components/SideFooter.vue'
</script>

<template>
  <div class="sidebar-container">
    <!-- 顶部Logo -->
    <SideLogo />
    
    <!-- 中间菜单区域 - 可滚动 -->
    <div class="sidebar-menu-container">
      <SideMenu />
    </div>
    
    <!-- 底部Footer - 固定 -->
    <SideFooter />
  </div>
</template>

<style lang="scss" scoped>
.sidebar-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: var(--n-color);
}

.sidebar-menu-container {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  min-height: 0; // 重要：确保flex子元素可以收缩
  
  // 自定义滚动条样式
  &::-webkit-scrollbar {
    width: 4px;
  }
  
  &::-webkit-scrollbar-track {
    background: transparent;
  }
  
  &::-webkit-scrollbar-thumb {
    background: var(--n-border-color);
    border-radius: 2px;
  }
  
  &::-webkit-scrollbar-thumb:hover {
    background: var(--text-color-tertiary);
  }
}

// Dark模式适配
:deep(.dark) {
  .sidebar-container {
    background: var(--n-color);
  }
  
  .sidebar-menu-container::-webkit-scrollbar-thumb {
    background: var(--n-border-color);
    
    &:hover {
      background: var(--text-color-tertiary);
    }
  }
}
</style>
