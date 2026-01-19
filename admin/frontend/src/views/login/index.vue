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

        <!-- 步骤指示器 -->
        <div v-if="currentForm !== 'login'" mt-20 mb-5>
          <div flex items-center justify-center gap-15>
            <div class="step-indicator" :class="{ active: currentForm === 'forgot' }">
              <div class="step-circle">1</div>
              <span class="step-text">{{ $t('views.login.step_enter_email') }}</span>
            </div>
            <div class="step-line" :class="{ active: currentForm === 'reset' }"></div>
            <div class="step-indicator" :class="{ active: currentForm === 'reset' }">
              <div class="step-circle">2</div>
              <span class="step-text">{{ $t('views.login.step_reset_password') }}</span>
            </div>
          </div>
        </div>

        <!-- 表单容器，添加过渡动画 -->
        <div class="form-container" :key="currentForm">
          <!-- 登录表单 -->
          <div v-if="currentForm === 'login'" class="form-content">
            <div mt-30>
              <n-input
                v-model:value="loginInfo.email"
                autofocus
                class="h-50 items-center pl-10 text-16"
                :placeholder="$t('views.login.placeholder_email')"
                :maxlength="20"
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

            <div mt-20 flex items-center gap-10>
              <n-button h-50 flex-1 type="primary" :loading="loading" @click="handleLogin">
                {{ $t('views.login.text_login') }}
              </n-button>
              <n-button h-50 flex-1 type="default" class="register-btn" @click="goRegister">
                {{ $t('views.login.text_register') }}
              </n-button>
            </div>
            
            <!-- 忘记密码链接 -->
            <div mt-15 text-center>
              <n-button text type="primary" size="small" class="forgot-password-btn" @click="currentForm = 'forgot'">
                <template #icon>
                  <n-icon><svg viewBox="0 0 24 24"><path fill="currentColor" d="M12 17a2 2 0 0 0 2-2c0-1.11-.89-2-2-2a2 2 0 0 0-2 2a2 2 0 0 0 2 2m6-9a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V10a2 2 0 0 1 2-2h1V6a5 5 0 0 1 5-5a5 5 0 0 1 5 5v2h1m-6-5a3 3 0 0 0-3 3v2h6V6a3 3 0 0 0-3-3Z"/></svg></n-icon>
                </template>
                {{ $t('views.login.text_forgot_password') }}
              </n-button>
            </div>
            
            <!-- 错误提示 -->
            <div v-if="errorMsg" mt-15 class="error-message">
              <n-alert type="error" :show-icon="false">
                {{ errorMsg }}
              </n-alert>
            </div>
          </div>

          <!-- 忘记密码 - 输入邮箱阶段 -->
          <div v-if="currentForm === 'forgot'" class="form-content">
            <div mt-20 text-center>
              <div class="forgot-title">
                <n-icon size="40" color="var(--primary-color)" mb-10>
                  <svg viewBox="0 0 24 24"><path fill="currentColor" d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5l-8-5V6l8 5l8-5v2z"/></svg>
                </n-icon>
                <h3 text-18 font-medium color="#333" mb-10>{{ $t('views.login.title_forgot_password') }}</h3>
                <p text-14 color="#999" mb-20>{{ $t('views.login.desc_forgot_password') }}</p>
              </div>
            </div>
            
            <div mt-10>
              <n-input
                v-model:value="forgotForm.email"
                autofocus
                class="h-50 items-center pl-10 text-16"
                :placeholder="$t('views.login.placeholder_email')"
                :maxlength="50"
              >
                <template #prefix>
                  <n-icon color="#999">
                    <svg viewBox="0 0 24 24"><path fill="currentColor" d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5l-8-5V6l8 5l8-5v2z"/></svg>
                  </n-icon>
                </template>
              </n-input>
            </div>

            <div mt-25 flex flex-col gap-10>
              <n-button h-50 type="primary" :loading="sendCodeLoading" @click="handleSendCode">
                <template #icon>
                  <n-icon><svg viewBox="0 0 24 24"><path fill="currentColor" d="M2 21l21-9L2 3v7l15 2l-15 2v7z"/></svg></n-icon>
                </template>
                {{ $t('views.login.text_send_code') }}
              </n-button>
              <n-button h-45 tertiary @click="currentForm = 'login'">
                <template #icon>
                  <n-icon><svg viewBox="0 0 24 24"><path fill="currentColor" d="M20 11H7.83l5.59-5.59L12 4l-8 8l8 8l1.41-1.41L7.83 13H20v-2z"/></svg></n-icon>
                </template>
                {{ $t('views.login.text_back_to_login') }}
              </n-button>
            </div>
            
            <!-- 错误提示 -->
            <div v-if="errorMsg" mt-15 class="error-message">
              <n-alert type="error" :show-icon="false">
                {{ errorMsg }}
              </n-alert>
            </div>
          </div>

          <!-- 忘记密码 - 验证码和新密码阶段 -->
          <div v-if="currentForm === 'reset'" class="form-content">
            <div mt-20 text-center>
              <div class="reset-title">
                <n-icon size="40" color="var(--primary-color)" mb-10>
                  <svg viewBox="0 0 24 24"><path fill="currentColor" d="M12 17a2 2 0 0 0 2-2c0-1.11-.89-2-2-2a2 2 0 0 0-2 2a2 2 0 0 0 2 2m6-9a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V10a2 2 0 0 1 2-2h1V6a5 5 0 0 1 5-5a5 5 0 0 1 5 5v2h1m-6-5a3 3 0 0 0-3 3v2h6V6a3 3 0 0 0-3-3Z"/></svg>
                </n-icon>
                <h3 text-18 font-medium color="#333" mb-10>{{ $t('views.login.title_reset_password') }}</h3>
                <p text-14 color="#999" mb-20>{{ $t('views.login.desc_reset_password') }}</p>
              </div>
            </div>
            
            <div mt-10>
              <n-input
                v-model:value="forgotForm.verifyCode"
                autofocus
                class="h-50 items-center pl-10 text-16"
                :placeholder="$t('views.login.placeholder_verification_code')"
                :maxlength="10"
              >
                <template #prefix>
                  <n-icon color="#999">
                    <svg viewBox="0 0 24 24"><path fill="currentColor" d="M9 22C8.4 22 8 21.6 8 21V18H4C2.9 18 2 17.1 2 16V4C2 2.9 2.9 2 4 2H20C21.1 2 22 2.9 22 4V16C22 17.1 21.1 18 20 18H13.9L10.2 21.7C9.9 22 9.6 22 9.3 21.9C9.1 21.8 9 21.4 9 21.1V22M4 16H20V4H4V16Z"/></svg>
                  </n-icon>
                </template>
              </n-input>
            </div>
            
            <div mt-20>
              <n-input
                v-model:value="forgotForm.newPassword"
                class="h-50 items-center pl-10 text-16"
                type="password"
                show-password-on="mousedown"
                :placeholder="$t('views.login.placeholder_new_password')"
                :maxlength="20"
              >
                <template #prefix>
                  <n-icon color="#999">
                    <svg viewBox="0 0 24 24"><path fill="currentColor" d="M12 17a2 2 0 0 0 2-2c0-1.11-.89-2-2-2a2 2 0 0 0-2 2a2 2 0 0 0 2 2m6-9a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V10a2 2 0 0 1 2-2h1V6a5 5 0 0 1 5-5a5 5 0 0 1 5 5v2h1m-6-5a3 3 0 0 0-3 3v2h6V6a3 3 0 0 0-3-3Z"/></svg>
                  </n-icon>
                </template>
              </n-input>
            </div>
            
            <div mt-20>
              <n-input
                v-model:value="forgotForm.confirmPassword"
                class="h-50 items-center pl-10 text-16"
                type="password"
                show-password-on="mousedown"
                :placeholder="$t('views.login.placeholder_confirm_password')"
                :maxlength="20"
                @keypress.enter="handleResetPassword"
              >
                <template #prefix>
                  <n-icon color="#999">
                    <svg viewBox="0 0 24 24"><path fill="currentColor" d="M12 17a2 2 0 0 0 2-2c0-1.11-.89-2-2-2a2 2 0 0 0-2 2a2 2 0 0 0 2 2m6-9a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V10a2 2 0 0 1 2-2h1V6a5 5 0 0 1 5-5a5 5 0 0 1 5 5v2h1m-6-5a3 3 0 0 0-3 3v2h6V6a3 3 0 0 0-3-3Z"/></svg>
                  </n-icon>
                </template>
              </n-input>
            </div>

            <div mt-25 flex flex-col gap-10>
              <n-button h-50 type="primary" :loading="resetLoading" @click="handleResetPassword">
                <template #icon>
                  <n-icon><svg viewBox="0 0 24 24"><path fill="currentColor" d="M9 12l2 2l4-4m6 2a9 9 0 1 1-18 0a9 9 0 0 1 18 0Z"/></svg></n-icon>
                </template>
                {{ $t('views.login.text_reset_password') }}
              </n-button>
              <n-button h-45 tertiary @click="currentForm = 'forgot'">
                <template #icon>
                  <n-icon><svg viewBox="0 0 24 24"><path fill="currentColor" d="M20 11H7.83l5.59-5.59L12 4l-8 8l8 8l1.41-1.41L7.83 13H20v-2z"/></svg></n-icon>
                </template>
                {{ $t('common.back') }}
              </n-button>
            </div>
            
            <!-- 错误提示 -->
            <div v-if="errorMsg" mt-15 class="error-message">
              <n-alert type="error" :show-icon="false">
                {{ errorMsg }}
              </n-alert>
            </div>
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

