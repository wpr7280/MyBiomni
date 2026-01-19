# Frontend 修改说明

## 修改概述

本次修改主要包括三个部分：
1. 移除 layout 右上角的团队选择和创建团队功能
2. 添加首次登录强制修改密码的引导
3. Profile 页面移除 Access Token 管理，添加修改邮箱功能

---

## 1. 移除团队功能

### 修改文件
`src/layout/components/header/index.vue`

### 修改内容
- ❌ 移除 `<TeamSwitcher class="mr-3" />`
- ❌ 移除 `import TeamSwitcher from '@/components/team/TeamSwitcher.vue'`

### 修改前
```vue
<div ml-auto flex items-center>
  <TeamSwitcher class="mr-3" />
  <Languages />
  <ThemeMode />
  <FullScreen />
  <UserAvatar />
</div>
```

### 修改后
```vue
<div ml-auto flex items-center>
  <Languages />
  <ThemeMode />
  <FullScreen />
  <UserAvatar />
</div>
```

---

## 2. 添加首次登录强制修改密码引导

### 2.1 修改 Workbench 页面

**文件**: `src/views/workbench/index.vue`

**新增功能**:
- ✅ 添加强制修改密码提示 Alert
- ✅ 添加跳转到 Profile 页面的按钮
- ✅ 页面加载时检查 `forcePasswordChange` 状态

**新增代码**:
```vue
<!-- 强制修改密码提示 -->
<n-alert 
  v-if="userStore.forcePasswordChange" 
  type="warning" 
  :title="$t('views.workbench.alert_force_password_change_title')"
  closable
  style="margin-bottom: 16px;"
>
  <div>
    <p>{{ $t('views.workbench.alert_force_password_change_message') }}</p>
    <n-button 
      type="primary" 
      size="small" 
      @click="goToProfile"
      style="margin-top: 12px;"
    >
      {{ $t('views.workbench.button_go_to_change_password') }}
    </n-button>
  </div>
</n-alert>
```

### 2.2 修改 User Store

**文件**: `src/store/modules/user/index.js`

**新增内容**:
- ✅ 添加 `forcePasswordChange` getter
- ✅ 在 `getUserInfo()` 中获取 `forcePasswordChange` 字段
- ✅ 添加 `setForcePasswordChange()` action

**新增代码**:
```javascript
getters: {
  // ...
  forcePasswordChange() {
    return this.userInfo?.forcePasswordChange || false
  },
},
actions: {
  async getUserInfo() {
    // ...
    const { id, username, email, avatar, forcePasswordChange } = res.data
    this.userInfo = { id, username, email, avatar, forcePasswordChange }
    // ...
  },
  setForcePasswordChange(value) {
    this.userInfo.forcePasswordChange = value
  },
}
```

---

## 3. Profile 页面修改

### 3.1 移除 Access Token 管理

**文件**: `src/views/profile/index.vue`

**移除内容**:
- ❌ 移除 Access Token 管理卡片
- ❌ 移除 `accessTokens` 相关状态
- ❌ 移除 `loadAccessTokens()` 方法
- ❌ 移除 `generateAccessToken()` 方法
- ❌ 移除 `deleteAccessToken()` 方法
- ❌ 移除 Token 模态框
- ❌ 移除表格列定义
- ❌ 移除 `onMounted` 中的 `loadAccessTokens()` 调用

### 3.2 添加修改邮箱功能

**新增功能**:
- ✅ 邮箱输入框改为可编辑
- ✅ 添加邮箱验证规则
- ✅ 添加 `updateEmail()` 方法
- ✅ 添加邮箱更新按钮

**新增代码**:
```vue
<NFormItem :label="$t('views.profile.label_email')" path="email">
  <div class="username-input-group">
    <NInput
      v-model:value="infoForm.email"
      type="text"
      :placeholder="$t('views.profile.placeholder_email')"
      class="username-input"
    />
    <NButton 
      type="primary" 
      :loading="isLoading" 
      @click="updateEmail"
      class="inline-update-btn"
    >
      {{ $t('common.buttons.update') }}
    </NButton>
  </div>
</NFormItem>
```

```javascript
// 修改邮箱
async function updateEmail() {
  isLoading.value = true
  infoFormRef.value?.validate(async (err) => {
    if (err) {
      isLoading.value = false
      return
    }
    await api
      .updateEmail({ email: infoForm.value.email })
      .then(() => {
        userStore.setUserInfo(infoForm.value)
        isLoading.value = false
        message.success(t('views.profile.message_email_update_success'))
      })
      .catch(() => {
        isLoading.value = false
      })
  })
}
```

