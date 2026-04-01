#!/bin/bash
#
# WarpHelix One-Click Deployment Script
# Run on a fresh Ubuntu 22.04/24.04 server (Alibaba Cloud / AWS / etc.)
#
# Prerequisites: 
#   - Root or sudo access
#   - Git installed
#   - Internet access
#
# Usage:
#   chmod +x deploy.sh
#   sudo ./deploy.sh
#

set -e

echo "======================================"
echo "  WarpHelix Deployment Script"
echo "======================================"

# --- Config (edit these) ---
MYSQL_ROOT_PASSWORD="CHANGE_ME_$(openssl rand -hex 16)"
JWT_SECRET="$(openssl rand -hex 32)"
REDIS_PASSWORD=""  # empty = no auth
SERVER_IP="$(curl -s ifconfig.me || hostname -I | awk '{print $1}')"
REPO_URL="git@github.com:wpr7280/MyBiomni.git"
DEPLOY_DIR="/opt/biomni"
DATA_DIR="/opt/biomni/data"
UPLOAD_DIR="/opt/biomni/upload"
CONFIG_DIR="/opt/biomni/config"
LOG_DIR="/opt/biomni/logs"
AGENT_PORT=8000
ADMIN_PORT=9999
# --- End Config ---

echo ""
echo "Server IP: $SERVER_IP"
echo "Deploy to: $DEPLOY_DIR"
echo ""

# ==================== 1. System Dependencies ====================
echo ">>> [1/8] Installing system dependencies..."
apt-get update -qq
apt-get install -y -qq python3 python3-pip python3-venv \
    openjdk-17-jre-headless \
    mysql-server redis-server \
    nginx git curl unzip jq

# ==================== 2. Create user & directories ====================
echo ">>> [2/8] Creating biomni user and directories..."
id biomni &>/dev/null || useradd -r -m -s /bin/bash biomni
mkdir -p $DEPLOY_DIR/{agent,admin-backend,admin-frontend,client-frontend,config,logs,data,upload,scripts}
mkdir -p $DATA_DIR/user_uploads
mkdir -p $UPLOAD_DIR
mkdir -p $LOG_DIR

# ==================== 3. MySQL Setup ====================
echo ">>> [3/8] Setting up MySQL..."
systemctl enable --now mysql

# Set root password and create database
mysql -u root <<EOF
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '$MYSQL_ROOT_PASSWORD';
CREATE DATABASE IF NOT EXISTS biomni CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
FLUSH PRIVILEGES;
EOF

echo "MySQL root password: $MYSQL_ROOT_PASSWORD"

# ==================== 4. Redis Setup ====================
echo ">>> [4/8] Setting up Redis..."
systemctl enable --now redis-server

# ==================== 5. Clone & Build ====================
echo ">>> [5/8] Cloning repository and building..."
TEMP_DIR="/tmp/biomni-build"
rm -rf $TEMP_DIR
git clone $REPO_URL $TEMP_DIR

