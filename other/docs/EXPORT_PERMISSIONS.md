# 对话导出权限说明

## 权限模型

### 角色定义

系统中有两种角色：
- **admin**: 管理员，拥有完全权限
- **user**: 普通用户，只能访问自己的资源

### 导出权限规则

| 角色 | 可导出的对话 | 说明 |
|------|------------|------|
| **admin** | 所有对话 | 管理员可以导出任何用户的对话，用于系统管理、数据备份、问题排查等 |
| **user** | 仅自己的对话 | 普通用户只能导出自己创建的对话，保护其他用户的隐私 |

## 实现细节

### 后端验证逻辑

```java
// ConversationExportService.java
public String exportConversationToMarkdown(
    Integer conversationId, 
    Integer userId, 
    boolean isAdmin,  // 关键参数
    boolean includeImages
) throws Exception {
    ConversationDO conversation = conversationDAO.selectByPrimaryKey(conversationId);
    
    // 权限验证：管理员可以导出任何对话，普通用户只能导出自己的对话
    if (!isAdmin && !conversation.getUserId().equals(userId)) {
        throw new IllegalArgumentException("无权限访问此对话");
    }
    
    // ... 继续导出逻辑
}
```

### Controller 层调用

```java
// ConversationController.java
@PostMapping("/export")
public void exportConversation(
    @Valid @RequestBody ExportConversationRequest request,
    @AuthenticationPrincipal AdminVO currentUser,
    HttpServletResponse response
) {
    String filepath = conversationExportService.exportConversationToMarkdown(
        request.getConversationId(),
        currentUser.getId(),
        currentUser.isAdmin(),  // 从认证信息中获取角色
        request.getIncludeImages()
    );
    // ...
}
```

## 权限验证流程

```
用户请求导出对话
    ↓
验证用户身份（Token）
    ↓
获取用户角色（admin/user）
    ↓
查询对话信息
    ↓
权限检查：
  - 如果是 admin → 允许导出
  - 如果是 user：
    - 对话属于该用户 → 允许导出
    - 对话不属于该用户 → 拒绝（403 Forbidden）
    ↓
执行导出
    ↓
返回文件
```

## 错误处理

### 权限不足 (403 Forbidden)

**场景**: 普通用户尝试导出其他用户的对话

**响应**:
```json
{
  "error": "无权限访问此对话"
}
```

**日志**:
```
WARN: 导出对话权限不足: conversationId=123, userId=2, role=user, error=无权限访问此对话
```

### 对话不存在 (403 Forbidden)

**场景**: 对话 ID 不存在或已被删除

**响应**:
```json
{
  "error": "对话不存在"
}
```

## 安全考虑

### 1. 防止越权访问

- 始终验证用户对资源的所有权
- 管理员权限需要明确的角色标识
- 不依赖前端传递的权限信息

### 2. 审计日志

所有导出操作都会记录日志：

```java
// 成功导出
log.info("对话导出成功: conversationId={}, userId={}, role={}", 
    conversationId, userId, role);

// 权限不足
log.warn("导出对话权限不足: conversationId={}, userId={}, role={}, error={}", 
    conversationId, userId, role, errorMessage);
```

### 3. 敏感信息保护

- 导出文件包含完整对话内容，需要严格的权限控制
- 临时文件在下载后立即删除
- 定期清理过期的导出文件

## 测试场景

### 场景 1: 普通用户导出自己的对话 ✅

```java
// userId = 1, conversationOwnerId = 1, isAdmin = false
exportService.exportConversationToMarkdown(conversationId, 1, false, true);
// 结果: 成功导出
```

### 场景 2: 普通用户尝试导出其他用户的对话 ❌

```java
// userId = 2, conversationOwnerId = 1, isAdmin = false
exportService.exportConversationToMarkdown(conversationId, 2, false, true);
// 结果: IllegalArgumentException("无权限访问此对话")
```

### 场景 3: 管理员导出任何用户的对话 ✅

```java
// adminUserId = 1, conversationOwnerId = 2, isAdmin = true
exportService.exportConversationToMarkdown(conversationId, 1, true, true);
// 结果: 成功导出（即使对话不属于管理员）
```

### 场景 4: 管理员导出自己的对话 ✅

```java
// adminUserId = 1, conversationOwnerId = 1, isAdmin = true
exportService.exportConversationToMarkdown(conversationId, 1, true, true);
// 结果: 成功导出
```

## 最佳实践

### 1. 前端处理

前端应该：
- 只显示用户有权限导出的对话
- 对于管理员，可以在管理后台提供批量导出功能
- 提供清晰的权限错误提示

### 2. 后端处理

后端必须：
- 始终在服务层验证权限，不信任前端
- 记录所有导出操作的审计日志
- 对敏感操作（管理员导出其他用户对话）进行特别记录

### 3. 监控告警

建议监控：
- 频繁的权限拒绝（可能是攻击尝试）
- 管理员的导出操作（审计需要）
- 异常的大量导出请求

## 扩展建议

### 1. 更细粒度的权限

可以考虑添加：
- **viewer**: 只读用户，可以查看但不能导出
- **team_admin**: 团队管理员，可以导出团队成员的对话
- **super_admin**: 超级管理员，拥有所有权限

### 2. 导出审批流程

对于敏感场景，可以添加：
- 管理员导出其他用户对话需要审批
- 批量导出需要二次确认
- 导出操作需要提供理由

### 3. 数据脱敏

对于某些场景，可以：
- 导出时自动脱敏敏感信息
- 提供"匿名导出"选项
- 根据用户角色决定导出内容的详细程度

## 相关文档

- [导出功能实现文档](./EXPORT_FEATURE.md)
- [快速使用指南](./EXPORT_QUICK_GUIDE.md)
- [API 接口文档](./API接口文档.md)
