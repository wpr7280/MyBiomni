#!/bin/bash

# Biomni Agent 启动脚本
# 用法: ./start.sh

cd "$(dirname "$0")"

# 生成日志文件名（带时间戳）
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_OUT="logs/agent_${TIMESTAMP}.out"
LOG_ERR="logs/agent_${TIMESTAMP}.err"

# 确保 logs 目录存在
mkdir -p logs

# 停止旧进程（如果存在）
if [ -f agent.pid ]; then
    OLD_PID=$(cat agent.pid)
    if ps -p $OLD_PID > /dev/null 2>&1; then
        echo "🛑 停止旧进程 (PID: $OLD_PID)..."
        kill $OLD_PID
        sleep 2
    fi
    rm agent.pid
fi

# 启动新进程
echo "🚀 启动 Biomni Agent..."
echo "   stdout → $LOG_OUT"
echo "   stderr → $LOG_ERR"

nohup python main.py > "$LOG_OUT" 2> "$LOG_ERR" &
PID=$!

# 保存 PID
echo $PID > agent.pid
echo "✅ Agent 已启动 (PID: $PID)"

# 创建符号链接到最新日志
ln -sf "$LOG_OUT" logs/latest.out
ln -sf "$LOG_ERR" logs/latest.err

echo ""
echo "查看日志："
echo "  tail -f logs/latest.out    # 查看输出"
echo "  tail -f logs/latest.err    # 查看调试日志"
echo ""
echo "停止服务："
echo "  kill $PID"
echo "  或运行: ./stop.sh"
