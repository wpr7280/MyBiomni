# Frontend 实现计划

## 概述

根据后端菜单配置，前端需要实现以下页面和功能。

## 1. 页面结构

### 1.1 所有用户可访问的页面

```
/workbench              - 工作台（已存在）
/conversations          - 对话管理（需创建）
/knowhow                - 知识库（需创建）
/profile                - 个人中心（已存在）
```

### 1.2 仅管理员可访问的页面

```
/system/users           - 用户管理（需创建）
/system/quota           - 配额管理（需创建）
/system/conversations   - 对话记录（需创建）
/system/knowhow         - 文档管理（需创建）
/config/model           - 模型配置（需创建）
/config/commercial      - 商用模式（需创建）
/config/system          - 系统设置（需创建）
```

## 2. 需要创建的页面

### 2.1 对话管理 (/conversations)

**目录**: `src/views/conversations/`

**文件**:
- `index.vue` - 对话列表页面
- `detail.vue` - 对话详情页面
- `create.vue` - 创建对话页面（可选，可以用 Modal）

**功能**:
- 对话列表展示（卡片或表格）
- 创建新对话
- 查看对话详情
- 删除对话
- 搜索和筛选

**API**:
```javascript
getConversations: (params) => request.get('/conversations', { params })
createConversation: (data) => request.post('/conversations', data)
getConversationDetail: (id) => request.get(`/conversations/${id}`)
deleteConversation: (id) => request.delete(`/conversations/${id}`)
```

### 2.2 知识库 (/knowhow)

**目录**: `src/views/knowhow/`

**文件**:
- `index.vue` - 文档列表页面
- `detail.vue` - 文档详情页面

**功能**:
- 文档列表展示
- 文档搜索
- 分类筛选
- 标签筛选
- 查看文档详情（Markdown 渲染）

**API**:
```javascript
getKnowHowList: (params) => request.get('/knowhow', { params })
getKnowHowDetail: (id) => request.get(`/knowhow/${id}`)
```

### 2.3 用户管理 (/system/users)

**目录**: `src/views/system/users/`

**文件**:
- `index.vue` - 用户列表页面
- `components/UserModal.vue` - 创建/编辑用户弹窗

**功能**:
- 用户列表（表格）
- 创建用户
- 编辑用户
- 删除用户
- 重置密码
- 修改状态
- 角色管理

**API**:
```javascript
getUserList: (params) => request.get('/admin/users', { params })
createUser: (data) => request.post('/admin/users', data)
updateUser: (id, data) => request.put(`/admin/users/${id}`, data)
deleteUser: (id) => request.delete(`/admin/users/${id}`)
resetPassword: (id, data) => request.post(`/admin/users/${id}/reset-password`, data)
```

### 2.4 配额管理 (/system/quota)

**目录**: `src/views/system/quota/`

**文件**:
- `index.vue` - 配额管理页面
- `components/QuotaTemplateModal.vue` - 配额模板弹窗
- `components/UserQuotaModal.vue` - 用户配额设置弹窗

**功能**:
- 配额模板列表
- 创建/编辑模板
- 用户配额分配
- 配额使用统计

**API**:
```javascript
getQuotaTemplates: (params) => request.get('/admin/quota/templates', { params })
createQuotaTemplate: (data) => request.post('/admin/quota/templates', data)
setUserQuota: (userId, data) => request.put(`/admin/users/${userId}/quota`, data)
getUserQuotaUsage: (userId, params) => request.get(`/admin/users/${userId}/quota/usage`, { params })
```

### 2.5 对话记录 (/system/conversations)

**目录**: `src/views/system/conversations/`

**文件**:
- `index.vue` - 所有对话记录列表
- `detail.vue` - 对话详情（复用 /conversations/detail.vue）

**功能**:
- 查看所有用户的对话
- 按用户筛选
- 按时间筛选
- 导出对话记录
- 对话统计

**API**:
```javascript
getAllConversations: (params) => request.get('/admin/conversations', { params })
getConversationStats: (params) => request.get('/admin/conversations/stats', { params })
exportConversations: (data) => request.post('/admin/conversations/export', data)
```

### 2.6 文档管理 (/system/knowhow)

**目录**: `src/views/system/knowhow/`

**文件**:
- `index.vue` - 文档管理列表
- `editor.vue` - 文档编辑器
- `components/DocumentModal.vue` - 文档元数据编辑弹窗

**功能**:
- 文档列表管理
- 创建/编辑文档
- Markdown 编辑器
- 元数据管理
- 文档状态管理
- 版本历史

