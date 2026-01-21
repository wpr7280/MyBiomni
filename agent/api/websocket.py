from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
from sqlalchemy.orm import Session
from typing import Dict
from datetime import datetime

from core.security import verify_jwt_token
from core.database import get_db
from services.agent_service import AgentService
from services.callback import WebSocketCallback

router = APIRouter()

# WebSocket 连接管理器
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, conversation_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[conversation_id] = websocket
        print(f"WebSocket 连接建立: conversation_id={conversation_id}")
    
    def disconnect(self, conversation_id: str):
        if conversation_id in self.active_connections:
            del self.active_connections[conversation_id]
            print(f"WebSocket 连接断开: conversation_id={conversation_id}")
    
    async def send_message(self, conversation_id: str, message: dict):
        if conversation_id in self.active_connections:
            try:
                await self.active_connections[conversation_id].send_json(message)
            except Exception as e:
                print(f"发送消息失败: {e}")

manager = ConnectionManager()

@router.websocket("/chat/{conversation_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    conversation_id: str,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """WebSocket 连接处理"""
    
    # 1. 验证 Token
    payload = verify_jwt_token(token)
    if not payload:
        await websocket.close(code=1008, reason="Invalid token")
        return
    
    user_id = int(payload.get("sub"))
    print(f"用户 {user_id} 连接到对话 {conversation_id}")
    
    # 2. 建立连接
    await manager.connect(conversation_id, websocket)
    
    try:
        while True:
            # 接收前端消息
            data = await websocket.receive_json()
            
            if data['type'] == 'send_message':
                # 执行 Agent
                await handle_agent_execution(
                    conversation_id=int(conversation_id),
                    user_id=user_id,
                    content=data['content'],
                    manager=manager,
                    db=db
                )
    
    except WebSocketDisconnect:
        manager.disconnect(conversation_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(conversation_id)
        await manager.send_message(conversation_id, {
            'type': 'execution_error',
            'error': str(e)
        })

async def handle_agent_execution(
    conversation_id: int,
    user_id: int,
    content: str,
    manager: ConnectionManager,
    db: Session
):
    """执行 Agent 并推送结果"""
    
    try:
        # 0. 检查系统配置是否完成
        from services.config_service import ConfigService
        
        try:
            config = ConfigService.get_agent_config(db)
            
            # 检查必需的配置
            if not config.get('llm'):
                await manager.send_message(str(conversation_id), {
                    'type': 'config_error',
                    'error': '系统尚未配置 LLM 模型，请联系管理员完成配置'
                })
                return
            
            source = config.get('source', 'Anthropic')
            
            # 检查是否配置了对应的 API Key（Ollama 除外）
            if source != 'Ollama':
                # 这里只做基本检查，具体的环境变量设置在 ConfigService 中完成
                # 如果创建 Agent 失败，会在后面捕获异常
                pass
                
        except Exception as config_error:
            await manager.send_message(str(conversation_id), {
                'type': 'config_error',
                'error': f'配置加载失败：{str(config_error)}。请联系管理员检查系统配置'
            })
            return
        
        # 1. 检查配额
        from models.models import UserQuota
        
        quota = db.query(UserQuota).filter(UserQuota.user_id == user_id).first()
        
        if not quota:
            # 如果没有配额记录，创建默认配额
            quota = UserQuota(user_id=user_id, total_token_limit=1000000, total_token_used=0)
            db.add(quota)
            db.commit()
            db.refresh(quota)
        
        if quota.total_token_used >= quota.total_token_limit:
            await manager.send_message(str(conversation_id), {
                'type': 'quota_exceeded',
                'error': f'Token 配额已用完（{quota.total_token_used:,}/{quota.total_token_limit:,}）',
                'quota': {
                    'totalTokenLimit': quota.total_token_limit,
                    'totalTokenUsed': quota.total_token_used,
                    'remaining': 0
                }
            })
            return
        
        # 2. 保存用户消息到数据库
        from models.models import Message, Conversation
        
        user_message = Message(
            conversation_id=conversation_id,
            role='user',
            content=content,
            content_type='text',
            tokens=max(1, len(content) // 4),
            input_tokens=max(1, len(content) // 4),
            output_tokens=0,
            created_at=datetime.now()
        )
        db.add(user_message)
        db.commit()
        db.refresh(user_message)
        
        # 更新对话统计
        conversation = db.query(Conversation).get(conversation_id)
        if (conversation):
            conversation.message_count += 1
            conversation.last_message_at = datetime.now()
            conversation.updated_at = datetime.now()
            db.commit()
        
        # 3. 通知开始执行
        await manager.send_message(str(conversation_id), {
            'type': 'execution_start'
        })
        
        # 4. 创建回调处理器
        callback = WebSocketCallback(
            conversation_id=conversation_id,
            manager=manager,
            db=db,
            user_id=user_id
        )
        callback.current_message_id = user_message.id
        
        # 5. 执行 Agent（流式）
        result = await AgentService.execute_agent_stream(
            conversation_id=conversation_id,
            user_id=user_id,
            query=content,
            callback=callback,
            db=db
        )
        
        # 6. 通知完成
        await manager.send_message(str(conversation_id), {
            'type': 'execution_complete',
            'message': result
        })
        
    except Exception as e:
        error_msg = str(e)
        print(f"Agent 执行失败: {error_msg}")
        import traceback
        traceback.print_exc()
        
        # 检查是否是 API Key 相关错误
        if 'api' in error_msg.lower() and 'key' in error_msg.lower():
            error_msg = f'LLM API Key 配置错误：{error_msg}。请联系管理员检查配置'
        elif 'anthropic' in error_msg.lower() or 'openai' in error_msg.lower():
            error_msg = f'LLM 服务连接失败：{error_msg}。请联系管理员检查配置'
        
        await manager.send_message(str(conversation_id), {
            'type': 'execution_error',
            'error': error_msg
        })
