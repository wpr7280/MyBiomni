# 基于角色的访问控制 (RBAC) 实现

## 概述

系统使用统一的 `admin` 表存储所有用户，通过 `role` 字段区分管理员和普通用户，实现基于角色的访问控制。

## 1. 角色定义

### 1.1 角色类型

| 角色 | 代码 | 说明 | 权限 |
|------|------|------|------|
| 管理员 | `admin` | 系统管理员 | 所有功能 |
| 普通用户 | `user` | 普通用户 | 基础功能 |

### 1.2 角色枚举

**文件**: `common/constant/UserRole.java`

```java
public enum UserRole {
    ADMIN("admin", "管理员"),
    USER("user", "普通用户");
    
    public static boolean isAdmin(String code) {
        return ADMIN.code.equals(code);
    }
    
    public static boolean canAccessAdmin(String code) {
        return ADMIN.code.equals(code);
    }
}
```

## 2. 数据库设计

### 2.1 admin 表结构

```sql
CREATE TABLE `admin` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(50) NOT NULL,
  `password` VARCHAR(255) NOT NULL,
  `email` VARCHAR(100) NOT NULL,
  `role` VARCHAR(20) NOT NULL DEFAULT 'user',  -- 新增字段
  `status` INT NOT NULL DEFAULT 1,
  -- ... 其他字段
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_admin_email` (`email`),
  KEY `idx_admin_role` (`role`)  -- 新增索引
);
```

### 2.2 添加 role 字段

```bash
mysql -u root -p biomni_app < add_role_column.sql
```

## 3. 后端实现

### 3.1 认证流程

```
登录 → 验证密码 → 生成 JWT Token → 返回用户信息（包含 role）
     ↓
后续请求 → TokenAuthFilter 验证 Token → 提取用户信息 → 根据 role 设置权限
     ↓
Controller → @RequireRole 注解检查 → RoleCheckInterceptor 验证 → 执行业务逻辑
```

### 3.2 TokenAuthFilter 修改

**文件**: `common/interceptor/TokenAuthFilter.java`

```java
private void setAdminContext(String adminId, String email, String token) {
    AdminVO admin = adminService.getAdminInfo(adminId);
    admin.setToken(token);
    
    // 根据角色设置 Spring Security 权限
    String role = admin.getRole() != null ? admin.getRole() : "user";
    String springRole = "ROLE_" + role.toUpperCase();  // ROLE_ADMIN 或 ROLE_USER
    
    UsernamePasswordAuthenticationToken authentication = new UsernamePasswordAuthenticationToken(
        admin, 
        token, 
        Collections.singletonList(new SimpleGrantedAuthority(springRole))
    );
    SecurityContextHolder.getContext().setAuthentication(authentication);
}
```

### 3.3 权限控制方式

#### 方式 1: 使用 @RequireRole 注解（推荐）

```java
@RestController
@RequestMapping("/api/admin/users")
@RequireRole("admin")  // 整个 Controller 只有管理员可以访问
public class AdminUserController {
    
    @GetMapping
    public BaseResult<List<User>> getUserList() {
        // 只有管理员可以访问
    }
}
```

#### 方式 2: 使用 Spring Security 注解

```java
@PreAuthorize("hasRole('ADMIN')")
@GetMapping("/api/admin/config")
public BaseResult<Config> getConfig() {
    // 只有管理员可以访问
}

@PreAuthorize("hasAnyRole('ADMIN', 'USER')")
@GetMapping("/api/conversations")
public BaseResult<List<Conversation>> getConversations() {
    // 管理员和用户都可以访问
}
```

#### 方式 3: 在代码中手动检查

```java
@GetMapping("/api/admin/users")
public BaseResult<List<User>> getUserList(@AuthenticationPrincipal AdminVO currentUser) {
    // 手动检查权限
    if (!currentUser.isAdmin()) {
        return BaseResult.error("权限不足");
    }
    // 业务逻辑
}
```

### 3.4 菜单控制

**文件**: `controller/menu/MenuController.java`

```java
@RequestMapping("/list")
public BaseResult<List<BaseMenu>> getUserMenu(@AuthenticationPrincipal AdminVO currentUser) {
    // 根据角色返回不同菜单
    if (UserRole.isAdmin(currentUser.getRole())) {
        return ResultConvert.initSuccess(ADMIN_MENUS);  // 管理员菜单
    } else {
        return ResultConvert.initSuccess(USER_MENUS);   // 用户菜单
    }
}
```

## 4. 菜单设计

### 4.1 管理员菜单

```
工作台 (/workbench)
我的对话 (/conversations)
知识库 (/knowhow)
系统管理 (/system)
  ├─ 用户管理 (/system/users)
  ├─ 配额管理 (/system/quota)
  ├─ 对话记录 (/system/conversations)
  └─ 文档管理 (/system/knowhow)
系统配置 (/config)
  ├─ 模型配置 (/config/model)
  ├─ 商用模式 (/config/commercial)
  └─ 系统设置 (/config/system)
