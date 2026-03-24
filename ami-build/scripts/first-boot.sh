#!/bin/bash
# ============================================================
# Biomni First Boot Initialization Script
# Native MySQL/Redis (apt-installed, not Docker)
# ============================================================

set -euo pipefail

LOCK_FILE="/opt/biomni/.initialized"
LOG_FILE="/opt/biomni/logs/first-boot.log"
CONFIG_DIR="/opt/biomni/config"
SQL_DIR="/opt/biomni/sql"
CRED_FILE="/home/ubuntu/biomni-credentials.txt"

if [ -f "$LOCK_FILE" ]; then
    echo "Biomni already initialized. Skipping."
    exit 0
fi

mkdir -p /opt/biomni/logs
exec > >(tee -a "$LOG_FILE") 2>&1
echo "=========================================="
echo "Biomni First Boot - $(date)"
echo "=========================================="

# ------------------------------------------
# 1. Generate secrets
# ------------------------------------------
echo "[1/6] Generating secrets..."

MYSQL_ROOT_PASSWORD="$(openssl rand -hex 24)"
MYSQL_BIOMNI_PASSWORD="$(openssl rand -hex 24)"
BIOMNI_JWT_SECRET="$(openssl rand -hex 32)"

TOKEN=$(curl -sf -X PUT "http://169.254.169.254/latest/api/token" \
  -H "X-aws-ec2-metadata-token-ttl-seconds: 300" --connect-timeout 3 || echo "")
