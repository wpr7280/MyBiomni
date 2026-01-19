# Admin Backend API 总结

## 认证相关接口

### 1. 登录
**接口**: `POST /api/auth/login`

**请求参数**:
```json
{
  "email": "admin@biomni.com",
  "password": "admin123"
}
```

**响应**:
```json
{
  "code": 200,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "userId": "1",
    "email": "admin@biomni.com",
    "username": "admin",
    "forcePasswordChange": true
  }
}
```

### 2. 获取当前用户信息
**接口**: `GET /api/auth/me`

**请求头**:
```
Authorization: Bearer <token>
```

**响应**:
```json
{
  "code": 200,
  "data": {
    "token": "...",
    "userId": "1",
    "email": "admin@biomni.com",
    "username": "admin"
  }
}
```

### 3. 登出
**接口**: `POST /api/auth/logout`

**请求头**:
```
Authorization: Bearer <token>
```

**响应**:
```json
{
  "code": 200,
  "data": null
}
```

### 4. 修改密码
**接口**: `POST /api/auth/updatePassword`

**请求头**:
```
Authorization: Bearer <token>
```

**请求参数**:
```json
{
  "oldPassword": "admin123",
  "newPassword": "NewPassword@123"
}
```

**响应**:
```json
{
  "code": 200,
  "data": true
}
```

**功能**:
- ✅ 验证原密码
- ✅ 更新为新密码
- ✅ 如果是首次修改，清除 `force_password_change` 标记
- ✅ 清除缓存

### 5. 更新用户信息 (新增)
**接口**: `POST /api/auth/updateUserInfo`

**请求头**:
```
Authorization: Bearer <token>
```

**请求参数**:
```json
{
  "username": "新用户名",
  "email": "new@email.com"
}
```

**说明**:
- 两个字段都是可选的
- 可以只更新其中一个字段
- 邮箱会进行唯一性检查

**响应**:
```json
{
  "code": 200,
  "data": null
}
```

**错误响应**:
```json
{
  "code": 400,
  "message": "邮箱已被使用"
}
```

### 6. 重置密码
**接口**: `POST /api/auth/resetPassword`

**请求参数**:
```json
{
  "email": "admin@biomni.com",
  "verifyCode": "123456",
  "newPassword": "NewPassword@123"
}
```

**说明**: 需要先通过邮箱验证码验证

**响应**:
```json
{
  "code": 200,
  "data": true
}
```

## 实现细节

### 认证流程

```
1. 用户登录 → 验证邮箱密码 → 生成 JWT Token
2. 后续请求携带 Token → TokenAuthFilter 验证 → 提取管理员信息 → 设置到 SecurityContext
3. Controller 通过 @AuthenticationPrincipal AdminVO 获取当前管理员
```

### 使用的枚举类

#### AdminStatus
```java
DISABLED(0, "禁用")
ACTIVE(1, "启用")
```

#### ForcePasswordChange
```java
NO(0, "不需要")
YES(1, "需要强制修改")
```

### 缓存策略

- 管理员信息缓存 10 分钟
- 更新信息后自动清除缓存
- 使用 Guava Cache

### 安全特性

1. ✅ 密码使用 BCrypt 加密
2. ✅ JWT Token 认证
3. ✅ 账号锁定机制
4. ✅ 强制修改密码
5. ✅ 邮箱唯一性验证
6. ✅ 登录失败次数记录

## 数据库字段映射

### admin 表
```sql
id                    INT           管理员ID
username              VARCHAR(50)   用户名
password              VARCHAR(255)  密码(BCrypt)
email                 VARCHAR(100)  邮箱
phone                 VARCHAR(20)   手机号
real_name             VARCHAR(50)   真实姓名
avatar                VARCHAR(255)  头像URL
status                INT           状态: 0-禁用, 1-启用
last_login_at         DATETIME      最后登录时间
last_login_ip         VARCHAR(50)   最后登录IP
login_fail_count      INT           登录失败次数
locked_until          DATETIME      锁定截止时间
force_password_change INT           强制修改密码: 0-否, 1-是
created_at            DATETIME      创建时间
updated_at            DATETIME      更新时间
deleted_at            DATETIME      删除时间
```

## 测试用例

### 1. 登录测试
```bash
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@biomni.com",
    "password": "admin123"
  }'
```

### 2. 获取用户信息
```bash
curl -X GET http://localhost:8080/api/auth/me \
  -H "Authorization: Bearer <token>"
```

### 3. 更新用户信息
```bash
curl -X POST http://localhost:8080/api/auth/updateUserInfo \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "新用户名",
    "email": "new@email.com"
  }'
```

### 4. 修改密码
```bash
curl -X POST http://localhost:8080/api/auth/updatePassword \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "oldPassword": "admin123",
    "newPassword": "NewPassword@123"
  }'
```

## 常见问题

### Q1: 更新邮箱时提示"邮箱已被使用"
**A**: 检查数据库中是否有其他管理员使用了该邮箱

```sql
SELECT id, username, email FROM admin WHERE email = 'xxx@email.com';
```

### Q2: 修改密码后仍然提示需要修改密码
**A**: 检查 `force_password_change` 字段是否被正确清除

```sql
SELECT id, username, force_password_change FROM admin WHERE id = 1;
```

### Q3: Token 验证失败
**A**: 检查 Token 是否过期，或者 JWT secret 是否正确配置

---

**文档版本**: v1.0  
**最后更新**: 2025-01-19  
**维护者**: Biomni Team