```

### 4.2 普通用户菜单

```
工作台 (/workbench)
我的对话 (/conversations)
知识库 (/knowhow)
```

## 5. 前端实现

### 5.1 更新 User Store

**文件**: `store/modules/user/index.js`

```javascript
getters: {
  role() {
    return this.userInfo?.role || 'user'
  },
  isAdmin() {
    return this.userInfo?.role === 'admin'
  },
  canAccessAdmin() {
    return this.userInfo?.role === 'admin'
  },
},
actions: {
  async getUserInfo() {
    const res = await api.getUserInfo()
    const { id, username, email, avatar, role, forcePasswordChange } = res.data
    this.userInfo = { id, username, email, avatar, role, forcePasswordChange }
  }
}
```

### 5.2 路由守卫

```javascript
// router/guard/permission.js
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  const requiredRoles = to.meta.roles
  
  if (requiredRoles && requiredRoles.length > 0) {
    if (requiredRoles.includes(userStore.role)) {
      next()
    } else {
      next('/403')  // 无权限
    }
  } else {
    next()
  }
})
```

### 5.3 组件权限控制

```vue
<template>
  <!-- 只有管理员可见 -->
  <div v-if="userStore.isAdmin">
    <n-button @click="goToAdminPanel">管理后台</n-button>
  </div>
  
  <!-- 所有人可见 -->
  <div>
    <n-button @click="createConversation">创建对话</n-button>
  </div>
</template>