import { onUnmounted } from 'vue'

const router = useRouter()
const { query } = useRoute()
const { t } = useI18n({ useScope: 'global' })

// 当前显示的表单类型：login, forgot, reset
const currentForm = ref('login')

const loginInfo = ref({
  email: '',
  password: '',
})

// 忘记密码表单数据
const forgotForm = ref({
  email: '',
  verifyCode: '',
  newPassword: '',
  confirmPassword: ''
})

const loginPollingTimer = ref(null)
const loginCode = ref('')

initLoginInfo()

function initLoginInfo() {
  const localLoginInfo = lStorage.get('loginInfo')
  if (localLoginInfo) {
    loginInfo.value.email = localLoginInfo.email || ''
    loginInfo.value.password = localLoginInfo.password || ''
  }
}

onUnmounted(() => {
  stopPollingLoginStatus()
})

const loading = ref(false)
const sendCodeLoading = ref(false)
const resetLoading = ref(false)
const errorMsg = ref('') // 错误信息

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

/** 邮箱格式验证 */
function validateEmail(email) {
  if (!email) return t('views.login.message_input_email')
  const emailReg = /^[\w-.]+@([\w-]+\.)+[\w-]{2,}$/
  if (!emailReg.test(email)) return t('views.login.message_email_format')
  return ''
}

