#!/bin/bash

# Backend 服务部署脚本
# 目标服务器: root@39.103.178.214
# 部署路径: /root/biomni/app

set -e

# 配置
SERVER="root@39.103.178.214"
REMOTE_PATH="/root/biomni/app"
JAR_NAME="biomni-backend-0.0.1-SNAPSHOT.jar"

echo "=========================================="
echo "  Backend 服务部署脚本"
echo "=========================================="

# 1. Maven 打包
echo ""
echo "[1/4] 正在打包..."
mvn clean package -DskipTests -q

if [ ! -f "target/${JAR_NAME}" ]; then
    echo "错误: 打包失败，找不到 target/${JAR_NAME}"
    exit 1
fi

echo "打包完成: target/${JAR_NAME}"

# 2. 上传到服务器
echo ""
echo "[2/4] 上传到服务器..."
ssh ${SERVER} "mkdir -p ${REMOTE_PATH}"
scp target/${JAR_NAME} ${SERVER}:${REMOTE_PATH}/

echo "上传完成"

# 3. 重启服务
echo ""
echo "[3/4] 重启服务..."
ssh ${SERVER} << 'EOF'
cd /root/biomni/app

# 停止旧进程
PID=$(pgrep -f "biomni-backend-0.0.1-SNAPSHOT.jar" || true)
if [ -n "$PID" ]; then
    echo "停止旧进程: $PID"
    kill $PID
    sleep 3
fi

# 启动新进程
nohup java -jar biomni-backend-0.0.1-SNAPSHOT.jar --spring.profiles.active=prod > backend.log 2>&1 &

sleep 2
NEW_PID=$(pgrep -f "biomni-backend-0.0.1-SNAPSHOT.jar" || true)
if [ -n "$NEW_PID" ]; then
    echo "服务已启动，PID: $NEW_PID"
else
    echo "警告: 服务可能启动失败，请检查日志"
fi
EOF

# 4. 完成
echo ""
echo "[4/4] 部署完成!"
echo "=========================================="
echo "查看日志: ssh ${SERVER} 'tail -f ${REMOTE_PATH}/backend.log'"
echo "=========================================="
