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
        
        # 在创建 A1 之前，修改 default_config 来设置 temperature 和 max_tokens
        from biomni.config import default_config
        if 'temperature' in config:
            default_config.temperature = config['temperature']
            print(f"   Temperature: {config['temperature']} (via default_config)")
        if 'max_tokens' in config:
            default_config.max_tokens = config['max_tokens']
            print(f"   Max Tokens: {config['max_tokens']} (via default_config)")
        
        # 创建新的 Agent 实例
        print(f"🔧 创建 Agent 实例（用户 {user_id}）")
        print(f"   Path: {config.get('path', './data')}")
        print(f"   LLM: {config.get('llm', 'claude-sonnet-4-5')}")
        print(f"   Source: {config.get('source', 'Anthropic')}")
        print(f"   Base URL: {config.get('base_url', 'None')}")
        print(f"   Timeout: {config.get('timeout_seconds', 600)}s")
        print(f"   Tool Retriever: {config.get('use_tool_retriever', True)}")
        print(f"   Commercial Mode: {config.get('commercial_mode', False)}")
        
        # A1 只接受这些参数（temperature 通过 default_config 设置）
        agent = A1(
            path=config.get('path', './data'),
            llm=config.get('llm', 'claude-sonnet-4-5'),
            source=config.get('source'),  # 可选: "OpenAI", "Anthropic", "Ollama", "Gemini", "Bedrock", "Custom"
            use_tool_retriever=config.get('use_tool_retriever', True),
            timeout_seconds=config.get('timeout_seconds', 600),
            base_url=config.get('base_url'),  # 自定义模型服务的 URL
            api_key=config.get('api_key'),  # API 密钥
            commercial_mode=config.get('commercial_mode', False),  # 商业模式（排除非商业数据集）
            expected_data_lake_files=None  # None = 自动下载所有数据
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
            # 真实 A1 Agent 是同步的，需要在线程中流式处理
            import asyncio
            import queue
            import threading
            
            # 创建队列用于线程间通信
            step_queue = queue.Queue()
            
            def run_agent_in_thread():
                """在线程中运行 Agent，将步骤放入队列"""
                try:
                    for step in agent.go_stream(query):
                        step_queue.put(('step', step))
                    step_queue.put(('done', None))
                except Exception as e:
                    step_queue.put(('error', str(e)))
            
            # 启动线程
            thread = threading.Thread(target=run_agent_in_thread, daemon=True)
            thread.start()
            
            # 异步处理队列中的步骤
            while True:
                try:
                    # 非阻塞获取，避免卡住事件循环
                    msg_type, data = await asyncio.get_event_loop().run_in_executor(
                        None, step_queue.get, True, 0.1  # 100ms 超时
                    )
                    
                    if msg_type == 'step':
                        output = data.get('output', '')
                        usage = data.get('usage', None)
                        await callback.process_step(output, usage)
                    elif msg_type == 'done':
                        break
                    elif msg_type == 'error':
                        raise Exception(f"Agent execution error: {data}")
                        
                except queue.Empty:
                    # 队列为空，继续等待
                    await asyncio.sleep(0.1)
                    continue
        
        return callback.get_result()