**API**:
```javascript
getKnowHowListAdmin: (params) => request.get('/admin/knowhow', { params })
createKnowHow: (data) => request.post('/admin/knowhow', data)
updateKnowHow: (id, data) => request.put(`/admin/knowhow/${id}`, data)
deleteKnowHow: (id) => request.delete(`/admin/knowhow/${id}`)
updateKnowHowStatus: (id, data) => request.put(`/admin/knowhow/${id}/status`, data)
```

### 2.7 模型配置 (/config/model)

**目录**: `src/views/config/model/`

**文件**:
- `index.vue` - 模型配置页面

**功能**:
- 模型配置表单
- 测试连接
- 保存配置

**API**:
```javascript
getModelConfig: () => request.get('/admin/config/model')
updateModelConfig: (data) => request.put('/admin/config/model', data)
testModelConnection: (data) => request.post('/admin/config/model/test', data)
```

### 2.8 商用模式 (/config/commercial)

**目录**: `src/views/config/commercial/`

**文件**:
- `index.vue` - 商用模式配置页面

**功能**:
- 商用模式开关
- 影响说明
- 配置历史

**API**:
```javascript
getCommercialConfig: () => request.get('/admin/config/commercial')
updateCommercialConfig: (data) => request.put('/admin/config/commercial', data)
```

### 2.9 系统设置 (/config/system)

**目录**: `src/views/config/system/`

**文件**:
- `index.vue` - 系统设置页面

**功能**:
- 系统参数配置
- 保存设置

**API**:
```javascript
getSystemConfig: () => request.get('/admin/config/system')
updateSystemConfig: (data) => request.put('/admin/config/system', data)
```

## 3. 路由配置

### 3.1 更新路由文件

**文件**: `src/router/routes/index.js`

需要添加的路由（根据后端菜单动态生成）：

```javascript
// 对话管理
{
  name: '对话管理',
  path: '/conversations',
  component: Layout,
  meta: { roles: ['admin', 'user'] },
  children: [
    {
      path: '',
      component: () => import('@/views/conversations/index.vue'),
      meta: { title: '对话管理', icon: 'chat' }
    }
  ]
}

// 知识库
{
  name: '知识库',
  path: '/knowhow',
  component: Layout,
  meta: { roles: ['admin', 'user'] },
  children: [
    {
      path: '',
      component: () => import('@/views/knowhow/index.vue'),
      meta: { title: '知识库', icon: 'book' }
    }
  ]
}

// 系统管理（仅管理员）
{
  name: '系统管理',
  path: '/system',
  component: Layout,
  meta: { roles: ['admin'] },
  children: [
    {
      path: 'users',
      component: () => import('@/views/system/users/index.vue'),
      meta: { title: '用户管理' }
    },
    {
      path: 'quota',
      component: () => import('@/views/system/quota/index.vue'),
      meta: { title: '配额管理' }
    },
    {
      path: 'conversations',
      component: () => import('@/views/system/conversations/index.vue'),
      meta: { title: '对话记录' }
    },
    {
      path: 'knowhow',
      component: () => import('@/views/system/knowhow/index.vue'),
      meta: { title: '文档管理' }
    }
  ]
}

// 系统配置（仅管理员）
{
  name: '系统配置',
  path: '/config',
  component: Layout,
  meta: { roles: ['admin'] },
  children: [
    {
      path: 'model',
      component: () => import('@/views/config/model/index.vue'),
      meta: { title: '模型配置' }
    },
    {
      path: 'commercial',
      component: () => import('@/views/config/commercial/index.vue'),
      meta: { title: '商用模式' }
    },
    {
      path: 'system',
      component: () => import('@/views/config/system/index.vue'),
      meta: { title: '系统设置' }
    }
  ]
}
```

## 4. i18n 配置

### 4.1 需要添加的翻译键

**文件**: `i18n/messages/cn.json`

