import { infraRequest } from '@/utils/http/infra-client'

export default {
  // 沙箱管理（5个接口）
  getSandboxList: (params = {}) => {
    return infraRequest.get('/sandboxes', {
      params: {
        metadata: params.metadata,
        state: params.state,
        nextToken: params.nextToken,
        limit: params.limit,
      },
    })
  },

  getSandboxById: (sandboxID) => {
    return infraRequest.get(`/sandboxes/${sandboxID}`)
  },

  deleteSandbox: (sandboxID) => {
    return infraRequest.delete(`/sandboxes/${sandboxID}`)
  },

  pauseSandbox: (sandboxID) => {
    return infraRequest.post(`/sandboxes/${sandboxID}/pause`)
  },

  resumeSandbox: (sandboxID, data = {}) => {
    return infraRequest.post(`/sandboxes/${sandboxID}/resume`, data)
  },

  // 创建沙箱 - POST /sandboxes
  createSandbox: (data) => {
    return infraRequest.post('/sandboxes', {
      templateID: data.templateID,
      timeout: data.timeout || 15,
      autoPause: data.autoPause || false,
      secure: data.secure,
      metadata: data.metadata || {},
      envVars: data.envVars || {},
    })
  },

  // 模板管理（扩展接口）
  getTemplateList: (params = {}) => {
    //TODO 用于测试
    if(params.teamID == '8455fc27-81f5-48e0-a5c1-7be43628daf4'){
      params.teamID = '9b186512-b1ad-4de6-82f9-a7b06a935d50'
    }
    return infraRequest.get('/templates', {
      params: {
        teamID: params.teamID,
      },
    })
  },

  // 创建模版 - POST /templates
  createTemplate: (data) => {
    return infraRequest.post('/templates', {
      dockerfile: data.dockerfile,
      alias: data.alias,
      teamID: data.teamID,
      startCmd: data.startCmd,
      readyCmd: data.readyCmd,
      cpuCount: data.cpuCount,
      memoryMB: data.memoryMB,
    })
  },

  // 触发构建 - POST /templates/{templateID}/builds/{buildID}
  startTemplateBuild: (templateID, buildID) => {
    return infraRequest.post(`/templates/${templateID}/builds/${buildID}`)
  },

  // 获取构建状态 - GET /templates/{templateID}/builds/{buildID}/status
  getTemplateBuildStatus: (templateID, buildID, logsOffset = 0) => {
    return infraRequest.get(`/templates/${templateID}/builds/${buildID}/status`, {
      params: { logsOffset },
    })
  },

  // 获取模版详情（通过模版列表接口获取单个）
  getTemplateById: (templateID) => {
    return infraRequest
      .get('/templates', {
        params: { templateID },
      })
      .then((res) => {
        const templates = Array.isArray(res) ? res : []
        return templates.find((t) => t.templateID === templateID) || null
      })
  },

  deleteTemplate: (templateID) => {
    return infraRequest.delete(`/templates/${templateID}`)
  },

  updateTemplate: (templateID, data) => {
    return infraRequest.patch(`/templates/${templateID}`, {
      public: data.public,
    })
  },

  // API Key管理（3个接口）
  getApiKeys: () => {
    return infraRequest.get('/api-keys')
  },

  createApiKey: (data) => {
    return infraRequest.post('/api-keys', {
      name: data.name,
    })
  },

  deleteApiKey: (apiKeyID) => {
    return infraRequest.delete(`/api-keys/${apiKeyID}`)
  },
}
