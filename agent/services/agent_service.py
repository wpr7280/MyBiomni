from biomni.agent import A1
from services.mock_agent import MockAgent, MockAgentAsync
from services.config_service import ConfigService
from datetime import datetime
from typing import Dict
import asyncio
import re
import os
import threading

# Agent 实例池（每个用户一个实例）
agent_pool: Dict[int, tuple] = {}  # {user_id: (config_hash, agent)}
_agent_pool_lock = threading.Lock()  # 线程安全锁

# 是否使用 Mock Agent（通过环境变量控制）
USE_MOCK_AGENT = os.getenv('USE_MOCK_AGENT', 'false').lower() == 'true'

if USE_MOCK_AGENT:
    print("🎭 使用 Mock Agent 模式")
else:
    print("🤖 使用真实 WarpHelix Agent 模式")

class AgentService:
    
    @staticmethod
    def get_or_create_agent(user_id: int, db):
        """获取或创建 Agent 实例（线程安全）"""
        if USE_MOCK_AGENT:
            with _agent_pool_lock:
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
        
        with _agent_pool_lock:
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
        with _agent_pool_lock:
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
            # 真实 A1 Agent 是同步的，使用线程 + asyncio.Queue 实现真正流式
            loop = asyncio.get_event_loop()
            queue: asyncio.Queue = asyncio.Queue()
            stop_sentinel = object()

            # Load chat history from DB for context
            from models.models import Message as DBMessage
            history_rows = (
                db.query(DBMessage)
                .filter(
                    DBMessage.conversation_id == conversation_id,
                    DBMessage.role.in_(['user', 'assistant']),
                )
                .order_by(DBMessage.created_at.asc())
                .all()
            )
            # Exclude the current message (last user message just inserted)
            # and limit to last 20 messages to avoid token overflow
            if history_rows:
                # The last row is the message we just inserted, skip it
                history_rows = history_rows[:-1]
                # Keep only the last 20 messages for context
                history_rows = history_rows[-20:]
            
            chat_history = [(row.role, row.content) for row in history_rows] if history_rows else None

            def run_agent_stream():
                try:
                    for step in agent.go_stream(query, thread_id=conversation_id, chat_history=chat_history):
                        loop.call_soon_threadsafe(queue.put_nowait, step)
                except Exception as e:
                    loop.call_soon_threadsafe(queue.put_nowait, {"__error__": str(e)})
                finally:
                    loop.call_soon_threadsafe(queue.put_nowait, stop_sentinel)

            thread = threading.Thread(target=run_agent_stream, daemon=True)
            thread.start()

            # 逐步处理输出（实时推送）
            while True:
                step = await queue.get()
                if step is stop_sentinel:
                    break
                if isinstance(step, dict) and step.get("__error__"):
                    raise RuntimeError(step["__error__"])

                output = step.get('output', '')
                usage = step.get('usage', None)
                await callback.process_step(output, usage)
            print("✓ 开始调用 callback.get_result()")
            result = callback.get_result()
            print(f"✓ get_result() 返回: message_id={result.get('id')}")
            return result
