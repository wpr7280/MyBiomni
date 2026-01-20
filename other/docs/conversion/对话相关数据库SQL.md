# 对话相关数据库 SQL（精简版）

## 1. 对话表 (conversation) - 精简版

```sql
CREATE TABLE `conversation` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '对话ID',
  `user_id` INT NOT NULL COMMENT '用户ID（关联 admin 表）',
  `title` VARCHAR(255) NOT NULL COMMENT '对话标题',
  `status` VARCHAR(20) NOT NULL DEFAULT 'active' COMMENT '状态: active-进行中, completed-已完成, failed-失败, cancelled-已取消',
  `message_count` INT NOT NULL DEFAULT 0 COMMENT '消息数量',
  `total_tokens` INT NOT NULL DEFAULT 0 COMMENT '总Token消耗',
  `total_duration_ms` INT NOT NULL DEFAULT 0 COMMENT '总执行时长(毫秒)',
  `last_message_at` DATETIME DEFAULT NULL COMMENT '最后消息时间',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted_at` DATETIME DEFAULT NULL COMMENT '删除时间（软删除）',
  PRIMARY KEY (`id`),
  KEY `idx_conversations_user_updated` (`user_id`, `updated_at` DESC),
  KEY `idx_conversations_deleted_at` (`deleted_at`),
  CONSTRAINT `fk_conversations_users` FOREIGN KEY (`user_id`) REFERENCES `admin` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='对话表';
```

**字段说明**：
- ✅ 11 个字段（核心 6 + 统计 4 + 软删除 1）
- ✅ 所有 ID 和数值字段使用 INT
- ❌ 移除了 `model_name`, `model_source`（只用一个模型）
- ❌ 移除了 `thread_id`, `context_data`（暂不需要）
- ❌ 移除了 `is_favorite`, `is_pinned`（暂不需要）

---

## 2. 消息表 (messages) - 精简版

```sql
CREATE TABLE `messages` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '消息ID',
  `conversation_id` BIGINT NOT NULL COMMENT '对话ID',
  `role` VARCHAR(20) NOT NULL COMMENT '角色: user-用户, assistant-助手, system-系统',
  `content` TEXT NOT NULL COMMENT '消息内容',
  `content_type` VARCHAR(20) NOT NULL DEFAULT 'text' COMMENT '内容类型: text, markdown, code',
  `tokens` INT NOT NULL DEFAULT 0 COMMENT 'Token消耗',
  `input_tokens` INT DEFAULT 0 COMMENT '输入Token数',
  `output_tokens` INT DEFAULT 0 COMMENT '输出Token数',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_messages_conversation_created` (`conversation_id`, `created_at` ASC),
  CONSTRAINT `fk_messages_conversations` FOREIGN KEY (`conversation_id`) REFERENCES `conversations` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='消息表';
```

**字段说明**：
- ✅ 9 个字段（核心功能）
- ❌ 移除了 `attachments`（文件上传暂不实现）
- ❌ 移除了 `metadata`（暂不需要）
- ❌ 移除了 `parent_message_id`（暂不需要消息树）

---

## 3. 执行步骤表 (execution_steps)

```sql
CREATE TABLE `execution_steps` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '步骤ID',
  `conversation_id` BIGINT NOT NULL COMMENT '对话ID',
  `message_id` BIGINT NOT NULL COMMENT '消息ID',
  `step_order` INT NOT NULL COMMENT '步骤顺序',
  `step_type` VARCHAR(50) NOT NULL COMMENT '步骤类型: reasoning, tool_call, result',
  `step_name` VARCHAR(100) DEFAULT NULL COMMENT '步骤名称',
  `tool_name` VARCHAR(100) DEFAULT NULL COMMENT '工具名称',
  `tool_input` TEXT DEFAULT NULL COMMENT '工具输入(JSON)',
  `tool_output` TEXT DEFAULT NULL COMMENT '工具输出',
  `status` VARCHAR(20) NOT NULL DEFAULT 'running' COMMENT '状态: running, success, failed',
  `error_message` TEXT DEFAULT NULL COMMENT '错误信息',
  `duration_ms` INT NOT NULL DEFAULT 0 COMMENT '执行时长(毫秒)',
  `started_at` DATETIME NOT NULL COMMENT '开始时间',
  `completed_at` DATETIME DEFAULT NULL COMMENT '完成时间',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_steps_conversation` (`conversation_id`),
  KEY `idx_steps_message` (`message_id`),
  KEY `idx_steps_order` (`conversation_id`, `step_order`),
  KEY `idx_steps_status` (`status`),
  CONSTRAINT `fk_steps_conversations` FOREIGN KEY (`conversation_id`) REFERENCES `conversations` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_steps_messages` FOREIGN KEY (`message_id`) REFERENCES `messages` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='执行步骤表';
```

