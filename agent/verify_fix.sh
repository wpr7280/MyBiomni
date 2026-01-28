#!/bin/bash

echo "🔍 验证 Execution Steps 修复"
echo "========================================"

# 1. 检查代码修改
echo ""
echo "1️⃣ 检查关键代码修改..."
if grep -q "<observe>" services/callback.py; then
    echo "   ✅ callback.py 已支持 <observe> 标签"
else
    echo "   ❌ callback.py 未支持 <observe> 标签"
fi

if grep -q "print(f\"✓ Saved reasoning step" services/callback.py; then
    echo "   ✅ callback.py 已添加调试日志"
else
    echo "   ❌ callback.py 缺少调试日志"
fi

# 2. 运行测试脚本
echo ""
echo "2️⃣ 运行测试脚本..."
python test_callback.py 2>&1 | head -50

# 3. 检查最新对话
echo ""
echo "3️⃣ 诊断最新对话..."
python diagnose_steps.py

# 4. 提示下一步
echo ""
echo "========================================"
echo "✅ 验证完成"
echo ""
echo "下一步："
echo "  1. 重启服务: python main.py"
echo "  2. 在前端发送测试消息"
echo "  3. 观察后端日志中的步骤保存信息"
echo "  4. 检查前端 Execution Panel 显示"
echo ""