```json
{
  "views": {
    "conversations": {
      "label_conversations": "对话管理",
      "label_my_conversations": "我的对话",
      "label_conversation_list": "对话列表",
      "button_create_conversation": "创建对话",
      "button_delete": "删除",
      "button_view_detail": "查看详情",
      "label_title": "标题",
      "label_status": "状态",
      "label_created_at": "创建时间",
      "label_message_count": "消息数",
      "label_tokens": "Token消耗",
      "placeholder_search": "搜索对话...",
      "message_delete_confirm": "确认删除此对话吗？",
      "message_delete_success": "删除成功",
      "message_create_success": "创建成功"
    },
    "knowhow": {
      "label_knowhow": "知识库",
      "label_document_list": "文档列表",
      "label_title": "标题",
      "label_category": "分类",
      "label_tags": "标签",
      "label_author": "作者",
      "label_license": "许可证",
      "label_commercial_use": "商用许可",
      "placeholder_search": "搜索文档...",
      "button_view_detail": "查看详情",
      "text_allowed": "允许",
      "text_not_allowed": "不允许"
    },
    "system": {
      "users": {
        "label_user_management": "用户管理",
        "button_create_user": "创建用户",
        "button_edit": "编辑",
        "button_delete": "删除",
        "button_reset_password": "重置密码",
        "label_username": "用户名",
        "label_email": "邮箱",
        "label_role": "角色",
        "label_status": "状态",
        "label_created_at": "创建时间",
        "role_admin": "管理员",
        "role_user": "普通用户",
        "status_active": "启用",
        "status_disabled": "禁用",
        "message_create_success": "创建成功",
        "message_delete_confirm": "确认删除此用户吗？"
      },
      "quota": {
        "label_quota_management": "配额管理",
        "label_template_name": "模板名称",
        "label_daily_limit": "每日限制",
        "label_monthly_limit": "每月限制",
        "button_create_template": "创建模板",
        "button_set_quota": "设置配额"
      },
      "conversations": {
        "label_conversation_records": "对话记录",
        "label_all_conversations": "所有对话",
        "label_user": "用户",
        "button_export": "导出",
        "button_view_stats": "查看统计"
      },
      "knowhow": {
        "label_document_management": "文档管理",
        "button_create_document": "创建文档",
        "button_edit": "编辑",
        "button_delete": "删除",
        "label_status": "状态",
        "status_enabled": "启用",
        "status_disabled": "禁用",
        "status_draft": "草稿"
      }
    },
    "config": {
      "model": {
        "label_model_config": "模型配置",
        "label_model_name": "模型名称",
        "label_model_source": "模型来源",
        "label_temperature": "温度",
        "label_timeout": "超时时间",
        "button_test_connection": "测试连接",
        "button_save": "保存配置",
        "message_test_success": "连接测试成功",
        "message_save_success": "保存成功"
      },
      "commercial": {
        "label_commercial_mode": "商用模式",
        "label_enable_commercial": "启用商用模式",
        "text_description": "商用模式将排除非商用许可的数据集和工具",
        "button_save": "保存"
      },
      "system": {
        "label_system_settings": "系统设置",
        "label_max_concurrent_tasks": "最大并发任务数",
        "label_session_timeout": "会话超时时间",
        "button_save": "保存"
      }
    }
  }
}
```

## 5. 组件复用

### 5.1 通用组件

**已存在的组件**:
- `components/page/CommonPage.vue` - 页面容器
- `components/table/` - 表格组件
- `components/query-bar/` - 查询栏组件

**需要创建的组件**:
- `components/markdown/MarkdownViewer.vue` - Markdown 查看器
- `components/markdown/MarkdownEditor.vue` - Markdown 编辑器
- `components/conversation/ConversationCard.vue` - 对话卡片
- `components/knowhow/DocumentCard.vue` - 文档卡片

### 5.2 UI 风格统一

**参考现有页面**:
- Profile 页面的卡片样式
- Workbench 页面的布局
- 使用 Naive UI 组件库
- 保持圆角、阴影、渐变等设计风格

## 6. HTTP 请求配置

### 6.1 API 文件结构

**文件**: `src/api/index.js`

