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
        # 1. 保存用户消息到数据库
        from models.models import Message, Conversation
        
        user_message = Message(
            conversation_id=conversation_id,
            role='user',
            content=content,
            content_type='text',
            tokens=max(1, len(content) // 4),  # 简单估算
            input_tokens=max(1, len(content) // 4),
            output_tokens=0,
            created_at=datetime.now()
        )
        db.add(user_message)
        db.commit()
        db.refresh(user_message)
        
        # 更新对话统计
        conversation = db.query(Conversation).get(conversation_id)
        if conversation:
            conversation.message_count += 1
            conversation.last_message_at = datetime.now()
            conversation.updated_at = datetime.now()
            db.commit()
        
        # 2. 通知开始执行
        await manager.send_message(str(conversation_id), {
            'type': 'execution_start'
        })
        
        # 3. 创建回调处理器
        callback = WebSocketCallback(
            conversation_id=conversation_id,
            manager=manager,
            db=db
        )
        callback.current_message_id = user_message.id
        
        # 4. 执行 Agent（流式）
        result = await AgentService.execute_agent_stream(
            conversation_id=conversation_id,
            user_id=user_id,
            query=content,
            callback=callback
        )
        
        # 5. 通知完成
        await manager.send_message(str(conversation_id), {
            'type': 'execution_complete',
            'message': result
        })
        
    except Exception as e:
        print(f"Agent 执行失败: {e}")
        import traceback
        traceback.print_exc()
        await manager.send_message(str(conversation_id), {
            'type': 'execution_error',
            'error': str(e)
        })