---

## 4. 示例数据

### 4.1 插入测试对话

```sql
-- 插入测试对话
INSERT INTO conversations (user_id, title, status, message_count, last_message_at) VALUES
(1, '蛋白质结构分析', 'active', 4, '2025-01-20 10:30:00'),
(1, '基因测序数据处理', 'completed', 2, '2025-01-19 15:20:00'),
(1, '单细胞分析流程', 'active', 2, '2025-01-18 16:45:00');
```

### 4.2 插入测试消息

```sql
-- 对话 1 的消息
INSERT INTO messages (conversation_id, role, content, content_type, tokens, input_tokens, output_tokens) VALUES
(1, 'user', '什么是蛋白质的二级结构？', 'text', 15, 15, 0),
(1, 'assistant', '蛋白质的二级结构是指蛋白质多肽链中局部区域的空间排列方式...', 'markdown', 150, 15, 135),
(1, 'user', '如何使用 Python 分析蛋白质结构？', 'text', 20, 20, 0),
(1, 'assistant', '可以使用 Biopython 库来分析蛋白质结构...', 'markdown', 200, 20, 180);

-- 对话 2 的消息
INSERT INTO messages (conversation_id, role, content, content_type, tokens) VALUES
(2, 'user', '如何进行基因测序数据的质量控制？', 'text', 18),
(2, 'assistant', '基因测序数据的质量控制是非常重要的步骤...', 'markdown', 180);

-- 对话 3 的消息
INSERT INTO messages (conversation_id, role, content, content_type, tokens) VALUES
(3, 'user', '单细胞 RNA 测序的基本流程是什么？', 'text', 16),
(3, 'assistant', '单细胞 RNA 测序（scRNA-seq）的基本流程包括...', 'markdown', 220);
```

### 4.3 插入测试执行步骤

```sql
-- 消息 2 的执行步骤
INSERT INTO execution_steps (conversation_id, message_id, step_order, step_type, step_name, tool_name, tool_input, tool_output, status, duration_ms, started_at, completed_at) VALUES
(1, 2, 1, 'reasoning', '分析问题', NULL, NULL, NULL, 'success', 500, '2025-01-20 09:00:01', '2025-01-20 09:00:01.5'),
(1, 2, 2, 'tool_call', '搜索知识库', 'search_knowledge', '{"query": "蛋白质二级结构", "limit": 5}', '找到 5 篇相关文献', 'success', 1200, '2025-01-20 09:00:02', '2025-01-20 09:00:03.2'),
(1, 2, 3, 'tool_call', '生成回答', 'generate_answer', '{"context": "相关知识", "question": "什么是蛋白质的二级结构？"}', '回答生成完成', 'success', 2000, '2025-01-20 09:00:04', '2025-01-20 09:00:06');
```

---

## 5. 常用查询

### 5.1 获取用户的对话列表

```sql
SELECT 
  id,
  title,
  status,
  message_count,
  total_tokens,
  last_message_at,
  created_at,
  updated_at
FROM conversations
WHERE user_id = ? 
  AND deleted_at IS NULL
ORDER BY updated_at DESC
LIMIT ? OFFSET ?;
```

### 5.2 获取对话的消息列表

