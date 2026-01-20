# 消息管理 API 实现总结

## ✅ 已实现的 Java 代码

### 1. Controller 层

**文件**: `MessageController.java`

```java
@RestController
@RequestMapping("/api/messages")
@CrossOrigin(origins = "*")
public class MessageController {
    
    @Autowired
    private MessageService messageService;
    
    /**
     * 获取消息列表（历史消息）
     * GET /api/messages/list?conversationId=1&currentPage=1&pageSize=50
     */
    @RequestMapping("/list")
    public PageResult<List<MessageVO>> getMessages(
        GetMessagesRequest request,
        @AuthenticationPrincipal AdminVO currentUser
    ) {
        // 从数据库查询历史消息
        List<MessageVO> messages = messageService.getMessageList(
            request.getConversationId(), 
            currentUser.getId(),
            request
        );
        long total = messageService.getMessageCount(request.getConversationId());
        int totalPage = (int) Math.ceil((double) total / request.getPageSize());
        
        return PageResult.success(messages, request.getCurrentPage(), 
            request.getPageSize(), totalPage, total);
    }
    
    /**
     * 发送消息（保存用户消息）
     * POST /api/messages/send
     * Body: { "conversationId": 1, "content": "问题" }
     */
    @PostMapping("/send")
    public BaseResult<MessageVO> sendMessage(
        @Valid @RequestBody SendMessageRequest request,
        @AuthenticationPrincipal AdminVO currentUser
    ) {
        // 1. 检查配额（TODO）
        // 2. 保存用户消息到数据库
        // 3. 更新对话统计
        MessageVO message = messageService.sendMessage(
            request.getConversationId(),
            currentUser.getId(),
            request.getContent()
        );
        return BaseResult.success(message);
    }
}
```

### 2. Service 层

**文件**: `MessageService.java`

```java
@Service
public class MessageService {
    
    @Autowired
    private MessageDAO messageDAO;
    
    @Autowired
    private ConversationDAO conversationDAO;
    
    /**
     * 获取消息列表（历史消息）
     */
    public List<MessageVO> getMessageList(
        Integer conversationId, 
        Integer userId, 
        PageRequest pageRequest
    ) {
        // 1. 验证对话权限
        checkConversationAccess(conversationId, userId);
        
        // 2. 查询消息
        MessageDOExample example = new MessageDOExample();
        example.createCriteria().andConversationIdEqualTo(conversationId);
        example.setOrderByClause("created_at ASC");
        
        // 3. 分页
        int offset = (pageRequest.getCurrentPage() - 1) * pageRequest.getPageSize();
        example.setOffset(offset);
        example.setLimit(pageRequest.getPageSize());
        
        List<MessageDO> messages = messageDAO.selectByExample(example);
        
        return messages.stream()
            .map(this::convertToVO)
            .collect(Collectors.toList());
    }
    
    /**
     * 发送消息（保存用户消息）
     */
    @Transactional
    public MessageVO sendMessage(
        Integer conversationId, 
        Integer userId, 
        String content
    ) {
        // 1. 验证对话权限
        ConversationDO conversation = checkConversationAccess(conversationId, userId);
        
        // 2. TODO: 检查配额
        
        // 3. 创建用户消息
        MessageDO message = new MessageDO();
        message.setConversationId(conversationId);
        message.setRole("user");
        message.setContent(content);
        message.setContentType("text");
        message.setTokens(estimateTokens(content));
        message.setInputTokens(estimateTokens(content));
        message.setOutputTokens(0);
        message.setCreatedAt(LocalDateTime.now());
        
        messageDAO.insert(message);
        
        // 4. 更新对话统计
        conversation.setMessageCount(conversation.getMessageCount() + 1);
        conversation.setLastMessageAt(LocalDateTime.now());
        conversation.setUpdatedAt(LocalDateTime.now());
        conversationDAO.updateByPrimaryKey(conversation);
        
        return convertToVO(message);
    }
    
    /**
     * 验证对话访问权限
     */
    private ConversationDO checkConversationAccess(
        Integer conversationId, 
        Integer userId
    ) {
        ConversationDO conversation = conversationDAO.selectByPrimaryKey(conversationId);
        
        if (conversation == null || conversation.getDeletedAt() != null) {
            throw new RuntimeException("对话不存在");
        }
        
        if (!conversation.getUserId().equals(userId)) {
            throw new RuntimeException("无权访问此对话");
        }
        
        return conversation;
    }
    
    /**
     * 估算 Token 数量（简单实现：字符数 / 4）
     */
    private Integer estimateTokens(String content) {
        return Math.max(1, content.length() / 4);
    }
}
```

### 3. Request/Response

**已创建的文件**：
- ✅ `GetMessagesRequest.java` - 获取消息请求（继承 PageRequest）
- ✅ `SendMessageRequest.java` - 发送消息请求
- ✅ `MessageVO.java` - 消息响应对象

