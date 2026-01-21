from biomni.agent import A1
from services.mock_agent import MockAgent, MockAgentAsync
from services.config_service import ConfigService
from datetime import datetime
from typing import Dict
import asyncio
import re
import os

# Agent 实例池（每个用户一个实例）
agent_pool: Dict[int, tuple] = {}  # {user_id: (config_hash, agent)}

# 是否使用 Mock Agent（通过环境变量控制）
USE_MOCK_AGENT = os.getenv('USE_MOCK_AGENT', 'false').lower() == 'true'

if USE_MOCK_AGENT:
    print("🎭 使用 Mock Agent 模式")
else:
    print("🤖 使用真实 Biomni Agent 模式")

class AgentService:
    
    @staticmethod
    def get_or_create_agent(user_id: int, db):
        """获取或创建 Agent 实例"""
        if USE_MOCK_AGENT:
            # Mock Agent 不需要配置
            if user_id not in agent_pool:
                agent_pool[user_id] = (None, MockAgentAsync(
                    path='./data',
                    llm='claude-sonnet-4-5',
                ))
            return agent_pool[user_id][1]
        
        # 从数据库加载配置
        config = ConfigService.get_agent_config(db)
        
        # 计算配置哈希（用于检测配置变更）
        import hashlib
        import json
        config_str = json.dumps(config, sort_keys=True)
        config_hash = hashlib.md5(config_str.encode()).hexdigest()
        
        # 检查是否已有实例且配置未变更
        if user_id in agent_pool:
            cached_hash, cached_agent = agent_pool[user_id]
            if cached_hash == config_hash:
                print(f"✓ 使用缓存的 Agent 实例（用户 {user_id}）")
                return cached_agent
            else:
                print(f"⚠ 配置已变更，创建新的 Agent 实例（用户 {user_id}）")
        
        # 创建新的 Agent 实例
        print(f"🔧 创建 Agent 实例（用户 {user_id}）")
        print(f"   LLM: {config.get('llm', 'claude-sonnet-4-5')}")
        print(f"   Source: {config.get('source', 'Anthropic')}")
        print(f"   Temperature: {config.get('temperature', 0.7)}")
        
        agent = A1(
            path=config.get('path', './data'),
            llm=config.get('llm', 'claude-sonnet-4-5'),
            source=config.get('source'),
            temperature=config.get('temperature', 0.7),
            base_url=config.get('base_url'),
            api_key=config.get('api_key'),
            timeout_seconds=config.get('timeout_seconds', 600),
            use_tool_retriever=config.get('use_tool_retriever', True),
            commercial_mode=config.get('commercial_mode', False)
        )
        
        # 缓存实例
        agent_pool[user_id] = (config_hash, agent)
        
        return agent
    
    @staticmethod
    async def execute_agent_stream(
        conversation_id: int,
        user_id: int,
        query: str,
        callback,
        db
    ):
        """流式执行 Agent"""
        agent = AgentService.get_or_create_agent(user_id, db)
        
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