/** 验证码和密码验证 */
function validateResetForm() {
  const { verifyCode, newPassword, confirmPassword } = forgotForm.value
  if (!verifyCode) return t('views.login.message_input_verification_code')
  if (!newPassword) return t('views.login.message_input_new_password')
  if (newPassword.length < 6) return t('views.login.message_password_length')
  if (!confirmPassword) return t('views.login.message_input_confirm_password')
  if (newPassword !== confirmPassword) return t('views.login.message_passwords_not_match')
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
    console.log(res)
    $message.success(t('views.login.message_login_success'))
    setToken(res.data.token)
    await addDynamicRoutes()
    if (query.redirect) {
      const path = query.redirect
      console.log('path', { path, query })
      Reflect.deleteProperty(query, 'redirect')
      router.push({ path, query })
    } else {
      router.push('/')
    }
  } catch (e) {
    const msg = e?.error?.message || t('views.login.message_login_failed')
    console.error(msg)
    errorMsg.value = e?.message || t('views.login.message_login_failed')
  }
  loading.value = false
}

/** 发送验证码 */
async function handleSendCode() {
  const { email } = forgotForm.value
  errorMsg.value = validateEmail(email)
  if (errorMsg.value) return

  try {
    sendCodeLoading.value = true
    errorMsg.value = ''
    $message.loading(t('views.login.message_verifying'))
    
    await api.sendEmail({
      email,
      type: 'forgetPwd'
    })
    
    $message.success(t('views.login.message_send_code_success'))
    currentForm.value = 'reset'
  } catch (e) {
    console.error('Send code error:', e)
    errorMsg.value = e?.message || t('views.login.message_send_code_failed')
  }
  sendCodeLoading.value = false
}

