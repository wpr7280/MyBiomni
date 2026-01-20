<template>
  <AppPage :show-footer="true" bg-cover :style="{ backgroundImage: `url(${bgImg})` }">
    <div
      style="transform: translateY(25px)"
      class="m-auto max-w-1500 min-w-345 f-c-c rounded-10 bg-white bg-opacity-60 p-15 card-shadow"
      dark:bg-dark
    >
      <div hidden w-380 px-20 py-35 md:block>
        <icon-custom-front-page pt-10 text-300 color-primary></icon-custom-front-page>
      </div>

      <div w-320 flex-col px-20 py-35>
        <h5 f-c-c text-24 font-normal color="#6a6a6a">
          <icon-custom-logo mr-10 text-50 color-primary />
          {{ $t('app_name') }}
        </h5>

        <!-- 登录表单 -->
        <div class="form-content">
          <div mt-30>
            <n-input
              v-model:value="loginInfo.email"
              autofocus
              class="h-50 items-center pl-10 text-16"
              :placeholder="$t('views.login.placeholder_email')"
              :maxlength="50"
            />
          </div>
          <div mt-30>
            <n-input
              v-model:value="loginInfo.password"
              class="h-50 items-center pl-10 text-16"
              type="password"
              show-password-on="mousedown"
              :placeholder="$t('views.login.placeholder_password')"
              :maxlength="20"
              @keypress.enter="handleLogin"
            />
          </div>

          <div mt-20>
            <n-button h-50 w-full type="primary" :loading="loading" @click="handleLogin">
              {{ $t('views.login.text_login') }}
            </n-button>
          </div>
          
          <!-- 错误提示 -->
          <div v-if="errorMsg" mt-15 class="error-message">
            <n-alert type="error" :show-icon="false">
              {{ errorMsg }}
            </n-alert>
          </div>
        </div>

        <!-- 协议/隐私 -->
        <div mt-15 flex justify-center gap-15 text-12 color-gray-500>
          <a href="/static/privacy.html" class="privacy-link">{{ $t('footer.privacy_policy') }}</a>
          <span class="separator">|</span>
          <a href="/static/terms.html" class="privacy-link">{{ $t('footer.user_agreement') }}</a>
        </div>
        <div mt-10 text-center text-11 color-gray-400>
          {{ $t('footer.copyright') }}
        </div>
      </div>
    </div>
  </AppPage>
</template>

<script setup>
import { lStorage, setToken } from '@/utils'
import bgImg from '@/assets/images/login_bg.webp'
import api from '@/api'
import { addDynamicRoutes } from '@/router'
import { useI18n } from 'vue-i18n'

const router = useRouter()
const { query } = useRoute()
const { t } = useI18n({ useScope: 'global' })

const loginInfo = ref({
  email: '',
  password: '',
})

initLoginInfo()

function initLoginInfo() {
  const localLoginInfo = lStorage.get('loginInfo')
  if (localLoginInfo) {
    loginInfo.value.email = localLoginInfo.email || ''
    loginInfo.value.password = localLoginInfo.password || ''
  }
}

const loading = ref(false)
const errorMsg = ref('')

/** 基础校验 */
function validate(email, password) {
  if (!email || !password) {
    return t('views.login.message_input_username_password')
  }
  const emailReg = /^[\w-.]+@([\w-]+\.)+[\w-]{2,}$/
  if (!emailReg.test(email)) return t('views.login.message_email_format')
  if (password.length < 6) return t('views.login.message_password_length')
  return ''
}

/** 登录 */
async function handleLogin() {
  const { email, password } = loginInfo.value
  errorMsg.value = validate(email, password)
  if (errorMsg.value) return

  try {
    loading.value = true
    errorMsg.value = ''
    $message.loading(t('views.login.message_verifying'))
    const res = await api.login({ email, password: password.toString() })
    $message.success(t('views.login.message_login_success'))
    setToken(res.data.token)
    await addDynamicRoutes()
    if (query.redirect) {
      const path = query.redirect
      Reflect.deleteProperty(query, 'redirect')
      router.push({ path, query })
    } else {
      router.push('/')
    }
  } catch (e) {
    console.error('Login error:', e)
    errorMsg.value = e?.message || t('views.login.message_login_failed')
  }
  loading.value = false
}
</script>

<style scoped>
.form-content {
  animation: fadeInUp 0.4s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 错误消息样式 */
.error-message {
  animation: shake 0.5s ease-in-out;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}

/* 隐私链接样式 */
.privacy-link {
  color: #999;
  text-decoration: none;
  transition: color 0.3s ease;
}

.privacy-link:hover {
  color: var(--primary-color);
  text-decoration: underline;
}

.separator {
  color: #ddd;
  margin: 0 8px;
}
</style>
