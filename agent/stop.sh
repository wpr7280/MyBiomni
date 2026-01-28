#!/bin/bash

# Biomni Agent 停止脚本
# 用法: ./stop.sh

cd "$(dirname "$0")"

if [ -f agent.pid ]; then
    PID=$(cat agent.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "🛑 停止 Biomni Agent (PID: $PID)..."
        kill $PID
        sleep 2
        
        # 检查是否成功停止
        if ps -p $PID > /dev/null 2>&1; then
            echo "⚠️ 进程未停止，强制终止..."
            kill -9 $PID
        fi
        
        echo "✅ Agent 已停止"
    else
        echo "⚠️ 进程 $PID 不存在"
    fi
    rm agent.pid
else
    echo "⚠️ 未找到 agent.pid 文件"
    echo "尝试查找 python main.py 进程..."
    
    PIDS=$(ps aux | grep "python main.py" | grep -v grep | awk '{print $2}')
    if [ -n "$PIDS" ]; then
        echo "找到进程: $PIDS"
        echo "停止这些进程..."
        kill $PIDS
        echo "✅ 已停止"
    else
        echo "❌ 未找到运行中的 Agent 进程"
    fi
fi
