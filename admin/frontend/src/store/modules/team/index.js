import { defineStore } from 'pinia'
import api from '@/api'

export const useTeamStore = defineStore('team', {
  state() {
    return {
      currentTeam: null,
      teams: [],
      teamMembers: [],
      loading: false,
      error: null,
    }
  },

  getters: {
    currentTeamId() {

      return this.currentTeam?.id
    },
    currentTeamName() {
      return this.currentTeam?.name || '未选择团队'
    },
    isTeamOwner() {
      if (!this.currentTeam || !this.teamMembers.length) return false
      const currentUser = this.teamMembers.find((member) => member.isCurrent)
      return currentUser?.role === 'owner'
    },
    isTeamAdmin() {
      if (!this.currentTeam || !this.teamMembers.length) return false
      const currentUser = this.teamMembers.find((member) => member.isCurrent)
      return currentUser?.role === 'owner' || currentUser?.role === 'admin'
    },
  },

  actions: {
    // 获取用户所属的团队列表
    async fetchTeams() {
      this.loading = true
      this.error = null
      try {
        const res = await api.getTeamInfo()
        console.log('API响应:', res)
        if (res.code === 200 && Array.isArray(res.data)) {
          // 转换API数据格式为前端需要的格式
          this.teams = res.data.map((team) => ({
            id: team.id,
            name: team.name,
            slug: team.slug,
            logo: team.profilePictureUrl,
            email: team.email,
            tier: team.tier,
            isBlocked: team.isBlocked,
            isBanned: team.isBanned,
            isDefault: team.isDefault,
            createdAt: this.formatCreatedAt(team.createdAt),
            memberCount: team.memberCount || 0,
          }))

          // 优先选择默认团队，如果没有默认团队则选择第一个
          if (!this.currentTeam && this.teams.length > 0) {
            const defaultTeam = this.teams.find((team) => team.isDefault) || this.teams[0]
            this.currentTeam = defaultTeam
            this.saveCurrentTeamToStorage()
          }
        }
      } catch (error) {
        this.error = error.message || '获取团队列表失败'
        console.error('获取团队列表失败:', error)
      } finally {
        this.loading = false
      }
    },

    // 切换当前团队
    async switchTeam(teamId) {
      const team = this.teams.find((t) => t.id === teamId)
      if (team) {
        this.currentTeam = team
        this.saveCurrentTeamToStorage()
        // 切换团队后重新获取成员信息
        await this.fetchTeamMembers()
        return true
      }
      return false
    },

    // 获取团队成员
    async fetchTeamMembers(teamId = null) {
      const targetTeamId = teamId || this.currentTeamId
      if (!targetTeamId) return

      this.loading = true
      try {
        const res = await api.getTeamMembers({ teamId: targetTeamId })
        console.log('团队成员API响应:', res)
        if (res.code === 200) {
          // 转换API数据格式为前端需要的格式
          this.teamMembers = (res.data || []).map((member) => ({
            userId: member.info?.id || member.relation?.userId,
            name: member.info?.email?.split('@')[0] || '未知用户', // 从邮箱提取用户名
            email: member.info?.email,
            avatar: member.info?.avatar || null,
            role: this.getMemberRole(member.relation),
            isDefault: member.relation?.isDefault || false,
            addBy: member.relation?.addedBy,
            addByName: member.relation?.addedByName || null,
            joinedAt: member.relation?.createdAt || new Date().toISOString(),
            isCurrent: false, // 这里需要根据当前用户ID判断
          }))

          // 更新团队成员数量
          const team = this.teams.find((t) => t.id === targetTeamId)
          if (team) {
            team.memberCount = this.teamMembers.length
          }
        }
      } catch (error) {
        this.error = error.message || '获取团队成员失败'
        console.error('获取团队成员失败:', error)
      } finally {
        this.loading = false
      }
    },

    // 根据关系信息确定成员角色
    getMemberRole(relation) {
      if (!relation) return 'member'

      // 如果是默认团队的默认成员，通常是所有者
      if (relation.isDefault) return 'owner'

      // 如果有addedBy字段为null，可能是所有者
      if (relation.addedBy === null) return 'owner'

      // 默认为普通成员
      return 'member'
    },

    // 创建新团队
    async createTeam(teamData) {
      this.loading = true
      try {
        const res = await api.createTeam({
          name: teamData.name,
        })

        if (res.code === 200) {
          // 重新获取团队列表
          await this.fetchTeams()
          return { success: true, data: res.data }
        }
        return { success: false, message: res.msg || '创建团队失败' }
      } catch (error) {
        console.error('创建团队失败:', error)
        return { success: false, message: error.message || '创建团队失败' }
      } finally {
        this.loading = false
      }
    },

    // 更新团队信息
    async updateTeam(teamId, teamData) {
      this.loading = true
      try {
        const res = await api.updateTeamName(teamData)
        if (res.code === 200) {
          // 更新本地团队信息
          const teamIndex = this.teams.findIndex((t) => t.id === teamId)
          if (teamIndex !== -1) {
            this.teams[teamIndex] = { ...this.teams[teamIndex], ...teamData }
            if (this.currentTeam?.id === teamId) {
              this.currentTeam = { ...this.currentTeam, ...teamData }
            }
          }
          return { success: true, data: res.data }
        }
        return { success: false, message: res.msg || '更新团队失败' }
      } catch (error) {
        console.error('更新团队失败:', error)
        return { success: false, message: error.message || '更新团队失败' }
      } finally {
        this.loading = false
      }
    },

    // 邀请团队成员
    async inviteMember(memberData) {
      this.loading = true
      try {
        const res = await api.addTeamMember(memberData)
        if (res.code === 200) {
          // 重新获取成员列表
          await this.fetchTeamMembers()
          return { success: true, data: res.data }
        }
        return { success: false, message: res.msg || '邀请成员失败' }
      } catch (error) {
        console.error('邀请成员失败:', error)
        return { success: false, message: error.message || '邀请成员失败' }
      } finally {
        this.loading = false
      }
    },

    // 移除团队成员
    async removeMember(userId) {
      this.loading = true
      try {
        const res = await api.removeTeamMember({ userId })
        if (res.code === 200) {
          // 重新获取成员列表
          await this.fetchTeamMembers()
          return { success: true, data: res.data }
        }
        return { success: false, message: res.msg || '移除成员失败' }
      } catch (error) {
        console.error('移除成员失败:', error)
        return { success: false, message: error.message || '移除成员失败' }
      } finally {
        this.loading = false
      }
    },

    // 保存当前团队到本地存储
    saveCurrentTeamToStorage() {
      if (this.currentTeam) {
        localStorage.setItem('currentTeam', JSON.stringify(this.currentTeam))
      }
    },

    // 从本地存储加载当前团队
    loadCurrentTeamFromStorage() {
      const stored = localStorage.getItem('currentTeam')
      if (stored) {
        try {
          this.currentTeam = JSON.parse(stored)
        } catch (error) {
          console.error('解析存储的团队信息失败:', error)
          localStorage.removeItem('currentTeam')
        }
      }
    },

    // 格式化创建时间（将数组格式转换为日期字符串）
    formatCreatedAt(createdAtArray) {
      if (!Array.isArray(createdAtArray) || createdAtArray.length < 6) {
        return new Date().toISOString()
      }

      const [year, month, day, hour, minute, second, nanosecond] = createdAtArray
      const date = new Date(
        year,
        month - 1,
        day,
        hour,
        minute,
        second,
        Math.floor(nanosecond / 1000000)
      )
      return date.toISOString()
    },

    // 重置状态
    resetTeamState() {
      this.currentTeam = null
      this.teams = []
      this.teamMembers = []
      this.loading = false
      this.error = null
      localStorage.removeItem('currentTeam')
    },
  },
})