if [ -n "$TOKEN" ]; then
    INSTANCE_ID=$(curl -sf -H "X-aws-ec2-metadata-token: $TOKEN" \
      http://169.254.169.254/latest/meta-data/instance-id || echo "unknown")
    PUBLIC_IP=$(curl -sf -H "X-aws-ec2-metadata-token: $TOKEN" \
      http://169.254.169.254/latest/meta-data/public-ipv4 || echo "127.0.0.1")
else
    INSTANCE_ID="unknown"
    PUBLIC_IP="127.0.0.1"
fi

echo "  Instance: $INSTANCE_ID | Public IP: $PUBLIC_IP"

# ------------------------------------------
# 2. Configure MySQL
# ------------------------------------------
echo "[2/6] Configuring MySQL..."

# Ensure MySQL is running
sudo systemctl start mysql
sleep 2

# Wait for MySQL to be ready
for i in $(seq 1 30); do
    if sudo mysqladmin ping --silent 2>/dev/null; then
        echo "  MySQL is ready."
        break
    fi
    if [ "$i" = "30" ]; then
        echo "  ERROR: MySQL failed to start within 60 seconds."
        exit 1
    fi
    sleep 2
done

# Reset root password and create biomni user
# pre-ami-cleanup.sh switches root to auth_socket, so sudo mysql works here
sudo mysql <<SQL
-- Set root password for TCP connections
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '${MYSQL_ROOT_PASSWORD}';

-- Create/reset biomni user
DROP USER IF EXISTS 'biomni'@'localhost';
CREATE USER 'biomni'@'localhost' IDENTIFIED BY '${MYSQL_BIOMNI_PASSWORD}';

-- Create database if not exists
CREATE DATABASE IF NOT EXISTS biomni DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
GRANT ALL PRIVILEGES ON biomni.* TO 'biomni'@'localhost';

FLUSH PRIVILEGES;
SQL

echo "  MySQL users configured."

# Initialize tables if admin table doesn't exist
TABLE_EXISTS=$(mysql -u biomni -p"${MYSQL_BIOMNI_PASSWORD}" biomni -sNe \
  "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='biomni' AND table_name='admin';" 2>/dev/null || echo "0")

if [ "$TABLE_EXISTS" = "0" ]; then
    echo "  Initializing database schema..."
    mysql -u biomni -p"${MYSQL_BIOMNI_PASSWORD}" biomni < ${SQL_DIR}/init.sql
    echo "  Database initialized."
else
    echo "  Database tables already exist, skipping schema init."
    # Ensure default admin exists (may have been cleaned by pre-ami-cleanup)
    ADMIN_EXISTS=$(mysql -u biomni -p"${MYSQL_BIOMNI_PASSWORD}" biomni -sNe \
      "SELECT COUNT(*) FROM admin WHERE id=1;" 2>/dev/null || echo "0")
    if [ "$ADMIN_EXISTS" = "0" ]; then
        echo "  Inserting default admin user..."
        mysql -u biomni -p"${MYSQL_BIOMNI_PASSWORD}" biomni -e \
          "INSERT INTO admin (id, username, password, email, real_name, role, status, created_at, updated_at) VALUES (1, 'admin', '\$2a\$10\$vENRNYeF7YQd8tHbO0iRpOC.7RH52v1agfvllZxeVn1GZgn5.rl7S', 'admin@biomni.com', 'System Admin', 'admin', 1, NOW(), NOW());"
        mysql -u biomni -p"${MYSQL_BIOMNI_PASSWORD}" biomni -e \
          "INSERT IGNORE INTO user_quotas (user_id, total_token_limit, total_token_used, created_at, updated_at) VALUES (1, 100000, 0, NOW(), NOW());"
        echo "  Default admin created."
    else
        mysql -u biomni -p"${MYSQL_BIOMNI_PASSWORD}" biomni -e \
          "UPDATE admin SET password='\$2a\$10\$vENRNYeF7YQd8tHbO0iRpOC.7RH52v1agfvllZxeVn1GZgn5.rl7S', force_password_change=0 WHERE id=1;"
        echo "  Admin password reset to default."
    fi
fi

# Ensure default system_config entries exist
echo "  Ensuring default system config..."
mysql -u biomni -p"${MYSQL_BIOMNI_PASSWORD}" biomni <<'CONFIGSQL'
INSERT IGNORE INTO system_config (config_key, config_value, config_type, description) VALUES
('agent.llm', 'us.anthropic.claude-sonnet-4-20250514-v1:0', 'string', 'LLM model name'),
('agent.source', 'Bedrock', 'string', 'LLM source provider'),
('agent.temperature', '0.7', 'float', 'LLM temperature'),
('agent.max_tokens', '8192', 'int', 'Max output tokens'),
('agent.timeout_seconds', '600', 'int', 'LLM request timeout'),
('agent.use_tool_retriever', 'true', 'bool', 'Use tool retriever'),
('agent.commercial_mode', 'false', 'bool', 'Commercial mode'),
('agent.base_url', '', 'string', 'Custom LLM base URL'),
('agent.api_key', '', 'string', 'LLM API key'),
('llm.openai_api_key', '', 'string', 'OpenAI API key'),
('llm.anthropic_api_key', '', 'string', 'Anthropic API key'),
('llm.gemini_api_key', '', 'string', 'Gemini API key'),
('llm.groq_api_key', '', 'string', 'Groq API key'),
('llm.azure_api_key', '', 'string', 'Azure API key'),
('llm.azure_endpoint', '', 'string', 'Azure endpoint'),
('llm.aws_region', 'us-east-1', 'string', 'AWS region'),
('llm.aws_access_key_id', '', 'string', 'AWS access key'),
('llm.aws_secret_access_key', '', 'string', 'AWS secret key'),
('llm.aws_bearer_token', '', 'string', 'AWS bearer token');
CONFIGSQL
echo "  System config ready."

# ------------------------------------------
# 3. Configure Redis
# ------------------------------------------
echo "[3/6] Configuring Redis..."
sudo systemctl start redis-server
echo "  Redis is running."

# ------------------------------------------
# 4. Write biomni.env
# ------------------------------------------
echo "[4/6] Writing config files..."

cat > ${CONFIG_DIR}/biomni.env <<ENVEOF
# Generated by first-boot.sh at $(date)

# Spring Boot
SPRING_PROFILES_ACTIVE=ami
SERVER_PORT=9999
SPRING_DATASOURCE_MYSQL_JDBC_URL=jdbc:mysql://127.0.0.1:3306/biomni?useUnicode=true&characterEncoding=utf8&useSSL=false&serverTimezone=GMT%2B8
SPRING_DATASOURCE_MYSQL_USERNAME=biomni
SPRING_DATASOURCE_MYSQL_PASSWORD=${MYSQL_BIOMNI_PASSWORD}
SPRING_DATASOURCE_MYSQL_DRIVER_CLASS_NAME=com.mysql.cj.jdbc.Driver
JWT_SECRET=${BIOMNI_JWT_SECRET}
JWT_EXPIRATION=86400000
SPRING_DATA_REDIS_HOST=127.0.0.1
SPRING_DATA_REDIS_PORT=6379

# Agent
JWT_SECRET_KEY=${BIOMNI_JWT_SECRET}
JWT_ALGORITHM=HS512
DATABASE_URL=mysql+pymysql://biomni:${MYSQL_BIOMNI_PASSWORD}@127.0.0.1:3306/biomni
USE_MOCK_AGENT=false
AGENT_DATA_PATH=/opt/biomni/data
AGENT_UPLOAD_DATA_PATH=/opt/biomni/upload
CORS_ORIGINS=["http://127.0.0.1","http://${PUBLIC_IP}"]
SPRING_BOOT_URL=http://127.0.0.1:9999
ENVEOF

chown biomni:biomni ${CONFIG_DIR}/biomni.env
chmod 600 ${CONFIG_DIR}/biomni.env
echo "  Config written."

# ------------------------------------------
# 5. Start services
# ------------------------------------------
echo "[5/6] Preparing services..."

# Ensure admin frontend symlink exists (nginx config uses /admin path)
sudo ln -sf /opt/biomni/admin-frontend /opt/biomni/admin

sudo ln -sf /etc/nginx/sites-available/biomni /etc/nginx/sites-enabled/biomni
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# NOTE: Do NOT start biomni-admin/biomni-agent here!
# They have After=biomni-firstboot.service in their unit files,
# so systemd will start them automatically once this script exits.
echo "  Nginx restarted. biomni-admin and biomni-agent will start after firstboot completes."

# ------------------------------------------
# 6. Save credentials
# ------------------------------------------
echo "[6/6] Saving credentials..."

cat > ${CRED_FILE} <<CREDEOF
============================================================
  Biomni Installation Credentials
  Generated: $(date)
  Instance:  ${INSTANCE_ID}
============================================================

  Admin Portal:   http://${PUBLIC_IP}/admin/
  Client Portal:  http://${PUBLIC_IP}/

  Admin Username: admin
  Admin Email:    admin@biomni.com
  Admin Password: biomni123

  MySQL Root Password:   ${MYSQL_ROOT_PASSWORD}
  MySQL Biomni Password: ${MYSQL_BIOMNI_PASSWORD}
  JWT Secret:            ${BIOMNI_JWT_SECRET}

  IMPORTANT:
    1. Please change the default admin password immediately
    2. Configure LLM API Key in Admin > System Config
    3. Consider binding an Elastic IP
    4. Consider configuring HTTPS (Let's Encrypt)

============================================================
CREDEOF

chmod 600 ${CRED_FILE}
chown ubuntu:ubuntu ${CRED_FILE}

touch ${LOCK_FILE}

echo ""
echo "=========================================="
echo "  Biomni initialization completed!"
echo "  Credentials: ${CRED_FILE}"
echo "=========================================="
