import { request } from '@/utils'
import infraApi from './infra'

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
  getUserList: (params = {}) => request.get('/admin/users', { params }),
  createUser: (data = {}) => request.post('/admin/users', data),
  updateUser: (id, data = {}) => request.put(`/admin/users/${id}`, data),
  deleteUser: (id) => request.delete(`/admin/users/${id}`),
  resetUserPassword: (id, data = {}) => request.post(`/admin/users/${id}/reset-password`, data),
  
  // users
  getUserList: (params = {}) => request.get('/user/list', { params }),
  getUserById: (params = {}) => request.get('/user/get', { params }),
  createUser: (data = {}) => request.post('/user/create', data),
  updateUser: (data = {}) => request.post('/user/update', data),
  deleteUser: (params = {}) => request.delete(`/user/delete`, { params }),
  // role
  getRoleList: (params = {}) => request.get('/role/list', { params }),
  createRole: (data = {}) => request.post('/role/create', data),
  updateRole: (data = {}) => request.post('/role/update', data),
  deleteRole: (params = {}) => request.delete('/role/delete', { params }),
  updateRoleAuthorized: (data = {}) => request.post('/role/authorized', data),
  getRoleAuthorized: (params = {}) => request.get('/role/authorized', { params }),
  // menus
  getMenus: (params = {}) => request.get('/menu/list', { params }),
  createMenu: (data = {}) => request.post('/menu/create', data),
  updateMenu: (data = {}) => request.post('/menu/update', data),
  deleteMenu: (params = {}) => request.delete('/menu/delete', { params }),
  // apis
  getApis: (params = {}) => request.get('/api/list', { params }),
  createApi: (data = {}) => request.post('/api/create', data),
  updateApi: (data = {}) => request.post('/api/update', data),
  deleteApi: (params = {}) => request.delete('/api/delete', { params }),
  refreshApi: (data = {}) => request.post('/api/refresh', data),
  // depts
  getDepts: (params = {}) => request.get('/dept/list', { params }),
  createDept: (data = {}) => request.post('/dept/create', data),
  updateDept: (data = {}) => request.post('/dept/update', data),
  deleteDept: (params = {}) => request.delete('/dept/delete', { params }),
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
}