```javascript
import { request } from '@/utils'

export default {
  // ========== 认证相关 ==========
  login: (data) => request.post('/auth/login', data, { noNeedToken: true }),
  getUserInfo: () => request.get('/auth/me'),
  logout: () => request.post('/auth/logout'),
  updatePassword: (data) => request.post('/auth/updatePassword', data),
  updateUserInfo: (data) => request.post('/auth/updateUserInfo', data),
  
  // ========== 菜单 ==========
  getUserMenu: () => request.get('/menu/list'),
  
  // ========== 对话管理 ==========
  getConversations: (params) => request.get('/conversations', { params }),
  createConversation: (data) => request.post('/conversations', data),
  getConversationDetail: (id) => request.get(`/conversations/${id}`),
  deleteConversation: (id) => request.delete(`/conversations/${id}`),
  
  // ========== 知识库 ==========
  getKnowHowList: (params) => request.get('/knowhow', { params }),
  getKnowHowDetail: (id) => request.get(`/knowhow/${id}`),
  
  // ========== 管理员 - 用户管理 ==========
  getUserList: (params) => request.get('/admin/users', { params }),
  createUser: (data) => request.post('/admin/users', data),
  updateUser: (id, data) => request.put(`/admin/users/${id}`, data),
  deleteUser: (id) => request.delete(`/admin/users/${id}`),
  resetUserPassword: (id, data) => request.post(`/admin/users/${id}/reset-password`, data),
  
  // ========== 管理员 - 配额管理 ==========
  getQuotaTemplates: (params) => request.get('/admin/quota/templates', { params }),
  createQuotaTemplate: (data) => request.post('/admin/quota/templates', data),
  setUserQuota: (userId, data) => request.put(`/admin/users/${userId}/quota`, data),
  getUserQuotaUsage: (userId, params) => request.get(`/admin/users/${userId}/quota/usage`, { params }),
  
  // ========== 管理员 - 对话记录 ==========
  getAllConversations: (params) => request.get('/admin/conversations', { params }),
  getConversationStats: (params) => request.get('/admin/conversations/stats', { params }),
  exportConversations: (data) => request.post('/admin/conversations/export', data),
  
  // ========== 管理员 - 文档管理 ==========
  getKnowHowListAdmin: (params) => request.get('/admin/knowhow', { params }),
  createKnowHow: (data) => request.post('/admin/knowhow', data),
  updateKnowHow: (id, data) => request.put(`/admin/knowhow/${id}`, data),
  deleteKnowHow: (id) => request.delete(`/admin/knowhow/${id}`),
  updateKnowHowStatus: (id, data) => request.put(`/admin/knowhow/${id}/status`, data),
  
  // ========== 管理员 - 系统配置 ==========
  getModelConfig: () => request.get('/admin/config/model'),
  updateModelConfig: (data) => request.put('/admin/config/model', data),
  testModelConnection: (data) => request.post('/admin/config/model/test', data),
  getCommercialConfig: () => request.get('/admin/config/commercial'),
  updateCommercialConfig: (data) => request.put('/admin/config/commercial', data),
  getSystemConfig: () => request.get('/admin/config/system'),
  updateSystemConfig: (data) => request.put('/admin/config/system', data),
}
```

### 6.2 Request 工具配置

**文件**: `src/utils/http/request.js`

确保已配置：
- 自动添加 Authorization header
- 统一错误处理
- 401 自动跳转登录
- 403 显示权限不足

## 7. 权限控制

### 7.1 路由守卫

**文件**: `src/router/guard/permission.js`

```javascript
import { useUserStore } from '@/store'

export function setupPermissionGuard(router) {
  router.beforeEach((to, from, next) => {
    const userStore = useUserStore()
    
    // 检查路由是否需要特定角色
    const requiredRoles = to.meta.roles
    
    if (requiredRoles && requiredRoles.length > 0) {
      const userRole = userStore.role
      
      if (requiredRoles.includes(userRole)) {
        next()
      } else {
        // 无权限，跳转到 403
        next('/403')
      }
    } else {
      next()
    }
  })
}
```

### 7.2 组件权限指令

**文件**: `src/directives/permission.js`

```javascript
export default {
  mounted(el, binding) {
    const { value } = binding
    const userStore = useUserStore()
    const userRole = userStore.role
    
    if (value && value.length > 0) {
      const hasPermission = value.includes(userRole)
      
      if (!hasPermission) {
        el.parentNode && el.parentNode.removeChild(el)
      }
    }
  }
}

// 使用示例
<n-button v-permission="['admin']">管理员专用按钮</n-button>
```

## 8. 开发优先级

### Phase 1: 核心功能（1-2周）
1. ✅ 对话管理页面
2. ✅ 知识库浏览页面
3. ✅ 用户管理页面（管理员）

### Phase 2: 管理功能（1周）
4. ✅ 配额管理页面
5. ✅ 对话记录页面
6. ✅ 文档管理页面

### Phase 3: 配置功能（3-5天）
7. ✅ 模型配置页面
8. ✅ 商用模式页面
9. ✅ 系统设置页面

## 9. UI 设计规范

### 9.1 颜色规范
- 主色: `#18a058` (绿色)
- 辅助色: `#2080f0` (蓝色)
- 警告色: `#f0a020` (橙色)
- 错误色: `#d03050` (红色)

### 9.2 组件规范
- 卡片圆角: `16px`
- 按钮圆角: `6px`
- 输入框高度: `36px`
- 间距: `12px`, `16px`, `20px`, `24px`

### 9.3 响应式断点
- 移动端: `< 768px`
- 平板: `768px - 1024px`
- 桌面: `> 1024px`

## 10. 下一步行动

1. 创建页面目录结构
2. 实现对话管理页面（优先级最高）
3. 实现知识库页面
4. 实现用户管理页面
5. 实现其他管理页面
6. 添加完整的 i18n 配置
7. 测试权限控制
8. 优化 UI 和交互

---

**文档版本**: v1.0  
**创建日期**: 2025-01-19  
**维护者**: Biomni Team
