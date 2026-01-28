#!/usr/bin/env python3
"""
测试 WebSocketCallback 是否正确处理所有步骤
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.callback import WebSocketCallback
from core.database import get_db
from datetime import datetime

# 模拟的 WebSocket manager
class MockManager:
    async def send_message(self, conversation_id, message):
        print(f"📤 WebSocket 消息: {message['type']}")
        if message['type'] == 'execution_step':
            step = message['step']
            print(f"   Step {step['stepOrder']}: {step['stepType']} - {step['stepName']}")

# 测试数据（从 log20 提取）
test_outputs = [
    # Step 1: 初始推理
    """I'll help you explore how different perturbations affect protein expression. Let me start by creating a comprehensive plan to investigate this topic.

## Plan
1. [ ] Search for literature on perturbations and protein expression
2. [ ] Query relevant databases for protein expression data
3. [ ] Demonstrate simulations of how perturbations affect protein signaling networks
4. [ ] Analyze real data on CRISPR perturbations and their effects on protein expression
5. [ ] Create visualizations showing perturbation effects
6. [ ] Summarize findings and provide insights

Let me start executing this plan:
<execute>
# Step 1: Search for literature on perturbations and protein expression
from biomni.tool.literature import query_pubmed

print("=" * 80)
print("STEP 1: Searching for literature on perturbations and protein expression")
print("=" * 80)

query = "perturbations protein expression effects"
results = query_pubmed(query, max_papers=5)
print(results)
</execute>""",

    # Step 2: Observation
    """<observe>
The function executed and returned literature search results about perturbations and protein expression effects.
</observe>""",

    # Step 3: 下一步推理
    """Now let me query databases for relevant protein and expression data:
<execute>
# Step 2: Query databases for protein expression data
from biomni.tool.database import query_kegg, query_uniprot

print("\\n" + "=" * 80)
print("STEP 2: Querying databases for protein expression and signaling pathways")
print("=" * 80)

# Query KEGG for signaling pathways
kegg_result = query_kegg("protein signaling pathways and regulatory networks", verbose=True)
print("\\nKEGG Signaling Pathways:")
print(kegg_result)
</observe>""",

    # Step 4: Observation
    """<observe>
KEGG query returned information about protein signaling pathways and regulatory networks.
</observe>""",

    # Step 5: 继续推理
    """Now let me demonstrate how to simulate protein expression changes under different perturbations:
<execute>
# Step 3: Simulate protein signaling network with perturbations
from biomni.tool.systems_biology import simulate_protein_signaling_network
import numpy as np
import matplotlib.pyplot as plt

print("\\n" + "=" * 80)
print("STEP 3: Simulating protein signaling networks under different perturbations")
print("=" * 80)
</execute>"""
]

async def test_callback():
    """测试 callback 处理"""
    print("🧪 开始测试 WebSocketCallback")
    print("="*80)
    
    # 创建 mock 对象
    manager = MockManager()
    db = next(get_db())
    
    # 创建 callback
    callback = WebSocketCallback(
        conversation_id=999,
        manager=manager,
        db=db,
        user_id=1
    )
    
    # 处理每个输出
    for i, output in enumerate(test_outputs, 1):
        print(f"\n{'='*80}")
        print(f"测试输出 {i}/{len(test_outputs)}")
        print(f"{'='*80}")
        await callback.process_step(output)
    
    print(f"\n{'='*80}")
    print(f"✅ 测试完成")
    print(f"{'='*80}")
    print(f"总步骤数: {callback.step_order}")
    print(f"预期步骤数: ~10 (包括 reasoning, tool_call, result)")
    
    if callback.step_order < 8:
        print(f"⚠️ 警告: 步骤数太少！应该有更多步骤被保存")
    else:
        print(f"✓ 步骤数正常")

if __name__ == '__main__':
    asyncio.run(test_callback())
