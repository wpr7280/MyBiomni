-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS `biomni` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE `biomni`;

-- 管理员表
CREATE TABLE `admin` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '管理员ID',
  `username` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '用户名',
  `password` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '密码',
  `email` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '邮箱',
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '手机号',
  `real_name` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '真实姓名',
  `avatar` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '头像URL',
  `role` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'user' COMMENT '角色: admin, user',
  `status` int(11) NOT NULL DEFAULT '1' COMMENT '状态: 0-禁用, 1-启用',
  `last_login_at` datetime DEFAULT NULL COMMENT '最后登录时间',
  `last_login_ip` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '最后登录IP',
  `login_fail_count` int(11) NOT NULL DEFAULT '0' COMMENT '登录失败次数',
  `locked_until` datetime DEFAULT NULL COMMENT '锁定截止时间',
  `force_password_change` int(11) NOT NULL DEFAULT '0' COMMENT '强制修改密码: 0-否, 1-是',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted_at` datetime DEFAULT NULL COMMENT '删除时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_admin_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='管理员表';

-- 插入默认管理员
INSERT INTO `admin` (`id`, `username`, `password`, `email`, `real_name`, `role`, `status`, `created_at`, `updated_at`) 
VALUES (1, 'admin', '$2a$10$vENRNYeF7YQd8tHbO0iRpOC.7RH52v1agfvllZxeVn1GZgn5.rl7S', 'admin@biomni.com', '系统管理员', 'admin', 1, NOW(), NOW());

-- 对话表
CREATE TABLE `conversations` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '对话ID',
  `user_id` int(11) NOT NULL COMMENT '用户ID（关联 admin 表）',
  `title` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '对话标题',
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'active' COMMENT '状态: active-进行中, completed-已完成, failed-失败, cancelled-已取消',
  `message_count` int(11) NOT NULL DEFAULT '0' COMMENT '消息数量',
  `total_tokens` int(11) NOT NULL DEFAULT '0' COMMENT '总Token消耗',
  `total_duration_ms` int(11) NOT NULL DEFAULT '0' COMMENT '总执行时长(毫秒)',
  `last_message_at` datetime DEFAULT NULL COMMENT '最后消息时间',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted_at` datetime DEFAULT NULL COMMENT '删除时间（软删除）',
  PRIMARY KEY (`id`),
  KEY `idx_conversations_user_updated` (`user_id`,`updated_at`),
  KEY `idx_conversations_deleted_at` (`deleted_at`),
  CONSTRAINT `fk_conversations_users` FOREIGN KEY (`user_id`) REFERENCES `admin` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='对话表';

-- 消息表
CREATE TABLE `messages` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '消息ID',
  `conversation_id` int(11) NOT NULL COMMENT '对话ID',
  `role` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '角色: user-用户, assistant-助手, system-系统',
  `content` text COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '消息内容',
  `content_type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'text' COMMENT '内容类型: text, markdown, code',
  `tokens` int(11) NOT NULL DEFAULT '0' COMMENT 'Token消耗',
  `input_tokens` int(11) DEFAULT '0' COMMENT '输入Token数',
  `output_tokens` int(11) DEFAULT '0' COMMENT '输出Token数',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_messages_conversation` (`conversation_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='消息表';

-- 执行步骤表
CREATE TABLE `execution_steps` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '步骤ID',
  `conversation_id` int(11) NOT NULL COMMENT '对话ID',
  `message_id` int(11) NOT NULL COMMENT '消息ID',
  `step_order` int(11) NOT NULL COMMENT '步骤顺序',
  `step_type` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '步骤类型: reasoning, tool_call, result',
  `step_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '步骤名称',
  `tool_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '工具名称',
  `tool_input` text COLLATE utf8mb4_unicode_ci COMMENT '工具输入(JSON)',
  `tool_output` text COLLATE utf8mb4_unicode_ci COMMENT '工具输出',
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'running' COMMENT '状态: running, success, failed',
  `error_message` text COLLATE utf8mb4_unicode_ci COMMENT '错误信息',
  `duration_ms` int(11) NOT NULL DEFAULT '0' COMMENT '执行时长(毫秒)',
  `started_at` datetime NOT NULL COMMENT '开始时间',
  `completed_at` datetime DEFAULT NULL COMMENT '完成时间',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_steps_conversation` (`conversation_id`),
  KEY `idx_steps_message` (`message_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='执行步骤表';

-- 系统配置表
CREATE TABLE `system_config` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '配置ID',
  `config_key` varchar(100) NOT NULL COMMENT '配置键',
  `config_value` varchar(10000) DEFAULT NULL COMMENT '配置值',
  `config_type` varchar(20) NOT NULL DEFAULT 'string' COMMENT '配置类型: string, int, float, bool, json',
  `description` varchar(500) DEFAULT NULL COMMENT '配置说明',
  `is_sensitive` int(11) NOT NULL DEFAULT '0' COMMENT '是否敏感: 0-否, 1-是',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_config_key` (`config_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统配置表';

-- 用户配额表
CREATE TABLE `user_quotas` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '配额ID',
  `user_id` int(11) NOT NULL COMMENT '用户ID',
  `total_token_limit` int(11) NOT NULL DEFAULT '1000000' COMMENT '总Token配额',
  `total_token_used` int(11) NOT NULL DEFAULT '0' COMMENT '已使用Token数',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_user_quotas_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户配额表';

-- 插入默认配额
INSERT INTO `user_quotas` (`user_id`, `total_token_limit`, `total_token_used`, `created_at`, `updated_at`) 
VALUES (1, 100000, 0, NOW(), NOW());


CREATE TABLE `attachments` (
                               `id` int(11) NOT NULL AUTO_INCREMENT,
                               `user_id` int(11) NOT NULL,
                               `conversation_id` int(11) DEFAULT NULL,
                               `message_id` int(11) DEFAULT NULL,
                               `filename` VARCHAR(255) NOT NULL,
                               `path` TEXT NOT NULL,
                               `size` int(11) NOT NULL DEFAULT 0,
                               `mime_type` VARCHAR(100) DEFAULT NULL,
                               `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                               PRIMARY KEY (`id`),
                               KEY `idx_attachments_user` (`user_id`),
                               KEY `idx_attachments_conversation` (`conversation_id`),
                               KEY `idx_attachments_message` (`message_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='附件表';