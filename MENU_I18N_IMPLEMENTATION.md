# 菜单国际化实现方案

## 🎯 推荐方案：前端映射表

### 优势
- ✅ 无需修改后端代码
- ✅ 实现简单快速
- ✅ 对现有代码影响最小
- ✅ 支持动态语言切换

---

## 📝 实现步骤

### 1. 添加菜单翻译到 cn.json

```json
{
  "menu": {
    "workbench": "工作台",
    "system_management": "系统管理",
    "user_management": "用户管理",
    "conversation_records": "对话记录",
    "system_config": "系统配置",
    "model_config": "模型配置",
    "commercial_mode": "商用模式",
    "system_settings": "系统设置"
  }
}
```

### 2. 添加英文翻译到 en.json

```json
{
  "menu": {
    "workbench": "Workbench",
    "system_management": "System Management",
    "user_management": "User Management",
    "conversation_records": "Conversation Records",
    "system_config": "System Configuration",
    "model_config": "Model Configuration",
    "commercial_mode": "Commercial Mode",
    "system_settings": "System Settings"
  }
}
```

### 3. 创建菜单翻译工具函数

```javascript
// admin/frontend/src/utils/menu-i18n.js
export const menuNameMap = {
  '工作台': 'menu.workbench',
  '系统管理': 'menu.system_management',
  '用户管理': 'menu.user_management',
  '对话记录': 'menu.conversation_records',
  '系统配置': 'menu.system_config',
  '模型配置': 'menu.model_config',
  '商用模式': 'menu.commercial_mode',
  '系统设置': 'menu.system_settings'
}

export function translateMenuName(name, t) {
  const key = menuNameMap[name]
  return key ? t(key) : name
}

export function translateMenu(menu, t) {
  return {
    ...menu,
    name: translateMenuName(menu.name, t),
    children: menu.children?.map(child => translateMenu(child, t))
  }
}
```

### 4. 在路由生成时使用

```javascript
// admin/frontend/src/store/modules/permission/index.js
import { translateMenu } from '@/utils/menu-i18n'
import { useI18n } from 'vue-i18n'

// 在生成路由时
const { t } = useI18n()
const translatedMenus = menus.map(menu => translateMenu(menu, t))
```

---

## 🔄 语言切换

当用户切换语言时，菜单会自动更新：

```javascript
// 监听语言变化
watch(() => locale.value, () => {
  // 重新生成路由
  permissionStore.generateRoutes()
})
```

---

## 💡 替代方案：后端返回翻译键

如果你想要更彻底的解决方案，可以修改后端：

### 后端修改

```java
// MenuController.java
BaseMenu system = menu(10, "menu.system_management", "/system", ...);
```

### 前端处理

```javascript
// 直接使用 t() 翻译
menu.name = t(menu.name)
```

**优点**：
- ✅ 更规范
- ✅ 后端不包含中文

**缺点**：
- ❌ 需要修改后端
- ❌ 需要重新编译部署

---

## 🎯 建议

**当前阶段**：使用方案 C（前端映射表）
- 快速实现
- 无需修改后端
- 立即可用

**长期优化**：考虑方案 A（后端返回翻译键）
- 更规范
- 更易维护

---

**文档版本**: v1.0  
**创建时间**: 2025-01-20  
**状态**: 方案设计，待实现
