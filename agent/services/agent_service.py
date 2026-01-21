from biomni.agent import A1
from services.mock_agent import MockAgent, MockAgentAsync
from datetime import datetime
from typing import Dict
import asyncio
import re
import os

# Agent 实例池（每个用户一个实例）
agent_pool: Dict[int, A1] = {}

# 是否使用 Mock Agent（通过环境变量控制）
USE_MOCK_AGENT = os.getenv('USE_MOCK_AGENT', 'false').lower() == 'true'

if USE_MOCK_AGENT:
    print("🎭 使用 Mock Agent 模式")
else:
    print("🤖 使用真实 Biomni Agent 模式")

class AgentService:
    
    @staticmethod
    def get_or_create_agent(user_id: int, config: dict = None):
        """获取或创建 Agent 实例"""
        if USE_MOCK_AGENT:
            # 使用 Mock Agent
            if user_id not in agent_pool:
                agent_pool[user_id] = MockAgentAsync(
                    path=config.get('data_path', './data') if config else './data',
                    llm=config.get('llm', 'claude-sonnet-4-5') if config else 'claude-sonnet-4-5',
                )
            return agent_pool[user_id]
        else:
            # 使用真实 A1 Agent
            if user_id not in agent_pool:
                agent_pool[user_id] = A1(
                    path=config.get('data_path', './data') if config else './data',
                    llm=config.get('llm', 'claude-sonnet-4-5') if config else 'claude-sonnet-4-5',
                )
            return agent_pool[user_id]
    
    @staticmethod
    async def execute_agent_stream(
        conversation_id: int,
        user_id: int,
        query: str,
        callback
    ):
        """流式执行 Agent"""
        agent = AgentService.get_or_create_agent(user_id)
        
        if USE_MOCK_AGENT:
            # Mock Agent 是异步的
            async for step in agent.go_stream_async(query):
                output = step.get('output', '')
                usage = step.get('usage', None)
                await callback.process_step(output, usage)
        else:
            # 真实 A1 Agent 是同步的，需要在线程池中执行
            loop = asyncio.get_event_loop()
            
            def run_agent():
                results = []
                for step in agent.go_stream(query):
                    results.append(step)
                return results
            
            steps = await loop.run_in_executor(None, run_agent)
            
            # 处理每个步骤
            for step in steps:
                output = step.get('output', '')
                usage = step.get('usage', None)
                await callback.process_step(output, usage)
        
        return callback.get_result()
