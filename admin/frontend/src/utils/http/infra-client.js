import axios from 'axios'
import { getToken } from '@/utils/auth/token'
import { resolveResError } from './helpers'
import { useUserStore, useTeamStore } from '@/store'

// Infra API专用的请求拦截器
export function infraReqResolve(config) {
  console.log('Infra API请求拦截器 - 配置:', config)
  const token = getToken()
  const teamStore = useTeamStore()
  
  if (token) {
    // 使用固定的API Key进行认证
    // config.headers.Authorization = `Bearer sk_e2b_740red39iji9j770z0yko4p9s7fnwr2z`
    // config.headers['X-Supabase-Token'] = `eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJlOTI2ZTVkZC04NzllLTQ5OGMtODYyZS1hYTllMmJmZWJhYzgiLCJlbWFpbCI6ImUyYkBleGFtcGxlLmNvbSIsImlhdCI6MTc1MTU4MzEzOSwiZXhwIjoxNzUzMDU0MzY4fQ.5ls9Y3vJ8-8LFZWGWprGnNR_DkmQ6-vQg7Fy7FbFjQFDe9z8HlTR1W4QXe9CNl5OF8ImclnfkGrfqEnN05lPqw`
    // config.headers['X-Supabase-Team'] = '9b186512-b1ad-4de6-82f9-a7b06a935d50'
    // 使用用户token和当前团队ID进行认证
    config.headers['X-Supabase-Token'] = token
    config.headers['X-Supabase-Team'] = teamStore.currentTeamId || ''
  }
  console.log('Infra API请求拦截器 - 最终配置:', config)
  return config
}

// Infra API专用的响应拦截器
export function infraResResolve(response) {
  console.log('Infra API响应拦截器 - 原始响应:', response)
  const { data, status, statusText } = response
  console.log('Infra API响应拦截器 - 数据:', data)
  console.log('Infra API响应拦截器 - 状态:', status)

  // 根据Infra API的响应格式调整
  if (status >= 400) {
    const message = resolveResError(status, data?.message || statusText)
    window.$message?.error(message, { keepAliveOnHover: true })
    return Promise.reject({ code: status, message, error: data || response })
  }

  console.log('Infra API响应拦截器 - 返回数据:', data)
  return Promise.resolve(data) // 直接返回data，不需要检查code字段
}

export async function infraResReject(error) {
  if (!error || !error.response) {
    const code = error?.code
    const message = resolveResError(code, error.message)
    window.$message?.error(message)
    return Promise.reject({ code, message, error })
  }

  const { data, status } = error.response

  if (status === 401) {
    try {
      const userStore = useUserStore()
      userStore.logout()
    } catch (error) {
      console.log('infraResReject error', error)
      return
    }
  }

  const code = status
  const message = resolveResError(code, data?.message || error.message)
  window.$message?.error(message, { keepAliveOnHover: true })
  return Promise.reject({ code, message, error: data || error.response })
}

// 创建Infra API客户端
export const infraRequest = axios.create({
  baseURL: import.meta.env.VITE_INFRA_API_URL || '',  // 留空或由环境变量配置
  timeout: 12000,
})

infraRequest.interceptors.request.use(infraReqResolve, (error) => Promise.reject(error))
infraRequest.interceptors.response.use(infraResResolve, infraResReject)