```sql
SELECT 
  id,
  conversation_id,
  role,
  content,
  content_type,
  tokens,
  input_tokens,
  output_tokens,
  attachments,
  created_at
FROM messages
WHERE conversation_id = ?
ORDER BY created_at ASC
LIMIT ? OFFSET ?;
```

### 5.3 获取消息的执行步骤

```sql
SELECT 
  id,
  conversation_id,
  message_id,
  step_order,
  step_type,
  step_name,
  tool_name,
  tool_input,
  tool_output,
  status,
  error_message,
  duration_ms,
  started_at,
  completed_at
FROM execution_steps
WHERE message_id = ?
ORDER BY step_order ASC;
```

### 5.4 创建新对话

```sql
INSERT INTO conversations (user_id, title, status)
VALUES (?, ?, 'active');
```

### 5.5 更新对话标题（重命名）

```sql
UPDATE conversations
SET title = ?, updated_at = NOW()
WHERE id = ? AND user_id = ? AND deleted_at IS NULL;
```

### 5.6 删除对话（软删除）

```sql
UPDATE conversations
SET deleted_at = NOW()
WHERE id = ? AND user_id = ?;
```

### 5.7 保存用户消息

```sql
INSERT INTO messages (conversation_id, role, content, content_type, tokens)
VALUES (?, 'user', ?, 'text', ?);

-- 同时更新对话的消息数量和最后消息时间
UPDATE conversations
SET message_count = message_count + 1,
    last_message_at = NOW(),
    updated_at = NOW()
WHERE id = ?;
```

### 5.8 保存 Assistant 消息

```sql
INSERT INTO messages (conversation_id, role, content, content_type, tokens, input_tokens, output_tokens)
VALUES (?, 'assistant', ?, 'markdown', ?, ?, ?);

-- 同时更新对话统计
UPDATE conversations
SET message_count = message_count + 1,
    total_tokens = total_tokens + ?,
    total_duration_ms = total_duration_ms + ?,
    last_message_at = NOW(),
    updated_at = NOW()
WHERE id = ?;
```

### 5.9 保存执行步骤

```sql
INSERT INTO execution_steps (
  conversation_id,
  message_id,
  step_order,
  step_type,
  step_name,
  tool_name,
  tool_input,
  tool_output,
  status,
  duration_ms,
  started_at,
  completed_at
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
```

---

## 6. 索引优化

```sql
-- 对话列表查询优化（用户ID + 更新时间倒序）
CREATE INDEX idx_conversations_user_updated 
ON conversations(user_id, updated_at DESC, deleted_at);

-- 消息查询优化（对话ID + 创建时间正序）
CREATE INDEX idx_messages_conversation_created 
ON messages(conversation_id, created_at ASC);

-- 执行步骤查询优化（消息ID + 步骤顺序）
CREATE INDEX idx_execution_steps_message_order 
ON execution_steps(message_id, step_order ASC);

-- 软删除查询优化
CREATE INDEX idx_conversations_deleted 
ON conversations(deleted_at);
```

---

## 7. 数据库初始化脚本

```sql
-- 创建数据库
CREATE DATABASE IF NOT EXISTS biomni_app 
  DEFAULT CHARACTER SET utf8mb4 
  COLLATE utf8mb4_unicode_ci;

USE biomni_app;

-- 创建对话表
CREATE TABLE `conversations` (
  -- 见上文
);

-- 创建消息表
CREATE TABLE `messages` (
  -- 见上文
);

-- 创建执行步骤表
CREATE TABLE `execution_steps` (
  -- 见上文
);

-- 插入测试数据
INSERT INTO conversations (user_id, title, status, message_count, last_message_at) VALUES
(1, '蛋白质结构分析', 'active', 4, '2025-01-20 10:30:00'),
(1, '基因测序数据处理', 'completed', 2, '2025-01-19 15:20:00'),
(1, '单细胞分析流程', 'active', 2, '2025-01-18 16:45:00');
```

---

## 8. JPA Entity 示例

### 8.1 Conversation Entity（精简版）