### 3.3 添加强制修改密码提示

**新增内容**:
- ✅ 在页面顶部添加错误级别的 Alert
- ✅ 提示用户必须修改密码

**新增代码**:
```vue
<!-- 强制修改密码提示 -->
<n-alert 
  v-if="userStore.forcePasswordChange" 
  type="error" 
  :title="$t('views.profile.alert_must_change_password_title')"
  style="margin-bottom: 20px;"
>
  {{ $t('views.profile.alert_must_change_password_message') }}
</n-alert>
```

### 3.4 修改密码后清除强制修改标记

**新增代码**:
```javascript
async function updatePassword() {
  // ...
  await api.updatePassword(data).then((res) => {
    message.success(res.msg || t('views.profile.message_password_update_success'))
    // 如果是首次修改密码，更新用户状态
    if (userStore.forcePasswordChange) {
      userStore.setForcePasswordChange(false)
    }
    // ...
  })
}
```

---

## 4. 需要添加的国际化文本

### 4.1 Workbench 页面

**文件**: `i18n/messages/cn.json` 和 `en.json`

```json
{
  "views": {
    "workbench": {
      "alert_force_password_change_title": "需要修改密码",
      "alert_force_password_change_message": "为了您的账号安全，首次登录需要修改密码。",
      "button_go_to_change_password": "立即修改密码"
    }
  }
}
```

### 4.2 Profile 页面

```json
{
  "views": {
    "profile": {
      "alert_must_change_password_title": "必须修改密码",
      "alert_must_change_password_message": "首次登录必须修改密码才能继续使用系统。",
      "message_email_required": "请输入邮箱",
      "message_email_invalid": "请输入有效的邮箱地址",
      "message_email_update_success": "邮箱修改成功",
      "message_password_update_success": "密码修改成功",
      "message_password_min_length": "密码长度至少为 8 位"
    }
  }
}
```

---

## 5. 需要添加的后端接口

### 5.1 修改邮箱接口

**文件**: `src/api/index.js` 或相应的 API 文件

```javascript
// 修改邮箱
export function updateEmail(data) {
  return request.put('/api/admin/profile/email', data)
}
```

### 5.2 后端实现

**Controller**:
```java
@PutMapping("/profile/email")
public BaseResult<Void> updateEmail(
    @RequestBody UpdateEmailRequest request,
    @AuthenticationPrincipal AdminVO admin
) {
    adminService.updateEmail(admin.getId(), request.getEmail());
    return BaseResult.success(null);
}
```

**Service**:
```java
public void updateEmail(Integer adminId, String email) {
    // 检查邮箱是否已被使用
    AdminDO existingAdmin = getAdminByEmail(email);
    if (existingAdmin != null && !existingAdmin.getId().equals(adminId)) {
        throw new RuntimeException("邮箱已被使用");
    }
    
    AdminDO admin = new AdminDO();
    admin.setId(adminId);
    admin.setEmail(email);
    admin.setUpdatedAt(new Date());
    adminDAO.updateByPrimaryKeySelective(admin);
    evictAdminCache(String.valueOf(adminId));
}
```

---

## 6. 测试清单

### 6.1 Layout 测试
- [ ] 右上角不再显示团队选择器
- [ ] 其他功能（语言、主题、全屏、用户头像）正常

### 6.2 Workbench 测试
- [ ] 首次登录时显示强制修改密码提示
- [ ] 点击按钮可以跳转到 Profile 页面
- [ ] 修改密码后提示消失

### 6.3 Profile 测试
- [ ] 首次登录时显示错误级别的提示
- [ ] 可以修改用户名
- [ ] 可以修改邮箱
- [ ] 可以修改密码
- [ ] 修改密码后 `forcePasswordChange` 标记被清除
- [ ] 不再显示 Access Token 管理部分

---

## 7. 样式优化

### 7.1 Profile 页面
- ✅ 移除了 Access Token 相关的样式
- ✅ 保留了基本信息和修改密码的样式
- ✅ 响应式设计保持不变

### 7.2 Alert 样式
- ✅ Workbench: 使用 `warning` 类型（黄色）
- ✅ Profile: 使用 `error` 类型（红色）

---

## 8. 后续优化建议

### 8.1 短期
- [ ] 添加邮箱验证码验证（可选）
- [ ] 添加密码强度指示器
- [ ] 添加修改记录日志

### 8.2 长期
- [ ] 添加双因素认证 (2FA)
- [ ] 添加登录设备管理
- [ ] 添加安全日志查看

---

**修改日期**: 2025-01-19  
**修改人**: Biomni Team  
**版本**: v1.2
