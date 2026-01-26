#!/bin/bash

# Biomni Client Frontend PM2 启动脚本
set -e

echo "=========================================="
echo "Biomni Client Frontend PM2 启动"
echo "=========================================="

# 进入项目目录
cd "$(dirname "$0")"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 PM2 是否安装
if ! command -v pm2 &> /dev/null; then
    echo -e "${RED}错误: PM2 未安装${NC}"
    echo "请运行: npm install -g pm2"
    exit 1
fi

# 检查 npm 是否安装
if ! command -v npm &> /dev/null; then
    echo -e "${RED}错误: npm 未安装${NC}"
    exit 1
fi

# 创建日志目录
mkdir -p logs

# 检查 .env.development 文件
if [ ! -f ".env.development" ]; then
    echo -e "${RED}错误: .env.development 文件不存在${NC}"
    echo "请创建 .env.development 文件并配置远端 API 地址"
    exit 1
fi

echo -e "${YELLOW}当前环境配置:${NC}"
cat .env.development
echo ""

# 安装依赖
echo -e "${YELLOW}检查依赖...${NC}"
if [ ! -d "node_modules" ]; then
    echo "安装依赖..."
    npm install
else
    echo -e "${GREEN}✓ 依赖已安装${NC}"
fi

# 停止旧进程（如果存在）
echo -e "${YELLOW}停止旧进程...${NC}"
pm2 delete biomni-client-frontend 2>/dev/null || true

# 启动新进程
echo -e "${YELLOW}启动服务...${NC}"
pm2 start ecosystem.config.cjs

# 保存 PM2 配置
pm2 save

echo ""
echo "=========================================="
echo -e "${GREEN}启动完成！${NC}"
echo "=========================================="
echo "访问地址: http://localhost:5173"
echo ""
echo "常用命令:"
echo "  查看状态: pm2 list"
echo "  查看日志: pm2 logs biomni-client-frontend"
echo "  实时日志: pm2 logs biomni-client-frontend --lines 100"
echo "  重启服务: pm2 restart biomni-client-frontend"
echo "  停止服务: pm2 stop biomni-client-frontend"
echo "  删除服务: pm2 delete biomni-client-frontend"
echo "=========================================="
