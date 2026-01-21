-- 创建用户配额表
CREATE TABLE IF NOT EXISTS `user_quotas` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '配额ID',
  `user_id` INT NOT NULL COMMENT '用户ID',
  `total_token_limit` INT NOT NULL DEFAULT 1000000 COMMENT '总Token配额',
  `total_token_used` INT NOT NULL DEFAULT 0 COMMENT '已使用Token数',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_user_quotas_user` (`user_id`),
  CONSTRAINT `fk_user_quotas_users` FOREIGN KEY (`user_id`) REFERENCES `admin` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户配额表';

-- 为所有现有用户创建默认配额（100万 Token）
INSERT INTO user_quotas (user_id, total_token_limit, total_token_used)
SELECT id, 1000000, 0 FROM admin
ON DUPLICATE KEY UPDATE user_id = user_id;