```java
@Entity
@Table(name = "conversations")
public class Conversation {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "user_id", nullable = false)
    private Integer userId;
    
    @Column(nullable = false, length = 255)
    private String title;
    
    @Column(nullable = false, length = 20)
    private String status = "active";
    
    @Column(name = "message_count", nullable = false)
    private Integer messageCount = 0;
    
    @Column(name = "total_tokens", nullable = false)
    private Long totalTokens = 0L;
    
    @Column(name = "total_duration_ms", nullable = false)
    private Long totalDurationMs = 0L;
    
    @Column(name = "last_message_at")
    private LocalDateTime lastMessageAt;
    
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;
    
    @Column(name = "updated_at", nullable = false)
    private LocalDateTime updatedAt;
    
    @Column(name = "deleted_at")
    private LocalDateTime deletedAt;
    
    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }
    
    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
    
    // Getters and Setters
}
```

### 8.2 Message Entity

```java
@Entity
@Table(name = "messages")
public class Message {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "conversation_id", nullable = false)
    private Long conversationId;
    
    @Column(nullable = false)
    private String role;
    
    @Column(nullable = false, columnDefinition = "TEXT")
    private String content;
    
    @Column(name = "content_type")
    private String contentType = "text";
    
    @Column
    private Integer tokens = 0;
    
    @Column(name = "input_tokens")
    private Integer inputTokens;
    
    @Column(name = "output_tokens")
    private Integer outputTokens;
    
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;
    
    // Getters and Setters
}
```

### 8.3 ExecutionStep Entity

```java
@Entity
@Table(name = "execution_steps")
public class ExecutionStep {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "conversation_id", nullable = false)
    private Long conversationId;
    
    @Column(name = "message_id", nullable = false)
    private Long messageId;
    
    @Column(name = "step_order", nullable = false)
    private Integer stepOrder;
    
    @Column(name = "step_type", nullable = false)
    private String stepType;
    
    @Column(name = "step_name")
    private String stepName;
    
    @Column(name = "tool_name")
    private String toolName;
    
    @Column(name = "tool_input", columnDefinition = "TEXT")
    private String toolInput;
    
    @Column(name = "tool_output", columnDefinition = "TEXT")
    private String toolOutput;
    
    @Column(nullable = false)
    private String status = "running";
    
    @Column(name = "error_message", columnDefinition = "TEXT")
    private String errorMessage;
    
    @Column(name = "duration_ms")
    private Integer durationMs = 0;
    
    @Column(name = "started_at", nullable = false)
    private LocalDateTime startedAt;
    
    @Column(name = "completed_at")
    private LocalDateTime completedAt;
    
    // Getters and Setters
}
```

---

## 9. Python SQLAlchemy 模型示例（精简版）

```python
from sqlalchemy import Column, Integer, BigInteger, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Conversation(Base):
    __tablename__ = 'conversations'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    status = Column(String(20), nullable=False, default='active')
    message_count = Column(Integer, nullable=False, default=0)
    total_tokens = Column(BigInteger, nullable=False, default=0)
    total_duration_ms = Column(BigInteger, nullable=False, default=0)
    last_message_at = Column(DateTime)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    deleted_at = Column(DateTime)

class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    conversation_id = Column(BigInteger, nullable=False)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    content_type = Column(String(20), nullable=False, default='text')
    tokens = Column(Integer, nullable=False, default=0)
    input_tokens = Column(Integer)
    output_tokens = Column(Integer)
    created_at = Column(DateTime, nullable=False, default=datetime.now)

class ExecutionStep(Base):
    __tablename__ = 'execution_steps'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    conversation_id = Column(BigInteger, nullable=False)
    message_id = Column(BigInteger, nullable=False)
    step_order = Column(Integer, nullable=False)
    step_type = Column(String(50), nullable=False)
    step_name = Column(String(100))
    tool_name = Column(String(100))
    tool_input = Column(Text)
    tool_output = Column(Text)
    status = Column(String(20), nullable=False, default='running')
    error_message = Column(Text)
    duration_ms = Column(Integer, nullable=False, default=0)
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
```

---

**文档版本**: v1.0  
**创建时间**: 2025-01-20  
**维护者**: Biomni Team
