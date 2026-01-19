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

        <div v-if="loading" class="mt-30 f-c-c flex-col">
          <n-spin size="large" />
          <p class="mt-10 text-16 text-gray-600">{{ $t('views.oauth.processing') }}</p>
        </div>

        <div v-if="errorMsg" class="mt-30 text-center">
          <div class="f-c-c flex-col">
            <Icon icon="ri:error-warning-line" class="mb-4 text-60 text-red-500" />
            <n-alert type="error" show-icon class="w-full">{{ errorMsg }}</n-alert>
          </div>
          <n-button class="mt-20" type="primary" size="large" @click="redirectToLogin">
            {{ $t('views.oauth.back_to_login') }}
          </n-button>
        </div>

        <div v-if="success" class="mt-30 text-center">
          <div class="f-c-c flex-col">
            <Icon icon="ri:check-line" class="mb-4 text-60 text-green-500" />
            <n-alert type="success" show-icon class="w-full">{{
              $t('views.oauth.success')
            }}</n-alert>
          </div>
          <p class="mt-10 text-16 text-gray-600">{{ $t('views.oauth.redirecting') }}</p>
        </div>

        <div mt-15 flex justify-center gap-10 text-12 color-gray-500>
          <RouterLink to="/privacy">{{ $t('common.privacy') }}</RouterLink>
          <n-divider vertical />
          <RouterLink to="/agreement">{{ $t('common.agreement') }}</RouterLink>
        </div>
      </div>
    </div>
  </AppPage>
</template>

<script setup>
import { setToken } from '@/utils'
import bgImg from '@/assets/images/login_bg.webp'
import api from '@/api'
import { addDynamicRoutes } from '@/router'
import { useI18n } from 'vue-i18n'

const router = useRouter()
const route = useRoute()
const { t } = useI18n({ useScope: 'global' })

const loading = ref(true)
const errorMsg = ref('')
const success = ref(false)

onMounted(async () => {
  // const { code, state, type } = route.query
  // if (!code) {
  //   errorMsg.value = t('views.oauth.no_code_provided')
  //   loading.value = false
  //   return
  // }
  //
  // try {
  //   const res = await api.oauthCallback({ code, state, type })
  //   setToken(res.data.token)
  //   await addDynamicRoutes()
  //   success.value = true
  //
  //   setTimeout(() => {
  //     const redirect = route.query.redirect || '/'
  //     router.push(redirect)
  //   }, 1500)
  // } catch (e) {
  //   errorMsg.value = e?.message || t('views.oauth.failed')
  // } finally {
  //   loading.value = false
  // }
})

function redirectToLogin() {
  router.push({ name: 'Login' })
}
</script>
