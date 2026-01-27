# 对话导出功能 - 快速指南

## 快速开始

### 用户使用

1. 在聊天界面，点击底部的 "Export & Download" 按钮
2. 选择 "Export as Markdown"
3. 等待导出完成，文件会自动下载
4. **如果对话包含图片**：下载的是 ZIP 文件，解压后查看
5. **如果对话无图片**：下载的是 MD 文件，直接打开

### 文件格式

- **无图片**：`conversation_123.md`
- **有图片**：`conversation_123_1234567890.zip`
  ```
  conversation_123_1234567890.zip
  ├── conversation_123.md
  └── images/
      ├── image_1.png
      └── image_2.jpg
  ```

### 开发者集成

#### 前端调用
```typescript
import { conversationApi } from '@/api/conversation';

// 导出对话（包含图片）
await conversationApi.exportConversation(conversationId, true);

// 导出对话（不包含图片）
await conversationApi.exportConversation(conversationId, false);
```

#### 后端调用
```java
@Autowired
private ConversationExportService exportService;

// 普通用户导出自己的对话
String filepath = exportService.exportConversationToMarkdown(
    conversationId, 
    userId, 
    false,  // isAdmin = false
    true    // includeImages
);

// 管理员导出任何对话
String filepath = exportService.exportConversationToMarkdown(
    conversationId, 
    adminUserId, 
    true,   // isAdmin = true
    true    // includeImages
);
```

## API 端点

### POST /api/conversations/export

**请求**:
```json
{
  "conversationId": 123,
  "includeImages": true
}
```

**响应**: Binary file stream (Markdown)

**Headers**:
- Content-Type: application/octet-stream
- Content-Disposition: attachment; filename="conversation_123_1234567890.md"

## 文件结构

```
exports/
└── conversations/
    ├── conversation_1_1234567890.md
    ├── conversation_2_1234567891.md
    └── images/
        ├── image_1234567890.png
        └── image_1234567891.jpg
```

## 配置选项

### 导出目录
默认: `exports/conversations/`

修改位置: `ConversationExportService.EXPORT_BASE_DIR`

### 文件清理
定期清理过期文件（可选）:

```java
// 清理 7 天前的导出文件
exportService.cleanupOldExports(7);
```

建议在定时任务中调用。

## 导出内容

Markdown 文件包含：

1. **对话元数据**
   - 对话 ID
   - 创建时间
   - 状态
   - 消息数量
   - Token 消耗

2. **消息内容**
   - 用户消息
   - AI 回复
   - 时间戳
   - Token 统计

3. **执行步骤**（仅 AI 消息）
   - 步骤顺序
   - 工具名称
   - 输入参数（JSON）
   - 输出结果
   - 执行状态
   - 执行时长

4. **图片附件**（可选）
   - 自动提取 base64 图片
   - 保存为独立文件
   - Markdown 引用

## 故障排查

### 问题：导出失败
**可能原因**:
- 用户无权限访问对话（普通用户尝试导出其他用户的对话）
- 对话不存在或已删除
- 对话没有消息内容
- 磁盘空间不足

**解决方法**:
1. 检查用户权限和角色（admin 可以导出任何对话，user 只能导出自己的）
2. 确认对话 ID 正确
3. 检查数据库数据
4. 检查磁盘空间
5. 查看服务器日志中的详细错误信息

### 问题：图片未导出
**可能原因**:
- `includeImages` 设置为 false
- 图片格式不支持
- base64 数据格式错误

**解决方法**:
1. 确认 `includeImages` 参数
2. 检查图片数据格式
3. 查看日志错误信息

### 问题：文件下载失败
**可能原因**:
- 浏览器拦截下载
- 网络连接问题
- 文件已被删除

**解决方法**:
1. 检查浏览器下载设置
2. 重试导出
3. 检查服务器日志

## 性能优化建议

1. **大对话处理**
   - 对于超过 1000 条消息的对话，考虑分页导出
   - 添加进度反馈

2. **并发控制**
   - 限制同时导出的数量
   - 使用队列处理导出请求

3. **缓存策略**
   - 缓存最近导出的文件
   - 设置合理的过期时间

4. **异步处理**
   - 对于大文件，使用异步导出
   - 完成后通知用户

## 安全注意事项

1. **权限验证**: 
   - 管理员 (role='admin') 可以导出任何用户的对话
   - 普通用户 (role='user') 只能导出自己的对话
   - 始终验证用户对对话的所有权或管理员权限
2. **路径安全**: 使用安全的文件路径处理
3. **文件清理**: 定期清理临时文件
4. **大小限制**: 考虑添加文件大小限制
5. **审计日志**: 记录所有导出操作，特别是管理员导出其他用户对话的操作

## 扩展开发

### 添加 PDF 导出

参考 Python 实现:
```python
# agent/biomni/agent/a1.py
def _convert_markdown_to_pdf(self, markdown_path: str, pdf_path: str):
    # 使用 markdown2pdf 或类似库
    pass
```

Java 实现建议:
- 使用 iText 或 Apache PDFBox
- 先生成 HTML，再转 PDF
- 或调用外部工具（pandoc）

### 添加自定义模板

```java
public String exportWithTemplate(
    Integer conversationId, 
    Integer userId, 
    String templatePath
) {
    // 读取模板
    // 替换占位符
    // 生成文件
}
```

### 添加云存储支持

```java
public String exportToS3(
    Integer conversationId, 
    Integer userId
) {
    // 生成 Markdown
    // 上传到 S3
    // 返回下载链接
}
```

## 相关文档

- [完整实现文档](./EXPORT_FEATURE.md)
- [API 接口文档](./API接口文档.md)
- [数据库设计](./数据库设计.md)
