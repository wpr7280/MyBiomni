#!/usr/bin/env python3
"""
诊断 Execution Steps 问题的脚本
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.database import get_db
from models.models import ExecutionStep, Conversation, Message
from sqlalchemy import desc

def diagnose_conversation(conversation_id: int):
    """诊断指定对话的步骤保存情况"""
    db = next(get_db())
    
    print(f"\n{'='*80}")
    print(f"🔍 诊断对话 {conversation_id}")
    print(f"{'='*80}")
    
    # 1. 检查 conversation
    conversation = db.query(Conversation).get(conversation_id)
    if not conversation:
        print(f"❌ Conversation {conversation_id} 不存在")
        return
    
    print(f"\n📊 Conversation 信息:")
    print(f"   ID: {conversation.id}")
    print(f"   User ID: {conversation.user_id}")
    print(f"   Title: {conversation.title}")
    print(f"   Status: {conversation.status}")
    print(f"   Message Count: {conversation.message_count}")
    print(f"   Total Tokens: {conversation.total_tokens}")
    print(f"   Total Duration: {conversation.total_duration_ms}ms")
    print(f"   Last Message At: {conversation.last_message_at}")
    print(f"   Updated At: {conversation.updated_at}")
    
    # 2. 检查 messages
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.id).all()
    
    print(f"\n💬 Messages ({len(messages)} 条):")
    for msg in messages:
        print(f"   [{msg.id}] {msg.role}: {msg.content[:100]}... (tokens: {msg.tokens})")
    
    # 3. 检查 execution_steps
    steps = db.query(ExecutionStep).filter(
        ExecutionStep.conversation_id == conversation_id
    ).order_by(ExecutionStep.step_order).all()
    
    print(f"\n🔧 Execution Steps ({len(steps)} 个):")
    for step in steps:
        print(f"   [{step.id}] Step {step.step_order}: {step.step_type} - {step.step_name}")
        print(f"        Status: {step.status}, Duration: {step.duration_ms}ms")
        if step.tool_output:
            print(f"        Output: {step.tool_output[:100]}...")
    
    # 4. 检查步骤顺序是否连续
    print(f"\n🔢 步骤顺序检查:")
    step_orders = [s.step_order for s in steps]
    if step_orders:
        expected = list(range(1, len(steps) + 1))
        if step_orders == expected:
            print(f"   ✅ 步骤顺序连续: {step_orders}")
        else:
            print(f"   ❌ 步骤顺序不连续:")
            print(f"      实际: {step_orders}")
            print(f"      预期: {expected}")
            missing = set(expected) - set(step_orders)
            if missing:
                print(f"      缺失: {sorted(missing)}")
    else:
        print(f"   ⚠️ 没有步骤记录")
    
    # 5. 统计步骤类型
    print(f"\n📈 步骤类型统计:")
    from collections import Counter
    type_counts = Counter([s.step_type for s in steps])
    for step_type, count in type_counts.items():
        print(f"   {step_type}: {count}")
    
    # 6. 检查是否有图片
    print(f"\n🖼️ 图片检查:")
    steps_with_images = [s for s in steps if s.step_type == 'result']
    if steps_with_images:
        print(f"   找到 {len(steps_with_images)} 个 result 步骤（可能包含图片）")
    else:
        print(f"   ⚠️ 没有 result 步骤")
    
    print(f"\n{'='*80}")
    print(f"✅ 诊断完成")
    print(f"{'='*80}")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        conversation_id = int(sys.argv[1])
    else:
        # 默认诊断最新的对话
        db = next(get_db())
        latest = db.query(Conversation).order_by(desc(Conversation.id)).first()
        if latest:
            conversation_id = latest.id
            print(f"📌 使用最新对话: {conversation_id}")
        else:
            print("❌ 没有找到任何对话")
            sys.exit(1)
    
    diagnose_conversation(conversation_id)
