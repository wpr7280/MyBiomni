import { request } from '@/utils'

export default {
  // Skill 列表
  getSkillList: (params = {}) => request.get('/skills', { params }),
  // Skill 详情
  getSkillDetail: (id) => request.get(`/skills/${id}`),
  // 创建 Skill
  createSkill: (data = {}) => request.post('/skills', data),
  // 更新 Skill
  updateSkill: (id, data = {}) => request.put(`/skills/${id}`, data),
  // 启用 Skill
  enableSkill: (id) => request.patch(`/skills/${id}/enable`),
  // 禁用 Skill
  disableSkill: (id) => request.patch(`/skills/${id}/disable`),
  // 获取 How-To
  getSkillHowTo: (id) => request.get(`/skills/${id}/how-to`),
  // 更新 How-To
  updateSkillHowTo: (id, data = {}) => request.put(`/skills/${id}/how-to`, data),
  // 获取 Tools
  getSkillTools: (id) => request.get(`/skills/${id}/tools`),
  // 更新 Tool
  updateSkillTool: (id, toolName, data = {}) => request.put(`/skills/${id}/tools/${toolName}`, data),
  // 重载 Skill
  reloadSkill: (id) => request.post(`/skills/${id}/reload`),
  // 重载所有 Skill
  reloadAllSkills: () => request.post('/skills/reload-all'),
  // 获取分类列表
  getCategories: () => request.get('/skills/categories'),
  // 删除 Skill
  deleteSkill: (id) => request.delete(`/skills/${id}`),
}
