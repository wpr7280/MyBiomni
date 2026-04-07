import { request } from '@/utils'
import infraApi from './infra'
import skillsApi from './skills'
import knowhowApi from './knowhow'

export default {
  login: (data) => request.post('/auth/login', data, { noNeedToken: true }),
  // getLoginUrl: (params) => request.get('/auth/login/thirdGetUrl', { params, noNeedToken: true }),
  // oauthCallback: (data) => request.post('/auth/callback', data, { noNeedToken: true }),
  // checkLoginStatus: (data) => request.post('/auth/checkLoginStatus', data, { noNeedToken: true }),
  //注册
  register: (data) => request.post('/auth/register', data, { noNeedToken: true }),
  sendVerificationCode: (data) => request.post('/auth/sendEmail', data, { noNeedToken: true }),
  
  // 忘记密码相关接口
  sendEmail: (data) => request.post('/auth/sendEmail', data, { noNeedToken: true }),
  resetPassword: (data) => request.post('/auth/resetPassword', data, { noNeedToken: true }),

  getUserInfo: () => request.get('/auth/me'),
  getUserMenu: () => request.get('/menu/list'),

  // profile
  updateUserInfo: (data = {}) => request.post('/auth/updateUserInfo', data),
  updatePassword: (data = {}) => request.post('/auth/updatePassword', data),
  
  // ========== 对话管理 ==========
  getConversations: (params = {}) => request.get('/conversations', { params }),
  createConversation: (data = {}) => request.post('/conversations', data),
  getConversationDetail: (id) => request.get(`/conversations/${id}`),
  deleteConversation: (id) => request.delete(`/conversations/${id}`),
  
  // ========== 知识库 ==========
  getKnowHowList: (params = {}) => request.get('/knowhow', { params }),
  getKnowHowDetail: (id) => request.get(`/knowhow/${id}`),
  
  // ========== 管理员 - 用户管理 ==========
  getUserList: (params = {}) => request.post('/users/list', params),
  createUser: (data = {}) => request.post('/users/create', data),
  updateUser: (data = {}) => request.post('/users/update', data),
  deleteUser: (data = {}) => request.post('/users/delete', data),
  resetUserPassword: (data = {}) => request.post('/users/reset-password', data),
  
  // ========== 管理员 - 配额管理 ==========
  getQuota: (data = {}) => request.post('/quota/get', data),
  updateQuota: (data = {}) => request.post('/quota/update', data),
  resetQuota: (data = {}) => request.post('/quota/reset', data),
  
  // ========== 管理员 - 对话管理 ==========
  getAdminConversationList: (data = {}) => request.post('/admin/conversations/list', data),
  getAdminConversationDetail: (data = {}) => request.post('/admin/conversations/detail', data),
  deleteAdminConversation: (data = {}) => request.post('/admin/conversations/delete', data),
  
  // ========== 系统配置 ==========
  getConfigList: () => request.post('/config/list', {}),
  getConfigStatus: () => request.post('/config/status', {}),
  updateConfig: (data = {}) => request.post('/config/update', data),
  batchUpdateConfig: (data = {}) => request.post('/config/batch-update', data),
  resetConfig: () => request.post('/config/reset', {}),
  
  // // users
  // getUserList: (params = {}) => request.get('/user/list', { params }),
  // getUserById: (params = {}) => request.get('/user/get', { params }),
  // createUser: (data = {}) => request.post('/user/create', data),
  // updateUser: (data = {}) => request.post('/user/update', data),
  // deleteUser: (params = {}) => request.delete(`/user/delete`, { params }),
  // role

  // menus
  getMenus: (params = {}) => request.get('/menu/list', { params }),
  createMenu: (data = {}) => request.post('/menu/create', data),
  updateMenu: (data = {}) => request.post('/menu/update', data),
  deleteMenu: (params = {}) => request.delete('/menu/delete', { params }),
  // auditlog
  getAuditLogList: (params = {}) => request.get('/auditlog/list', { params }),

  // 模板管理 - 使用Infra API
  getTemplateList: infraApi.getTemplateList,
  getTemplateById: infraApi.getTemplateById,
  createTemplate: infraApi.createTemplate,
  startTemplateBuild: infraApi.startTemplateBuild,
  getTemplateBuildStatus: infraApi.getTemplateBuildStatus,
  updateTemplate: infraApi.updateTemplate,
  deleteTemplate: infraApi.deleteTemplate,

  // 沙箱管理 - 使用Infra API
  getSandboxList: infraApi.getSandboxList,
  getSandboxById: infraApi.getSandboxById,
  createSandbox: infraApi.createSandbox, // 使用Infra API
  updateSandbox: (data = {}) => request.post('/sandboxs/update', data), // 保持原有后端
  deleteSandbox: infraApi.deleteSandbox,
  pauseSandbox: infraApi.pauseSandbox,
  resumeSandbox: infraApi.resumeSandbox,
  getSandboxLogs: infraApi.getSandboxLogs,
  getSandboxMetrics: infraApi.getSandboxMetrics,
  setSandboxTimeout: infraApi.setSandboxTimeout,
  refreshSandbox: infraApi.refreshSandbox,
  setTimeoutSandbox: (data = {}) => request.post('/sandboxs/timeout', data), // 保持原有后端
  // usage
  getUsageSummary: (params = {}) => request.get('/bill/usage', { params }),
  getUsageTrend: (params = {}) => request.get('/usage/trend', { params }),
  getUsageList: (params = {}) => request.get('/usage/list', { params }),
 // API Key管理 - 调用后端API（使用用户token认证）
 getApiKeys: (params = {}) => request.get('/teams/getApiKeys', { params }),
 createApiKey: (data = {}) => request.post('/teams/createApiKey', data),
 deleteApiKey: (data = {}) => request.post('/teams/deleteApiKey',  data ),

  // teams
  getTeamInfo: (params = {}) => request.get('/teams', { params }),
  createTeam: (data = {}) => request.post('/teams/createTeam', data),
  updateTeamName: (data = {}) => request.post('/teams/update', data),
  getTeamMembers: (params = {}) => request.get('/teams/members', { params }),
  addTeamMember: (data = {}) => request.post('/teams/addTeamMember', data),
  removeTeamMember: (data = {}) => request.post('/teams/members/remove', data),

  // Access Token管理
  listAccessToken: (params = {}) => request.get('/auth/listAccessToken', { params }),
  createAccessToken: (data = {}) => request.post('/auth/createAccessToken', data),
  deleteAccessToken: (data = {}) => request.post('/auth/deleteAccessToken', data),

  // ========== Skill 管理 ==========
  ...skillsApi,

  // ========== Know-How 管理 ==========
  ...knowhowApi,
}
