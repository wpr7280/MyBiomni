# 用户管理 API 文档

## 概述

用户管理功能允许管理员创建、编辑、删除和查询用户。所有用户存储在 `admin` 表中，通过 `role` 字段区分权限。

## 1. 获取用户列表

### 接口
`GET /api/admin/users`

### 权限
仅管理员可访问（`@RequireRole("admin")`）

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| currentPage | Integer | 否 | 当前页码，默认 1 |
| pageSize | Integer | 否 | 每页数量，默认 10 |
| keyword | String | 否 | 搜索关键词（用户名或邮箱） |
| role | String | 否 | 角色筛选（admin/user） |
| status | Integer | 否 | 状态筛选（0-禁用/1-启用） |

### 请求示例
```bash
GET /api/admin/users?currentPage=1&pageSize=20&keyword=test&role=user&status=1
```

### 响应示例
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "username": "user001",
        "email": "user001@example.com",
        "phone": null,
        "realName": "测试用户",
        "avatar": null,
        "role": "user",
        "status": 1,
        "lastLoginAt": "2025-01-19T10:30:00",
        "createdAt": "2025-01-18T00:00:00"
      }
    ],
    "total": 100,
    "page": 1,
    "pageSize": 20
  }
}
```

## 2. 创建用户

### 接口
`POST /api/admin/users`

### 权限
仅管理员可访问

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | String | 是 | 用户名 |
| email | String | 是 | 邮箱（唯一） |
| password | String | 否 | 密码，为空则使用邮箱前缀 |
| realName | String | 否 | 真实姓名 |
| role | String | 否 | 角色，默认 'user' |
| status | Integer | 否 | 状态，默认 1（启用） |

### 请求示例
```json
{
  "username": "user002",
  "email": "user002@example.com",
  "password": "",
  "realName": "张三",
  "role": "user",
  "status": 1
}
```

### 密码规则
- 如果提供了 `password`，使用提供的密码
- 如果 `password` 为空，自动使用邮箱前缀作为密码
  - 例如：`user002@example.com` → 密码为 `user002`
- 所有新创建的用户 `force_password_change` 设置为 1（首次登录需要修改密码）

### 响应示例
```json
{
  "code": 200,
  "message": "success",
  "data": 2
}
```

## 3. 更新用户

### 接口
`PUT /api/admin/users/{id}`

### 权限
仅管理员可访问

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | String | 否 | 用户名 |
| email | String | 否 | 邮箱 |
| realName | String | 否 | 真实姓名 |
| role | String | 否 | 角色（admin/user） |
| status | Integer | 否 | 状态（0-禁用/1-启用） |

### 请求示例
```json
{
  "username": "user002_updated",
  "email": "user002_new@example.com",
  "realName": "张三",
  "role": "admin",
  "status": 1
}
```

### 功能说明
- 只更新提供的字段
- 邮箱会进行唯一性检查
- 更新后自动清除缓存

### 响应示例
```json
{
  "code": 200,
  "message": "success",
  "data": null
}
```

## 4. 删除用户

### 接口
`DELETE /api/admin/users/{id}`

### 权限
仅管理员可访问

### 请求示例
```bash
DELETE /api/admin/users/2
```

### 功能说明
- 软删除（设置 `deleted_at` 字段）
- 不会真正删除数据
- 删除后自动清除缓存

### 响应示例
```json
{
  "code": 200,
  "message": "success",
  "data": null
}
```

## 5. 错误码

| 错误码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 403 | 权限不足（非管理员） |
| 404 | 用户不存在 |
| 500 | 服务器错误 |

### 常见错误

| 错误信息 | 原因 | 解决方案 |
|---------|------|---------|
| 邮箱已被使用 | 邮箱重复 | 使用其他邮箱 |
| 用户不存在 | ID 不存在或已删除 | 检查用户 ID |
| 权限不足 | 非管理员访问 | 使用管理员账号 |

## 6. 使用示例

### 6.1 创建普通用户

```bash
curl -X POST http://localhost:8080/api/admin/users \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user003",
    "email": "user003@example.com",
    "realName": "李四",
    "role": "user",
    "status": 1
  }'
```

**结果**: 
- 用户名: `user003`
- 邮箱: `user003@example.com`
- 密码: `user003`（自动使用邮箱前缀）
- 首次登录需要修改密码

### 6.2 创建管理员

```bash
curl -X POST http://localhost:8080/api/admin/users \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin2",
    "email": "admin2@biomni.com",
    "password": "Admin@123",
    "realName": "管理员2",
    "role": "admin",
    "status": 1
  }'
```

### 6.3 将用户升级为管理员

```bash
curl -X PUT http://localhost:8080/api/admin/users/2 \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "admin"
  }'
```

### 6.4 禁用用户

```bash
curl -X PUT http://localhost:8080/api/admin/users/2 \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "status": 0
  }'
```

### 6.5 搜索用户

```bash
curl -X GET "http://localhost:8080/api/admin/users?keyword=user&currentPage=1&pageSize=20" \
  -H "Authorization: Bearer <token>"
```

## 7. 前端集成

### 7.1 API 调用

```javascript
// 获取用户列表
const res = await api.getUserList({
  currentPage: 1,
  pageSize: 20,
  keyword: 'test',
  role: 'user',
  status: 1
})

// 创建用户
const res = await api.createUser({
  username: 'user003',
  email: 'user003@example.com',
  realName: '李四',
  role: 'user',
  status: 1
})

// 更新用户
const res = await api.updateUser(userId, {
  role: 'admin',
  status: 1
})

// 删除用户
const res = await api.deleteUser(userId)
```

### 7.2 响应处理

```javascript
if (res.code === 200) {
  message.success('操作成功')
  loadUsers()  // 刷新列表
} else {
  message.error(res.message || '操作失败')
}
```

## 8. 数据库操作

### 8.1 查看所有用户

```sql
SELECT 
  id, username, email, real_name, role, status, 
  force_password_change, created_at
FROM admin
WHERE deleted_at IS NULL
ORDER BY created_at DESC;
```

### 8.2 查看管理员

```sql
SELECT id, username, email, role, status
FROM admin
WHERE role = 'admin' AND deleted_at IS NULL;
```

### 8.3 查看普通用户

```sql
SELECT id, username, email, role, status
FROM admin
WHERE role = 'user' AND deleted_at IS NULL;
```

### 8.4 手动创建用户

```sql
INSERT INTO admin (username, password, email, real_name, role, status, force_password_change)
VALUES (
  'user004',
  '$2a$10$dXJ3SW6G7P50lGmMkkmwe.20cQQubK3.HZWzG3YB1tlRy.fqvM/BG',  -- user123
  'user004@example.com',
  '王五',
  'user',
  1,
  1
);
```

## 9. 测试清单

- [ ] 管理员可以访问用户管理页面
- [ ] 普通用户无法访问用户管理页面（403）
- [ ] 用户列表正常加载
- [ ] 分页功能正常
- [ ] 搜索功能正常
- [ ] 创建用户成功（密码为空时使用邮箱前缀）
- [ ] 创建用户成功（提供密码）
- [ ] 邮箱重复时提示错误
- [ ] 更新用户信息成功
- [ ] 修改角色成功
- [ ] 禁用用户成功
- [ ] 删除用户成功（软删除）
- [ ] 新创建的用户首次登录需要修改密码

---

**文档版本**: v1.0  
**最后更新**: 2025-01-19  
**维护者**: Biomni Team
