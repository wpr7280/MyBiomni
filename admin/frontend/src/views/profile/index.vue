<script setup>
import { ref, onMounted, h } from 'vue'
import { NButton, NCard, NForm, NFormItem, NInput, NDataTable, NPopconfirm, NIcon, NSpace, NTag, NModal, NText, NAlert } from 'naive-ui'
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
      .updateUserInfo({ username: infoForm.value.username })
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
const infoFormRules = {
  username: [
    {
      required: true,
      message: t('views.profile.message_username_required'),
      trigger: ['input', 'blur', 'change'],
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
          message.success(res.msg)
          passwordForm.value = {
            old_password: '',
            new_password: '',
            confirm_password: '',
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

// Access Token 管理
const accessTokens = ref([])
const tokenLoading = ref(false)
const generateTokenLoading = ref(false)
const showTokenModal = ref(false)
const newGeneratedToken = ref('')

// 加载Access Token列表
async function loadAccessTokens() {
  tokenLoading.value = true
  try {
    const res = await api.listAccessToken()
    if (res.code === 200) {
      accessTokens.value = res.data || []
    }
  } catch (error) {
    message.error(t('views.profile.message_get_tokens_failed'))
  } finally {
    tokenLoading.value = false
  }
}

// 生成新的Access Token
async function generateAccessToken() {
  generateTokenLoading.value = true
  try {
    const res = await api.createAccessToken()
    if (res.code === 200) {
      // 保存新生成的token（未mask的完整token）
      newGeneratedToken.value = res.data.accessTokenWithMask
      // 显示模态框让用户复制
      showTokenModal.value = true
      // 重新加载token列表
      await loadAccessTokens()
    } else {
      message.error(res.msg || t('views.profile.message_generate_token_failed'))
    }
  } catch (error) {
    message.error(t('views.profile.message_generate_token_failed'))
  } finally {
    generateTokenLoading.value = false
  }
}

// 删除Access Token
async function deleteAccessToken(tokenData) {
  try {
    // 从masked token中提取后10位
    const maskedToken = tokenData.accessTokenWithMask
    const last10Chars = maskedToken.slice(-10)
    
    const deleteRequest = {
      accessToken: last10Chars,
      createdAt: tokenData.createdAt
    }
    
    const res = await api.deleteAccessToken(deleteRequest)
    if (res.code === 200) {
      message.success(t('views.profile.message_delete_token_success'))
      await loadAccessTokens()
    } else {
      message.error(res.msg || t('views.profile.message_delete_token_failed'))
    }
  } catch (error) {
    message.error(t('views.profile.message_delete_token_failed'))
  }
}

// 复制token
async function copyToken() {
  try {
    await navigator.clipboard.writeText(newGeneratedToken.value)
    message.success(t('views.profile.message_token_copied'))
  } catch (error) {
    message.error(t('views.profile.message_token_copy_failed'))
  }
}

// 关闭token模态框
function closeTokenModal() {
  showTokenModal.value = false
  newGeneratedToken.value = ''
}

// 表格列定义
const columns = [
  {
    title: () => t('views.profile.label_access_token'),
    key: 'accessTokenWithMask',
    render: (row) => row.accessTokenWithMask || '-'
  },
  {
    title: () => t('views.profile.label_created_at'),
    key: 'createdAt',
    render: (row) => row.createdAt ? new Date(row.createdAt).toLocaleString() : '-'
  },
  {
    title: () => t('views.profile.label_actions'),
    key: 'actions',
    render: (row) => {
      return h(NPopconfirm, {
        onPositiveClick: () => deleteAccessToken(row)
      }, {
        default: () => t('views.profile.message_delete_token_confirm'),
        trigger: () => h(NButton, {
          size: 'small',
          type: 'error',
          ghost: true
        }, {
          default: () => t('views.profile.button_delete')
        })
      })
    }
  }
]

onMounted(() => {
  loadAccessTokens()
})
</script>

<template>
  <CommonPage :show-header="false">
        <div class="profile-container">
      <!-- 基本信息和修改密码在一行 -->
      <div class="info-password-row">
        <!-- 修改信息卡片 -->
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
              <NInput
                v-model:value="infoForm.email"
                type="text"
                :placeholder="$t('views.profile.placeholder_email')"
                disabled
              />
            </NFormItem>
          </NForm>
        </NCard>

        <!-- 修改密码卡片 -->
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

      <!-- Access Token管理卡片 -->
      <NCard class="profile-card" :title="$t('views.profile.title_access_token')">
        <template #header-extra>
          <NIcon size="20" color="#2080f0">
            <svg viewBox="0 0 24 24">
              <path fill="currentColor" d="M7 14c-1.66 0-3 1.34-3 3s1.34 3 3 3s3-1.34 3-3s-1.34-3-3-3zM20.99 4c0-1.1-.89-2-2-2H5c-1.1 0-2 .9-2 2v6c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2l-.01-6zM9 10.5c0 .83-.67 1.5-1.5 1.5S6 11.33 6 10.5S6.67 9 7.5 9S9 9.67 9 10.5zM15.5 9c.83 0 1.5.67 1.5 1.5s-.67 1.5-1.5 1.5S14 11.33 14 10.5S14.67 9 15.5 9z"/>
            </svg>
          </NIcon>
        </template>
        <div class="token-section">
          <div class="token-header">
            <p class="token-description">
              {{ $t('views.profile.text_manage_access_token') }}
            </p>
            <NButton 
              type="primary" 
              :loading="generateTokenLoading" 
              @click="generateAccessToken"
              class="generate-btn"
            >
              <template #icon>
                <NIcon>
                  <svg viewBox="0 0 24 24">
                    <path fill="currentColor" d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
                  </svg>
                </NIcon>
              </template>
              {{ $t('views.profile.button_generate_token') }}
            </NButton>
          </div>
          
          <div class="token-table">
            <NDataTable
              :columns="columns"
              :data="accessTokens"
              :loading="tokenLoading"
              :bordered="false"
              :single-line="false"
              flex-height
              style="min-height: 200px"
            />
          </div>
        </div>
      </NCard>
    </div>

    <!-- 新生成Token模态框 -->
    <NModal 
      v-model:show="showTokenModal" 
      preset="card" 
      :title="$t('views.profile.modal_title_new_token')"
      style="max-width: 600px"
      :mask-closable="false"
      :close-on-esc="false"
    >
      <div class="token-modal-content">
        <NAlert 
          type="warning" 
          :title="$t('views.profile.text_token_important_notice')"
          style="margin-bottom: 16px"
        >
          {{ $t('views.profile.text_copy_token_notice') }}
        </NAlert>
        
        <div class="token-display">
          <NText code style="word-break: break-all; font-size: 14px; line-height: 1.6;">
            {{ newGeneratedToken }}
          </NText>
        </div>
        
        <div class="token-notice">
          <NText depth="3" style="font-size: 13px;">
            {{ $t('views.profile.text_token_security_notice') }}
          </NText>
        </div>
        
        <div class="token-modal-actions">
          <NButton type="primary" @click="copyToken" style="margin-right: 12px;">
            <template #icon>
              <NIcon>
                <svg viewBox="0 0 24 24">
                  <path fill="currentColor" d="M19 21H8V7h11m0-2H8a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2m-3-4H4a2 2 0 0 0-2 2v14h2V3h12V1Z"/>
                </svg>
              </NIcon>
            </template>
            {{ $t('views.profile.button_copy_token') }}
          </NButton>
          <NButton @click="closeTokenModal">
            {{ $t('views.profile.button_i_have_copied') }}
          </NButton>
        </div>
      </div>
    </NModal>
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

.profile-card:not(.info-card):not(.password-card) {
  max-width: 1100px;
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
  display: flex;
  align-items: center;
  gap: 8px;
}

.profile-card :deep(.n-card-header__extra) {
  display: flex;
  align-items: center;
}

.profile-card :deep(.n-card__content) {
  padding: 20px 24px;
}

.info-form,
.password-form {
  max-width: 600px;
}

.info-form :deep(.n-form-item),
.password-form :deep(.n-form-item) {
  margin-bottom: 16px;
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
  margin-left: 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.inline-update-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.info-form :deep(.n-form-item-label),
.password-form :deep(.n-form-item-label) {
  font-weight: 500;
  color: #333;
  font-size: 13px;
  white-space: normal;
  word-break: break-word;
  line-height: 1.4;
}

.info-form :deep(.n-input),
.password-form :deep(.n-input) {
  height: 36px;
  border-radius: 6px;
  border: 1px solid #e0e0e0;
  transition: all 0.3s ease;
  font-size: 14px;
}

.info-form :deep(.n-input:hover),
.password-form :deep(.n-input:hover) {
  border-color: #18a058;
}

.info-form :deep(.n-input.n-input--focus),
.password-form :deep(.n-input.n-input--focus) {
  border-color: #18a058;
  box-shadow: 0 0 0 2px rgba(24, 160, 88, 0.1);
}

.info-form :deep(.n-input.n-input--disabled),
.password-form :deep(.n-input.n-input--disabled) {
  background: #f5f5f5;
  border-color: #e0e0e0;
  color: #999;
}

.password-form-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.password-form-actions :deep(.n-button) {
  padding: 0 24px;
  height: 36px;
  border-radius: 6px;
  font-weight: 500;
  font-size: 14px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.password-form-actions :deep(.n-button:hover) {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.token-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.token-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
  padding: 16px 20px;
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
  border-radius: 8px;
  border: 1px solid #f0f0f0;
}

.token-description {
  color: #666;
  line-height: 1.5;
  margin: 0;
  flex: 1;
  min-width: 200px;
  font-size: 14px;
}

.generate-btn {
  flex-shrink: 0;
  height: 36px;
  padding: 0 16px;
  border-radius: 6px;
  font-weight: 500;
  font-size: 14px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.generate-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.token-table {
  min-height: 150px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e0e0e6;
}

.token-table :deep(.n-data-table) {
  border: none;
}

.token-table :deep(.n-data-table-wrapper) {
  border: none;
}

.token-table :deep(.n-data-table-base-table) {
  border: none;
}

.token-table :deep(.n-data-table-thead) {
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
}

.token-table :deep(.n-data-table-th) {
  background: transparent;
  font-weight: 600;
  color: #333;
  padding: 12px 16px;
  font-size: 14px;
  border-bottom: 1px solid #e0e0e6;
  border-right: none;
}

.token-table :deep(.n-data-table-th:not(:last-child)) {
  border-right: 1px solid #f0f0f0;
}

.token-table :deep(.n-data-table-td) {
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
  border-right: none;
  font-size: 14px;
}

.token-table :deep(.n-data-table-td:not(:last-child)) {
  border-right: 1px solid #f5f5f5;
}

.token-table :deep(.n-data-table-tr:hover .n-data-table-td) {
  background: #f8f9fa;
}

.token-table :deep(.n-data-table-tr:last-child .n-data-table-td) {
  border-bottom: none;
}

.token-table :deep(.n-data-table-empty) {
  padding: 24px;
  color: #999;
  text-align: center;
}

.token-table :deep(.n-button) {
  border-radius: 6px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.token-table :deep(.n-button:hover) {
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .info-password-row {
    flex-direction: column;
    gap: 16px;
  }
  
  .info-card,
  .password-card {
    max-width: none;
    min-width: 0;
  }
}

@media (max-width: 768px) {
  .profile-container {
    padding: 12px 16px;
    gap: 16px;
  }
  
  .profile-card :deep(.n-card-header) {
    padding: 12px 16px;
  }
  
  .profile-card :deep(.n-card__content) {
    padding: 16px;
  }
  
  .token-header {
    flex-direction: column;
    align-items: stretch;
    padding: 12px;
    gap: 12px;
  }
  
  .generate-btn {
    align-self: stretch;
  }
  
  .info-form,
  .password-form {
    max-width: 100%;
  }
  
  .info-form :deep(.n-form-item) {
    margin-bottom: 12px;
  }
  
  .password-form :deep(.n-form-item) {
    margin-bottom: 12px;
  }
  
  .info-form :deep(.n-form-item-label),
  .password-form :deep(.n-form-item-label) {
    font-size: 12px;
    width: 85px !important;
  }
  
  .username-input-group {
    flex-direction: column;
    gap: 8px;
    align-items: stretch;
  }
  
  .inline-update-btn {
    align-self: stretch;
    margin-left: 0;
  }
  
  .password-form-actions {
    margin-top: 12px;
    padding-top: 12px;
  }
  
  .info-form :deep(.n-form-item-label),
  .password-form :deep(.n-form-item-label) {
    font-size: 11px;
    width: 65px !important;
  }
  
  .info-form :deep(.n-form-item) {
    margin-bottom: 10px;
  }
  
  .password-form :deep(.n-form-item) {
    margin-bottom: 10px;
  }
  
  .token-section {
    gap: 12px;
  }
  
  .token-table :deep(.n-data-table-th),
  .token-table :deep(.n-data-table-td) {
    padding: 8px 12px;
    font-size: 13px;
  }
}

@media (max-width: 480px) {
  .profile-container {
    padding: 8px 12px;
    gap: 12px;
  }
  
  .info-password-row {
    gap: 12px;
  }
  
  .profile-card :deep(.n-card-header) {
    padding: 10px 12px;
  }
  
  .profile-card :deep(.n-card__content) {
    padding: 12px;
  }
  
  .token-header {
    padding: 10px;
    gap: 8px;
  }
  
  .username-input-group {
    gap: 6px;
  }
  
  .inline-update-btn,
  .generate-btn {
    height: 32px;
    font-size: 13px;
  }
  
  .inline-update-btn {
    margin-left: 0;
  }
  
  .token-table :deep(.n-data-table-th),
  .token-table :deep(.n-data-table-td) {
    padding: 6px 8px;
    font-size: 12px;
  }
}

/* Token模态框样式 */
.token-modal-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.token-display {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 16px;
  margin: 16px 0;
  position: relative;
}

.token-notice {
  padding: 12px;
  background: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 6px;
  color: #856404;
}

.token-modal-actions {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.token-modal-actions .n-button {
  min-width: 120px;
}

/* 模态框响应式 */
@media (max-width: 768px) {
  .token-modal-content {
    gap: 12px;
  }
  
  .token-display {
    padding: 12px;
    margin: 12px 0;
  }
  
  .token-modal-actions {
    flex-direction: column;
    gap: 8px;
  }
  
  .token-modal-actions .n-button {
    width: 100%;
    min-width: auto;
  }
}
</style>
