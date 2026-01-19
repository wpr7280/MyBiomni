<!-- src/views/login/register.vue -->
<template>
  <AppPage :show-footer="true" bg-cover :style="{ backgroundImage: `url(${bgImg})` }">
    <div
        style="transform: translateY(25px)"
        class="m-auto max-w-1500 min-w-345 f-c-c rounded-10 bg-white bg-opacity-60 p-15 card-shadow"
        dark:bg-dark
    >
      <!-- 左侧插画（可选） -->
      <div hidden w-380 px-20 py-35 md:block>
        <icon-custom-front-page pt-10 text-300 color-primary/>
      </div>

      <!-- 注册表单 -->
      <n-card
          w-420
          :bordered="false"
          class="rounded-10 px-20 py-30 backdrop-blur-md bg-white/70 dark:bg-dark/70"
      >
        <h4 f-c-c text-24 mb-20>
          <icon-custom-logo mr-10 text-50 color-primary/>
          {{ $t('views.register.title') }}
        </h4>

        <n-form
            :model="form"
            :rules="rules"
            ref="formRef"
            label-placement="top"
            size="large"
        >
          <!-- 用户邮箱 -->
          <n-form-item path="email" :label="$t('views.register.email')">
            <n-input v-model:value="form.email" placeholder="name@domain.com">
              <template #suffix>
                <n-button
                    type="primary"
                    :disabled="isSendingCode || countdown > 0"
                    @click="sendVerificationCode"
                    text
                    class="send-code-btn"
                >
                  <span v-if="countdown > 0">{{ countdown }}s</span>
                  <span v-else>{{ $t('views.register.send_code') }}</span>
                </n-button>
              </template>
            </n-input>
          </n-form-item>

          <n-form-item path="verifyCode" :label="$t('views.register.verification_code')">
            <n-input v-model:value="form.verifyCode" :placeholder="$t('views.register.code_placeholder')"/>
          </n-form-item>
          <!-- 用户名 -->
          <n-form-item path="username" :label="$t('views.register.username')">
            <n-input v-model:value="form.username" placeholder="your nickname"/>
          </n-form-item>

          <!-- 密码 -->
          <n-form-item path="password" :label="$t('views.register.password')">
            <n-input
                v-model:value="form.password"
                type="password"
                show-password-on="mousedown"
                placeholder="******"
            />
          </n-form-item>

          <!-- 确认密码 -->
          <n-form-item path="confirm" :label="$t('views.register.confirm')">
            <n-input
                v-model:value="form.confirm"
                type="password"
                show-password-on="mousedown"
                placeholder="******"
            />
          </n-form-item>

          <n-button
              type="primary"
              block
              :loading="loading"
              @click="handleSubmit"
          >
            {{ $t('views.register.submit') }}
          </n-button>

          <!-- 返回登录 -->
          <div mt-10 text-center>
            <RouterLink to="/login">{{ $t('views.register.back_login') }}</RouterLink>
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
        </n-form>
      </n-card>
    </div>
  </AppPage>
</template>

<script setup lang="ts">
import {ref} from 'vue'
import {useRouter} from 'vue-router'
import {useMessage} from 'naive-ui'
import {useI18n} from 'vue-i18n'
import bgImg from '@/assets/images/login_bg.webp'
import api from '@/api'

interface RegisterForm {
  email: string
  verifyCode: string
  username: string
  password: string
  confirm: string
}

const {t} = useI18n({useScope: 'global'})
const router = useRouter()
const message = useMessage()
const isSendingCode = ref(false)
const countdown = ref(0)
let countdownTimer: NodeJS.Timeout | null = null

const formRef = ref()
const form = ref<RegisterForm>({
  email: '',
  verifyCode: '',
  username: '',
  password: '',
  confirm: '',
})

/** 表单校验规则 */
const rules = {
  email: [
    {required: true, message: t('views.register.rule_email'), trigger: 'blur'},
    {
      type: 'email',
      message: t('views.register.rule_email_format'),
      trigger: ['blur', 'input'],
    },
  ],
  code: {required: true, message: t('views.register.rule_code'), trigger: 'blur'}, // New rule for verification code
  username: {required: true, message: t('views.register.rule_username'), trigger: 'blur'},
  password: {required: true, message: t('views.register.rule_password'), trigger: 'blur'},
  confirm: {
    required: true,
    message: t('views.register.rule_confirm'),
    trigger: 'blur',
    validator: (_rule: any, value: string) =>
        value === form.value.password || new Error(t('views.register.rule_confirm_match')),
  },
}

/** Send Verification Code */
async function sendVerificationCode() {
  // Validate email before sending code
  const emailRule = rules.email as any[]
  const emailError = emailRule
      .map(rule => rule.validator ? rule.validator(null, form.value.email) : undefined)
      .find(error => error instanceof Error)

  if (emailError) {
    message.error(emailError.message)
    return
  }

  isSendingCode.value = true
  try {
    // You'll need an API endpoint for sending the verification code
    const res = await api.sendVerificationCode({email: form.value.email}) // Assume `type` is to differentiate code usage
    if (res.code === 200) {
      message.success(t('views.register.send_code_success'))
      startCountdown()
    } else {
      message.error(res.msg || t('views.register.send_code_failed'))
    }
  } catch (e) {
    console.error(e)
    message.error(t('views.register.send_code_failed'))
  } finally {
    isSendingCode.value = false
  }
}

/** Start Countdown */
function startCountdown() {
  countdown.value = 60 // 60 seconds countdown
  if (countdownTimer) clearInterval(countdownTimer)
  countdownTimer = setInterval(() => {
    if (countdown.value > 0) {
      countdown.value--
    } else {
      clearInterval(countdownTimer!)
      countdownTimer = null
    }
  }, 1000)
}

const loading = ref(false)

/** 提交注册 */
function handleSubmit() {
  formRef.value?.validate(async (errors: any) => {
    if (errors) return
    try {
      loading.value = true
      const payload = {
        username: form.value.username,
        email: form.value.email,
        verifyCode: form.value.verifyCode,
        password: form.value.password,
      }

      const res = await api.register(payload)
      console.log("-----")
      console.log(res)
      if (res.code === 200) {
        message.success(t('views.register.success'))
        // 示例：保存 token
        // localStorage.setItem('token', res.data.token)
        router.replace('/login')
      } else {
        message.error(res.msg || t('views.register.failed'))
      }
    } catch (e) {
      console.error(e)
      message.error(t('views.register.failed'))
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
/* 发送验证码按钮样式 */
.send-code-btn {
  color: var(--primary-color) !important;
  background-color: transparent !important;
  border: none !important;
  font-size: 14px !important;
  padding: 4px 8px !important;
  
  &:hover {
    color: var(--primary-color-hover) !important;
    background-color: var(--primary-color-suppl) !important;
  }
  
  &:active {
    color: var(--primary-color-pressed) !important;
  }
  
  &:disabled {
    color: var(--text-color-tertiary) !important;
    background-color: transparent !important;
  }
}

/* 隐私链接样式 */
.privacy-link {
  color: #999;
  text-decoration: none;
  transition: color 0.3s ease;
}

.privacy-link:hover {
  color: #18a058;
  text-decoration: underline;
}

.separator {
  color: #ddd;
  margin: 0 8px;
}
</style>