<script setup>
import { useUserStore } from '@/store'
const userStore = useUserStore()
</script>
```

## 6. API 接口权限

### 6.1 公开接口（无需认证）

```
POST /api/auth/login          - 登录
POST /api/auth/register       - 注册（如果开放）
POST /api/auth/sendEmail      - 发送邮件
POST /api/auth/resetPassword  - 重置密码
```

### 6.2 认证接口（需要登录）

```
GET  /api/auth/me             - 获取当前用户信息
POST /api/auth/logout         - 登出
POST /api/auth/updatePassword - 修改密码
POST /api/auth/updateUserInfo - 更新用户信息
GET  /api/menu/list           - 获取菜单（根据角色返回）
```

### 6.3 管理员接口（需要 admin 角色）

```
GET    /api/admin/users              - 用户列表
POST   /api/admin/users              - 创建用户
PUT    /api/admin/users/{id}         - 更新用户
DELETE /api/admin/users/{id}         - 删除用户
GET    /api/admin/config/*           - 系统配置
PUT    /api/admin/config/*           - 更新配置
GET    /api/admin/conversations      - 所有对话记录
GET    /api/admin/knowhow            - 文档管理
```

### 6.4 用户接口（admin 和 user 都可访问）

```
GET    /api/conversations            - 我的对话列表
POST   /api/conversations            - 创建对话
GET    /api/conversations/{id}       - 对话详情
DELETE /api/conversations/{id}       - 删除对话
GET    /api/knowhow                  - 浏览文档
GET    /api/profile                  - 个人信息
```

## 7. 使用示例

### 7.1 Controller 示例

```java
// 示例 1: 管理员专用接口
@RestController
@RequestMapping("/api/admin/config")
@RequireRole("admin")
public class ConfigController {
    
    @GetMapping("/model")
    public BaseResult<ModelConfig> getModelConfig() {
        // 只有管理员可以访问
    }
}

// 示例 2: 所有人可访问的接口
@RestController
@RequestMapping("/api/conversations")
public class ConversationController {
    
    @GetMapping
    public BaseResult<List<Conversation>> getMyConversations(
        @AuthenticationPrincipal AdminVO currentUser
    ) {
        // 管理员和用户都可以访问
        // 但只能看到自己的对话
    }
}

// 示例 3: 混合权限
@RestController
@RequestMapping("/api/conversations")
public class ConversationController {
    
    // 所有人可以访问
    @GetMapping
    public BaseResult<List<Conversation>> getMyConversations() {
        // ...
    }
    
    // 只有管理员可以访问
    @RequireRole("admin")
    @GetMapping("/all")
    public BaseResult<List<Conversation>> getAllConversations() {
        // 查看所有用户的对话
    }
}
```

## 8. 测试

### 8.1 测试账号

| 用户名 | 密码 | 角色 | 说明 |
|--------|------|------|------|
| admin | admin123 | admin | 管理员，可以访问所有功能 |
| user001 | user123 | user | 普通用户，只能使用基础功能 |

### 8.2 测试用例

#### 测试 1: 管理员登录并访问管理功能

```bash
# 1. 登录
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@biomni.com","password":"admin123"}'

# 响应包含 role: "admin"

# 2. 获取菜单（应该返回管理员菜单）
curl -X GET http://localhost:8080/api/menu/list \
  -H "Authorization: Bearer <token>"

# 3. 访问用户管理（应该成功）
curl -X GET http://localhost:8080/api/admin/users \
  -H "Authorization: Bearer <token>"
```

#### 测试 2: 普通用户登录并尝试访问管理功能

```bash
# 1. 登录
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user001@example.com","password":"user123"}'

# 响应包含 role: "user"

# 2. 获取菜单（应该返回用户菜单）
curl -X GET http://localhost:8080/api/menu/list \
  -H "Authorization: Bearer <token>"

# 3. 访问用户管理（应该返回 403 权限不足）
curl -X GET http://localhost:8080/api/admin/users \
  -H "Authorization: Bearer <token>"

# 响应: {"code":403,"message":"权限不足"}
```

## 9. 权限矩阵

| 功能 | 路径 | admin | user |
|------|------|-------|------|
| 登录 | POST /api/auth/login | ✅ | ✅ |
| 获取个人信息 | GET /api/auth/me | ✅ | ✅ |
| 修改密码 | POST /api/auth/updatePassword | ✅ | ✅ |
| 更新个人信息 | POST /api/auth/updateUserInfo | ✅ | ✅ |
| 获取菜单 | GET /api/menu/list | ✅ | ✅ |
| 创建对话 | POST /api/conversations | ✅ | ✅ |
| 我的对话列表 | GET /api/conversations | ✅ | ✅ |
| 浏览文档 | GET /api/knowhow | ✅ | ✅ |
| 用户管理 | /api/admin/users/* | ✅ | ❌ |
| 配额管理 | /api/admin/quota/* | ✅ | ❌ |
| 所有对话记录 | GET /api/admin/conversations | ✅ | ❌ |
| 文档管理 | /api/admin/knowhow/* | ✅ | ❌ |
| 系统配置 | /api/admin/config/* | ✅ | ❌ |

## 10. 实现文件清单

### 10.1 新增文件

- ✅ `common/annotation/RequireRole.java` - 角色权限注解
- ✅ `common/interceptor/RoleCheckInterceptor.java` - 角色检查拦截器
- ✅ `config/WebMvcConfig.java` - Web MVC 配置
- ✅ `controller/admin/AdminUserController.java` - 用户管理示例

### 10.2 修改文件

- ✅ `controller/auth/AuthController.java` - 添加 role 返回
- ✅ `controller/auth/LoginResponse.java` - 添加 role 字段
- ✅ `controller/auth/AdminVO.java` - 添加 role 字段和权限判断方法
- ✅ `controller/menu/MenuController.java` - 根据角色返回菜单
- ✅ `service/AuthService.java` - 登录时返回 role
- ✅ `service/AdminService.java` - 读取 role 字段
- ✅ `common/interceptor/TokenAuthFilter.java` - 根据 role 设置权限
- ✅ `common/constant/AdminRole.java` → `UserRole.java` - 更新角色枚举

### 10.3 SQL 文件

- ✅ `add_role_column.sql` - 添加 role 字段
- ✅ `create_admin_table.sql` - 创建包含 role 的表
- ✅ `ROLE_MIGRATION.md` - 迁移指南
- ✅ `QUICK_REFERENCE.md` - 快速参考

## 11. 部署步骤

### 11.1 数据库迁移

```bash
# 1. 备份数据
mysqldump -u root -p biomni_app admin > admin_backup.sql

# 2. 添加 role 字段
mysql -u root -p biomni_app < add_role_column.sql

# 3. 验证
mysql -u root -p biomni_app -e "SELECT id, username, email, role FROM admin;"
```

### 11.2 代码部署

```bash
# 1. 拉取最新代码
git pull

# 2. 编译
cd admin/backend
mvn clean package

# 3. 重启服务
# Docker: docker-compose restart backend
# 或直接运行: java -jar target/mybiomni-backend.jar
```

### 11.3 验证

1. ✅ 管理员登录，检查返回的 role 是否为 "admin"
2. ✅ 管理员获取菜单，检查是否包含管理功能
3. ✅ 普通用户登录，检查返回的 role 是否为 "user"
4. ✅ 普通用户获取菜单，检查是否只有基础功能
5. ✅ 普通用户访问管理接口，检查是否返回 403

## 12. 常见问题

### Q1: 用户登录后看不到菜单

**A**: 检查 role 字段是否正确设置

```sql
SELECT id, username, email, role FROM admin WHERE email = 'xxx@email.com';
```

### Q2: 管理员无法访问管理功能

**A**: 检查 role 是否为 'admin'

```sql
UPDATE admin SET role = 'admin' WHERE id = 1;
```

### Q3: 权限检查不生效

**A**: 确保 `RoleCheckInterceptor` 已注册到 `WebMvcConfig`

### Q4: 如何将用户升级为管理员

**A**: 
```sql
UPDATE admin SET role = 'admin' WHERE id = 2;
```

## 13. 安全建议

1. ✅ 定期审计管理员账号
2. ✅ 记录所有权限变更操作
3. ✅ 限制管理员数量
4. ✅ 使用强密码策略
5. ✅ 启用登录失败锁定
6. ✅ 记录所有敏感操作日志

---

**文档版本**: v1.0  
**最后更新**: 2025-01-19  
**维护者**: Biomni Team
