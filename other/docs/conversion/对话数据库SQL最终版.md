# 对话相关数据库 SQL（最终精简版）

## 1. 对话表 (conversations)

```sql
CREATE TABLE `conversations` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '对话ID',
  `user_id` INT NOT NULL COMMENT '用户ID（关联 admin 表）',
  `title` VARCHAR(255) NOT NULL COMMENT '对话标题',
  `status` VARCHAR(20) NOT NULL DEFAULT 'active' COMMENT '状态: active, completed, failed, cancelled',
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

**字段总数**: 11 个  
**所有 ID 和数值字段使用 INT**

---

## 2. 消息表 (messages)

```sql
CREATE TABLE `messages` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '消息ID',
  `conversation_id` INT NOT NULL COMMENT '对话ID',
  `role` VARCHAR(20) NOT NULL COMMENT '角色: user, assistant, system',
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

**字段总数**: 9 个

---

## 3. 执行步骤表 (execution_steps)

```sql
CREATE TABLE `execution_steps` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '步骤ID',
  `conversation_id` INT NOT NULL COMMENT '对话ID',
  `message_id` INT NOT NULL COMMENT '消息ID',
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
  KEY `idx_steps_message_order` (`message_id`, `step_order` ASC),
  CONSTRAINT `fk_steps_conversations` FOREIGN KEY (`conversation_id`) REFERENCES `conversations` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_steps_messages` FOREIGN KEY (`message_id`) REFERENCES `messages` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='执行步骤表';
```

**字段总数**: 15 个

---

## 4. 完整初始化脚本

```sql
-- 创建数据库
CREATE DATABASE IF NOT EXISTS biomni_app 
  DEFAULT CHARACTER SET utf8mb4 
  COLLATE utf8mb4_unicode_ci;

USE biomni_app;

-- 1. 创建对话表
CREATE TABLE `conversations` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '对话ID',
  `user_id` INT NOT NULL COMMENT '用户ID',
  `title` VARCHAR(255) NOT NULL COMMENT '对话标题',
  `status` VARCHAR(20) NOT NULL DEFAULT 'active' COMMENT '状态',
  `message_count` INT NOT NULL DEFAULT 0 COMMENT '消息数量',
  `total_tokens` INT NOT NULL DEFAULT 0 COMMENT '总Token消耗',
  `total_duration_ms` INT NOT NULL DEFAULT 0 COMMENT '总执行时长(毫秒)',
  `last_message_at` DATETIME DEFAULT NULL COMMENT '最后消息时间',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted_at` DATETIME DEFAULT NULL COMMENT '删除时间',
  PRIMARY KEY (`id`),
  KEY `idx_conversations_user_updated` (`user_id`, `updated_at` DESC),
  KEY `idx_conversations_deleted_at` (`deleted_at`),
  CONSTRAINT `fk_conversations_users` FOREIGN KEY (`user_id`) REFERENCES `admin` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='对话表';

-- 2. 创建消息表
CREATE TABLE `messages` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '消息ID',
  `conversation_id` INT NOT NULL COMMENT '对话ID',
  `role` VARCHAR(20) NOT NULL COMMENT '角色: user, assistant, system',
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

-- 3. 创建执行步骤表
CREATE TABLE `execution_steps` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '步骤ID',
  `conversation_id` INT NOT NULL COMMENT '对话ID',
  `message_id` INT NOT NULL COMMENT '消息ID',
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
  KEY `idx_steps_message_order` (`message_id`, `step_order` ASC),
  CONSTRAINT `fk_steps_conversations` FOREIGN KEY (`conversation_id`) REFERENCES `conversations` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_steps_messages` FOREIGN KEY (`message_id`) REFERENCES `messages` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='执行步骤表';

-- 4. 插入测试数据
INSERT INTO conversations (user_id, title, status, message_count, last_message_at) VALUES
(1, '蛋白质结构分析', 'active', 4, '2025-01-20 10:30:00'),
(1, '基因测序数据处理', 'completed', 2, '2025-01-19 15:20:00'),
(1, '单细胞分析流程', 'active', 2, '2025-01-18 16:45:00');
```

---

**文档版本**: v2.0（最终精简版）  
**创建时间**: 2025-01-20  
**维护者**: WarpHelix Team  
**说明**: 所有 ID 和数值字段使用 INT，移除了不必要的字段
