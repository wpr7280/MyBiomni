<template>
  <AppPage :show-footer="false">
    <div flex-1>
      <!-- 强制修改密码提示 -->
      <n-alert 
        v-if="userStore.forcePasswordChange" 
        type="warning" 
        :title="$t('views.workbench.alert_force_password_change_title')"
        closable
        style="margin-bottom: 16px;"
      >
        <template #icon>
          <n-icon size="20">
            <svg viewBox="0 0 24 24">
              <path fill="currentColor" d="M12 2L1 21h22M12 6l7.53 13H4.47M11 10v4h2v-4m-2 6v2h2v-2"/>
            </svg>
          </n-icon>
        </template>
        <div>
          <p>{{ $t('views.workbench.alert_force_password_change_message') }}</p>
          <n-button 
            type="primary" 
            size="small" 
            @click="goToProfile"
            style="margin-top: 12px;"
          >
            {{ $t('views.workbench.button_go_to_change_password') }}
          </n-button>
        </div>
      </n-alert>

      <n-card rounded-10>
        <div flex items-center justify-between>
          <div flex items-center>
            <div class="default-avatar-large" rounded-full width="60" height="60" bg-gradient-to-br from-purple-400 to-pink-500 flex items-center justify-center>
              <n-icon size="28" color="white">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 2L15.09 8.26L22 9L17 13.74L18.18 20.02L12 16.77L5.82 20.02L7 13.74L2 9L8.91 8.26L12 2Z" fill="currentColor"/>
                </svg>
              </n-icon>
            </div>
            <div ml-10>
              <p text-20 font-semibold>
                {{ $t('views.workbench.text_hello', { username: userStore.name }) }}
              </p>
              <p mt-5 text-14 op-60>{{ $t('views.workbench.text_welcome') }}</p>
            </div>
          </div>
        </div>
      </n-card>
    </div>
  </AppPage>
</template>

<script setup>
import { useUserStore } from '@/store'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { onMounted } from 'vue'

const { t } = useI18n({ useScope: 'global' })
const userStore = useUserStore()
const router = useRouter()

// 跳转到个人中心修改密码
function goToProfile() {
  router.push('/profile')
}

// 页面加载时检查是否需要强制修改密码
onMounted(() => {
  if (userStore.forcePasswordChange) {
    // 可以选择直接跳转，或者显示提示
    // router.push('/profile')
  }
})
</script>