---

## 📋 接口清单

### 1. 获取历史消息

**接口**: `GET /api/messages/list`

**参数**:
```
conversationId: 1
currentPage: 1
pageSize: 50
```

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "conversationId": 1,
      "role": "user",
      "content": "什么是蛋白质？",
      "contentType": "text",
      "tokens": 15,
      "createdAt": "2025-01-20T09:00:00"
    }
  ],
  "currentPage": 1,
  "pageSize": 50,
  "totalPage": 1,
  "total": 2
}
```

### 2. 发送消息

**接口**: `POST /api/messages/send`

**请求**:
```json
{
  "conversationId": 1,
  "content": "什么是蛋白质？"
}
```

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "conversationId": 1,
    "role": "user",
    "content": "什么是蛋白质？",
    "contentType": "text",
    "tokens": 15,
    "inputTokens": 15,
    "outputTokens": 0,
    "createdAt": "2025-01-20T09:00:00"
  }
}
```

---

## 🔄 完整流程

### 打开对话时

```
1. 前端调用: GET /api/messages/list?conversationId=1
   ↓
2. MessageController.getMessages()
   ↓
3. MessageService.getMessageList()
   - 验证权限
   - 查询数据库
   - 分页返回
   ↓
4. 返回历史消息列表
   ↓
5. 前端显示历史消息
```

### 发送新消息时

```
1. 前端立即显示用户消息（乐观更新）
   ↓
2. 前端调用: POST /api/messages/send
   Body: { conversationId: 1, content: "问题" }
   ↓
3. MessageController.sendMessage()
   ↓
4. MessageService.sendMessage()
   - 验证权限
   - 检查配额（TODO）
   - 保存用户消息
   - 更新对话统计
   ↓
5. 返回消息 ID
   ↓
6. 前端通过 WebSocket 发送给 Python Agent
   ↓
7. Python Agent 执行并保存 AI 消息
   ↓
8. WebSocket 推送 AI 消息给前端
```

---

## ⚠️ 待实现的功能

### 1. 配额检查

在 `MessageService.sendMessage()` 中添加：

```java
// 检查配额
if (!quotaService.checkQuota(userId)) {
    throw new RuntimeException("配额不足");
}
```

### 2. Python Agent 保存 AI 消息

Python Agent 需要实现：

```python
# 保存 AI 消息到数据库
assistant_message = Message(
    conversation_id=conversation_id,
    role='assistant',
    content=result['content'],
    content_type='markdown',
    tokens=result['total_tokens'],
    input_tokens=result['input_tokens'],
    output_tokens=result['output_tokens'],
    created_at=datetime.now()
)
db.add(assistant_message)
db.commit()

# 更新对话统计
conversation = db.query(Conversation).get(conversation_id)
conversation.message_count += 1
conversation.total_tokens += result['total_tokens']
conversation.total_duration_ms += result['duration_ms']
conversation.last_message_at = datetime.now()
conversation.updated_at = datetime.now()
db.commit()
```

---

## 📊 数据库操作

### 查询历史消息

```sql
SELECT * FROM messages
WHERE conversation_id = ?
ORDER BY created_at ASC
LIMIT ? OFFSET ?;
```

### 保存用户消息

```sql
INSERT INTO messages (
  conversation_id, role, content, content_type, 
  tokens, input_tokens, output_tokens, created_at
) VALUES (?, 'user', ?, 'text', ?, ?, 0, NOW());

UPDATE conversations
SET message_count = message_count + 1,
    last_message_at = NOW(),
    updated_at = NOW()
WHERE id = ?;
```

### 保存 AI 消息（Python）

```sql
INSERT INTO messages (
  conversation_id, role, content, content_type,
  tokens, input_tokens, output_tokens, created_at
) VALUES (?, 'assistant', ?, 'markdown', ?, ?, ?, NOW());

UPDATE conversations
SET message_count = message_count + 1,
    total_tokens = total_tokens + ?,
    total_duration_ms = total_duration_ms + ?,
    last_message_at = NOW(),
    updated_at = NOW()
WHERE id = ?;
```

---

## ✅ 总结

### 已实现（Java）
- ✅ MessageController - 消息控制器
- ✅ MessageService - 消息业务逻辑
- ✅ 获取历史消息接口
- ✅ 发送消息接口
- ✅ 权限检查
- ✅ 对话统计更新

### 待实现
- ⏳ 配额检查（QuotaService）
- ⏳ Python Agent WebSocket 服务
- ⏳ Python Agent 保存 AI 消息
- ⏳ Python Agent 更新配额

---

**文档版本**: v1.0  
**创建时间**: 2025-01-20  
**维护者**: Biomni Team
