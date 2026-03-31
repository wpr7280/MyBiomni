# 对话导出功能实现文档

## 功能概述

实现了将对话历史导出为 Markdown 格式的功能，包括：
- 用户和 AI 的完整对话内容
- 执行步骤详情（工具调用、输入输出）
- 图片和附件的嵌入
- 元数据信息（Token 消耗、时间戳等）

## 技术架构

### 后端实现

#### 1. ConversationExportService
**位置**: `admin/backend/src/main/java/com/qusu/mybiomni/service/ConversationExportService.java`

**核心方法**:
- `exportConversationToMarkdown()`: 主导出方法
- `generateMarkdownContent()`: 生成 Markdown 内容
- `appendMessageToMarkdown()`: 添加消息到 Markdown
- `appendExecutionSteps()`: 添加执行步骤
- `processImagesInOutput()`: 处理图片数据
- `saveBase64Image()`: 保存 base64 图片
- `cleanupOldExports()`: 清理过期文件

**特性**:
- 权限验证：确保用户只能导出自己的对话
- 图片处理：支持 base64 图片提取和保存
- 文件管理：自动创建导出目录，支持定期清理
- 格式化：JSON 格式化、状态 emoji、时间格式化

#### 2. ConversationController
**位置**: `admin/backend/src/main/java/com/qusu/mybiomni/controller/conversation/ConversationController.java`

**新增端点**:
```java
POST /api/conversations/export
Request Body: {
  "conversationId": 123,
  "includeImages": true
}
Response: Binary file stream (Markdown)
```

**实现细节**:
- 使用 `HttpServletResponse` 直接返回文件流
- 设置正确的 Content-Type 和 Content-Disposition
- 导出后自动删除临时文件

### 前端实现

#### 1. API 层
**位置**: `client/frontend/src/api/conversation.ts`

**新增方法**:
```typescript
async exportConversation(conversationId: number, includeImages = true): Promise<void>
```

**特性**:
- 使用 `responseType: 'blob'` 接收二进制数据
- 自动创建下载链接并触发下载
- 支持 Mock 模式测试

#### 2. UI 组件
**位置**: `client/frontend/src/components/ChatWindow.tsx`

**集成方式**:
- 在导出下拉菜单中添加 "Export as Markdown" 选项
- 点击时调用 API 并显示加载/成功/失败提示
- 使用 antd Message 组件提供用户反馈

#### 3. 国际化
**文件**: 
- `client/frontend/src/i18n/locales/en-US.json`
- `client/frontend/src/i18n/locales/zh-CN.json`

**新增翻译**:
- `chat.exportMarkdown`: 导出按钮文本
- `chat.exporting`: 导出中提示
- `chat.exportSuccess`: 导出成功提示
- `chat.exportFailed`: 导出失败提示

## Markdown 格式示例

```markdown
# Conversation Title

---

**Conversation ID:** 123
**Created:** 2025-01-27 10:30:00
**Status:** active
**Total Messages:** 10
**Total Tokens:** 5000

---

## 👤 User Message #1

**Time:** 2025-01-27 10:30:15

### Content

How do I design CRISPR sgRNA?

---

## 🤖 Assistant Message #2

**Time:** 2025-01-27 10:30:45
**Tokens:** 450 (Input: 50, Output: 400)

### Content

I'll help you design CRISPR sgRNA...

### 🔧 Execution Steps

#### Step 1: search_literature

**Status:** ✅ success
**Tool:** `search_pubmed`

**Input:**
```json
{
  "query": "CRISPR sgRNA design",
  "max_results": 10
}
```

**Output:**
```
Found 10 relevant papers...
```

**Duration:** 1250 ms

---

*Exported from WarpHelix - 2025-01-27 11:00:00*
```

## 数据库依赖

使用现有表结构：
- `conversations`: 对话基本信息
- `messages`: 消息内容
- `execution_steps`: 执行步骤详情

## 文件存储

**导出目录**: `exports/conversations/`
**图片目录**: `exports/conversations/images/`

**文件命名**:
- Markdown: `conversation_{id}_{timestamp}.md`
- 图片: `image_{timestamp}.{ext}`

## 安全考虑

1. **权限验证**: 
   - **管理员 (admin)**: 可以导出任何用户的对话
   - **普通用户 (user)**: 只能导出自己的对话
   - 验证用户对对话的所有权或管理员权限
2. **路径安全**: 使用 Java NIO 防止路径遍历攻击
3. **文件清理**: 定期清理过期导出文件（可配置）
4. **大小限制**: 可添加文件大小限制（未实现）
5. **日志记录**: 记录所有导出操作，包括权限验证失败的尝试

## 扩展功能（未实现）

1. **PDF 导出**: 参考 Python 版本的 PDF 转换
2. **批量导出**: 支持导出多个对话
3. **自定义模板**: 允许用户自定义导出格式
4. **云存储**: 将导出文件保存到 S3/OSS
5. **邮件发送**: 导出完成后发送邮件通知

## 使用示例

### 前端调用
```typescript
import { conversationApi } from '@/api/conversation';

// 导出对话
await conversationApi.exportConversation(123, true);
```

### 后端调用
```java
@Autowired
private ConversationExportService exportService;

// 导出对话
String filepath = exportService.exportConversationToMarkdown(
    conversationId, 
    userId, 
    true  // includeImages
);
```

## 测试建议

1. **单元测试**:
   - 测试 Markdown 生成逻辑
   - 测试图片提取和保存
   - 测试权限验证

2. **集成测试**:
   - 测试完整导出流程
   - 测试文件下载
   - 测试错误处理

3. **性能测试**:
   - 测试大对话导出（1000+ 消息）
   - 测试并发导出
   - 测试图片处理性能

## 已知限制

1. 图片仅支持 base64 格式检测
2. 暂不支持 PDF 导出
3. 文件存储在本地，不支持分布式部署
4. 没有导出进度反馈

## 参考

- Python 实现: `agent/biomni/agent/a1.py` - `save_conversation_history()`
- 数据库设计: `admin/backend/data/init/mysql/init.sql`
