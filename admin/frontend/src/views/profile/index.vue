<script setup>
import { ref } from 'vue'
import { NButton, NCard, NForm, NFormItem, NInput, NIcon, NAlert } from 'naive-ui'
import { useI18n } from 'vue-i18n'
import CommonPage from '@/components/page/CommonPage.vue'
import { useUserStore } from '@/store'
import api from '@/api'
import { useMessage } from 'naive-ui'

const { t } = useI18n()
const userStore = useUserStore()
const message = useMessage()
const isLoading = ref(false)

// 用户信息的表单
const infoFormRef = ref(null)
const infoForm = ref({
  username: userStore.name,
  email: userStore.email,
})

async function updateProfile() {
  isLoading.value = true
  infoFormRef.value?.validate(async (err) => {
    if (err) {
      isLoading.value = false
      return
    }
    await api
      .updateUserInfo({ 
        username: infoForm.value.username,
        email: infoForm.value.email 
      })
      .then(() => {
        userStore.setUserInfo(infoForm.value)
        isLoading.value = false
        message.success(t('common.text.update_success'))
      })
      .catch(() => {
        isLoading.value = false
      })
  })
}

// 修改邮箱（使用同一个接口）
async function updateEmail() {
  await updateProfile()
}

const infoFormRules = {
  username: [
    {
      required: true,
      message: t('views.profile.message_username_required'),
      trigger: ['input', 'blur', 'change'],
    },
  ],
  email: [
    {
      required: true,
      message: t('views.profile.message_email_required'),
      trigger: ['input', 'blur', 'change'],
    },
    {
      type: 'email',
      message: t('views.profile.message_email_invalid'),
      trigger: ['input', 'blur'],
    },
  ],
}

// 修改密码的表单
const passwordFormRef = ref(null)
const passwordForm = ref({
  old_password: '',
  new_password: '',
  confirm_password: '',
})

async function updatePassword() {
  isLoading.value = true
  passwordFormRef.value?.validate(async (err) => {
    if (!err) {
      const data = { 
        oldPassword: passwordForm.value.old_password,
        newPassword: passwordForm.value.new_password
      }
      await api
        .updatePassword(data)
        .then((res) => {
          message.success(res.msg || t('views.profile.message_password_update_success'))
          passwordForm.value = {
            old_password: '',
            new_password: '',
            confirm_password: '',
          }
          if (userStore.forcePasswordChange) {
            userStore.setForcePasswordChange(false)
          }
          isLoading.value = false
        })
        .catch(() => {
          isLoading.value = false
        })
    } else {
      isLoading.value = false
    }
  })
}

const passwordFormRules = {
  old_password: [
    {
      required: true,
      message: t('views.profile.message_old_password_required'),
      trigger: ['input', 'blur', 'change'],
    },
  ],
  new_password: [
    {
      required: true,
      message: t('views.profile.message_new_password_required'),
      trigger: ['input', 'blur', 'change'],
    },
    {
      min: 8,
      message: t('views.profile.message_password_min_length'),
      trigger: ['input', 'blur'],
    },
  ],
  confirm_password: [
    {
      required: true,
      message: t('views.profile.message_password_confirmation_required'),
      trigger: ['input', 'blur'],
    },
    {
      validator: validatePasswordStartWith,
      message: t('views.profile.message_password_confirmation_diff'),
      trigger: 'input',
    },
    {
      validator: validatePasswordSame,
      message: t('views.profile.message_password_confirmation_diff'),
      trigger: ['blur', 'password-input'],
    },
  ],
}

function validatePasswordStartWith(rule, value) {
  return (
    !!passwordForm.value.new_password &&
    passwordForm.value.new_password.startsWith(value) &&
    passwordForm.value.new_password.length >= value.length
  )
}

function validatePasswordSame(rule, value) {
  return value === passwordForm.value.new_password
}
</script>