# -- Agent (Python) --
echo "  Building Agent..."
cp -r $TEMP_DIR/agent/* $DEPLOY_DIR/agent/
python3 -m venv $DEPLOY_DIR/agent/venv
$DEPLOY_DIR/agent/venv/bin/pip install -q -r $DEPLOY_DIR/agent/requirements.txt 2>/dev/null || \
$DEPLOY_DIR/agent/venv/bin/pip install -q fastapi uvicorn sqlalchemy pymysql langchain langchain-aws langchain-openai biopython

# -- Admin Backend (Java) --
echo "  Building Admin Backend..."
cd $TEMP_DIR/admin/backend
if command -v mvn &>/dev/null; then
    mvn package -DskipTests -q
else
    echo "  Maven not found, installing..."
    apt-get install -y -qq maven
    mvn package -DskipTests -q
fi
cp target/biomni-admin.jar $DEPLOY_DIR/admin-backend/

# -- Admin Frontend --
echo "  Building Admin Frontend..."
cd $TEMP_DIR/admin/frontend
if ! command -v node &>/dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
    apt-get install -y -qq nodejs
fi
npm install --silent
npx vite build
cp -r dist/* $DEPLOY_DIR/admin-frontend/

# -- Client Frontend --
echo "  Building Client Frontend..."
cd $TEMP_DIR/client/frontend
npm install --silent
npx vite build
cp -r dist/* $DEPLOY_DIR/client-frontend/

# ==================== 6. Config Files ====================
echo ">>> [6/8] Writing config files..."

cat > $CONFIG_DIR/biomni.env <<EOF
# WarpHelix Configuration
SPRING_PROFILES_ACTIVE=ami
SERVER_PORT=$ADMIN_PORT
SPRING_DATASOURCE_MYSQL_JDBC_URL=jdbc:mysql://127.0.0.1:3306/biomni?useUnicode=true&characterEncoding=utf8&useSSL=false&serverTimezone=GMT%2B8&allowPublicKeyRetrieval=true
SPRING_DATASOURCE_MYSQL_USERNAME=root
SPRING_DATASOURCE_MYSQL_PASSWORD=$MYSQL_ROOT_PASSWORD
SPRING_DATASOURCE_MYSQL_DRIVER_CLASS_NAME=com.mysql.cj.jdbc.Driver
JWT_SECRET=$JWT_SECRET
JWT_EXPIRATION=86400000
JWT_ALGORITHM=HS512
SPRING_DATA_REDIS_HOST=127.0.0.1
SPRING_DATA_REDIS_PORT=6379
DATABASE_URL=mysql+pymysql://root:$MYSQL_ROOT_PASSWORD@127.0.0.1:3306/biomni
USE_MOCK_AGENT=false
AGENT_DATA_PATH=$DATA_DIR
AGENT_UPLOAD_DATA_PATH=$UPLOAD_DIR
CORS_ORIGINS=["http://127.0.0.1","http://$SERVER_IP"]
SPRING_BOOT_URL=http://127.0.0.1:$ADMIN_PORT
EOF

chmod 600 $CONFIG_DIR/biomni.env

# ==================== 7. Systemd Services ====================
echo ">>> [7/8] Setting up systemd services..."

cat > /etc/systemd/system/biomni-agent.service <<EOF
[Unit]
Description=WarpHelix AI Agent (FastAPI)
After=network.target mysql.service redis-server.service

[Service]
User=biomni
WorkingDirectory=$DEPLOY_DIR/agent
EnvironmentFile=$CONFIG_DIR/biomni.env
ExecStart=$DEPLOY_DIR/agent/venv/bin/uvicorn api.app:app \\
    --host 127.0.0.1 --port $AGENT_PORT \\
    --log-level info
Environment="PYTHONUNBUFFERED=1"
StandardOutput=append:$LOG_DIR/agent.log
StandardError=append:$LOG_DIR/agent-error.log
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

cat > /etc/systemd/system/biomni-admin.service <<EOF
[Unit]
Description=WarpHelix Admin Backend (Spring Boot)
After=network.target mysql.service redis-server.service

[Service]
User=biomni
WorkingDirectory=$DEPLOY_DIR/admin-backend
EnvironmentFile=$CONFIG_DIR/biomni.env
ExecStart=/usr/bin/java -Xms512m -Xmx1g \\
    -jar $DEPLOY_DIR/admin-backend/biomni-admin.jar
StandardOutput=append:$LOG_DIR/admin-backend.log
StandardError=append:$LOG_DIR/admin-backend-error.log
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Fix ownership
chown -R biomni:biomni $DEPLOY_DIR

# Enable and start services
systemctl daemon-reload
systemctl enable biomni-agent biomni-admin
systemctl start biomni-agent biomni-admin

# ==================== 8. Nginx ====================
echo ">>> [8/8] Configuring Nginx..."

cat > /etc/nginx/sites-available/biomni <<'NGINX'
# WarpHelix - Client (port 80)
server {
    listen 80;
    server_name _;

    # Client frontend
    root /opt/biomni/client-frontend;
    index index.html;

    # SPA fallback
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Admin frontend
    location /admin/ {
        alias /opt/biomni/admin-frontend/;
        try_files $uri $uri/ /admin/index.html;
    }

    # Spring Boot API
    location /api/ {
        proxy_pass http://127.0.0.1:9999/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 600s;
    }

    # Agent API
    location /agent-api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 600s;
    }

    # WebSocket
    location /ws/ {
        proxy_pass http://127.0.0.1:8000/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 3600s;
        proxy_send_timeout 3600s;
    }
}
NGINX

ln -sf /etc/nginx/sites-available/biomni /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

# ==================== Done ====================
echo ""
echo "======================================"
echo "  ✅ WarpHelix Deployed Successfully!"
echo "======================================"
echo ""
echo "  Client UI:  http://$SERVER_IP/"
echo "  Admin UI:   http://$SERVER_IP/admin/"
echo "  MySQL Pass: $MYSQL_ROOT_PASSWORD"
echo ""
echo "  Services:"
echo "    systemctl status biomni-agent"
echo "    systemctl status biomni-admin"
echo ""
echo "  Logs:"
echo "    tail -f $LOG_DIR/agent.log"
echo "    tail -f $LOG_DIR/agent-error.log"
echo ""
echo "  ⚠️  Remember to configure:"
echo "    1. Edit $CONFIG_DIR/biomni.env (add API keys)"
echo "    2. Set up SSL with certbot if needed"
echo "    3. Open ports 80/443 in security group"
echo "======================================"

# Cleanup
rm -rf $TEMP_DIR
