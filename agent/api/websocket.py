from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
from sqlalchemy.orm import Session
from typing import Dict
from datetime import datetime

from core.security import verify_jwt_token
from core.database import get_db
from services.agent_service import AgentService
from services.callback import WebSocketCallback

router = APIRouter()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.active_executions: Dict[str, bool] = {}  # Track which conversations are executing
    
    async def connect(self, conversation_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[conversation_id] = websocket
        print(f"WebSocket connected: conversation_id={conversation_id}")
        
        # If this conversation was executing, notify the client to resume
        if self.active_executions.get(conversation_id):
            try:
                await websocket.send_json({
                    'type': 'execution_resumed',
                    'message': 'Reconnected to an active execution. Steps will continue streaming.'
                })
            except Exception:
                pass
    
    def disconnect(self, conversation_id: str):
        if conversation_id in self.active_connections:
            del self.active_connections[conversation_id]
            print(f"WebSocket disconnected: conversation_id={conversation_id}")
    
    def set_executing(self, conversation_id: str, executing: bool):
        if executing:
            self.active_executions[conversation_id] = True
        else:
            self.active_executions.pop(conversation_id, None)
    
    def is_executing(self, conversation_id: str) -> bool:
        return self.active_executions.get(conversation_id, False)
    
    async def send_message(self, conversation_id: str, message: dict):
        if conversation_id in self.active_connections:
            try:
                await self.active_connections[conversation_id].send_json(message)
            except Exception as e:
                print(f"Failed to send message: {e}")

manager = ConnectionManager()


@router.get("/execution-status/{conversation_id}")
async def get_execution_status(conversation_id: str):
    """Check if a conversation is currently executing."""
    return {
        "conversationId": conversation_id,
        "executing": manager.is_executing(conversation_id),
    }


@router.websocket("/chat/{conversation_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    conversation_id: str,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """WebSocket connection handler"""
    
    # 1. Verify Token
    payload = verify_jwt_token(token)
    if not payload:
        await websocket.close(code=1008, reason="Invalid token")
        return
    
    user_id = int(payload.get("sub"))
    print(f"User {user_id} connected to conversation {conversation_id}")
    
    # 2. Establish connection
    await manager.connect(conversation_id, websocket)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            if data['type'] == 'send_message':
                # Execute Agent
                await handle_agent_execution(
                    conversation_id=int(conversation_id),
                    user_id=user_id,
                    content=data['content'],
                    file_ids=data.get('file_ids', []),
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
    file_ids: list[int] | None,
    manager: ConnectionManager,
    db: Session
):
    """Execute Agent and push results"""
    
    try:
        # 0. Check system configuration
        from services.config_service import ConfigService
        
        try:
            config = ConfigService.get_agent_config(db)
            
            # Check required configuration
            if not config.get('llm'):
                await manager.send_message(str(conversation_id), {
                    'type': 'config_error',
                    'error': 'LLM model not configured. Please ask the administrator to complete the configuration.'
                })
                return
            
            source = config.get('source', 'Anthropic')
            
            # Check if API Key is configured (except Ollama)
            if source != 'Ollama':
                # Basic check only; env vars are set in ConfigService
                # If Agent creation fails, the exception is caught below
                pass
                
        except Exception as config_error:
            await manager.send_message(str(conversation_id), {
                'type': 'config_error',
                'error': f'Failed to load configuration: {str(config_error)}. Please contact the administrator.'
            })
            return
        
        # 1. Check quota
        from models.models import UserQuota
        
        quota = db.query(UserQuota).filter(UserQuota.user_id == user_id).first()
        
        if not quota:
            # Create default quota if none exists
            quota = UserQuota(user_id=user_id, total_token_limit=1000000, total_token_used=0)
            db.add(quota)
            db.commit()
            db.refresh(quota)
        
        if quota.total_token_used >= quota.total_token_limit:
            await manager.send_message(str(conversation_id), {
                'type': 'quota_exceeded',
                'error': f'Token quota exhausted ({quota.total_token_used:,}/{quota.total_token_limit:,})',
                'quota': {
                    'totalTokenLimit': quota.total_token_limit,
                    'totalTokenUsed': quota.total_token_used,
                    'remaining': 0
                }
            })
            return
        
        # 2. Save user message to database
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
        
        # Update conversation stats
        conversation = db.query(Conversation).get(conversation_id)
        if (conversation):
            conversation.message_count += 1
            conversation.last_message_at = datetime.now()
            conversation.updated_at = datetime.now()
            
            # Auto-generate title from first user message
            if conversation.message_count == 1 and (not conversation.title or conversation.title.startswith('Chat #') or conversation.title == 'New Chat'):
                # Truncate user query to make a title (max 50 chars)
                title = content.strip().replace('\n', ' ')
                if len(title) > 50:
                    title = title[:47] + '...'
                conversation.title = title
            
            db.commit()
        
        # 2.1 Handle uploaded files (bind message_id, append to prompt)
        content_with_files = content
        if file_ids:
            from models.models import Attachment
            import os

            attachments = (
                db.query(Attachment)
                .filter(Attachment.id.in_(file_ids), Attachment.user_id == user_id)
                .all()
            )
            
            if attachments:
                file_info_lines = ["\n\n--- Uploaded Files ---"]
                for attachment in attachments:
                    attachment.conversation_id = conversation_id
                    attachment.message_id = user_message.id
                    
                    file_size = attachment.size
                    size_str = f"{file_size / 1024:.1f} KB" if file_size < 1024 * 1024 else f"{file_size / (1024*1024):.1f} MB"
                    mime = attachment.mime_type or "unknown"
                    
                    file_info_lines.append(
                        f"- File: `{attachment.filename}` ({size_str}, {mime})"
                        f"\n  Path: `{attachment.path}`"
                    )
                    
                    # For small text/csv files, include a preview
                    if file_size < 50000 and mime in ('text/csv', 'text/plain', 'text/tab-separated-values',
                                                       'application/json', 'text/markdown'):
                        try:
                            with open(attachment.path, 'r', encoding='utf-8', errors='replace') as f:
                                preview = f.read(2000)
                            file_info_lines.append(f"  Preview (first 2000 chars):\n```\n{preview}\n```")
                        except Exception:
                            pass
                
                file_info_lines.append("\nYou can read these files using their full path in your <execute> code. For example: `pd.read_csv('/path/to/file.csv')`")
                file_info_lines.append("---")
                content_with_files += "\n".join(file_info_lines)
                db.commit()

        # 3. Notify execution start
        manager.set_executing(str(conversation_id), True)
        await manager.send_message(str(conversation_id), {
            'type': 'execution_start'
        })
        
        # 4. Create callback handler
        callback = WebSocketCallback(
            conversation_id=conversation_id,
            manager=manager,
            db=db,
            user_id=user_id
        )
        # Note: don't set current_message_id, keep it at 0
        callback.current_message_id = user_message.id
        # Execution steps will be batch-updated to assistant_message.id in get_result()
        
        # 5. Execute Agent (streaming)
        print(f"🚀 Starting Agent: conversation_id={conversation_id}, user_id={user_id}")
        result = await AgentService.execute_agent_stream(
            conversation_id=conversation_id,
            user_id=user_id,
            query=content_with_files,
            callback=callback,
            db=db
        )
        print(f"✓ Agent execution complete, result: {result}")
        
        # 6. Notify completion
        manager.set_executing(str(conversation_id), False)
        await manager.send_message(str(conversation_id), {
            'type': 'execution_complete',
            'message': result
        })
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Agent execution failed: {error_msg}")
        import traceback
        traceback.print_exc()
        
        manager.set_executing(str(conversation_id), False)
        
        # User-friendly error messages
        user_friendly_error = error_msg
        
        # Check common error types
        if 'Read timeout' in error_msg or 'ReadTimeoutError' in error_msg:
            user_friendly_error = '⏱️ LLM service timed out. Please try again later or ask the administrator to increase the timeout.'
        elif 'api' in error_msg.lower() and 'key' in error_msg.lower():
            user_friendly_error = '🔑 LLM API Key configuration error. Please contact the administrator.'
        elif 'bedrock' in error_msg.lower():
            if 'timeout' in error_msg.lower():
                user_friendly_error = '⏱️ AWS Bedrock service timed out. Please try again later.'
            elif 'credentials' in error_msg.lower() or 'access' in error_msg.lower():
                user_friendly_error = '🔑 AWS Bedrock authentication failed. Please contact the administrator to check AWS credentials.'
            else:
                user_friendly_error = f'☁️ AWS Bedrock service error: {error_msg[:200]}'
        elif 'anthropic' in error_msg.lower():
            user_friendly_error = '🤖 Anthropic API connection failed. Please contact the administrator.'
        elif 'openai' in error_msg.lower():
            user_friendly_error = '🤖 OpenAI API connection failed. Please contact the administrator.'
        elif 'connection' in error_msg.lower():
            user_friendly_error = '🌐 Network connection failed. Please check your network or try again later.'
        
        # Send error message to client
        await manager.send_message(str(conversation_id), {
            'type': 'execution_error',
            'error': user_friendly_error,
            'technical_details': error_msg[:500]  # Provide technical details for debugging
        })
