import { defineStore } from 'pinia'
import { resetRouter } from '@/router'
import { useTagsStore, usePermissionStore, useTeamStore } from '@/store'
import { removeToken, toLogin } from '@/utils'
import api from '@/api'

export const useUserStore = defineStore('user', {
  state() {
    return {
      userInfo: {},
    }
  },
  getters: {
    userId() {
      return this.userInfo?.id
    },
    name() {
      return this.userInfo?.username
    },
    email() {
      return this.userInfo?.email
    },
    avatar() {
      return this.userInfo?.avatar
    },
    role() {
      return this.userInfo?.roles || []
    },
    forcePasswordChange() {
      return this.userInfo?.forcePasswordChange || false
    },
  },
  actions: {
    async getUserInfo() {
      try {
        const res = await api.getUserInfo()
        if (res.code === 401) {
          this.logout()
          return
        }
        const { id, username, email, avatar, forcePasswordChange } = res.data
        this.userInfo = { id, username, email, avatar, forcePasswordChange }
        return res.data
      } catch (error) {
        return error
      }
    },
    async logout() {
      const { resetTags } = useTagsStore()
      const { resetPermission } = usePermissionStore()
      const { resetTeamState } = useTeamStore()
      removeToken()
      resetTags()
      resetPermission()
      resetTeamState()
      resetRouter()
      this.$reset()
      toLogin()
    },
    setUserInfo(userInfo = {}) {
      this.userInfo = { ...this.userInfo, ...userInfo }
    },
    setForcePasswordChange(value) {
      this.userInfo.forcePasswordChange = value
    },
  },
})
