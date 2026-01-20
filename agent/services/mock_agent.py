import asyncio
import random

class MockAgent:
    """Mock Agent 用于测试，模拟 A1 的行为"""
    
    def __init__(self, path: str = './data', llm: str = 'claude-sonnet-4-5'):
        self.path = path
        self.llm = llm
        print(f"🎭 Mock Agent 初始化: path={path}, llm={llm}")
    
    def go_stream(self, query: str):
        """模拟流式输出"""
        
        # 步骤 1: 思考
        yield {
            'output': f"Let me analyze your question: {query}\n\nI'll break this down into steps..."
        }
        
        # 步骤 2: 执行代码
        yield {
            'output': """
<execute>
# 分析问题
import pandas as pd
import numpy as np

print("正在分析数据...")
data = pd.DataFrame({
    'gene': ['GENE1', 'GENE2', 'GENE3'],
    'expression': [1.5, 2.3, 0.8]
})
print(data)
</execute>
"""
        }
        
        # 步骤 3: 观察结果
        yield {
            'output': """
<observation>
正在分析数据...
   gene  expression
0  GENE1         1.5
1  GENE2         2.3
2  GENE3         0.8
</observation>
"""
        }
        
        # 步骤 4: 再次执行
        yield {
            'output': """
<execute>
# 进一步分析
result = data[data['expression'] > 1.0]
print(f"找到 {len(result)} 个高表达基因")
print(result)
</execute>
"""
        }
        
        # 步骤 5: 观察结果
        yield {
            'output': """
<observation>
找到 2 个高表达基因
   gene  expression
0  GENE1         1.5
1  GENE2         2.3
</observation>
"""
        }
        
        # 步骤 6: 最终答案
        yield {
            'output': f"""
Based on the analysis, here are the findings:

<solution>
## 分析结果

根据您的问题 "{query}"，我为您整理了以下信息：

### 1. 数据分析
- 总共分析了 3 个基因
- 发现 2 个高表达基因（表达量 > 1.0）

### 2. 高表达基因列表
1. **GENE1**: 表达量 1.5
2. **GENE2**: 表达量 2.3

### 3. 建议
- GENE2 显示最高表达量，建议优先关注
- 可以进一步进行功能富集分析
- 建议验证这些基因在相关通路中的作用

如果您需要更详细的分析，请告诉我！
</solution>
"""
        }

class MockAgentAsync:
    """异步 Mock Agent，带延迟模拟真实执行"""
    
    def __init__(self, path: str = './data', llm: str = 'claude-sonnet-4-5'):
        self.path = path
        self.llm = llm
        print(f"🎭 Mock Agent (Async) 初始化: path={path}, llm={llm}")
    
    async def go_stream_async(self, query: str):
        """异步流式输出，带延迟"""
        
        # 步骤 1: 思考（延迟 500ms）
        await asyncio.sleep(0.5)
        yield {
            'output': f"Let me analyze your question: {query}\n\nI'll break this down into steps..."
        }
        
        # 步骤 2: 执行代码（延迟 1s）
        await asyncio.sleep(1.0)
        yield {
            'output': """
<execute>
# 分析问题
import pandas as pd
import numpy as np

print("正在分析数据...")
data = pd.DataFrame({
    'gene': ['GENE1', 'GENE2', 'GENE3'],
    'expression': [1.5, 2.3, 0.8]
})
print(data)
</execute>
"""
        }
        
        # 步骤 3: 观察结果（延迟 800ms）
        await asyncio.sleep(0.8)
        yield {
            'output': """
<observation>
正在分析数据...
   gene  expression
0  GENE1         1.5
1  GENE2         2.3
2  GENE3         0.8
</observation>
"""
        }
        
        # 步骤 4: 再次执行（延迟 1.2s）
        await asyncio.sleep(1.2)
        yield {
            'output': """
<execute>
# 进一步分析
result = data[data['expression'] > 1.0]
print(f"找到 {len(result)} 个高表达基因")
print(result)
</execute>
"""
        }
        
        # 步骤 5: 观察结果（延迟 600ms）
        await asyncio.sleep(0.6)
        yield {
            'output': """
<observation>
找到 2 个高表达基因
   gene  expression
0  GENE1         1.5
1  GENE2         2.3
</observation>
"""
        }
        
        # 步骤 6: 最终答案（延迟 1.5s）
        await asyncio.sleep(1.5)
        yield {
            'output': f"""
Based on the analysis, here are the findings:

<solution>
## 分析结果

根据您的问题 "{query}"，我为您整理了以下信息：

### 1. 数据分析
- 总共分析了 3 个基因
- 发现 2 个高表达基因（表达量 > 1.0）

### 2. 高表达基因列表
1. **GENE1**: 表达量 1.5
2. **GENE2**: 表达量 2.3

### 3. 建议
- GENE2 显示最高表达量，建议优先关注
- 可以进一步进行功能富集分析
- 建议验证这些基因在相关通路中的作用

如果您需要更详细的分析，请告诉我！
</solution>
"""
        }