/** 重置密码 */
async function handleResetPassword() {
  const { email } = forgotForm.value
  errorMsg.value = validateResetForm()
  if (errorMsg.value) return

  try {
    resetLoading.value = true
    errorMsg.value = ''
    $message.loading(t('views.login.message_verifying'))
    
    await api.resetPassword({
      email,
      verifyCode: forgotForm.value.verifyCode,
      newPassword: forgotForm.value.newPassword
    })
    
    $message.success(t('views.login.message_reset_success'))
    
    // 重置表单
    forgotForm.value = {
      email: '',
      verifyCode: '',
      newPassword: '',
      confirmPassword: ''
    }
    
    // 返回登录页面
    currentForm.value = 'login'
  } catch (e) {
    console.error('Reset password error:', e)
    errorMsg.value = e?.message || t('views.login.message_reset_failed')
  }
  resetLoading.value = false
}

/** 点击注册跳转 */
function goRegister() {
  router.push({ name: 'Register' })
}

function stopPollingLoginStatus() {
  if (loginPollingTimer.value) {
    clearInterval(loginPollingTimer.value)
    loginPollingTimer.value = null
  }
}

// 监听表单切换，清除错误信息
watch(currentForm, () => {
  errorMsg.value = ''
})
</script>

<style scoped>
/* 表单容器过渡动画 */
.form-container {
  transition: all 0.3s ease-in-out;
}

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

/* 步骤指示器样式 */
.step-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  opacity: 0.5;
  transition: opacity 0.3s ease;
}

.step-indicator.active {
  opacity: 1;
}

.step-circle {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #f0f0f0;
  color: #999;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.step-indicator.active .step-circle {
  background: var(--primary-color);
  color: white;
}

.step-text {
  font-size: 12px;
  color: #999;
  white-space: nowrap;
}

.step-indicator.active .step-text {
  color: var(--primary-color);
  font-weight: 500;
}

.step-line {
  width: 40px;
  height: 2px;
  background: #f0f0f0;
  transition: background 0.3s ease;
}

.step-line.active {
  background: var(--primary-color);
}

/* 忘记密码标题样式 */
.forgot-title, .reset-title {
  display: flex;
  flex-direction: column;
  align-items: center;
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

/* 注册按钮样式 */
.register-btn {
  color: var(--primary-color) !important;
  border-color: var(--primary-color) !important;
  background-color: transparent !important;
  
  &:hover {
    color: var(--primary-color-hover) !important;
    border-color: var(--primary-color-hover) !important;
    background-color: var(--primary-color-suppl) !important;
  }
  
  &:active {
    color: var(--primary-color-pressed) !important;
    border-color: var(--primary-color-pressed) !important;
  }
}

/* 忘记密码按钮样式 */
.forgot-password-btn {
  color: var(--primary-color) !important;
  background-color: transparent !important;
  border: none !important;
  font-size: 14px !important;
  
  &:hover {
    color: var(--primary-color-hover) !important;
    background-color: var(--primary-color-suppl) !important;
  }
  
  &:active {
    color: var(--primary-color-pressed) !important;
  }
}

/* 响应式调整 */
@media (max-width: 480px) {
  .step-indicator {
    gap: 4px;
  }
  
  .step-text {
    font-size: 10px;
  }
  
  .step-line {
    width: 30px;
  }
}
</style>
