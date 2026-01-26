#!/bin/bash

# Biomni Admin Frontend PM2 启动脚本
set -e

echo "=========================================="
echo "Biomni Admin Frontend PM2 启动"
echo "=========================================="

# 进入项目目录
cd "$(dirname "$0")"

# 检查 PM2 是否安装
if ! command -v pm2 &> /dev/null; then
    echo "错误: PM2 未安装"
    echo "请运行: npm install -g pm2"
    exit 1
fi

# 检查 pnpm 是否安装
if ! command -v pnpm &> /dev/null; then
    echo "错误: pnpm 未安装"
    echo "请运行: npm install -g pnpm"
    exit 1
fi

# 安装依赖
echo "检查依赖..."
if [ ! -d "node_modules" ]; then
    echo "安装依赖..."
    pnpm install
fi

# 构建项目
echo "构建项目..."
pnpm run build

# 停止旧进程（如果存在）
echo "停止旧进程..."
pm2 delete biomni-admin-frontend 2>/dev/null || true

# 启动新进程
echo "启动服务..."
pm2 start ecosystem.config.js

# 保存 PM2 配置
pm2 save

echo ""
echo "=========================================="
echo "启动完成！"
echo "=========================================="
echo "访问地址: http://localhost:3000"
echo ""
echo "常用命令:"
echo "  查看状态: pm2 list"
echo "  查看日志: pm2 logs biomni-admin-frontend"
echo "  重启服务: pm2 restart biomni-admin-frontend"
echo "  停止服务: pm2 stop biomni-admin-frontend"
echo "=========================================="