<template>
  <CommonPage :show-header="false">
    <div class="profile-container">
      <n-alert 
        v-if="userStore.forcePasswordChange" 
        type="error" 
        :title="$t('views.profile.alert_must_change_password_title')"
        style="margin-bottom: 20px;"
      >
        <template #icon>
          <n-icon size="20">
            <svg viewBox="0 0 24 24">
              <path fill="currentColor" d="M12 2L1 21h22M12 6l7.53 13H4.47M11 10v4h2v-4m-2 6v2h2v-2"/>
            </svg>
          </n-icon>
        </template>
        {{ $t('views.profile.alert_must_change_password_message') }}
      </n-alert>

      <div class="info-password-row">
        <NCard class="profile-card info-card" :title="$t('views.profile.title_basic_info')">
          <template #header-extra>
            <NIcon size="20" color="#18a058">
              <svg viewBox="0 0 24 24">
                <path fill="currentColor" d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
              </svg>
            </NIcon>
          </template>
          <NForm
            ref="infoFormRef"
            label-placement="left"
            label-align="left"
            label-width="90"
            :model="infoForm"
            :rules="infoFormRules"
            class="info-form"
          >
            <NFormItem :label="$t('views.profile.label_username')" path="username">
              <div class="username-input-group">
                <NInput
                  v-model:value="infoForm.username"
                  type="text"
                  :placeholder="$t('views.profile.placeholder_username')"
                  :maxlength="32"
                  show-count
                  class="username-input"
                />
                <NButton 
                  type="primary" 
                  :loading="isLoading" 
                  @click="updateProfile"
                  class="inline-update-btn"
                >
                  {{ $t('common.buttons.update') }}
                </NButton>
              </div>
            </NFormItem>
            <NFormItem :label="$t('views.profile.label_email')" path="email">
              <div class="username-input-group">
                <NInput
                  v-model:value="infoForm.email"
                  type="text"
                  :placeholder="$t('views.profile.placeholder_email')"
                  class="username-input"
                />
                <NButton 
                  type="primary" 
                  :loading="isLoading" 
                  @click="updateEmail"
                  class="inline-update-btn"
                >
                  {{ $t('common.buttons.update') }}
                </NButton>
              </div>
            </NFormItem>
          </NForm>
        </NCard>

        <NCard class="profile-card password-card" :title="$t('views.profile.title_change_password')">
          <template #header-extra>
            <NIcon size="20" color="#f0a020">
              <svg viewBox="0 0 24 24">
                <path fill="currentColor" d="M12 17a2 2 0 0 0 2-2c0-1.11-.89-2-2-2a2 2 0 0 0-2 2a2 2 0 0 0 2 2m6-9a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V10a2 2 0 0 1 2-2h1V6a5 5 0 0 1 5-5a5 5 0 0 1 5 5v2h1m-6-5a3 3 0 0 0-3 3v2h6V6a3 3 0 0 0-3-3Z"/>
              </svg>
            </NIcon>
          </template>
          <NForm
            ref="passwordFormRef"
            label-placement="left"
            label-align="left"
            :model="passwordForm"
            label-width="100"
            :rules="passwordFormRules"
            class="password-form"
          >
            <NFormItem :label="$t('views.profile.label_old_password')" path="old_password">
              <NInput
                v-model:value="passwordForm.old_password"
                type="password"
                show-password-on="mousedown"
                :placeholder="$t('views.profile.placeholder_old_password')"
              />
            </NFormItem>
            <NFormItem :label="$t('views.profile.label_new_password')" path="new_password">
              <NInput
                v-model:value="passwordForm.new_password"
                :disabled="!passwordForm.old_password"
                type="password"
                show-password-on="mousedown"
                :placeholder="$t('views.profile.placeholder_new_password')"
              />
            </NFormItem>
            <NFormItem :label="$t('views.profile.label_confirm_password')" path="confirm_password">
              <NInput
                v-model:value="passwordForm.confirm_password"
                :disabled="!passwordForm.new_password"
                type="password"
                show-password-on="mousedown"
                :placeholder="$t('views.profile.placeholder_confirm_password')"
              />
            </NFormItem>
            <div class="password-form-actions">
              <NButton type="primary" :loading="isLoading" @click="updatePassword">
                {{ $t('common.buttons.update') }}
              </NButton>
            </div>
          </NForm>
        </NCard>
      </div>
    </div>
  </CommonPage>
</template>

<style scoped>
.profile-container {
  width: 100%;
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  position: relative;
}

.profile-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 150px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 0 0 16px 16px;
  opacity: 0.03;
  z-index: 0;
}

.profile-container > * {
  position: relative;
  z-index: 1;
}

.profile-card {
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border: 1px solid #e8e8e8;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  position: relative;
  width: 100%;
}

.profile-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #18a058 0%, #2080f0 50%, #f0a020 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.profile-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

.profile-card:hover::before {
  opacity: 1;
}

.profile-card :deep(.n-card-header) {
  padding: 16px 24px;
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
  border-bottom: 1px solid #f0f0f0;
}

.profile-card :deep(.n-card-header__main) {
  font-size: 16px;
  font-weight: 700;
  color: #333;
}

.profile-card :deep(.n-card__content) {
  padding: 20px 24px;
}

.info-form,
.password-form {
  max-width: 600px;
}

.info-password-row {
  display: flex;
  gap: 20px;
  width: 100%;
  max-width: 1100px;
}

.info-card,
.password-card {
  flex: 1;
  min-width: 280px;
}

.username-input-group {
  display: flex;
  gap: 12px;
  align-items: center;
}

.username-input {
  flex: 1;
}

.inline-update-btn {
  height: 36px;
  padding: 0 16px;
  border-radius: 6px;
  font-weight: 500;
  font-size: 14px;
  flex-shrink: 0;
}

.password-form-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

@media (max-width: 1024px) {
  .info-password-row {
    flex-direction: column;
  }
}

@media (max-width: 768px) {
  .username-input-group {
    flex-direction: column;
    align-items: stretch;
  }
  
  .inline-update-btn {
    margin-left: 0;
  }
}
</style>
